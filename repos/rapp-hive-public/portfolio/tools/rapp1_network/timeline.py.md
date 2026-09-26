# `rapp1_network/timeline.py`

The timeline: every pulse of the network's body stream, newest first, with its hashes, totals, files and what changed since the pulse before it. One static page (no script, a strict CSP whose one style is pinned by hash), served by GitHub Pages as portfolio/timeline.html from the Hive's timeline.html.md.

Source: `rapp1_network/timeline.py` (rapp1-network 0.1.5). SHA-256 of the source below: `3155b45d96a6dc06e0deba84857560768579c5405df106ab0a3f8c7d1e81340b` (15078 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/timeline.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The timeline: every pulse of the network's body stream, newest first, with its hashes, totals, files and what changed
since the pulse before it. One static page (no script, a strict CSP whose one style is pinned by hash), served by
GitHub Pages as portfolio/timeline.html from the Hive's timeline.html.md."""
from __future__ import annotations

import base64
import hashlib
import html
import json
from typing import Mapping, Sequence

from .constants import CANON_RAPP1, INDEX_NAME, INSTALLER, OWNER, PAGES, PORTFOLIO, PUBLIC_BLOB
from .lifecycle import schema_of, shown_version
from .pulses import pulse_changes, pulse_diff
from .wrapping import Refused, wrap

TIMELINE_CSS = """body{margin:0;background:#f6f8fa;color:#1b1f24;font:16px/1.5 Helvetica,Arial,sans-serif}
header{background:#fff;border-bottom:1px solid #d0d7de;padding:14px 24px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
header h1{font-size:22px;margin:0;flex:1}
a{color:#0969da;text-decoration:none}
main{max-width:1040px;margin:0 auto;padding:20px 24px 60px}
section,article{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:16px 20px;margin:0 0 16px}
h2{font-size:19px;margin:0 0 8px}
h3{font-size:18px;margin:0 0 6px}
code,pre{font:13px/1.45 Menlo,Consolas,monospace;overflow-wrap:anywhere}
pre{white-space:pre-wrap;background:#f6f8fa;border-radius:6px;padding:10px 12px;margin:8px 0}
dl{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:8px 0}
dt{font-weight:700;color:#57606a}
dd{margin:0}
.totals span{display:inline-block;margin-right:14px}
.c{color:#1a7f37;font-weight:700}.n{color:#9a6700;font-weight:700}.u{color:#57606a;font-weight:700}
.seq{color:#57606a;font-weight:400;font-size:15px}
.note{border-left:5px solid #dfb317}
ul{margin:4px 0 8px 20px;padding:0}
footer{color:#57606a;font-size:13px;margin-top:24px}"""

VERSION_1_TOOL = "rapp1_portfolio.py"  # version 1's generator names the two legacy tools; this one drew its timeline
TIMELINE_TOOL = "rapp1_network/timeline.py"  # a package release's generator names every file of its copy


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def csp() -> str:
    """No source at all but the one style block, pinned by its SHA-256."""
    digest = base64.b64encode(hashlib.sha256(TIMELINE_CSS.encode()).digest()).decode()
    return f"default-src 'none'; style-src 'sha256-{digest}'; base-uri 'none'; form-action 'none'"


def genesis_entry(sid: str, genesis: Mapping) -> dict:
    """The §13.3 genesis registry entry for the stream's creation genesis, which the estate owner records."""
    return {"type": "genesis", "stream_id": sid, "frame_hash": genesis["frame_hash"], "deprecated": False}


def generator_note(generator: Mapping) -> str:
    """The footer: which tool drew the page and its SHA-256, from the head pulse's generator (both shapes)."""
    tools = f'<a href="{PUBLIC_BLOB}/tools">portfolio/tools</a>'
    if VERSION_1_TOOL in generator:
        return (f'Generated from the pulse frames by {VERSION_1_TOOL} (source in {tools}, SHA-256 '
                f'<code>{esc(generator[VERSION_1_TOOL])}</code>).')
    drew = TIMELINE_TOOL if TIMELINE_TOOL in generator else next(
        (path for path in sorted(generator) if path.rsplit("/", 1)[-1] == "timeline.py"), None)
    files = f"{len(generator)} file(s)"
    if drew is None:
        return f"Generated from the pulse frames by the {files} its generator names (source in {tools})."
    return (f'Generated from the pulse frames by {esc(drew)} (source in {tools}, SHA-256 <code>{esc(generator[drew])}'
            f"</code>; the head pulse's generator names all {files} of that release).")


def _totals(payload: Mapping) -> str:
    t = payload["totals"]
    return (f'<p class="totals"><span>{t["stations"]} stations</span><span class="c">{t["certified"]} certified'
            f'</span><span class="n">{t["not yet"]} not yet</span><span class="u">{t["unchecked"]} unchecked</span></p>')


def _when(utc: str) -> str:
    return f"{utc[:10]} {utc[11:16]} UTC"


def timeline_html(sid: str, record: Mapping, frames: Sequence, public: bool, facts: Mapping) -> str:
    """Every pulse, newest first: its hashes, totals, files, and what changed since the pulse before it.

    `frames` is the verified chain [(frame, vid)] (pulses.read_chain plus the new pulse); `public` whether the pulses
    are published beside their maps (pulses.placement); `facts` = {chain: pulses.check_chain(..), conformance: the
    summary line of rapp-1's conformance.py, published: {vid: the public copy's commit that first carried that
    pulse}, certify: pulses.certify_public(..)}."""
    if not frames:
        raise Refused("a timeline needs at least one pulse")
    for key in ("chain", "conformance", "published", "certify"):
        if key not in facts:
            raise Refused(f"the timeline facts need {key!r}")
    genesis, head = frames[0][0], frames[-1][0]
    public_copy = f'<a href="https://github.com/{OWNER}/rapp-hive-public">kody-w/rapp-hive-public</a>'
    identity = (f'<a href="{PAGES}/rappid.json">rappid.json</a> · <a href="{PAGES}/{INDEX_NAME}">frame index</a>'
                if public else "its rappid.json and frame index wait in the private RAPP Hive with the pulses")
    if len(frames) >= 3:  # from version 3: say whose signature it is (GitHub cannot check a Hive's key)
        attribution = (f"published it in a commit of {public_copy} signed by the RAPP Hive's own key (only the Hive "
                       "can check that signature; GitHub shows these commits as unverified)" if public else
                       f"{public_copy} publishes this page and the maps in commits signed by the RAPP Hive's own key, "
                       "not the pulses")
    else:
        attribution = (f"published it in a signed commit of {public_copy}" if public else
                       f"{public_copy} publishes this page and the maps in signed commits, not the pulses")
    where = (f"in public. Every pulse is served as JSON beside its maps, and rapp_check.py still certifies this public copy: "
             f"{facts['certify']['files']['verdict']} on its files as they are (the Hive holds only markdown) and "
             f"{facts['certify']['served']['verdict']} on the files as GitHub Pages serves them, where each unsigned pulse "
             f"passes the §7 envelope, hash and chain checks (a body stream permits sig null)."
             if public else
             "in the private RAPP Hive. rapp_check.py would not certify this public copy with the unsigned pulses in it, so the frames "
             "stay in the private RAPP Hive until the estate owner authorizes a signer. This page and the version "
             "folders are public; each pulse's hashes are listed here so it can be matched when it is published.")
    parts = [f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
             f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
             f'<meta http-equiv="Content-Security-Policy" content="{csp()}">\n<meta name="referrer" content="no-referrer">\n'
             f'<title>RAPP/1 network: timeline of {len(frames)} version(s)</title>\n<style>{TIMELINE_CSS}</style>\n'
             f'</head>\n<body>\n<header><h1>RAPP/1 network · timeline</h1><a href="{PAGES}/subway.html">Latest map</a>'
             f'<a href="{PUBLIC_BLOB}/PORTFOLIO.md">Portfolio</a>'
             + (f'<a href="{PAGES}/NOTICES.html">Notices</a>' if schema_of(head["payload"]) >= 2 else "")
             + f'<a href="{INSTALLER}">Start here</a></header>\n<main>\n',
             '<section>\n<h2>One RAPP/1 frame per crawl</h2>\n'
             '<p>Each crawl of the RAPP/1 network is one pulse of its life: a RAPP/1 frame of the registered kind '
             '<code>body.pulse</code> on the network\'s body stream, chained to the pulse before it. Its payload holds '
             'the crawl time, the checker pin, the totals per status and per line, every repo\'s status, verdict and '
             'evidence commit, a digest of the links between repos, and the content hashes of that version\'s '
             '<code>PORTFOLIO.md</code> and maps.</p>\n<dl>\n'
             f'<dt>Stream</dt><dd><code>{esc(sid)}</code><br>Keyless, minted once ({esc(record.get("minted_utc", ""))}); '
             f'{identity}</dd>\n'
             f'<dt>Genesis</dt><dd>payload_hash <code>{genesis["payload_hash"]}</code><br>frame_hash '
             f'<code>{genesis["frame_hash"]}</code></dd>\n'
             f'<dt>Head</dt><dd>version {head["payload"]["version"]} (seq {head["seq"]}), payload_hash '
             f'<code>{head["payload_hash"]}</code></dd>\n'
             f'<dt>Checked</dt><dd>Every pulse passes RAPP/1 §7.5 steps 1–5 with the reference <code>rapp.py</code>, and '
             f'rapp-1\'s own <code>rapp_check.py</code> at <code>{CANON_RAPP1[:7]}</code> gives the chain '
             f'{facts["chain"]["verdict"]} ({facts["chain"]["frames"]} frame(s) passing, no findings). The reference '
             f'implementation passes rapp-1\'s <code>conformance.py</code> ({esc(facts["conformance"])}).</dd>\n'
             f'</dl>\n</section>\n',
             '<section class="note">\n<h2>Signing and anchoring</h2>\n'
             '<p>The pulses are unsigned (<code>sig: null</code>), which RAPP/1 §10 allows on a body stream. Their hashes '
             'prove integrity and order, not authorship: do not infer who wrote a pulse from the frame. Attribution comes '
             f'from the RAPP Hive, which committed each pulse in a signed save and {attribution}. Anchoring comes later: '
             'the estate owner authorizes a signer (phase 4), and records this stream\'s creation genesis in the '
             'estate\'s signed registry (§13.3), with this entry:</p>\n'
             f'<pre>{esc(json.dumps(genesis_entry(sid, genesis), separators=(", ", ": ")))}</pre>\n'
             f'<p>Where the pulses live: {esc(where)}</p>\n</section>\n',
             f'<h2>Versions ({len(frames)})</h2>\n']
    for k in range(len(frames) - 1, -1, -1):
        frame, vid = frames[k]
        payload, base = frame["payload"], f"{PAGES}/versions/{vid}"
        commit = facts["published"].get(vid)
        shipped = (f' · first published in <a href="https://github.com/{OWNER}/rapp-hive-public/commit/{commit}">'
                   f'{commit[:7]}</a>' if commit else " · published with this page")
        files = (f'<a href="{base}/subway.html">map</a> · <a href="{base}/subway.pdf">poster</a> · '
                 f'<a href="{base}/subway.svg">SVG</a> · <a href="{base}/pulse.json">pulse</a>' if public else
                 f'<a href="{base}/subway.html">map</a> · <a href="{base}/subway.pdf">poster</a> · '
                 f'<a href="{base}/subway.svg">SVG</a> · pulse kept private')
        parts.append(f'<article>\n<h3>Version {payload["version"]} · {_when(payload["crawl"]["finished_utc"])} '
                     f'<span class="seq">seq {frame["seq"]}</span></h3>\n{_totals(payload)}\n'
                     f'<p>payload_hash <code>{frame["payload_hash"]}</code><br>frame_hash <code>{frame["frame_hash"]}'
                     f'</code><br>prev <code>{frame["prev"] or "null"}</code></p>\n<p>{files}{shipped}</p>\n')
        if k == 0:
            parts.append(f'<p>Genesis: the first pulse, {payload["totals"]["stations"]} repos. Nothing before it to '
                         f'compare.</p>\n')
        elif schema_of(payload) >= 2:
            parts.append(_changes_2(frames[k - 1][0], frame))
        else:
            changes, new, removed, moved = pulse_diff(frames[k - 1][0], frame)
            parts.append(f'<p><b>Since version {frames[k - 1][0]["payload"]["version"]}:</b> {len(changes)} status '
                         f'change(s), {len(new)} new repo(s), {len(removed)} removed, {moved} repo(s) at a new commit.</p>\n')
            if changes:
                parts.append("<ul>" + "".join(f"<li>{esc(n)}: {esc(a)} → {esc(b)}</li>" for n, a, b in changes)
                             + "</ul>\n")
            if new:
                parts.append("<p>New: " + ", ".join(f"{esc(n)} ({esc(payload['repos'][n]['status'])})" for n in new)
                             + "</p>\n")
            if removed:
                parts.append("<p>Removed: " + ", ".join(esc(n) for n in removed) + "</p>\n")
        parts.append("</article>\n")
    parts.append(f'<footer>{generator_note(head["payload"]["generator"])}</footer>\n</main>\n</body>\n</html>\n')
    return "".join(parts)


def _changes_2(before: Mapping, frame: Mapping) -> str:
    """What changed since the pulse before, for a /2 pulse: the status line as for /1 (a repo that went without
    leaving was held back by the privacy rule, so it is counted, never named), then lifecycle changes with their
    notices, version and channel changes, and the repos that left."""
    diff, payload = pulse_changes(before, frame), frame["payload"]
    since = before["payload"]["version"]
    out = [f'<p><b>Since version {since}:</b> {len(diff["status"])} status change(s), {len(diff["added"])} new '
           f'repo(s), {diff["removed"]} removed, {diff["moved"]} repo(s) at a new commit.</p>\n']
    if diff["status"]:
        out.append("<ul>" + "".join(f"<li>{esc(n)}: {esc(a)} → {esc(b)}</li>" for n, a, b in diff["status"]) + "</ul>\n")
    if diff["added"]:
        out.append("<p>New: " + ", ".join(f"{esc(n)} ({esc(payload['repos'][n]['status'])})" for n in diff["added"])
                   + "</p>\n")
    cards = len(diff.get("cards", []))
    out.append(f'<p>{len(diff["lifecycle"])} lifecycle change(s), {len(diff["version"])} version change(s), '
               f'{len(diff["channel"])} channel change(s), '
               + (f'{cards} member card change(s), ' if cards else '')
               + f'{len(diff["left"])} repo(s) left the network.'
               + (f" Version {since} recorded no versions or channels, so none are compared." if
                  schema_of(before["payload"]) < 2 else "") + "</p>\n")
    items = [f"<li>{esc(n)}: {esc(a)} → <b>{esc(b)}</b>" + (f": {esc(notice)}" if notice else "") + "</li>"
             for n, a, b, notice in diff["lifecycle"]]
    shown = lambda v: esc(shown_version(v)) if v else "none"
    items += [f"<li>{esc(n)}: version {shown(a)} → {shown(b)}</li>" for n, a, b in diff["version"]]
    items += [f"<li>{esc(n)}: channel {esc(a)} → {esc(b)}</li>" for n, a, b in diff["channel"]]
    items += [f"<li>{esc(n)}: left the network on {esc(date)}</li>" for n, date in diff["left"]]
    items += [f"<li>{esc(n)}: member card {'added' if has else 'removed'}</li>" for n, has in diff.get("cards", [])]
    if items:
        out.append("<ul>" + "".join(items) + "</ul>\n")
    return "".join(out)


def timeline_file(sid: str, record: Mapping, frames: Sequence, public: bool, facts: Mapping) -> str:
    """timeline.html.md: the page in its Hive wrapper, served at /portfolio/timeline.html."""
    return wrap(f"/{PORTFOLIO}/timeline.html", timeline_html(sid, record, frames, public, facts))
`````
{% endraw %}
