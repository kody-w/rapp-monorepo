# `rapp1_network/config.py`

Settings: each one from its flag, then its environment variable, then <work>/local/settings.json, then a default.

Source: `rapp1_network/config.py` (rapp1-network 0.1.5). SHA-256 of the source below: `0c6612a7adf95f0cbe43ebb6d447314a7f19eb22b59081e6c10d08be053ee2e6` (4269 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/config.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Settings: each one from its flag, then its environment variable, then <work>/local/settings.json, then a default.

The local settings file never leaves the device. Nothing here reads a key store: the Hive's own device state is
read only by hive.py, and only under <hive>/.git/rapp-hive/.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .constants import PORTFOLIO, PRIVATE_ROOM, ROOM

# flag name -> environment variable
FLAGS = {
    "work": "RAPP1_WORK",
    "hives": "RAPP_HIVES",
    "hive": "RAPP1_HIVE",
    "hive-agent": "RAPP_HIVE_AGENT",
    "checker": "RAPP1_CHECKER",
    "denylist": "RAPP1_DENYLIST",
    "lts-pins": "RAPP1_LTS_PINS",
}


@dataclass(frozen=True)
class Settings:
    work: Path  # crawl inputs and results: data/, sweep/, cache/, local/ (private), subway/
    hives: Path  # the folder that holds the Hives
    hive: str  # the RAPP Hive's name inside `hives`
    hive_agent: Path | None  # hive_agent.py from kody-w/rapp-model-hive (branch experimental/hive-md)
    checker: Path  # a kody-w/rapp-1 checkout at CANON_RAPP1
    denylist: Path | None  # an optional private scanner (tree/diff/commits modes); never copied anywhere
    lts_pins: Path | None = None  # the estate's LTS pins file (lts-pins.json); without it, the known pins (pins.py)

    @property
    def data(self) -> Path:
        return self.work / "data"

    @property
    def sweep(self) -> Path:
        return self.work / "sweep"

    @property
    def cache(self) -> Path:
        return self.work / "cache"

    @property
    def clones(self) -> Path:
        return self.cache / "clones"  # depth-1 clones live here only while their repo is checked

    @property
    def local(self) -> Path:
        return self.work / "local"  # private to this device

    @property
    def hive_dir(self) -> Path:
        return self.hives / self.hive

    @property
    def room_dir(self) -> Path:
        return self.hive_dir / ROOM

    @property
    def portfolio_dir(self) -> Path:
        return self.room_dir / PORTFOLIO

    @property
    def private_chain_dir(self) -> Path:
        return self.hive_dir / PRIVATE_ROOM


def split_flags(argv: Sequence[str]) -> tuple[dict[str, str], list[str]]:
    """({flag: value} for the settings flags, the other arguments in order). `--flag value` and `--flag=value`."""
    flags, rest, i = {}, [], 0
    args = list(argv)
    while i < len(args):
        arg = args[i]
        name, eq, value = arg[2:].partition("=") if arg.startswith("--") else ("", "", "")
        if name in FLAGS:
            if eq:
                flags[name] = value
            elif i + 1 < len(args):
                flags[name] = args[i + 1]
                i += 1
            else:
                raise SystemExit(f"--{name} needs a value")
        else:
            rest.append(arg)
        i += 1
    return flags, rest


def _local_settings(work: Path) -> dict:
    try:
        value = json.loads((work / "local" / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def resolve(flags: Mapping[str, str] | None = None, env: Mapping[str, str] | None = None,
            default_work: Path | None = None) -> Settings:
    flags = dict(flags or {})
    env = os.environ if env is None else env
    work = Path(flags.get("work") or env.get("RAPP1_WORK") or default_work or Path.cwd()).expanduser().resolve()
    local = _local_settings(work)

    def pick(name, default=None):
        value = flags.get(name) or env.get(FLAGS[name]) or local.get(name.replace("-", "_")) or default
        return str(value) if value is not None else None

    agent, deny, lts = pick("hive-agent"), pick("denylist"), pick("lts-pins")
    return Settings(
        work=work,
        hives=Path(pick("hives", "~/Hives")).expanduser(),
        hive=pick("hive", "rapp-hive"),
        hive_agent=Path(agent).expanduser() if agent else None,
        checker=Path(pick("checker", str(work / "checker" / "rapp-1"))).expanduser(),
        denylist=Path(deny).expanduser() if deny else None,
        lts_pins=Path(lts).expanduser() if lts else None,
    )
`````
{% endraw %}
