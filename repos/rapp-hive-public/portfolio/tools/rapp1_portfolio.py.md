# rapp1_portfolio.py

The crawler. It finds the RAPP family, crawls every repo with rapp-1's own rapp_check.py, writes the portfolio files and badges, emits one RAPP/1 body.pulse per crawl, keeps each version's maps, builds the timeline, then saves through the Hive and publishes.

SHA-256 of the source below: `ef3317b1035e4d18799bd4cef20213c65b9eced2b8f930ef311b5dfb572cc26f` (96423 bytes). Every pulse records it in `payload.generator`. Copy it out with the extractor in [README.md](README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""RAPP/1 portfolio: every public RAPP repo's earned RAPP/1 status, its subway map, and one RAPP/1 frame per crawl.

Repos are crawled outside the Hive with rapp-1's own rapp_check.py at the canon pin (depth-1 clones, at most six at a
time, each deleted after its check). Each crawl becomes one `body.pulse` frame (RAPP/1 SPEC §7) on the network's body
stream, with that version's maps kept under versions/<date>-<seq>/. Everything comes into the Hive by one signed save
(portfolio room under shared/organism/) and goes out only through the Hive's publish path, which runs check-public.
GitHub Pages on the public copy serves the badges, the maps, the pulses and the timeline.

    python3 -B rapp1_portfolio.py crawl [--denylist PATH]   # the one command: discover, crawl, pulse, maps, save, publish
    python3 -B rapp1_portfolio.py discover | sweep [--wave 1|2|all] [--repos a,b] [--workers 6]   # crawl steps, local
    python3 -B rapp1_portfolio.py verify [<portfolio-folder>]   # every pulse (§7.5 steps 1-5) and every version's hashes
    python3 -B rapp1_portfolio.py publish     # retry the Hive publish and push after a failed push
    python3 -B rapp1_portfolio.py status      # totals per wave and per line
    python3 -B rapp1_portfolio.py header <README> <repo> [--check]   # add or refresh the network header

Settings (flag, then environment, then <work>/local/settings.json, which never leaves this device):
    --work DIR          RAPP1_WORK         default: the folder above this tools/ folder
    --hives DIR         RAPP_HIVES         default: ~/Hives        --hive NAME   RAPP1_HIVE   default: rapp-hive
    --hive-agent PATH   RAPP_HIVE_AGENT    hive_agent.py from kody-w/rapp-model-hive (branch experimental/hive-md)
    --checker PATH      RAPP1_CHECKER      default: <work>/checker/rapp-1, cloned at the pin when missing
    --denylist PATH     RAPP1_DENYLIST     an optional private scanner (tree/diff/commits modes); kept outside the Hive

It reads only the Hive's own device state (<hive>/.git/rapp-hive/), never any other key store, and it never signs a
frame: pulses carry sig null until the estate owner authorizes a signer.
"""
import concurrent.futures as cf
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _flag(name):
    argv = sys.argv
    flag = "--" + name
    return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None


WORK = Path(_flag("work") or os.environ.get("RAPP1_WORK") or HERE.parent).expanduser().resolve()
_SETTINGS_FILE = WORK / "local" / "settings.json"


def option(name, env, default=None):
    """A setting: its flag, then its environment variable, then the local settings file, then the default."""
    try:
        local = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        local = {}
    return _flag(name) or os.environ.get(env) or local.get(name.replace("-", "_")) or default


DATA, SWEEP, CACHE, LOCAL = WORK / "data", WORK / "sweep", WORK / "cache", WORK / "local"
CLONES = CACHE / "clones"          # depth-1 clones live here only while their repo is checked
CHECKER = Path(option("checker", "RAPP1_CHECKER", str(WORK / "checker" / "rapp-1"))).expanduser()
CANON_RAPP1 = "591e014ad39e223b00ab343ae26e5d9a867ebeee"   # kody-w/rapp-1: the checker and the reference rapp.py
HIVES = Path(option("hives", "RAPP_HIVES", "~/Hives")).expanduser()
HIVE = option("hive", "RAPP1_HIVE", "rapp-hive")
HIVE_DIR = HIVES / HIVE
ROOM = "shared/organism"            # the one published room; its prefix is stripped when published
PORTFOLIO = "portfolio"             # shared/organism/portfolio/ -> portfolio/ in the public copy
OWNER = "kody-w"
PAGES = f"https://{OWNER}.github.io/rapp-hive-public/{PORTFOLIO}"
PUBLIC_BLOB = f"https://github.com/{OWNER}/rapp-hive-public/blob/main/{PORTFOLIO}"
INSTALLER = f"https://github.com/{OWNER}/rapp-installer#start-here"
START, END = "<!-- rapp1:network-header:start -->", "<!-- rapp1:network-header:end -->"
_DENY = option("denylist", "RAPP1_DENYLIST")
DENYLIST = Path(_DENY).expanduser() if _DENY else None   # private; never copied into the Hive
WAVE1 = ["RAPP", "rapp-installer", "rapp-1", "rapp-work", "rapp-workspace", "RAR", "rapp-model-hive",
         "rapp-hive-public", "hive-hub", "rapp-hive-hub", "hive-hub-mcp", "hive-hub-join",
         "rapp-hive-hub-join", "rapp-drift-lint", "lisppy"]
STATUSES = ("certified", "not yet", "unchecked")
COLORS = {"certified": "#2da44e", "not yet": "#dfb317", "unchecked": "#9f9f9f"}


# ---- the Hive: its own agent, proposal then apply (the way the dogfood driver does it) ----------------

_AGENT = None


def hive_agent():
    global _AGENT
    if _AGENT is None:
        path = option("hive-agent", "RAPP_HIVE_AGENT")
        if not path or not Path(path).expanduser().is_file():
            raise SystemExit("name the Hive agent: --hive-agent <path to hive_agent.py from kody-w/rapp-model-hive>")
        sys.path.insert(0, str(Path(path).expanduser().resolve().parent))
        import hive_agent as agent  # noqa: E402
        _AGENT = agent
    return _AGENT


def say(**kw):
    os.environ["RAPP_HIVES"] = str(HIVES)
    return hive_agent().HiveAgent().perform(**kw)


def do(**kw):
    proposal = say(**kw)
    plan = re.search(r'plan "([0-9a-f]{64})"', proposal)
    if not plan:
        raise SystemExit(f"{kw.get('action')}: no proposal\n{proposal[:1500]}")
    done = say(action="apply", plan=plan[1])
    if "Not done" in done or "Refused" in done[:200]:
        raise SystemExit(f"{kw.get('action')}: apply failed\n{done[:1500]}")
    print(f"ok {kw.get('action')} {kw.get('path') or ''}".rstrip())
    return proposal + "\n" + done


def hive_state(name):
    """The Hive's own device state, under <hive>/.git/rapp-hive/ (public.json, device.json)."""
    return load(HIVE_DIR / ".git" / "rapp-hive" / name, {}) or {}


def public_dir():
    name = hive_state("public.json").get("name")
    if not name:
        raise SystemExit(f"the Hive {HIVE} has no public copy pinned (set_public)")
    return HIVES / name


def member():
    return hive_state("device.json").get("name") or "kody"


def run(*args, cwd=None, timeout=None, env=None, check=False):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, **(env or {})}, check=check)


def load(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


# ---- discover: the RAPP family, and its lines ----------------------------------------------------

RAPP = re.compile(r"(?<![wtcgfs])rapp", re.I)          # rapp, RAPP, openrappter; not wrapper/trapped
HIVE_WORD = re.compile(r"(?<![a-z])hive", re.I)          # hive, Hives; not archive
RAR_WORD = re.compile(r"\bRAR\b")                         # the registry, written in capitals


def tokens(name):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return [t for t in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if t]


def matched_on(repo):
    name, desc = repo["name"], repo.get("description") or ""
    topics, toks = [t["name"] for t in (repo.get("repositoryTopics") or [])], tokens(repo["name"])
    why = set()
    if RAPP.search(name) or RAPP.search(desc) or any(RAPP.search(t) for t in topics):
        why.add("rapp")
    if any(t.startswith("hive") for t in toks) or HIVE_WORD.search(desc) or any(HIVE_WORD.search(t) for t in topics):
        why.add("hive")
    if "rar" in toks or RAR_WORD.search(desc) or "rar" in topics:
        why.add("rar")
    for word in ("brainstem", "rappter", "lisppy", "grail"):
        if word in "".join(toks) or re.search(word, desc, re.I) or any(word in t for t in topics):
            why.add(word)
    return sorted(why)


def _names(text):
    return frozenset(text.split())


# The families are the subway lines. A repo belongs to the first line that names it, else to the first line
# whose token pattern matches one of its name tokens, else to "RAPP Projects". It is also on every other
# line whose token pattern matches (not the line's parent), which makes it an interchange.
LINES = [
    {"id": "rapp1-core", "name": "RAPP/1 Core", "color": "#5f3dc4", "match": r"installer",
     "names": _names("RAPP rapp-1 rapp-installer rapp-work rapp-workspace rapp-drift-lint lisppy"),
     "about": "The RAPP/1 stack in layer order, from layer 0 (RAPP/1) up to the Brainstem, ending at the "
              "Start here terminal."},
    {"id": "hive", "name": "Hive", "color": "#1971c2", "match": r"hive.*",
     "names": _names("rapp-model-hive hive-hub rapp-hive-hub hive-hub-mcp hive-hub-join rapp-hive-hub-join "
                     "rapp-hive-public hive-showcase"),
     "about": "Hives, the hubs that list them, and the ways in."},
    {"id": "agents-rar", "name": "Agents (RAR)", "color": "#c2255c", "match": r"rar|skills?|store|binder",
     "names": _names("RAR rapp-agents RAPP_Store RAPP_Sense_Store rapp-store-archive RAPP_Hub rapp-skill rapp-skills "
                     "rapp-claude-skills rapp-toaster rapp-carts rapp-egg-hub rapp-packs rapp-hatchery "
                     "rapp-sentinel-hub rapp-leviathan-hub AI-Agent-Templates-Pilot rapp-stack-cubby "
                     "cowork-cookbook-rapp RAPPcards red-binder obsidian-binder"),
     "about": "The agent registry, its stores, skills, cartridges and card binders."},
    {"id": "brainstem", "name": "Brainstem", "color": "#e8590c", "match": r".*brainstem.*|stemcell|skillstem",
     "names": _names("rapp-brainstem brainstem-agent rapp-brainstem-foundation rapp-brainstem-frontier-template "
                     "rapp-brainstem-sdk vbrainstem stemcell skillstem brainstem-harness brainstem-copilot chat "
                     "ez-rapp rapp-light rapp-brainfreeze rapp-brainfreeze-studio rapp-petri rapp-quests "
                     "rapp-vscode-extension"),
     "about": "The one surface you talk to: Brainstem engines, strains, harnesses and shells."},
    {"id": "connect", "name": "Brainstem Connect", "color": "#9c36b5", "match": r"", "parent": "brainstem",
     "names": _names("rapp-brainstem-claude rapp-brainstem-claude-desktop rapp-brainstem-cline rapp-brainstem-codex "
                     "rapp-brainstem-copilot rapp-brainstem-cursor rapp-brainstem-gemini rapp-brainstem-goose "
                     "rapp-brainstem-kiro rapp-brainstem-mcp rapp-brainstem-opencode rapp-brainstem-vscode "
                     "rapp-brainstem-windsurf rapp-brainstem-plugin scout-brainstem-bootstrap rapp-mcp"),
     "about": "One line into any AI app: the per-app Brainstem setup pages and bridges."},
    {"id": "learn", "name": "Learn & Docs", "color": "#339af0", "match": r"docs|learn|specs|bible|bootcamp|walkthrough",
     "names": _names("learn-brainstem brainstem-bootcamp rapp-brainstem-walkthrough RAPP-Bible rapp-docs rapp_docs "
                     "rapp-specs rapp-map rapp-mapp rapp-roadmap rapp-mission rapp-education-shorts rapp-demos "
                     "rapp-wiki-observatory dimensional-bottles rapp-spine rapp-lab-kit rappdex"),
     "about": "Guides, specs, maps and teaching material."},
    {"id": "release", "name": "Release Channels", "color": "#212529", "match": r"alpha|beta|canary|nightly|release",
     "names": _names("rapp-alpha rapp-beta rapp-canary rapp-nightly rapp-release-train rapp-installer-canary "
                     "rapp-installer-dev rapp-brainstem-beta openrappter-alpha openrappter-beta openrappter-canary "
                     "openrappter-nightly openrappter-release-train rapp-rings rapp-train rapp-flight rapp-flight-deck "
                     "rapp-mirror-releases rapp-shape-aibast"),
     "about": "Pre-release rings and trains, from canary to stable."},
    {"id": "openrappter", "name": "OpenRappter", "color": "#e03131", "match": r"openrappter.*",
     "names": _names("openrappter homebrew-tap rappterhub rappter-cli rappter-plays-palworld rappter-plays-pokemon "
                     "rappter-prompts rappter-vui"),
     "about": "The local-first OpenRappter agent and what ships around it."},
    {"id": "rappterbook", "name": "Rappterbook", "color": "#0b7285", "match": r"rappterbook.*",
     "names": _names("rappbook-admin mars-barn"),
     "about": "The social network for AI agents and its swarm projects."},
    {"id": "rappterverse", "name": "Rappterverse", "color": "#15aabf", "match": r"rappterverse.*|rappterbox|rappternest",
     "names": _names("rappterverse rappterverse-data rappterbox RappterNest rappter-site rappter-mmo rappter-factory "
                     "rappter-distro CrystalRAPP VoidRAPP ShadowRAPP"),
     "about": "RappterBox, the Rappterverse worlds and their dimensions."},
    {"id": "rappvision", "name": "Rappvision", "color": "#f06595", "match": r"rappvision.*",
     "names": _names("rapp-vision rapp-video rapp-remix"),
     "about": "Video channels, shorts and the studio that makes them."},
    {"id": "twins", "name": "Twins", "color": "#9c6644", "match": r"twins?",
     "names": _names("echo-brainstem lumen-brainstem tide-brainstem sim-demo-twin rapp-twin rapp-twin-hub "
                     "rapp-twin-in-residence rapp-kited-twin twin-binder twin-egg-hatcher wildhaven-ai-homes-twin "
                     "rapp-zoo rapp-kite rapp-overwatch rapp-ratchet"),
     "about": "Digital twins: planted, kited, hatched and watching."},
    {"id": "neighborhoods", "name": "Neighborhoods", "color": "#be4bdb", "match": r"v?neighborhood.*|neighbor|pkstop",
     "names": _names("heimdall second-seat microsoft-se-team-neighborhood public-art-collective rapp-herdr "
                     "rapp-virtual-as400 rapp-resident rapp-work-cubbies rapp-sealed RAPP-Network "
                     "rapp-plant-smoke-20260505-233637 rapp-test-neighbor"),
     "about": "Front doors and sealed twin neighborhoods."},
    {"id": "organism", "name": "Organism & Platform", "color": "#862e2e",
     "match": r"body|brain|cortex|hippocampus|hippo|membrane|nervous|spinal|organism",
     "names": _names("rapp-body rapp-brain rapp-cortex rapp-hippocampus RAPP_hippo CommunityRAPP rapp-ai "
                     "rapp-membrane rapp-nervous-system rapp-spinal-cord rapp-organism rapp-second-brain "
                     "rapp-secondbrain rapp-apex-dino rapp-dino rapp-platform rapp-base rapp-base-template "
                     "RAPPsquared braintrust-template"),
     "about": "The organism's body parts, memory tiers and platform bases."},
    {"id": "dogg", "name": "DOGG & Commons", "color": "#3d5a80", "match": r"dogg.*|commons",
     "names": _names("dogg dogg-markets dogg-planet dogg-canon rapp-dog-hub rappidverse-field rapp-commons "
                     "rapp-god-forum rapp-open rapp-frame-net workroom"),
     "about": "The federated DOGG network, the commons and the wire between estates."},
    {"id": "tools", "name": "Tools & Apps", "color": "#3b5bdb", "match": r"",
     "names": _names("rapp-cli rapp-sdk rapp-tools rapp-static-apis rapp-static-mcp rapp-dynamic-workflows "
                     "rapp-ultracode rapp-dataverse rapp-local-install rapp-oneclick-deploy rapp-workspace-manager "
                     "rapp-projects copilot-harness-sdk dynamics365-business-process-api lisppy-shepherd "
                     "RAPPAIClaudeCodePlayground rapp-copilot-in-chrome rapp-copilot-in-edge rapp-doorman rapp-keyring "
                     "rapp-omarchy RAPP_Desktop rapp-imessage-launchpad rapp-messaging rapp-voice rapp-crispy "
                     "rapp-recall rapp-rewind rapp-shot rapp-vui"),
     "about": "Command lines, SDKs, bridges and local-first desktop apps."},
    {"id": "estate", "name": "Estate & Ops", "color": "#495057", "match": r"estate|sentinel",
     "names": _names("rapp-estate rapp-infrastructure-city rapp-monorepo rapp-distro rapp-parity rapp-sentinel "
                     "sentinel rapp-tower rapp-bake-off rapp-rock-tumbler rapp-personpower rapp-bench rapp-postflight "
                     "rapp-support rapp-refresh rapp-roadside rapp-version-selector rapp-metrics"),
     "about": "Running the estate: inventories, watchdogs, benches, resets and support."},
    {"id": "worlds", "name": "Worlds & Play", "color": "#845ef7",
     "match": r"holo|hologram|zoo|pets|pokemon|palworld|mmo",
     "names": _names("racon rio rionet RaGo rappid rapp-zoo-v2 rapp-pets rapp-play-pokemon rapp-fps rapp-holo "
                     "rapp-hologram rapp-moment rapp-snap rapp-lantern rapp-basket rapp-burrow rapp-eternity rapp-coop "
                     "rapp-heir rapp-moonshots rapp_orion ant-farm double-jump leviathan the-coliseum "
                     "sim-art-collective"),
     "about": "Games, worlds, holograms and swarm experiments."},
    {"id": "projects", "name": "RAPP Projects", "color": "#a0522d", "match": r"",
     "names": frozenset(), "about": "Everything else in the family, until it gets a line of its own."},
]
LINE = {line["id"]: line for line in LINES}
# The Core line's stations, in layer order (the organism's layers 0 to 5), ending at the Start here terminal.
TRUNK = [("rapp-1", "0 RAPP/1"), ("rapp-drift-lint", "1 Estate"), ("rapp-work", "1-2 Estate, Organization"),
         ("rapp-model-hive", "3 Hive"), ("rapp-workspace", "4 Your device"), ("lisppy", "5 Brainstem"),
         ("RAPP", "5 Brainstem"), ("rapp-installer", "Start here")]


def line_of(name):
    """(primary line, other lines): named first, else by the earliest name token a line matches."""
    toks = tokens(name)
    lines_for = lambda t: [line["id"] for line in LINES if line["match"] and re.fullmatch(line["match"], t)]
    primary = (next((line["id"] for line in LINES if name in line["names"]), None)
               or next((ids[0] for t in toks for ids in [lines_for(t)] if ids), None) or "projects")
    also = {i for t in toks for i in lines_for(t)} - {primary, LINE[primary].get("parent")}
    if name in dict(TRUNK) and primary != "rapp1-core":
        also.add("rapp1-core")
    order = {line["id"]: n for n, line in enumerate(LINES)}
    return primary, sorted(also, key=order.get)


_PATTERN = []


def denied(text):  # the optional private denylist; its patterns are never printed or copied
    if DENYLIST is None:
        if not _PATTERN:
            print("warning: no --denylist: repo names and descriptions are not privacy-checked", file=sys.stderr)
            _PATTERN.append(None)
        return False
    if not _PATTERN or _PATTERN[0] is None:
        _PATTERN.clear()
        import importlib.util
        spec = importlib.util.spec_from_file_location("rapp1_private_denylist", DENYLIST)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _PATTERN.append(module.PATTERN)
    return bool(_PATTERN[0].search(text))


def discover():
    fields = ("name,description,repositoryTopics,isFork,isArchived,visibility,defaultBranchRef,diskUsage,"
              "pushedAt,isEmpty")
    out = run("gh", "repo", "list", OWNER, "--limit", "1000", "--json", fields, check=True).stdout
    repos = json.loads(out)
    eligible = [r for r in repos if r["visibility"] == "PUBLIC" and not r["isFork"] and not r["isArchived"]]
    dump(DATA / "public-repos.json", eligible)  # private, archived and forked repos are never kept
    held, entries = [], []
    for r in eligible:
        why = matched_on(r)
        if not why and r["name"] not in WAVE1:
            continue
        if denied(r["name"] + "\n" + (r.get("description") or "")):
            held.append({"repo": r["name"], "matched_on": why})
            continue
        family, also = line_of(r["name"])
        entries.append({"repo": r["name"], "wave": 1 if r["name"] in WAVE1 else 2, "family": family, "also_on": also,
                        "matched_on": why, "default_branch": (r.get("defaultBranchRef") or {}).get("name") or "",
                        "empty": bool(r.get("isEmpty")), "disk_kb": r.get("diskUsage") or 0,
                        "description": r.get("description") or ""})
    missing = [n for n in WAVE1 if n not in {e["repo"] for e in entries}]
    entries.sort(key=lambda e: (e["wave"], e["family"], e["repo"].lower()))
    dump(DATA / "family.json", entries)
    dump(LOCAL / "denylist-held.json",
         {"note": "LOCAL ONLY: repos whose name or description hit the private denylist; kept out of "
                  "every public artifact (no portfolio file, badge, header, PR or map station).", "repos": held})
    print(f"public, non-fork, unarchived: {len(eligible)}; RAPP family: {len(entries) + len(held)} "
          f"({len(held)} held back locally by the denylist)")
    print("wave 1:", sum(e["wave"] == 1 for e in entries), "| wave 2:", sum(e["wave"] == 2 for e in entries))
    counts = Counter(e["family"] for e in entries)
    print("lines:", ", ".join(f"{LINE[i]['name']} {counts.get(i, 0)}" for i in LINE))
    print("interchanges by line membership:", sum(bool(e["also_on"]) for e in entries))
    if missing:
        print("WAVE-1 REPOS NOT FOUND (or held back):", ", ".join(missing))


def family():
    entries = load(DATA / "family.json")
    if not entries:
        raise SystemExit("run discover first")
    return entries


# ---- sweep: the full crawl, with rapp-1's own checker, outside the Hive ----------------------------

README_NAME = re.compile(r"readme(\.[A-Za-z0-9]+)?", re.I)
MARKDOWN_EXT = {".md", ".markdown", ".mdown", ".mkdn"}
MAX_WORKERS = 6  # at most six clones at a time
GENERATED = re.compile(r"generated by|auto-?generated|do not edit|don't edit|autogenerated", re.I)
LINK_URL = re.compile(r"(?:github\.com/kody-w/|raw\.githubusercontent\.com/kody-w/|kody-w\.github\.io/)([A-Za-z0-9._-]+)",
                      re.I)
LINK_BARE = re.compile(r"(?<![A-Za-z0-9._/-])kody-w/([A-Za-z0-9._-]+)", re.I)
LINK_USES = re.compile(r"^\s*-?\s*(?:uses|repository)\s*:\s*['\"]?kody-w/([A-Za-z0-9._-]+)", re.I | re.M)
LINK_SUBMODULE = re.compile(r"^\s*url\s*=\s*\S*?kody-w/([A-Za-z0-9._-]+)", re.I | re.M)
PIN_NAME = re.compile(r"(?i)(^|[_.-])(pin|pins|lock)([_.-]|$)")


def find_readme(root):
    """The README GitHub shows: .github/, then the root, then docs/ (a markdown one preferred)."""
    for sub in (".github", "", "docs"):
        folder = Path(root) / sub
        if not folder.is_dir():
            continue
        names = sorted((p.name for p in folder.iterdir() if p.is_file() and README_NAME.fullmatch(p.name)),
                       key=lambda n: (Path(n).suffix.lower() not in MARKDOWN_EXT, n))
        if names:
            return f"{sub}/{names[0]}".lstrip("/")
    return ""


def reason_for(result, code, raw_error=""):
    if code == "timeout":
        return "the checker did not finish within 15 minutes, so nothing is verified"
    if "error" in result:
        return f"the checker could not read the repository: {str(result['error'])[:160]}"
    findings = result.get("findings") or []
    if not findings:
        return f"the checker stopped (exit {code}) without a verdict{': ' + raw_error[:120] if raw_error else ''}"
    rules = Counter(str(f.get("rule", "?")) for f in findings)
    unverified = sum(1 for f in findings if f.get("status") == "unverified")
    parts = ", ".join(f"{rule} ×{n}" if n > 1 else rule for rule, n in rules.most_common(4))
    more = f", and {len(rules) - 4} more rule(s)" if len(rules) > 4 else ""
    tail = f"; {unverified} of them unverified" if unverified else ""
    return f"{len(findings)} finding(s) from rapp_check: {parts}{more}{tail}"


def remove_tree(path):
    def force(func, target, _exc):
        os.chmod(target, 0o700)
        func(target)
    if Path(path).exists():
        shutil.rmtree(path, onexc=force)


def tracked(repo_dir):
    out = run("git", "-C", str(repo_dir), "ls-files", "-z").stdout
    return [p for p in out.split("\0") if p]


def crawl_links(root, files, self_name, known):
    """{portfolio repo: {kinds}} this checkout references: markdown links, pin files, workflows, submodules."""
    found = {}
    for rel_path in files:
        low = rel_path.lower()
        base = low.rsplit("/", 1)[-1]
        stem, _, ext = base.rpartition(".")
        kinds = []
        if low.endswith((".md", ".markdown", ".mdx")) or README_NAME.fullmatch(base):
            kinds.append(("markdown", (LINK_URL,)))
        if ext in ("json", "yaml", "yml", "toml") and PIN_NAME.search(stem):
            kinds.append(("pin", (LINK_URL, LINK_BARE)))
        if low.startswith(".github/workflows/") and ext in ("yml", "yaml"):
            kinds.append(("workflow", (LINK_USES,)))
        if rel_path == ".gitmodules":
            kinds.append(("submodule", (LINK_SUBMODULE,)))
        if not kinds:
            continue
        path = Path(root) / rel_path
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 4 << 20:
                continue
            text = path.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        if "kody-w" not in text.lower():
            continue
        for kind, patterns in kinds:
            for pattern in patterns:
                for match in pattern.finditer(text):
                    name = match.group(1).rstrip(".")
                    name = name[:-4] if name.lower().endswith(".git") else name
                    canon = known.get(name.lower())
                    if canon and canon != self_name:
                        found.setdefault(canon, set()).add(kind)
    return found


def readme_facts(root, files, repo):
    """What a header PR would change, and what could stand in its way (so the clone can go)."""
    readme = find_readme(root)
    facts = {"readme": readme, "readme_markdown": Path(readme).suffix.lower() in MARKDOWN_EXT if readme else False,
             "header_present": False}
    if not readme:
        return facts
    raw = (Path(root) / readme).read_bytes()
    text = raw.decode("utf-8", errors="replace")
    facts["header_present"] = START in text and END in text
    if not facts["readme_markdown"]:
        return facts
    digest, blob = hashlib.sha256(raw).hexdigest(), hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
    pinned = run("git", "-C", str(root), "grep", "-l", "-I", "-F", "-e", digest, "-e", blob).stdout.split()
    tests = [p for p in files if re.search(r"(^|/)(tests?|spec)/|(^|/)test_[^/]*\.py$|\.test\.[mc]?[jt]s$", p)]
    readers = (run("git", "-C", str(root), "grep", "-l", "-I", "-e", "README", "--", *tests[:2000]).stdout.split()
               if tests else [])
    try:
        new, action = apply_header(text, repo)
    except ValueError as error:
        new, action = text, f"manual: {error}"
    diff = "".join(difflib.unified_diff(text.splitlines(True), new.splitlines(True), f"a/{readme}", f"b/{readme}", n=2))
    facts.update(readme_sha256=digest, readme_receipts=[p for p in pinned if p != readme],
                 readme_generated=bool(GENERATED.search("\n".join(text.splitlines()[:15]))),
                 readme_test_readers=readers, header_action=action, header_diff=diff[:4000])
    return facts


def sweep_one(entry, today, known):
    repo = entry["repo"]
    rec = {"repo": repo, "wave": entry["wave"], "family": entry["family"], "checked": today,
           "checker": f"kody-w/rapp-1 rapp_check.py at {CANON_RAPP1[:7]}", "default_branch": entry["default_branch"]}
    clone, url = CLONES / repo, f"https://github.com/{OWNER}/{repo}.git"
    lfs_off = {"GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}
    try:
        error = ""
        for attempt in range(3):  # depth-1 fetch into the cache, or a fresh depth-1 clone
            if (clone / ".git").is_dir():
                steps = [("git", "-C", str(clone), "fetch", "-q", "--depth", "1", "--no-tags", "origin", "HEAD"),
                         ("git", "-C", str(clone), "reset", "-q", "--hard", "FETCH_HEAD"),
                         ("git", "-C", str(clone), "clean", "-qfdx")]
            else:
                remove_tree(clone)
                steps = [("git", "clone", "-q", "--depth", "1", "--no-tags", url, str(clone))]
            error = ""
            for step in steps:
                try:
                    done = run(*step, timeout=1800, env=lfs_off)
                except subprocess.TimeoutExpired:
                    done = subprocess.CompletedProcess(step, 1, "", "timed out after 30 minutes")
                if done.returncode:
                    error = (done.stderr.strip().splitlines() or ["unknown error"])[-1][:160]
                    break
            if not error:
                break
            remove_tree(clone)
            time.sleep(5 * (attempt + 1))
        commit = run("git", "-C", str(clone), "rev-parse", "--verify", "-q", "HEAD").stdout.strip() if not error else ""
        if error or not commit:
            rec.update(status="unchecked", reason=("the crawl could not clone it: " + error) if error else
                       "the repository is empty: GitHub holds no commit to clone or check")
            dump(SWEEP / f"{repo}.record.json", rec)
            return rec
        attrs = clone / ".gitattributes"
        if attrs.is_file() and "filter=lfs" in attrs.read_text(errors="replace"):  # checked files only
            run("git", "-C", str(clone), "lfs", "pull", "--include", "*.json,*.egg", timeout=1800)
        try:
            done = run(sys.executable, "-B", str(CHECKER / "rapp_check.py"), repo, "--json", cwd=str(CLONES), timeout=900)
            raw, code, err = done.stdout, done.returncode, done.stderr
        except subprocess.TimeoutExpired:
            raw, code, err = "", "timeout", ""
        (SWEEP / f"{repo}.json").write_text(raw or "{}", encoding="utf-8", newline="\n")
        result = load(SWEEP / f"{repo}.json", {}) or {}
        result = result if isinstance(result, dict) else {}
        verdict = result.get("verdict")
        if verdict in ("COMPLIANT", "CLEAN") and code == 0:
            status, reason = "certified", ""
        else:
            status, reason = "not yet", reason_for(result, code, err.strip())
        files = tracked(clone)
        grep = run("git", "-C", str(clone), "grep", "-I", "-i", "-o", "-w", "-e", "experimental")
        links = crawl_links(clone, files, repo, known)
        findings = result.get("findings") or []
        rec.update(status=status, reason=reason, verdict=verdict or ("timeout" if code == "timeout" else "error"),
                   evidence_commit=commit, raw_sha256=hashlib.sha256((raw or "{}").encode()).hexdigest(),
                   findings=len(findings), findings_head=[
                       {k: str(f.get(k, ""))[:200] for k in ("artifact", "rule", "detail", "status") if f.get(k)}
                       for f in findings[:12]],
                   evidence=len(result.get("evidence") or []),
                   experimental_mentions=len(grep.stdout.splitlines()),
                   tracked_files=len(files),
                   links_to=sorted(links, key=str.lower),
                   links_kinds={name: sorted(kinds) for name, kinds in sorted(links.items(), key=lambda kv: kv[0].lower())},
                   **readme_facts(clone, files, repo))
        dump(SWEEP / f"{repo}.record.json", rec)
        return rec
    finally:
        remove_tree(clone)  # keep the results, not the clones


def ensure_checker():
    """rapp-1 at the canon pin: the checker (rapp_check.py) and the reference implementation (rapp.py)."""
    if not (CHECKER / ".git").exists():
        CHECKER.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "-q", f"https://github.com/{OWNER}/rapp-1.git", str(CHECKER), check=True)
        run("git", "-C", str(CHECKER), "checkout", "-q", "--detach", CANON_RAPP1, check=True)
    if run("git", "-C", str(CHECKER), "rev-parse", "HEAD").stdout.strip() != CANON_RAPP1:
        raise SystemExit(f"the checker at {CHECKER} is not at the canon pin {CANON_RAPP1}")
    if run("git", "-C", str(CHECKER), "status", "--porcelain").stdout.strip():
        raise SystemExit(f"the checker at {CHECKER} has local changes; it must be exactly the pinned commit")


def sweep(args):
    SWEEP.mkdir(parents=True, exist_ok=True)
    CLONES.mkdir(parents=True, exist_ok=True)
    ensure_checker()
    wave = arg(args, "--wave", "all")
    names = [n for n in arg(args, "--repos", "").split(",") if n]
    everyone = family()
    known = {e["repo"].lower(): e["repo"] for e in everyone}  # only public portfolio repos count as links
    entries = [e for e in everyone if (wave == "all" or str(e["wave"]) == wave) and (not names or e["repo"] in names)]
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    started_utc = utc_now()
    workers = max(1, min(int(arg(args, "--workers", str(MAX_WORKERS))), MAX_WORKERS))
    print(f"crawling {len(entries)} repo(s) with rapp_check.py at {CANON_RAPP1[:7]}: depth-1 clones, {workers} at a "
          "time, each deleted after its check", flush=True)
    started = time.time()
    with cf.ThreadPoolExecutor(workers) as pool:
        for rec in pool.map(lambda e: sweep_one(e, today, known), entries):
            print(f"swept {rec['repo']}: {rec['status']}" + (f" ({rec.get('verdict')})" if rec.get("verdict") else "")
                  + (f" · {len(rec.get('links_to', []))} link(s)" if "links_to" in rec else "")
                  + (f" · {rec['reason'][:90]}" if rec.get("reason") else ""), flush=True)
    left = [p.name for p in CLONES.iterdir()] if CLONES.exists() else []
    if wave == "all" and not names:  # a full crawl: the one a pulse may record
        dump(DATA / "crawl.json", {"started_utc": started_utc, "finished_utc": utc_now(), "repos": len(entries),
                                   "clones_left": len(left), "workers": workers})
    print(f"crawl done in {time.time() - started:.0f} s; clones left in the cache: {len(left)}")


def arg(args, name, default):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default


def utc_now():
    """The RAPP/1 §7.4 fixed form: YYYY-MM-DDTHH:MM:SS.mmmZ, in UTC."""
    now = dt.datetime.now(dt.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


# ---- the network header -------------------------------------------------------------------------

def header_block(repo):
    r = quote(repo, safe="")
    return (f"{START}\n[![RAPP/1]({PAGES}/badges/{r}.svg)]({PUBLIC_BLOB}/repos/{r}.md) · **New to RAPP?** "
            f"[Start here: get your Brainstem →]({INSTALLER})\n{END}")


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_H = re.compile(r"<h([1-6])[\s>]", re.I)


def first_heading(lines, start):
    """(level, index of the heading's last line, is_html) for the first heading, else None."""
    fence, comment = None, False
    for i in range(start, len(lines)):
        line = lines[i]
        if comment:
            comment = "-->" not in line
            continue
        if fence:
            if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$", line):
                fence = None
            continue
        m = FENCE.match(line)
        if m:
            fence = m.group(1)
            continue
        if "<!--" in line and "-->" not in line.split("<!--", 1)[1]:
            comment = True
            continue
        m = ATX.match(line)
        if m:
            return len(m.group(1)), i, False
        m = HTML_H.search(line)
        if m:
            return int(m.group(1)), i, True
        if line.strip() and i + 1 < len(lines) and SETEXT.match(lines[i + 1]) and not line.lstrip().startswith(("<", "|", "-", "*", "+", ">")):
            if lines[i + 1].strip().startswith("="):
                return 1, i + 1, False
            if lines[i + 1].strip().startswith("-") and len(lines[i + 1].strip()) >= 2:
                return 2, i + 1, False
    return None


def apply_header(text, repo):
    """(new text, action): refresh the marked header in place, or add it after the H1 (else at the top)."""
    crlf = text.count("\r\n") > text.count("\n") / 2
    body = text.replace("\r\n", "\n")
    bom = "\ufeff" if body.startswith("\ufeff") else ""
    body = body[len(bom):]
    block = header_block(repo)
    has_start, has_end = body.count(START), body.count(END)
    if has_start or has_end:
        if has_start != 1 or has_end != 1 or body.index(START) > body.index(END):
            raise ValueError("the network header markers are unbalanced; fix them by hand")
        a, b = body.index(START), body.index(END) + len(END)
        new = body[:a] + block + body[b:]
        action = "unchanged" if new == body else "refreshed"
    else:
        lines = body.split("\n")
        start = 0
        if lines and lines[0].strip() == "---":  # front matter stays first
            end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
            start = end + 1 if end is not None else 0
        found = first_heading(lines, start)
        if found and found[0] == 1:
            level, at, is_html = found
            if is_html:  # after the HTML block that holds the <h1>
                at = next((i - 1 for i in range(at + 1, len(lines)) if not lines[i].strip()), len(lines) - 1)
            before, after = lines[:at + 1], lines[at + 1:]
            action = "added after the H1"
        else:
            before, after = lines[:start], lines[start:]
            action = "added at the top"
        while after and not after[0].strip():
            after = after[1:]
        while before and not before[-1].strip() and len(before) > start:
            before = before[:-1]
        pieces = (before + [""] if before else []) + block.split("\n") + ([""] + after if after else [""])
        new = "\n".join(pieces)
        if body.endswith("\n") and not new.endswith("\n"):
            new += "\n"
    new = bom + new
    return (new.replace("\n", "\r\n") if crlf else new), action


def header_cli(args):
    path, repo = Path(args[0]), args[1]
    text = path.read_text(encoding="utf-8")
    new, action = apply_header(text, repo)
    if "--check" in args:
        print(action)
        return 0 if action == "unchanged" else 1
    if new != text:
        path.write_bytes(new.encode("utf-8"))
    print(f"{path}: {action}")
    return 0


# ---- the badge ----------------------------------------------------------------------------------

WIDTH = {"R": 7.6, "A": 7.5, "P": 6.6, "/": 4.6, "1": 7.0, "c": 5.7, "e": 6.8, "r": 4.7, "t": 4.3, "i": 3.0,
         "f": 3.9, "d": 6.9, "n": 7.0, "o": 6.7, "y": 6.5, " ": 3.9, "u": 7.0, "h": 7.0, "k": 6.5}


def text_width(s):
    return int(sum(WIDTH.get(ch, 7.0) for ch in s) + 0.999) + 10


def badge_svg(status):
    """A flat 'RAPP/1 | status' badge. Lowercase attribute names only: GitHub Pages runs every .md
    through kramdown, which lowercases attribute names in HTML blocks."""
    left, right, color = text_width("RAPP/1"), text_width(status), COLORS[status]
    w, label = left + right, f"RAPP/1: {status}"
    font = 'font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}">'
            f"<title>{label}</title>"
            f'<rect width="{w}" height="20" rx="3" fill="{color}"/>'
            f'<rect width="{left}" height="20" rx="3" fill="#555"/>'
            f'<rect x="{left - 4}" width="4" height="20" fill="#555"/>'
            f'<g fill="#fff" text-anchor="middle" {font}>'
            f'<text x="{left / 2:g}" y="15" fill="#010101" fill-opacity=".3">RAPP/1</text>'
            f'<text x="{left / 2:g}" y="14">RAPP/1</text>'
            f'<text x="{left + right / 2:g}" y="15" fill="#010101" fill-opacity=".3">{status}</text>'
            f'<text x="{left + right / 2:g}" y="14">{status}</text></g></svg>')


def badge_file(repo, status):
    # The Hive holds only .md files, so the badge is a markdown file whose front matter tells GitHub
    # Pages (Jekyll) to emit it at badges/<repo>.svg with no layout: served as image/svg+xml.
    return (f"---\npermalink: /{PORTFOLIO}/badges/{quote(repo, safe='')}.svg\nlayout: null\n---\n"
            f"{badge_svg(status)}\n")


# ---- build: the portfolio room, by one signed save ------------------------------------------------

def records():
    out = {}
    for e in family():
        rec = load(SWEEP / f"{e['repo']}.record.json") or {
            "repo": e["repo"], "status": "unchecked", "reason": "the sweep has not run on it yet"}
        rec.update(wave=e["wave"], family=e["family"], also_on=e.get("also_on", []), default_branch=e["default_branch"])
        out[e["repo"]] = rec
    return out


def linked_from(recs):
    back = {name: set() for name in recs}
    for name, rec in recs.items():
        for target in rec.get("links_to", []):
            if target in back:
                back[target].add(name)
    return {name: sorted(names, key=str.lower) for name, names in back.items()}


def exceptions():  # repos whose header is held back on purpose, with the reason
    return load(DATA / "header-exceptions.json", {}) or {}


def header_state(rec, pr):
    if rec.get("header_present"):
        return "present"
    if rec["repo"] in exceptions():
        return "held"
    if pr and pr.get("state") == "OPEN":
        return "pr-open"
    if pr and pr.get("state") == "MERGED":
        return "merged"
    if "readme" not in rec:
        return "unknown"
    if not rec["readme"]:
        return "no-readme"
    return "missing" if rec.get("readme_markdown") else "not-markdown"


HEADER_WORDS = {"present": "present", "pr-open": "PR open", "merged": "merged, awaiting the next sweep",
                "missing": "not yet added", "no-readme": "no README (skipped)",
                "not-markdown": "README is not markdown (skipped)", "unknown": "unknown until swept",
                "held": "held back"}


def repo_file(rec, pr, back=()):
    repo, status = rec["repo"], rec["status"]
    commit, header = rec.get("evidence_commit", ""), header_state(rec, pr)
    meta = [("repo", f"{OWNER}/{repo}"), ("family", rec["family"]), ("line", LINE[rec["family"]]["name"]),
            ("wave", rec["wave"]), ("status", status),
            ("verdict", rec.get("verdict", "none")), ("evidence_commit", commit or "none"),
            ("checked", rec.get("checked", "never")), ("checker", f"kody-w/rapp-1 rapp_check.py at {CANON_RAPP1[:7]}"),
            ("experimental_mentions", rec.get("experimental_mentions", "unknown")), ("header", header)]
    if pr and pr.get("url"):
        meta.append(("header_pr", pr["url"]))
    r = quote(repo, safe="")
    listed_meta = [(k, v) for k, v in (("also_on", rec.get("also_on", [])), ("links_to", rec.get("links_to", []))) if v]
    lines = ["---", *[f"{k}: {v}" for k, v in meta],
             *[x for k, v in listed_meta for x in [f"{k}:", *[f"  - {i}" for i in v]]], "---", "",
             f"# {repo}: {status}", "", f"![RAPP/1: {status}]({PAGES}/badges/{r}.svg)", ""]
    if status == "certified":
        meaning = ("every RAPP artifact passes" if rec["verdict"] == "COMPLIANT"
                   else "no RAPP artifacts, found by a complete bounded scan")
        lines += [f"**Certified:** rapp-1's own checker gave **{rec['verdict']}** ({meaning}) at the evidence commit.", ""]
    elif status == "not yet":
        lines += [f"**Not yet:** {rec.get('reason', '')}.", ""]
    else:
        lines += [f"**Unchecked:** {rec.get('reason', 'the sweep has not run on it yet')}.", ""]
    if commit:
        lines += [f"- Evidence: [`{OWNER}/{repo}` at `{commit[:10]}`](https://github.com/{OWNER}/{repo}/tree/{commit})"
                  f" on `{rec.get('default_branch') or 'the default branch'}`, checked {rec['checked']}.",
                  f"- Checker: [`rapp_check.py` at `{CANON_RAPP1[:7]}`](https://github.com/{OWNER}/rapp-1/blob/"
                  f"{CANON_RAPP1}/rapp_check.py), verdict **{rec.get('verdict')}**"
                  + (f", {rec['findings']} finding(s)" if rec.get("findings") else "")
                  + (f", {rec['evidence']} passing artifact(s)" if rec.get("evidence") else "")
                  + ". The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is "
                  f"`{rec.get('raw_sha256', '')}`.",
                  f"- \"experimental\" mentions: {rec.get('experimental_mentions')} (whole word, any case, in "
                  "tracked text files at the evidence commit; tracked, not a gate).",
                  f"- Network header: {HEADER_WORDS[header]}"
                  + (f": {exceptions()[repo]}" if header == "held" else "")
                  + (f" ({pr['url']})" if pr and pr.get("url") and header in ("pr-open", "merged") else "")
                  + (f" in `{rec['readme']}`" if rec.get("readme") and header == "present" else "") + ".", ""]
    heads = rec.get("findings_head") or []
    if heads:
        lines += [f"## Findings ({rec.get('findings', len(heads))})", ""]
        lines += [f"- `{f.get('artifact', '?')}` · {f.get('rule', '?')} · {f.get('detail', '')[:160]}"
                  + (f" ({f['status']})" if f.get("status") else "") for f in heads]
        if rec.get("findings", 0) > len(heads):
            lines.append(f"- … and {rec['findings'] - len(heads)} more in the raw output")
        lines.append("")
    others = [LINE[i]["name"] for i in rec.get("also_on", [])]
    lines += [f"On the map: the **{LINE[rec['family']]['name']}** line" + (f", and also {', '.join(others)}" if others else "")
              + f" ([subway map]({PAGES}/subway.html)).", ""]
    kinds = rec.get("links_kinds", {})
    if rec.get("links_to") or back:
        lines += ["## Links", ""]
        if rec.get("links_to"):
            lines.append(f"Links to {len(rec['links_to'])} portfolio repo(s): " + ", ".join(
                f"[{t}]({quote(t, safe='')}.md) ({', '.join(kinds.get(t, []))})" for t in rec["links_to"]) + ".")
        if back:
            lines.append(f"Linked from {len(back)}: " + ", ".join(f"[{t}]({quote(t, safe='')}.md)" for t in back) + ".")
        lines += ["", "Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, "
                  "workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in "
                  "this portfolio count.", ""]
    if commit:
        clone = (f"Clone `{OWNER}/rapp-1` at `{CANON_RAPP1[:7]}`" if repo == "rapp-1" and commit == CANON_RAPP1
                 else f"Clone `{OWNER}/{repo}` at `{commit[:10]}` and `{OWNER}/rapp-1` at `{CANON_RAPP1[:7]}`")
        lines += ["## Check it yourself", "",
                  f"{clone}, then run `python3 -B rapp-1/rapp_check.py {repo} --json` from the folder that holds "
                  + ("it." if repo == "rapp-1" and commit == CANON_RAPP1 else "both."), ""]
    return "\n".join(lines)


def line_file(line, n, recs):
    members = sorted((r for r in recs.values() if r["family"] == line["id"]), key=lambda r: r["repo"].lower())
    meta = ["---", f"line: {line['id']}", f"name: {line['name']}", f'color: "{line["color"]}"', f"order: {n}",
            f"stations: {len(members)}", f'about: "{line["about"]}"']
    body = [f"# {line['name']}", "", line["about"], ""]
    if line["id"] == "rapp1-core":
        meta += ["trunk:", *[f"  - {repo} | {layer}" for repo, layer in TRUNK], "terminal: rapp-installer"]
        body += ["The Core line's stations, in layer order (the organism's layers 0 to 5), ending at the Start here "
                 "terminal:", "", "| Station | Layer | Status |", "|---|---|---|"]
        body += [f"| [{repo}](../repos/{quote(repo, safe='')}.md) | {layer} | {recs[repo]['status']} |" for repo, layer in TRUNK]
        body.append("")
    if members:
        body += ["| Station | Status | Also on |", "|---|---|---|"]
        body += [f"| [{r['repo']}](../repos/{quote(r['repo'], safe='')}.md) | {r['status']} | "
                 f"{', '.join(LINE[i]['name'] for i in r.get('also_on', []))} |" for r in members]
    return "\n".join(meta + ["---", ""] + body) + "\n"


def portfolio_md(recs, prs, version=None):
    by_wave = {w: Counter(r["status"] for r in recs.values() if r["wave"] == w) for w in (1, 2)}
    total = Counter(r["status"] for r in recs.values())
    row = lambda c: " | ".join(str(c.get(s, 0)) for s in STATUSES) + f" | {sum(c.values())}"
    lines = ["# RAPP/1 portfolio", "",
             "Every public RAPP repo, each with an **earned** RAPP/1 status. RAPP/1 is the LTS version for the whole "
             "network: a repo is certified when rapp-1's own checker passes it at a recorded commit.", "",
             "| Wave | certified | not yet | unchecked | total |", "|---|---|---|---|---|",
             f"| 1: the RAPP/1 stack | {row(by_wave[1])} |", f"| 2: the rest of the RAPP family | {row(by_wave[2])} |",
             f"| **all** | {row(total)} |", "",
             f"- **certified**: [`rapp_check.py` at `{CANON_RAPP1[:7]}`](https://github.com/{OWNER}/rapp-1/blob/"
             f"{CANON_RAPP1}/rapp_check.py) says COMPLIANT or CLEAN at the recorded commit.",
             "- **not yet**: drift or unverified; each file says why.",
             "- **unchecked**: the sweep has not run on it yet.", "",
             "Each repo's README carries one marked line: its badge (served from this folder by GitHub Pages, so the "
             f"URL never changes) and a link to [Start here]({INSTALLER}) for anyone without a Brainstem yet. "
             "\"experimental\" mentions are tracked here as a metric; they are not a gate yet.", "",
             "A Hive holds only markdown, so each badge is `badges/<repo>.svg.md`: its front matter tells GitHub Pages "
             f"to serve it as `{PAGES}/badges/<repo>.svg` (image/svg+xml).", "",
             "## The map", "",
             f"**[Subway map]({PAGES}/subway.html)** (zoomable; click a station for its portfolio file and its repo) · "
             f"[poster PDF]({PAGES}/subway.pdf) · [SVG]({PAGES}/subway.svg)", "",
             "Lines are the families below; stations are repos, filled by status; the RAPP/1 Core line runs in layer "
             "order and ends at `rapp-installer`, the Start here terminal. It is drawn from these files by "
             "`rapp1_subway.py`, and the links between repos come from each file's `links_to`.", "",
             *([f"**Version {version['number']}**, crawled {version['utc'][:10]} {version['utc'][11:16]} UTC. Every crawl "
                "is one RAPP/1 frame, a `body.pulse` on the network's body stream "
                f"`{version['stream_id']}`. The [timeline]({PAGES}/timeline.html) lists every version with its pulse "
                "hashes and what changed, and each version's maps stay under `versions/`.", ""] if version else []),
             "| Line | Stations | certified | not yet | unchecked |", "|---|---|---|---|---|"]
    for line in LINES:
        c = Counter(r["status"] for r in recs.values() if r["family"] == line["id"])
        if sum(c.values()):
            lines.append(f"| [{line['name']}](lines/{line['id']}.md) | {sum(c.values())} | "
                         + " | ".join(str(c.get(s, 0)) for s in STATUSES) + " |")
    lines.append("")
    order = {line["id"]: n for n, line in enumerate(LINES)}
    for wave, title in ((1, "Wave 1: the RAPP/1 stack"), (2, "Wave 2: the rest of the RAPP family")):
        group = sorted((r for r in recs.values() if r["wave"] == wave), key=lambda r: (order[r["family"]], r["repo"].lower()))
        lines += [f"## {title} ({len(group)})", ""]
        for fam in sorted({r["family"] for r in group}, key=order.get):
            members = [r for r in group if r["family"] == fam]
            lines += [f"### {LINE[fam]['name']} ({len(members)})", "",
                      "| Repo | Status | Verdict | Commit | Checked | \"experimental\" | Header |", "|---|---|---|---|---|---|---|"]
            for r in members:
                h = header_state(r, prs.get(r["repo"]))
                lines.append(f"| [{r['repo']}](repos/{quote(r['repo'], safe='')}.md) | {r['status']} | "
                             f"{r.get('verdict', '')} | {r.get('evidence_commit', '')[:7]} | {r.get('checked', '')} | "
                             f"{r.get('experimental_mentions', '')} | {HEADER_WORDS[h]} |")
            lines.append("")
    return "\n".join(lines)


def public_readme(text):
    new, _ = apply_header(text, "rapp-hive-public")
    bullet = ("- `portfolio/`: every public RAPP repo's earned RAPP/1 status, one file per repo in `repos/`, the "
              "whole table in `PORTFOLIO.md`, the badges each repo's README shows, and the subway map of the network "
              f"({PAGES}/subway.html, poster: {PAGES}/subway.pdf). Every crawl is one RAPP/1 `body.pulse` frame; "
              f"each version's maps stay under `versions/`, and the timeline ({PAGES}/timeline.html) lists them all. "
              "GitHub Pages serves them.")
    if "- `portfolio/`" in new:
        new = re.sub(r"- `portfolio/`[^\n]*", lambda m: bullet, new, count=1)
    else:
        new = re.sub(r"(- `canon/`[^\n]*\n)", lambda m: m.group(1) + bullet + "\n", new, count=1)
    return new


def scan_tree(*folders):
    if DENYLIST is None:
        print("privacy scan (tree): skipped, no --denylist given")
        return
    done = run(sys.executable, "-B", str(DENYLIST), "tree", *map(str, folders))
    where = sorted({line.split(": ", 1)[0] for line in done.stdout.splitlines()[:-1]})
    print("privacy scan (tree):", done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr[-200:],
          ("in " + ", ".join(where[:20])) if where else "")
    if done.returncode:
        raise SystemExit("the privacy scan found something; nothing was saved or published")


def signed_save():
    """One signed commit of every hand edit in the Hive, through its own save (proposal, then apply)."""
    proposal = say(action="save", hive=HIVE)
    if "There is nothing to save" in proposal:
        print("nothing to save")
        return None
    plan = re.search(r'plan "([0-9a-f]{64})"', proposal)
    if not plan or "Not allowed" in proposal or "None of these" in proposal:
        if plan:
            say(action="cancel", plan=plan[1])
        lines = proposal.splitlines()
        start = next((n for n, line in enumerate(lines) if "Not allowed" in line or "None of these" in line), 0)
        raise SystemExit("the Hive refused part of the save:\n" + "\n".join(line[:400] for line in lines[start:start + 12]))
    done = say(action="apply", plan=plan[1])
    if "Done:" not in done:
        raise SystemExit("apply failed:\n" + done[:2000])
    commit = re.search(r"commit ([0-9a-f]{10})", done)
    print(re.search(r"Done: .*", done)[0][:200])
    return commit[1] if commit else None


def portfolio_files(recs, prs, version=None):
    """{path in the portfolio room: text}: repo files, badges, lines and PORTFOLIO.md (the maps are drawn from them)."""
    back = linked_from(recs)
    want = {f"repos/{r}.md": repo_file(rec, prs.get(r), back[r]) for r, rec in recs.items()}
    want.update({f"badges/{r}.svg.md": badge_file(r, rec["status"]) for r, rec in recs.items()})
    used = {rec["family"] for rec in recs.values()}
    want.update({f"lines/{line['id']}.md": line_file(line, n, recs) for n, line in enumerate(LINES, 1)
                 if line["id"] in used})
    want["PORTFOLIO.md"] = portfolio_md(recs, prs, version)
    return want


def write_room(room, want, keep=()):
    """Write `want` into the room; remove any other file, except under the `keep` prefixes."""
    for rel_path in want:
        if len(f"{ROOM}/{PORTFOLIO}/{rel_path}") > 120 or any(len(p) > 64 for p in rel_path.split("/")):
            raise SystemExit(f"{rel_path}: too long for a Hive path")
    existing = {p.relative_to(room).as_posix() for p in room.rglob("*") if p.is_file()} if room.exists() else set()
    removed = {p for p in existing - set(want) if not any(p.startswith(k) for k in keep)}
    for stale in removed:
        (room / stale).unlink()
    changed = 0
    for rel_path, text in want.items():
        path = room / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
    return changed, removed


# ---- the pulse: one RAPP/1 frame per crawl ----------------------------------------------------------------

STREAM_SLUG = "rapp1-network"           # the stream's rappid slug; the tail is minted once, keyless (§6.2)
PULSE_KIND = "body.pulse"               # a registered kind of the body family (SPEC §7.2; rapp-1 anchor head rev-16)
PULSE_SCHEMA = "rapp1-network-pulse/1"  # a label for the payload's shape, never an identity
INDEX_NAME = "rapp-frame-index.json"
CHAIN_PUBLIC = HIVE_DIR / ROOM / PORTFOLIO               # published with the portfolio
CHAIN_PRIVATE = HIVE_DIR / "shared" / "network-pulses"   # an unpublished room, if the public copy would lose its badge
CODE_FENCE, LB = "`" * 5, "{"
RAW_START, RAW_END = LB + "% raw %}", LB + "% endraw %}"  # composed, so this file never ends a raw block itself


def rapp():
    """The reference implementation, imported from the pinned rapp-1 checkout (never re-typed: SPEC §4, note C4)."""
    ensure_checker()
    if str(CHECKER) not in sys.path:
        sys.path.insert(0, str(CHECKER))
    import rapp as reference  # noqa: E402
    return reference


def subway():
    import rapp1_subway as module  # noqa: E402
    return module


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def chain_home():
    for home in (CHAIN_PUBLIC, CHAIN_PRIVATE):
        if (home / "rappid.json.md").is_file():
            return home
    return None


def read_chain(home):
    """(stream_id, record, [(frame, version folder)]): every pulse verified from genesis against the stream of record,
    RAPP/1 §7.5 steps 1-5 with the reference rapp.py. A failure refuses, never repairs."""
    if home is None or not (Path(home) / "rappid.json.md").is_file():
        return None, None, []
    reference, home = rapp(), Path(home)
    record = json.loads(subway().unwrap((home / "rappid.json.md").read_text(encoding="utf-8")))
    sid = record.get("rappid") if isinstance(record, dict) else None
    if not reference.rappid_valid(sid) or record.get("schema") != "rapp/1":
        raise SystemExit(f"{home}/rappid.json.md: not a RAPP/1 identity record")
    found = []
    for path in sorted(home.glob("versions/*/pulse.json.md")):
        blob = subway().unwrap(path.read_text(encoding="utf-8")).encode("utf-8")
        try:
            frame = reference._strict_json(blob)
        except ValueError as error:
            raise SystemExit(f"{path}: not strict I-JSON ({error})")
        found.append((frame, path.parent.name))
    found.sort(key=lambda item: item[0].get("seq", -1) if isinstance(item[0], dict) else -1)
    head = None
    for n, (frame, vid) in enumerate(found):
        if not isinstance(frame, dict) or frame.get("seq") != n:
            raise SystemExit(f"versions/{vid}: the chain has a gap or a duplicate at seq {n}")
        ok, step, why = reference.verify_frame(frame, head=head, stream_id_of_record=sid)
        if not ok:
            raise SystemExit(f"versions/{vid}/pulse.json: fails RAPP/1 §7.5 step {step}: {why}")
        if frame["kind"] != PULSE_KIND or subway().version_id(frame) != vid:
            raise SystemExit(f"versions/{vid}/pulse.json: not a {PULSE_KIND} of this chain, or in the wrong folder")
        head = frame
    return sid, record, found


def mint_stream():
    """The network's body-stream identity: minted exactly once (§6.2 keyless: Hb("rapp/1:rappid", UUIDv4 octets)).
    Until the genesis pulse is saved the record waits in <work>/local/, so a failed first crawl never mints twice."""
    pending = LOCAL / "minted-rappid.json"
    kept = load(pending)
    if kept and rapp().rappid_valid(kept.get("rappid")):
        return kept["rappid"], kept
    sid = rapp().mint_rappid(OWNER, STREAM_SLUG)
    record = {
        "schema": "rapp/1", "rappid": sid, "kind": "body", "name": STREAM_SLUG, "display_name": "RAPP/1 network",
        "minted_utc": utc_now(),
        "stream": {"kind": PULSE_KIND, "index": INDEX_NAME, "timeline": f"{PAGES}/timeline.html"},
        "note": ("Minted once per RAPP/1 §6.2 from UUIDv4 entropy (keyless); never re-mint, never derive from a name. "
                 "It names the RAPP/1 network's body stream: one body.pulse per crawl. Keyless, so it asserts location, "
                 "not authorship; no key exists for it."),
    }
    dump(pending, record)
    return sid, record


def crawl_record():
    meta = load(DATA / "crawl.json")
    names = [e["repo"] for e in family()]
    if not meta or meta.get("repos") != len(names):
        raise SystemExit("no full crawl covers the current portfolio: run crawl (or sweep with no filters) first")
    missing = [n for n in names if not (SWEEP / f"{n}.record.json").is_file()]
    if missing:
        raise SystemExit(f"the crawl has no record for {', '.join(missing[:5])}")
    return meta


def pulse_payload(recs, number, crawl, artifacts, generator):
    """What one pulse records: when and with what it crawled, the totals, each repo's result, the links digest, and
    the content hashes of this version's files. Integers and strings only (RAPP/1 §4 forbids floats)."""
    reference = rapp()
    nfc = lambda text: __import__("unicodedata").normalize("NFC", str(text))
    count = lambda group: {s: sum(1 for r in group if r["status"] == s) for s in STATUSES}
    lines = {}
    for line in LINES:
        members = [r for r in recs.values() if r["family"] == line["id"]]
        if members:
            lines[line["id"]] = {"name": nfc(line["name"]), "stations": len(members), **count(members)}
    repos = {}
    for name, r in sorted(recs.items()):
        commit = r.get("evidence_commit") or None
        entry = {"line": r["family"], "status": r["status"], "verdict": r.get("verdict") if commit else None,
                 "evidence_commit": commit}
        if r["status"] == "unchecked":
            entry["reason"] = nfc(r.get("reason", ""))
        repos[nfc(name)] = entry
    links = {nfc(name): sorted(nfc(t) for t in r.get("links_to", [])) for name, r in recs.items()}
    return {
        "schema": PULSE_SCHEMA,
        "version": number,
        "crawl": {"started_utc": crawl["started_utc"], "finished_utc": crawl["finished_utc"], "repos": crawl["repos"]},
        "checker": {"repository": f"https://github.com/{OWNER}/rapp-1", "commit": CANON_RAPP1, "path": "rapp_check.py",
                    "sha256": sha256((CHECKER / "rapp_check.py").read_bytes())},
        "totals": {"stations": len(recs), **count(recs.values())},
        "waves": {str(w): {"stations": len([r for r in recs.values() if r["wave"] == w]),
                           **count([r for r in recs.values() if r["wave"] == w])} for w in (1, 2)},
        "lines": lines,
        "repos": repos,
        "links_to": {"sha256": sha256(reference.canonical(links)), "edges": sum(len(v) for v in links.values()),
                     "repos_linking": sum(1 for v in links.values() if v),
                     "form": "SHA-256 of the RFC 8785 canonical JSON object {repo: [links_to sorted by code point]} "
                             "over every repo in this pulse"},
        "artifacts": artifacts,
        "generator": generator,
    }


def frame_index(sid, frames):
    """The optional rapp-frame-index/1 discovery index (it confers no trust): the stream, its frames, its head."""
    return {"schema": "rapp-frame-index/1", "stream_id": sid,
            "frames": [f"versions/{vid}/pulse.json" for _, vid in frames],
            "head": {"seq": frames[-1][0]["seq"], "frame_hash": frames[-1][0]["frame_hash"]}}


def chain_files(sid, record, frames):
    """The chain as Hive files: the identity record, the discovery index and every pulse (served as .json)."""
    wrap = subway().wrap
    out = {"rappid.json.md": wrap(f"/{PORTFOLIO}/rappid.json", pretty(record)),
           f"{INDEX_NAME}.md": wrap(f"/{PORTFOLIO}/{INDEX_NAME}", pretty(frame_index(sid, frames)))}
    for frame, vid in frames:
        out[f"versions/{vid}/pulse.json.md"] = wrap(f"/{PORTFOLIO}/versions/{vid}/pulse.json",
                                                   rapp().canonical(frame) + "\n")
    return out


def materialize(files, root):
    """Write wrapped Hive files as GitHub Pages serves them (permalink path, exact body); others as they are."""
    unwrap = subway().unwrap
    for rel_path, text in files.items():
        permalink = re.match(r"---\npermalink: /(\S+)\n", text)
        target = root / (permalink[1] if permalink and "{::nomarkdown}\n" in text else rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        body = unwrap(text) if permalink and "{::nomarkdown}\n" in text else text
        target.write_bytes(body.encode("utf-8"))


def rapp_check(root):
    done = run(sys.executable, "-B", str(CHECKER / "rapp_check.py"), str(root), "--json", timeout=900)
    try:
        result = json.loads(done.stdout)
    except ValueError:
        raise SystemExit(f"rapp_check.py gave no verdict for {root}: {done.stderr[-300:]}")
    return result


def check_chain(chain):
    """rapp-1's own rapp_check.py on the chain alone: COMPLIANT, every pulse passing, no finding at all."""
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / "chain"
        materialize(chain, root)
        result = rapp_check(root)
    frames = [e for e in result.get("evidence", []) if e.get("ok") == "RAPP/1 frame passes §7 envelope, hashes, and chain"]
    pulses = sum(1 for name in chain if name.endswith("pulse.json.md"))
    if result.get("verdict") != "COMPLIANT" or result.get("findings") or len(frames) != pulses:
        raise SystemExit(f"rapp_check.py refused the chain: {result.get('verdict')}, "
                         f"{len(result.get('findings') or [])} finding(s): {json.dumps(result.get('findings'))[:600]}")
    return {"verdict": result["verdict"], "frames": len(frames), "evidence": len(result.get("evidence", []))}


def certify_public(room_root):
    """rapp_check.py on the would-be public copy, twice: its files as they are (the Hive holds only markdown), and as
    GitHub Pages serves them (every wrapper unwrapped to its permalink)."""
    files = {p.relative_to(room_root).as_posix(): p.read_text(encoding="utf-8")
             for p in sorted(room_root.rglob("*")) if p.is_file() and p.suffix == ".md"}
    out = {}
    with tempfile.TemporaryDirectory() as scratch:
        literal, served = Path(scratch) / "literal", Path(scratch) / "served"
        for rel_path, text in files.items():
            (literal / rel_path).parent.mkdir(parents=True, exist_ok=True)
            (literal / rel_path).write_text(text, encoding="utf-8")
        materialize(files, served)
        for name, root in (("files", literal), ("served", served)):
            result = rapp_check(root)
            out[name] = {"verdict": result.get("verdict"), "findings": len(result.get("findings") or []),
                         "evidence": len(result.get("evidence") or []),
                         "certified": result.get("verdict") in ("COMPLIANT", "CLEAN") and not result.get("findings")}
    return out


def conformance():
    """rapp-1's conformance suite at the pin: the reference implementation the pulses are built with."""
    done = run(sys.executable, "-B", "conformance.py", cwd=str(CHECKER), timeout=600)
    last = (done.stdout.strip().splitlines() or ["no output"])[-1]
    if done.returncode or " 0 FAIL" not in last:
        raise SystemExit(f"rapp-1 conformance.py did not pass at the pin: {last}")
    return last


def pulse_diff(prev, cur):
    """Status changes, new repos, removed repos, and how many repos moved to a new commit."""
    a, b = prev["payload"]["repos"], cur["payload"]["repos"]
    both = sorted(a.keys() & b.keys(), key=str.lower)
    changes = [(n, a[n]["status"], b[n]["status"]) for n in both if a[n]["status"] != b[n]["status"]]
    moved = sum(1 for n in both if a[n].get("evidence_commit") != b[n].get("evidence_commit"))
    return (changes, sorted(b.keys() - a.keys(), key=str.lower), sorted(a.keys() - b.keys(), key=str.lower), moved)


TIMELINE_CSS = """body{margin:0;background:#f6f8fa;color:#1b1f24;font:16px/1.5 Helvetica,Arial,sans-serif}
header{background:#fff;border-bottom:1px solid #d0d7de;padding:14px 24px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
header h1{font-size:22px;margin:0;flex:1}
a{color:#0969da;text-decoration:none}
main{max-width:1040px;margin:0 auto;padding:20px 24px 60px}
section,article{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:16px 20px;margin:0 0 16px}
h2{font-size:19px;margin:0 0 8px}
h3{font-size:18px;margin:0 0 6px}
code,pre{font:13px/1.45 Menlo,Consolas,monospace;overflow-wrap:anywhere}
pre{white-space:pre-wrap;background:#f6f8fa;border-radius:6px;padding:10px 12px;margin:8px 0}
dl{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:8px 0}
dt{font-weight:700;color:#57606a}
dd{margin:0}
.totals span{display:inline-block;margin-right:14px}
.c{color:#1a7f37;font-weight:700}.n{color:#9a6700;font-weight:700}.u{color:#57606a;font-weight:700}
.seq{color:#57606a;font-weight:400;font-size:15px}
.note{border-left:5px solid #dfb317}
ul{margin:4px 0 8px 20px;padding:0}
footer{color:#57606a;font-size:13px;margin-top:24px}"""


def timeline_html(sid, record, frames, public, facts):
    """Every pulse, newest first: its hashes, totals, files, and what changed since the pulse before it."""
    esc = subway().esc
    csp = ("default-src 'none'; style-src 'sha256-"
           + __import__("base64").b64encode(hashlib.sha256(TIMELINE_CSS.encode()).digest()).decode()
           + "'; base-uri 'none'; form-action 'none'")
    genesis, head = frames[0][0], frames[-1][0]
    when = lambda utc: f"{utc[:10]} {utc[11:16]} UTC"

    def totals(payload):
        t = payload["totals"]
        return (f'<p class="totals"><span>{t["stations"]} stations</span><span class="c">{t["certified"]} certified'
                f'</span><span class="n">{t["not yet"]} not yet</span><span class="u">{t["unchecked"]} unchecked</span></p>')

    genesis_entry = {"type": "genesis", "stream_id": sid, "frame_hash": genesis["frame_hash"], "deprecated": False}
    where = (f"in public. Every pulse is served as JSON beside its maps, and rapp_check.py still certifies this public copy: "
             f"{facts['certify']['files']['verdict']} on its files as they are (the Hive holds only markdown) and "
             f"{facts['certify']['served']['verdict']} on the files as GitHub Pages serves them, where each unsigned pulse "
             f"passes the §7 envelope, hash and chain checks (a body stream permits sig null)."
             if public else
             "in the private RAPP Hive. rapp_check.py would not certify this public copy with the unsigned pulses in it, so the frames "
             "stay in the private RAPP Hive until the estate owner authorizes a signer. This page and the version "
             "folders are public; each pulse's hashes are listed here so it can be matched when it is published.")
    parts = [f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
             f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
             f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n<meta name="referrer" content="no-referrer">\n'
             f'<title>RAPP/1 network: timeline of {len(frames)} version(s)</title>\n<style>{TIMELINE_CSS}</style>\n'
             f'</head>\n<body>\n<header><h1>RAPP/1 network · timeline</h1><a href="{PAGES}/subway.html">Latest map</a>'
             f'<a href="{PUBLIC_BLOB}/PORTFOLIO.md">Portfolio</a><a href="{INSTALLER}">Start here</a></header>\n<main>\n',
             '<section>\n<h2>One RAPP/1 frame per crawl</h2>\n'
             '<p>Each crawl of the RAPP/1 network is one pulse of its life: a RAPP/1 frame of the registered kind '
             '<code>body.pulse</code> on the network\'s body stream, chained to the pulse before it. Its payload holds '
             'the crawl time, the checker pin, the totals per status and per line, every repo\'s status, verdict and '
             'evidence commit, a digest of the links between repos, and the content hashes of that version\'s '
             '<code>PORTFOLIO.md</code> and maps.</p>\n<dl>\n'
             f'<dt>Stream</dt><dd><code>{esc(sid)}</code><br>Keyless, minted once ({esc(record.get("minted_utc", ""))}); '
             f'<a href="{PAGES}/rappid.json">rappid.json</a> · <a href="{PAGES}/{INDEX_NAME}">frame index</a></dd>\n'
             f'<dt>Genesis</dt><dd>payload_hash <code>{genesis["payload_hash"]}</code><br>frame_hash '
             f'<code>{genesis["frame_hash"]}</code></dd>\n'
             f'<dt>Head</dt><dd>version {head["payload"]["version"]} (seq {head["seq"]}), payload_hash '
             f'<code>{head["payload_hash"]}</code></dd>\n'
             f'<dt>Checked</dt><dd>Every pulse passes RAPP/1 §7.5 steps 1–5 with the reference <code>rapp.py</code>, and '
             f'rapp-1\'s own <code>rapp_check.py</code> at <code>{CANON_RAPP1[:7]}</code> gives the chain '
             f'{facts["chain"]["verdict"]} ({facts["chain"]["frames"]} frame(s) passing, no findings). The reference '
             f'implementation passes rapp-1\'s <code>conformance.py</code> ({esc(facts["conformance"])}).</dd>\n'
             f'</dl>\n</section>\n',
             '<section class="note">\n<h2>Signing and anchoring</h2>\n'
             '<p>The pulses are unsigned (<code>sig: null</code>), which RAPP/1 §10 allows on a body stream. Their hashes '
             'prove integrity and order, not authorship: do not infer who wrote a pulse from the frame. Attribution comes '
             'from the RAPP Hive, which committed each pulse in a signed save and published it in a signed commit of '
             f'<a href="https://github.com/{OWNER}/rapp-hive-public">kody-w/rapp-hive-public</a>. Anchoring comes later: '
             'the estate owner authorizes a signer (phase 4), and records this stream\'s creation genesis in the '
             'estate\'s signed registry (§13.3), with this entry:</p>\n'
             f'<pre>{esc(json.dumps(genesis_entry, separators=(", ", ": ")))}</pre>\n'
             f'<p>Where the pulses live: {esc(where)}</p>\n</section>\n',
             f'<h2>Versions ({len(frames)})</h2>\n']
    for k in range(len(frames) - 1, -1, -1):
        frame, vid = frames[k]
        payload, base = frame["payload"], f"{PAGES}/versions/{vid}"
        commit = facts["published"].get(vid)
        shipped = (f' · first published in <a href="https://github.com/{OWNER}/rapp-hive-public/commit/{commit}">'
                   f'{commit[:7]}</a>' if commit else " · published with this page")
        files = (f'<a href="{base}/subway.html">map</a> · <a href="{base}/subway.pdf">poster</a> · '
                 f'<a href="{base}/subway.svg">SVG</a> · <a href="{base}/pulse.json">pulse</a>' if public else
                 f'<a href="{base}/subway.html">map</a> · <a href="{base}/subway.pdf">poster</a> · '
                 f'<a href="{base}/subway.svg">SVG</a> · pulse kept private')
        parts.append(f'<article>\n<h3>Version {payload["version"]} · {when(payload["crawl"]["finished_utc"])} '
                     f'<span class="seq">seq {frame["seq"]}</span></h3>\n{totals(payload)}\n'
                     f'<p>payload_hash <code>{frame["payload_hash"]}</code><br>frame_hash <code>{frame["frame_hash"]}'
                     f'</code><br>prev <code>{frame["prev"] or "null"}</code></p>\n<p>{files}{shipped}</p>\n')
        if k == 0:
            parts.append(f'<p>Genesis: the first pulse, {payload["totals"]["stations"]} repos. Nothing before it to '
                         f'compare.</p>\n')
        else:
            changes, new, removed, moved = pulse_diff(frames[k - 1][0], frame)
            parts.append(f'<p><b>Since version {frames[k - 1][0]["payload"]["version"]}:</b> {len(changes)} status '
                         f'change(s), {len(new)} new repo(s), {len(removed)} removed, {moved} repo(s) at a new commit.</p>\n')
            if changes:
                parts.append("<ul>" + "".join(f"<li>{esc(n)}: {esc(a)} → {esc(b)}</li>" for n, a, b in changes)
                             + "</ul>\n")
            if new:
                parts.append("<p>New: " + ", ".join(f"{esc(n)} ({esc(payload['repos'][n]['status'])})" for n in new)
                             + "</p>\n")
            if removed:
                parts.append("<p>Removed: " + ", ".join(esc(n) for n in removed) + "</p>\n")
        parts.append("</article>\n")
    parts.append(f'<footer>Generated from the pulse frames by rapp1_portfolio.py (source in '
                 f'<a href="{PUBLIC_BLOB}/tools">portfolio/tools</a>, SHA-256 '
                 f'<code>{head["payload"]["generator"]["rapp1_portfolio.py"]}</code>).</footer>\n</main>\n</body>\n</html>\n')
    return "".join(parts)


TOOL_PURPOSE = {
    "rapp1_portfolio.py": ("The crawler. It finds the RAPP family, crawls every repo with rapp-1's own rapp_check.py, "
                           "writes the portfolio files and badges, emits one RAPP/1 body.pulse per crawl, keeps each "
                           "version's maps, builds the timeline, then saves through the Hive and publishes."),
    "rapp1_subway.py": ("The map generator. It draws every portfolio repo as a station on its family's line and writes "
                        "the SVG, the zoomable HTML and the one-page PDF."),
}


def tool_files():
    """This file and the map generator, byte for byte, as data for the public copy (a Hive never runs code)."""
    out = {}
    for name, purpose in TOOL_PURPOSE.items():
        source = (HERE / name).read_text(encoding="utf-8")
        if CODE_FENCE in source or RAW_END in source:
            raise SystemExit(f"{name} holds a sequence that would end its own block")
        out[f"tools/{name}.md"] = (
            f"# {name}\n\n{purpose}\n\nSHA-256 of the source below: `{sha256(source)}` "
            f"({len(source.encode('utf-8'))} bytes). Every pulse records it in `payload.generator`. Copy it out with the "
            f"extractor in [README.md](README.md); code in a Hive is data, never run from the Hive.\n\n"
            f"{RAW_START}\n{CODE_FENCE}python\n{source}{CODE_FENCE}\n{RAW_END}\n")
    out["tools/README.md"] = (
        "# Tools\n\nThe two standard-library Python files that made this portfolio, exactly as they ran for the latest "
        "version. Each `.py.md` holds one source file in a fenced block, with its SHA-256 above it.\n\n"
        "Copy them out and check them (run this in a clone of `kody-w/rapp-hive-public`, inside `portfolio/tools/`):\n\n"
        "```bash\npython3 - <<'PY'\nimport hashlib, pathlib, re\nfence = chr(96) * 5\n"
        "for md in sorted(pathlib.Path('.').glob('*.py.md')):\n    text = md.read_text(encoding='utf-8')\n"
        "    source = text.split(fence + 'python\\n', 1)[1].rsplit(fence + '\\n', 1)[0]\n"
        "    want = re.search(r'SHA-256 of the source below: .([0-9a-f]+).', text).group(1)\n"
        "    assert hashlib.sha256(source.encode('utf-8')).hexdigest() == want, md.name\n"
        "    pathlib.Path(md.name[:-3]).write_text(source, encoding='utf-8')\n    print('ok', md.name[:-3], want)\nPY\n```\n\n"
        "Check the published chain (no Hive needed; it clones rapp-1 at the pin):\n\n"
        "```bash\npython3 -B rapp1_portfolio.py verify ../\n```\n\n"
        "Crawl again and cut the next version (needs git, a signed-in `gh`, Chrome, and a Hive with `hive_agent.py` from "
        "`kody-w/rapp-model-hive`):\n\n"
        "```bash\npython3 -B rapp1_portfolio.py crawl --hive-agent <path to hive_agent.py> [--denylist <private scanner>]\n```\n")
    return out


def published_commits(frames):
    """For each version already public: the public copy's commit that first carried its pulse (a signed Hive commit)."""
    try:
        public = public_dir()
    except SystemExit:
        return {}
    out = {}
    for _, vid in frames:
        log = run("git", "-C", str(public), "log", "--format=%H", "--diff-filter=A", "--",
                  f"{PORTFOLIO}/versions/{vid}/pulse.json.md").stdout.split()
        if log:
            out[vid] = log[-1]
    return out


def restore_hive():
    """Put every hand edit in the Hive back as its last commit had it (a failed crawl leaves nothing behind)."""
    agent = hive_agent()
    os.environ["RAPP_HIVES"] = str(HIVES)
    h = agent.Hive(str(HIVES), HIVE)
    head = agent.tree(h.path, h.head())
    for path in h.edits():
        full = HIVE_DIR / path
        if path in head:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_bytes(agent.blobs(h.path, [head[path][1]])[0])
        elif full.is_file() or full.is_symlink():
            full.unlink()
    print("restored the Hive's work tree to its last commit")


def hive_edits():
    agent = hive_agent()
    os.environ["RAPP_HIVES"] = str(HIVES)
    return agent.Hive(str(HIVES), HIVE).edits()


class CrawlLock:
    """One writer per stream (two writers would fork it): an exclusive lock file for the whole crawl."""

    def __enter__(self):
        LOCAL.mkdir(parents=True, exist_ok=True)
        self.path = LOCAL / "crawl.lock"
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            pid = (self.path.read_text().strip() or "0")
            if pid.isdigit() and pid != "0":
                try:
                    os.kill(int(pid), 0)
                    raise SystemExit(f"another crawl is running (pid {pid}); one writer per stream")
                except ProcessLookupError:
                    pass
            self.path.unlink()
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def cut():
    """The next version: portfolio files, the version's maps, its pulse (verified), the stable maps, the timeline and
    the tools, written into the Hive room, checked, then saved in one signed commit. Returns the version facts."""
    maps, reference = subway(), rapp()
    crawl = crawl_record()
    recs, prs = records(), load(DATA / "prs.json", {})
    home = chain_home() or CHAIN_PUBLIC
    sid, record, frames = read_chain(chain_home())
    minted = sid is None
    if minted:
        sid, record = mint_stream()
    sys.path.insert(0, str(CHECKER))
    import rapp_registry  # noqa: E402  (rapp-1's own §6.1.1 stream forms)
    if rapp_registry.stream_form(sid) != "body-stream":  # body.pulse is family body: a bare-rappid stream (§7.2)
        raise SystemExit(f"{sid} is not a body-stream, so it cannot carry {PULSE_KIND}")
    head = frames[-1][0] if frames else None
    seq, utc = (head["seq"] + 1 if head else 0), utc_now()
    if head and utc < head["utc"]:
        raise SystemExit(f"this clock ({utc}) is behind the head pulse ({head['utc']}); a pulse never goes back (§7.4)")
    vid = f"{utc[:10]}-{seq}"
    version = {"number": seq + 1, "utc": crawl["finished_utc"], "stream_id": sid, "id": vid}
    room = CHAIN_PUBLIC
    keep = ("versions/", "subway.", "timeline.", "rappid.", f"{INDEX_NAME}.", "tools/")
    write_room(room, portfolio_files(recs, prs, version), keep=keep)
    readme = HIVE_DIR / ROOM / "README.md"
    text = readme.read_text(encoding="utf-8")
    if public_readme(text) != text:
        readme.write_text(public_readme(text), encoding="utf-8", newline="\n")
    # this version's maps, drawn from the files just written; a version folder never changes once saved
    versions = maps.chain(home) + [(seq + 1, vid, crawl["finished_utc"])]
    files, L = maps.render(room, version, maps.nav_for(versions, current=seq + 1), prefix=f"versions/{vid}/", pdf=True)
    artifacts = {"PORTFOLIO.md": {"sha256": sha256((room / "PORTFOLIO.md").read_bytes()),
                                  "bytes": len((room / "PORTFOLIO.md").read_bytes())}}
    for name, text in files.items():
        body = maps.served(name, text)
        artifacts[name[:-3]] = {"sha256": sha256(body), "bytes": len(body)}
    generator = {name: sha256((HERE / name).read_bytes()) for name in TOOL_PURPOSE}
    payload = pulse_payload(recs, seq + 1, crawl, artifacts, generator)
    frame = reference.build_frame(PULSE_KIND, sid, seq, utc, payload, head["payload_hash"] if head else None,
                                  prev_wave=None, sig=None)
    ok, step, why = reference.verify_frame(frame, head=head, stream_id_of_record=sid)
    size = len(reference.canonical(frame).encode("utf-8"))
    if not ok or size > reference.MAX_CANONICAL_BYTES:
        raise SystemExit(f"the new pulse fails RAPP/1 §7.5 step {step}: {why}" if not ok else
                         f"the new pulse is {size} bytes, over RAPP/1's 1 MiB")
    frames = frames + [(frame, vid)]
    chain = chain_files(sid, record, frames)
    facts = {"chain": check_chain(chain), "conformance": conformance(), "published": published_commits(frames[:-1])}
    for name, text in files.items():
        (room / f"versions/{vid}/{name}").parent.mkdir(parents=True, exist_ok=True)
        (room / f"versions/{vid}/{name}").write_text(text, encoding="utf-8", newline="\n")
    for rel_path, text in chain.items():
        path = home / rel_path
        if path.is_file() and rel_path.startswith("versions/") and path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{rel_path} changed since it was saved; a pulse never changes")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    # the stable path always shows the latest map, with a picker for every version
    stable, _ = maps.render(room, version, maps.nav_for(versions))
    stable["subway.pdf.md"] = files["subway.pdf.md"].replace(f"/{PORTFOLIO}/versions/{vid}/subway.pdf",
                                                             f"/{PORTFOLIO}/subway.pdf", 1)
    for name in ("subway.svg.md", "subway.pdf.md"):  # the same bytes as the version's, at the stable URL
        assert maps.served(name, stable[name]) == maps.served(name, files[name])
    tools = tool_files()
    for rel_path, text in {**stable, **tools}.items():
        (room / rel_path).parent.mkdir(parents=True, exist_ok=True)
        (room / rel_path).write_text(text, encoding="utf-8", newline="\n")
    facts["certify"] = certify_public(HIVE_DIR / ROOM)
    public = home == CHAIN_PUBLIC and facts["certify"]["files"]["certified"] and facts["certify"]["served"]["certified"]
    if not public and home == CHAIN_PUBLIC:  # keep the frames in the private Hive until a signer is authorized
        for rel_path in chain:
            (CHAIN_PRIVATE / rel_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(room / rel_path), str(CHAIN_PRIVATE / rel_path))
    (room / "timeline.html.md").write_text(
        maps.wrap(f"/{PORTFOLIO}/timeline.html", timeline_html(sid, record, frames, public, facts)),
        encoding="utf-8", newline="\n")
    return {"sid": sid, "minted": minted, "frame": frame, "vid": vid, "public": public, "facts": facts,
            "stations": len(L["repos"]), "interchanges": len(L["interchange"])}


def crawl(args):
    """The one command: discover, crawl, cut the next version, save it through the Hive, publish, check Pages."""
    with CrawlLock():
        ensure_checker()
        if hive_edits():
            raise SystemExit("the Hive has unsaved edits; save or put them back before a crawl")
        discover()
        sweep(["--workers", str(MAX_WORKERS)])
        try:
            cut_facts = cut()
            scan_tree(HIVE_DIR / ROOM, *( [CHAIN_PRIVATE] if CHAIN_PRIVATE.exists() else []))
            saved = signed_save()
        except BaseException:
            restore_hive()
            raise
        f = cut_facts["frame"]
        print(f"pulse: version {f['payload']['version']} (seq {f['seq']}) on {cut_facts['sid']}")
        print(f"  payload_hash {f['payload_hash']}\n  frame_hash   {f['frame_hash']}\n  prev         {f['prev']}")
        print(f"  chain: rapp_check {cut_facts['facts']['chain']['verdict']} ({cut_facts['facts']['chain']['frames']} "
              f"frame(s)); public copy: files {cut_facts['facts']['certify']['files']['verdict']}, served "
              f"{cut_facts['facts']['certify']['served']['verdict']}; pulses {'public' if cut_facts['public'] else 'private'}")
        print(f"  saved in Hive commit {saved}")
        commit = publish()
        if "--no-wait" not in args:
            wait_for_pages(commit, cut_facts)
        status()


def wait_for_pages(commit, cut_facts, timeout=900):
    """Wait for GitHub Pages to build the pushed commit, then check the new version's URLs against the local bytes."""
    import urllib.request
    repo = f"{OWNER}/{public_dir().name}"
    deadline, state = time.time() + timeout, ""
    while time.time() < deadline:
        state = run("gh", "api", f"repos/{repo}/pages/builds/latest", "--jq", '.status + " " + .commit').stdout.strip()
        if state == f"built {commit}":
            break
        if state.startswith("errored"):
            raise SystemExit(f"the Pages build failed: {state}")
        time.sleep(15)
    else:
        raise SystemExit(f"Pages did not build {commit[:10]} in {timeout} s (last: {state})")
    vid, room, maps = cut_facts["vid"], CHAIN_PUBLIC, subway()
    checks = [f"subway.html.md", "subway.pdf.md", "timeline.html.md", f"versions/{vid}/subway.html.md",
              f"versions/{vid}/subway.pdf.md"] + ([f"versions/{vid}/pulse.json.md", f"{INDEX_NAME}.md", "rappid.json.md"]
                                                  if cut_facts["public"] else [])
    for rel_path in checks:
        text = (room / rel_path).read_text(encoding="utf-8")
        url = PAGES + "/" + re.match(r"---\npermalink: /portfolio/(\S+)\n", text)[1]
        with urllib.request.urlopen(url, timeout=60) as response:
            body, kind = response.read(), response.headers.get("content-type", "")
        same = body == maps.served(rel_path, text)
        print(f"  {url}: {response.status} {kind.split(';')[0]}" + (", identical" if same else ", DIFFERS"))
        if not same:
            raise SystemExit(f"{url} does not serve the published bytes yet")


# ---- publish: the Hive's own path, then the push ------------------------------------------------

def publish():
    public = public_dir()
    do(action="publish", hive=HIVE, path=ROOM)
    do(action="publish", hive=HIVE, path=f"members/{member()}/publish/{Path(ROOM).name}.md")
    problems = hive_agent().check_public(str(public), str(HIVE_DIR))
    print("check-public --hive:", problems or "no problems")
    if problems:
        raise SystemExit("check-public failed; nothing was pushed")
    scan_tree(public)
    run("git", "-C", str(public), "fetch", "-q", "origin", check=True)
    if DENYLIST is not None:
        done = run(sys.executable, "-B", str(DENYLIST), "commits", str(public), "origin/main..main")
        print("privacy scan (commits):", done.stdout.strip().splitlines()[-1])
        if done.returncode:
            raise SystemExit("the commit scan found something; nothing was pushed")
    push = run("git", "-C", str(public), "push", "-q", "origin", "main")
    print("push:", "ok" if push.returncode == 0 else push.stderr.strip()[-300:])
    if push.returncode:
        raise SystemExit(1)
    commit = run("git", "-C", str(public), "rev-parse", "HEAD").stdout.strip()
    print("public copy at", commit)
    return commit


def verify(args):
    """Every pulse in a portfolio folder (the Hive room, or a public copy's portfolio/): the chain from genesis, the
    discovery index, rapp_check.py on the chain, and each version's files against the hashes its pulse recorded."""
    folder = Path(args[0]).expanduser().resolve() if args else (chain_home() or CHAIN_PUBLIC)
    folder = folder / PORTFOLIO if (folder / PORTFOLIO / "rappid.json.md").is_file() else folder
    sid, record, frames = read_chain(folder)
    if not frames:
        raise SystemExit(f"{folder}: no pulse chain here")
    maps, problems = subway(), []
    index = json.loads(maps.unwrap((folder / f"{INDEX_NAME}.md").read_text(encoding="utf-8")))
    if index != frame_index(sid, frames):
        problems.append(f"{INDEX_NAME} does not name exactly these frames and this head")
    chain = {p.relative_to(folder).as_posix(): p.read_text(encoding="utf-8") for p in
             [folder / "rappid.json.md", folder / f"{INDEX_NAME}.md", *sorted(folder.glob("versions/*/pulse.json.md"))]}
    checked = check_chain(chain)
    for frame, vid in frames:
        for name, want in frame["payload"]["artifacts"].items():
            path = folder / (name if name == "PORTFOLIO.md" else f"versions/{vid}/{name}.md")
            if name == "PORTFOLIO.md" and frame is not frames[-1][0]:
                continue  # an older version's PORTFOLIO.md lives in the history of the copy it was published in
            body = path.read_bytes() if name == "PORTFOLIO.md" else maps.served(path.name, path.read_text(encoding="utf-8"))
            if sha256(body) != want["sha256"]:
                problems.append(f"versions/{vid}: {name} differs from its pulse")
    for problem in problems:
        print("problem:", problem)
    print(f"stream {sid}: {len(frames)} pulse(s) verified from genesis (§7.5 steps 1-5); rapp_check {checked['verdict']} "
          f"({checked['frames']} frame(s)); head version {frames[-1][0]['payload']['version']} payload_hash "
          f"{frames[-1][0]['payload_hash']}; {'no problems' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


def status():
    recs = records()
    for wave in (1, 2):
        c = Counter(r["status"] for r in recs.values() if r["wave"] == wave)
        print(f"wave {wave}: " + ", ".join(f"{s} {c.get(s, 0)}" for s in STATUSES) + f" (of {sum(c.values())})")
    for line in LINES:
        c = Counter(r["status"] for r in recs.values() if r["family"] == line["id"])
        if sum(c.values()):
            print(f"  {line['name']}: {sum(c.values())} (" + ", ".join(f"{s} {c.get(s, 0)}" for s in STATUSES) + ")")
    home = chain_home()
    if home is not None:
        sid, _, frames = read_chain(home)
        if frames:
            head = frames[-1][0]
            print(f"stream {sid}: head version {head['payload']['version']} (seq {head['seq']}), payload_hash "
                  f"{head['payload_hash']}; pulses {'public' if home == CHAIN_PUBLIC else 'private'}")


if __name__ == "__main__":
    argv = [a for a in sys.argv[1:]]
    for flag in ("--work", "--hives", "--hive", "--hive-agent", "--checker", "--denylist"):
        if flag in argv:
            at = argv.index(flag)
            del argv[at:at + 2]
    mode, rest = (argv[0] if argv else "status"), argv[1:]
    if mode == "crawl":
        crawl(rest)
    elif mode == "discover":
        discover()
    elif mode == "sweep":
        sweep(rest)
    elif mode == "publish":
        publish()
    elif mode == "verify":
        raise SystemExit(verify(rest))
    elif mode == "header":
        raise SystemExit(header_cli(rest))
    elif mode == "status":
        status()
    else:
        raise SystemExit(__doc__)
`````
{% endraw %}
