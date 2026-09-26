# `rapp1_network/inventory.py`

The RAPP family: which of the owner's repos the network tracks, and on which subway line each one runs.

Source: `rapp1_network/inventory.py` (rapp1-network 0.1.5). SHA-256 of the source below: `3d2d4ea40b3171d463bce72c734e2775f9199bbb09e0ff7d521d24ce6dfcfc04` (7763 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/inventory.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The RAPP family: which of the owner's repos the network tracks, and on which subway line each one runs.

`discover` lists the owner's repos with `gh`, keeps the eligible ones (public, not a fork, not archived), picks the
RAPP family among them (`matched_on` names why; the wave-1 stack is always in by name), holds back every repo whose
name or description hits the private denylist, and writes the files below. An archived repo stays in the family
(`archived: true`) when it was a station in the previous version, so the notice board shows it as archived instead
of losing it; an archived repo that never was a station is not added.

    data/family.json          the portfolio: one entry per repo, sorted by (wave, family, repo lower-case)
    data/public-repos.json    every eligible repo as gh listed it (never leaves this device)
    local/denylist-held.json  the held-back repos (local only; no other output ever names them)
"""
from __future__ import annotations

import functools
import json
import re
import subprocess
from collections import Counter

from . import privacy, util
from .config import Settings
from .constants import OWNER, WAVE1
from .lines import LINE, line_of, tokens

FIELDS = "name,description,repositoryTopics,isFork,isArchived,visibility,defaultBranchRef,diskUsage,pushedAt,isEmpty"
LIST_LIMIT = 4000  # `gh repo list --limit`; a list that fills it may be cut off, so discover refuses one
LIST_TIMEOUT = 600
HELD_NOTE = ("LOCAL ONLY: repos whose name or description hit the private denylist; kept out of every public "
             "artifact (no portfolio file, badge, header, PR or map station).")

RAPP = re.compile(r"(?<![wtcgfs])rapp", re.I)  # rapp, RAPP, openrappter; not wrapper/trapped
HIVE_WORD = re.compile(r"(?<![a-z])hive", re.I)  # hive, Hives; not archive
RAR_WORD = re.compile(r"\bRAR\b")  # the registry, written in capitals


def matched_on(repo: dict) -> list[str]:
    """Why a repo (one object of `gh repo list --json`) belongs to the RAPP family; [] when it does not."""
    name, desc = repo["name"], repo.get("description") or ""
    topics = [t["name"] if isinstance(t, dict) else str(t) for t in (repo.get("repositoryTopics") or [])]
    toks = tokens(name)
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


def _list_repos(gh, limit: int) -> list[dict]:
    command = (*gh, "repo", "list", OWNER, "--limit", str(limit), "--json", FIELDS)
    try:
        done = util.run(*command, timeout=LIST_TIMEOUT)
    except FileNotFoundError:
        raise SystemExit(f"cannot run {gh[0]!r}: install the GitHub CLI (gh) or pass its path") from None
    except subprocess.TimeoutExpired:
        raise SystemExit(f"gh repo list did not answer within {LIST_TIMEOUT} s") from None
    if done.returncode:
        last = (done.stderr.strip().splitlines() or ["no error output"])[-1][:300]
        raise SystemExit(f"gh repo list failed (exit {done.returncode}): {last}")
    try:
        repos = json.loads(done.stdout)
    except ValueError:
        raise SystemExit("gh repo list did not print JSON") from None
    if not isinstance(repos, list) or not all(isinstance(r, dict) and isinstance(r.get("name"), str) for r in repos):
        raise SystemExit("gh repo list printed something other than a list of repos")
    if len(repos) >= limit:
        raise SystemExit(f"gh repo list returned {len(repos)} repos, its --limit; the list may be cut off, so the "
                         "family would be incomplete: discover again with a higher limit")
    return repos


def previous_family(settings: Settings) -> set[str]:
    """The repos of the family data/family.json holds now (the last discovery's), before it is written again."""
    entries = util.load(settings.data / "family.json")
    return {e["repo"] for e in entries if isinstance(e, dict) and isinstance(e.get("repo"), str)} \
        if isinstance(entries, list) else set()


def discover(settings: Settings, deny: privacy.Denylist | None = None, gh=("gh",), *, limit: int = LIST_LIMIT,
             say=functools.partial(print, flush=True), stations=None) -> list[dict]:
    """The RAPP family from `gh repo list`: writes data/family.json, data/public-repos.json and
    local/denylist-held.json, and returns the family entries in their file order. `stations` names the repos that
    were stations in the previous version (default: the family data/family.json holds now); an archived one of them
    stays in the family, marked `archived: true`."""
    deny = deny if deny is not None else privacy.Denylist(settings.denylist)
    stations = {name.lower() for name in (previous_family(settings) if stations is None else stations)}
    repos = _list_repos(tuple(gh), limit)
    public = [r for r in repos if r.get("visibility") == "PUBLIC" and not r.get("isFork")]
    eligible = [r for r in public if not r.get("isArchived")]
    util.dump(settings.data / "public-repos.json", eligible)  # private, archived and forked repos are never kept
    kept = [r for r in public if r.get("isArchived") and r["name"].lower() in stations]
    held, entries = [], []
    for r in eligible + kept:
        why = matched_on(r)
        if not why and r["name"] not in WAVE1:
            continue
        if deny.denied(r["name"] + "\n" + (r.get("description") or "")):
            held.append({"repo": r["name"], "matched_on": why})
            continue
        line, also = line_of(r["name"])
        entries.append({"repo": r["name"], "wave": 1 if r["name"] in WAVE1 else 2, "family": line, "also_on": also,
                        "matched_on": why, "default_branch": (r.get("defaultBranchRef") or {}).get("name") or "",
                        "empty": bool(r.get("isEmpty")), "disk_kb": r.get("diskUsage") or 0,
                        "description": r.get("description") or "", **({"archived": True} if r.get("isArchived") else {})})
    found = {e["repo"] for e in entries}
    missing = [name for name in WAVE1 if name not in found]
    entries.sort(key=lambda e: (e["wave"], e["family"], e["repo"].lower()))
    util.dump(settings.data / "family.json", entries)
    util.dump(settings.local / "denylist-held.json", {"note": HELD_NOTE, "repos": held})
    say(f"public, non-fork, unarchived: {len(eligible)}; RAPP family: {len(entries) + len(held)} "
        f"({len(held)} held back locally by the denylist)")
    say(f"wave 1: {sum(e['wave'] == 1 for e in entries)} | wave 2: {sum(e['wave'] == 2 for e in entries)}")
    counts = Counter(e["family"] for e in entries)
    say("lines: " + ", ".join(f"{LINE[i]['name']} {counts.get(i, 0)}" for i in LINE))
    say(f"interchanges by line membership: {sum(bool(e['also_on']) for e in entries)}")
    if any(e.get("archived") for e in entries):
        say(f"archived on GitHub, kept as stations: {sum(bool(e.get('archived')) for e in entries)}")
    if missing:
        say("WAVE-1 REPOS NOT FOUND (or held back): " + ", ".join(missing))
    return entries


def family(settings: Settings) -> list[dict]:
    """data/family.json, as discover wrote it; refuses when there is none yet."""
    entries = util.load(settings.data / "family.json")
    if not entries or not isinstance(entries, list):
        raise SystemExit("run discover first: there is no data/family.json")
    return entries
`````
{% endraw %}
