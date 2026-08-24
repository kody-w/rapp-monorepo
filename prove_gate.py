#!/usr/bin/env python3
"""prove_gate.py — the gate withholds what it must, keeps what it should,
and never quotes what it found.

A guard nobody has watched fail is indistinguishable from a guard that
cannot fail. This mirror is public and it copies ~190 repositories on a
schedule, so the gate is the only thing standing between an upstream mistake
and a second public home for it. Every property it claims is exercised here.

The three that matter most, and why:

  * FAIL CLOSED. An unconfigured gate screens nothing while returning
    success — worse than no gate, because it launders unscreened content
    through a step that looks like diligence.
  * NAME THE RULE, NOT THE MATCH. A report that quotes its finding
    republishes it. Every reason string is checked against the secret it
    was triggered by.
  * REFUSE ITS OWN RULES. The rules file is the one document whose
    publication would be worse than the leak it prevents, and this mirror
    copies files for a living.

Run: python3 prove_gate.py   (exit 0 only when every scenario behaves)
"""

import importlib
import json
import os
import stat
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

FAILURES = []


def scenario(name, cond, observed):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}\n        {observed}")
    if not cond:
        FAILURES.append(name)


def fresh_gate(rules=None, *, raw_rules=None):
    """Re-import the module so its rule cache is rebuilt per scenario."""
    os.environ.pop("RAPP_GATE_RULES", None)
    if raw_rules is not None:
        os.environ["RAPP_GATE_RULES"] = raw_rules
    elif rules is not None:
        os.environ["RAPP_GATE_RULES"] = json.dumps(rules)
    if "ip_gate" in sys.modules:
        del sys.modules["ip_gate"]
    return importlib.import_module("ip_gate")


def snapshot(path):
    """Capture the properties the proof must never change."""
    try:
        metadata = path.stat()
        payload = path.read_bytes()
    except FileNotFoundError:
        return None
    return (
        payload,
        stat.S_IMODE(metadata.st_mode),
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_dev,
        metadata.st_ino,
    )


def invalid_policy_scenario(name, rules=None, *, raw_rules=None):
    gate = fresh_gate(rules, raw_rules=raw_rules)
    try:
        gate.assert_configured()
    except gate.GatePolicyInvalid as error:
        scenario(name, True, type(error).__name__)
    except Exception as error:
        scenario(name, False, f"unexpected {type(error).__name__}")
    else:
        scenario(name, False, "invalid policy was accepted")


SECRET = "SUPER-SECRET-MATTER-9931"
LOCAL_RULES = Path(__file__).resolve().parent / ".gate-rules"
LOCAL_RULES_BEFORE = snapshot(LOCAL_RULES)

# ── fail closed ─────────────────────────────────────────────────────────────
g = fresh_gate(None)
with patch.object(g, "_local_rules_file", return_value=None):
    raised = False
    try:
        g.assert_configured()
    except g.GateNotConfigured:
        raised = True
    scenario("unconfigured gate REFUSES rather than passing everything",
             raised, f"GateNotConfigured raised={raised}")

# ── exact, closed policy schema ─────────────────────────────────────────────
invalid_policy_scenario(
    "a non-object policy is rejected",
    ["not", "an", "object"],
)
invalid_policy_scenario(
    "both root keys are required even when one valid rule exists",
    {"content": [SECRET]},
)
invalid_policy_scenario(
    "unknown root keys are rejected even when all rules are valid",
    {"content": [SECRET], "paths": [], "extra": []},
)
invalid_policy_scenario(
    "content must be an array",
    {"content": SECRET, "paths": ["**/private-notes/**"]},
)
invalid_policy_scenario(
    "paths must be an array",
    {"content": [SECRET], "paths": "**/private-notes/**"},
)
invalid_policy_scenario(
    "a non-string content value invalidates valid sibling rules",
    {"content": [SECRET, 7], "paths": ["**/private-notes/**"]},
)
invalid_policy_scenario(
    "a blank path value invalidates valid sibling rules",
    {"content": [SECRET], "paths": ["**/private-notes/**", " \t"]},
)
invalid_policy_scenario(
    "an invalid regex invalidates valid sibling rules",
    {"content": [SECRET, "("], "paths": ["**/private-notes/**"]},
)
invalid_policy_scenario(
    "duplicate content values invalidate the whole policy",
    {"content": [SECRET, SECRET], "paths": ["**/private-notes/**"]},
)
invalid_policy_scenario(
    "duplicate path values invalidate the whole policy",
    {
        "content": [SECRET],
        "paths": ["**/private-notes/**", "**/private-notes/**"],
    },
)
invalid_policy_scenario(
    "malformed Unicode values invalidate the whole policy",
    {"content": [SECRET, "\ud800"], "paths": ["**/private-notes/**"]},
)
invalid_policy_scenario(
    "NUL path values invalidate the whole policy",
    {"content": [SECRET], "paths": ["**/private-notes/**", "\x00"]},
)
invalid_policy_scenario(
    "malformed JSON is rejected",
    raw_rules='{"content":["valid"],"paths":[',
)
invalid_policy_scenario(
    "duplicate JSON object keys are rejected",
    raw_rules='{"content":["one"],"content":["two"],"paths":[]}',
)
invalid_policy_scenario(
    "an empty total policy fails closed",
    {"content": [], "paths": []},
)
for name, policy in (
    ("a content-only policy remains valid", {"content": [SECRET], "paths": []}),
    (
        "a path-only policy remains valid",
        {"content": [], "paths": ["**/private-notes/**"]},
    ),
):
    valid_gate = fresh_gate(policy)
    try:
        valid_gate.assert_configured()
    except Exception as error:
        scenario(name, False, f"unexpected {type(error).__name__}")
    else:
        scenario(name, True, "configured")

# The real local source is never moved. Exercise local-file loading against a
# separate 0600 fixture and prove that even its inode is left untouched.
proof_cache = Path(__file__).resolve().parent / ".pytest_cache"
cache_preexisted = proof_cache.exists()
proof_cache.mkdir(mode=0o700, exist_ok=True)
proof_rules = proof_cache / f"gate-rules-preservation-{uuid.uuid4().hex}.json"
fixture_payload = json.dumps(
    {"content": [SECRET], "paths": ["**/private-notes/**"]}
).encode("utf-8")
fixture_before = None
fixture_after = None
fixture_error = ""
invalid_override_rejected = False
try:
    descriptor = os.open(
        proof_rules,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    with os.fdopen(descriptor, "wb") as fixture:
        fixture.write(fixture_payload)
        fixture.flush()
        os.fsync(fixture.fileno())

    fixture_before = snapshot(proof_rules)
    local_gate = fresh_gate(None)
    with patch.object(
        local_gate,
        "_local_rules_file",
        return_value=proof_rules,
    ):
        local_gate.assert_configured()

    invalid_override = fresh_gate(raw_rules=" ")
    with patch.object(
        invalid_override,
        "_local_rules_file",
        return_value=proof_rules,
    ):
        try:
            invalid_override.assert_configured()
        except invalid_override.GatePolicyInvalid:
            invalid_override_rejected = True
    fixture_after = snapshot(proof_rules)
except Exception as error:
    fixture_error = type(error).__name__
finally:
    proof_rules.unlink(missing_ok=True)
    if not cache_preexisted:
        try:
            proof_cache.rmdir()
        except OSError:
            pass

fixture_preserved = (
    fixture_before is not None
    and fixture_before[1] == 0o600
    and fixture_after == fixture_before
)
scenario(
    "loading a separate 0600 rules file preserves bytes, mode, owner, and inode",
    fixture_preserved,
    fixture_error
    or (
        "fixture missing after load" if fixture_after is None
        else (
            f"mode={oct(fixture_after[1])}; "
            f"unchanged={fixture_after == fixture_before}"
        )
    ),
)
scenario(
    "an invalid environment policy never falls back to a valid local file",
    invalid_override_rejected,
    f"GatePolicyInvalid raised={invalid_override_rejected}",
)

# ── configured behaviour ────────────────────────────────────────────────────
g = fresh_gate({"content": [SECRET], "paths": ["**/private-notes/**"]})

keep, why = g.screen(b"# A perfectly ordinary spec\n", "docs/SPEC.md")
scenario("an ordinary file is kept", keep and why == "", f"keep={keep}")

keep, why = g.screen(f"see {SECRET} for context".encode(), "docs/SPEC.md")
scenario("a configured content rule withholds the file",
         not keep and "content rule" in why, why)
scenario("...and the reason NAMES THE RULE, never the match",
         SECRET not in why, f"reason={why!r}")

keep, why = g.screen(b"anything", "a/private-notes/b.md")
scenario("a configured path rule withholds the file", not keep, why)

keep, why = g.screen_path("modules/public-dependency")
scenario("a public gitlink path passes path-only screening",
         keep and why == "", f"keep={keep}")
keep, why = g.screen_path("a/private-notes/dependency")
scenario("a configured gitlink path is still withheld", not keep, why)

# ── always-on structural rules (public by design) ───────────────────────────
for path in (".env", "api/.env.production", "keys/server.pem", "id_rsa",
             "cfg/local.settings.json", "x/sensitive/notes.md"):
    keep, why = g.screen(b"whatever", path)
    scenario(f"structural: {path} never travels", not keep, why)

keep, why = g.screen(b"-----BEGIN RSA PRIVATE KEY-----\nabc\n", "misc/blob.txt")
scenario("a private key is withheld even under an innocent filename",
         not keep and "credential" in why, why)

keep, why = g.screen(b"token = 'ghp_" + b"a" * 36 + b"'", "settings.py")
scenario("a token-shaped string is withheld", not keep, why)
scenario("...and the reason does not echo the token",
         "ghp_" not in why, f"reason={why!r}")

# ── the recursion: the gate must refuse to publish its own rules ────────────
for path in (".gate-rules", "tools/.ip-rules", "x/.pii-terms",
             "sensitive/publication-denylist.json"):
    keep, why = g.screen(b'{"content":["x"]}', path)
    scenario(f"the gate refuses to publish its own rules ({path})", not keep, why)

# ── invalid UTF-8: scan what is recognizable, then fail closed ──────────────
keep, why = g.screen(bytes(range(256)), "assets/logo.png")
scenario("undecodable content is withheld rather than treated as screened",
         not keep and "UTF-8" in why, why)

keep, why = g.screen(
    b"\xff configured finding: " + SECRET.encode(),
    "assets/blob.bin",
)
scenario("configured rules still scan invalid UTF-8 bytes",
         not keep and "content rule" in why, why)
scenario("...and invalid UTF-8 findings still never echo the match",
         SECRET not in why, f"reason={why!r}")

keep, why = g.screen(
    b"\xff token = ghp_" + b"a" * 36,
    "assets/blob.bin",
)
scenario("credential shapes still scan invalid UTF-8 bytes",
         not keep and "credential" in why, why)

keep, why = g.screen(bytes(range(256)), "certs/private.pem")
scenario("path rules still take precedence for invalid UTF-8", not keep, why)

local_rules_after = snapshot(LOCAL_RULES)
if LOCAL_RULES_BEFORE is None:
    local_rules_observed = "absent throughout"
elif local_rules_after is None:
    local_rules_observed = "source disappeared during proof"
else:
    local_rules_observed = (
        f"mode={oct(local_rules_after[1])}; "
        f"same owner={local_rules_after[2:4] == LOCAL_RULES_BEFORE[2:4]}; "
        f"same inode={local_rules_after[4:] == LOCAL_RULES_BEFORE[4:]}"
    )
scenario(
    "the proof never changes the user's .gate-rules source",
    local_rules_after == LOCAL_RULES_BEFORE,
    local_rules_observed,
)

print(f"\n{len(FAILURES)} failing scenario(s)" if FAILURES
      else "\nall scenarios behaved as specified")
sys.exit(1 if FAILURES else 0)
