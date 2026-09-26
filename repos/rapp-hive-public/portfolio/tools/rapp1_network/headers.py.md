# `rapp1_network/headers.py`

The network header: one marked line in a portfolio repo's README, the same on every repo.

Source: `rapp1_network/headers.py` (rapp1-network 0.1.5). SHA-256 of the source below: `ab1416ed8b3c167009762762769ca596f97068e378269fc06b74fe3f1c12de17` (9903 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/headers.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The network header: one marked line in a portfolio repo's README, the same on every repo.

    <!-- rapp1:network-header:start -->
    [![RAPP/1](<badge URL>)](<portfolio file URL>) · **New to RAPP?** [Start here: get your Brainstem →](<installer>)
    <!-- rapp1:network-header:end -->

Placement (docs/headers.md has the whole rule set):
- markers present (outside fenced code): the block between them is refreshed in place; unbalanced markers are
  refused (ValueError), since only a person can tell which one is meant;
- otherwise the block goes right after the README's H1 (ATX `#`, setext `===`, or an HTML `<h1>`, then after the
  HTML block that holds it), else at the top (after any front matter), with exactly one blank line on each side;
- a leading byte order mark stays first; the block takes the README's own line ending (the most common one), and
  every other byte of the README is kept, so a PR's diff is the header and nothing else.
The action words are "unchanged", "refreshed", "added after the H1" and "added at the top". Applying twice is
applying once.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from .constants import END, INSTALLER, PAGES, PUBLIC_BLOB, START

UNBALANCED = "the network header markers are unbalanced; fix them by hand"
NOT_UTF8 = "the README is not UTF-8 text; add the header by hand"
BOM = "\ufeff"

FENCE = re.compile(r"^ {0,3}(`{3,}(?=[^`]*$)|~{3,})")  # a backtick fence's info string holds no backtick
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_H = re.compile(r"<h([1-6])[\s>]", re.I)
COMMENT = re.compile(r"<!--.*?-->")  # an HTML comment that closes on its own line
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)")
NOT_SETEXT_TEXT = re.compile(r"[<|\-*+>]|\d{1,9}[.)](?:[ \t]|$)")  # HTML, a table row, a list item, a quote
NEWLINE = re.compile(r"(\r\n|\r|\n)")


def header_block(repo: str) -> str:
    """The marked block for one repo (LF line endings); its bytes are in open PRs across the network."""
    r = quote(repo, safe="")
    return (f"{START}\n[![RAPP/1]({PAGES}/badges/{r}.svg)]({PUBLIC_BLOB}/repos/{r}.md) · **New to RAPP?** "
            f"[Start here: get your Brainstem →]({INSTALLER})\n{END}")


def split_lines(text: str) -> list[tuple[str, str]]:
    """[(line, its ending)] for every line: CRLF, CR and LF all end a line (as in CommonMark); the last line's
    ending is "" (so "" gives [("", "")] and "a\\n" gives [("a", "\\n"), ("", "")], like str.split)."""
    parts = NEWLINE.split(text)
    return list(zip(parts[0::2], parts[1::2] + [""]))


def newline_of(text: str) -> str:
    """The README's own line ending: the most common one, LF on a tie or when there is none."""
    crlf = text.count("\r\n")
    counts = {"\n": text.count("\n") - crlf, "\r\n": crlf, "\r": text.count("\r") - crlf}
    return max(counts, key=lambda nl: (counts[nl], -("\n", "\r\n", "\r").index(nl)))


def _fence_closes(fence: str, line: str) -> bool:
    return bool(re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$", line))


def _opens_comment(line: str) -> bool:
    """Whether an HTML comment opens on this line and closes on a later one (code spans and closed comments
    aside)."""
    return "<!--" in COMMENT.sub(" ", CODE_SPAN.sub(" ", line))


def _blocks(lines):
    """(index, line, in_comment) for every line outside fenced code (an unclosed fence runs to the end).
    `in_comment` marks the lines of an HTML comment that spans lines, up to the line that closes it; a fence inside
    such a comment is not a fence. An ATX heading line never opens a comment (it is one line)."""
    fence, comment = None, False
    for i, line in enumerate(lines):
        if comment:
            comment = "-->" not in line
            yield i, line, True
            continue
        if fence:
            if _fence_closes(fence, line):
                fence = None
            continue
        found = FENCE.match(line)
        if found:
            fence = found.group(1)
            continue
        yield i, line, False
        comment = not ATX.match(line) and _opens_comment(line)


def first_heading(lines, start: int = 0):
    """(level, index of the heading's last line, is_html) for the first heading at or after `start`, else None.

    Fenced code and HTML comments are skipped; an `<h1>` inside an inline code span or a closed comment is not a
    heading; a line that starts a list item, a table row, a quote or HTML is never a setext heading's text."""
    lines = list(lines)
    for i, line, in_comment in _blocks(lines[start:]):
        i += start
        if in_comment:
            continue
        found = ATX.match(line)
        if found:
            return len(found.group(1)), i, False
        visible = COMMENT.sub(" ", CODE_SPAN.sub(" ", line)).partition("<!--")[0]
        found = HTML_H.search(visible)
        if found:
            return int(found.group(1)), i, True
        if _opens_comment(line):
            continue
        if i + 1 < len(lines) and line.strip() and SETEXT.match(lines[i + 1]) \
                and not NOT_SETEXT_TEXT.match(line.lstrip()):
            underline = lines[i + 1].strip()
            if underline.startswith("="):
                return 1, i + 1, False
            if len(underline) >= 2:
                return 2, i + 1, False
    return None


def _markers(body: str):
    """[(offset, marker)] for every START or END marker outside fenced code, in order."""
    records, offsets, at = split_lines(body), [], 0
    for line, ending in records:
        offsets.append(at)
        at += len(line) + len(ending)
    found = []
    for i, line, _ in _blocks([line for line, _ in records]):
        for marker in (START, END):
            found += [(offsets[i] + m.start(), marker) for m in re.finditer(re.escape(marker), line)]
    return sorted(found)


def header_present(text: str) -> bool:
    """Whether the README holds both markers outside fenced code (a README may show them in a code block)."""
    kinds = {marker for _, marker in _markers(text)}
    return kinds == {START, END}


def _front_matter_end(lines) -> int:
    """The index of the first line after a leading front matter block (--- ... --- or ...), else 0."""
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
        return end + 1 if end is not None else 0
    return 0


def apply_header(text: str, repo: str) -> tuple[str, str]:
    """(new text, action): refresh the marked header in place, or add it after the H1 (else at the top).
    ValueError when it cannot be placed (unbalanced markers)."""
    bom = BOM if text.startswith(BOM) else ""
    body = text[len(bom):]
    nl = newline_of(body)
    block = header_block(repo).split("\n")
    markers = _markers(body)
    if markers:
        kinds = [marker for _, marker in markers]
        if kinds != [START, END]:
            raise ValueError(UNBALANCED)
        a, b = markers[0][0], markers[1][0] + len(END)
        new = body[:a] + nl.join(block) + body[b:]
        return bom + new, "unchanged" if new == body else "refreshed"
    records = split_lines(body)
    lines = [line for line, _ in records]
    start = _front_matter_end(lines)
    found = first_heading(lines, start)
    if found and found[0] == 1:
        _, at, is_html = found
        if is_html:  # after the HTML block that holds the <h1>
            at = next((i - 1 for i in range(at + 1, len(lines)) if not lines[i].strip()), len(lines) - 1)
        before, after, action = records[:at + 1], records[at + 1:], "added after the H1"
    else:
        before, after, action = records[:start], records[start:], "added at the top"
    while after and not after[0][0].strip():
        after = after[1:]
    while before and not before[-1][0].strip() and len(before) > start:
        before = before[:-1]
    pieces = [(line, ending or nl) for line, ending in before] + ([("", nl)] if before else [])
    pieces += [(line, nl) for line in block] + ([("", nl)] + after if after else [])
    return bom + "".join(line + ending for line, ending in pieces), action


def decode(raw: bytes) -> str:
    """A README's text: strict UTF-8 (a byte order mark stays, as U+FEFF). ValueError when it is not UTF-8."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(NOT_UTF8) from None


def apply_header_file(path, repo: str, *, write: bool = True) -> str:
    """Add or refresh the header in a README file, byte-exact: read as bytes, strict UTF-8, written back only when
    it changes (and `write`). Returns the action; ValueError when it cannot be placed or is not UTF-8."""
    path = Path(path)
    raw = path.read_bytes()
    new, action = apply_header(decode(raw), repo)
    if write and new.encode("utf-8") != raw:
        path.write_bytes(new.encode("utf-8"))
    return action


USAGE = "usage: header <README> <repo> [--check]"


def header_cli(args, say=print) -> int:
    """`header <README> <repo> [--check]`. Writes the README unless --check. Exit codes: 0 done (with --check:
    already current), 1 with --check when it would change, 2 when the header cannot be placed by a tool."""
    check = "--check" in args
    rest = [a for a in args if a != "--check"]
    if len(rest) != 2:
        raise SystemExit(USAGE)
    path, repo = Path(rest[0]), rest[1]
    try:
        action = apply_header_file(path, repo, write=not check)
    except ValueError as error:
        say(f"manual: {error}" if check else f"{path}: manual: {error}")
        return 2
    except OSError as error:
        raise SystemExit(f"{path}: {error.strerror or error}")
    if check:
        say(action)
        return 0 if action == "unchanged" else 1
    say(f"{path}: {action}")
    return 0
`````
{% endraw %}
