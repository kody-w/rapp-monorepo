"""ip_gate.py — nothing private gets into the public mirror.

This repo aggregates every public RAPP repo into one place. That is useful,
and it is also a second public home for anything that should never have been
in the first one — with its own history, where undoing a mistake is harder.
So every file passes this gate on the way in.

WITHHOLD, DO NOT REDACT. A flagged file is left out entirely and named in the
manifest, rather than rewritten. Two reasons:

  * This mirror's whole promise is "what you have is what upstream has". A
    quietly rewritten file breaks that promise in the one place a reader
    would never think to check.
  * Partial redaction is how sensitive content survives: you fix the sentence
    you thought of and ship the paragraph you did not.

So the rule is simple. If a file trips the gate, it does not travel, and the
manifest says which file and which rule — never the matched text, because a
report that quotes the finding republishes it.

THE RULES ARE INJECTED, NEVER COMMITTED. A committed list of the exact
strings being suppressed is a better search index than the content it
suppresses. Sources, in order:

  1. $RAPP_GATE_RULES  — JSON. In CI: ${{ secrets.GATE_RULES }}.
  2. ./.gate-rules     — JSON, gitignored, local only.

  { "content": ["regex", ...], "paths": ["glob", ...] }

`content` patterns are matched case-insensitively against the file's text.
`paths` are globs matched against the repo-relative path.

If neither source is configured, assert_configured() RAISES and the
aggregation refuses to run. A gate that is not configured screens nothing
while reporting success, which is worse than having no gate: it launders
unscreened content through a step that looks like diligence.

The structural rules below are NOT secret and ship in the open on purpose —
"do not publish a .env" is not information anyone needs protected, and
having it here means a fresh clone is safe before any secret is configured.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
from pathlib import Path

# Always-on structural rules. Public by design: these describe shapes, not
# secrets, and they must apply even when the injected rules are missing.
ALWAYS_WITHHOLD_PATHS = [
    "**/.env", "**/.env.*", "**/*.pem", "**/*.key", "**/*.p12", "**/*.pfx",
    "**/id_rsa", "**/id_dsa", "**/id_ecdsa", "**/id_ed25519",
    "**/.npmrc", "**/.pypirc", "**/.netrc", "**/.git-credentials",
    "**/local.settings.json", "**/secrets.json", "**/credentials.json",
    "**/*.copilot_token", "**/.brainstem_secret",
    "**/.pii-terms", "**/.ip-rules", "**/.gate-rules",
    "**/publication-denylist.json", "**/sensitive/**",
]

# Credential shapes. Kept generic — these match the FORM of a secret, so
# publishing the patterns tells an attacker nothing they did not know.
ALWAYS_WITHHOLD_CONTENT = [
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\bgh[pousr]_[A-Za-z0-9]{30,}",
    r"\bgithub_pat_[A-Za-z0-9_]{50,}",
    r"\bxox[baprs]-[A-Za-z0-9-]{10,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bsk-[A-Za-z0-9]{32,}",
    r"AccountKey=[A-Za-z0-9+/=]{40,}",
]


class GateNotConfigured(RuntimeError):
    """Raised when the injected rules are missing. Never swallow this."""


_MESSAGE = (
    "No gate rules configured, so screening would pass everything through.\n"
    "  Set RAPP_GATE_RULES='{\"content\":[...],\"paths\":[...]}'\n"
    "      (CI: ${{ secrets.GATE_RULES }})\n"
    "  or create an untracked ./.gate-rules with the same JSON.\n"
    "Refusing to aggregate unscreened content (fail closed)."
)

_cache: dict | None = None


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    raw = os.environ.get("RAPP_GATE_RULES", "").strip()
    if not raw:
        f = Path(__file__).resolve().parent / ".gate-rules"
        if f.is_file():
            raw = f.read_text(encoding="utf-8").strip()
    if not raw:
        raise GateNotConfigured(_MESSAGE)
    doc = json.loads(raw)
    content = [c for c in (doc.get("content") or []) if isinstance(c, str) and c.strip()]
    paths = [p for p in (doc.get("paths") or []) if isinstance(p, str) and p.strip()]
    if not content and not paths:
        raise GateNotConfigured(_MESSAGE)
    _cache = {
        "content": [re.compile(c, re.IGNORECASE) for c in content],
        "paths": paths,
        "labels": {i: f"rule-{i + 1}" for i in range(len(content))},
    }
    return _cache


def assert_configured() -> None:
    _load()


def _path_hit(rel: str, globs) -> str | None:
    posix = rel.replace(os.sep, "/")
    for g in globs:
        if fnmatch.fnmatch(posix, g) or fnmatch.fnmatch("/" + posix, g):
            return g
        # `**/x` should also match a bare `x` at the root
        if g.startswith("**/") and fnmatch.fnmatch(posix, g[3:]):
            return g
    return None


def screen(raw: bytes, rel_path: str) -> tuple[bool, str]:
    """(keep, reason). reason names the RULE, never the matched text."""
    rules = _load()

    hit = _path_hit(rel_path, ALWAYS_WITHHOLD_PATHS)
    if hit:
        return False, f"path matches an always-withhold shape ({hit})"
    hit = _path_hit(rel_path, rules["paths"])
    if hit:
        return False, "path matches a configured withhold rule"

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return True, ""          # binary: path rules already had their say

    for pat in ALWAYS_WITHHOLD_CONTENT:
        if re.search(pat, text):
            return False, "contains something shaped like a credential"
    for i, pat in enumerate(rules["content"]):
        if pat.search(text):
            return False, f"matches configured content rule {i + 1}"
    return True, ""
