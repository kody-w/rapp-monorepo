"""No internal legal/IP notes appear in committed Bible content.

Upstream specs sometimes annotate an article with the maintainers' internal
legal posture, or point at a credential-gated legal directory. That is not
platform specification, and this repo is public, so `mirror_sync.redact_
internal_notes` strips it on the way in. This test is the backstop: if such a
note ever lands in the tree by another route, the suite goes red here.

Scanned: every committed file EXCEPT this test and the redaction filter
itself, both of which carry the patterns as *patterns*, not as content.
"""

import pathlib
import re
import sys

from .conftest import REPO_ROOT, iter_committed_files

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from ip_terms import IPRulesNotConfigured, load_rules  # noqa: E402

# Nothing needs allowlisting any more: the patterns live outside the tree
# (scripts/ip_terms.py), so neither this test nor the filter carries them as
# content. A file that had to be exempted from its own tripwire scan was the
# tell that the list was in the wrong place.
ALLOWLIST: set[str] = set()


def test_no_internal_ip_notes_in_committed_content():
    try:
        tripwires, _ = load_rules()
    except IPRulesNotConfigured as exc:      # never a silent pass
        import pytest
        pytest.skip(f"no rules configured, so this scan would be vacuous: {exc}")
    patterns = [re.compile(t, re.IGNORECASE) for t in tripwires]
    assert patterns, "tripwire list is empty; this test would pass vacuously"
    violations = []
    for p in iter_committed_files():
        rel = p.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWLIST:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in patterns:
            m = pat.search(text)
            if m:
                violations.append(f"{rel}: matched {pat.pattern!r} -> {m.group(0)!r}")
    assert not violations, (
        "Internal legal/IP notes found in committed files:\n" + "\n".join(violations)
    )
