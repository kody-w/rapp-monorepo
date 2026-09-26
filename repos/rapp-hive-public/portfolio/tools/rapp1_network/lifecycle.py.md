# `rapp1_network/lifecycle.py`

Versions, LTS pins, channels, lifecycles and notices: what portfolio edition 2 (version 2 onwards) says about each repo besides its earned RAPP/1 status. Pure functions of their inputs, except the crawl's two readers (a root VERSION file in a checkout, the latest GitHub release through gh) and the LTS pins file.

Source: `rapp1_network/lifecycle.py` (rapp1-network 0.1.6). SHA-256 of the source below: `1a6564a64f895f9dd12939de8ea09a8003d17b244234ddda9abb0cac1a5cc75c` (23023 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/lifecycle.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Versions, LTS pins, channels, lifecycles and notices: what portfolio edition 2 (version 2 onwards) says about each
repo besides its earned RAPP/1 status. Pure functions of their inputs, except the crawl's two readers (a root VERSION
file in a checkout, the latest GitHub release through gh) and the LTS pins file.

    version     the repo's own version: the first non-empty line of its root VERSION file at the evidence commit, else
                the tag of its latest GitHub release (gh, paced; a 404 or any failure means none). The first source
                that gives a valid version wins; valid means ^[A-Za-z0-9][A-Za-z0-9._+-]{0,39}$.
    LTS pin     the repo's long-term-support commit in RAPP/1: from the estate's LTS pins file (--lts-pins), else from
                the known pins (pins.py). Its label is the tag when the pin is a tag, else the 7-character commit.
    channel     rapp1-lts when the repo has an LTS pin, else newest.
    lifecycle   active; deprecated or superseded only from a notice file saved in the Hive by signed save
                (shared/organism/notices/<repo>.md); archived only from GitHub (it wins over a notice, whose text
                stays). A repo that leaves the family keeps its portfolio file and badge, marked left.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import threading
import time
import unicodedata
from pathlib import Path
from typing import Mapping, Sequence

from . import util
from .constants import OWNER, ROOM
from .pins import KNOWN_PINS
from .wrapping import PRECHECK, Refused, check_hive_text

VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,39}")
LIFECYCLES = ("active", "deprecated", "superseded", "archived")
NOTICED = ("deprecated", "superseded")  # the lifecycles a notice file may set
LEFT = "left"  # not a lifecycle: a repo that left the family, kept so no URL breaks
CHANNELS = ("rapp1-lts", "newest")
COLORS = {"deprecated": "#cf222e", "superseded": "#8250df", "archived": "#57606a", LEFT: "#57606a"}
VERSION_COLOR = "#0969da"
VERSION_SOURCES = {"VERSION": "its root VERSION file at the evidence commit",
                   "release": "the tag of its latest GitHub release"}
PIN_SOURCES = {"lts-pins": "the estate's LTS pins",
               "known": "the network's built-in known pins, until the estate publishes its LTS pins"}
NOTICES = f"{ROOM}/notices"  # in the Hive; notices/<repo>.md in the public copy
NOTICE_KEYS = ("repo", "lifecycle", "since", "superseded_by", "notice")
MAX_NOTICE = 200
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
REPO = re.compile(r"[A-Za-z0-9._-]{1,100}")
OWNER_REPO = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
COMMIT = re.compile(r"[0-9a-f]{40}")
MARKERS = re.compile(r"\{\{|\{%|\{:/")  # Liquid (Pages runs it on every file with front matter) and kramdown's end
NOTICE_MARKERS = re.compile(r"\{\{|\{%|\{:")
YAML_INDICATOR = re.compile(r"[-?:,\[\]{}#&*!|>'\"%@`]")


def nfc(text) -> str:
    return unicodedata.normalize("NFC", str(text))


# ---- versions ----------------------------------------------------------------------------------------------------

def valid_version(value) -> str | None:
    """The version when it is one (^[A-Za-z0-9][A-Za-z0-9._+-]{0,39}$), else None."""
    return value if isinstance(value, str) and VERSION.fullmatch(value) else None


def shown_version(version: str) -> str:
    """A version as a badge shows it: v1.2.3 when it starts with a digit, else as it is (v1.0.0, brainstem-v0.6.9)."""
    return f"v{version}" if version[:1].isdigit() else version


def read_version_file(root, files: Sequence[str] = ()) -> str | None:
    """The first non-empty line of the checkout's root file named exactly VERSION, when it is tracked, a plain file
    inside the checkout (never a symlink) and a valid version; else None."""
    root = Path(root)
    if "VERSION" not in files:
        return None
    path = root / "VERSION"
    try:
        if path.is_symlink() or not path.is_file():
            return None
        path.resolve().relative_to(root.resolve())
        with path.open("rb") as handle:
            data = handle.read(4096)
    except (OSError, RuntimeError, ValueError):
        return None
    text = data.decode("utf-8", "replace").lstrip("\ufeff")
    first = next((line.strip() for line in text.splitlines() if line.strip()), None)
    return valid_version(first)


class Releases:
    """The tag of a repo's latest GitHub release (`gh api repos/<owner>/<repo>/releases/latest`), through the injected
    gh, one call at a time and at most one per `pace` seconds across the crawl's workers. A 404 (no release), any
    failure, a timeout or a tag that is not a valid version means none: it never fails the crawl."""

    def __init__(self, gh, pace: float = 0.25, *, timeout: int = 60, clock=time.monotonic, sleep=time.sleep):
        self.gh, self.pace, self.timeout, self.clock, self.sleep = tuple(gh), pace, timeout, clock, sleep
        self._lock, self._next = threading.Lock(), 0.0
        self.calls = 0

    def __call__(self, repo: str) -> str | None:
        with self._lock:
            wait = self._next - self.clock()
            if wait > 0:
                self.sleep(wait)
            self._next = self.clock() + self.pace
            self.calls += 1
        try:
            done = util.run(*self.gh, "api", f"repos/{OWNER}/{repo}/releases/latest", "--jq", ".tag_name",
                            timeout=self.timeout)
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        tag = done.stdout.strip()
        return valid_version(tag) if done.returncode == 0 and tag != "null" else None  # jq prints null for no tag


# ---- LTS pins and channels ---------------------------------------------------------------------------------------

def read_pins(path) -> dict[str, dict]:
    """{repo: {commit[, version]}} of the owner's repos from an LTS pins file, in any of its shapes:
    {"schema": ..., "pins": {"owner/repo": {"commit": "<40 hex>", "version": "<label>"}}},
    {"pins": {"owner/repo": "<40 hex>"}} or {"owner/repo": "<40 hex>"}; a bare repo name means the owner's. Pins of
    other owners are left out. A file that is not one of these shapes is refused (SystemExit)."""
    path = Path(path).expanduser()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise SystemExit(f"{path}: the LTS pins file cannot be read ({error.strerror or error})") from None
    except ValueError as error:
        raise SystemExit(f"{path}: the LTS pins file is not JSON ({error})") from None
    if isinstance(value, dict) and "pins" in value:
        pins = value["pins"]
    elif isinstance(value, dict):
        pins = {k: v for k, v in value.items() if k != "schema"}
    else:
        pins = None
    if not isinstance(pins, dict):
        raise SystemExit(f"{path}: an LTS pins file maps repos to pins ({{\"pins\": {{\"owner/repo\": ...}}}})")
    out = {}
    for key, pin in sorted(pins.items()):
        owner, _, name = key.rpartition("/") if isinstance(key, str) else ("", "", "")
        if not isinstance(key, str) or not REPO.fullmatch(name) or (owner and not re.fullmatch(r"[A-Za-z0-9-]+", owner)):
            raise SystemExit(f"{path}: {key!r} is not a repo (owner/repo or a bare name)")
        commit, label = (pin, None) if isinstance(pin, str) else (
            (pin.get("commit"), pin.get("version")) if isinstance(pin, dict) else (None, None))
        if not (isinstance(commit, str) and COMMIT.fullmatch(commit)):
            raise SystemExit(f"{path}: the pin of {key} needs a full 40-hex commit")
        if label is not None and not valid_version(label):
            raise SystemExit(f"{path}: the pin of {key} has a version label that is not one ({label!r})")
        if owner and owner.lower() != OWNER.lower():
            continue
        out[name] = {"commit": commit, **({"version": label} if label else {})}
    return out


def pins_for(settings) -> tuple[dict[str, dict], str]:
    """(pins, source): the LTS pins file when the settings name one (source "lts-pins"; it replaces the known pins),
    else the known pins (source "known")."""
    path = getattr(settings, "lts_pins", None)
    if path:
        return read_pins(path), "lts-pins"
    return {name: dict(pin) for name, pin in KNOWN_PINS.items()}, "known"


def pin_label(pin: Mapping) -> str:
    return pin.get("version") or pin["commit"][:7]


def pin_facts(names, pins: Mapping[str, Mapping], source: str) -> dict[str, dict]:
    """{repo: {channel[, lts_commit, lts_version, lts_source]}} for every name (a pin's repo matches in any case)."""
    lower = {name.lower(): pin for name, pin in pins.items()}
    out = {}
    for name in names:
        pin = lower.get(name.lower())
        out[name] = ({"lts_commit": pin["commit"], "lts_version": pin_label(pin), "lts_source": source,
                      "channel": "rapp1-lts"} if pin else {"channel": "newest"})
    return out


# ---- notices -----------------------------------------------------------------------------------------------------

def notice_path(repo: str) -> str:
    """A notice file's path in the Hive."""
    return f"{NOTICES}/{repo}.md"


def _scalar(rel_path: str, key: str, value: str) -> str:
    """A front matter value: double-quoted (JSON escapes, which YAML reads the same), single-quoted, or plain."""
    if value.startswith('"'):
        try:
            text = json.loads(value)
        except ValueError:
            text = None
        if not isinstance(text, str):
            raise Refused(f"{rel_path}: {key} is not one double-quoted string")
        return text
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'") or "'" in value[1:-1].replace("''", ""):
            raise Refused(f"{rel_path}: {key} is not one single-quoted string")
        return value[1:-1].replace("''", "'")
    if value and (YAML_INDICATOR.match(value) or ": " in value or " #" in value or value.endswith(":")):
        raise Refused(f"{rel_path}: {key} would not read as plain text in YAML; write it in double quotes")
    return value


def valid_date(text) -> bool:
    try:
        return bool(isinstance(text, str) and DATE.fullmatch(text) and dt.date.fromisoformat(text))
    except ValueError:
        return False


def _unprintable(char: str) -> bool:
    """A character no page should carry in a notice: a control, format (soft hyphen, zero-width, bidi), private-use,
    unassigned or surrogate code point, or a variation selector (the Hive's text rules refuse these)."""
    return (unicodedata.category(char) in ("Cc", "Cf", "Co", "Cn", "Cs")
            or "\ufe00" <= char <= "\ufe0f" or "\U000e0100" <= char <= "\U000e01ef")


def check_notice_text(notice, where: str) -> str:
    """A notice line: 1 to 200 characters, one line, NFC, no control, bidi or invisible character, no Liquid or
    kramdown marker. Refused (Refused) otherwise."""
    if not isinstance(notice, str) or not notice.strip():
        raise Refused(f"{where}: the notice is empty (one line, 1 to {MAX_NOTICE} characters)")
    if len(notice) > MAX_NOTICE:
        raise Refused(f"{where}: the notice is {len(notice)} characters; at most {MAX_NOTICE}")
    if "\n" in notice or "\r" in notice or PRECHECK.search(notice) or any(_unprintable(c) for c in notice):
        raise Refused(f"{where}: the notice is one line of printable text (no control, bidi, invisible, private-use, "
                      "unassigned or surrogate character)")
    if notice != notice.strip():
        raise Refused(f"{where}: the notice has spaces at its start or end")
    if not unicodedata.is_normalized("NFC", notice):
        raise Refused(f"{where}: the notice is not NFC (the Hive keeps text NFC)")
    if NOTICE_MARKERS.search(notice):
        raise Refused(f"{where}: the notice holds a Liquid or kramdown marker ({{{{, {{% or {{:)")
    return notice


def successor(value: str, repo: str, portfolio) -> str:
    """A superseded_by value: a repo name in the portfolio, or owner/repo (the owner's own repo in the portfolio is
    written by its name)."""
    names = set(portfolio)
    if OWNER_REPO.fullmatch(value):
        owner, name = value.split("/", 1)
        if owner.lower() == OWNER.lower() and name in names:
            value = name
    elif not (REPO.fullmatch(value) and value in names):
        raise Refused(f"superseded_by {value!r} is neither a repo in the portfolio nor owner/repo")
    if value == repo or value.lower() == f"{OWNER}/{repo}".lower():
        raise Refused(f"a repo is never superseded by itself ({value})")
    return value


def parse_notice(rel_path: str, text: str, portfolio) -> dict:
    """{repo, lifecycle, since[, superseded_by], notice, body} from one notice file at its Hive path; `portfolio` holds
    the portfolio's repo names. Refused (Refused) naming the file and the rule it breaks."""
    folder, _, file_name = rel_path.rpartition("/")
    repo = file_name[:-3] if file_name.endswith(".md") else ""
    if folder != NOTICES or not repo:
        raise Refused(f"{rel_path}: a notice file is {NOTICES}/<repo>.md")
    if repo not in set(portfolio):
        raise Refused(f"{rel_path}: {repo} is not a repo in the portfolio (names are exact; to take the notice away: "
                      f"python -m rapp1_network notice {repo} --clear)")
    try:
        check_hive_text(rel_path, text)
    except Refused as error:
        raise Refused(f"{error} (the Hive's text rules)") from None
    if MARKERS.search(text):
        raise Refused(f"{rel_path}: holds a Liquid or kramdown marker ({{{{, {{% or {{:/}}), which GitHub Pages would run")
    if not text.startswith("---\n"):
        raise Refused(f"{rel_path}: starts with its front matter (a --- line)")
    end = text.find("\n---\n", 3)
    if end < 0 and text.endswith("\n---"):
        end = len(text) - 4
    if end < 0:
        raise Refused(f"{rel_path}: its front matter has no closing --- line")
    pairs = []
    for line in text[4:end].split("\n"):
        key, sep, value = line.partition(":")
        if not sep or not re.fullmatch(r"[a-z_]+", key) or (value and not value.startswith(" ")):
            raise Refused(f"{rel_path}: each front matter line is `key: value` ({line[:60]!r} is not)")
        pairs.append((key, value.strip()))
    keys = [key for key, _ in pairs]
    meta = {key: _scalar(rel_path, key, value) for key, value in pairs if key in NOTICE_KEYS}
    lifecycle = meta.get("lifecycle")
    want = [k for k in NOTICE_KEYS if k != "superseded_by" or lifecycle == "superseded"]
    if keys != want:
        raise Refused(f"{rel_path}: the front matter keys are {', '.join(want)}, in this order (found "
                      f"{', '.join(keys) or 'none'})")
    if meta["repo"] not in (repo, f"{OWNER}/{repo}"):
        raise Refused(f"{rel_path}: repo is {meta['repo']!r}, not {OWNER}/{repo} (the file's name)")
    if lifecycle not in NOTICED:
        raise Refused(f"{rel_path}: lifecycle is {', '.join(NOTICED)} (archived comes only from GitHub), not "
                      f"{meta['lifecycle']!r}")
    if not valid_date(meta["since"]):
        raise Refused(f"{rel_path}: since is a date, YYYY-MM-DD (not {meta['since']!r})")
    out = {"repo": repo, "lifecycle": lifecycle, "since": meta["since"],
           "notice": check_notice_text(meta["notice"], rel_path), "body": text[end + 5:]}
    if lifecycle == "superseded":
        try:
            out["superseded_by"] = successor(meta["superseded_by"], repo, portfolio)
        except Refused as error:
            raise Refused(f"{rel_path}: {error}") from None
    return out


def notice_file(repo: str, lifecycle: str, since: str, notice: str, superseded_by: str | None = None) -> str:
    """The notice file the command line writes (and parse_notice reads back): the front matter keys in order, the
    notice double-quoted, and a short body in plain words."""
    lines = ["---", f"repo: {OWNER}/{repo}", f"lifecycle: {lifecycle}", f"since: {since}"]
    if superseded_by:
        lines.append(f"superseded_by: {superseded_by}")
    lines += [f"notice: {json.dumps(notice, ensure_ascii=False)}", "---", "",
              f"# {repo}: {lifecycle} since {since}", "", notice.replace("<", "&lt;"), ""]
    if superseded_by:
        lines += [f"Superseded by {superseded_by}.", ""]
    lines += ["Saved in the RAPP Hive by signed save. The next crawl shows it on the repo's badge and portfolio file, "
              "the subway map, the notices page and the pulse.", ""]
    return "\n".join(lines)


# ---- lifecycles --------------------------------------------------------------------------------------------------

def lifecycle_facts(names, *, archived=(), notices: Mapping[str, Mapping] | None = None,
                    previous: Mapping[str, Mapping] | None = None, today: str) -> dict[str, dict]:
    """{repo: {lifecycle[, since, superseded_by, notice, notice_commit]}}: archived (from GitHub, since the first crawl
    that saw it, carried from the previous pulse; a notice's text and successor stay), else a notice's lifecycle,
    else active."""
    notices, previous, archived = notices or {}, previous or {}, set(archived)
    out = {}
    for name in names:
        notice, before = notices.get(name), previous.get(name) or {}
        if name in archived:
            since = before.get("since") if before.get("lifecycle") == "archived" and before.get("since") else today
            facts = {"lifecycle": "archived", "since": since}
        elif notice:
            facts = {"lifecycle": notice["lifecycle"], "since": notice["since"]}
        else:
            facts = {"lifecycle": "active"}
        if notice:
            facts["notice"] = notice["notice"]
            if notice.get("superseded_by"):
                facts["superseded_by"] = notice["superseded_by"]
            if notice.get("commit"):
                facts["notice_commit"] = notice["commit"]
        out[name] = facts
    return out


def entry(rec: Mapping, schema: int = 2) -> dict:
    """A repo's entry in a pulse payload: {line, status, verdict, evidence_commit[, reason]} (schema 1), and from
    schema 2 also {channel, lifecycle[, version, lts_version, superseded_by, since, notice]}: the notice text too, so
    the chain itself versions every notice."""
    commit = rec.get("evidence_commit") or None
    out = {"line": rec["family"], "status": rec["status"], "verdict": rec.get("verdict") if commit else None,
           "evidence_commit": commit}
    if rec["status"] == "unchecked":
        out["reason"] = nfc(rec.get("reason", ""))
    if schema >= 2:
        out["channel"] = rec.get("channel") or "newest"
        out["lifecycle"] = rec.get("lifecycle") or "active"
        for key in ("version", "lts_version", "superseded_by", "since", "notice"):
            if rec.get(key):
                out[key] = nfc(rec[key])
        if rec.get("member_card"):
            out["card"] = True  # the repo carries its network card (.rapp/member.md) at the evidence commit
    return out


def left_repos(frames: Sequence, names, held=(), today: str = "") -> dict[str, dict]:
    """{repo: {left, last, last_version, last_crawled}}: the repos that were stations (or had left) in the head pulse
    and are not in the family now (compared in any case), except the ones the private denylist holds back now
    (privacy wins: they are removed). `left` is the date of the first crawl that no longer found it (carried from
    the head pulse's `left` map); `last` is its entry in the last pulse that recorded it as a station."""
    if not frames:
        return {}
    head = frames[-1][0]["payload"]
    before = head.get("left") if isinstance(head.get("left"), dict) else {}
    now = {name.lower() for name in names}
    hidden = {name.lower() for name in held}
    out = {}
    for name in sorted(set(head.get("repos", {})) | set(before), key=lambda n: (n.lower(), n)):
        if name.lower() in now or name.lower() in hidden:
            continue
        last = next(((frame["payload"]["repos"][name], frame["payload"]) for frame, _ in reversed(frames)
                     if name in frame["payload"].get("repos", {})), None)
        if last is None:
            continue
        out[name] = {"left": before.get(name) or today, "last": dict(last[0]), "last_version": last[1]["version"],
                     "last_crawled": last[1]["crawl"]["finished_utc"][:10]}
    return out


# ---- what changed between two versions ---------------------------------------------------------------------------

def schema_of(payload: Mapping) -> int:
    """1 or 2: the payload's shape (rapp1-network-pulse/<n>)."""
    return 2 if str(payload.get("schema", "")).endswith("/2") else 1


def changes(prev: Mapping, cur: Mapping) -> dict:
    """What changed from one payload to the next ({schema, repos, left}; a /1 payload has no left, and every repo in
    it was active): status, lifecycle (with the notice), version and channel changes (the last two only between /2
    payloads, since /1 recorded neither), member cards added or removed (only where both pulses checked the repo),
    repos added, repos that left (with their date), how many others went (held back by the privacy rule: never named)
    and how many are at a new evidence commit."""
    a, b = prev.get("repos", {}), cur.get("repos", {})
    order = lambda name: (name.lower(), name)
    both = sorted(a.keys() & b.keys(), key=order)
    left_before, left_now = prev.get("left") or {}, cur.get("left") or {}
    compare = schema_of(prev) >= 2 and schema_of(cur) >= 2
    life = lambda e: e.get("lifecycle") or "active"
    out = {"status": [(n, a[n]["status"], b[n]["status"]) for n in both if a[n]["status"] != b[n]["status"]],
           "lifecycle": [(n, life(a[n]), life(b[n]), b[n].get("notice") or "") for n in both if life(a[n]) != life(b[n])],
           "version": [(n, a[n].get("version"), b[n].get("version")) for n in both
                       if compare and a[n].get("version") != b[n].get("version")],
           "channel": [(n, a[n].get("channel"), b[n].get("channel")) for n in both
                       if compare and a[n].get("channel") != b[n].get("channel")],
           # a card is compared only where both pulses checked the repo: an unchecked entry (a failed clone)
           # records no card, and that is not a card removed
           "cards": [(n, bool(b[n].get("card"))) for n in both
                     if a[n].get("evidence_commit") and b[n].get("evidence_commit")
                     and bool(a[n].get("card")) != bool(b[n].get("card"))],
           "added": sorted(b.keys() - a.keys(), key=order),
           "left": [(n, left_now[n]) for n in sorted(left_now, key=order) if n not in left_before],
           "removed": len([n for n in a.keys() - b.keys() if n not in left_now]),
           "moved": sum(1 for n in both if a[n].get("evidence_commit") != b[n].get("evidence_commit"))}
    return out
`````
{% endraw %}
