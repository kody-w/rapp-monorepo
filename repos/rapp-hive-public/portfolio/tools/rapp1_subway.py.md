# rapp1_subway.py

The map generator. It draws every portfolio repo as a station on its family's line and writes the SVG, the zoomable HTML and the one-page PDF.

SHA-256 of the source below: `9f95a0ddc594a932444e91cea51045d257a62ca0a49af5dcc7a8437e5380c481` (54274 bytes). Every pulse records it in `payload.generator`. Copy it out with the extractor in [README.md](README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
#!/usr/bin/env python3
"""Draw the RAPP/1 network as a subway map, from the portfolio files alone.

    python3 -B rapp1_subway.py <portfolio-folder>           write the stable subway.svg.md and subway.html.md
    python3 -B rapp1_subway.py <portfolio-folder> --pdf     also print subway.pdf with headless Chrome (one page)
    python3 -B rapp1_subway.py <portfolio-folder> --check   rebuild in memory; exit 1 if a stable map file differs

rapp1_portfolio.py calls render() once per crawl for the version folder (versions/<id>/) and once for the stable
path, which always shows the latest map with a picker for every version.

Standard library only. The same portfolio files always give the same bytes. Lines are the families (lines/*.md),
stations are the repos (repos/*.md) filled by their earned RAPP/1 status, and the RAPP/1 Core line runs in layer
order to the Start here terminal. A Hive holds only markdown, so every output is a .md file whose front matter
tells GitHub Pages where to serve it and whose body passes through untouched ({::nomarkdown}); the PDF is
rewritten as 7-bit text (ASCIIHex streams) so it fits that rule, and renders exactly as Chrome printed it.
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PAGES = "https://kody-w.github.io/rapp-hive-public/portfolio"
PUBLIC_BLOB = "https://github.com/kody-w/rapp-hive-public/blob/main/portfolio"
REPO_URL = "https://github.com/kody-w/"
STATUS = {"certified": "#2da44e", "not yet": "#dfb317", "unchecked": "#9f9f9f"}
INK, PAPER, MUTED = "#1b1f24", "#ffffff", "#57606a"
FONT = "Helvetica, Arial, sans-serif"
HUB_LINES = 6          # a station linked from this many other lines (a third of them) is an interchange
POSTER_MM = 1189       # the poster's long edge: A0

# Geometry, in SVG pixels.
LABEL, TRUNK_LABEL, TAG = 13, 17, 12
STEP, R, R_TRUNK = 26, 6, 10
LINE_W, TRUNK_W, LANE, STEM, COL_GAP = 7, 12, 12, 11, 42
MARGIN, LABEL_BAND, LAYER_BAND, BADGE_H, CALLOUT_W, PANEL_W = 70, 54, 62, 30, 470, 640
MAX_BYTES = 1 << 20    # the Hive's limit for one file

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


class Refused(Exception):
    """The portfolio breaks a rule the map needs. The message names what to fix."""


def text_w(s, size, bold=False):
    table = WIDTHS[bold]
    return sum(table.get(ch, 1000 if ch in "→←" else 600) for ch in s) * size / 1000 * 1.06  # slack for Arial


def num(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(str(s), quote=True)


def ink_on(color):  # black or white text on a fill, by luminance
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
        if meta.get("family") not in lines or meta.get("status") not in STATUS:
            raise Refused(f"repos/{path.name}: its family must be a line in lines/ and its status one of {list(STATUS)}")
        repos[name] = {"repo": name, "line": meta["family"], "also": [a for a in listed(meta, "also_on") if a in lines],
                       "status": meta["status"], "verdict": meta.get("verdict", ""),
                       "commit": meta.get("evidence_commit", ""), "checked": meta.get("checked", ""),
                       "wave": str(meta.get("wave", "")), "links": [x for x in listed(meta, "links_to")]}
    for r in repos.values():
        r["links"] = sorted({x for x in r["links"] if x in repos and x != r["repo"]}, key=str.lower)
    core = [line for line in lines.values() if line["trunk"]]
    if len(core) != 1 or any(s not in repos for s, _ in core[0]["trunk"]):
        raise Refused("exactly one line needs a trunk, and every trunk station must be a repo in repos/")
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
    offs = [0.0]
    for i in range(1, len(widths)):
        offs.append(offs[-1] + (widths[i - 1] + widths[i]) / 2 + COL_GAP)
    ys = pav([c - s for c, s in zip(centers, offs)])
    low, high = lo + widths[0] / 2, hi - widths[-1] / 2 - offs[-1]
    if low > high:
        raise Refused("the columns do not fit the width")
    return [min(max(y, low), high) + s for y, s in zip(ys, offs)]


def layout(repos, lines, version=None):
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
        if line is core:
            continue
        members = sorted((n for n, r in repos.items() if r["line"] == line["id"] and n not in trunk),
                         key=lambda n: (-len(linked_from[n]), n.lower()))
        if not members:
            continue
        inside = [s for s in trunk if repos[s]["line"] == line["id"]]
        weight = {s: sum((s in repos[m]["links"]) + (m in repos[s]["links"]) for m in members) for s in trunk}
        junction = inside[0] if inside else max(trunk, key=lambda s: (weight[s], trunk.index(s)))
        branches.append({"line": line, "members": members, "junction": junction})
    heights = {"up": 0, "down": 0}
    for b in sorted(branches, key=lambda b: (-len(b["members"]), b["line"]["order"])):
        b["side"] = "up" if heights["up"] <= heights["down"] else "down"
        heights[b["side"]] += len(b["members"])
    interchange = {n for n in repos if len(on_lines[n]) > 1 or len(in_lines[n]) >= HUB_LINES}
    interchange |= {b["junction"] for b in branches}

    def col_width(b):
        widest = max(text_w(n, LABEL) + 11 * len([a for a in repos[n]["also"]]) for n in b["members"])
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
    col_len = lambda b: (len(b["members"]) - 1) * STEP + 44 + BADGE_H
    h_up = max([col_len(b) for b in up] or [0])
    h_down = max([col_len(b) for b in down] or [0])
    man_up, man_down = up_lanes * LANE + 26, down_lanes * LANE + 26
    y0 = MARGIN + h_up + 34 + man_up + LABEL_BAND
    first_up = y0 - LABEL_BAND - man_up - 34
    first_down = y0 + LAYER_BAND + man_down + 34
    height = first_down + h_down + MARGIN
    for b in up:
        b["lane_y"] = y0 - LABEL_BAND - 14 - max(b["lane"], 0) * LANE
        b["ys"] = [first_up - i * STEP for i in range(len(b["members"]))]
    for b in down:
        b["lane_y"] = y0 + LAYER_BAND + 14 + max(b["lane"], 0) * LANE
        b["ys"] = [first_down + i * STEP for i in range(len(b["members"]))]
    stems = {s: [b["stem"] - tx[s] for b in branches if b["junction"] == s] for s in trunk}
    result = {"repos": repos, "lines": lines, "core": core, "trunk": trunk, "layer": layer, "tx": tx, "y0": y0,
            "branches": up + down, "width": width + PANEL_W, "map_width": width,
            "height": height,
            "interchange": interchange, "linked_from": linked_from, "in_lines": in_lines, "on_lines": on_lines,
            "stems": stems, "version": version}
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


def station_group(L, name, x, y, r, label_x, label_y, size, bold, interactive, anchor="start", links=True):
    repo = L["repos"][name]
    ring = name in L["interchange"]
    lines = sorted(L["on_lines"][name], key=lambda i: L["lines"][i]["order"])
    attrs = (f' class="st" data-repo="{esc(name)}" data-status="{esc(repo["status"])}" data-verdict="{esc(repo["verdict"])}"'
             f' data-commit="{esc(repo["commit"])}" data-checked="{esc(repo["checked"])}" data-wave="{esc(repo["wave"])}"'
             f' data-lines="{esc(",".join(lines))}" data-out="{len(repo["links"])}" data-in="{len(L["linked_from"][name])}"'
             f' tabindex="0" role="button" aria-label="{esc(name)}: {esc(repo["status"])}"' if interactive else "")
    parts = [f'<a href="{PUBLIC_BLOB}/repos/{esc(name)}.md" target="_blank"{attrs}>' if links else "<g>"]
    if ring:
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r + 4.5)}" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>')
    parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{STATUS[repo["status"]]}" stroke="{INK}" '
                 f'stroke-width="{2.5 if r > R else 1.6}"/>')
    weight = ' font-weight="700"' if bold else ""
    halo = f' paint-order="stroke" stroke="{PAPER}" stroke-width="4"' if bold else ""  # trunk labels sit near lines
    parts.append(f'<text x="{num(label_x)}" y="{num(label_y)}" font-size="{size}"{weight} text-anchor="{anchor}" '
                 f'fill="{INK}"{halo}>{esc(name)}</text>')
    dot_x = label_x + text_w(name, size, bold) / 1.06 + 8
    for other in [i for i in lines if i != repo["line"] and not (name in L["trunk"] and i == L["core"]["id"])]:
        parts.append(f'<circle cx="{num(dot_x)}" cy="{num(label_y - size * 0.33)}" r="4" '
                     f'fill="{L["lines"][other]["color"]}" stroke="{PAPER}" stroke-width="1"/>')
        dot_x += 11
    parts.append("</a>" if links else "</g>")
    return "".join(parts)


def svg(L, interactive=False, links=True):
    W, H, y0, tx, core = L["width"], L["height"], L["y0"], L["tx"], L["core"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(W)} {num(H)}" width="{num(W)}" height="{num(H)}" '
           f'font-family="{FONT}" role="img" aria-labelledby="map-title map-desc">',
           f'<title id="map-title">RAPP/1 network subway map</title>',
           f'<desc id="map-desc">Every public RAPP repo as a station, filled by its earned RAPP/1 status; lines are '
           f'families; the RAPP/1 Core line runs in layer order to the Start here terminal, rapp-installer.</desc>',
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
                   f'<text x="{num(bx + 11)}" y="{num(by + 20)}" font-size="14" font-weight="700" fill="{ink_on(line["color"])}">'
                   f'{esc(text)}</text></g>')
    # branch stations
    for b in L["branches"]:
        for name, y in zip(b["members"], b["ys"]):
            out.append(station_group(L, name, b["col"], y, R, b["col"] + R + 9, y + 4.6, LABEL, False, interactive,
                                     links=links))
    # trunk stations, their layer tags, and the terminal
    for s in L["trunk"]:
        right = max([d for d in L["stems"][s]] + [0])
        lx = tx[s] + max(right, 0) + R_TRUNK + 12
        r = R_TRUNK + (6 if s == last else 0)
        out.append(station_group(L, s, tx[s], y0, r, lx, y0 - 17, TRUNK_LABEL, True, interactive, links=links))
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
    notes = ["The RAPP/1 Core line runs in layer order, from 0 (RAPP/1) up to",
             "the Brainstem, and ends at rapp-installer: Start here. Each branch",
             "leaves the Core at the station its repos link to most (links_to).",
             "",
             "Checked with kody-w/rapp-1 rapp_check.py at 591e014. Drawn from",
             "portfolio/repos/*.md and lines/*.md by rapp1_subway.py.",
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

CSS = """html,body{margin:0;height:100%;background:#f6f8fa;color:#1b1f24;font:15px Helvetica,Arial,sans-serif}
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

JS = r"""(function () {
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


def page(L, drawing, nav=None, prefix=""):
    """The zoomable viewer. `nav` = {entries: [{label, url, selected}], latest: url|None, timeline: url|None}."""
    nav = nav or {}
    lines = {i: {"name": line["name"], "color": line["color"], "ink": ink_on(line["color"])} for i, line in L["lines"].items()}
    data = json.dumps(lines, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    sha = lambda s: "sha256-" + base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode()
    csp = (f"default-src 'none'; script-src '{sha(JS)}'; style-src '{sha(CSS)}'; img-src data:; "
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
    title = f"RAPP/1 network: subway map of {total} repos" + (f", version {version['number']}" if version else "")
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n'
            f'<meta name="referrer" content="no-referrer">\n'
            f'<title>{esc(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n'
            f'<header><h1>RAPP/1 network</h1><input id="q" type="search" placeholder="Find a repo, then Enter" '
            f'aria-label="Find a repo"><button id="zin" type="button" aria-label="Zoom in">+</button>'
            f'<button id="zout" type="button" aria-label="Zoom out">\u2212</button><button id="fit" type="button">Fit</button>'
            f'{picker}<span class="grow"></span>{links}<a href="{PAGES}/{prefix}subway.pdf">Poster (PDF)</a>'
            f'<a href="{PUBLIC_BLOB}/PORTFOLIO.md">Portfolio</a>'
            f'<a href="https://github.com/kody-w/rapp-installer#start-here">Start here</a></header>\n'
            f'<main id="map">{drawing}</main>\n'
            f'<aside id="info" hidden data-public="{PUBLIC_BLOB}" data-repo="{REPO_URL}" aria-live="polite"></aside>\n'
            f'<script type="application/json" id="lines">{data}</script>\n'
            f'<script>{JS}</script>\n</body>\n</html>\n')


def poster(L, drawing):
    """The page Chrome prints: the drawing alone, scaled onto one A0-long page."""
    ratio = L["height"] / L["width"]
    w_mm, h_mm = POSTER_MM, POSTER_MM * ratio
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>RAPP/1 network subway map</title>'
            f'<style>@page{{size:{num(w_mm)}mm {num(h_mm)}mm;margin:0}}html,body{{margin:0;padding:0}}'
            f'svg{{display:block;width:{num(w_mm)}mm;height:{num(h_mm)}mm}}</style></head><body>{drawing}</body></html>\n')


# ---- the Hive's wrappers, the PDF, and the build ----------------------------------------------------------

def wrap(permalink, body):
    """A markdown file GitHub Pages serves at `permalink`, body untouched: Jekyll's front matter, then a raw block."""
    if "{{" in body or "{%" in body or "{:/" in body:
        raise Refused(f"{permalink}: the body holds Liquid or kramdown markers, which Pages would change")
    if "\r" in body or re.search(r"[\x00-\x08\x0b-\x1f\x7f]", body):
        raise Refused(f"{permalink}: only printable text and line feeds may pass through the Hive")
    return f"---\npermalink: {permalink}\nlayout: null\n---\n{{::nomarkdown}}\n{body.rstrip(chr(10))}\n{{:/}}\n"


def unwrap(text):
    body = text.split("{::nomarkdown}\n", 1)[1]
    return body[: body.rindex("\n{:/}")] + "\n"


WS, DELIM = b" \t\r\n\f\x00", b"()<>[]{}/%"


def _ws(d, i):
    while i < len(d):
        if d[i] in WS:
            i += 1
        elif d[i] == 0x25:
            while i < len(d) and d[i] not in b"\r\n":
                i += 1
        else:
            break
    return i


def _token(d, i):
    j = i
    while j < len(d) and d[j] not in WS and d[j] not in DELIM:
        j += 1
    return j


def _value(d, i):
    """The end of the PDF value that starts at i."""
    i = _ws(d, i)
    if d.startswith(b"<<", i):
        i += 2
        while True:
            i = _ws(d, i)
            if d.startswith(b">>", i):
                return i + 2
            i = _value(d, _value(d, i))
    c = d[i:i + 1]
    if c == b"[":
        i += 1
        while True:
            i = _ws(d, i)
            if d[i:i + 1] == b"]":
                return i + 1
            i = _value(d, i)
    if c == b"(":
        depth = 0
        while True:
            ch = d[i]
            if ch == 0x5C:
                i += 2
                continue
            depth += (ch == 0x28) - (ch == 0x29)
            i += 1
            if depth == 0:
                return i
    if c == b"<":
        return d.index(b">", i) + 1
    if c == b"/":
        return _token(d, i + 1)
    j = _token(d, i)
    if re.fullmatch(rb"\d+", d[i:j]):  # an indirect reference "n g R"
        k = _ws(d, j)
        k2 = _token(d, k)
        if re.fullmatch(rb"\d+", d[k:k2]):
            k3 = _ws(d, k2)
            if d[k3:k3 + 1] == b"R" and _token(d, k3) == k3 + 1:
                return k3 + 1
    return j


def _entries(d):
    """[(key, raw value)] of the dictionary d."""
    i, out = _ws(d, 0) + 2, []
    while True:
        i = _ws(d, i)
        if d.startswith(b">>", i):
            return out
        k = _value(d, i)
        v0 = _ws(d, k)
        v1 = _value(d, v0)
        out.append((d[i:k], d[v0:v1]))
        i = v1


def _ascii_strings(d):
    """Literal strings holding bytes outside printable ASCII become hex strings with the same bytes."""
    out, i = bytearray(), 0
    while i < len(d):
        ch = d[i]
        if ch == 0x28:
            j = _value(d, i)
            raw = d[i + 1:j - 1]
            if any(b > 0x7E or (b < 0x20 and b not in b"\n") for b in raw) or b"\r" in raw:
                s, k = bytearray(), 0
                while k < len(raw):  # undo the literal string's escapes
                    b = raw[k]
                    if b == 0x5C and k + 1 < len(raw):
                        n = raw[k + 1]
                        simple = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12, 0x28: 0x28, 0x29: 0x29, 0x5C: 0x5C}
                        if n in simple:
                            s.append(simple[n]); k += 2
                        elif 0x30 <= n <= 0x37:
                            m = re.match(rb"[0-7]{1,3}", raw[k + 1:k + 4]).group(0)
                            s.append(int(m, 8) & 0xFF); k += 1 + len(m)
                        elif n in b"\r\n":
                            k += 2 + (n == 13 and raw[k + 2:k + 3] == b"\n")
                        else:
                            s.append(n); k += 2
                    else:
                        s.append(b); k += 1
                out += b"<" + bytes(s).hex().upper().encode() + b">"
            else:
                out += d[i:j]
            i = j
        elif d.startswith(b"<<", i) or d.startswith(b">>", i):
            out += d[i:i + 2]
            i += 2
        elif ch == 0x3C:
            j = d.index(b">", i) + 1
            out += d[i:j]
            i = j
        else:
            out.append(ch)
            i += 1
    return bytes(out)


def ascii_pdf(data, date):
    """Rewrite Chrome's classic-xref PDF as 7-bit text, with fixed dates and IDs so a reprint gives the same bytes."""
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    if not m or not data.startswith(b"%PDF-"):
        raise Refused("subway.pdf: not a PDF Chrome wrote")
    at = int(m.group(1))
    if not data.startswith(b"xref", at):
        raise Refused("subway.pdf: its cross-reference is a stream; only classic tables are rewritten")
    offsets, i = {}, at + 4
    while True:
        i = _ws(data, i)
        if data.startswith(b"trailer", i):
            break
        head = re.match(rb"(\d+)\s+(\d+)", data[i:i + 40])
        first, count = int(head.group(1)), int(head.group(2))
        i += head.end()
        for n in range(count):
            i = _ws(data, i)
            entry = data[i:i + 18]
            if entry[17:18] == b"n":
                offsets[first + n] = int(entry[:10])
            i += 18
    t0 = _ws(data, i + 7)
    trailer = dict(_entries(data[t0:_value(data, t0)]))

    def obj(n):
        o = offsets[n]
        h = re.match(rb"\s*(\d+)\s+(\d+)\s+obj", data[o:o + 40])
        s = o + h.end()
        e = _value(data, s)
        return s, e

    def length_of(raw):
        ref = re.fullmatch(rb"(\d+)\s+(\d+)\s+R", raw.strip())
        if ref:
            s, e = obj(int(ref.group(1)))
            return int(data[s:e].strip())
        return int(raw)

    stamp = f"D:{date.replace('-', '')}000000Z".encode()
    iso = f"{date}T00:00:00Z".encode()
    bodies = {}
    for n in sorted(offsets):
        s, e = obj(n)
        k = _ws(data, e)
        value = data[s:e].strip()
        if data.startswith(b"stream", k):
            p = k + 6
            p += 2 if data[p:p + 2] == b"\r\n" else 1
            entries = _entries(value)
            keys = dict(entries)
            stream = data[p:p + length_of(keys[b"/Length"])]
            if not data[_ws(data, p + len(stream)):].startswith(b"endstream"):
                raise Refused(f"subway.pdf: object {n}'s stream length is wrong")
            filters = keys.get(b"/Filter", b"")
            if keys.get(b"/Type") == b"/Metadata" and filters in (b"", b"/FlateDecode"):
                xml = zlib.decompress(stream) if filters else stream
                xml = re.sub(rb"(<xmp:(?:CreateDate|ModifyDate|MetadataDate)>)[^<]*", rb"\g<1>" + iso, xml)
                xml = re.sub(rb"uuid:[0-9a-fA-F-]{36}", b"uuid:" + hashlib.md5(b"rapp1-subway").hexdigest().encode(), xml)
                stream, filters = xml, b""
            if filters == b"/FlateDecode" and b"/DecodeParms" not in keys:
                stream = zlib.compress(zlib.decompress(stream), 9)
            parms = keys.get(b"/DecodeParms")
            if filters.startswith(b"["):
                chain = b"[/ASCIIHexDecode " + filters[1:-1].strip() + b"]"
                parms = b"[null " + parms[1:-1].strip() + b"]" if parms and parms.startswith(b"[") else (
                    b"[null " + parms + b"]" if parms else None)
            elif filters:
                chain = b"[/ASCIIHexDecode " + filters + b"]"
                parms = b"[null " + parms + b"]" if parms else None
            else:
                chain = b"/ASCIIHexDecode"
            hexed = stream.hex().upper().encode()
            hexed = b"\n".join(hexed[j:j + 128] for j in range(0, len(hexed), 128)) + b">"
            kept = [(k2, _ascii_strings(v2)) for k2, v2 in entries if k2 not in (b"/Length", b"/Filter", b"/DecodeParms")]
            kept += [(b"/Filter", chain)] + ([(b"/DecodeParms", parms)] if parms else []) + [(b"/Length", str(len(hexed)).encode())]
            head = b"<<" + b" ".join(k2 + b" " + v2 for k2, v2 in kept) + b">>"
            bodies[n] = head + b"\nstream\n" + hexed + b"\nendstream"
        else:
            value = _ascii_strings(value)
            if value.startswith(b"<<") and re.search(rb"/(CreationDate|ModDate)\b", value):
                entries = [(k2, b"(" + stamp + b")" if k2 in (b"/CreationDate", b"/ModDate") else v2)
                           for k2, v2 in _entries(value)]
                value = b"<<" + b" ".join(k2 + b" " + v2 for k2, v2 in entries) + b">>"
            bodies[n] = value
    out = bytearray(b"%PDF-1.4\n%rapp1-subway 7-bit\n")
    where = {}
    for n in sorted(bodies):
        where[n] = len(out)
        out += f"{n} 0 obj\n".encode() + bodies[n] + b"\nendobj\n"
    size = max(bodies) + 1
    ident = hashlib.md5(bytes(out)).hexdigest().upper().encode()
    xref = bytearray(f"xref\n0 {size}\n".encode() + b"0000000000 65535 f \n")
    for n in range(1, size):
        xref += (f"{where[n]:010d} 00000 n \n" if n in where else "0000000000 00000 f \n").encode()
    tail = [(b"/Size", str(size).encode()), (b"/Root", trailer[b"/Root"])]
    if b"/Info" in trailer:
        tail.append((b"/Info", trailer[b"/Info"]))
    tail.append((b"/ID", b"[<" + ident + b"> <" + ident + b">]"))
    start = len(out)
    out += bytes(xref) + b"trailer\n<<" + b" ".join(k2 + b" " + v2 for k2, v2 in tail) + b">>\n"
    out += f"startxref\n{start}\n%%EOF\n".encode()
    result = bytes(out)
    if any(b > 0x7E or (b < 0x20 and b != 10) for b in result):
        raise Refused("subway.pdf: the rewrite left bytes that are not printable ASCII")
    return result


def chrome():
    mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac.is_file():
        return str(mac)
    return next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)


def version_id(frame):
    """The version folder a pulse lives in: its crawl date and sequence, e.g. 2026-09-25-0."""
    return f"{frame['utc'][:10]}-{frame['seq']}"


def chain(folder):
    """[(version number, folder id, crawl utc)] from the folder's pulse chain, oldest first. Reading only:
    rapp1_portfolio.py verifies every pulse before it is written; this just labels the maps."""
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


def render(folder, version=None, nav=None, prefix="", pdf=False):
    """({name: wrapped text}, L) for one place: subway.svg.md, subway.html.md and, with pdf, subway.pdf.md, served at
    /portfolio/<prefix>subway.*. `version` = {number, utc} labels the legend; `nav` fills the viewer's picker."""
    repos, lines = load(folder)
    L = layout(repos, lines, version)
    drawing, viewer, plain = svg(L), svg(L, interactive=True), svg(L, links=False)
    files = {"subway.svg.md": wrap(f"/portfolio/{prefix}subway.svg", drawing),
             "subway.html.md": wrap(f"/portfolio/{prefix}subway.html", page(L, viewer, nav, prefix))}
    poster_html = poster(L, plain)
    date = (version["utc"][:10] if version else
            max((r["checked"] for r in repos.values() if r["checked"]), default="1970-01-01"))
    if pdf:
        files["subway.pdf.md"] = print_pdf(poster_html, date, f"/portfolio/{prefix}subway.pdf")
    for name, text in files.items():
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise Refused(f"{prefix}{name} is over the Hive's 1 MB limit")
    L["poster_sha256"] = hashlib.sha256(poster_html.encode("utf-8")).hexdigest()
    return files, L


def print_pdf(poster_html, date, permalink):
    exe = chrome()
    if exe is None:
        raise Refused("no Chrome or Chromium found: subway.pdf was not printed")
    with tempfile.TemporaryDirectory() as scratch:
        source, raw = Path(scratch) / "poster.html", Path(scratch) / "subway.chrome.pdf"
        source.write_text(poster_html, encoding="utf-8")
        try:
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={raw}",
                            source.as_uri()], capture_output=True, timeout=240, check=False)
        except subprocess.TimeoutExpired:
            pass
        if not raw.is_file():
            raise Refused("Chrome did not print subway.pdf")
        data = raw.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", data))
    if count != 1:
        raise Refused(f"subway.pdf has {count} pages, not 1")
    text = ascii_pdf(data, date).decode("ascii")
    sha = hashlib.sha256(poster_html.encode("utf-8")).hexdigest()
    wrapped = wrap(permalink, text).replace("layout: null\n", f"layout: null\nprinted_from: {sha}\n", 1)
    if len(wrapped.encode()) > MAX_BYTES:
        raise Refused(f"subway.pdf is {len(wrapped.encode())} bytes as text, over the Hive's 1 MB limit")
    return wrapped


def served(name, text):
    """The exact bytes GitHub Pages serves for a wrapped file."""
    return unwrap(text).encode("ascii" if name.endswith("pdf.md") else "utf-8")


def stable_label(folder):
    versions = chain(folder)
    if not versions:
        return None, None
    n, vid, utc = versions[-1]
    return {"number": n, "utc": utc}, nav_for(versions)


def build(folder, pdf=False):
    """The stable map files, labelled with the folder's latest version (rapp1_portfolio.py's crawl does this too)."""
    folder = Path(folder)
    version, nav = stable_label(folder)
    files, L = render(folder, version, nav, pdf=pdf)
    for name, text in files.items():
        path = folder / name
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8", newline="\n")
    stale = check(folder, quiet=True)
    print(f"subway: {len(L['repos'])} stations on {sum(1 for _ in L['lines'])} lines, {len(L['interchange'])} "
          f"interchanges; {L['width']:.0f} x {L['height']:.0f} px" + (f"; stale: {', '.join(stale)}" if stale else ""))
    return L


def check(folder, quiet=False):
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
            print(f"stale: {name} differs from the portfolio files; run rapp1_subway.py {folder}" +
                  (" --pdf" if name.endswith("pdf.md") else ""))
        if not stale:
            print(f"subway: all 3 stable map files match the portfolio files" +
                  (f" (version {version['number']})" if version else ""))
    return stale


def main(argv):
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
    sys.exit(main(sys.argv[1:]))
`````
{% endraw %}
