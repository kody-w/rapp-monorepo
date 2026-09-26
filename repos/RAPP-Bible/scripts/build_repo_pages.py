#!/usr/bin/env python3
"""
Build repos/<name>.md one-pagers and repos/_index.md from the canonical
repo inventory. Uses gh CLI via subprocess (must be authenticated).

Skips private repos (don't link them as if public).
Skips repos without a README.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote

REPO_ROOT = Path(__file__).resolve().parent.parent

# Mirrored from sanitize_pii but evaluated locally to be safe.
from pii_terms import load_patterns  # roster is injected, never committed

# The roster used to be a literal list of real customer names right here,
# in a PUBLIC repo -- the denylist was itself the disclosure. See pii_terms.
PII_PATTERNS = load_patterns()


def sanitize(text: str) -> str:
    out = text
    for pat in PII_PATTERNS:
        out = pat.sub("example-co", out)
    return out


# (name, tier, role)
INVENTORY = [
    # Tier 1
    ("RAPP", 1, "Kernel + organism spec, CONSTITUTION, NEIGHBORHOOD_PROTOCOL"),
    ("RAPP-Network", 1, "Project-anchored twin neighborhoods (drop-in agent.py)"),
    ("RAPP_Store", 1, "Public catalog of rapplications (single-file agents)"),
    ("RAR", 1, "RAPP Agent Registry — browse/vote/share agent.py files"),
    ("RAPP_Sense_Store", 1, "Catalog of senses (per-channel output overlays)"),
    ("rapp-installer", 1, "One-liner install path for the brainstem"),
    ("rapp-mcp", 1, "MCP gateway — serve agents + a brainstem to any MCP host (rapp-mcp-spec/2.0)"),
    # Tier 2
    ("rappterbook", 2, "Social network for AI agents (GitHub-native)"),
    ("twin-egg-hatcher", 2, "Generic single-file hatcher for organism eggs"),
    ("ez-rapp", 2, "Electron desktop wrapper for the brainstem"),
    ("openrappter", 2, "Local-first AI agent powered by GitHub Copilot SDK"),
    ("rapp-leviathan-hub", 2, "Portable .leviathan.egg distribution hub"),
    ("rapp-commons", 2, "Cross-estate signed event stream (global hangout)"),
    ("rapp-estate", 2, "Local-first inventory of a single operator's estate"),
    ("rappter-distro", 2, "Full-bodied Rappter organism distro on top of the kernel"),
    ("rappterverse", 2, "RAPPverse federation hub"),
    ("rappterbox", 2, "Local-first brainstem console for digital organisms"),
    # Tier 3 — front doors, link only
    ("heimdall", 3, "Front door — Heimdall"),
    ("kody-twin", 3, "Front door — Kody Wildfeuer"),
    ("kody-w-twin", 3, "Front door — Kody Wildfeuer (twin v2)"),
    ("echo-brainstem", 3, "Front door — Echo (pattern-synthesizer)"),
    ("lumen-brainstem", 3, "Front door — Lumen (chronicler)"),
    ("tide-brainstem", 3, "Front door — Tide (rhythmic/oceanic voice)"),
]


# Bible-authored text that the generated pages carry. Each page is rebuilt from
# INVENTORY plus live repository data; these blocks are written here, not
# upstream, and are emitted again on every rebuild so that a regeneration never
# drops them (tests/test_mirror_contract.py requires RAR's disposition).
# A note is a blockquote placed right after the "**Tier N**" line.
HAND_KEPT_NOTES = {
    "heimdall": (
        "> **Historical v1.2.0 note.** `heimdall` appeared only as a\n"
        "> `fractal_scales` example, not in that snapshot's `repos` group. The snapshot\n"
        "> is retired and is not current authority; this page remains illustrative."
    ),
    "twin-egg-hatcher": (
        "> **Historical v1.2.0 note.** `twin-egg-hatcher` was not listed in that\n"
        "> snapshot's `repos` map. The snapshot is retired and is not current\n"
        "> authority; this page remains an out-of-catalog historical overview."
    ),
}

# A role replaces the one-line INVENTORY role in "## Role in the ecosystem".
HAND_KEPT_ROLES = {
    "RAR": (
        "RAPP Agent Registry — browse/vote/share agent.py files. It is the home of\n"
        "**`@rapp/rapp`** (`rapp_agent.py`), [the one agent](../THE_ONE_AGENT.md) that\n"
        "makes the entire ecosystem reachable through natural language — and of every\n"
        "specialist agent the one agent `install`s on demand (`@rapp/twin_agent`,\n"
        "`@rapp/egg_hatcher`, and the rest).\n"
        "\n"
        "Historical Bible versions called this “leg one” of the\n"
        "[drift triangle](../DRIFT_TRIANGLE.md). The mirror contract is retired; this\n"
        "page makes no current `action=verify` or spec-alignment claim."
    ),
    "rapp-mcp": (
        "MCP gateway — serve agents + a brainstem to any MCP host (rapp-mcp-spec/2.0).\n"
        "The on-ramp for AIs joining the RAPP ecosystem.\n"
        "\n"
        "- Spec: [SPEC/mcp/SPEC.md](../SPEC/mcp/SPEC.md)\n"
        "- Site: https://kody-w.github.io/rapp-mcp/"
    ),
}

# repos/_index.md is the historical v1.2.0 family index, kept by hand since
# 7c89f12 (2026-08-23). build_index() leaves an index that carries this marker
# alone instead of replacing it with the tier table below.
INDEX_KEEP_MARKER = "<!-- hand-kept: scripts/build_repo_pages.py does not rewrite this file -->"
NETWORK_HEADER_START = "<!-- rapp1:network-header:start -->"
NETWORK_HEADER_END = "<!-- rapp1:network-header:end -->"


def gh_repo(name: str) -> dict | None:
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/kody-w/{name}"],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def gh_readme(name: str) -> str | None:
    """Fetch README via raw URL (works for any default branch)."""
    import urllib.request
    for branch in ("main", "master"):
        url = f"https://raw.githubusercontent.com/kody-w/{name}/{branch}/README.md"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rapp-bible/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8", errors="replace")
        except Exception:
            continue
    return None


def _absolute_readme_url(target: str, repo: str, branch: str, image: bool = False) -> str:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        return target
    if target.startswith("#"):
        return f"https://github.com/kody-w/{repo}{target}"
    path, sep, fragment = target.partition("#")
    while path.startswith("./"):
        path = path[2:]
    while path.startswith("/"):
        path = path[1:]
    if not path:
        path = "README.md"
    quoted = "/".join(quote(unquote(part)) for part in path.split("/"))
    if image:
        base = f"https://raw.githubusercontent.com/kody-w/{repo}/{branch}/{quoted}"
    else:
        base = f"https://github.com/kody-w/{repo}/blob/{branch}/{quoted}"
    return base + (sep + fragment if sep else "")


def absolutize_readme_links(text: str, repo: str | None, branch: str = "main") -> str:
    if not repo:
        return text

    def linked_image_repl(match: re.Match) -> str:
        label, image_target, link_target = match.groups()
        image_url = _absolute_readme_url(image_target, repo, branch, image=True)
        link_url = _absolute_readme_url(link_target, repo, branch, image=False)
        return f"[![{label}]({image_url})]({link_url})"

    text = re.sub(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)", linked_image_repl, text)

    def image_repl(match: re.Match) -> str:
        label, target = match.groups()
        return f"![{label}]({_absolute_readme_url(target, repo, branch, image=True)})"

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)

    def repl(match: re.Match) -> str:
        label, target = match.groups()
        return f"[{label}]({_absolute_readme_url(target, repo, branch, image=False)})"

    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", repl, text)


def _candidate_text(lines: list[str], blockquote: bool = False) -> str:
    if blockquote:
        lines = [re.sub(r"^>\s?", "", ln.strip()) for ln in lines]
    return " ".join(ln.strip() for ln in lines if ln.strip())


def _markdown_only_or_navigation(text: str) -> bool:
    if _file_pointer_notice(text):
        return True
    without_links = re.sub(r"\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)", "", text)
    without_links = re.sub(r"!?\[[^\]]*\]\([^)]+\)", "", without_links)
    without_html = re.sub(r"<!--.*?-->", "", without_links)
    without_html = re.sub(r"<[^>]+>", "", without_html)
    without_markup = re.sub(r"[*_`~#>|·•\-\s.,:;!?/\\()\[\]{}]+", "", without_html)
    return not re.search(r"[A-Za-z0-9]", without_markup)


def _file_pointer_notice(text: str) -> bool:
    links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)
    file_links = [
        target
        for target in links
        if re.search(r"\.(?:json|md|txt)(?:#.*)?$", target, re.I)
    ]
    if len(file_links) < 2:
        return False
    outside = re.sub(r"\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)", "", text)
    outside = re.sub(r"!?\[[^\]]*\]\([^)]+\)", "", outside)
    words = re.findall(r"[A-Za-z0-9]+", outside)
    has_pointer_word = re.search(
        r"\b(?:authority|inventory|ledger|migration|pin|provenance|status)\b",
        outside,
        re.I,
    )
    return bool(has_pointer_word) and len(words) <= 14


def _html_only(text: str) -> bool:
    if all(ln.strip().startswith("<") and ln.strip().endswith(">") for ln in text.splitlines() if ln.strip()):
        return True
    stripped = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    stripped = re.sub(r"<[^>]+>", "", stripped).strip()
    return not stripped


def _descriptive_candidate(lines: list[str]) -> tuple[str, str] | None:
    if not lines:
        return None
    blockquote = all(ln.strip().startswith(">") for ln in lines)
    text = _candidate_text(lines, blockquote=blockquote)
    if not text:
        return None
    if _html_only(text) or _markdown_only_or_navigation(text):
        return None
    if all(re.match(r"^\s*(?:[-*+]\s+|\|)", ln) for ln in lines):
        return None
    return ("quote" if blockquote else "plain", text)


def first_paragraph(
    md: str,
    max_chars: int = 600,
    repo: str | None = None,
    branch: str = "main",
) -> str:
    """Extract the first descriptive README paragraph."""
    if not md:
        return ""
    lines = md.splitlines()
    paragraph: list[str] = []
    quote_fallback: str | None = None
    in_network_header = False
    in_code = False

    def flush():
        nonlocal paragraph, quote_fallback
        candidate = _descriptive_candidate(paragraph)
        paragraph = []
        if candidate is None:
            return None
        kind, text = candidate
        if kind == "plain":
            return text
        if quote_fallback is None:
            quote_fallback = text
        return None

    for ln in lines:
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s == NETWORK_HEADER_START:
            in_network_header = True
            paragraph = []
            continue
        if in_network_header:
            if s == NETWORK_HEADER_END:
                in_network_header = False
            continue
        if not s:
            winner = flush()
            if winner:
                return absolutize_readme_links(winner, repo, branch)[:max_chars]
            continue
        if s.startswith("#"):
            if paragraph or quote_fallback:
                break
            continue
        if s.startswith("<!--") and s.endswith("-->"):
            continue
        if s.startswith("!["):
            continue
        paragraph.append(s)

    winner = flush() or quote_fallback or ""
    return absolutize_readme_links(winner, repo, branch)[:max_chars]


def build_one(name: str, tier: int, role: str) -> tuple[bool, str]:
    meta = gh_repo(name)
    if meta is None:
        return False, f"could not fetch metadata for {name}"
    if meta.get("private"):
        return False, f"skipped (private): {name}"

    readme = gh_readme(name)
    branch = meta.get("default_branch", "main")
    summary = sanitize(first_paragraph(readme, repo=name, branch=branch)) if readme else ""
    desc = sanitize(meta.get("description") or "")

    body = []
    body.append(f"# {name}")
    body.append("")
    body.append(f"**Tier {tier}** — {role}")
    body.append("")
    if name in HAND_KEPT_NOTES:
        body.extend(HAND_KEPT_NOTES[name].split("\n"))
        body.append("")
    body.append(f"- Canonical: https://github.com/kody-w/{name}")
    homepage = meta.get("homepage")
    if homepage:
        body.append(f"- Site: {homepage}")
    body.append(f"- Default branch: `{branch}`")
    body.append(f"- Last updated: {meta.get('updated_at', 'unknown')}")
    body.append(f"- License: {(meta.get('license') or {}).get('spdx_id') or 'unspecified'}")
    body.append("")
    body.append("## Description")
    body.append("")
    body.append(desc if desc else "_No description set upstream._")
    body.append("")
    if summary:
        body.append("## Summary (from upstream README)")
        body.append("")
        body.append(summary)
        body.append("")
    body.append("## Role in the ecosystem")
    body.append("")
    body.extend(HAND_KEPT_ROLES.get(name, role).split("\n"))
    body.append("")
    body.append("---")
    body.append("")
    body.append("_This page is generated by `scripts/build_repo_pages.py`. ")
    body.append("Upstream README is the source of truth — edit there, not here._")
    body.append("")

    dest = REPO_ROOT / "repos" / f"{name}.md"
    dest.write_text("\n".join(body), encoding="utf-8")
    return True, str(dest.relative_to(REPO_ROOT))


def build_index(results: list[tuple[str, int, str, bool, str]]) -> None:
    dest = REPO_ROOT / "repos" / "_index.md"
    if dest.exists() and INDEX_KEEP_MARKER in dest.read_text(encoding="utf-8"):
        print("  KEEP: repos/_index.md (hand-kept)")
        return
    by_tier: dict[int, list[tuple[str, str]]] = {1: [], 2: [], 3: []}
    skipped: list[tuple[str, str]] = []
    for name, tier, role, ok, msg in results:
        if ok:
            by_tier[tier].append((name, role))
        else:
            skipped.append((name, msg))

    tier_labels = {
        1: "Tier 1 — Core specs and kernel",
        2: "Tier 2 — Distribution and ecosystem",
        3: "Tier 3 — Front doors (link only)",
    }

    lines = [
        "# Repos Index",
        "",
        "Every RAPP-ecosystem repo the Bible knows about, grouped by tier.",
        "Each entry links to the Bible one-pager (which in turn links upstream).",
        "",
    ]
    for tier in (1, 2, 3):
        lines.append(f"## {tier_labels[tier]}")
        lines.append("")
        lines.append("| Repo | Role |")
        lines.append("|------|------|")
        for name, role in sorted(by_tier[tier]):
            lines.append(f"| [{name}]({name}.md) | {role} |")
        lines.append("")

    if skipped:
        lines.append("## Skipped")
        lines.append("")
        lines.append("| Repo | Reason |")
        lines.append("|------|--------|")
        for name, msg in sorted(skipped):
            lines.append(f"| {name} | {msg} |")
        lines.append("")

    (REPO_ROOT / "repos" / "_index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results: list[tuple[str, int, str, bool, str]] = []
    for name, tier, role in INVENTORY:
        ok, msg = build_one(name, tier, role)
        print(f"  {'OK' if ok else 'SKIP'}: {name} — {msg}")
        results.append((name, tier, role, ok, msg))
    build_index(results)
    print(f"\nBuilt {sum(1 for r in results if r[3])} repo pages, skipped {sum(1 for r in results if not r[3])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
