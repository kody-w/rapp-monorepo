# `rapp1_network/records.py`

The portfolio's records: one per family repo, from the crawl's sweep/<repo>.record.json, and the links between them.

Source: `rapp1_network/records.py` (rapp1-network 0.1.5). SHA-256 of the source below: `8137b718ca186fb4a26f50318e6a461b2866ec4a1c1b79e6ff15ed18bcf45604` (1493 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/records.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The portfolio's records: one per family repo, from the crawl's sweep/<repo>.record.json, and the links between them.

A repo the sweep has not reached yet is `unchecked` with that reason. The family decides each record's wave, line
(`family`), other lines (`also_on`) and default branch, so a record always agrees with data/family.json.
"""
from __future__ import annotations

from . import util
from .config import Settings
from .inventory import family

NOT_SWEPT = "the sweep has not run on it yet"


def records(settings: Settings) -> dict[str, dict]:
    """{repo: record} for every family repo, in family order."""
    out = {}
    for entry in family(settings):
        rec = util.load(settings.sweep / f"{entry['repo']}.record.json") or {
            "repo": entry["repo"], "status": "unchecked", "reason": NOT_SWEPT}
        rec.update(wave=entry["wave"], family=entry["family"], also_on=entry.get("also_on", []),
                   default_branch=entry["default_branch"])
        out[entry["repo"]] = rec
    return out


def linked_from(recs: dict[str, dict]) -> dict[str, list[str]]:
    """{repo: the portfolio repos whose links_to name it}, each list sorted case-insensitively."""
    back: dict[str, set[str]] = {name: set() for name in recs}
    for name, rec in recs.items():
        for target in rec.get("links_to", []):
            if target in back:
                back[target].add(name)
    return {name: sorted(names, key=str.lower) for name, names in back.items()}
`````
{% endraw %}
