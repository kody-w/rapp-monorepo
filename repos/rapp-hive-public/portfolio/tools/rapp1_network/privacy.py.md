# `rapp1_network/privacy.py`

The optional private denylist, used strictly as a black box.

Source: `rapp1_network/privacy.py` (rapp1-network 0.1.5). SHA-256 of the source below: `2118cc57d14d89933a1860d2c895f7e9122dba3e05f96adc92eba9ecacf73e10` (3731 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/privacy.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The optional private denylist, used strictly as a black box.

The scanner is a local file outside this repository (passed as --denylist or RAPP1_DENYLIST). This module never
prints, logs, copies or returns its patterns, or the text a finding matched: callers see only yes/no, the scanner's
one-line summary, and the paths of the files that hold a finding.

    scanner tree <folder>...          every file under the folders
    scanner diff <repo> <base>        the changes of a checkout against a base
    scanner commits <repo> <range>    the commits in a range (messages and changes)

Each exits non-zero when it finds something; its last output line is a summary such as "0 finding(s)".
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .util import run


@dataclass(frozen=True)
class Scan:
    ok: bool
    summary: str
    where: list[str] = field(default_factory=list)  # paths holding a finding; never the finding itself
    skipped: bool = False

    def line(self, mode: str) -> str:
        return f"privacy scan ({mode}): {self.summary}" + (f" in {', '.join(self.where[:20])}" if self.where else "")


class Denylist:
    def __init__(self, path: Path | None, warn=None):
        self.path = Path(path).expanduser() if path else None
        self._pattern = None
        self._warn = warn if warn is not None else (lambda text: print(text, file=sys.stderr))
        self._warned = False

    @property
    def enabled(self) -> bool:
        return self.path is not None

    def denied(self, text: str) -> bool:
        """Whether a repo's name or description (or any text) hits the denylist."""
        if not self.enabled:
            if not self._warned:
                self._warn("warning: no --denylist: repo names and descriptions are not privacy-checked")
                self._warned = True
            return False
        if self._pattern is None:
            spec = importlib.util.spec_from_file_location("rapp1_private_denylist", self.path)
            if spec is None or spec.loader is None:
                raise SystemExit("the denylist scanner could not be loaded")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            pattern = getattr(module, "PATTERN", None)
            if pattern is None or not hasattr(pattern, "search"):
                raise SystemExit("the denylist scanner has no usable PATTERN")
            self._pattern = pattern
        return bool(self._pattern.search(text))

    def _scan(self, mode: str, *args) -> Scan:
        if not self.enabled:
            return Scan(ok=True, summary="skipped, no --denylist given", skipped=True)
        done = run(sys.executable, "-B", str(self.path), mode, *map(str, args), timeout=1800)
        lines = done.stdout.strip().splitlines()
        summary = lines[-1] if lines else (done.stderr.strip().splitlines() or ["no output"])[-1][:200]
        where = sorted({line.split(": ", 1)[0] for line in lines[:-1] if ": " in line})
        return Scan(ok=done.returncode == 0, summary=summary, where=where)

    def tree(self, *folders) -> Scan:
        return self._scan("tree", *folders)

    def diff(self, repo_dir, base: str) -> Scan:
        return self._scan("diff", repo_dir, base)

    def commits(self, repo_dir, rev_range: str) -> Scan:
        return self._scan("commits", repo_dir, rev_range)


def require(scan: Scan, mode: str, what: str, say=print) -> Scan:
    """Print the scan's line; refuse (SystemExit) when it found something."""
    say(scan.line(mode))
    if not scan.ok:
        raise SystemExit(f"the privacy scan found something; {what}")
    return scan
`````
{% endraw %}
