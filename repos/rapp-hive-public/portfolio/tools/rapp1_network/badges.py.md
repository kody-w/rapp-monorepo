# `rapp1_network/badges.py`

The badge: a small self-made SVG, "RAPP/1 | <status>" (certified green, not yet amber, unchecked grey), kept in the Hive as `badges/<repo>.svg.md` and served by GitHub Pages as `badges/<repo>.svg` (image/svg+xml).

Source: `rapp1_network/badges.py` (rapp1-network 0.1.6). SHA-256 of the source below: `0f0d801576069c8557ba94d15701605bd07f14a19544905843b5edd7fb39bde3` (9808 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/badges.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The badge: a small self-made SVG, "RAPP/1 | <status>" (certified green, not yet amber, unchecked grey), kept in the
Hive as `badges/<repo>.svg.md` and served by GitHub Pages as `badges/<repo>.svg` (image/svg+xml).

A badge is a list of segments, (text, color) from left to right, so a later edition can add one (a version, a
lifecycle) without touching the renderer. Edition 1 is `[("RAPP/1", "#555"), (status, COLORS[status])]`.

Edition 2 (version 2 onwards) puts the lifecycle first and adds the version: an active repo without a version keeps
edition 1's bytes exactly; any other gets three segments, `RAPP/1 | <lifecycle word, or the status when active> |
<version>` (the version segment only when there is one), each text in the ink (dark or white) with the higher WCAG
contrast on its fill, and a title that says it all in words (`RAPP/1: deprecated (certified), version 1.2.3`).
Attribute names are lowercase only: GitHub Pages runs every .md file through kramdown, which lowercases attribute
names in HTML blocks.
"""
from __future__ import annotations

from urllib.parse import quote
from xml.sax.saxutils import escape

from .constants import COLORS, PORTFOLIO
from .lifecycle import COLORS as LIFECYCLE_COLORS, LEFT, LIFECYCLES, VERSION_COLOR, shown_version, valid_version
from .wrapping import Refused

# Verdana 11px advance widths (px) of the characters the badges use; any other character counts 7.0. Edition 1's
# words use only the first row; the rest are for edition 2's lifecycle words and versions.
WIDTH = {"R": 7.6, "A": 7.5, "P": 6.6, "/": 4.6, "1": 7.0, "c": 5.7, "e": 6.8, "r": 4.7, "t": 4.3, "i": 3.0,
         "f": 3.9, "d": 6.9, "n": 7.0, "o": 6.7, "y": 6.5, " ": 3.9, "u": 7.0, "h": 7.0, "k": 6.5,
         "a": 6.7, "b": 6.9, "g": 6.9, "j": 3.8, "l": 3.0, "m": 10.7, "p": 6.9, "q": 6.9, "s": 5.7, "v": 6.5,
         "w": 8.9, "x": 6.5, "z": 5.8, "0": 7.0, "2": 7.0, "3": 7.0, "4": 7.0, "5": 7.0, "6": 7.0, "7": 7.0,
         "8": 7.0, "9": 7.0, ".": 4.0, "-": 4.9, "_": 7.0, "+": 9.2}
DARK, WHITE = "#1b1f24", "#ffffff"  # the two inks of edition 2, the subway's
LABEL = ("RAPP/1", "#555")  # the left segment
HEIGHT, RADIUS, JOIN = 20, 3, 4  # px: the badge's height, its corner radius, the square patch at the first join
FONT = 'font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11"'
SHADOW = ("#010101", ".3")  # the text's shadow: color and opacity, one pixel lower


def text_width(s: str) -> int:
    """A segment's width: its text's advance, rounded up, plus 5 px of padding on each side."""
    return int(sum(WIDTH.get(ch, 7.0) for ch in s) + 0.999) + 10


def segments(status: str) -> list[tuple[str, str]]:
    """Edition 1's segments for a status. Refused for anything but the three statuses."""
    if status not in COLORS:
        raise Refused(f"{status!r} is not a RAPP/1 status ({', '.join(COLORS)})")
    return [LABEL, (status, COLORS[status])]


def segments_svg(parts) -> str:
    """The SVG for segments [(text, color)], left to right: one rounded bar in the last color, each earlier segment
    painted over it (the first one rounded on the left, squared at its join), then each text with its shadow."""
    parts = list(parts)
    if not parts:
        raise Refused("a badge needs at least one segment")
    widths = [text_width(text) for text, _ in parts]
    total, lefts = sum(widths), [sum(widths[:n]) for n in range(len(parts))]
    label = escape(": ".join(text for text, _ in parts), {'"': "&quot;"})
    shapes = [f'<rect width="{total}" height="{HEIGHT}" rx="{RADIUS}" fill="{parts[-1][1]}"/>']
    for n, ((_, color), left, width) in enumerate(zip(parts[:-1], lefts, widths)):
        if n == 0:
            shapes += [f'<rect width="{width}" height="{HEIGHT}" rx="{RADIUS}" fill="{color}"/>',
                       f'<rect x="{width - JOIN}" width="{JOIN}" height="{HEIGHT}" fill="{color}"/>']
        else:
            shapes.append(f'<rect x="{left}" width="{width}" height="{HEIGHT}" fill="{color}"/>')
    texts = []
    for (text, _), left, width in zip(parts, lefts, widths):
        x, shown = f"{left + width / 2:g}", escape(text)
        texts += [f'<text x="{x}" y="15" fill="{SHADOW[0]}" fill-opacity="{SHADOW[1]}">{shown}</text>',
                  f'<text x="{x}" y="14">{shown}</text>']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{HEIGHT}" role="img" '
            f'aria-label="{label}"><title>{label}</title>{"".join(shapes)}'
            f'<g fill="#fff" text-anchor="middle" {FONT}>{"".join(texts)}</g></svg>')


def badge_svg(status: str, parts=None) -> str:
    """A flat 'RAPP/1 | status' badge (or the given segments)."""
    return segments_svg(parts if parts is not None else segments(status))


def badge_permalink(repo: str) -> str:
    return f"/{PORTFOLIO}/badges/{quote(repo, safe='')}.svg"


def badge_file(repo: str, status: str, parts=None) -> str:
    """The Hive file `badges/<repo>.svg.md`: front matter that makes GitHub Pages (Jekyll) emit it at
    badges/<repo>.svg with no layout, then the SVG (the plain form: an SVG never needs the raw block)."""
    return f"---\npermalink: {badge_permalink(repo)}\nlayout: null\n---\n{badge_svg(status, parts)}\n"


# ---- edition 2: lifecycle first, and the version ------------------------------------------------------------------

def _luminance(color: str) -> float:
    def channel(hex2):
        c = int(hex2, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(color[i:i + 2]) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """The WCAG 2 contrast ratio of two #rrggbb colors."""
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def ink(fill: str) -> str:
    """The text color with the higher WCAG contrast on a fill (as the subway's line badges)."""
    fill = "#555555" if fill == "#555" else fill
    return DARK if contrast(fill, DARK) > contrast(fill, WHITE) else WHITE


def _check(status: str, lifecycle: str, version) -> None:
    if status not in COLORS:
        raise Refused(f"{status!r} is not a RAPP/1 status ({', '.join(COLORS)})")
    if lifecycle not in (*LIFECYCLES, LEFT):
        raise Refused(f"{lifecycle!r} is not a lifecycle ({', '.join(LIFECYCLES)}, or {LEFT})")
    if version is not None and not valid_version(version):
        raise Refused(f"{version!r} is not a version")


def segments2(status: str, lifecycle: str = "active", version: str | None = None) -> list[tuple[str, str]] | None:
    """Edition 2's segments, or None when the badge is edition 1's (an active repo without a version)."""
    _check(status, lifecycle, version)
    if lifecycle == "active" and not version:
        return None
    first = (status, COLORS[status]) if lifecycle == "active" else (lifecycle, LIFECYCLE_COLORS[lifecycle])
    return [LABEL, first] + ([(shown_version(version), VERSION_COLOR)] if version else [])


def label2(status: str, lifecycle: str = "active", version: str | None = None) -> str:
    """The badge in words (its title and aria-label): e.g. "RAPP/1: deprecated (certified), version 1.2.3"."""
    _check(status, lifecycle, version)
    if lifecycle == "active":
        words = status
    elif lifecycle == LEFT:
        words = f"left the network (last status: {status})"
    else:
        words = f"{lifecycle} ({status})"
    return f"RAPP/1: {words}" + (f", version {version}" if version else "")


def segments_svg2(parts, label: str) -> str:
    """Edition 2's renderer: the same geometry as segments_svg, each text in its own ink (dark or white by the higher
    contrast) with a shadow that suits it, and `label` as the title and aria-label."""
    parts = list(parts)
    widths = [text_width(text) for text, _ in parts]
    total, lefts = sum(widths), [sum(widths[:n]) for n in range(len(parts))]
    words = escape(label, {'"': "&quot;"})
    shapes = [f'<rect width="{total}" height="{HEIGHT}" rx="{RADIUS}" fill="{parts[-1][1]}"/>']
    for n, ((_, color), left, width) in enumerate(zip(parts[:-1], lefts, widths)):
        if n == 0:
            shapes += [f'<rect width="{width}" height="{HEIGHT}" rx="{RADIUS}" fill="{color}"/>',
                       f'<rect x="{width - JOIN}" width="{JOIN}" height="{HEIGHT}" fill="{color}"/>']
        else:
            shapes.append(f'<rect x="{left}" width="{width}" height="{HEIGHT}" fill="{color}"/>')
    texts = []
    for (text, color), left, width in zip(parts, lefts, widths):
        x, shown, fill = f"{left + width / 2:g}", escape(text), ink(color)
        shadow = SHADOW if fill == WHITE else ("#ffffff", ".4")
        texts += [f'<text x="{x}" y="15" fill="{shadow[0]}" fill-opacity="{shadow[1]}">{shown}</text>',
                  f'<text x="{x}" y="14" fill="{fill}">{shown}</text>']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{HEIGHT}" role="img" '
            f'aria-label="{words}"><title>{words}</title>{"".join(shapes)}'
            f'<g text-anchor="middle" {FONT}>{"".join(texts)}</g></svg>')


def badge_svg2(status: str, lifecycle: str = "active", version: str | None = None) -> str:
    """Edition 2's badge: edition 1's bytes for an active repo without a version, else the three-segment badge."""
    parts = segments2(status, lifecycle, version)
    return badge_svg(status) if parts is None else segments_svg2(parts, label2(status, lifecycle, version))


def badge_file2(repo: str, status: str, lifecycle: str = "active", version: str | None = None) -> str:
    """`badges/<repo>.svg.md` of edition 2 (the same plain form and permalink as edition 1)."""
    return f"---\npermalink: {badge_permalink(repo)}\nlayout: null\n---\n{badge_svg2(status, lifecycle, version)}\n"
`````
{% endraw %}
