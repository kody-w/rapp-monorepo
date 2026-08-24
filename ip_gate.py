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
This is a closed schema: both keys are required, no other keys are allowed,
both values must be arrays of unique, nonblank strings, every regex must
compile, and at least one rule must exist. A malformed policy is rejected as
a whole; valid entries never excuse invalid siblings.
Invalid UTF-8 is still scanned with a byte-preserving decode and is withheld
if no rule matches, because content the gate cannot fully interpret must not
be treated as screened.

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


class GatePolicyInvalid(GateNotConfigured):
    """Raised when configured rules do not satisfy the closed policy schema."""


_MESSAGE = (
    "No gate rules configured, so screening would pass everything through.\n"
    "  Set RAPP_GATE_RULES='{\"content\":[...],\"paths\":[...]}'\n"
    "      (CI: ${{ secrets.GATE_RULES }})\n"
    "  or create an untracked ./.gate-rules with the same JSON.\n"
    "Refusing to aggregate unscreened content (fail closed)."
)

_INVALID_MESSAGE = (
    "Gate rules are configured but invalid. Expected exactly "
    "'content' and 'paths', each an array of unique nonblank strings, "
    "with at least one rule in total. Refusing to aggregate unscreened "
    "content (fail closed)."
)

_cache: dict | None = None


class _MalformedJson(ValueError):
    pass


def _local_rules_file() -> Path | None:
    """Return the local source; kept injectable so proofs never move it."""
    return Path(__file__).resolve().parent / ".gate-rules"


def _reject_duplicate_keys(pairs):
    doc = {}
    for key, value in pairs:
        if key in doc:
            raise _MalformedJson
        doc[key] = value
    return doc


def _reject_non_json_constant(_value):
    raise _MalformedJson


def _invalid() -> None:
    raise GatePolicyInvalid(_INVALID_MESSAGE)


def _read_policy() -> str:
    if "RAPP_GATE_RULES" in os.environ:
        raw = os.environ["RAPP_GATE_RULES"]
        if not raw.strip():
            _invalid()
        return raw

    source = _local_rules_file()
    if source is None:
        raise GateNotConfigured(_MESSAGE)
    try:
        if not source.is_file():
            raise GateNotConfigured(_MESSAGE)
        raw = source.read_text(encoding="utf-8")
    except GateNotConfigured:
        raise
    except (OSError, UnicodeError):
        _invalid()
    if not raw.strip():
        _invalid()
    return raw


def _validate_strings(values, *, regex: bool) -> list:
    if type(values) is not list:
        _invalid()

    validated = []
    seen = set()
    for value in values:
        if type(value) is not str or not value.strip() or value in seen:
            _invalid()
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            _invalid()
        if not regex and "\x00" in value:
            _invalid()
        seen.add(value)
        if regex:
            try:
                value = re.compile(value, re.IGNORECASE)
            except (re.error, OverflowError):
                _invalid()
        validated.append(value)
    return validated


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache

    try:
        doc = json.loads(
            _read_policy(),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except (json.JSONDecodeError, _MalformedJson):
        _invalid()

    if type(doc) is not dict or set(doc) != {"content", "paths"}:
        _invalid()
    content = _validate_strings(doc["content"], regex=True)
    paths = _validate_strings(doc["paths"], regex=False)
    if not content and not paths:
        _invalid()
    _cache = {
        "content": content,
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


def screen_path(rel_path: str) -> tuple[bool, str]:
    """Screen a path without pretending a gitlink OID is file content."""
    rules = _load()
    hit = _path_hit(rel_path, ALWAYS_WITHHOLD_PATHS)
    if hit:
        return False, f"path matches an always-withhold shape ({hit})"
    hit = _path_hit(rel_path, rules["paths"])
    if hit:
        return False, "path matches a configured withhold rule"
    return True, ""


def screen(raw: bytes, rel_path: str) -> tuple[bool, str]:
    """(keep, reason). reason names the RULE, never the matched text."""
    keep, reason = screen_path(rel_path)
    if not keep:
        return keep, reason
    rules = _load()

    try:
        text = raw.decode("utf-8")
        invalid_utf8 = False
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="surrogateescape")
        invalid_utf8 = True

    for pat in ALWAYS_WITHHOLD_CONTENT:
        if re.search(pat, text):
            return False, "contains something shaped like a credential"
    for i, pat in enumerate(rules["content"]):
        if pat.search(text):
            return False, f"matches configured content rule {i + 1}"
    if invalid_utf8:
        return False, "content is not valid UTF-8 and cannot be screened safely"
    return True, ""
