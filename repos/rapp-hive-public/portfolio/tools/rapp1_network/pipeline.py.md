# `rapp1_network/pipeline.py`

The pipeline: cut the next version into the RAPP Hive, save it, publish it, check what Pages serves, and the one command that reruns it all (`crawl`: discover, sweep, cut, publish, the Pages check, status).

Source: `rapp1_network/pipeline.py` (rapp1-network 0.1.5). SHA-256 of the source below: `6807003cd7e817dfff055cfd4a8daa8876175fd9694f7ad70c738a5c9fde0be8` (41498 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/pipeline.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The pipeline: cut the next version into the RAPP Hive, save it, publish it, check what Pages serves, and the one
command that reruns it all (`crawl`: discover, sweep, cut, publish, the Pages check, status).

A cut, in order (docs/pulses.md "A cut"; legacy `cut()`): the full crawl it records, the verified chain (or the
stream's one mint), the time taken once, the portfolio files, the public README, the version's maps (picker 1..N,
the poster PDF), the pulse (built and verified by rapp-1's reference at the pin), rapp_check.py on the chain, the
stable maps (picker of every version), the release copy in tools/, rapp_check.py twice on the would-be public copy
and the placement, the chain files, the timeline; then the privacy scan, the Hive's own rules on every file, the
Hive's signed save, this device's head, and the local copies of the latest map. One writer at a time
(`<work>/local/crawl.lock`); a Hive with unsaved edits is refused; any failure puts the Hive's work tree back.

Every choice of an edition gets the version number: the portfolio files and both map renders get `version`
({number, utc, stream_id, id}), so a later edition is a data change in that module, not a rewiring here. Extra
per-repo facts join the records in one place, `network_facts()`.
"""
from __future__ import annotations

import concurrent.futures as cf
import contextlib
import dataclasses
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Callable, Mapping

from . import checker, export, inventory, lifecycle, portfolio, pulses, records, subway, timeline, util
from .config import Settings
from .constants import INDEX_NAME, MAX_WORKERS, OWNER, PAGES, PORTFOLIO, PUBLIC_REPO, REPO_URL, ROOM, STATUSES
from .hive import Hive, write_room
from .lines import LINES
from .privacy import Denylist, require
from .wrapping import Refused, permalink_of, served

MAPS = ("subway.svg.md", "subway.html.md", "subway.pdf.md")
STABLE = (*MAPS, "timeline.html.md")  # the latest map and the timeline, served at stable URLs
IMMUTABLE = (f"{PORTFOLIO}/versions/", *(f"{PORTFOLIO}/tools/{name}.md" for name in export.LEGACY_TOOLS))
LEAVES = (f"{PORTFOLIO}/repos/", f"{PORTFOLIO}/badges/", f"{PORTFOLIO}/lines/")  # go when their repo or line goes
PAGES_STATE = '.status + " " + .commit'


# ---- one writer ------------------------------------------------------------------------------------------------

class CrawlLock:
    """One writer per stream (two writers would fork it): `<work>/local/crawl.lock`, made exclusively, for the whole
    command. A lock left by a process that is gone (same host) is taken over; any other lock refuses."""

    def __init__(self, settings: Settings):
        self.path = settings.local / "crawl.lock"
        self.mine = b""

    def _refuse(self):
        raise SystemExit(f"another crawl or cut is running ({self._holder()}); one writer per stream "
                         f"(if none runs, delete {self.path})") from None

    def _create(self) -> None:
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        self.mine = json.dumps({"pid": os.getpid(), "host": socket.gethostname(),
                                "started": util.utc_now()}).encode("utf-8")
        os.write(fd, self.mine)
        os.close(fd)

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._create()
        except FileExistsError:
            try:
                seen = self.path.read_bytes()
            except OSError:
                seen = b""
            if self._alive(seen):
                self._refuse()
            self._take_over(seen)
        return self

    def _take_over(self, seen: bytes) -> None:
        """Take over a dead writer's lock atomically: move it aside under a name of our own, check that what moved is
        still the lock judged dead (`seen`), then create ours exclusively (a second taker finds nothing to move, or
        loses the exclusive create, and is refused)."""
        aside = self.path.with_name(f"{self.path.name}.stale-{os.getpid()}-{time.monotonic_ns()}")
        try:
            os.replace(self.path, aside)
        except FileNotFoundError:
            self._refuse()
        moved = aside.read_bytes()
        if moved != seen:  # another writer's fresh lock moved instead: put it back and refuse
            try:
                os.link(aside, self.path)
            except OSError:
                pass
            aside.unlink(missing_ok=True)
            self._refuse()
        aside.unlink(missing_ok=True)
        try:
            self._create()
        except FileExistsError:
            self._refuse()

    def _read(self, data: bytes | None = None) -> dict:
        try:
            text = (self.path.read_bytes() if data is None else data).decode("utf-8", "replace").strip()
        except OSError:
            return {}
        if text.isdigit():  # version 1 wrote the pid alone
            return {"pid": int(text), "host": socket.gethostname()}
        try:
            value = json.loads(text)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    def _holder(self) -> str:
        held = self._read()
        return f"pid {held.get('pid', '?')} on {held.get('host', '?')}, since {held.get('started', '?')}"

    def _alive(self, data: bytes | None = None) -> bool:
        held = self._read(data)
        pid = held.get("pid")
        if not isinstance(pid, int) or pid <= 0:  # being written this moment, or a crashed write of one
            try:
                return time.time() - self.path.stat().st_mtime < 30
            except OSError:
                return False
        if held.get("host") != socket.gethostname() or os.name == "nt":
            return True  # another device's lock, or Windows (os.kill(pid, 0) is not a probe there): keep it
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def __exit__(self, *exc):
        try:
            if self.mine and self.path.read_bytes() == self.mine:  # only our own lock, never another writer's
                self.path.unlink(missing_ok=True)
        except OSError:
            pass


# ---- the records a cut draws from ------------------------------------------------------------------------------

def held_back(settings: Settings) -> list[str]:
    """The repos the private denylist holds back now (local/denylist-held.json; never in any output)."""
    held = util.load(settings.local / "denylist-held.json", {}) or {}
    repos = held.get("repos") if isinstance(held, dict) else None
    return [r["repo"] for r in repos or () if isinstance(r, dict) and isinstance(r.get("repo"), str)]


def read_notices(hive: Hive, names) -> dict[str, dict]:
    """{repo: notice} from the notice files of the Hive's last commit (shared/organism/notices/<repo>.md: every one
    was saved by signed save, since a cut refuses unsaved edits), each with the Hive commit that last changed it.
    `names` are the repos a notice may name. An invalid notice file refuses the cut, naming the file and the rule."""
    out = {}
    for rel_path, text in sorted(hive.committed_texts(lifecycle.NOTICES + "/").items()):
        try:
            notice = lifecycle.parse_notice(rel_path, text, names)
        except Refused as error:
            raise SystemExit(f"a notice file breaks a rule, so nothing is cut: {error}") from None
        out[notice["repo"]] = {**notice, "commit": hive.last_commit(rel_path)}
    return out


def network_facts(settings: Settings, hive: Hive, recs: Mapping[str, dict], *, frames=(), today: str | None = None,
                  left: Mapping | None = None) -> dict[str, dict]:
    """Extra per-repo facts for this cut, {repo: {field: value}}: the one place such facts join the records. Each
    repo's channel and LTS pin (the LTS pins file, else the known pins), and its lifecycle: archived from GitHub (the
    family's `archived`, since carried from the head pulse), else a notice saved in the Hive, else active. `frames`
    is the verified chain before this cut, `today` the crawl's date, `left` the repos that left (lifecycle.left_repos),
    which a notice may still name."""
    if settings is None or not recs:
        return {}
    today = today or util.today_utc()
    pins, source = lifecycle.pins_for(settings)
    archived = {e["repo"] for e in inventory.family(settings) if e.get("archived")}
    notices = read_notices(hive, set(recs) | set(left or {})) if hive is not None else {}
    head = frames[-1][0]["payload"] if frames else {}
    life = lifecycle.lifecycle_facts(recs, archived=archived, notices=notices, previous=head.get("repos"), today=today)
    pinned = lifecycle.pin_facts(recs, pins, source)
    return {name: {**pinned[name], **life[name]} for name in recs}


def notice_names(settings: Settings) -> set[str]:
    """The repos a notice may name: the family, and the repos that left (their files, marked `left:`, stay)."""
    names = {e["repo"] for e in inventory.family(settings)}
    for path in sorted((settings.portfolio_dir / "repos").glob("*.md")):
        head = util.read_text(path)[:2000]
        if re.search(r"^left: \d{4}-\d{2}-\d{2}$", head.split("\n---\n", 1)[0], re.M):
            names.add(path.name[:-3])
    return names


def previous_stations(settings: Settings) -> set[str] | None:
    """The stations of the head pulse (the previous version), or None when there is no chain yet."""
    home = pulses.chain_home(settings)
    if home is None:
        return None
    _, _, frames = pulses.read_chain(home, settings.checker, pulses.known_head(settings))
    return set(frames[-1][0]["payload"]["repos"]) if frames else None


def merge_facts(recs: Mapping[str, dict], facts: Mapping[str, Mapping]) -> dict[str, dict]:
    """The records with each repo's extra facts added (a fact never replaces a crawl field)."""
    unknown = sorted(set(facts) - set(recs))
    if unknown:
        raise SystemExit(f"network facts for repos outside the portfolio: {', '.join(unknown[:5])}")
    out = {}
    for name, rec in recs.items():
        extra = dict(facts.get(name) or {})
        clash = sorted(set(extra) & set(rec))
        if clash:
            raise SystemExit(f"{name}: a network fact would replace the crawl's {', '.join(clash)}")
        out[name] = {**rec, **extra}
    return out


# ---- the cut -----------------------------------------------------------------------------------------------------

def _chain_paths(folder: Path) -> list[Path]:
    """The chain files in a home folder: the identity record, the index and every pulse."""
    found = [folder / f"{pulses.IDENTITY}.md", folder / f"{INDEX_NAME}.md", *sorted(folder.glob("versions/*/pulse.json.md"))]
    return [p for p in found if p.is_file()]


def _write_chain(home: Path, chain: Mapping[str, str]) -> None:
    for rel_path, text in chain.items():
        path = home.joinpath(*rel_path.split("/"))
        if path.is_file() and rel_path.startswith("versions/") and path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{rel_path} changed since it was saved; a pulse never changes")
        util.write_text(path, text)


def build(settings: Settings, hive: Hive, *, utc: str | None = None, printer=None, conformance: str | None = None,
          mint: bool = True, say: Callable[[str], None] = print) -> dict:
    """Build the next version into the Hive's work tree (nothing is saved): the steps of a cut up to the save.
    Returns the cut facts {sid, minted, frame, frames, vid, number, placement, public, facts, stations,
    interchanges, room, tools}."""
    chk = settings.checker
    crawl = pulses.crawl_record(settings)
    recs = records.records(settings)
    prs = util.load(settings.data / "prs.json", {}) or {}
    exceptions = portfolio.exceptions(settings)
    folder, private = settings.portfolio_dir, settings.private_chain_dir
    home = pulses.chain_home(settings)
    sid, record, frames = pulses.read_chain(home, chk, pulses.known_head(settings))
    today = crawl.get("started_utc", "")[:10] or util.today_utc()
    left = lifecycle.left_repos(frames, recs, held_back(settings), today)
    recs = merge_facts(recs, network_facts(settings, hive, recs, frames=frames, today=today, left=left))
    minted = sid is None
    if minted:
        if not mint:
            raise SystemExit("there is no pulse chain yet: a dry run never mints the stream; cut mints it once")
        sid, record = pulses.mint_stream(settings, chk)
    head = frames[-1][0] if frames else None
    if head is not None and crawl.get("started_utc", "") < head["payload"]["crawl"]["finished_utc"]:
        raise SystemExit(f"data/crawl.json is the crawl of {crawl.get('started_utc')}, not one after the head pulse's "
                         f"({head['payload']['crawl']['finished_utc']}): one pulse per crawl; run a full sweep first")
    utc = utc or util.utc_now()  # taken once: the pulse lands in the folder its maps are drawn in
    if head is not None and utc < head["utc"]:
        raise SystemExit(f"this clock ({utc}) is behind the head pulse ({head['utc']}); a pulse never goes back (§7.4)")
    seq = len(frames)
    number, vid = seq + 1, pulses.version_id({"utc": utc, "seq": seq})
    if (folder / "versions" / vid).exists() or (private / "versions" / vid).exists():
        raise SystemExit(f"versions/{vid}/ exists already; a version folder never changes")
    version = {"number": number, "utc": crawl["finished_utc"], "stream_id": sid, "id": vid}
    previous = frames[-1][0]["payload"] if frames else None
    room = write_room(folder, portfolio.portfolio_files(recs, prs, exceptions, version, left=left, previous=previous))
    readme = settings.room_dir / "README.md"
    if readme.is_file():
        text = util.read_text(readme)
        if portfolio.public_readme(text) != text:
            util.write_text(readme, portfolio.public_readme(text))
    versions = pulses.picker_versions(frames) + [(number, vid, crawl["finished_utc"])]
    files, L = subway.render(folder, version, subway.nav_for(versions, current=number), prefix=f"versions/{vid}/",
                             pdf=True, printer=printer)
    room_matches(folder, recs, left, L)
    sources = export.sources()
    generator = export.generator(sources)
    published = hive.published_commits(v for _, v in frames)
    copies = release_copies(hive, frames, published)
    history = [(f["payload"]["version"], v, f["payload"]["generator"], copies.get(v)) for f, v in frames]
    tools = export.tool_files(sources, release=export.provenance(), history=history + [(number, vid, generator, None)])
    notices = folder / portfolio.NOTICES_MD
    artifacts = pulses.artifacts_for((folder / "PORTFOLIO.md").read_bytes(), files,
                                     notices.read_bytes() if pulses.schema_for(number) >= 2 else None)
    payload = pulses.pulse_payload(recs, number, crawl, artifacts, generator, chk,
                                   left={name: entry["left"] for name, entry in left.items()})
    frame = pulses.build_pulse(chk, sid, seq, utc, payload, head, vid=vid)
    frames = frames + [(frame, vid)]
    chain = pulses.chain_files(sid, record, frames, chk)
    facts = {"chain": pulses.check_chain(chain, chk), "conformance": conformance or checker.conformance(chk),
             "published": published}
    write_room(folder, {f"versions/{vid}/{name}": text for name, text in files.items()}, generated=())
    stable, _ = subway.render(folder, version, subway.nav_for(versions))
    stable["subway.pdf.md"] = files["subway.pdf.md"].replace(f"/{PORTFOLIO}/versions/{vid}/subway.pdf",
                                                             f"/{PORTFOLIO}/subway.pdf", 1)
    for name in ("subway.svg.md", "subway.pdf.md"):  # the version's bytes, served at the stable URL too
        if served(name, stable[name]) != served(name, files[name]):
            raise SystemExit(f"the stable {name[:-3]} is not the version's")
    written = write_room(folder, {**stable, **tools}, generated=())
    certify = pulses.certify_public(settings.room_dir, chk, chain=chain)
    placement = pulses.placement(certify)
    public_before = home == folder and len(frames) > 1
    if placement == "private" and public_before:
        raise SystemExit("rapp_check.py would not certify the public copy with the new pulse in it, and the earlier "
                         "pulses are public: moving the chain to the private room would delete live URLs, so this "
                         "cut stops (nothing is saved)")
    target, other = (folder, private) if placement == "public" else (private, folder)
    for stale in _chain_paths(other):
        stale.unlink()
    _write_chain(target, chain)
    facts["certify"] = certify
    util.write_text(folder / "timeline.html.md",
                    timeline.timeline_file(sid, record, frames, placement == "public", facts))
    return {"sid": sid, "minted": minted, "frame": frame, "frames": frames, "vid": vid, "number": number,
            "placement": placement, "public": placement == "public", "facts": facts, "stations": len(L["repos"]),
            "interchanges": len(L["interchange"]), "room": room, "tools": written, "version": version,
            "left": sorted(left)}


def release_copies(hive: Hive, frames, published: Mapping[str, str]) -> dict[str, str]:
    """{vid: the public copy's commit that holds the release copy which made that version}: the commit that first
    carried the version, kept only when its tools/RELEASE.md records exactly that version's `generator` (two versions
    cut by different releases and published together would otherwise point at the later one)."""
    try:
        public = hive.public_dir()
    except SystemExit:
        return {}
    out = {}
    for frame, vid in frames:
        commit, gen = published.get(vid), frame["payload"].get("generator") or {}
        if not commit or not any(str(name).startswith(f"{export.PACKAGE}/") for name in gen):
            continue
        done = util.run("git", "-C", str(public), "show", f"{commit}:{PORTFOLIO}/tools/RELEASE.md")
        try:
            listed = json.loads(done.stdout.split("```json\n", 1)[1].split("```", 1)[0])
        except (IndexError, ValueError):
            continue
        if done.returncode == 0 and listed == gen:
            out[vid] = commit
    return out


def room_matches(folder: Path, recs: Mapping, left: Mapping, L: Mapping) -> None:
    """Refuse a version whose map, repo files and badges do not match its records: every repo of the pulse is a
    station, and every repo (and every repo that left) has its repo file and its badge under its exact name."""
    drawn, want = set(L["repos"]), set(recs)
    if drawn != want:
        missing, extra = sorted(want - drawn, key=str.lower), sorted(drawn - want, key=str.lower)
        raise SystemExit(f"the map does not match the records (not drawn: {missing[:5]}; not in the records: "
                         f"{extra[:5]}); nothing is saved")
    names = {kind: {p.name for p in (folder / kind).iterdir()} if (folder / kind).is_dir() else set()
             for kind in ("repos", "badges")}
    for repo in sorted({*recs, *left}, key=str.lower):
        if f"{repo}.md" not in names["repos"] or f"{repo}.svg.md" not in names["badges"]:
            raise SystemExit(f"repos/{repo}.md or badges/{repo}.svg.md is not in the room under that exact name "
                             "(a repo renamed only by case?); nothing is saved")


def summary(cut_facts: Mapping) -> list[str]:
    """The lines a cut prints: the pulse, its checks and its placement."""
    f, facts = cut_facts["frame"], cut_facts["facts"]
    certify = facts["certify"]
    return [f"pulse: version {f['payload']['version']} (seq {f['seq']}) on {cut_facts['sid']}",
            f"  payload_hash {f['payload_hash']}", f"  frame_hash   {f['frame_hash']}", f"  prev         {f['prev']}",
            f"  chain: rapp_check {facts['chain']['verdict']} ({facts['chain']['frames']} frame(s)); public copy: files "
            f"{certify['files']['verdict']}, served {certify['served']['verdict']}; without the chain: files "
            f"{certify['without']['files']['verdict']}, served {certify['without']['served']['verdict']}; pulses "
            f"{cut_facts['placement']}",
            f"  map: {cut_facts['stations']} stations, {cut_facts['interchanges']} interchanges; conformance: "
            f"{facts['conformance']}"] + (
        ["  lifecycle: " + ", ".join(f"{n} {life}" for life, n in f["payload"]["totals"]["lifecycle"].items())]
        if isinstance(f["payload"]["totals"].get("lifecycle"), dict) else [])


def scan_room(settings: Settings, deny: Denylist, say=print) -> None:
    """The private scanner in tree mode on the published room and the private pulse room, before a save."""
    folders = [settings.room_dir] + ([settings.private_chain_dir] if settings.private_chain_dir.exists() else [])
    require(deny.tree(*folders), "tree", "nothing was saved or published", say=say)


def _edits_plan(hive: Hive) -> dict[str, list[str]]:
    edits, head = hive.edits(), hive.committed()
    return {"added": sorted(p for p, d in edits.items() if d is not None and p not in head),
            "changed": sorted(p for p, d in edits.items() if d is not None and p in head),
            "deleted": sorted(p for p, d in edits.items() if d is None)}


def cut(settings: Settings, *, hive: Hive | None = None, deny: Denylist | None = None, dry_run: bool = False,
        utc: str | None = None, printer=None, conformance: str | None = None, lock: bool = True,
        say: Callable[[str], None] = print) -> dict:
    """Build the next version from the current records into the Hive room and save it (one signed commit), then
    remember the head and write the local copies. With dry_run: build it in a scratch copy of the Hive under
    <work>/scratch/ instead, run every check a cut runs, print the plan, and never save, publish or push."""
    hive = hive or Hive(settings, say=say)
    deny = deny or Denylist(settings.denylist, warn=say)
    with CrawlLock(settings) if lock else contextlib.nullcontext():
        checker.ensure_checker(settings.checker)
        if hive.edits():
            raise SystemExit("the Hive has unsaved edits; save or put them back before a cut")
        if dry_run:
            return dry_run_cut(settings, hive, deny, utc=utc, printer=printer, conformance=conformance, say=say)
        release = export.provenance()
        if release["commit"] and not release["clean"]:
            say(f"warning: the package has local changes at {release['commit'][:10]}; RELEASE.md will say so")
        try:
            facts = build(settings, hive, utc=utc, printer=printer, conformance=conformance, say=say)
            for line in summary(facts):
                say(line)
            scan_room(settings, deny, say=say)
            saved = hive.signed_save()
            if saved is None:
                raise SystemExit("the Hive saved nothing; the cut is not saved")
        except BaseException:
            hive.restore()
            raise
        say(f"  saved in Hive commit {saved}")
        pulses.remember_head(settings, facts["sid"], facts["frames"])
        local_copies(settings, say=say)
        return {**facts, "saved": saved}


# ---- the dry run ------------------------------------------------------------------------------------------------

def _git(*args) -> str:
    done = util.run("git", "-c", "core.autocrlf=false", "-c", "core.longpaths=true", *args)
    if done.returncode:
        raise SystemExit(f"git {args[0]} failed: {done.stderr.strip()[-300:]}")
    return done.stdout


def scratch_copy(settings: Settings, hive: Hive, where: Path) -> Settings:
    """A copy of the Hive (its committed files) and of its public copy under `where`/hives/, with the Hive's device
    state limited to its name and its public copy (no key, no shared copy address, so nothing there can sign, sync
    or push). The settings that point at it."""
    hives = where / "hives"
    _git("clone", "-q", "--no-hardlinks", str(hive.path), str(hives / settings.hive))
    device = {k: v for k, v in hive.state("device.json").items() if k in ("name", "fingerprint", "root")}
    util.dump(hives / settings.hive / ".git" / "rapp-hive" / "device.json", device)
    public = hive.state("public.json").get("name")
    if public:
        util.dump(hives / settings.hive / ".git" / "rapp-hive" / "public.json", {"name": public})
        source = settings.hives / public
        if (source / ".git").exists():
            _git("clone", "-q", "--no-hardlinks", str(source), str(hives / public))
            (hives / public / ".git" / "rapp-hive").mkdir(parents=True, exist_ok=True)
            _git("-C", str(hives / public), "remote", "remove", "origin")  # a scratch copy never pushes
    return dataclasses.replace(settings, hives=hives)


def dry_run_cut(settings: Settings, hive: Hive, deny: Denylist, *, utc=None, printer=None, conformance=None,
                say=print) -> dict:
    stamp = re.sub(r"[^0-9]", "", util.utc_now())[:14]
    where = settings.work / "scratch" / f"cut-dry-run-{stamp}"
    if where.exists():
        raise SystemExit(f"{where} exists already; try again in a second")
    where.mkdir(parents=True)
    scratch = scratch_copy(settings, hive, where)
    copy = Hive(scratch, say=say, agent=hive.agent)
    facts = build(scratch, copy, utc=utc, printer=printer, conformance=conformance, mint=False, say=say)
    for line in summary(facts):
        say(line)
    checked = copy.check_edits()
    say(f"  the Hive's own rules (text_rules): all {checked} file(s) the save would commit pass")
    scan_room(scratch, deny, say=say)
    plan = _edits_plan(copy)
    live = []
    if (scratch.hives / (copy.state("public.json").get("name") or "-") / ".git").exists():
        before = public_tree(copy.public_dir())
        live = kept_problems(before, {p[len(ROOM) + 1:]: v[1] for p, v in _work_tree(copy, ROOM + "/").items()})
    plan_facts = {"added": plan["added"], "changed": plan["changed"], "deleted": plan["deleted"],
                  "unchanged": facts["room"]["unchanged"] + facts["tools"]["unchanged"], "live_url_problems": live,
                  "pulse": {k: facts["frame"][k] for k in ("seq", "prev", "payload_hash", "frame_hash", "utc")},
                  "placement": facts["placement"], "scratch": str(where)}
    util.dump(where / "plan.json", plan_facts)
    say(f"dry run: {len(plan['added'])} file(s) added, {len(plan['changed'])} changed, {len(plan['deleted'])} "
        f"deleted, {len(plan_facts['unchanged'])} generated file(s) unchanged")
    for kind in ("added", "changed", "deleted"):
        for rel_path in plan[kind][:60]:
            say(f"  {kind}: {rel_path}")
        if len(plan[kind]) > 60:
            say(f"  ... and {len(plan[kind]) - 60} more {kind} (see plan.json)")
    say(f"  new pulse: seq {facts['frame']['seq']}, prev {facts['frame']['prev']}, payload_hash "
        f"{facts['frame']['payload_hash']}; placement {facts['placement']}")
    say("  live URLs: " + ("every file served now stays" if not live else "; ".join(live[:10])))
    say(f"dry run only: nothing was saved, published or pushed; the scratch copy and plan.json are in {where}")
    return {**facts, "dry_run": True, "plan": plan_facts, "scratch": where}


def _work_tree(hive: Hive, prefix: str) -> dict[str, tuple[str, str]]:
    """{path: (mode, blob id)} of the Hive's work tree under prefix (its committed state plus its edits)."""
    files = hive.committed(prefix)
    for rel_path, data in hive.edits().items():
        if not rel_path.startswith(prefix):
            continue
        if data is None:
            files.pop(rel_path, None)
        elif isinstance(data, bytes):
            files[rel_path] = ("100644", util.git_blob_id(data))
    return files


# ---- publishing, and what stays live ----------------------------------------------------------------------------

def _has(folder: Path, ref: str) -> bool:
    return util.run("git", "-C", str(folder), "rev-parse", "-q", "--verify", ref + "^{commit}").returncode == 0


def public_tree(folder: Path, ref: str = "HEAD") -> dict[str, str]:
    """{path: blob id} of a commit of the public copy (its last one by default; empty before its first publish)."""
    if not _has(folder, ref):
        return {}
    out = {}
    listing = _git("-C", str(folder), "ls-tree", "-r", "-z", "--full-tree", ref)
    for record in listing.split("\0"):
        if record:
            meta, path = record.split("\t", 1)
            out[path] = meta.split()[2]
    return out


def kept_problems(before: Mapping[str, str], after: Mapping[str, str]) -> list[str]:
    """What a publish would break among the portfolio's live files: a file served now that it would delete
    (only a repo's or a line's own files go, with their repo or line), or a file that never changes (a version's
    files, version 1's tools) that it would change."""
    problems = []
    for path, blob in sorted(before.items()):
        if not path.startswith(f"{PORTFOLIO}/"):
            continue
        if path not in after:
            if not path.startswith(LEAVES):
                problems.append(f"{path}: served now, and the publish would delete it")
            elif not path.startswith(f"{PORTFOLIO}/lines/"):
                name = path.rsplit("/", 1)[-1].removesuffix(".svg.md").removesuffix(".md")
                if f"{PORTFOLIO}/repos/{name}.md" in after or f"{PORTFOLIO}/badges/{name}.svg.md" in after:
                    problems.append(f"{path}: served now, and the publish would delete it while its repo stays")
        elif path.startswith(IMMUTABLE) and after[path] != blob:
            problems.append(f"{path}: never changes once published, and the publish would change it")
    return problems


def publish(settings: Settings, *, hive: Hive | None = None, deny: Denylist | None = None, lock: bool = True,
            say: Callable[[str], None] = print) -> str:
    """The Hive's own publish of the saved room, check-public, the privacy scans, then the push of the public copy
    (never forced). Refuses before anything moves when the publish would delete or change a live file of the
    portfolio. Returns the public copy's commit. Also the retry after a failed push."""
    hive = hive or Hive(settings, say=say)
    deny = deny or Denylist(settings.denylist, warn=say)
    with CrawlLock(settings) if lock else contextlib.nullcontext():
        if hive.edits():
            raise SystemExit("the Hive has unsaved edits; save (cut) or put them back before a publish")
        public = hive.public_dir()
        if not (public / ".git").exists():
            raise SystemExit(f"{public}: the Hive's public copy is not a git repository here")
        _git("-C", str(public), "fetch", "-q", "origin")
        live = _has(public, "origin/main")
        before = public_tree(public, "origin/main" if live else "HEAD")  # what Pages serves now
        room = {p[len(ROOM) + 1:]: v[1] for p, v in hive.committed(ROOM + "/").items()}
        problems = kept_problems(before, room)
        if problems:
            raise SystemExit("the publish would break live URLs; nothing was published:\n" + "\n".join(problems[:20]))
        held = public_tree(public)
        if held and {p: b for p, b in held.items() if p not in ("PUBLISHED.md", ".gitattributes")} == room:
            say("the public copy already holds exactly the saved room; nothing to publish")
        else:
            hive.publish()
        problems = hive.check_public(public)
        say("check-public --hive: " + ("; ".join(problems) if problems else "no problems"))
        if problems:
            raise SystemExit("check-public failed; nothing was pushed")
        problems = kept_problems(before, public_tree(public))
        if problems:
            raise SystemExit("the published copy would break live URLs; nothing was pushed:\n" + "\n".join(problems[:20]))
        require(deny.tree(public), "tree", "nothing was pushed", say=say)
        _git("-C", str(public), "fetch", "-q", "origin")
        live = _has(public, "origin/main")
        require(deny.commits(public, "origin/main..main" if live else "main"), "commits", "nothing was pushed", say=say)
        push = util.run("git", "-C", str(public), "push", "-q", "origin", "main")
        say("push: " + ("ok" if push.returncode == 0 else push.stderr.strip()[-300:]))
        if push.returncode:
            raise SystemExit("the push failed; run publish again to retry")
        commit = _git("-C", str(public), "rev-parse", "HEAD").strip()
        say(f"public copy at {commit}")
        return commit


def _fetch(url: str, timeout: int = 60) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "rapp1-network"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.headers.get("content-type", ""), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("content-type", "") if error.headers else "", b""
    except (urllib.error.URLError, OSError) as error:
        return 0, str(error)[:120], b""


def expected_urls(settings: Settings, cut_facts: Mapping | None = None) -> dict[str, tuple[str, object]]:
    """{url: (kind, want)} of what the published portfolio serves: every wrapped file of the room at its permalink
    with its exact bytes (the stable maps, the timeline, every version's maps, and the chain when it is public),
    each badge of a repo in the portfolio (an SVG of its status), and PORTFOLIO.html (the rendered table)."""
    folder, out = settings.portfolio_dir, {}
    names = [*STABLE, *(p.relative_to(folder).as_posix() for p in sorted(folder.glob("versions/*/*.md")))]
    if (folder / f"{pulses.IDENTITY}.md").is_file():
        names += [f"{pulses.IDENTITY}.md", f"{INDEX_NAME}.md"]
    for rel_path in names:
        path = folder.joinpath(*rel_path.split("/"))
        if not path.is_file():
            continue
        text = util.read_text(path)
        link = permalink_of(text)
        if link:
            out[f"https://{OWNER}.github.io/{PUBLIC_REPO}/{link}"] = ("bytes", served(path.name, text))
    for path in sorted((folder / "badges").glob("*.svg.md")):
        text = util.read_text(path)
        label = re.search(r' aria-label="([^"]*)"', text)  # the badge's own words: its status (and lifecycle, version)
        link = permalink_of(text)
        if link:
            out[f"https://{OWNER}.github.io/{PUBLIC_REPO}/{link}"] = ("badge", label[1] if label else "")
    out[f"{PAGES}/PORTFOLIO.html"] = ("page", None)
    for name in (portfolio.NOTICES_MD, portfolio.HOWTO_MD):
        if (folder / name).is_file():
            out[f"{PAGES}/{name[:-3]}.html"] = ("page", None)
    return out


def check_served(urls: Mapping[str, tuple[str, object]], fetch=None, workers: int = 8) -> list[str]:
    """The problems of the URLs as served now: a status other than 200, other bytes, a badge that is no SVG of
    its status, a page that does not serve."""
    fetch = fetch or _fetch

    def one(item):
        url, (kind, want) = item
        status, kind_header, body = fetch(url)
        if status != 200:
            return f"{url}: HTTP {status} {kind_header}".rstrip()
        if kind == "bytes" and body != want:
            return f"{url}: serves other bytes than the published file"
        if kind == "badge" and (b"<svg" not in body or (want and f'aria-label="{want}"'.encode() not in body)):
            return f"{url}: does not serve the badge {want!r}"
        return None

    with cf.ThreadPoolExecutor(max(1, workers)) as pool:
        return [p for p in pool.map(one, sorted(urls.items())) if p]


def wait_for_pages(settings: Settings, cut_facts: Mapping | None, commit: str, *, hive: Hive | None = None, gh=("gh",),
                   fetch=None, timeout: int = 900, retries: int = 4, sleep=time.sleep, clock=time.monotonic,
                   say: Callable[[str], None] = print) -> int:
    """Wait for GitHub Pages to build the pushed commit, then check every URL of the portfolio: every file live
    before still serves (the stable maps, the timeline, PORTFOLIO.html, each badge, every version's files) and
    the new version's files serve exactly the published bytes. Returns the number of URLs checked."""
    hive = hive or Hive(settings, say=say)
    repo = f"{OWNER}/{hive.public_dir().name}"
    deadline, state = clock() + timeout, ""
    while True:
        done = util.run(*gh, "api", f"repos/{repo}/pages/builds/latest", "--jq", PAGES_STATE)
        state = done.stdout.strip()
        if state == f"built {commit}":
            break
        if state.startswith("errored"):
            raise SystemExit(f"the Pages build failed: {state}")
        if clock() >= deadline:
            raise SystemExit(f"Pages did not build {commit[:10]} in {timeout} s (last: {state or done.stderr[-200:]})")
        sleep(15)
    urls = expected_urls(settings, cut_facts)
    problems = check_served(urls, fetch)
    for _ in range(retries):  # the Pages CDN may serve the previous build for a few minutes
        if not problems:
            break
        sleep(30)
        problems = check_served({u: urls[u] for u in urls if any(p.startswith(u + ":") for p in problems)}, fetch)
    for problem in problems[:20]:
        say(f"  {problem}")
    if problems:
        raise SystemExit(f"{len(problems)} of {len(urls)} URL(s) do not serve the published files yet")
    say(f"Pages: all {len(urls)} URL(s) serve the published files (commit {commit[:10]})")
    return len(urls)


def local_copies(settings: Settings, say: Callable[[str], None] = print) -> list[Path]:
    """The latest map and timeline as plain files on this device, in <work>/subway/ (the bytes Pages serves)."""
    out, written = settings.work / "subway", []
    for name in STABLE:
        path = settings.portfolio_dir / name
        if path.is_file():
            target = out / name[:-3]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(served(name, util.read_text(path)))
            written.append(target)
    if written:
        say(f"local copies: {', '.join(p.name for p in written)} in {out}")
    return written


# ---- status and the one command ------------------------------------------------------------------------------------

def status(settings: Settings, say: Callable[[str], None] = print) -> dict:
    """Totals per wave and per line, and the head of the chain."""
    recs = records.records(settings)
    out = {"waves": {}, "lines": {}, "head": None}
    for wave in (1, 2):
        c = Counter(r["status"] for r in recs.values() if r["wave"] == wave)
        out["waves"][wave] = dict(c)
        say(f"wave {wave}: " + ", ".join(f"{s} {c.get(s, 0)}" for s in STATUSES) + f" (of {sum(c.values())})")
    for line in LINES:
        c = Counter(r["status"] for r in recs.values() if r["family"] == line["id"])
        if sum(c.values()):
            out["lines"][line["id"]] = dict(c)
            say(f"  {line['name']}: {sum(c.values())} (" + ", ".join(f"{s} {c.get(s, 0)}" for s in STATUSES) + ")")
    home = pulses.chain_home(settings)
    if home is not None:
        checker.ensure_checker(settings.checker)
        sid, _, frames = pulses.read_chain(home, settings.checker, pulses.known_head(settings))
        if frames:
            head = frames[-1][0]
            out["head"] = {"sid": sid, "seq": head["seq"], "payload_hash": head["payload_hash"],
                           "public": home == settings.portfolio_dir}
            say(f"stream {sid}: head version {head['payload']['version']} (seq {head['seq']}), payload_hash "
                f"{head['payload_hash']}; pulses {'public' if home == settings.portfolio_dir else 'private'}")
    return out


def crawl(settings: Settings, args=(), *, hive: Hive | None = None, deny: Denylist | None = None, gh=("gh",),
          fetch=None, printer=None, remote: str = REPO_URL, say: Callable[[str], None] = print, **sweep_options) -> dict:
    """The one command: discover, the full crawl, cut the next version (saved through the Hive), publish, check
    Pages (unless --no-wait), status."""
    from . import crawl as crawler
    hive = hive or Hive(settings, say=say)
    deny = deny or Denylist(settings.denylist, warn=say)
    with CrawlLock(settings):
        checker.ensure_checker(settings.checker)
        if hive.edits():
            raise SystemExit("the Hive has unsaved edits; save or put them back before a crawl")
        inventory.discover(settings, deny, gh=gh, say=say, stations=previous_stations(settings))
        crawler.sweep(settings, workers=MAX_WORKERS, remote=remote, say=say, gh=gh, **sweep_options)
        facts = cut(settings, hive=hive, deny=deny, printer=printer, lock=False, say=say)
        commit = publish(settings, hive=hive, deny=deny, lock=False, say=say)
        if "--no-wait" not in args:
            wait_for_pages(settings, facts, commit, hive=hive, gh=gh, fetch=fetch, say=say)
        status(settings, say=say)
        return {**facts, "public_commit": commit}
`````
{% endraw %}
