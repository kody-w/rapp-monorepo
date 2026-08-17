"""Where the internal-note rules come from — deliberately NOT from this repo.

Same argument as pii_terms.py, one layer up. This repo is PUBLIC, and a
committed list of the exact internal strings a filter suppresses is a better
search index than the notes it removes: a reader who cannot find the matter
number in the tree can simply read the tripwire list and go looking for it in
history. The denylist becomes the disclosure. So the rules live outside the
tree and are injected at run time.

Sources, in order:
  1. $RAPP_IP_RULES  -- JSON. In CI: ${{ secrets.IP_RULES }}.
  2. ./.ip-rules     -- JSON, gitignored, local only.

Shape:
  {
    "tripwires": ["regex", ...],
    "redactions": [["regex", "replacement"], ...]
  }

`tripwires` are the fail-closed backstop: anything still matching after
redaction means an internal note reached the mirror in a shape the rules did
not anticipate. `redactions` rewrite the known shapes, preserving the
surrounding technical sentence.

If neither source is configured this module RAISES, for the same reason
pii_terms does: a sanitiser that silently sanitises nothing, or a test that
passes vacuously because its pattern list is empty, is worse than none at
all — it reports "clean" while publishing everything. Fail closed, loudly.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


class IPRulesNotConfigured(RuntimeError):
    """Raised when no rules are available. Never swallow this."""


_MESSAGE = (
    "No internal-note rules configured, so redaction would silently do nothing.\n"
    "  Set RAPP_IP_RULES='{\"tripwires\":[...],\"redactions\":[[...]]}'\n"
    "      (CI: ${{ secrets.IP_RULES }})\n"
    "  or create an untracked ./.ip-rules with the same JSON.\n"
    "Refusing to run with an empty rule set (fail closed)."
)


def _parse(raw: str):
    doc = json.loads(raw)
    tripwires = [t for t in (doc.get("tripwires") or []) if isinstance(t, str) and t.strip()]
    redactions = [(p, r) for p, r in (doc.get("redactions") or [])
                  if isinstance(p, str) and isinstance(r, str)]
    return tripwires, redactions


def load_rules() -> tuple[list[str], list[tuple[str, str]]]:
    raw = os.environ.get("RAPP_IP_RULES", "").strip()
    if not raw:
        f = Path(__file__).resolve().parent.parent / ".ip-rules"
        if f.is_file():
            raw = f.read_text(encoding="utf-8").strip()
    if not raw:
        raise IPRulesNotConfigured(_MESSAGE)
    tripwires, redactions = _parse(raw)
    if not tripwires:
        raise IPRulesNotConfigured(_MESSAGE)
    return tripwires, redactions
