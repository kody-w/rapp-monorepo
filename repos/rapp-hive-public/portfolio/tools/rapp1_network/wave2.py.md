# `rapp1_network/wave2.py`

Wave 2 of the network header: a dry run now, the pull requests only after the owner approves (from legacy/rapp1_wave2.py).

Source: `rapp1_network/wave2.py` (rapp1-network 0.1.9). SHA-256 of the source below: `7f6d71e2d08ee41c0a4adba40ef1d42094e4bd3c78e63bfd179a976bc61d637f` (39604 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/wave2.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Wave 2 of the network header: a dry run now, the pull requests only after the owner approves
(from legacy/rapp1_wave2.py).

    plan                                                     the dry run, from the crawl's records (no clones)
    open --rehearse [--limit N] [--only a,b]                 everything but the push
    open --owner-approved [--limit N] [--only a,b] [--pace 5]

`plan` writes <work>/wave2/plan.json, DRY-RUN.md and samples/*.diff: for every wave-2 repo, whether a README exists,
the exact action, and why a repo is held for a hand-made PR (receipts that pin the README's bytes, a generated README,
or tests that read it). `open` handles only the rows the plan marks `auto`, one at a time: a fresh shallow clone, the
README's facts checked again on it with the crawler's own rules, the header, a commit with the kody-w noreply identity
and both Copilot trailers, the private scanner's diff scan, a push of rapp1/network-header and an ordinary PR (never
merged, never a push to a default branch). It paces about one PR per 5 s and backs off on GitHub's secondary rate
limits. Repos already in data/prs.json are skipped, so a re-run resumes.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from . import headers, prs, util
from .config import Settings
from .constants import BRANCH, OWNER, PAGES, PUBLIC_REPO, REPO_URL, TITLE, TRAILERS
from .lines import LINE
from .privacy import Denylist

GENERATED_FROM = "the sweep's fresh clones (data/family.json, sweep/*.record.json)"
COMMAND = "python -m rapp1_network wave2 open --owner-approved --denylist <private scanner>"
APPROVAL = ("wave 2 opens PRs only after the owner approves: re-run with --owner-approved "
            "(or --rehearse to stop before any push)")
RATE_LIMITED = re.compile(r"rate limit|abuse|submitted too quickly|http 429", re.I)
MAX_SAMPLES = 16


def out_dir(settings: Settings) -> Path:
    return settings.work / "wave2"


def family(settings: Settings) -> list[dict]:
    """data/family.json (as inventory.family reads it); refuses when there is none yet."""
    entries = util.load(settings.data / "family.json")
    if not entries or not isinstance(entries, list):
        raise SystemExit("run discover first: there is no data/family.json")
    return entries


def decide(item: dict, rec: dict) -> dict:
    """The item with its action (auto, manual, none or skip) and why, from a record's README facts alone."""
    item = dict(item)
    if not rec.get("evidence_commit"):
        return {**item, "action": "skip", "why": rec.get("reason") or "not crawled yet"}
    readme = rec.get("readme", "")
    if not readme:
        return {**item, "action": "skip", "why": "no README"}
    if not rec.get("readme_markdown"):
        return {**item, "action": "skip", "why": f"README is not markdown ({readme})"}
    action, pinned, tests = rec.get("header_action", ""), rec.get("readme_receipts", []), rec.get(
        "readme_test_readers", [])
    item.update(readme_sha256=rec.get("readme_sha256"), header_action=action, evidence_commit=rec["evidence_commit"])
    if action.startswith("manual"):
        item.update(action="manual", why=action.split(": ", 1)[-1])
    elif action == "unchanged":
        item.update(action="none", why="the header is already current")
    elif pinned:
        item.update(action="manual", why="tracked files pin the README's exact bytes: " + ", ".join(pinned[:6])
                    + (f" and {len(pinned) - 6} more" if len(pinned) > 6 else ""))
    elif rec.get("readme_generated"):
        item.update(action="manual", why="the README says it is generated; change its source instead")
    elif tests:
        item.update(action="manual", why="tests read README.md (run them before a PR): " + ", ".join(tests[:4])
                    + (f" and {len(tests) - 4} more" if len(tests) > 4 else ""))
    else:
        item.update(action="auto", why=action)
    return item


def plan_one(settings: Settings, entry: dict) -> tuple[dict, str | None]:
    """(the plan row for one repo, its header diff or None), from its crawl record alone."""
    repo = entry["repo"]
    rec = util.load(settings.sweep / f"{repo}.record.json", {}) or {}
    item = {"repo": repo, "family": entry["family"], "line": LINE[entry["family"]]["name"],
            "status": rec.get("status", "unchecked"), "default_branch": entry["default_branch"],
            "readme": rec.get("readme", ""), "readme_exists": bool(rec.get("readme"))}
    item = decide(item, rec)
    return item, (rec.get("header_diff") or None) if item["action"] in ("auto", "manual", "none") else None


def pick_samples(items: list[dict]) -> list[str]:
    """One sample diff per (action, header action), then one per line among the automatic ones; at most 16."""
    wanted, seen = [], set()
    for item in items:
        key = (item["action"], item.get("header_action"))
        if item["action"] in ("auto", "manual") and item.get("header_action") and key not in seen:
            seen.add(key)
            wanted.append(item["repo"])
    for item in items:
        if item["action"] == "auto" and item["family"] not in {i["family"] for i in items if i["repo"] in wanted}:
            wanted.append(item["repo"])
    return wanted[:MAX_SAMPLES]


def report(items: list[dict], samples: list[str], diffs: dict[str, str]) -> str:
    """DRY-RUN.md."""
    counts = Counter(i["action"] for i in items)
    fam = Counter(i["line"] for i in items)
    fam_auto = Counter(i["line"] for i in items if i["action"] == "auto")
    lines = ["# RAPP/1 network header: wave 2 dry run", "",
             "Nothing here has been pushed. `open` acts only on the `auto` rows, after the owner approves:", "",
             f"    {COMMAND}", "",
             f"- Repos: {len(items)} (public, unarchived, non-fork kody-w repos in the RAPP family, outside wave 1; "
             "denylist hits are held back in a local-only report).",
             f"- Actions: {counts.get('auto', 0)} automatic PRs, {counts.get('manual', 0)} held for a hand-made PR, "
             f"{counts.get('skip', 0)} skipped, {counts.get('none', 0)} already current.",
             f"- READMEs: {sum(i['readme_exists'] for i in items)} exist; "
             f"{sum(1 for i in items if not i['readme_exists'] and i['action'] == 'skip')} repos have none or are "
             "empty.", "",
             "| Line (family) | Repos | Automatic PRs |", "|---|---|---|"]
    lines += [f"| {f} | {n} | {fam_auto.get(f, 0)} |" for f, n in sorted(fam.items())]
    lines += ["", "## Every repo", "", "| Repo | Line | RAPP/1 status | README | Action | Detail |",
              "|---|---|---|---|---|---|"]
    for i in sorted(items, key=lambda i: (i["line"], i["repo"].lower())):
        lines.append(f"| {i['repo']} | {i['line']} | {i['status']} | {i['readme'] or 'none'} | {i['action']} | "
                     f"{i['why'].replace('|', '/')} |")
    lines += ["", "## Sample diffs", ""]
    for repo in samples:
        lines += [f"### {repo}", "", "```diff", diffs[repo].rstrip("\n"), "```", ""]
    return "\n".join(lines)


def plan(settings: Settings, say=print) -> list[dict]:
    """The dry run: <work>/wave2/plan.json, DRY-RUN.md and samples/<repo>.diff. Pushes nothing, clones nothing."""
    out = out_dir(settings)
    items, diffs = [], {}
    for entry in family(settings):
        if entry["wave"] != 2:
            continue
        item, diff = plan_one(settings, entry)
        items.append(item)
        if diff:
            diffs[item["repo"]] = diff
    util.dump(out / "plan.json", {"generated_from": GENERATED_FROM, "repos": items})
    samples = pick_samples(items)
    (out / "samples").mkdir(parents=True, exist_ok=True)
    for repo in samples:
        util.write_text(out / "samples" / f"{repo}.diff", diffs[repo])
    util.write_text(out / "DRY-RUN.md", report(items, samples, diffs))
    say(f"wave 2: {len(items)} repos; actions: {dict(Counter(i['action'] for i in items))}")
    say(f"by line: {dict(sorted(Counter(i['line'] for i in items).items()))}")
    say(f"wrote {out / 'DRY-RUN.md'}, {out / 'plan.json'} and {len(samples)} sample diffs")
    return items


def gh_with_backoff(gh, args, *, attempts: int = 6, sleep=time.sleep, say=print):
    """gh with retries on GitHub's rate limits (secondary included): 60 s, doubling, at most 900 s a wait. Any
    other failure returns at once."""
    done = None
    for attempt in range(attempts):
        done = prs.gh_run(gh, *args)
        if done.returncode == 0 or not RATE_LIMITED.search(done.stderr or ""):
            return done
        if attempt + 1 < attempts:
            wait = min(60 * 2 ** attempt, 900)
            say(f"  rate limited; waiting {wait} s (attempt {attempt + 1}/{attempts})")
            sleep(wait)
    return done


def crawl_rules():
    """(readme_facts, tracked): the crawler's own README facts, checked again on the fresh clone."""
    from .crawl import readme_facts, tracked
    return readme_facts, tracked


def _open_one(settings, item, clone, deny, gh, *, remote, rehearse, rules, sleep, say) -> str:
    repo = item["repo"]
    done = util.run(*prs.GIT, "clone", "-q", "--depth", "1", f"{remote}{repo}.git", str(clone),
                    env={"GIT_LFS_SKIP_SMUDGE": "1"})
    if done.returncode:
        return f"failed (git clone: {done.stderr.strip()[-200:]})"
    readme_facts, tracked = rules
    facts = readme_facts(clone, tracked(clone), repo)
    if facts.get("readme") != item["readme"]:
        return f"skipped: the README is now {facts.get('readme') or 'gone'!r}, not {item['readme']!r}; re-plan"
    fresh = decide(item, {**facts, "evidence_commit": prs.git(clone, "rev-parse", "HEAD")})
    if fresh["action"] != "auto":
        return f"skipped: now {fresh['action']}: {fresh['why']}"
    base = prs.git(clone, "rev-parse", "--abbrev-ref", "HEAD")
    if base == BRANCH:
        return f"skipped: the default branch is {BRANCH}"
    prs.git(clone, "checkout", "-q", "-b", BRANCH)
    try:
        action = headers.apply_header_file(clone / item["readme"], repo)
    except ValueError as error:
        return f"skipped: manual: {error}"
    if action == "unchanged":
        return "already current"
    prs.git(clone, "add", "--", item["readme"])
    prs.commit(clone, prs.message(repo))
    scan = deny.diff(clone, f"origin/{base}")
    if not scan.ok:
        return "privacy scan found something; not pushed"
    if rehearse:
        stat = prs.git(clone, "show", "--stat", "--format=%an <%ae>%n%s%n%(trailers:only)", "HEAD")
        return (f"rehearsed ({action}; {scan.line('diff')}); would push {BRANCH} and open a PR against {base}\n    "
                + stat.replace("\n", "\n    "))
    if prs.git(clone, "ls-remote", "--heads", "origin", BRANCH):
        return f"skipped: {BRANCH} already exists on the remote; finish it with the wave-1 helper"
    prs.git(clone, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    made = gh_with_backoff(gh, ["pr", "create", "-R", f"{OWNER}/{repo}", "--base", base, "--head", BRANCH,
                                "--title", TITLE, "--body", prs.body(repo)], sleep=sleep, say=say)
    if made.returncode:
        return f"failed (gh pr create: {made.stderr.strip()[-300:]})"
    url = made.stdout.strip().splitlines()[-1]
    recs = prs.records(settings)
    recs[repo] = {"url": url, "number": int(url.rstrip("/").rsplit("/", 1)[1]), "state": "OPEN", "branch": BRANCH,
                  "base": base, "head": prs.git(clone, "rev-parse", "HEAD"), "wave": 2}
    prs.save(settings, recs)
    return url


def open_prs(settings: Settings, args, deny: Denylist | None, gh=prs.GH, *, remote: str = REPO_URL,
             sleep=time.sleep, clock=time.monotonic, rules=None, say=print) -> dict[str, str]:
    """Open the plan's automatic PRs (see the module docstring); {repo: outcome} for each one tried.
    Refuses without --owner-approved (or --rehearse), and --owner-approved refuses without the private scanner."""
    args = list(args)
    rehearse = "--rehearse" in args  # everything up to the push, then stop: nothing leaves this machine
    if "--owner-approved" not in args and not rehearse:
        raise SystemExit(APPROVAL)
    if not rehearse:
        prs.need_scanner(deny, "wave 2")
    deny = deny if deny is not None else Denylist(None, warn=say)
    plan_data = util.load(out_dir(settings) / "plan.json")
    if not plan_data:
        raise SystemExit("run plan first")
    only = {n for n in util.arg(args, "--only", "").split(",") if n}
    try:
        limit, pace = int(util.arg(args, "--limit", "0")), float(util.arg(args, "--pace", "5"))
    except ValueError:
        raise SystemExit("--limit takes a whole number and --pace a number of seconds") from None
    recorded = prs.records(settings)
    queue = [i for i in plan_data["repos"] if i["action"] == "auto" and (not only or i["repo"] in only)
             and i["repo"] not in recorded]
    if limit:
        queue = queue[:limit]
    rules = rules or crawl_rules()
    clones = out_dir(settings) / "clones"
    clones.mkdir(parents=True, exist_ok=True)
    say(f"{'rehearsing' if rehearse else 'opening'} {len(queue)} PR(s), one about every {pace:g} s")
    outcomes = {}
    for n, item in enumerate(queue, 1):
        repo, started = prs.check_name(item["repo"]), clock()
        clone = clones / repo
        try:
            util.remove_tree(clone)
            outcomes[repo] = _open_one(settings, item, clone, deny, gh, remote=remote, rehearse=rehearse,
                                       rules=rules, sleep=sleep, say=say)
        except (SystemExit, OSError, UnicodeDecodeError, RuntimeError) as error:
            outcomes[repo] = f"failed ({str(error)[:200]})"
        finally:
            util.remove_tree(clone)
        say(f"[{n}/{len(queue)}] {repo}: {outcomes[repo]}")
        if n < len(queue):
            sleep(max(0.0, pace - (clock() - started)))
    say("done; next: `prs ci` for the PRs' checks; the next crawl shows them in the portfolio")
    return outcomes


# ---- wave 2 with member cards (v0.1.7) -----------------------------------------------------------------------------
# `plan --cards` extends the header plan above (which stays version 1's, byte for byte) with each repo's card: a fresh
# depth-1 clone checks that nothing pins the tracked tree (a new file would break such a receipt), asks the network's
# card generator (member_cards.py plan) whether it can write the card, and notes whether pull requests run CI. `open
# --cards` then opens one PR per `auto` row on the header branch: the header (when due) and the card, nothing else.

CARD = ".rapp/member.md"
CARD_IGNORE_RULE = (".rapp/*", "!.rapp/member.md")
CARD_TOOL, RESOLVER = "member_cards.py", "hive_resolve.py"
CARD_PLAN, CARD_REPORT = "plan-cards.json", "CARDS-PLAN.md"
TITLE_BOTH = "RAPP/1 network header and member card"
TITLE_CARD = "RAPP/1 member card: .rapp/member.md"
KINDS = ("header+card", "card", "header")
TREE_MARKERS = (b"tracked_path_count", b"tracked_path_set_sha256", b"path_set_sha256", b"tracked_paths",
                b"inventory_sha256", b"check-manifest", b"check_manifest", b"sdist is missing")
RECEIPT_WORDS = ("manifest", "inventory", "files", "checksum", "sha256", "boundary", "provenance")
STRUCTURED = frozenset((".json", ".txt", ".yml", ".yaml", ".toml", ".csv", ".sha256", ".lst", ".list", ""))
MAX_READ = 1_000_000  # bytes of one tracked file the receipt check reads
PATH_TOKEN = re.compile(rb"[A-Za-z0-9_./@+-]+")
TEST_PATH = re.compile(r"(^|/)(tests?|spec)/|(^|/)test_[^/]*\.py$|\.test\.[mc]?[jt]s$")
PR_TRIGGERS = (re.compile(r"(?m)^\s*['\"]?pull_request(?:_target)?['\"]?\s*:"),
               re.compile(r"(?m)^\s*['\"]?on['\"]?\s*:[^\n#]*\bpull_request(?:_target)?\b"))
TOOL_TIMEOUT = 300


def card_tools(settings: Settings) -> tuple[Path, Path]:
    """(member_cards.py, hive_resolve.py) from --card-tools; refused when either is missing."""
    if settings.card_tools is None:
        raise SystemExit(f"wave 2 with cards needs --card-tools DIR (the folder of {CARD_TOOL} and {RESOLVER})")
    tools = (Path(settings.card_tools) / CARD_TOOL, Path(settings.card_tools) / RESOLVER)
    missing = [str(path) for path in tools if not path.is_file()]
    if missing:
        raise SystemExit(f"--card-tools: missing {', '.join(missing)}")
    return tools


def regular_files(root) -> dict[str, str]:
    """{path: mode} of the checkout's tracked regular files (index modes 100644 and 100755)."""
    done = util.run(*prs.GIT, "-C", str(root), "ls-files", "-s", "-z")
    if done.returncode:
        raise RuntimeError(f"git ls-files failed: {done.stderr.strip()[-160:]}")
    out = {}
    for item in done.stdout.split("\0"):
        meta, _, path = item.partition("\t")
        mode = meta.split(" ", 1)[0]
        if path and mode in ("100644", "100755"):
            out[path] = mode
    return out


def _read(root: Path, path: str) -> bytes | None:
    full = root / path
    try:
        if full.is_symlink() or not full.is_file() or full.stat().st_size > MAX_READ:
            return None
        data = full.read_bytes()
    except OSError:
        return None
    return None if b"\0" in data[:8192] else data


def tree_receipts(root, files: dict[str, str] | None = None) -> list[str]:
    """Tracked files that pin the tracked path set, so the card (a new file) would break them: any tracked text file
    holding a path-set receipt's marker or an sdist completeness check, and any structured or test file (JSON, text,
    YAML, TOML, CSV, a checksum list, one named for a manifest, inventory, file list, boundary or provenance, or a
    test/spec file) that names at least half of the other tracked files (at least three). A receipt-like file too large
    to read is one too: nothing is assumed away."""
    root = Path(root)
    files = regular_files(root) if files is None else files
    found = []
    for path in sorted(files):
        base = path.rsplit("/", 1)[-1].lower()
        ext = base[base.rfind("."):] if "." in base else ""
        receipt_like = ext in STRUCTURED or any(word in base for word in RECEIPT_WORDS) or TEST_PATH.search(path)
        data = _read(root, path)
        if data is None:
            try:
                too_large = (root / path).stat().st_size > MAX_READ and not (root / path).is_symlink()
            except OSError:
                too_large = False
            if too_large and receipt_like and any(word in base for word in RECEIPT_WORDS):
                found.append(f"{path}: a receipt-like file too large to check")
            continue
        marks = [mark.decode() for mark in TREE_MARKERS if mark in data]
        if marks:
            found.append(f"{path} ({', '.join(marks)})")
            continue
        if receipt_like:
            others = [other for other in files if other != path]
            tokens = set(PATH_TOKEN.findall(data))
            listed = sum(1 for other in others if other.encode() in tokens or f"./{other}".encode() in tokens)
            if len(others) >= 3 and listed >= 3 and 2 * listed >= len(others):
                found.append(f"{path} lists {listed} of the {len(others)} other tracked files")
    return found


def pr_ci(root, files: dict[str, str]) -> bool:
    """Whether a workflow under .github/workflows/ runs on pull requests."""
    for path in files:
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            data = _read(Path(root), path)
            text = data.decode("utf-8", "replace") if data else ""
            if any(trigger.search(text) for trigger in PR_TRIGGERS):
                return True
    return False


def _card_args(settings: Settings, tool: Path, *more: str) -> list[str]:
    return [sys.executable, "-B", str(tool), *more, "--portfolio", str(settings.portfolio_dir),
            "--family", str(settings.data / "family.json")]


def card_verdict(settings: Settings, tools, repo: str, clones: Path) -> list[str]:
    """The card generator's own reasons to hold this repo's card (member_cards.py plan), [] when it can write it."""
    done = util.run(*_card_args(settings, tools[0], "plan"), "--clones", str(clones), "--repos", repo,
                    timeout=TOOL_TIMEOUT)
    if done.returncode:
        return [f"the card generator failed: {done.stderr.strip()[-200:]}"]
    try:
        rows = json.loads(done.stdout)["repos"]
    except (ValueError, KeyError, TypeError):
        return ["the card generator gave no plan"]
    row = next((r for r in rows if r.get("repo") == repo), None)
    if row is None:
        return ["the card generator did not plan it"]
    return list(row.get("reasons", [])) if row.get("action") != "auto" else []


def combine(item: dict, facts: dict) -> dict:
    """One row of the card plan, from the header plan's row and the fresh clone's facts: `kind` (header+card, card,
    header or none) and `action` (auto, hold, skip or none), with why."""
    row = {key: item[key] for key in ("repo", "family", "line", "status", "readme")}
    row.update(header=item["action"], header_why=item["why"], ci=bool(facts.get("ci")),
               receipts=list(facts.get("receipts", [])), card_hold=list(facts.get("card_hold", [])),
               card_present=bool(facts.get("card_present")))
    header, why = item["action"], item["why"]
    no_readme = header == "skip" and (why == "no README" or why.startswith("README is not markdown"))
    if header == "skip" and not no_readme:
        return {**row, "kind": "none", "action": "skip", "why": why}
    if facts.get("error"):
        return {**row, "kind": "none", "action": "skip", "why": f"the clone failed ({facts['error']}); re-plan"}
    if header == "manual":
        return {**row, "kind": "none", "action": "hold", "why": f"README held: {why}"}
    wants_header, wants_card = header == "auto", not row["card_present"]
    if not wants_header and not wants_card:
        return {**row, "kind": "none", "action": "none", "why": "the header and the card are current"}
    if row["receipts"]:
        shown = "; ".join(row["receipts"][:3]) + (f"; and {len(row['receipts']) - 3} more" if len(row["receipts"]) > 3
                                                   else "")
        return {**row, "kind": "none", "action": "hold", "why": f"tracked files pin the tree: {shown}"}
    if wants_card and row["card_hold"]:
        return {**row, "kind": "none", "action": "hold", "why": "the card generator holds it: "
                + "; ".join(row["card_hold"][:3])}
    kind = "header+card" if wants_header and wants_card else ("header" if wants_header else "card")
    detail = {"header+card": f"header ({why}) and card", "card": f"card only ({why})" if no_readme else
              "card only (the header is current)", "header": "header only (the card is current)"}[kind]
    return {**row, "kind": kind, "action": "auto", "why": detail}


def clone_repo(clone: Path, url: str, attempts: int = 3, sleep=time.sleep) -> str:
    """"" when `url` is cloned at depth 1 into `clone`, else git's error (after `attempts` tries)."""
    error = ""
    for attempt in range(attempts):
        util.remove_tree(clone)
        done = util.run(*prs.GIT, "clone", "-q", "--depth", "1", "--no-tags", url, str(clone),
                        env={"GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}, timeout=TOOL_TIMEOUT)
        if done.returncode == 0:
            return ""
        error = done.stderr.strip()[-200:] or f"exit {done.returncode}"
        if attempt + 1 < attempts:
            sleep(5 * (attempt + 1))
    return error


def card_facts(settings: Settings, tools, repo: str, clones: Path, remote: str, sleep=time.sleep) -> dict:
    """A fresh clone's facts for the card plan: its tree receipts, its CI, whether the card is there, and the card
    generator's reasons to hold it. The clone is deleted, whatever happened."""
    clone = clones / prs.check_name(repo)
    try:
        error = clone_repo(clone, f"{remote}{repo}.git", sleep=sleep)
        if error:
            return {"error": error}
        files = regular_files(clone)
        return {"receipts": tree_receipts(clone, files), "ci": pr_ci(clone, files), "card_present": CARD in files,
                "card_hold": card_verdict(settings, tools, repo, clones)}
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        return {"error": f"{type(error).__name__}: {str(error)[:160]}"}
    finally:
        util.remove_tree(clone)


def card_report(rows: list[dict]) -> str:
    """CARDS-PLAN.md."""
    counts = Counter(r["action"] for r in rows)
    kinds = Counter(r["kind"] for r in rows if r["action"] == "auto")
    lines = ["# RAPP/1 wave 2: headers and member cards (plan)", "",
             "Nothing here has been pushed. `open --cards` acts only on the `auto` rows, after the owner approves:",
             "", f"    {COMMAND} --cards --card-tools <folder>", "",
             f"- Repos: {len(rows)}. Actions: {counts.get('auto', 0)} automatic PRs ({kinds.get('header+card', 0)} "
             f"header and card, {kinds.get('card', 0)} card only, {kinds.get('header', 0)} header only), "
             f"{counts.get('hold', 0)} held, {counts.get('skip', 0)} skipped, {counts.get('none', 0)} current.",
             f"- Pull requests run CI in {sum(r['ci'] for r in rows if r['action'] == 'auto')} of the automatic repos.",
             "", "| Repo | Line | Kind | Action | CI | Detail |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["action"], r["line"], r["repo"].lower())):
        lines.append(f"| {r['repo']} | {r['line']} | {r['kind']} | {r['action']} | {'yes' if r['ci'] else 'no'} | "
                     f"{r['why'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def plan_cards(settings: Settings, say=print, *, workers: int = 6, remote: str = REPO_URL,
               sleep=time.sleep) -> list[dict]:
    """The card plan: <work>/wave2/plan-cards.json and CARDS-PLAN.md, from the header plan's rows and each wave-2
    repo's fresh depth-1 clone (deleted after its check). Pushes nothing."""
    tools = card_tools(settings)
    items = [plan_one(settings, entry)[0] for entry in family(settings) if entry["wave"] == 2]
    clones = out_dir(settings) / "plan-clones"
    clones.mkdir(parents=True, exist_ok=True)
    say(f"card plan: {len(items)} wave-2 repos, {workers} fresh clones at a time")
    with cf.ThreadPoolExecutor(max(1, workers)) as pool:
        facts = list(pool.map(lambda i: card_facts(settings, tools, i["repo"], clones, remote, sleep), items))
    rows = [combine(item, fact) for item, fact in zip(items, facts)]
    util.dump(out_dir(settings) / CARD_PLAN, {"generated_from": "the header plan and fresh depth-1 clones",
                                              "repos": rows})
    util.write_text(out_dir(settings) / CARD_REPORT, card_report(rows))
    say(f"card plan: {dict(Counter(r['action'] for r in rows))}; automatic kinds: "
        f"{dict(Counter(r['kind'] for r in rows if r['action'] == 'auto'))}")
    say(f"wrote {out_dir(settings) / CARD_REPORT} and {out_dir(settings) / CARD_PLAN}")
    return rows


def card_section(repo: str) -> list[str]:
    """The card's paragraphs of a wave-2 PR body."""
    pointer = f"https://github.com/{OWNER}/{PUBLIC_REPO}/blob/main/members/{quote(repo, safe='')}.md"
    return [f"**Member card** (`{CARD}`): this repo's card in the RAPP Hive, the RAPP/1 network's distributed Hive. It "
            f"says what the repo is, its line on the [RAPP/1 subway map]({PAGES}/subway.html), its neighbors, and the "
            f"Start here link; the Hive's public copy points to it from [`members/{repo}.md`]({pointer}). It follows "
            "section 8 (\"The card\") of the distributed-Hive contract (`DISTRIBUTED-HIVE.md` on "
            "`kody-w/rapp-model-hive`, branch `experimental/hive-md-distributed`); the network's card generator wrote "
            "it from the Hive's portfolio, and the network's resolver checked it.",
            "",
            "The card is markdown only: rapp-1's `rapp_check.py` reads only `.json` and `.egg` files, so this repo's "
            "RAPP/1 status and badge cannot change because of it, and the network's crawler leaves it out of this "
            "repo's links and counts. Change it with an ordinary commit; no `rappid.json` is added."]


def pr_title(kind: str) -> str:
    return {"header+card": TITLE_BOTH, "card": TITLE_CARD}.get(kind, TITLE)


def pr_body(repo: str, kind: str) -> str:
    if kind == "card":
        return "\n".join([f"Adds this repo's card for the RAPP/1 network's distributed Hive: one markdown file, "
                          f"`{CARD}`.", "", *card_section(repo)])
    if kind == "header+card":
        return "\n".join([prs.body(repo), "", *card_section(repo)])
    return prs.body(repo)


def pr_message(repo: str, kind: str) -> str:
    return f"{pr_title(kind)}\n\n{pr_body(repo, kind)}\n\n{TRAILERS}\n"


def write_card(settings: Settings, tools, repo: str, clone: Path) -> str | None:
    """Write the card with the network's generator into the checkout, check it with the resolver and the generator's
    --check; None when all is well, else why not."""
    wrote = util.run(*_card_args(settings, tools[0], "card"), "--repo", repo, "--checkout", str(clone),
                     timeout=TOOL_TIMEOUT)
    if wrote.returncode:
        return f"the card generator refused: {(wrote.stderr or wrote.stdout).strip()[-200:]}"
    valid = util.run(sys.executable, "-B", str(tools[1]), "validate", "card", CARD, "--repo", f"{OWNER}/{repo}",
                     cwd=str(clone), timeout=TOOL_TIMEOUT)
    if valid.returncode or not valid.stdout.startswith("ok:"):
        return f"the resolver refused the card: {(valid.stdout + valid.stderr).strip()[-200:]}"
    again = util.run(*_card_args(settings, tools[0], "card"), "--repo", repo, "--checkout", str(clone), "--check",
                     timeout=TOOL_TIMEOUT)
    if again.returncode:
        return f"the card generator's --check failed: {(again.stderr or again.stdout).strip()[-200:]}"
    return None


def _changed(clone: Path) -> set[str]:
    """Every path the checkout changed against its index: modified, deleted or new (untracked, not ignored)."""
    changed = set()
    for args in (("diff", "--name-only", "-z"), ("ls-files", "--others", "--exclude-standard", "-z")):
        done = util.run(*prs.GIT, "-C", str(clone), *args)
        if done.returncode:
            raise RuntimeError(f"git {args[0]} failed: {done.stderr.strip()[-160:]}")
        changed.update(path for path in done.stdout.split("\0") if path)
    return changed


def allow_card_while_ignoring_rapp(gitignore: Path) -> bool:
    """Replace a `.rapp/` directory ignore with rules that track only the member card.

    Git cannot re-include a file inside an ignored parent directory, so `!.rapp/` is unsafe: it exposes every
    untracked file under `.rapp/` to `git add -A`. The safe shape ignores the contents and negates only the card.
    """
    lines = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.is_file() else []
    out, changed, inserted = [], False, False
    for line in lines:
        stripped = line.strip()
        if stripped in CARD_IGNORE_RULE or stripped == "!.rapp/":
            changed = True
            continue
        if stripped in (".rapp/", "/.rapp/", ".rapp", "/.rapp"):
            if not inserted:
                out.extend(CARD_IGNORE_RULE)
                inserted = True
            changed = True
        else:
            out.append(line)
    if not inserted:
        out.extend(["", *CARD_IGNORE_RULE])
        changed = True
    if changed:
        gitignore.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return changed


def _open_card_pr(settings, row, clone, deny, gh, tools, *, remote, rehearse, rules, sleep, say) -> str:
    repo, kind = row["repo"], row["kind"]
    error = clone_repo(clone, f"{remote}{repo}.git", sleep=sleep)
    if error:
        return f"failed (git clone: {error})"
    files = regular_files(clone)
    head = prs.git(clone, "rev-parse", "HEAD")
    if "header" in kind:
        readme_facts, tracked = rules
        facts = readme_facts(clone, tracked(clone), repo)
        if facts.get("readme") != row["readme"]:
            return f"skipped: the README is now {facts.get('readme') or 'gone'!r}, not {row['readme']!r}; re-plan"
        fresh = decide({"repo": repo, "readme": row["readme"]}, {**facts, "evidence_commit": head})
        if fresh["action"] != "auto":
            return f"skipped: the header is now {fresh['action']}: {fresh['why']}; re-plan"
    receipts = tree_receipts(clone, files)
    if receipts:
        return f"skipped: now held: tracked files pin the tree: {receipts[0]}; re-plan"
    if "card" in kind and CARD in files:
        return "skipped: the card is there now; re-plan"
    base = prs.git(clone, "rev-parse", "--abbrev-ref", "HEAD")
    if base == BRANCH:
        return f"skipped: the default branch is {BRANCH}"
    if prs.git(clone, "ls-remote", "--heads", "origin", BRANCH):
        return f"skipped: {BRANCH} already exists on the remote; finish it by hand"
    prs.git(clone, "checkout", "-q", "-b", BRANCH)
    expected = set()
    if "header" in kind:
        try:
            action = headers.apply_header_file(clone / row["readme"], repo)
        except ValueError as problem:
            return f"skipped: manual: {problem}"
        if action == "unchanged":
            return "skipped: the header is current now; re-plan"
        expected.add(row["readme"])
    if "card" in kind:
        problem = write_card(settings, tools, repo, clone)
        if problem:
            return f"skipped: {problem}"
        expected.add(CARD)
    changed = _changed(clone)
    if changed != expected:
        return f"skipped: the checkout changed {sorted(changed)}, not exactly {sorted(expected)}"
    prs.git(clone, "add", "--", *sorted(expected))
    prs.commit(clone, pr_message(repo, kind))
    scan = deny.diff(clone, f"origin/{base}")
    if not scan.ok:
        return "privacy scan found something; not pushed"
    if rehearse:
        stat = prs.git(clone, "show", "--stat", "--format=%an <%ae>%n%s%n%(trailers:only)", "HEAD")
        return (f"rehearsed ({kind}; {scan.line('diff')}); would push {BRANCH} and open a PR against {base}\n    "
                + stat.replace("\n", "\n    "))
    prs.git(clone, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    made = gh_with_backoff(gh, ["pr", "create", "-R", f"{OWNER}/{repo}", "--base", base, "--head", BRANCH,
                                "--title", pr_title(kind), "--body", pr_body(repo, kind)], sleep=sleep, say=say)
    if made.returncode:
        return f"failed (gh pr create: {made.stderr.strip()[-300:]})"
    url = made.stdout.strip().splitlines()[-1]
    recs = prs.records(settings)
    recs[repo] = {"url": url, "number": int(url.rstrip("/").rsplit("/", 1)[1]), "state": "OPEN", "branch": BRANCH,
                  "base": base, "head": prs.git(clone, "rev-parse", "HEAD"), "wave": 2, "kind": kind}
    prs.save(settings, recs)
    return url


def open_card_prs(settings: Settings, args, deny: Denylist | None, gh=prs.GH, *, remote: str = REPO_URL,
                  sleep=time.sleep, clock=time.monotonic, rules=None, say=print) -> dict[str, str]:
    """`open --cards`: the card plan's `auto` rows, one PR each (see the section note above); {repo: outcome}.
    The same gates as `open`: --owner-approved (or --rehearse), and the private scanner for a real run."""
    args = list(args)
    rehearse = "--rehearse" in args
    if "--owner-approved" not in args and not rehearse:
        raise SystemExit(APPROVAL)
    if not rehearse:
        prs.need_scanner(deny, "wave 2")
    deny = deny if deny is not None else Denylist(None, warn=say)
    tools = card_tools(settings)
    plan_data = util.load(out_dir(settings) / CARD_PLAN)
    if not plan_data:
        raise SystemExit("run `wave2 plan --cards` first")
    only = [n for n in util.arg(args, "--only", "").split(",") if n]
    try:
        limit, pace = int(util.arg(args, "--limit", "0")), float(util.arg(args, "--pace", "5"))
    except ValueError:
        raise SystemExit("--limit takes a whole number and --pace a number of seconds") from None
    if pace < 5:
        raise SystemExit("--pace is at least 5 seconds a PR")
    rows = {r["repo"]: r for r in plan_data["repos"]}
    unknown = [n for n in only if n not in rows]
    if unknown:
        raise SystemExit(f"not in the card plan: {', '.join(unknown)}")
    recorded = prs.records(settings)
    order = only or [r["repo"] for r in plan_data["repos"]]
    queue = [rows[n] for n in order if rows[n]["action"] == "auto" and rows[n]["kind"] in KINDS
             and n not in recorded]
    if limit:
        queue = queue[:limit]
    rules = rules or crawl_rules()
    clones = out_dir(settings) / "clones"
    clones.mkdir(parents=True, exist_ok=True)
    say(f"{'rehearsing' if rehearse else 'opening'} {len(queue)} PR(s), one about every {pace:g} s")
    outcomes = {}
    for n, row in enumerate(queue, 1):
        repo, started = prs.check_name(row["repo"]), clock()
        clone = clones / repo
        try:
            outcomes[repo] = _open_card_pr(settings, row, clone, deny, gh, tools, remote=remote, rehearse=rehearse,
                                           rules=rules, sleep=sleep, say=say)
        except (SystemExit, OSError, UnicodeDecodeError, RuntimeError, subprocess.TimeoutExpired) as error:
            outcomes[repo] = f"failed ({str(error)[:200]})"
        finally:
            util.remove_tree(clone)
        say(f"[{n}/{len(queue)}] {repo}: {outcomes[repo]}")
        if n < len(queue):
            sleep(max(0.0, pace - (clock() - started)))
    return outcomes


def status(settings: Settings, args, gh=prs.GH, say=print) -> list[dict]:
    """The READY rows of the wave-2 PRs (all, or --only a,b): repo, URL, head, files, CI, state; into data/prs.json."""
    only = {n for n in util.arg(list(args), "--only", "").split(",") if n}
    recs, rows, updates = prs.records(settings), [], {}
    for repo in sorted(recs, key=str.lower):
        rec = dict(recs[repo])
        if rec.get("wave") != 2 or (only and repo not in only):
            continue
        view = gh_with_backoff(gh, ["pr", "view", str(rec["number"]), "-R", f"{OWNER}/{repo}", "--json",
                                    "state,headRefOid,statusCheckRollup,mergeable,files"], say=say)
        if view.returncode:
            say(f"{repo}: {view.stderr.strip()[-200:]}")
            continue
        info = json.loads(view.stdout)
        summary = prs.checks_summary(info.get("statusCheckRollup"))
        files = [f["path"] for f in info.get("files") or []]
        updates[repo] = {**rec, "state": info["state"], "ci": summary, "head": info["headRefOid"],
                         "mergeable": info.get("mergeable")}
        rows.append({"repo": repo, "url": rec["url"], "head": info["headRefOid"], "files": files, "ci": summary,
                     "state": info["state"], "mergeable": info.get("mergeable")})
        say(f"{repo} | {rec['url']} | {info['headRefOid']} | {', '.join(files)} | {summary} | "
            f"{info['state']}/{info.get('mergeable')}")
    current = prs.records(settings)
    for repo, rec in updates.items():
        current[repo] = {**current.get(repo, rec), **rec}
    prs.save(settings, current)
    return rows
`````
{% endraw %}
