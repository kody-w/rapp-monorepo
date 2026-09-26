# `rapp1_network/subway.py`

Draw the RAPP/1 network as a subway map, from the portfolio files alone.

Source: `rapp1_network/subway.py` (rapp1-network 0.1.6). SHA-256 of the source below: `0cc14f9f53790e1a1ed0b74db3274ac49a63d3e766dcc3f9bd5c9b113fedc3b7` (71066 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/subway.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Draw the RAPP/1 network as a subway map, from the portfolio files alone.

    python -m rapp1_network.subway <portfolio-folder>           write the stable subway.svg.md and subway.html.md
    python -m rapp1_network.subway <portfolio-folder> --pdf     also print subway.pdf with headless Chrome (one page)
    python -m rapp1_network.subway <portfolio-folder> --check   rebuild in memory; exit 1 if a stable map file differs

The pipeline's cut calls render() once per crawl for the version folder (versions/<id>/) and once for the stable
path, which always shows the latest map with a picker for every version.

Standard library only. The same portfolio files always give the same bytes. Lines are the families (lines/*.md),
stations are the repos (repos/*.md) filled by their earned RAPP/1 status, and the RAPP/1 Core line runs in layer
order to the Start here terminal. A Hive holds only markdown, so every output is a .md file whose front matter
tells GitHub Pages where to serve it and whose body passes through untouched ({::nomarkdown}); the PDF is
rewritten as 7-bit text (ASCIIHex streams, see pdf.py) so it fits that rule, and renders exactly as Chrome printed it.
Ported from legacy/rapp1_subway.py, which drew version 1; docs/subway.md has the design and the rules.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import sys
from pathlib import Path

from . import pdf as pdf_printer
from .constants import CANON_RAPP1, COLORS, HIVE_MAX_BYTES, PAGES, PUBLIC_BLOB, REPO_URL
from .util import write_text
from .wrapping import Refused, served, unwrap, wrap

__all__ = ["EDITION", "Refused", "build", "chain", "check", "edition_for", "front", "layout", "load", "main", "nav_for",
           "page", "panel", "poster", "render", "served", "stable_label", "svg", "unwrap", "version_id", "wrap"]

STATUS = COLORS
INK, PAPER, MUTED = "#1b1f24", "#ffffff", "#57606a"
HOLLOW = ("deprecated", "superseded", "archived")  # edition 2 draws these stations hollow (archived: a dashed ring)
SUPERSEDED = "#8250df"  # the "superseded by" connector, the badges' superseded color
DASH = "2.6 2.2"  # an archived station's ring
FONT = "Helvetica, Arial, sans-serif"
HUB_LINES = 6          # a station linked from this many other lines (a third of them) is an interchange
POSTER_MM = 1189       # the poster's long edge: A0
CAP_HEIGHT = 0.718     # Helvetica's cap height, per em
MIN_TEXT_MM = 2.0      # the smallest cap height a named station may print at on the poster

# Geometry, in SVG pixels.
LABEL, TRUNK_LABEL, TAG = 13, 17, 12
STEP, R, R_TRUNK = 26, 6, 10
LINE_W, TRUNK_W, LANE, STEM, COL_GAP = 7, 12, 12, 11, 42
MARGIN, LABEL_BAND, LAYER_BAND, BADGE_H, CALLOUT_W, PANEL_W = 70, 54, 62, 30, 470, 640
MAX_BYTES = HIVE_MAX_BYTES  # the Hive's limit for one file

# Editions of the drawing. A version's maps are drawn once, by the edition in force when that version is cut, and a
# saved version folder is never redrawn. Edition 1 is legacy/rapp1_subway.py's drawing, kept byte for byte so version
# 1's published maps still reproduce from its portfolio files; edition 2 (docs/CHANGES.md) draws version 2 onwards.
EDITIONS = ((1, 1), (2, 2))  # (the first version number it draws, edition)
EDITION = EDITIONS[-1][1]    # the current edition; it also draws a map that carries no version

# Helvetica advance widths (per 1000 em) for printable ASCII; Arial shares them.
_W = ("278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 556 556 556 556 556 556 556 556 556 556 278 "
      "278 584 584 584 556 1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 667 778 722 667 611 722 "
      "667 944 667 667 611 278 278 278 469 556 333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 556 "
      "556 333 500 278 556 500 722 500 500 500 334 260 334 584")
_B = ("278 333 474 556 556 889 722 238 333 333 389 584 278 333 278 278 556 556 556 556 556 556 556 556 556 556 333 "
      "333 584 584 584 611 975 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778 667 778 722 667 611 722 "
      "667 944 667 667 611 333 278 333 584 556 333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611 611 "
      "611 389 556 333 611 556 778 556 556 500 389 280 389 584")
WIDTHS = {False: dict(zip(map(chr, range(32, 127)), map(int, _W.split()))),
          True: dict(zip(map(chr, range(32, 127)), map(int, _B.split())))}


def text_w(s, size, bold=False):
    table = WIDTHS[bold]
    return sum(table.get(ch, 1000 if ch in "→←" else 600) for ch in s) * size / 1000 * 1.06  # slack for Arial


def num(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(str(s), quote=True)


def edition_for(version):
    """The edition that draws a version's maps: the newest one whose first version is at or below its number."""
    if not version:
        return EDITION
    number = int(version["number"])
    return max((e for first, e in EDITIONS if first <= number), default=EDITIONS[0][1])


def luminance(color):
    """The WCAG 2 relative luminance of a #rrggbb color."""
    def channel(hex2):
        c = int(hex2, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(color[i:i + 2]) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    """The WCAG 2 contrast ratio of two #rrggbb colors, 1 to 21."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def ink_on(color, edition=EDITION):
    """Dark or white text on a fill. Edition 1 compared the gamma-encoded luminance with 0.55, which put white text on
    light fills (2.8:1 on #15aabf); from edition 2 the ink with the higher WCAG contrast ratio wins."""
    if edition >= 2:
        return INK if contrast(color, INK) >= contrast(color, PAPER) else PAPER
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return INK if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.55 else PAPER


# ---- the portfolio files -----------------------------------------------------------------------------

def front(text):
    """({key: value or [items]}, body) from a leading --- block, the way the Hive reads it."""
    end, meta, key = (text.find("\n---\n", 3) if text.startswith("---\n") else -1), {}, None
    for line in text[4:end].split("\n") if end > 0 else []:
        k, sep, v = line.partition(":")
        if line.startswith("  - ") and isinstance(meta.get(key), list):
            meta[key].append(line[4:].strip())
        elif sep and re.fullmatch(r"[a-z][a-z0-9_]*", k):
            key, meta[k] = k, v.strip() or []
    return (meta, text[end + 5:]) if end > 0 else ({}, text)


def unquote(v):
    return v[1:-1] if isinstance(v, str) and len(v) > 1 and v[0] == v[-1] == '"' else v


def listed(meta, key):
    return [unquote(v) for v in meta.get(key)] if isinstance(meta.get(key), list) else []


def load(folder):
    folder = Path(folder)
    lines = {}
    for path in sorted((folder / "lines").glob("*.md")):
        meta, _ = front(path.read_text(encoding="utf-8"))
        color = unquote(meta.get("color", ""))
        if not re.fullmatch(r"#[0-9a-f]{6}", color) or not meta.get("line") or not meta.get("name"):
            raise Refused(f"lines/{path.name}: needs line, name and a #rrggbb color")
        lines[meta["line"]] = {"id": meta["line"], "name": unquote(meta["name"]), "color": color,
                               "order": int(meta.get("order", 99)), "about": unquote(meta.get("about", "")),
                               "trunk": [tuple(s.split(" | ", 1)) for s in listed(meta, "trunk")]}
    repos = {}
    for path in sorted((folder / "repos").glob("*.md")):
        meta, _ = front(path.read_text(encoding="utf-8"))
        name = str(meta.get("repo", "")).split("/", 1)[-1]
        if meta.get("left"):  # a repo that left the network keeps its file, off the map (edition 2)
            continue
        if meta.get("family") not in lines or meta.get("status") not in STATUS:
            raise Refused(f"repos/{path.name}: its family must be a line in lines/ and its status one of {list(STATUS)}")
        repos[name] = {"repo": name, "line": meta["family"], "also": [a for a in listed(meta, "also_on") if a in lines],
                       "status": meta["status"], "verdict": meta.get("verdict", ""),
                       "commit": meta.get("evidence_commit", ""), "checked": meta.get("checked", ""),
                       "wave": str(meta.get("wave", "")), "links": [x for x in listed(meta, "links_to")],
                       "lifecycle": unquote(meta.get("lifecycle") or "active"), "version": unquote(meta.get("version") or ""),
                       "since": unquote(meta.get("since") or ""), "superseded_by": unquote(meta.get("superseded_by") or "")}
    for r in repos.values():
        r["links"] = sorted({x for x in r["links"] if x in repos and x != r["repo"]}, key=str.lower)
    core = [line for line in lines.values() if line["trunk"]]
    if len(core) != 1 or any(s not in repos for s, _ in core[0]["trunk"]):
        raise Refused("exactly one line needs a trunk, and every trunk station must be a repo in repos/")
    if len(core[0]["trunk"]) < 2 or len({s for s, _ in core[0]["trunk"]}) != len(core[0]["trunk"]):
        raise Refused(f"lines/{core[0]['id']}.md: the trunk needs at least two different stations, the last one the "
                      "Start here terminal")
    return repos, dict(sorted(lines.items(), key=lambda kv: (kv[1]["order"], kv[0])))


# ---- the layout ----------------------------------------------------------------------------------------

def pav(targets):
    """Isotonic (nondecreasing) least-squares fit of the targets: pool adjacent violators."""
    blocks = []
    for t in targets:
        blocks.append([t, 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            v, n = blocks.pop()
            blocks[-1] = [(blocks[-1][0] * blocks[-1][1] + v * n) / (blocks[-1][1] + n), blocks[-1][1] + n]
    return [v for v, n in blocks for _ in range(n)]


def place_columns(centers, widths, lo, hi):
    """Column centres as close to their junctions as order, widths and gaps allow."""
    if not widths:  # no branch on this side of the Core
        return []
    offs = [0.0]
    for i in range(1, len(widths)):
        offs.append(offs[-1] + (widths[i - 1] + widths[i]) / 2 + COL_GAP)
    ys = pav([c - s for c, s in zip(centers, offs)])
    low, high = lo + widths[0] / 2, hi - widths[-1] / 2 - offs[-1]
    if low > high:
        raise Refused("the columns do not fit the width")
    return [min(max(y, low), high) + s for y, s in zip(ys, offs)]


def more_text(more):
    """A summary poster's row for a branch's unnamed stations: how many, then certified / not yet / unchecked."""
    return f"+ {more['n']} more · {more['certified']} / {more['not yet']} / {more['unchecked']}"


def layout(repos, lines, version=None, edition=None, summary=False):
    """Where everything goes: the trunk, each branch's side, stem, lane and column, the interchanges, the size.
    `summary` (edition 2, the poster only): each branch names only its interchanges and counts the rest in one row."""
    edition = edition_for(version) if edition is None else edition
    core = next(line for line in lines.values() if line["trunk"])
    trunk = [s for s, _ in core["trunk"]]
    layer = dict(core["trunk"])
    line_of = {name: r["line"] for name, r in repos.items()}
    on_lines = {name: {r["line"], *r["also"]} | ({core["id"]} if name in trunk else set()) for name, r in repos.items()}
    linked_from = {name: set() for name in repos}
    in_lines = {name: set() for name in repos}
    for name, r in repos.items():
        for target in r["links"]:
            linked_from[target].add(name)
            if line_of[name] not in on_lines[target]:
                in_lines[target].add(line_of[name])
    branches = []
    for line in lines.values():
        if line is core and edition < 2:  # edition 1 never drew a Core repo that is not on the trunk
            continue
        members = sorted((n for n, r in repos.items() if r["line"] == line["id"] and n not in trunk),
                         key=lambda n: (-len(linked_from[n]), n.lower()))
        if not members:
            continue
        inside = [s for s in trunk if repos[s]["line"] == line["id"]] if line is not core else []
        weight = {s: sum((s in repos[m]["links"]) + (m in repos[s]["links"]) for m in members) for s in trunk}
        junction = inside[0] if inside else max(trunk, key=lambda s: (weight[s], trunk.index(s)))
        branches.append({"line": line, "members": members, "junction": junction})
    interchange = {n for n in repos if len(on_lines[n]) > 1 or len(in_lines[n]) >= HUB_LINES}
    interchange |= {b["junction"] for b in branches if b["line"] is not core}  # where another line meets the Core
    if summary:
        for b in branches:
            hidden = [m for m in b["members"] if m not in interchange]
            b["members"] = [m for m in b["members"] if m in interchange]
            if hidden:
                b["more"] = {"n": len(hidden), **{s: sum(repos[m]["status"] == s for m in hidden) for s in STATUS}}
    rows = lambda b: len(b["members"]) + (1 if b.get("more") else 0)
    heights = {"up": 0, "down": 0}
    for b in sorted(branches, key=lambda b: (-rows(b), b["line"]["order"])):
        b["side"] = "up" if heights["up"] <= heights["down"] else "down"
        heights[b["side"]] += rows(b)

    def col_width(b):
        widest = max([text_w(n, LABEL) + 11 * len([a for a in repos[n]["also"]]) for n in b["members"]]
                     + ([text_w(more_text(b["more"]), LABEL)] if b.get("more") else []))
        total = sum(1 for r in repos.values() if r["line"] == b["line"]["id"])
        return max(widest + 2 * R + 30, text_w(f"{b['line']['name']} · {total}", 14, True) + 26)

    for b in branches:
        b["width"] = col_width(b)
    sides = {s: [b for b in branches if b["side"] == s] for s in ("up", "down")}
    span = max(sum(b["width"] for b in bs) + COL_GAP * max(0, len(bs) - 1) for bs in sides.values())
    names_w = [text_w(s, TRUNK_LABEL, True) for s in trunk]
    tags_w = [max(text_w(part, TAG + 1, True) for part in tag_lines(layer[s])) for s in trunk]
    per = max(max(n, t) for n, t in zip(names_w, tags_w)) + 90
    width = max(span, per * (len(trunk) - 1) + CALLOUT_W + 120) + 2 * MARGIN
    x0, x_end = MARGIN + 50, width - MARGIN - CALLOUT_W
    tx = {s: x0 + (x_end - x0) * i / (len(trunk) - 1) for i, s in enumerate(trunk)}
    for side, bs in sides.items():
        bs.sort(key=lambda b: (trunk.index(b["junction"]), b["line"]["order"]))
        # parallel stems at one junction, in column order
        centers = []
        for b in bs:
            group = [c for c in bs if c["junction"] == b["junction"]]
            k = group.index(b)
            b["stem"] = tx[b["junction"]] + (k - (len(group) - 1) / 2) * STEM
            centers.append(b["stem"] + b["width"] / 2 - R - 4)
        xs = place_columns(centers, [b["width"] for b in bs], MARGIN, width - MARGIN)
        for b, x in zip(bs, xs):
            b["col"] = x - b["width"] / 2 + R + 4  # the line runs down the left of its column
        lefts = sorted((b for b in bs if b["col"] < b["stem"] - 0.5), key=lambda b: b["stem"])
        rights = sorted((b for b in bs if b["col"] > b["stem"] + 0.5), key=lambda b: -b["stem"])
        for group in (lefts, rights):
            for lane, b in enumerate(group):
                b["lane"] = lane
        for b in bs:
            b.setdefault("lane", -1)
        side_lanes = max([len(lefts), len(rights), 0])
        sides[side] = (bs, side_lanes)
    up, up_lanes = sides["up"]
    down, down_lanes = sides["down"]
    col_len = lambda b: (rows(b) - 1) * STEP + 44 + BADGE_H
    h_up = max([col_len(b) for b in up] or [0])
    h_down = max([col_len(b) for b in down] or [0])
    man_up, man_down = up_lanes * LANE + 26, down_lanes * LANE + 26
    y0 = MARGIN + h_up + 34 + man_up + LABEL_BAND
    first_up = y0 - LABEL_BAND - man_up - 34
    first_down = y0 + LAYER_BAND + man_down + 34
    height = first_down + h_down + MARGIN
    for b in up:
        b["lane_y"] = y0 - LABEL_BAND - 14 - max(b["lane"], 0) * LANE
        b["ys"] = [first_up - i * STEP for i in range(rows(b))]
    for b in down:
        b["lane_y"] = y0 + LAYER_BAND + 14 + max(b["lane"], 0) * LANE
        b["ys"] = [first_down + i * STEP for i in range(rows(b))]
    stems = {s: [b["stem"] - tx[s] for b in branches if b["junction"] == s] for s in trunk}
    result = {"repos": repos, "lines": lines, "core": core, "trunk": trunk, "layer": layer, "tx": tx, "y0": y0,
            "branches": up + down, "width": width + PANEL_W, "map_width": width,
            "height": height,
            "interchange": interchange, "linked_from": linked_from, "in_lines": in_lines, "on_lines": on_lines,
            "stems": stems, "version": version, "edition": edition, "summary": summary}
    result["height"] = max(height, MARGIN + panel_height(result) + MARGIN)
    return result


# ---- drawing ------------------------------------------------------------------------------------------

def chamfer(points, cut=14):
    """An octilinear polyline: every right-angle corner is cut at 45 degrees."""
    out = [points[0]]
    for i in range(1, len(points) - 1):
        (ax, ay), (bx, by), (cx, cy) = points[i - 1], points[i], points[i + 1]
        d1, d2 = abs(bx - ax) + abs(by - ay), abs(cx - bx) + abs(cy - by)
        c = min(cut, d1 / 2, d2 / 2)
        if c < 1:
            out.append((bx, by))
            continue
        ux, uy = ((bx - ax) / d1, (by - ay) / d1) if d1 else (0, 0)
        vx, vy = ((cx - bx) / d2, (cy - by) / d2) if d2 else (0, 0)
        out += [(bx - ux * c, by - uy * c), (bx + vx * c, by + vy * c)]
    out.append(points[-1])
    return "M" + " L".join(f"{num(x)} {num(y)}" for x, y in out)


def tag_lines(tag):
    """A trunk station's layer tag on two lines: "layer 0" over "RAPP/1"."""
    m = re.match(r"(\d+(?:-\d+)?) (.*)", tag)
    return (f"layer{'s' if '-' in m.group(1) else ''} {m.group(1)}", m.group(2)) if m else (tag, "")


def lifecycle_words(repo):
    """A station's lifecycle in words: active, or e.g. "deprecated since 2026-10-01", "superseded by rapp-x"."""
    life = repo.get("lifecycle") or "active"
    if life == "active":
        return "active"
    return (life + (f" since {repo['since']}" if repo.get("since") else "")
            + (f", superseded by {repo['superseded_by']}" if repo.get("superseded_by") else ""))


def station_title(L, name):
    """A station in words (its accessible name and tooltip from edition 2): status, lifecycle, version, interchange,
    every line it is on, so neither the colored dots after a name nor a hollow ring is ever the only way to tell."""
    repo = L["repos"][name]
    names = [L["lines"][i]["name"] for i in sorted(L["on_lines"][name], key=lambda i: L["lines"][i]["order"])]
    version = repo.get("version")
    return (f"{name}: {repo['status']} · {lifecycle_words(repo)} · " + (f"version {version}" if version else "no version")
            + (" · interchange" if name in L["interchange"] else "") + " · on " + ", ".join(names))


def station_group(L, name, x, y, r, label_x, label_y, size, bold, interactive, anchor="start", links=True, span=None):
    """One station: its link (or group), title, ring or capsule, status circle, name and the dots of its other lines.
    `span` = (left, right) offsets of the branch stems at a trunk junction: the ring becomes a capsule over them."""
    repo = L["repos"][name]
    ring = name in L["interchange"]
    lines = sorted(L["on_lines"][name], key=lambda i: L["lines"][i]["order"])
    v1 = L["edition"] < 2
    label = f' aria-label="{esc(name)}: {esc(repo["status"])}"' if v1 else ""
    life = "" if v1 else (f' data-lifecycle="{esc(repo.get("lifecycle") or "active")}"'
                          + (f' data-version="{esc(repo["version"])}"' if repo.get("version") else ""))
    attrs = (f' class="st" data-repo="{esc(name)}" data-status="{esc(repo["status"])}" data-verdict="{esc(repo["verdict"])}"'
             f' data-commit="{esc(repo["commit"])}" data-checked="{esc(repo["checked"])}" data-wave="{esc(repo["wave"])}"'
             f' data-lines="{esc(",".join(lines))}" data-out="{len(repo["links"])}" data-in="{len(L["linked_from"][name])}"'
             f'{life} tabindex="0" role="button"{label}' if interactive else "")
    parts = [f'<a href="{PUBLIC_BLOB}/repos/{esc(name)}.md" target="_blank"{attrs}>' if links else "<g>"]
    if links and not v1:
        parts.append(f"<title>{esc(station_title(L, name))}</title>")
    if ring and span:
        rr = r + 4.5
        parts.append(f'<rect x="{num(x + span[0] - rr)}" y="{num(y - rr)}" width="{num(span[1] - span[0] + 2 * rr)}" '
                     f'height="{num(2 * rr)}" rx="{num(rr)}" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>')
    elif ring:
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r + 4.5)}" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>')
    if not v1 and repo.get("lifecycle") in HOLLOW:  # hollow: white inside a ring of its status color
        dash = f' stroke-dasharray="{DASH}"' if repo["lifecycle"] == "archived" else ""
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r - 0.4)}" fill="{PAPER}" '
                     f'stroke="{STATUS[repo["status"]]}" stroke-width="{4 if r > R else 3.2}"{dash}/>')
    else:
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{STATUS[repo["status"]]}" stroke="{INK}" '
                     f'stroke-width="{2.5 if r > R else 1.6}"/>')
    weight = ' font-weight="700"' if bold else ""
    halo = f' paint-order="stroke" stroke="{PAPER}" stroke-width="4"' if bold else ""  # trunk labels sit near lines
    parts.append(f'<text x="{num(label_x)}" y="{num(label_y)}" font-size="{size}"{weight} text-anchor="{anchor}" '
                 f'fill="{INK}"{halo}>{esc(name)}</text>')
    dot_x = label_x + text_w(name, size, bold) / 1.06 + 8
    if v1:
        others = [i for i in lines if i != repo["line"] and not (name in L["trunk"] and i == L["core"]["id"])]
    elif name in L["trunk"]:  # drawn on the Core: a dot for each other line, unless its branch meets it right here
        met = {b["line"]["id"] for b in L["branches"] if b["junction"] == name}
        others = [i for i in lines if i != L["core"]["id"] and i not in met]
    else:
        others = [i for i in lines if i != repo["line"]]
    for other in others:
        parts.append(f'<circle cx="{num(dot_x)}" cy="{num(label_y - size * 0.33)}" r="4" '
                     f'fill="{L["lines"][other]["color"]}" stroke="{PAPER}" stroke-width="1"/>')
        dot_x += 11
    parts.append("</a>" if links else "</g>")
    return "".join(parts)


def svg(L, interactive=False, links=True):
    W, H, y0, tx, core = L["width"], L["height"], L["y0"], L["tx"], L["core"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(W)} {num(H)}" width="{num(W)}" height="{num(H)}" '
           f'font-family="{FONT}" role="{"img" if L["edition"] < 2 or not links else "graphics-document"}" '
           f'aria-labelledby="map-title map-desc">',
           f'<title id="map-title">RAPP/1 network subway map</title>',
           f'<desc id="map-desc">Every public RAPP repo as a station, filled by its earned RAPP/1 status; lines are '
           f'families; the RAPP/1 Core line runs in layer order to the Start here terminal, rapp-installer.'
           + (' This poster names the Core stations and the interchanges and counts the other stations of each line.'
              if L.get("summary") else "") + '</desc>',
           f'<rect width="{num(W)}" height="{num(H)}" fill="{PAPER}"/>']
    # branch lines first, then the trunk over their stems, then stations
    out.append('<g fill="none" stroke-linejoin="round" stroke-linecap="round">')
    for b in L["branches"]:
        color, sx, jy = b["line"]["color"], b["stem"], y0
        pts = [(sx, jy)]
        if b["lane"] >= 0:
            pts += [(sx, b["lane_y"]), (b["col"], b["lane_y"])]
        pts += [(b["col"], b["ys"][0]), (b["col"], b["ys"][-1])]
        end = b["ys"][-1] + (-34 if b["side"] == "up" else 34)
        pts[-1] = (b["col"], end)
        out.append(f'<path d="{chamfer(pts)}" stroke="{color}" stroke-width="{LINE_W}" data-line="{b["line"]["id"]}"/>')
    first, last = L["trunk"][0], L["trunk"][-1]
    out.append(f'<path d="M{num(tx[first] - 40)} {num(y0)} L{num(tx[last])} {num(y0)}" stroke="{core["color"]}" '
               f'stroke-width="{TRUNK_W}" data-line="{core["id"]}"/>')
    out.append("</g>")
    # line badges at the far end of each column
    for b in L["branches"]:
        line = b["line"]
        n = sum(1 for r in L["repos"].values() if r["line"] == line["id"])  # the whole line, trunk stations too
        text = f"{line['name']} · {n}"
        bw = text_w(text, 14, True) + 22
        by = b["ys"][-1] + (-34 - BADGE_H if b["side"] == "up" else 34)
        bx = b["col"] - 14
        out.append(f'<g><rect x="{num(bx)}" y="{num(by)}" width="{num(bw)}" height="{BADGE_H}" rx="15" fill="{line["color"]}"/>'
                   f'<text x="{num(bx + 11)}" y="{num(by + 20)}" font-size="14" font-weight="700" '
                   f'fill="{ink_on(line["color"], L["edition"])}">'
                   f'{esc(text)}</text></g>')
    if L["edition"] >= 2:  # "superseded by": a dashed arrow from a superseded station to its successor, under both
        out.append(connectors(L))
    # branch stations (and, on a summary poster, the row that counts the unnamed ones)
    for b in L["branches"]:
        for name, y in zip(b["members"], b["ys"]):
            out.append(station_group(L, name, b["col"], y, R, b["col"] + R + 9, y + 4.6, LABEL, False, interactive,
                                     links=links))
        if b.get("more"):
            m, y = b["more"], b["ys"][len(b["members"])]
            out.append(f'<text x="{num(b["col"] + R + 9)}" y="{num(y + 4.6)}" font-size="{LABEL}" fill="{MUTED}">'
                       f'+ {m["n"]} more · <tspan fill="#1a7f37">{m["certified"]}</tspan> / <tspan fill="#9a6700">'
                       f'{m["not yet"]}</tspan> / <tspan fill="{MUTED}">{m["unchecked"]}</tspan></text>')
    # trunk stations, their layer tags, and the terminal
    for s in L["trunk"]:
        right = max([d for d in L["stems"][s]] + [0])
        lx = tx[s] + max(right, 0) + R_TRUNK + 12
        r = R_TRUNK + (6 if s == last else 0)
        stems = L["stems"][s]
        span = ((min(stems + [0]), max(stems + [0])) if L["edition"] >= 2 and stems
                and max(abs(d) for d in stems) + LINE_W / 2 > r else None)  # stems wider than the station itself
        out.append(station_group(L, s, tx[s], y0, r, lx, y0 - 17, TRUNK_LABEL, True, interactive, links=links,
                                 span=span))
        first, second = tag_lines(L["layer"][s])
        out.append(f'<text x="{num(lx)}" y="{num(y0 + 29)}" font-size="{TAG + 1}" font-weight="700" fill="{MUTED}">{esc(first)}</text>')
        if second:
            out.append(f'<text x="{num(lx)}" y="{num(y0 + 45)}" font-size="{TAG + 1}" fill="{MUTED}">{esc(second)}</text>')
    tx_last = tx[last]
    label_right = tx_last + max(L["stems"][last] + [0]) + R_TRUNK + 12 + text_w(last, TRUNK_LABEL, True)
    cx, cw, ch = label_right + 30, 262, 118
    out.append(f'<g><path d="M{num(tx_last + R_TRUNK + 22)} {num(y0)} L{num(cx)} {num(y0)}" stroke="{core["color"]}" '
               f'stroke-width="4" stroke-dasharray="2 6" stroke-linecap="round" fill="none"/>'
               f'<rect x="{num(cx)}" y="{num(y0 - ch / 2)}" width="{num(cw)}" height="{ch}" rx="16" fill="{core["color"]}"/>'
               f'<text x="{num(cx + 18)}" y="{num(y0 - ch / 2 + 36)}" font-size="26" font-weight="700" fill="{PAPER}">START HERE</text>'
               f'<text x="{num(cx + 18)}" y="{num(y0 - ch / 2 + 62)}" font-size="15" fill="{PAPER}">Get your Brainstem:</text>'
               f'<text x="{num(cx + 18)}" y="{num(y0 - ch / 2 + 82)}" font-size="15" font-weight="700" fill="{PAPER}">rapp-installer</text>'
               f'<text x="{num(cx + 18)}" y="{num(y0 - ch / 2 + 103)}" font-size="12" fill="{PAPER}">RAPP/1 LTS · brainstem-v0.6.9</text></g>')
    out.append(panel(L))
    out.append("</svg>")
    return "".join(out)


def arrowhead(tip, ux, uy, size=10.0, extra=""):
    """A filled arrowhead (a triangle path, no marker: the viewer's CSP-strict page references nothing by url())
    whose tip is at `tip`, pointing along (ux, uy)."""
    bx, by = tip[0] - ux * size, tip[1] - uy * size
    nx, ny = -uy * size * 0.55, ux * size * 0.55
    pts = [tip, (bx + nx, by + ny), (bx - nx, by - ny), tip]
    return (f'<path d="M' + " L".join(f"{num(x)} {num(y)}" for x, y in pts) + f'" fill="{SUPERSEDED}" '
            f'stroke="none"{extra}/>')


def positions(L):
    """{station: (x, y, radius)} of every station drawn (a summary poster leaves some branch stations out)."""
    out = {}
    for b in L["branches"]:
        for name, y in zip(b["members"], b["ys"]):
            out[name] = (b["col"], y, R)
    last = L["trunk"][-1]
    for s in L["trunk"]:
        out[s] = (L["tx"][s], L["y0"], R_TRUNK + (6 if s == last else 0))
    return out


def connectors(L):
    """The "superseded by" connectors: from each superseded (or archived) station whose successor is also on this
    map, a dashed curve to the successor's edge and an arrowhead there (both marked data-superseded-by), the curve
    carrying its words as its title. The curve bulges to the left of the stations (their names are on the right), so
    even two neighbours in one column get a visible arrow."""
    pos, out = positions(L), []
    for name in sorted(pos, key=lambda n: (n.lower(), n)):
        repo, target = L["repos"][name], L["repos"][name].get("superseded_by")
        if repo.get("lifecycle") not in ("superseded", "archived") or target not in pos or target == name:
            continue
        (ax, ay, ar), (bx, by, br) = pos[name], pos[target]
        d = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        if d <= ar + br + 6:
            continue
        ux, uy = (bx - ax) / d, (by - ay) / d
        nx, ny = -uy, ux  # a normal of the line; take the one to the left (or below, for a level line)
        if nx > 0 or (nx == 0 and ny < 0):
            nx, ny = -nx, -ny
        bulge = min(60.0, 30 + 0.1 * d)
        cx, cy = (ax + bx) / 2 + nx * bulge, (ay + by) / 2 + ny * bulge
        unit = lambda x, y: (x / ((x * x + y * y) ** 0.5 or 1), y / ((x * x + y * y) ** 0.5 or 1))
        sx, sy = unit(cx - ax, cy - ay)
        ex, ey = unit(bx - cx, by - cy)
        start, tip = (ax + sx * (ar + 3), ay + sy * (ar + 3)), (bx - ex * (br + 3), by - ey * (br + 3))
        end = (tip[0] - ex * 9, tip[1] - ey * 9)
        pts = [((1 - k / 12) ** 2 * start[0] + 2 * (1 - k / 12) * (k / 12) * cx + (k / 12) ** 2 * end[0],
                (1 - k / 12) ** 2 * start[1] + 2 * (1 - k / 12) * (k / 12) * cy + (k / 12) ** 2 * end[1])
               for k in range(13)]
        mark = f' data-superseded-by="{esc(target)}"'
        out.append(f'<path d="M' + " L".join(f"{num(x)} {num(y)}" for x, y in pts) + f'" fill="none" '
                   f'stroke="{SUPERSEDED}" stroke-width="2.5" stroke-dasharray="7 5" stroke-linecap="round"{mark}>'
                   f'<title>{esc(name)}: superseded by {esc(target)}</title></path>' + arrowhead(tip, ex, ey, extra=mark))
    return "".join(out)


def panel_rows(L):
    """The legend as rows of (height, svg markup at y=baseline); one list gives both the drawing and its height."""
    repos, rows = L["repos"], []
    date = max((r["checked"] for r in repos.values() if r["checked"]), default="")
    total = {s: sum(r["status"] == s for r in repos.values()) for s in STATUS}
    t = lambda y, text, size=18, bold=False, color=INK, x=0, anchor="start": (
        f'<text x="{x}" y="{y}" font-size="{size}"{" font-weight=\"700\"" if bold else ""} fill="{color}"'
        f'{" text-anchor=\"end\"" if anchor == "end" else ""}>{text}</text>')
    rows.append((50, lambda y: t(y, "RAPP/1 network", 48, True)))
    rows.append((34, lambda y: t(y, "Every public RAPP repo is a station, filled by its earned", 20, color=MUTED)))
    rows.append((26, lambda y: t(y, "RAPP/1 status. Lines are families.", 20, color=MUTED)))
    version = L.get("version")
    label = (f"Version {version['number']} · crawled {version['utc'][:10]} {version['utc'][11:16]} UTC"
             if version else f"Crawled {date}")
    rows.append((34, lambda y: t(y, esc(label), 20, True)))
    rows.append((52, lambda y: t(y, f"STATIONS · {len(repos)}", 18, True)))
    words = {"certified": "certified: rapp_check says COMPLIANT or CLEAN", "not yet": "not yet: drift or unverified",
             "unchecked": "unchecked: could not be cloned or checked"}
    for s_, color in STATUS.items():
        rows.append((32, lambda y, s_=s_, color=color: (
            f'<circle cx="12" cy="{y - 6}" r="{R + 2}" fill="{color}" stroke="{INK}" stroke-width="1.8"/>'
            + t(y, f'<tspan font-weight="700">{total[s_]}</tspan> {esc(words[s_])}', 18, x=34))))
    rows.append((40, lambda y: (
        f'<circle cx="12" cy="{y - 6}" r="{R + 6}" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>'
        f'<circle cx="12" cy="{y - 6}" r="{R + 1}" fill="{STATUS["certified"]}" stroke="{INK}" stroke-width="1.8"/>'
        + t(y, f"interchange ({len(L['interchange'])}): where lines meet, a repo on", 18, x=34))))
    rows.append((24, lambda y: t(y, f"several lines, or one linked from {HUB_LINES}+ other lines", 18, x=34)))
    dots = [L["lines"][i]["color"] for i in ("brainstem", "worlds") if i in L["lines"]] or [INK, MUTED]
    rows.append((34, lambda y: (f'<circle cx="7" cy="{y - 6}" r="5" fill="{dots[0]}"/>'
                                f'<circle cx="20" cy="{y - 6}" r="5" fill="{dots[-1]}"/>'
                                + t(y, "dots after a name: the other lines it is on", 18, x=34))))
    if L["edition"] >= 2:
        life = {x: sum((r.get("lifecycle") or "active") == x for r in repos.values()) for x in HOLLOW}
        rows.append((34, lambda y: (
            f'<circle cx="12" cy="{y - 6}" r="{R + 1.6}" fill="{PAPER}" stroke="{STATUS["certified"]}" stroke-width="3.2"/>'
            + t(y, f"hollow: deprecated ({life['deprecated']}) or superseded ({life['superseded']}),", 18, x=34))))
        rows.append((24, lambda y: t(y, "the ring in its status color", 18, x=34)))
        rows.append((32, lambda y: (
            f'<circle cx="12" cy="{y - 6}" r="{R + 1.6}" fill="{PAPER}" stroke="{STATUS["certified"]}" stroke-width="3.2" '
            f'stroke-dasharray="{DASH}"/>' + t(y, f"dashed ring: archived on GitHub ({life['archived']})", 18, x=34))))
        rows.append((32, lambda y: (
            f'<path d="M0 {y - 6} L16 {y - 6}" fill="none" stroke="{SUPERSEDED}" stroke-width="2.5" '
            f'stroke-dasharray="7 5" stroke-linecap="round"/>' + arrowhead((26, y - 6), 1, 0)
            + t(y, "dashed arrow: superseded by (to its successor)", 18, x=34))))
    rows.append((52, lambda y: t(y, "WAVES", 18, True)))
    for wave, name in (("1", "Wave 1 · the RAPP/1 stack"), ("2", "Wave 2 · the rest of the family")):
        sts = [r["status"] for r in repos.values() if r["wave"] == wave]
        rows.append((30, lambda y, name=name, sts=sts: t(y, esc(name), 18) + t(
            y, f'{len(sts)} · <tspan fill="#1a7f37">{sts.count("certified")}</tspan> / <tspan fill="#9a6700">'
               f'{sts.count("not yet")}</tspan> / <tspan fill="{MUTED}">{sts.count("unchecked")}</tspan>', 18,
            x=PANEL_W - MARGIN, anchor="end")))
    rows.append((50, lambda y: t(y, f"LINES · {sum(1 for i in L['lines'] if any(r['line'] == i for r in repos.values()))}", 18, True)))
    for line in L["lines"].values():
        sts = [r["status"] for r in repos.values() if r["line"] == line["id"]]
        if not sts:
            continue
        rows.append((31, lambda y, line=line, sts=sts: (
            f'<rect x="0" y="{y - 15}" width="40" height="11" rx="5.5" fill="{line["color"]}"/>'
            + t(y, esc(line["name"]), 18, True, x=54) + t(
                y, f'{len(sts)} · <tspan fill="#1a7f37">{sts.count("certified")}</tspan> / <tspan fill="#9a6700">'
                   f'{sts.count("not yet")}</tspan> / <tspan fill="{MUTED}">{sts.count("unchecked")}</tspan>', 18,
                x=PANEL_W - MARGIN, anchor="end"))))
    rows.append((26, lambda y: t(y, "stations · certified / not yet / unchecked", 14, color=MUTED, x=PANEL_W - MARGIN,
                                 anchor="end")))
    tool = "rapp1_subway.py" if L["edition"] < 2 else "rapp1_network (subway.py)"
    notes = ["The RAPP/1 Core line runs in layer order, from 0 (RAPP/1) up to",
             "the Brainstem, and ends at rapp-installer: Start here. Each branch",
             "leaves the Core at the station its repos link to most (links_to).",
             ""]
    if L.get("summary"):
        notes += ["This poster names the Core stations and the interchanges, and",
                  "counts each branch's other stations (+ more · certified / not",
                  "yet / unchecked). Every station is on the zoomable map.",
                  ""]
    notes += [f"Checked with kody-w/rapp-1 rapp_check.py at {CANON_RAPP1[:7]}. Drawn from",
             f"portfolio/repos/*.md and lines/*.md by {tool}.",
             "Zoomable map with a click per station:",
             f"{PAGES}/subway.html"]
    for n, line in enumerate(notes):
        rows.append((48 if n == 0 else 22, lambda y, line=line: t(y, esc(line), 15, color=MUTED)))
    return rows


def panel_height(L):
    return sum(h for h, _ in panel_rows(L))


def panel(L):
    """Title, legend and totals, in the right-hand column."""
    x, y = L["map_width"] + 10, MARGIN
    out = [f'<g transform="translate({num(x)} {num(y)})">']
    for h, draw in panel_rows(L):
        y += h
        out.append(draw(y - MARGIN))
    out.append("</g>")
    if y + MARGIN > L["height"]:
        raise Refused("the legend is taller than the map")
    return "".join(out)


# ---- the HTML viewer ------------------------------------------------------------------------------------

# Edition 1's viewer, frozen: the style and script version 1's pages carry (their hashes are in its CSP).
CSS_V1 = """html,body{margin:0;height:100%;background:#f6f8fa;color:#1b1f24;font:15px Helvetica,Arial,sans-serif}
header{position:fixed;top:0;left:0;right:0;height:52px;display:flex;align-items:center;gap:10px;padding:0 14px;
background:#ffffffee;border-bottom:1px solid #d0d7de;z-index:2}
header h1{font-size:17px;margin:0 8px 0 0;white-space:nowrap}
header input{font:inherit;padding:6px 10px;border:1px solid #d0d7de;border-radius:6px;width:230px}
header button{font:inherit;padding:6px 11px;border:1px solid #d0d7de;border-radius:6px;background:#fff;cursor:pointer}
header a{color:#0969da;text-decoration:none;white-space:nowrap}
header select{font:inherit;padding:5px 8px;border:1px solid #d0d7de;border-radius:6px;background:#fff;max-width:280px}
header .ver{color:#57606a;white-space:nowrap}
header .grow{flex:1}
#map{position:fixed;top:53px;left:0;right:0;bottom:0}
#map svg{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#map svg.drag{cursor:grabbing}
#map a.st{cursor:pointer}
#map a.st:hover circle,#map a.st:focus circle{stroke:#0969da}
#map a.st.hit text{fill:#0969da;font-weight:700}
#map a.st:focus{outline:none}
aside{position:fixed;right:14px;top:66px;width:330px;background:#fff;border:1px solid #d0d7de;border-radius:10px;
box-shadow:0 8px 24px #1b1f2433;padding:14px 16px;z-index:3}
aside h2{font-size:19px;margin:0 30px 6px 0;word-break:break-all}
aside p{margin:6px 0}
aside .chips span{display:inline-block;margin:0 5px 5px 0;padding:2px 9px;border-radius:10px;font-size:13px;font-weight:700}
aside .links a{display:block;margin:8px 0 0;padding:8px 10px;border:1px solid #d0d7de;border-radius:6px;color:#0969da;
text-decoration:none;font-weight:700}
aside .close{position:absolute;right:10px;top:8px;border:0;background:none;font-size:22px;cursor:pointer;color:#57606a}
.status{font-weight:700}"""

JS_V1 = r"""(function () {
  "use strict";
  var svg = document.querySelector("#map svg");
  var full = svg.viewBox.baseVal;
  var home = [full.x, full.y, full.width, full.height];
  var vb = home.slice();
  var lines = JSON.parse(document.getElementById("lines").textContent);
  var panel = document.getElementById("info");
  var PUBLIC = panel.getAttribute("data-public");
  var REPO = panel.getAttribute("data-repo");
  function apply() { svg.setAttribute("viewBox", vb.map(function (v) { return v.toFixed(1); }).join(" ")); }
  function point(cx, cy) {
    var p = svg.createSVGPoint();
    p.x = cx; p.y = cy;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  }
  function zoomAt(cx, cy, k) {
    var w = Math.min(home[2] * 1.2, Math.max(home[2] / 14, vb[2] * k));
    var r = w / vb[2];
    var q = point(cx, cy);
    vb = [q.x - (q.x - vb[0]) * r, q.y - (q.y - vb[1]) * r, w, vb[3] * r];
    apply();
  }
  function centre() { var b = svg.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }
  svg.addEventListener("wheel", function (e) {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, Math.exp(e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)));
  }, { passive: false });
  var drag = null, moved = false;
  svg.addEventListener("pointerdown", function (e) {
    if (e.button !== 0) { return; }
    drag = { x: e.clientX, y: e.clientY, vb: vb.slice(), id: e.pointerId };
    moved = false;
  });
  svg.addEventListener("pointermove", function (e) {
    if (!drag) { return; }
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!moved && Math.abs(dx) + Math.abs(dy) < 5) { return; }
    if (!moved) { svg.setPointerCapture(drag.id); svg.classList.add("drag"); }
    moved = true;
    var b = svg.getBoundingClientRect();
    var s = Math.max(drag.vb[2] / b.width, drag.vb[3] / b.height);
    vb = [drag.vb[0] - dx * s, drag.vb[1] - dy * s, drag.vb[2], drag.vb[3]];
    apply();
  });
  function stop() { drag = null; svg.classList.remove("drag"); }
  svg.addEventListener("pointerup", stop);
  svg.addEventListener("pointercancel", stop);
  function chip(id) {
    var s = document.createElement("span");
    var line = lines[id];
    s.textContent = line.name;
    s.style.background = line.color;
    s.style.color = line.ink;
    return s;
  }
  function link(text, href) {
    var a = document.createElement("a");
    a.textContent = text;
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener";
    return a;
  }
  function show(st) {
    var d = st.dataset;
    while (panel.firstChild) { panel.removeChild(panel.firstChild); }
    var close = document.createElement("button");
    close.className = "close";
    close.setAttribute("aria-label", "Close");
    close.textContent = "\u00d7";
    close.addEventListener("click", function () { panel.hidden = true; });
    var h = document.createElement("h2");
    h.textContent = d.repo;
    var chips = document.createElement("p");
    chips.className = "chips";
    d.lines.split(",").forEach(function (id) { if (lines[id]) { chips.appendChild(chip(id)); } });
    var status = document.createElement("p");
    var strong = document.createElement("span");
    strong.className = "status";
    strong.textContent = d.status;
    status.appendChild(strong);
    var detail = d.commit ? " \u00b7 " + d.verdict + " at " + d.commit.slice(0, 10) + " \u00b7 checked " + d.checked : "";
    status.appendChild(document.createTextNode(detail + " \u00b7 wave " + d.wave));
    var links = document.createElement("p");
    links.textContent = "Links to " + d.out + " portfolio repos; linked from " + d["in"] + ".";
    var go = document.createElement("div");
    go.className = "links";
    go.appendChild(link("Open its portfolio file \u2192", PUBLIC + "/repos/" + encodeURIComponent(d.repo) + ".md"));
    go.appendChild(link("Open the repo \u2192", REPO + encodeURIComponent(d.repo)));
    [close, h, chips, status, links, go].forEach(function (n) { panel.appendChild(n); });
    panel.hidden = false;
  }
  var stations = Array.prototype.slice.call(document.querySelectorAll("#map a.st"));
  stations.forEach(function (st) {
    st.addEventListener("click", function (e) {
      e.preventDefault();
      if (moved) { return; }
      show(st);
    });
    st.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); show(st); }
    });
  });
  function focusOn(st) {
    var box = st.getBBox();
    var w = Math.min(vb[2], home[2] / 4), h = w * vb[3] / vb[2];
    vb = [box.x + box.width / 2 - w / 2, box.y + box.height / 2 - h / 2, w, h];
    apply();
    st.focus({ preventScroll: true });
    show(st);
  }
  var q = document.getElementById("q");
  q.addEventListener("input", function () {
    var t = q.value.trim().toLowerCase();
    stations.forEach(function (st) { st.classList.toggle("hit", t.length > 1 && st.dataset.repo.toLowerCase().indexOf(t) >= 0); });
  });
  q.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") { return; }
    var t = q.value.trim().toLowerCase();
    var exact = stations.filter(function (st) { return st.dataset.repo.toLowerCase() === t; });
    var any = stations.filter(function (st) { return st.dataset.repo.toLowerCase().indexOf(t) >= 0; });
    var st = exact[0] || any[0];
    if (st) { focusOn(st); }
  });
  document.getElementById("zin").addEventListener("click", function () { var c = centre(); zoomAt(c[0], c[1], 1 / 1.4); });
  document.getElementById("zout").addEventListener("click", function () { var c = centre(); zoomAt(c[0], c[1], 1.4); });
  document.getElementById("fit").addEventListener("click", function () { vb = home.slice(); apply(); });
  document.addEventListener("keydown", function (e) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "SELECT")) { return; }
    var c = centre(), step = vb[2] * 0.08;
    if (e.key === "+" || e.key === "=") { zoomAt(c[0], c[1], 1 / 1.25); }
    else if (e.key === "-") { zoomAt(c[0], c[1], 1.25); }
    else if (e.key === "0") { vb = home.slice(); apply(); }
    else if (e.key === "ArrowLeft") { vb[0] -= step; apply(); }
    else if (e.key === "ArrowRight") { vb[0] += step; apply(); }
    else if (e.key === "ArrowUp") { vb[1] -= step; apply(); }
    else if (e.key === "ArrowDown") { vb[1] += step; apply(); }
    else if (e.key === "Escape") { panel.hidden = true; }
  });
  var ver = document.getElementById("ver");
  if (ver) {
    ver.addEventListener("change", function () { if (ver.value) { window.location.href = ver.value; } });
  }
})();"""

# Edition 2's viewer: the header wraps so every control stays on screen (a phone, a tablet), the picker shows its whole
# label, the station panel sits inside the map area (a bottom sheet on a phone), form borders reach 3:1, and the
# keyboard gets a clear focus ring.
CSS = """html,body{margin:0;height:100%;background:#f6f8fa;color:#1b1f24;font:15px Helvetica,Arial,sans-serif}
body{display:flex;flex-direction:column}
header{flex:none;display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;padding:8px 14px;background:#fff;
border-bottom:1px solid #d0d7de;z-index:2}
header h1{font-size:17px;margin:0 8px 0 0;white-space:nowrap}
header input{font:inherit;padding:6px 10px;border:1px solid #6e7781;border-radius:6px;width:230px;max-width:100%;
box-sizing:border-box}
header button{font:inherit;color:inherit;padding:6px 11px;border:1px solid #6e7781;border-radius:6px;background:#fff;
cursor:pointer}
header select{font:inherit;color:inherit;padding:5px 8px;border:1px solid #6e7781;border-radius:6px;background:#fff;
max-width:100%}
header .ver{color:#57606a;white-space:nowrap}
header .grow{flex:1}
header nav{display:flex;flex-wrap:wrap;gap:4px 14px}
header a{color:#0969da;text-decoration:none;white-space:nowrap}
header a:hover{text-decoration:underline}
.stage{flex:1;min-height:0;position:relative}
#map{position:absolute;inset:0}
#map svg{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#map svg.drag{cursor:grabbing}
#map a.st{cursor:pointer}
#map a.st:hover circle{stroke:#0969da}
#map a.st.hit text{fill:#0969da;font-weight:700}
#map a.st:focus{outline:none}
#map a.st:focus-visible circle{stroke:#0969da;stroke-width:4px}
#map a.st:focus-visible text{fill:#0969da;font-weight:700;text-decoration:underline}
:focus-visible{outline:2px solid #0969da;outline-offset:2px}
header input[aria-invalid=true]{border-color:#cf222e;box-shadow:0 0 0 1px #cf222e}
.sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap;
border:0}
aside{position:absolute;right:14px;top:14px;width:330px;max-width:calc(100% - 28px);max-height:calc(100% - 28px);
overflow:auto;box-sizing:border-box;background:#fff;border:1px solid #d0d7de;border-radius:10px;
box-shadow:0 8px 24px #1b1f2433;padding:14px 16px;z-index:3}
aside h2{font-size:19px;margin:0 30px 6px 0;word-break:break-all}
aside p{margin:6px 0}
aside .chips span{display:inline-block;margin:0 5px 5px 0;padding:2px 9px;border-radius:10px;font-size:13px;font-weight:700}
aside .links a{display:block;margin:8px 0 0;padding:8px 10px;border:1px solid #d0d7de;border-radius:6px;color:#0969da;
text-decoration:none;font-weight:700}
aside .close{position:absolute;right:10px;top:8px;border:0;background:none;font-size:22px;cursor:pointer;color:#57606a}
.status{font-weight:700}
@media (max-width:640px){header{gap:6px 8px;padding:6px 10px}header input{flex:1 1 150px;width:auto}
header .grow{display:none}aside{left:8px;right:8px;top:auto;bottom:8px;width:auto;max-width:none;max-height:55%}}"""


# Edition 2's script: the keyboard reaches everything (Enter moves focus into the station panel, Escape brings it back;
# a station reached with Tab comes into view; the picker moves only on Enter or a pointer pick), a search that finds
# nothing says so, browser shortcuts with Ctrl, Alt or Cmd are left alone, and two fingers pinch to zoom.
JS = r"""(function () {
  "use strict";
  var svg = document.querySelector("#map svg");
  var full = svg.viewBox.baseVal;
  var home = [full.x, full.y, full.width, full.height];
  var vb = home.slice();
  var lines = JSON.parse(document.getElementById("lines").textContent);
  var panel = document.getElementById("info");
  var found = document.getElementById("found");
  var PUBLIC = panel.getAttribute("data-public");
  var REPO = panel.getAttribute("data-repo");
  var opener = null;
  function apply() { svg.setAttribute("viewBox", vb.map(function (v) { return v.toFixed(1); }).join(" ")); }
  function point(cx, cy) {
    var p = svg.createSVGPoint();
    p.x = cx; p.y = cy;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  }
  function zoomAt(cx, cy, k) {
    var w = Math.min(home[2] * 1.2, Math.max(home[2] / 14, vb[2] * k));
    var r = w / vb[2];
    var q = point(cx, cy);
    vb = [q.x - (q.x - vb[0]) * r, q.y - (q.y - vb[1]) * r, w, vb[3] * r];
    apply();
  }
  function centre() { var b = svg.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }
  svg.addEventListener("wheel", function (e) {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, Math.exp(e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)));
  }, { passive: false });
  // one pointer pans; two (a pinch) zoom about their midpoint and pan with it
  var touches = {}, drag = null, pinch = null, moved = false, pressed = false;
  function capture(id) { try { svg.setPointerCapture(id); } catch (err) { return; } }
  function pair() {
    var ids = Object.keys(touches), a = touches[ids[0]], b = touches[ids[1]];
    return { d: Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)), x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }
  svg.addEventListener("pointerdown", function (e) {
    if (e.pointerType === "mouse" && e.button !== 0) { return; }
    if (e.isPrimary) { touches = {}; pinch = null; }
    pressed = true;
    touches[e.pointerId] = { x: e.clientX, y: e.clientY };
    var n = Object.keys(touches).length;
    if (n === 1) {
      drag = { x: e.clientX, y: e.clientY, vb: vb.slice(), id: e.pointerId };
      moved = false;
    } else if (n === 2) {
      drag = null;
      pinch = pair();
      moved = true;
      Object.keys(touches).forEach(function (id) { capture(Number(id)); });
    }
  });
  svg.addEventListener("pointermove", function (e) {
    if (!touches[e.pointerId]) { return; }
    touches[e.pointerId] = { x: e.clientX, y: e.clientY };
    if (pinch) {
      var now = pair();
      zoomAt(now.x, now.y, pinch.d / now.d);
      var b = svg.getBoundingClientRect(), s = Math.max(vb[2] / b.width, vb[3] / b.height);
      vb[0] -= (now.x - pinch.x) * s;
      vb[1] -= (now.y - pinch.y) * s;
      apply();
      pinch = now;
      return;
    }
    if (!drag || e.pointerId !== drag.id) { return; }
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!moved && Math.abs(dx) + Math.abs(dy) < 5) { return; }
    if (!moved) { capture(drag.id); svg.classList.add("drag"); }
    moved = true;
    var r = svg.getBoundingClientRect();
    var k = Math.max(drag.vb[2] / r.width, drag.vb[3] / r.height);
    vb = [drag.vb[0] - dx * k, drag.vb[1] - dy * k, drag.vb[2], drag.vb[3]];
    apply();
  });
  function lift(e) {
    delete touches[e.pointerId];
    var left = Object.keys(touches);
    if (left.length < 2) { pinch = null; }
    if (left.length === 1) {
      var t = touches[left[0]];
      drag = { x: t.x, y: t.y, vb: vb.slice(), id: Number(left[0]) };
    } else if (!left.length) {
      drag = null;
      pressed = false;
      svg.classList.remove("drag");
    }
  }
  svg.addEventListener("pointerup", lift);
  svg.addEventListener("pointercancel", lift);
  function chip(id) {
    var s = document.createElement("span");
    var line = lines[id];
    s.textContent = line.name;
    s.style.background = line.color;
    s.style.color = line.ink;
    return s;
  }
  function link(text, href) {
    var a = document.createElement("a");
    a.textContent = text;
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener";
    return a;
  }
  function hide() {
    if (panel.hidden) { return; }
    var inside = panel.contains(document.activeElement);
    panel.hidden = true;
    if (inside && opener) { opener.focus({ preventScroll: true }); }
  }
  function show(st, keyboard) {
    var d = st.dataset;
    while (panel.firstChild) { panel.removeChild(panel.firstChild); }
    var h = document.createElement("h2");
    h.id = "info-title";
    h.tabIndex = -1;
    h.textContent = d.repo;
    var chips = document.createElement("p");
    chips.className = "chips";
    d.lines.split(",").forEach(function (id) { if (lines[id]) { chips.appendChild(chip(id)); } });
    var status = document.createElement("p");
    var strong = document.createElement("span");
    strong.className = "status";
    strong.textContent = d.status;
    status.appendChild(strong);
    var detail = d.commit ? " \u00b7 " + d.verdict + " at " + d.commit.slice(0, 10) + " \u00b7 checked " + d.checked : "";
    var life = (d.lifecycle && d.lifecycle !== "active" ? " \u00b7 " + d.lifecycle : "") +
      (d.version ? " \u00b7 version " + d.version : "");
    status.appendChild(document.createTextNode(detail + " \u00b7 wave " + d.wave + life));
    var links = document.createElement("p");
    links.textContent = "Links to " + d.out + " portfolio repos; linked from " + d["in"] + ".";
    var go = document.createElement("div");
    go.className = "links";
    go.appendChild(link("Open its portfolio file \u2192", PUBLIC + "/repos/" + encodeURIComponent(d.repo) + ".md"));
    go.appendChild(link("Open the repo \u2192", REPO + encodeURIComponent(d.repo)));
    var close = document.createElement("button");
    close.type = "button";
    close.className = "close";
    close.setAttribute("aria-label", "Close");
    close.textContent = "\u00d7";
    close.addEventListener("click", hide);
    [h, chips, status, links, go, close].forEach(function (n) { panel.appendChild(n); });
    panel.hidden = false;
    opener = st;
    if (keyboard) { h.focus(); }
  }
  var stations = Array.prototype.slice.call(document.querySelectorAll("#map a.st"));
  stations.forEach(function (st) {
    st.addEventListener("click", function (e) {
      e.preventDefault();
      if (moved) { return; }
      show(st, e.detail === 0);
    });
    st.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); show(st, true); }
    });
  });
  svg.addEventListener("focusin", function (e) {
    var st = e.target;
    if (pressed || !st.classList || !st.classList.contains("st")) { return; }
    var b = st.getBBox();
    if (b.x < vb[0] || b.y < vb[1] || b.x + b.width > vb[0] + vb[2] || b.y + b.height > vb[1] + vb[3]) {
      vb[0] = b.x + b.width / 2 - vb[2] / 2;
      vb[1] = b.y + b.height / 2 - vb[3] / 2;
      apply();
    }
  });
  function focusOn(st) {
    var box = st.getBBox();
    var w = Math.min(vb[2], home[2] / 4), h = w * vb[3] / vb[2];
    vb = [box.x + box.width / 2 - w / 2, box.y + box.height / 2 - h / 2, w, h];
    apply();
    st.focus({ preventScroll: true });
    show(st, true);
  }
  var q = document.getElementById("q");
  q.addEventListener("input", function () {
    var t = q.value.trim().toLowerCase(), n = 0;
    q.removeAttribute("aria-invalid");
    stations.forEach(function (st) {
      var hit = t.length > 1 && st.dataset.repo.toLowerCase().indexOf(t) >= 0;
      st.classList.toggle("hit", hit);
      n += hit ? 1 : 0;
    });
    found.textContent = t.length > 1 ? (n ? n + (n === 1 ? " repo matches" : " repos match") : "No repo matches") : "";
  });
  q.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") { return; }
    var t = q.value.trim().toLowerCase();
    if (!t) { return; }
    var exact = stations.filter(function (st) { return st.dataset.repo.toLowerCase() === t; });
    var any = stations.filter(function (st) { return st.dataset.repo.toLowerCase().indexOf(t) >= 0; });
    var st = exact[0] || any[0];
    if (st) { q.removeAttribute("aria-invalid"); focusOn(st); return; }
    q.setAttribute("aria-invalid", "true");
    found.textContent = "No repo matches \u201c" + q.value.trim() + "\u201d";
  });
  document.getElementById("zin").addEventListener("click", function () { var c = centre(); zoomAt(c[0], c[1], 1 / 1.4); });
  document.getElementById("zout").addEventListener("click", function () { var c = centre(); zoomAt(c[0], c[1], 1.4); });
  document.getElementById("fit").addEventListener("click", function () { vb = home.slice(); apply(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { hide(); return; }
    if (e.altKey || e.ctrlKey || e.metaKey) { return; }
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "SELECT")) { return; }
    var c = centre(), step = vb[2] * 0.08;
    if (e.key === "+" || e.key === "=") { zoomAt(c[0], c[1], 1 / 1.25); }
    else if (e.key === "-") { zoomAt(c[0], c[1], 1.25); }
    else if (e.key === "0") { vb = home.slice(); apply(); }
    else if (e.key === "ArrowLeft") { vb[0] -= step; apply(); }
    else if (e.key === "ArrowRight") { vb[0] += step; apply(); }
    else if (e.key === "ArrowUp") { vb[1] -= step; apply(); }
    else if (e.key === "ArrowDown") { vb[1] += step; apply(); }
  });
  var ver = document.getElementById("ver");
  if (ver) {
    var chosen = ver.value, keyed = false;
    var go = function () { if (ver.value && ver.value !== chosen) { window.location.href = ver.value; } };
    ver.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); keyed = false; go(); }
      else if (e.key !== "Tab" && e.key !== "Shift" && e.key !== "Escape") { keyed = true; }
    });
    ver.addEventListener("pointerdown", function () { keyed = false; });
    ver.addEventListener("change", function () { if (!keyed) { go(); } });
  }
})();"""



def page(L, drawing, nav=None, prefix=""):
    """The zoomable viewer. `nav` = {entries: [{label, url, selected}], latest: url|None, timeline: url|None}."""
    nav = nav or {}
    v1 = L["edition"] < 2
    css, js = (CSS_V1, JS_V1) if v1 else (CSS, JS)
    lines = {i: {"name": line["name"], "color": line["color"], "ink": ink_on(line["color"], L["edition"])}
             for i, line in L["lines"].items()}
    data = json.dumps(lines, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    sha = lambda s: "sha256-" + base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode()
    csp = (f"default-src 'none'; script-src '{sha(js)}'; style-src '{sha(css)}'; img-src data:; "
           "base-uri 'none'; form-action 'none'")
    total, version = len(L["repos"]), L.get("version")
    if nav.get("entries"):
        options = "".join(f'<option value="{esc(e["url"])}"{" selected" if e.get("selected") else ""}>{esc(e["label"])}</option>'
                          for e in nav["entries"])
        picker = f'<select id="ver" aria-label="Map version">{options}</select>'
    else:
        picker = f'<span class="ver">Version {version["number"]}</span>' if version else ""
    links = (f'<a href="{esc(nav["latest"])}">Latest map</a>' if nav.get("latest") else "") + (
        f'<a href="{esc(nav["timeline"])}">Timeline</a>' if nav.get("timeline") else "")
    links += (f'<a href="{PAGES}/{prefix}subway.pdf">Poster (PDF)</a><a href="{PUBLIC_BLOB}/PORTFOLIO.md">Portfolio</a>'
              + ("" if v1 else f'<a href="{PAGES}/NOTICES.html">Notices</a>')
              + f'<a href="https://github.com/kody-w/rapp-installer#start-here">Start here</a>')
    title = f"RAPP/1 network: subway map of {total} repos" + (f", version {version['number']}" if version else "")
    head = (f'<!doctype html>\n<html lang="en"{"" if v1 else f' data-edition="{L["edition"]}"'}>\n<head>\n'
            f'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n'
            f'<meta name="referrer" content="no-referrer">\n'
            f'<title>{esc(title)}</title>\n<style>{css}</style>\n</head>\n<body>\n')
    found = "" if v1 else '<span id="found" class="sr" role="status"></span>'
    controls = (f'<header><h1>RAPP/1 network</h1><input id="q" type="search" placeholder="Find a repo, then Enter" '
                f'aria-label="Find a repo">{found}<button id="zin" type="button" aria-label="Zoom in">+</button>'
                f'<button id="zout" type="button" aria-label="Zoom out">\u2212</button>'
                f'<button id="fit" type="button">Fit</button>{picker}<span class="grow"></span>')
    aside = f'<aside id="info" hidden data-public="{PUBLIC_BLOB}" data-repo="{REPO_URL}" aria-live="polite"></aside>'
    tail = f'<script type="application/json" id="lines">{data}</script>\n<script>{js}</script>\n</body>\n</html>\n'
    if v1:
        return f'{head}{controls}{links}</header>\n<main id="map">{drawing}</main>\n{aside}\n{tail}'
    return (f'{head}{controls}<nav aria-label="Links">{links}</nav></header>\n'
            f'<div class="stage"><main id="map">{drawing}</main>\n{aside}</div>\n{tail}')


def poster_scale(L):
    """Millimetres per drawing pixel on the poster: its long edge is A0's (edition 1 always scaled the width)."""
    return POSTER_MM / (max(L["width"], L["height"]) if L["edition"] >= 2 else L["width"])


def legible(L):
    """Whether every station's name prints with a cap height of at least MIN_TEXT_MM on the poster."""
    return LABEL * CAP_HEIGHT * poster_scale(L) >= MIN_TEXT_MM


def poster(L, drawing):
    """The page Chrome prints: the drawing alone, scaled onto one page whose long edge is A0's."""
    if L["edition"] >= 2 and L["height"] > L["width"]:
        w_mm, h_mm = POSTER_MM * (L["width"] / L["height"]), POSTER_MM
    else:
        ratio = L["height"] / L["width"]
        w_mm, h_mm = POSTER_MM, POSTER_MM * ratio
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>RAPP/1 network subway map</title>'
            f'<style>@page{{size:{num(w_mm)}mm {num(h_mm)}mm;margin:0}}html,body{{margin:0;padding:0}}'
            f'svg{{display:block;width:{num(w_mm)}mm;height:{num(h_mm)}mm}}</style></head><body>{drawing}</body></html>\n')


# ---- the version chain, the build and the check -----------------------------------------------------------


def version_id(frame):
    """The version folder a pulse lives in: its crawl date and sequence, e.g. 2026-09-25-0."""
    return f"{frame['utc'][:10]}-{frame['seq']}"


def chain(folder):
    """[(version number, folder id, crawl utc)] from the folder's pulse chain, oldest first. Reading only: the
    pipeline verifies every pulse before it is written (pulses.py); this just labels the maps."""
    folder = Path(folder)
    out = []
    for path in sorted(folder.glob("versions/*/pulse.json.md")):
        frame = json.loads(unwrap(path.read_text(encoding="utf-8")))
        payload = frame.get("payload", {})
        out.append((int(payload.get("version", frame["seq"] + 1)), path.parent.name,
                    payload.get("crawl", {}).get("finished_utc", frame["utc"]), frame["seq"]))
    return [(n, vid, utc) for n, vid, utc, _ in sorted(out, key=lambda item: item[3])]


def nav_for(versions, current=None):
    """The picker: every version (newest first) for the stable page, or versions up to `current` for a version page
    (so a version's page never changes once written)."""
    if current is not None:
        shown = [v for v in versions if v[0] <= current]
        entries = [{"label": f"Version {n} · {utc[:10]} {utc[11:16]} UTC", "url": f"{PAGES}/versions/{vid}/subway.html",
                    "selected": n == current} for n, vid, utc in reversed(shown)]
        return {"entries": entries, "latest": f"{PAGES}/subway.html", "timeline": f"{PAGES}/timeline.html"}
    entries = [{"label": f"Version {n} · {utc[:10]} {utc[11:16]} UTC" + (" (latest)" if k == 0 else ""),
                "url": f"{PAGES}/subway.html" if k == 0 else f"{PAGES}/versions/{vid}/subway.html", "selected": k == 0}
               for k, (n, vid, utc) in enumerate(reversed(versions))]
    return {"entries": entries, "latest": None, "timeline": f"{PAGES}/timeline.html" if versions else None}


def render(folder, version=None, nav=None, prefix="", pdf=False, printer=None, edition=None):
    """({name: wrapped text}, L) for one place: subway.svg.md, subway.html.md and, with pdf, subway.pdf.md, served at
    /portfolio/<prefix>subway.*. `version` = {number, utc} labels the legend; `nav` fills the viewer's picker.
    `printer(poster_html, date, permalink) -> wrapped text` prints the PDF (default: headless Chrome, pdf.print_pdf).
    The version picks the edition that draws it (edition_for); `edition` overrides that, e.g. to compare editions."""
    repos, lines = load(folder)
    L = layout(repos, lines, version, edition)
    drawing, viewer = svg(L), svg(L, interactive=True)
    printed = L
    if L["edition"] >= 2 and not legible(L):  # not every name fits legibly on one A0 page: the summary poster
        printed = layout(repos, lines, version, L["edition"], summary=True)
    files = {"subway.svg.md": wrap(f"/portfolio/{prefix}subway.svg", drawing),
             "subway.html.md": wrap(f"/portfolio/{prefix}subway.html", page(L, viewer, nav, prefix))}
    poster_html = poster(printed, svg(printed, links=False))
    date = (version["utc"][:10] if version else
            max((r["checked"] for r in repos.values() if r["checked"]), default="1970-01-01"))
    if pdf:
        files["subway.pdf.md"] = (printer or pdf_printer.print_pdf)(poster_html, date, f"/portfolio/{prefix}subway.pdf")
    for name, text in files.items():
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise Refused(f"{prefix}{name} is over the Hive's 1 MB limit")
    L["poster_sha256"] = hashlib.sha256(poster_html.encode("utf-8")).hexdigest()
    L["poster_html"] = poster_html
    L["poster_summary"] = printed is not L
    return files, L


def stable_label(folder):
    """({number, utc} of the folder's latest version, the stable picker), or (None, None) without a chain."""
    versions = chain(folder)
    if not versions:
        return None, None
    n, vid, utc = versions[-1]
    return {"number": n, "utc": utc}, nav_for(versions)


def build(folder, pdf=False, printer=None, say=print):
    """Write the stable map files, labelled with the folder's latest version (the pipeline's cut does this too)."""
    folder = Path(folder)
    version, nav = stable_label(folder)
    files, L = render(folder, version, nav, pdf=pdf, printer=printer)
    for name, text in files.items():
        path = folder / name
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            write_text(path, text)
    stale = check(folder, quiet=True)
    say(f"subway: {len(L['repos'])} stations on {sum(1 for _ in L['lines'])} lines, {len(L['interchange'])} "
        f"interchanges; {L['width']:.0f} x {L['height']:.0f} px" + (f"; stale: {', '.join(stale)}" if stale else ""))
    return L


def check(folder, quiet=False, say=print):
    """The stable map files that differ from a rebuild in memory (the PDF by its printed_from); [] when all match."""
    folder = Path(folder)
    version, nav = stable_label(folder)
    files, L = render(folder, version, nav)
    stale = [name for name, text in files.items()
             if not (folder / name).is_file() or (folder / name).read_text(encoding="utf-8") != text]
    pdf = folder / "subway.pdf.md"
    if not pdf.is_file() or f"printed_from: {L['poster_sha256']}\n" not in pdf.read_text(encoding="utf-8")[:400]:
        stale.append("subway.pdf.md")
    if not quiet:
        for name in stale:
            say(f"stale: {name} differs from the portfolio files; run python -m rapp1_network subway {folder}" +
                (" --pdf" if name.endswith("pdf.md") else ""))
        if not stale:
            say(f"subway: all 3 stable map files match the portfolio files" +
                (f" (version {version['number']})" if version else ""))
    return stale


def main(argv=None):
    """`<portfolio-folder> [--pdf | --check]`: 0 done (or all match), 1 refused (or stale), 2 usage."""
    argv = sys.argv[1:] if argv is None else list(argv)
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    try:
        if "--check" in argv:
            return 1 if check(args[0]) else 0
        build(args[0], pdf="--pdf" in argv)
        return 0
    except Refused as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
`````
{% endraw %}
