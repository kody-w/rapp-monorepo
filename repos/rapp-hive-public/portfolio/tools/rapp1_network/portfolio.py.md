# `rapp1_network/portfolio.py`

The portfolio room (`<hive>/shared/organism/portfolio/`, published as `portfolio/`): one file per repo (`repos/<repo>.md`), its badge (`badges/<repo>.svg.md`), one file per line (`lines/<line>.md`) and `PORTFOLIO.md`, plus the public README's portfolio bullet. The subway map and the pulses are drawn from these files.

Source: `rapp1_network/portfolio.py` (rapp1-network 0.1.5). SHA-256 of the source below: `8e80519fa73633df6ab1a34698bcd1c56298155a1fa50098fd9c5c489879bba5` (48628 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/portfolio.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The portfolio room (`<hive>/shared/organism/portfolio/`, published as `portfolio/`): one file per repo
(`repos/<repo>.md`), its badge (`badges/<repo>.svg.md`), one file per line (`lines/<line>.md`) and `PORTFOLIO.md`,
plus the public README's portfolio bullet. The subway map and the pulses are drawn from these files.

Everything here is a pure function of its inputs: the records (records.records), the PR records (data/prs.json),
the header exceptions (data/header-exceptions.json) and the version facts. The front matter of a repo file is an
ordered list of (key, value) pairs (`repo_meta`, `repo_lists`), so a later edition can add keys without touching
the rest. Free text from a record (a reason, a finding) is made inert before it reaches a page: no Liquid or
kramdown markers, no raw HTML, no table breaks (none of which occur in version 1's records).
"""
from __future__ import annotations

import re
from collections import Counter
from urllib.parse import quote

import json

from . import lifecycle, util
from .badges import badge_file, badge_file2, label2
from .config import Settings
from .constants import CANON_RAPP1, INSTALLER, OWNER, PAGES, PUBLIC_BLOB, STATUSES
from .headers import apply_header
from .lines import LINE, LINES, TRUNK
from .wrapping import Refused, check_hive_path, check_hive_text

CHECKER_LABEL = f"{OWNER}/rapp-1 rapp_check.py at {CANON_RAPP1[:7]}"
CHECKER_URL = f"https://github.com/{OWNER}/rapp-1/blob/{CANON_RAPP1}/rapp_check.py"
NOT_SWEPT = "the sweep has not run on it yet"
HEADER_WORDS = {"present": "present", "pr-open": "PR open", "merged": "merged, awaiting the next sweep",
                "missing": "not yet added", "no-readme": "no README (skipped)",
                "not-markdown": "README is not markdown (skipped)", "unknown": "unknown until swept",
                "held": "held back"}
LIQUID = re.compile(r"\{(?=[{%:])")  # {{ and {% (Liquid, which Pages runs on every file with front matter), {: {::
# Editions of the portfolio files, as the subway's: a version's files are written by the edition in force when it is
# cut. Edition 1 is exactly version 1's; edition 2 (docs/CHANGES.md, "lifecycle") writes version 2 onwards.
EDITIONS = ((1, 1), (2, 2))  # (the first version number it writes, edition)
EDITION = EDITIONS[-1][1]  # the current edition; it also writes a portfolio that carries no version
NOTICES_MD = "NOTICES.md"  # the notice board, served as NOTICES.html
HOWTO_MD = "lifecycle.md"  # how to deprecate, move or version a repo, served as lifecycle.html


def edition_for(version: dict | None) -> int:
    """The edition that writes a version's portfolio files: the newest one whose first version is at or below it."""
    if not version:
        return EDITION
    number = int(version["number"])
    return max((e for first, e in EDITIONS if first <= number), default=EDITIONS[0][1])


def exceptions(settings: Settings) -> dict[str, str | dict]:
    """data/header-exceptions.json: {repo: reason} for the headers held back on purpose; a value may also be
    {"short": "...", "reason": "..."} (edition 2 shows `held: <short>` in the tables, the reason in the repo file)."""
    value = util.load(settings.data / "header-exceptions.json", {}) or {}
    return value if isinstance(value, dict) else {}


def held_reason(value) -> str:
    """An exception's full reason (a string, or the dict's reason)."""
    if isinstance(value, dict):
        return str(value.get("reason") or value.get("short") or "")
    return str(value)


def held_short(value) -> str | None:
    """An exception's short form for the tables (edition 2), or None."""
    return str(value["short"]) if isinstance(value, dict) and value.get("short") else None


def _one_line(text) -> str:
    text = str(text)
    return " ".join(text.split()) if "\n" in text or "\r" in text else text


def inert(text) -> str:
    """Record text as a page may show it: one line, no Liquid or kramdown markers, no raw HTML."""
    return LIQUID.sub("{ ", _one_line(text)).replace("<", "&lt;")


def cell(text) -> str:
    """Text for a markdown table cell."""
    return inert(text).replace("|", "\\|")


def code(text) -> str:
    """Text as an inline code span, whatever backticks it holds (CommonMark: a longer fence, padded)."""
    text = LIQUID.sub("{ ", _one_line(text))
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    pad = " " if longest or text.startswith(" ") or text.endswith(" ") else ""
    return f"{'`' * (longest + 1)}{pad}{text}{pad}{'`' * (longest + 1)}"


def sentence(text) -> str:
    """Text ending in one full stop."""
    text = inert(text).rstrip()
    return text if text.endswith((".", "!", "?", "…")) else text + "."


def header_state(rec: dict, pr: dict | None, exceptions: dict | None = None) -> str:
    """The network header's state for a repo: a key of HEADER_WORDS."""
    if rec.get("header_present"):
        return "present"
    if rec["repo"] in (exceptions or {}):
        return "held"
    if pr and pr.get("state") == "OPEN":
        return "pr-open"
    if pr and pr.get("state") == "MERGED":
        return "merged"
    if "readme" not in rec:
        return "unknown"
    if not rec["readme"]:
        return "no-readme"
    return "missing" if rec.get("readme_markdown") else "not-markdown"


def front_matter(meta, lists=()) -> list[str]:
    """Front matter lines: `key: value` for each pair, then `key:` and `  - item` for each non-empty list."""
    return ["---", *[f"{key}: {value}" for key, value in meta],
            *[line for key, items in lists if items for line in [f"{key}:", *[f"  - {i}" for i in items]]], "---"]


def repo_meta(rec: dict, pr: dict | None, exceptions: dict | None = None) -> list[tuple[str, object]]:
    """A repo file's scalar front matter, in order (the subway map reads it)."""
    meta = [("repo", f"{OWNER}/{rec['repo']}"), ("family", rec["family"]), ("line", LINE[rec["family"]]["name"]),
            ("wave", rec["wave"]), ("status", rec["status"]), ("verdict", rec.get("verdict", "none")),
            ("evidence_commit", rec.get("evidence_commit", "") or "none"), ("checked", rec.get("checked", "never")),
            ("checker", CHECKER_LABEL), ("experimental_mentions", rec.get("experimental_mentions", "unknown")),
            ("header", header_state(rec, pr, exceptions))]
    if pr and pr.get("url"):
        meta.append(("header_pr", pr["url"]))
    return meta


def repo_lists(rec: dict) -> list[tuple[str, list]]:
    """A repo file's list keys, in order."""
    return [("also_on", rec.get("also_on", [])), ("links_to", rec.get("links_to", []))]


def _status_lines(rec: dict) -> list[str]:
    status = rec["status"]
    if status == "certified":
        meaning = ("every RAPP artifact passes" if rec["verdict"] == "COMPLIANT"
                   else "no RAPP artifacts, found by a complete bounded scan")
        return [f"**Certified:** rapp-1's own checker gave **{inert(rec['verdict'])}** ({meaning}) at the evidence "
                "commit.", ""]
    if status == "not yet":
        return [f"**Not yet:** {sentence(rec.get('reason', ''))}", ""]
    return [f"**Unchecked:** {sentence(rec.get('reason', NOT_SWEPT))}", ""]


def _evidence_lines(rec: dict, pr: dict | None, header: str, exceptions: dict) -> list[str]:
    repo, commit = rec["repo"], rec["evidence_commit"]
    branch = rec.get("default_branch")
    return [f"- Evidence: [`{OWNER}/{repo}` at `{commit[:10]}`](https://github.com/{OWNER}/{repo}/tree/{commit})"
            f" on {f'`{branch}`' if branch else 'the default branch'}, checked {rec['checked']}.",
            f"- Checker: [`rapp_check.py` at `{CANON_RAPP1[:7]}`]({CHECKER_URL}), "
            f"verdict **{inert(rec.get('verdict'))}**"
            + (f", {rec['findings']} finding(s)" if rec.get("findings") else "")
            + (f", {rec['evidence']} passing artifact(s)" if rec.get("evidence") else "")
            + ". The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is "
            f"`{rec.get('raw_sha256', '')}`.",
            f"- \"experimental\" mentions: {rec.get('experimental_mentions')} (whole word, any case, in "
            "tracked text files at the evidence commit; tracked, not a gate).",
            f"- Network header: {HEADER_WORDS[header]}"
            + (f": {inert(held_reason(exceptions[repo])).rstrip('.')}" if header == "held" else "")
            + (f" ({pr['url']})" if pr and pr.get("url") and header in ("pr-open", "merged") else "")
            + (f" in {code(rec['readme'])}" if rec.get("readme") and header == "present" else "") + ".", ""]


def _findings_lines(rec: dict) -> list[str]:
    heads = rec.get("findings_head") or []
    if not heads:
        return []
    lines = [f"## Findings ({rec.get('findings', len(heads))})", ""]
    lines += [f"- {code(f.get('artifact', '?'))} · {inert(f.get('rule', '?'))} · {inert(f.get('detail', '')[:160])}"
              + (f" ({inert(f['status'])})" if f.get("status") else "") for f in heads]
    if rec.get("findings", 0) > len(heads):
        lines.append(f"- … and {rec['findings'] - len(heads)} more in the raw output")
    return lines + [""]


def _links_lines(rec: dict, back) -> list[str]:
    links, kinds = rec.get("links_to", []), rec.get("links_kinds", {})
    if not links and not back:
        return []
    lines = ["## Links", ""]
    if links:
        lines.append(f"Links to {len(links)} portfolio repo(s): " + ", ".join(
            f"[{t}]({quote(t, safe='')}.md) ({', '.join(kinds.get(t, []))})" for t in links) + ".")
    if back:
        lines.append(f"Linked from {len(back)}: " + ", ".join(f"[{t}]({quote(t, safe='')}.md)" for t in back) + ".")
    return lines + ["", "Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin "
                    "files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only "
                    "public repos in this portfolio count.", ""]


def _check_lines(rec: dict) -> list[str]:
    repo, commit = rec["repo"], rec["evidence_commit"]
    itself = repo == "rapp-1" and commit == CANON_RAPP1
    if repo == "rapp-1" and not itself:  # the checked copy and the checker are both rapp-1: two folder names
        return ["## Check it yourself", "", f"Clone `{OWNER}/rapp-1` at `{commit[:10]}` into `rapp-1` and again at "
                f"`{CANON_RAPP1[:7]}` into `rapp-1-checker`, then run `python3 -B rapp-1-checker/rapp_check.py rapp-1 "
                "--json` from the folder that holds both.", ""]
    clone = (f"Clone `{OWNER}/rapp-1` at `{CANON_RAPP1[:7]}`" if itself
             else f"Clone `{OWNER}/{repo}` at `{commit[:10]}` and `{OWNER}/rapp-1` at `{CANON_RAPP1[:7]}`")
    return ["## Check it yourself", "", f"{clone}, then run `python3 -B rapp-1/rapp_check.py {repo} --json` from the "
            f"folder that holds {'it' if itself else 'both'}.", ""]


def repo_body(rec: dict, pr: dict | None, back=(), exceptions: dict | None = None) -> list[str]:
    """A repo file's body lines, after its front matter."""
    exceptions = exceptions or {}
    repo, status, header = rec["repo"], rec["status"], header_state(rec, pr, exceptions)
    lines = [f"# {repo}: {status}", "", f"![RAPP/1: {status}]({PAGES}/badges/{quote(repo, safe='')}.svg)", ""]
    lines += _status_lines(rec)
    if rec.get("evidence_commit"):
        lines += _evidence_lines(rec, pr, header, exceptions)
    lines += _findings_lines(rec)
    others = [LINE[i]["name"] for i in rec.get("also_on", [])]
    lines += [f"On the map: the **{LINE[rec['family']]['name']}** line"
              + (f", and also {', '.join(others)}" if others else "") + f" ([subway map]({PAGES}/subway.html)).", ""]
    lines += _links_lines(rec, back)
    if rec.get("evidence_commit"):
        lines += _check_lines(rec)
    return lines


def repo_file(rec: dict, pr: dict | None, back=(), exceptions: dict | None = None) -> str:
    """`repos/<repo>.md`: the repo's earned status, its evidence, findings, lines and links."""
    return "\n".join(front_matter(repo_meta(rec, pr, exceptions), repo_lists(rec)) + [""]
                     + repo_body(rec, pr, back, exceptions))


def line_meta(line: dict, n: int, members) -> list[tuple[str, object]]:
    return [("line", line["id"]), ("name", line["name"]), ("color", f'"{line["color"]}"'), ("order", n),
            ("stations", len(members)), ("about", f'"{line["about"]}"')]


def line_file(line: dict, n: int, recs: dict) -> str:
    """`lines/<line>.md`: a subway line, its stations and their statuses (the Core line also its trunk)."""
    members = sorted((r for r in recs.values() if r["family"] == line["id"]), key=lambda r: r["repo"].lower())
    meta = front_matter(line_meta(line, n, members))[:-1]
    body = [f"# {line['name']}", "", line["about"], ""]
    if line["id"] == "rapp1-core":
        missing = [repo for repo, _ in TRUNK if repo not in recs]
        if missing:
            raise Refused(f"the Core line's trunk names {', '.join(missing)}, which the portfolio does not hold")
        meta += ["trunk:", *[f"  - {repo} | {layer}" for repo, layer in TRUNK], "terminal: rapp-installer"]
        body += ["The Core line's stations, in layer order (the organism's layers 0 to 5), ending at the Start here "
                 "terminal:", "", "| Station | Layer | Status |", "|---|---|---|"]
        body += [f"| [{repo}](../repos/{quote(repo, safe='')}.md) | {layer} | {cell(recs[repo]['status'])} |"
                 for repo, layer in TRUNK]
        body.append("")
    if members:
        body += ["| Station | Status | Also on |", "|---|---|---|"]
        body += [f"| [{r['repo']}](../repos/{quote(r['repo'], safe='')}.md) | {cell(r['status'])} | "
                 f"{', '.join(LINE[i]['name'] for i in r.get('also_on', []))} |" for r in members]
    return "\n".join(meta + ["---", ""] + body) + "\n"


def _counts(recs, **where) -> Counter:
    return Counter(r["status"] for r in recs.values() if all(r[k] == v for k, v in where.items()))


def _version_lines(version: dict | None) -> list[str]:
    if not version:
        return []
    return [f"**Version {version['number']}**, crawled {version['utc'][:10]} {version['utc'][11:16]} UTC. Every crawl "
            "is one RAPP/1 frame, a `body.pulse` on the network's body stream "
            f"`{version['stream_id']}`. The [timeline]({PAGES}/timeline.html) lists every version with its pulse "
            "hashes and what changed, and each version's maps stay under `versions/`.", ""]


def portfolio_md(recs: dict, prs: dict, exceptions: dict | None = None, version: dict | None = None) -> str:
    """PORTFOLIO.md: the totals by wave and by line, the map, the version, and every repo by wave and line."""
    row = lambda c: " | ".join(str(c.get(s, 0)) for s in STATUSES) + f" | {sum(c.values())}"
    lines = ["# RAPP/1 portfolio", "",
             "Every public RAPP repo, each with an **earned** RAPP/1 status. RAPP/1 is the LTS version for the whole "
             "network: a repo is certified when rapp-1's own checker passes it at a recorded commit.", "",
             "| Wave | certified | not yet | unchecked | total |", "|---|---|---|---|---|",
             f"| 1: the RAPP/1 stack | {row(_counts(recs, wave=1))} |",
             f"| 2: the rest of the RAPP family | {row(_counts(recs, wave=2))} |",
             f"| **all** | {row(_counts(recs))} |", "",
             f"- **certified**: [`rapp_check.py` at `{CANON_RAPP1[:7]}`]({CHECKER_URL}) says COMPLIANT or CLEAN at the "
             "recorded commit.",
             "- **not yet**: drift or unverified; each file says why.",
             "- **unchecked**: the sweep has not run on it yet.", "",
             "Each repo's README carries one marked line: its badge (served from this folder by GitHub Pages, so the "
             f"URL never changes) and a link to [Start here]({INSTALLER}) for anyone without a Brainstem yet. "
             "\"experimental\" mentions are tracked here as a metric; they are not a gate yet.", "",
             "A Hive holds only markdown, so each badge is `badges/<repo>.svg.md`: its front matter tells GitHub Pages "
             f"to serve it as `{PAGES}/badges/<repo>.svg` (image/svg+xml).", "",
             "## The map", "",
             f"**[Subway map]({PAGES}/subway.html)** (zoomable; click a station for its portfolio file and its "
             "repo) · "
             f"[poster PDF]({PAGES}/subway.pdf) · [SVG]({PAGES}/subway.svg)", "",
             "Lines are the families below; stations are repos, filled by status; the RAPP/1 Core line runs in layer "
             "order and ends at `rapp-installer`, the Start here terminal. It is drawn from these files by "
             "`rapp1_subway.py`, and the links between repos come from each file's `links_to`.", "",
             *_version_lines(version),
             "| Line | Stations | certified | not yet | unchecked |", "|---|---|---|---|---|"]
    for line in LINES:
        c = _counts(recs, family=line["id"])
        if sum(c.values()):
            lines.append(f"| [{line['name']}](lines/{line['id']}.md) | {sum(c.values())} | "
                         + " | ".join(str(c.get(s, 0)) for s in STATUSES) + " |")
    lines.append("")
    order = {line["id"]: n for n, line in enumerate(LINES)}
    for wave, title in ((1, "Wave 1: the RAPP/1 stack"), (2, "Wave 2: the rest of the RAPP family")):
        group = sorted((r for r in recs.values() if r["wave"] == wave),
                       key=lambda r: (order[r["family"]], r["repo"].lower()))
        lines += [f"## {title} ({len(group)})", ""]
        for fam in sorted({r["family"] for r in group}, key=order.get):
            members = [r for r in group if r["family"] == fam]
            lines += [f"### {LINE[fam]['name']} ({len(members)})", "",
                      "| Repo | Status | Verdict | Commit | Checked | \"experimental\" | Header |",
                      "|---|---|---|---|---|---|---|"]
            for r in members:
                h = header_state(r, prs.get(r["repo"]), exceptions)
                lines.append(f"| [{r['repo']}](repos/{quote(r['repo'], safe='')}.md) | {cell(r['status'])} | "
                             f"{cell(r.get('verdict', ''))} | {r.get('evidence_commit', '')[:7]} | "
                             f"{cell(r.get('checked', ''))} | {cell(r.get('experimental_mentions', ''))} | "
                             f"{HEADER_WORDS[h]} |")
            lines.append("")
    return "\n".join(lines)


PORTFOLIO_BULLET = ("- `portfolio/`: every public RAPP repo's earned RAPP/1 status, one file per repo in `repos/`, the "
                    "whole table in `PORTFOLIO.md`, the badges each repo's README shows, and the subway map of the "
                    f"network ({PAGES}/subway.html, poster: {PAGES}/subway.pdf). Every crawl is one RAPP/1 "
                    "`body.pulse` frame; each version's maps stay under `versions/`, and the timeline "
                    f"({PAGES}/timeline.html) lists them all. GitHub Pages serves them.")


def public_readme(text: str) -> str:
    """The public copy's README (`shared/organism/README.md`): its own network header, and the `portfolio/` bullet
    (replaced in place, else added after the `canon/` bullet)."""
    new, _ = apply_header(text, "rapp-hive-public")
    if "- `portfolio/`" in new:
        return re.sub(r"- `portfolio/`[^\n]*", lambda _: PORTFOLIO_BULLET, new, count=1)
    return re.sub(r"(- `canon/`[^\n]*\n)", lambda m: m.group(1) + PORTFOLIO_BULLET + "\n", new, count=1)


def linked_from(recs: dict) -> dict[str, list[str]]:
    """{repo: the portfolio repos whose links_to name it}, sorted case-insensitively (as records.linked_from)."""
    back: dict[str, set[str]] = {name: set() for name in recs}
    for name, rec in recs.items():
        for target in rec.get("links_to", []):
            if target in back:
                back[target].add(name)
    return {name: sorted(names, key=str.lower) for name, names in back.items()}


def portfolio_files(recs: dict, prs: dict, exceptions: dict | None, version: dict | None = None, *,
                    left: dict | None = None, previous: dict | None = None, edition: int | None = None) -> dict[str, str]:
    """{path in the portfolio room: text}: repo files, badges, lines and PORTFOLIO.md (the maps are drawn from them);
    from edition 2 also the repo files and badges of the repos that left (`left`, lifecycle.left_repos), the notice
    board NOTICES.md (its changes against `previous`, the head pulse's payload) and the how-to lifecycle.md.
    `version` is {number, utc, stream_id, id}, or None for a portfolio outside the pulse chain; it picks the edition
    (`edition` overrides it). Refused when a path or a text would not fit the Hive."""
    edition = edition_for(version) if edition is None else edition
    back = linked_from(recs)
    if edition < 2:
        want = {f"repos/{r}.md": repo_file(rec, prs.get(r), back[r], exceptions) for r, rec in recs.items()}
        want.update({f"badges/{r}.svg.md": badge_file(r, rec["status"]) for r, rec in recs.items()})
    else:
        left = {name: entry for name, entry in (left or {}).items() if name not in recs}
        want = {f"repos/{r}.md": repo_file2(rec, prs.get(r), back[r], exceptions) for r, rec in recs.items()}
        want.update({f"badges/{r}.svg.md": badge_file2(r, rec["status"], rec.get("lifecycle") or "active",
                                                       rec.get("version")) for r, rec in recs.items()})
        want.update({f"repos/{r}.md": left_file(r, entry) for r, entry in left.items()})
        want.update({f"badges/{r}.svg.md": badge_file2(r, entry["last"]["status"], lifecycle.LEFT,
                                                       entry["last"].get("version")) for r, entry in left.items()})
    used = {rec["family"] for rec in recs.values()}
    want.update({f"lines/{line['id']}.md": line_file(line, n, recs) for n, line in enumerate(LINES, 1)
                 if line["id"] in used})
    if edition < 2:
        want["PORTFOLIO.md"] = portfolio_md(recs, prs, exceptions, version)
    else:
        want["PORTFOLIO.md"] = portfolio_md2(recs, prs, exceptions, version, left)
        want[NOTICES_MD] = notices_md(recs, left, version, previous)
        want[HOWTO_MD] = HOWTO
    for rel_path, text in want.items():
        check_hive_path(rel_path)
        check_hive_text(rel_path, text)
        if edition >= 2 and rel_path in (NOTICES_MD, HOWTO_MD) and LIQUID.search(text):
            raise Refused(f"{rel_path}: holds a Liquid or kramdown marker, which GitHub Pages would run")
    return want


# ---- edition 2: versions, channels, lifecycles and notices -----------------------------------------------------------

LIFE_WORDS = {"deprecated": "Deprecated", "superseded": "Superseded", "archived": "Archived"}
CHANNEL_WORDS = {"rapp1-lts": "it has a long-term-support pin, so the network builds on that commit; its newer commits "
                              "are the newest channel",
                 "newest": "it has no long-term-support pin, so its newest commit is the one in use"}


def successor_link(name: str, prefix: str = "") -> str:
    """A superseded_by value as a link: its portfolio file (a repo in the portfolio), else its GitHub repo."""
    if "/" in name:
        return f"[{inert(name)}](https://github.com/{quote(name, safe='/')})"
    return f"[{inert(name)}]({prefix}{quote(name, safe='')}.md)"


def notice_quote(rec: dict, prefix: str = "") -> list[str]:
    """The notice a non-active repo's file leads with (a quote), e.g. > **Deprecated since 2026-10-01.** <notice>."""
    life = rec.get("lifecycle") or "active"
    if life == "active":
        return []
    since = f" since {rec['since']}" if rec.get("since") else ""
    text = f"> **{LIFE_WORDS[life]}{since}.**"
    if life == "archived":
        text += " The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay."
    if rec.get("notice"):
        text += " " + sentence(rec["notice"])
    if rec.get("superseded_by"):
        text += f" Superseded by {successor_link(rec['superseded_by'], prefix)}."
    return [text, ""]


def _front_value(key: str, value) -> str:
    """A front matter value of edition 2: free text (a version, a label, the notice) is double-quoted with JSON
    escapes (YAML reads them the same), so no YAML reader takes it for a number or a date."""
    return json.dumps(str(value), ensure_ascii=False) if key in ("version", "lts_version", "notice") else str(value)


def repo_meta2(rec: dict, pr: dict | None, exceptions: dict | None = None) -> list[tuple[str, object]]:
    """Edition 2's scalar front matter: edition 1's, then the version, the LTS pin, the channel and the lifecycle
    (each only when present; channel and lifecycle always are)."""
    meta = repo_meta(rec, pr, exceptions)
    extra = {"version": rec.get("version"), "version_source": rec.get("version_source") if rec.get("version") else None,
             "lts_version": rec.get("lts_version"), "lts_commit": rec.get("lts_commit"),
             "lts_source": rec.get("lts_source"), "channel": rec.get("channel") or "newest",
             "lifecycle": rec.get("lifecycle") or "active", "since": rec.get("since"),
             "superseded_by": rec.get("superseded_by"), "notice": rec.get("notice"), "left": rec.get("left"),
             "member_card": "present" if rec.get("member_card") else None}
    return meta + [(key, _front_value(key, value)) for key, value in extra.items() if value]


def version_line(rec: dict) -> list[str]:
    """The Version line: the version and its source, the LTS pin (label and commit link), and the channel."""
    repo, version = rec["repo"], rec.get("version")
    if version:
        text = (f"**Version:** {code(lifecycle.shown_version(version))}, from "
                f"{lifecycle.VERSION_SOURCES.get(rec.get('version_source'), 'the crawl')}.")
    else:
        text = "**Version:** none recorded (no root VERSION file and no GitHub release)."
    if rec.get("lts_commit"):
        commit = rec["lts_commit"]
        text += (f" **LTS:** [{code(rec.get('lts_version') or commit[:7])}](https://github.com/{OWNER}/"
                 f"{quote(repo, safe='')}/tree/{commit}) (commit `{commit[:10]}`, from "
                 f"{lifecycle.PIN_SOURCES.get(rec.get('lts_source'), 'the LTS pins')}).")
    channel = rec.get("channel") or "newest"
    return [text + f" **Channel:** `{channel}`: {CHANNEL_WORDS[channel]}.", ""]


EXPERIMENTAL_WORDS_1 = "(whole word, any case, in tracked text files at the evidence commit; tracked, not a gate)"
EXPERIMENTAL_WORDS_2 = ("(whole word, any case, in tracked text files at the evidence commit, leaving out the network's "
                        "own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, "
                        "`members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate)")


def repo_body2(rec: dict, pr: dict | None, back=(), exceptions: dict | None = None) -> list[str]:
    """Edition 2's body: the notice first (when not active), then edition 1's body with the badge's words as its alt
    text and the Version line after the status."""
    body = repo_body(rec, pr, back, exceptions)
    label = label2(rec["status"], rec.get("lifecycle") or "active", rec.get("version"))
    badge = f"![{label}]({PAGES}/badges/{quote(rec['repo'], safe='')}.svg)"
    at = body.index("") + 1  # after the title and its blank line: the badge, then the status lines
    status_end = at + 2 + len(_status_lines(rec))
    tail = [line.replace(EXPERIMENTAL_WORDS_1, EXPERIMENTAL_WORDS_2, 1) for line in body[status_end:]]
    if rec.get("member_card"):
        at_header = next((k for k, line in enumerate(tail) if line.startswith("- Network header:")), None)
        if at_header is not None:
            tail.insert(at_header + 1, card_line(rec))
    return notice_quote(rec) + body[:at] + [badge, ""] + body[at + 2:status_end] + version_line(rec) + tail


def card_line(rec: dict) -> str:
    """Edition 2: the repo's network card, at its evidence commit, and its pointer in the Hive's public copy."""
    repo, commit = quote(rec["repo"], safe=""), rec["evidence_commit"]
    return (f"- Member card: [`.rapp/member.md`](https://github.com/{OWNER}/{repo}/blob/{commit}/.rapp/member.md) at "
            f"the evidence commit: this repo's card in the RAPP Hive, beside its pointer "
            f"[`members/{inert(rec['repo'])}.md`](https://github.com/{OWNER}/rapp-hive-public/blob/main/members/"
            f"{repo}.md).")


def repo_file2(rec: dict, pr: dict | None, back=(), exceptions: dict | None = None) -> str:
    """`repos/<repo>.md` of edition 2."""
    return "\n".join(front_matter(repo_meta2(rec, pr, exceptions), repo_lists(rec)) + [""]
                     + repo_body2(rec, pr, back, exceptions))


def left_file(repo: str, entry: dict) -> str:
    """`repos/<repo>.md` of a repo that left the network: kept so no link breaks, marked `left: <date>`, with its last
    recorded facts and a short "Left the network" section."""
    last = entry["last"]
    line = last.get("line") if last.get("line") in LINE else "projects"
    commit = last.get("evidence_commit") or ""
    meta = [("repo", f"{OWNER}/{repo}"), ("family", line), ("line", LINE[line]["name"]), ("status", last["status"]),
            ("verdict", last.get("verdict") or "none"), ("evidence_commit", commit or "none")]
    for key in ("version", "lts_version", "channel", "lifecycle", "since", "superseded_by", "notice"):
        if last.get(key):
            meta.append((key, _front_value(key, last[key])))
    meta.append(("left", entry["left"]))
    label = label2(last["status"], lifecycle.LEFT, last.get("version"))
    evidence = (f", verdict **{inert(last.get('verdict'))}** at [`{OWNER}/{repo}` at `{commit[:10]}`]"
                f"(https://github.com/{OWNER}/{quote(repo, safe='')}/tree/{commit})" if commit else "")
    body = [f"> **Left the network on {entry['left']}.** `{OWNER}/{repo}` is no longer a public repo of the RAPP "
            "family on GitHub (deleted, made private, or renamed away), so the crawl no longer checks it. This file "
            "and its badge stay, so no link to them breaks.", "",
            f"# {repo}: left the network", "", f"![{label}]({PAGES}/badges/{quote(repo, safe='')}.svg)", "",
            "## Left the network", "",
            f"- Last recorded in version {entry['last_version']} (crawled {entry['last_crawled']}): "
            f"**{inert(last['status'])}**{evidence}.",
            f"- It is off the [subway map]({PAGES}/subway.html) and out of the totals; the "
            f"[notices page]({PAGES}/NOTICES.html) lists it.",
            "- If it comes back as a public repo of the RAPP family, the next crawl checks it again.", ""]
    if last.get("superseded_by"):
        body[-1:-1] = [f"- Superseded by {successor_link(last['superseded_by'])}."]
    return "\n".join(front_matter(meta) + [""] + body)


def status_cell(rec: dict) -> str:
    """The Status cell of edition 2: the lifecycle first when the repo is not active."""
    life = rec.get("lifecycle") or "active"
    return cell(rec["status"]) if life == "active" else f"**{life}** · {cell(rec['status'])}"


def version_cell(rec: dict) -> str:
    """The Version cell: the version (v1.2.3), and `LTS <label>` when the repo is pinned."""
    parts = [cell(lifecycle.shown_version(rec["version"]))] if rec.get("version") else []
    if rec.get("lts_version"):
        parts.append(f"LTS {cell(rec['lts_version'])}")
    return " · ".join(parts)


HEADER_COUNT_WORDS = (("present", "carry it"), ("pr-open", "in an open pull request"),
                      ("merged", "merged, awaiting the next sweep"), ("held", "held"),
                      ("missing", "waiting for their pull request (wave 2 waits for the owner's approval)"),
                      ("no-readme", "without a README (skipped)"), ("not-markdown", "with a README that is not markdown "
                                                                     "(skipped)"),
                      ("unchecked", "not checked (they could not be cloned)"), ("unknown", "unknown until swept"))


def _header_key(rec: dict, pr: dict | None, exceptions: dict | None) -> str:
    state = header_state(rec, pr, exceptions)
    return "unchecked" if state == "unknown" and rec.get("status") == "unchecked" and rec.get("reason") else state


def header_counts(recs: dict, prs: dict, exceptions: dict | None) -> str:
    """Edition 2: how many READMEs carry the header today and where the rest stand, in words."""
    counts: dict[str, int] = {}
    for r in recs.values():
        key = _header_key(r, prs.get(r["repo"]), exceptions)
        counts[key] = counts.get(key, 0) + 1
    words = [f"{counts[key]} {phrase}" for key, phrase in HEADER_COUNT_WORDS if counts.get(key)]
    return f"today, of {len(recs)}: " + ", ".join(words)


def header_cell(rec: dict, pr: dict | None, exceptions: dict | None) -> str:
    """The Header cell of edition 2: `held: <short>` for a held header with a short form; `none (not checked)` for a
    repo that could not be cloned or checked."""
    state = header_state(rec, pr, exceptions)
    short = held_short((exceptions or {}).get(rec["repo"])) if state == "held" else None
    if short:
        return f"held: {cell(short)}"
    return "none (not checked)" if _header_key(rec, pr, exceptions) == "unchecked" else HEADER_WORDS[state]


def lifecycle_counts(recs: dict, left: dict | None) -> dict[str, int]:
    """{active, deprecated, superseded, archived, left}: the notice board's counts."""
    counts = {life: sum((r.get("lifecycle") or "active") == life for r in recs.values()) for life in lifecycle.LIFECYCLES}
    return {**counts, lifecycle.LEFT: len(left or {})}


def portfolio_md2(recs: dict, prs: dict, exceptions: dict | None = None, version: dict | None = None,
                  left: dict | None = None) -> str:
    """PORTFOLIO.md of edition 2: edition 1's, with the Notices paragraph near the top, the channel legend, the map
    drawn by the package, and a Version column; the Status cell names the lifecycle first when it is not active."""
    text = portfolio_md(recs, prs, exceptions, version)
    counts = lifecycle_counts(recs, left)
    notices = (f"**Notices:** {counts['active']} active, {counts['deprecated']} deprecated, {counts['superseded']} "
               f"superseded, {counts['archived']} archived, {counts['left']} left the network. The "
               f"[notices page]({PAGES}/NOTICES.html) lists every repo that is not active or has left, and what changed "
               f"in this version; [how to deprecate, move or version a repo]({PAGES}/lifecycle.html).")
    intro_end = "recorded commit.\n\n"
    text = text.replace(intro_end, intro_end + notices + "\n\n", 1)
    legend = "- **unchecked**: the sweep has not run on it yet.\n"
    text = text.replace(legend, (
        "- **unchecked**: it could not be cloned or checked (for example, an empty repository); its file says why.\n"
        "- **rapp1-lts**: the repo has a long-term-support pin (the network's built-in known pins, until the estate "
        "publishes its LTS pins; the Version column shows `LTS` and its label); **newest**: no pin, so its newest "
        "commit is the one in use. **deprecated**, **superseded** and **archived** come first in the Status column; "
        "each repo's file says since when and why.\n"), 1)
    text = text.replace("Each repo's README carries one marked line:",
                        f"Each repo's README gets one marked line ({header_counts(recs, prs, exceptions)}):", 1)
    cards = sum(1 for r in recs.values() if r.get("member_card"))
    text = text.replace("A Hive holds only markdown, so each badge is", (
        f"**Member cards:** {cards} of {len(recs)} repos carry their card in the RAPP Hive (`.rapp/member.md`, "
        "the repo's own side of its pointer in `members/`); the file of each repo that has one links it.\n\n"
        "A Hive holds only markdown, so each badge is"), 1)
    text = text.replace("stations are repos, filled by status;", "stations are repos, filled by status (hollow when "
                        "deprecated, superseded or archived);", 1)
    text = text.replace("It is drawn from these files by `rapp1_subway.py`, and the links",
                        f"It is drawn from these files by the `rapp1_network` package (its release copy is in "
                        f"[`tools/`]({PUBLIC_BLOB}/tools)), and the links", 1)
    old_head = "| Repo | Status | Verdict | Commit | Checked | \"experimental\" | Header |\n|---|---|---|---|---|---|---|"
    new_head = ("| Repo | Status | Version | Verdict | Commit | Checked | \"experimental\" | Header |\n"
                "|---|---|---|---|---|---|---|---|")
    text = text.replace(old_head, new_head)
    lines = text.split("\n")
    for n, line in enumerate(lines):
        found = re.match(r"\| \[([^\]]+)\]\(repos/[^)]*\.md\) \| ", line)
        if found and found[1] in recs:
            r = recs[found[1]]
            lines[n] = (f"| [{r['repo']}](repos/{quote(r['repo'], safe='')}.md) | {status_cell(r)} | {version_cell(r)} | "
                        f"{cell(r.get('verdict', ''))} | {r.get('evidence_commit', '')[:7]} | "
                        f"{cell(r.get('checked', ''))} | {cell(r.get('experimental_mentions', ''))} | "
                        f"{header_cell(r, prs.get(r['repo']), exceptions)} |")
    return "\n".join(lines)


def _changes_lines(recs: dict, left: dict, previous: dict | None) -> list[str]:
    if not previous:
        return ["This is the first version: there is nothing before it to compare.", ""]
    cur = {"schema": "rapp1-network-pulse/2", "repos": {name: lifecycle.entry(rec) for name, rec in recs.items()},
           "left": {name: entry["left"] for name, entry in left.items()}}
    diff = lifecycle.changes(previous, cur)
    link = lambda name: f"[{inert(name)}](repos/{quote(name, safe='')}.md)"
    shown = lambda v: code(lifecycle.shown_version(v)) if v else "none"
    lines = []
    for name, before, after, notice in diff["lifecycle"]:
        lines.append(f"- {link(name)}: lifecycle {before} → **{after}**" + (f": {sentence(notice)}" if notice else "."))
    for name, before, after in diff["channel"]:
        lines.append(f"- {link(name)}: channel `{before}` → `{after}`.")
    for name, before, after in diff["version"]:
        lines.append(f"- {link(name)}: version {shown(before)} → {shown(after)}.")
    for name, has in diff.get("cards", []):
        lines.append(f"- {link(name)}: member card " + ("added (`.rapp/member.md`)." if has else "removed."))
    for name in diff["added"]:
        lines.append(f"- {link(name)}: added to the network ({cell(recs[name]['status'])}).")
    for name, date in diff["left"]:
        lines.append(f"- {link(name)}: left the network on {date}.")
    if diff["removed"]:
        lines.append(f"- {diff['removed']} repo(s) removed from the portfolio (held back by the privacy rule).")
    if lifecycle.schema_of(previous) < 2:
        lines.append(f"- Version {previous.get('version')} recorded no versions or channels, so this is the first "
                     "version to record them; every repo counted as active then.")
    return (lines or ["None: no lifecycle, channel, version or member card changed, and no repo was added or left."]
            ) + [""]


def notices_md(recs: dict, left: dict | None, version: dict | None = None, previous: dict | None = None) -> str:
    """NOTICES.md, the notice board (served as NOTICES.html): every repo that is not active and every repo that left,
    with its lifecycle, since, notice and successor; then what changed in this version against the previous pulse;
    and the how-to."""
    left = left or {}
    counts = lifecycle_counts(recs, left)
    order = lambda item: (item[0].lower(), item[0])
    lines = ["# RAPP/1 notices", "",
             "The notice board of the RAPP/1 network: every repo that is **deprecated**, **superseded** or "
             "**archived**, and every repo that **left** the network, with since when and why. Deprecated and "
             "superseded come only from a notice saved in the RAPP Hive by signed save; archived comes only from "
             "GitHub. Every crawl is one RAPP/1 `body.pulse` frame, and each pulse records these lifecycles, so the "
             f"[timeline]({PAGES}/timeline.html) versions every notice.", ""]
    if version:
        lines += [f"**Version {version['number']}**, crawled {version['utc'][:10]} {version['utc'][11:16]} UTC: "
                  f"{counts['active']} active, {counts['deprecated']} deprecated, {counts['superseded']} superseded, "
                  f"{counts['archived']} archived, {counts['left']} left the network.", ""]
    not_active = sorted(((n, r) for n, r in recs.items() if (r.get("lifecycle") or "active") != "active"), key=order)
    lines += [f"## Not active ({len(not_active)})", ""]
    if not_active:
        lines += ["| Repo | Lifecycle | Since | Notice | Successor | Status | Saved in |",
                  "|---|---|---|---|---|---|---|"]
        for name, r in not_active:
            saved = f"`{r['notice_commit'][:10]}`" if r.get("notice_commit") else ("GitHub" if r["lifecycle"] == "archived"
                                                                                 else "")
            lines.append(f"| [{name}](repos/{quote(name, safe='')}.md) | **{r['lifecycle']}** | {r.get('since', '')} | "
                         f"{cell(r.get('notice', ''))} | "
                         f"{successor_link(r['superseded_by'], 'repos/') if r.get('superseded_by') else ''} | "
                         f"{cell(r['status'])} | {saved} |")
        lines += ["", "Saved in: the RAPP Hive commit (a signed save) that last changed the repo's notice file, or GitHub "
                      "for an archived repo."]
    else:
        lines.append("None: every repo in the portfolio is active.")
    lines += ["", f"## Left the network ({len(left)})", ""]
    if left:
        lines += ["| Repo | Left | Last status | Last recorded in |", "|---|---|---|---|"]
        for name, entry in sorted(left.items(), key=order):
            lines.append(f"| [{name}](repos/{quote(name, safe='')}.md) | {entry['left']} | "
                         f"{cell(entry['last']['status'])} | version {entry['last_version']} |")
    else:
        lines.append("None: every repo of the previous version is still in the network (or held back by the "
                     "privacy rule, which removes it).")
    lines += ["", "## Changes in this version", ""]
    lines += _changes_lines(recs, left, previous)
    lines += [f"[How to deprecate, move or version a RAPP/1 repo]({PAGES}/lifecycle.html) · "
              f"[Portfolio]({PAGES}/PORTFOLIO.html) · [Subway map]({PAGES}/subway.html) · "
              f"[Timeline]({PAGES}/timeline.html)", ""]
    return "\n".join(lines)


HOWTO = f"""# How to deprecate, move or version a RAPP/1 repo

Every public RAPP repo of kody-w is a station of the RAPP/1 network. Its portfolio file, its badge, the subway map,
the [notices page]({PAGES}/NOTICES.html) and each crawl's pulse show its version, its channel and its lifecycle. This
page says how to change them, in plain words. A step marked **(owner)** only the owner can do: it needs the owner's
GitHub account or a signed save in the owner's RAPP Hive. Everything else follows from the next crawl.

## Deprecate a repo

1. **(owner)** Save a notice in the RAPP Hive by signed save: the file `shared/organism/notices/<repo>.md`, which
   the public copy serves as `notices/<repo>.md`. The package writes it and asks the Hive for its signed save (the
   same save a crawl uses):

   ```
   python -m rapp1_network notice <repo> --lifecycle deprecated --since 2026-10-01 --notice "Use rapp-example instead; this repo gets no new features."
   ```

   `--dry-run` prints the file and changes nothing, and `python -m rapp1_network notice check` checks every notice
   file in the Hive. By hand, the file is:

   ```
   ---
   repo: kody-w/<repo>
   lifecycle: deprecated
   since: 2026-10-01
   notice: "One line of plain text, 1 to 200 characters."
   ---

   Anything else you want to say, in markdown.
   ```

   The keys come in this order. The notice is one line of plain text in double quotes, without Liquid or kramdown
   markers (a brace followed by another brace, a percent sign or a colon). The folder holds notice files only. A
   notice file that breaks a rule stops the next cut with a message that names the file and the rule, and so does a
   notice for a repo that is not in the portfolio.
2. **(owner)** Say it in the repo's own README too, near the top. The README is the repo's front door and stays
   editable; its network header (the badge and "Start here") stays where it is.
3. The next crawl changes the rest: the badge reads **deprecated** first (then the version, when there is one); the
   repo's portfolio file leads with the notice; PORTFOLIO.md shows it first in the Status column; the subway map
   draws the station hollow; the notices page lists it; and the pulse records the lifecycle, its date and the
   notice, so the [timeline]({PAGES}/timeline.html) lists the change.

To take a notice back: `python -m rapp1_network notice <repo> --clear` (a signed save that removes the file). The
next crawl shows the repo as active again.

## Move a repo

1. **(owner)** Make the successor a new repo with its own network header (its badge and "Start here"), so the crawl
   checks it as a station of its own.
2. **(owner)** Save a `superseded` notice for the old repo that names its successor:

   ```
   python -m rapp1_network notice <old repo> --lifecycle superseded --since 2026-10-01 --superseded-by <new repo> --notice "Moved to <new repo>."
   ```

   The successor is a repo of the portfolio (its name) or any `owner/repo`. While both are on the subway map, a
   dashed arrow runs from the old station to the new one.
3. A new repo and a notice are safer than a GitHub rename. A rename redirects the repo's page, its git URL and its
   raw file links for now, but never its GitHub Pages site, and a repo made later under the old name ends every
   redirect, so raw and Pages links that name the old repo can break. The old repo, left where it is, keeps every
   link working.
4. **(owner)** Archive the old repo on GitHub when you are ready. The crawl then shows it as **archived** (a dashed
   hollow station): an archived repo that was a station stays on the notice board instead of vanishing, and GitHub's
   archived wins over the notice, whose text stays.

A repo that leaves the family (deleted, made private or renamed away) keeps its portfolio file and its badge, which
turns grey and says `left`: it goes off the map and out of the totals, and the notices page lists it. A repo that
the private denylist holds back is removed instead: privacy wins.

## Version a repo

1. **(owner, or anyone who can push to the repo)** Give it a version: a root file named exactly `VERSION` whose first
   line is the version (for example `1.2.3`), or a GitHub release, whose tag is the version. When both exist, the
   VERSION file wins. A version is 1 to 40 letters, digits, dots, underscores, plus and minus signs, starting with a
   letter or a digit; anything else is not shown.
2. The next crawl records it: the badge adds it (`v1.2.3`; a tag such as `v1.0.0` stays as it is), and the repo's
   portfolio file, PORTFOLIO.md and the pulse show it.
3. The LTS pin comes from the estate's LTS pins (a file the crawl is given with `--lts-pins`); until the estate
   publishes them, from the known pins built into the package: rapp-1 at `591e014` (the canon pin every check runs
   at), rapp-installer at `brainstem-v0.6.9`, rapp-work at `29ead23` and rapp-map at `4c8ba6b`. A repo with an LTS
   pin is on the channel **rapp1-lts**; every other repo is on **newest**.
4. **(owner)** A later LTS is a new `release_scope` in the estate's LTS pins, never an edit of a published one: a
   published pin, like a published pulse, never changes.

## What only the owner can do

Save or clear a notice (a signed save in the RAPP Hive), archive or rename a repo on GitHub, and change the estate's
LTS pins. The crawl reads all of them and changes nothing by itself.

[Notices]({PAGES}/NOTICES.html) · [Portfolio]({PAGES}/PORTFOLIO.html) · [Subway map]({PAGES}/subway.html) ·
[Timeline]({PAGES}/timeline.html)
"""
`````
{% endraw %}
