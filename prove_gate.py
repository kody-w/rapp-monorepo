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
import sys
import tempfile
from pathlib import Path

FAILURES = []


def scenario(name, cond, observed):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}\n        {observed}")
    if not cond:
        FAILURES.append(name)


def fresh_gate(rules=None):
    """Re-import the module so its rule cache is rebuilt per scenario."""
    for k in ("RAPP_GATE_RULES",):
        os.environ.pop(k, None)
    if rules is not None:
        os.environ["RAPP_GATE_RULES"] = json.dumps(rules)
    if "ip_gate" in sys.modules:
        del sys.modules["ip_gate"]
    return importlib.import_module("ip_gate")


SECRET = "SUPER-SECRET-MATTER-9931"

# ── fail closed ─────────────────────────────────────────────────────────────
g = fresh_gate(None)
# Neutralise a stray local .gate-rules so this scenario tests what it says.
_local = Path(__file__).resolve().parent / ".gate-rules"
_stash = None
if _local.exists():
    _stash = _local.read_text(encoding="utf-8")
    _local.unlink()
try:
    g = fresh_gate(None)
    raised = False
    try:
        g.assert_configured()
    except g.GateNotConfigured:
        raised = True
    scenario("unconfigured gate REFUSES rather than passing everything",
             raised, "GateNotConfigured raised")
finally:
    if _stash is not None:
        _local.write_text(_stash, encoding="utf-8")

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

# ── an empty rule set is not a configured rule set ──────────────────────────
g2 = fresh_gate({"content": [], "paths": []})
raised = False
try:
    g2.assert_configured()
except g2.GateNotConfigured:
    raised = True
scenario("an EMPTY rule set counts as unconfigured, not as 'nothing to do'",
         raised, "GateNotConfigured raised")

print(f"\n{len(FAILURES)} failing scenario(s)" if FAILURES
      else "\nall scenarios behaved as specified")
sys.exit(1 if FAILURES else 0)
