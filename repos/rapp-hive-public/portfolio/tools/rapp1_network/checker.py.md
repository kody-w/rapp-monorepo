# `rapp1_network/checker.py`

rapp-1 at the canon pin: its checker (rapp_check.py), its reference implementation (rapp.py), its registry of stream forms (rapp_registry.py) and its conformance suite. They are always run or imported from the pinned checkout, never re-typed (RAPP/1 SPEC §4, note C4).

Source: `rapp1_network/checker.py` (rapp1-network 0.1.6). SHA-256 of the source below: `914b298cac4c04abe45829653f6334d0ddf2f0a042a62097e2afa344b51b5fb5` (4094 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/checker.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""rapp-1 at the canon pin: its checker (rapp_check.py), its reference implementation (rapp.py), its registry of
stream forms (rapp_registry.py) and its conformance suite. They are always run or imported from the pinned checkout,
never re-typed (RAPP/1 SPEC §4, note C4)."""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

from .constants import CANON_RAPP1, RAPP1_REPO
from .util import run


def ensure_checker(checker: Path, pin: str = CANON_RAPP1, clone: bool = True) -> Path:
    """The checkout at `checker`, cloned at the pin when missing; refuses any other commit or a local change."""
    checker = Path(checker)
    if not (checker / ".git").exists():
        if not clone:
            raise SystemExit(f"no rapp-1 checkout at {checker}")
        checker.parent.mkdir(parents=True, exist_ok=True)
        run("git", "-c", "core.autocrlf=false", "clone", "-q", RAPP1_REPO, str(checker), check=True)  # exact bytes
        run("git", "-C", str(checker), "checkout", "-q", "--detach", pin, check=True)
    head = run("git", "-C", str(checker), "rev-parse", "HEAD").stdout.strip()
    if head != pin:
        raise SystemExit(f"the checker at {checker} is at {head[:10]}, not at the canon pin {pin}")
    if run("git", "-C", str(checker), "status", "--porcelain").stdout.strip():
        raise SystemExit(f"the checker at {checker} has local changes; it must be exactly the pinned commit")
    return checker


def run_rapp_check(target, checker: Path, cwd=None, timeout: int = 900) -> tuple[str, int | str, str]:
    """(raw stdout, exit code or "timeout", stderr) of `rapp_check.py <target> --json`, run with this Python.
    The target is passed as given (the crawl passes the repo's folder name, with cwd the clones folder, so the
    artifact paths in the output are relative to the repo)."""
    try:
        done = run(sys.executable, "-B", str(Path(checker) / "rapp_check.py"), str(target), "--json", cwd=cwd,
                   timeout=timeout)
    except subprocess.TimeoutExpired:
        return "", "timeout", ""
    return done.stdout, done.returncode, done.stderr


def rapp_check(root, checker: Path, timeout: int = 900) -> dict:
    """The parsed JSON verdict of rapp_check.py on a folder; refuses when it gives none."""
    raw, code, err = run_rapp_check(root, checker, timeout=timeout)
    try:
        result = json.loads(raw)
    except ValueError:
        raise SystemExit(f"rapp_check.py gave no verdict for {root} (exit {code}): {err[-300:]}")
    if not isinstance(result, dict):
        raise SystemExit(f"rapp_check.py gave no verdict object for {root}")
    return result


def _import(checker: Path, name: str):
    checker = Path(checker).resolve()
    if str(checker) not in sys.path:
        sys.path.insert(0, str(checker))
    module = importlib.import_module(name)
    where = Path(getattr(module, "__file__", "") or "").resolve()
    if where.parent != checker:
        raise SystemExit(f"`{name}` was imported from {where}, not from the pinned checker at {checker}")
    return module


def reference(checker: Path):
    """rapp.py, the reference implementation (canonical JSON, hashes, frames, rappids)."""
    return _import(checker, "rapp")


def registry(checker: Path):
    """rapp_registry.py (the §6.1.1 stream forms, e.g. stream_form(sid) == "body-stream")."""
    return _import(checker, "rapp_registry")


def conformance(checker: Path, timeout: int = 600) -> str:
    """rapp-1's conformance suite at the pin; its summary line, e.g. "22 controlled checks | 22 PASS | 0 FAIL"."""
    done = run(sys.executable, "-B", "conformance.py", cwd=str(checker), timeout=timeout)
    last = (done.stdout.strip().splitlines() or ["no output"])[-1]
    if done.returncode or " 0 FAIL" not in last:
        raise SystemExit(f"rapp-1 conformance.py did not pass at the pin: {last}")
    return last


def certified(result: dict, code=0) -> bool:
    """The earned status rule: COMPLIANT or CLEAN, exit 0."""
    return result.get("verdict") in ("COMPLIANT", "CLEAN") and code == 0
`````
{% endraw %}
