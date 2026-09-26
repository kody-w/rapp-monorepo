# `rapp1_network/wrapping.py`

The Hive's wrappers: a Hive holds only markdown, so every served file is a .md file whose Jekyll front matter tells GitHub Pages where to serve it, and whose body passes through untouched inside a kramdown {::nomarkdown} block.

Source: `rapp1_network/wrapping.py` (rapp1-network 0.1.5). SHA-256 of the source below: `05012bd906de43409181b4ade23e6ee0cbb0fd32954287af0f5dd8da70db4539` (4709 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/wrapping.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The Hive's wrappers: a Hive holds only markdown, so every served file is a .md file whose Jekyll front matter tells
GitHub Pages where to serve it, and whose body passes through untouched inside a kramdown {::nomarkdown} block.

    ---
    permalink: /portfolio/<path>
    layout: null
    [printed_from: <sha256 of the poster HTML>]      (subway.pdf only)
    ---
    {::nomarkdown}
    <body without its final LF>
    {:/}

Badges use the plain form (front matter, then the SVG), since an SVG never needs the raw block.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

from .constants import HIVE_MAX_BYTES, HIVE_MAX_PART, HIVE_MAX_PATH, PORTFOLIO, ROOM

OPEN, CLOSE = "{::nomarkdown}\n", "\n{:/}"
PERMALINK = re.compile(r"---\npermalink: /(\S+)\n")
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


class Refused(Exception):
    """An input breaks a rule the outputs need. The message names what to fix."""


def wrap(permalink: str, body: str) -> str:
    """A markdown file GitHub Pages serves at `permalink`, body untouched: Jekyll's front matter, then a raw block."""
    if "{{" in body or "{%" in body or "{:/" in body:
        raise Refused(f"{permalink}: the body holds Liquid or kramdown markers, which Pages would change")
    if "\r" in body or CONTROL.search(body):
        raise Refused(f"{permalink}: only printable text and line feeds may pass through the Hive")
    return f"---\npermalink: {permalink}\nlayout: null\n---\n{OPEN}{body.rstrip(chr(10))}\n{{:/}}\n"


def unwrap(text: str) -> str:
    """The body of a wrapped file, with its final LF (the exact text Pages serves)."""
    body = text.split(OPEN, 1)[1]
    return body[: body.rindex(CLOSE)] + "\n"


def is_wrapped(text: str) -> bool:
    return bool(PERMALINK.match(text)) and OPEN in text


def permalink_of(text: str) -> str | None:
    """The served path without its leading slash (e.g. portfolio/subway.html), or None."""
    found = PERMALINK.match(text)
    return found[1] if found else None


def served(name: str, text: str) -> bytes:
    """The exact bytes GitHub Pages serves for a wrapped file (the PDF is 7-bit ASCII by construction)."""
    return unwrap(text).encode("ascii" if name.endswith("pdf.md") else "utf-8")


def inside(root: Path, rel_path: str) -> Path:
    """root/rel_path, refused unless rel_path is a relative POSIX path that stays inside root (no absolute path, drive,
    backslash, or empty, "." or ".." part): a permalink or a path from a copy is data, never a place to write."""
    parts = rel_path.split("/")
    if (not rel_path or rel_path.startswith("/") or "\\" in rel_path or ":" in parts[0]
            or any(part in ("", ".", "..") for part in parts)):
        raise Refused(f"{rel_path!r}: not a relative path inside the folder")
    return Path(root).joinpath(*parts)


def materialize(files: Mapping[str, str], root: Path) -> None:
    """Write wrapped Hive files as GitHub Pages serves them (permalink path, exact body); others as they are. Every
    target stays inside root (see inside())."""
    root = Path(root)
    for rel_path, text in files.items():
        permalink = permalink_of(text)
        wrapped = permalink is not None and OPEN in text
        target = inside(root, permalink if wrapped else rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((unwrap(text) if wrapped else text).encode("utf-8"))


def check_hive_path(rel_path: str, room_prefix: str = f"{ROOM}/{PORTFOLIO}") -> None:
    """Refuse a path the Hive would refuse: at most 120 characters in all, 64 in one part, markdown only."""
    full = f"{room_prefix}/{rel_path}" if room_prefix else rel_path
    if len(full) > HIVE_MAX_PATH or any(len(part) > HIVE_MAX_PART for part in rel_path.split("/")):
        raise Refused(f"{rel_path}: too long for a Hive path")
    if not rel_path.endswith(".md"):
        raise Refused(f"{rel_path}: a Hive holds only .md files")


PRECHECK = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e\u2060-\u206f\ufeff]")


def check_hive_text(rel_path: str, text: str) -> None:
    """A fast pre-check of a subset of the Hive's text rules: over 1 MB, a CR, a control character (tabs and LFs
    pass), a bidi or an invisible one. The Hive agent's own text_rules() decide; hive.py runs them before a save."""
    if len(text.encode("utf-8")) > HIVE_MAX_BYTES:
        raise Refused(f"{rel_path}: over the Hive's 1 MB limit")
    found = PRECHECK.search(text)
    if "\r" in text or found:
        raise Refused(f"{rel_path}: holds a CR, a control, bidi or invisible character"
                      + (f" (U+{ord(found[0]):04X})" if found else ""))
`````
{% endraw %}
