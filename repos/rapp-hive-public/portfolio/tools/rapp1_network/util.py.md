# `rapp1_network/util.py`

Small helpers every module shares. Standard library only; text is always UTF-8 with LF line endings.

Source: `rapp1_network/util.py` (rapp1-network 0.1.6). SHA-256 of the source below: `0fd970b5ffe990b46b155718b74605048c552dcd5a98f75269e648a15a0a80d4` (2865 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/util.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Small helpers every module shares. Standard library only; text is always UTF-8 with LF line endings."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence


def run(*args: str, cwd=None, timeout=None, env: Mapping[str, str] | None = None,
        check: bool = False, input: str | None = None) -> subprocess.CompletedProcess:
    """A subprocess with text output captured (UTF-8, undecodable bytes replaced, so Windows code pages never matter)."""
    return subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, env={**os.environ, **(env or {})}, check=check,
                          input=input)


def load(path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def dump(path, value: Any) -> None:
    """JSON the way the crawl data has always been written: indent 1, sorted keys, ASCII escapes, one final LF."""
    write_text(path, json.dumps(value, indent=1, sort_keys=True) + "\n")


def write_text(path, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def read_text(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def pretty(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def utc_now(now: dt.datetime | None = None) -> str:
    """The RAPP/1 §7.4 fixed form: YYYY-MM-DDTHH:MM:SS.mmmZ, in UTC."""
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def today_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def remove_tree(path) -> None:
    """Delete a folder even when git made files read-only (Windows)."""
    def force(func, target, _exc):
        os.chmod(target, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        func(target)
    if Path(path).is_symlink() or Path(path).is_file():
        Path(path).unlink()
    elif Path(path).exists():
        shutil.rmtree(path, onexc=force)


def arg(args: Sequence[str], name: str, default: str) -> str:
    """The value after `name` in args, or the default."""
    args = list(args)
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default
`````
{% endraw %}
