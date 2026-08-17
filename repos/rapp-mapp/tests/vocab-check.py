#!/usr/bin/env python3
"""
Vocabulary conformance for rapp-mapp.

The repo this supersedes drifted two ways at once, and the second is what made
it useless: 544 uses of "hatch" against 277 of "plant", while the membrane —
Lexicon word 5, the split every organism has — appeared 5 times and DOG 4.

A map whose words disagree with the Lexicon cannot route anyone correctly, so
this checks the words. It fetches the Lexicon from the governance authority
rather than trusting a local copy, because a vendored copy is the drift.

    python3 tests/vocab-check.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEXICON_URL = "https://raw.githubusercontent.com/kody-w/RAPP/main/LEXICON.md"

GRN, RED, YEL, DIM, NC = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

passed = failed = 0


def ok(msg: str) -> None:
    global passed
    passed += 1
    print(f"  {GRN}ok{NC}   {msg}")


def bad(msg: str, detail: str = "") -> None:
    global failed
    failed += 1
    print(f"  {RED}FAIL{NC} {msg}")
    if detail:
        print(f"       {detail}")


def fetch_lexicon() -> str | None:
    """The authority, not a copy of it."""
    try:
        out = subprocess.run(
            ["gh", "api", "repos/kody-w/RAPP/contents/LEXICON.md", "--jq", ".content"],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0 and out.stdout.strip():
            import base64
            return base64.b64decode(out.stdout).decode("utf-8")
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        with urllib.request.urlopen(LEXICON_URL, timeout=10) as r:
            return r.read().decode("utf-8")
    except Exception:
        return None


print("\nrapp-mapp — vocabulary conformance\n")

# ── the map is well-formed and honest about what it is ───────────────────
try:
    mapp = json.loads((ROOT / "mapp.json").read_text())
    ok("mapp.json parses")
except Exception as exc:
    bad("mapp.json parses", str(exc))
    sys.exit(1)

if mapp.get("is_registry") is False and "not a registry" in mapp.get("authority_note", "").lower():
    ok("declares itself NOT a registry")
else:
    bad("declares itself NOT a registry",
        "the repo this supersedes was quarantined for drifting toward registry authority")

if any(s.get("authority") for s in mapp["surfaces"]):
    ok("names the surfaces that DO carry authority")
else:
    bad("names the surfaces that DO carry authority")

if mapp.get("known_gaps"):
    unfixed = [g for g in mapp["known_gaps"] if g.get("status") == "open"]
    ok(f"records {len(mapp['known_gaps'])} known gaps ({len(unfixed)} open) rather than hiding them")
else:
    bad("records known gaps")

# ── the words ────────────────────────────────────────────────────────────
prose = "\n".join(
    p.read_text() for p in [ROOT / "mapp.json", ROOT / "README.md"] if p.exists()
)

# An organism is planted. Hatching belongs to eggs (Article L).
organism_hatch = re.findall(r"hatch\w*\s+(?:an?\s+|your\s+|the\s+)?organism", prose, re.I)
if organism_hatch:
    bad("no organism is 'hatched'", f"found: {organism_hatch[:3]}")
else:
    ok("no organism is 'hatched' — organisms are planted (word 3)")

if re.search(r"\bplant\b", prose, re.I):
    ok("uses PLANT for organisms")
else:
    bad("uses PLANT for organisms")

# The membrane and its two sides must actually be present — this is the
# specific thing the old map lost.
for word, why in [
    ("membrane", "word 5 — the split every organism has"),
    ("bones", "the public skeleton"),
    ("vault", "the private flesh"),
    ("DOG", "the bones walking"),
    ("GOD", "bones + vault"),
]:
    hits = len(re.findall(rf"\b{word}\b", prose, 0 if word in ("DOG", "GOD") else re.I))
    if hits >= 2:
        ok(f"{word} is present ({hits}) — {why}")
    else:
        bad(f"{word} is present — {why}", f"only {hits} occurrence(s)")

# GOD contains DOG. Stating them as disjoint halves is the error corrected in
# Article LVI.9, and a map must not reintroduce it.
if re.search(r"\*{0,2}GOD\*{0,2} is bones \+ vault", prose):
    ok("GOD is stated as bones + vault — the whole that CONTAINS the DOG")
else:
    bad("GOD is stated as bones + vault",
        "stating DOG and GOD as disjoint halves is the Article LVI.9 error")

if re.search(r"twin is not (?:an|itself an) organism", prose, re.I):
    ok("a twin is not an organism (Article XLIX)")
else:
    bad("a twin is not an organism (Article XLIX)")

# ── agreement with the actual Lexicon ────────────────────────────────────
lexicon = fetch_lexicon()
if lexicon is None:
    print(f"  {YEL}skip{NC} Lexicon unreachable (offline)")
else:
    if "### 3. organism" in lexicon:
        ok("Lexicon fetched from the authority — organism is word 3")
    else:
        bad("Lexicon word 3 is organism", "the Lexicon changed; this map must follow")

    if re.search(r"DOG.*bones walking", lexicon, re.S):
        ok("Lexicon agrees: the DOG is the bones walking")
    else:
        bad("Lexicon agrees: the DOG is the bones walking")

    if re.search(r"\*{0,2}GOD\*{0,2} is bones \+ vault", lexicon):
        ok("Lexicon agrees: the GOD is bones + vault")
    else:
        bad("Lexicon agrees: the GOD is bones + vault")

    claimed = [r["source"] for r in [mapp["vocabulary"]]]
    if "LEXICON.md" in claimed[0]:
        ok("cites the Lexicon as its vocabulary source")
    else:
        bad("cites the Lexicon as its vocabulary source")

# ── every surface is real ────────────────────────────────────────────────
print()
missing = []
for surface in mapp["surfaces"]:
    repo = surface["repo"]
    try:
        out = subprocess.run(["gh", "api", f"repos/{repo}", "--jq", ".full_name"],
                             capture_output=True, text=True, timeout=15)
        if out.returncode != 0:
            missing.append(repo)
    except (OSError, subprocess.SubprocessError):
        missing = None
        break

if missing is None:
    print(f"  {YEL}skip{NC} surface existence (gh unavailable)")
elif missing:
    # A map that points at a 404 is the defect Article LVI.9 records.
    bad("every mapped surface exists", f"missing: {', '.join(missing)}")
else:
    ok(f"every one of the {len(mapp['surfaces'])} mapped surfaces exists")

print(f"\n{passed} passed, {failed} failed\n")
sys.exit(0 if failed == 0 else 1)
