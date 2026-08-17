#!/usr/bin/env python3
"""M21-corollary check on verify_spec.py itself.

A test that cannot fail is worse than no test. For each of the five defects,
reintroduce it into a COPY of SPEC.md and assert verify_spec.py goes RED.
The real SPEC.md is never written to.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/private/tmp/claude-501/-Users-kodywildfeuer-Documents-GitHub-"
            "m365-agents-for-python-localFirstTools/"
            "a6328c52-bd98-4aa5-b065-20e583737a46/scratchpad")
SPEC = ROOT / "rapp-metrics" / "SPEC.md"
VERIFY = ROOT / "verify_spec.py"
original = SPEC.read_text(encoding="utf-8")

# Each mutation puts ONE defect back the way the review found it.
MUTATIONS = {
    "D1 reactor classification removed (M38 gutted)":
        lambda t: t.replace(
            "**M38 — Reactors MUST be classified",
            "**M38 — Reactors are counted as the platform reports them"),
    "D1 honest residual removed from §1.1":
        lambda t: t.replace(
            '**"no *declared* machine actor is in a\n  human counter"** — not "no machine actor is"',
            '**no machine actor is ever in a\n  human counter**'),
    "D2 endorsement back to 'a positive reaction' (multi-content)":
        lambda t: t.replace("**Exactly one named reaction content**",
                            "A positive reaction"),
    "D2 M39 no-sum rule removed":
        lambda t: t.replace(
            "**M39 — No counter is a sum of two or more reaction contents",
            "**M39 — Positive reactions may be summed"),
    "D3 M10 formula back to comments.totalCount only":
        lambda t: t.replace("replies.totalCount", "0  # replies ignored"),
    "D3 replies dropped from the required query":
        lambda t: t.replace("replies(first: M)", "# no replies requested"),
    "D4 M40 anchoring removed (substring matching restored)":
        lambda t: t.replace("**M40 — Marker recognition is anchored AND author-bound.**",
                            "**M40 — Markers are located by substring.**"),
    "D4 M37 exhaustive lookup removed":
        lambda t: t.replace("**M37 — Marker lookup MUST be exhaustive.**",
                            "**M37 — One page of comments is enough.**"),
    "D5 reviewer_id removed from the review surface (S9 gutted)":
        lambda t: t.replace("**S9. Every `review` surface MUST declare a `reviewer_id`",
                            "**S9. A `review` surface has no reviewer binding"),
    "D5 §8.5 keyed by the rubric string again":
        lambda t: t.replace('"rubric": {\n      "surface": "review:rubric",',
                            '"rapp-vision-rubric/1.0": {\n      "surface": "review:rubric",'),
    "structural: a checklist item deleted (numbering gap)":
        lambda t: re.sub(r"^64\. \*\*No published counter.*?(?=^65\. )", "",
                         t, flags=re.M | re.S),
    "structural: a json example broken":
        lambda t: t.replace('"kind": "endorsement",\n      "object": "top_post",',
                            '"kind": "endorsement"\n      "object": "top_post",', 1),
    "structural: stale invariant count restored":
        lambda t: t.replace("§9 is forty invariants", "§9 is thirty-six invariants")
                   .replace("40 invariants each with rationale", "36 invariants each with rationale"),
}

print("Baseline: verifier on the real SPEC.md")
base = subprocess.run([sys.executable, str(VERIFY), str(SPEC)],
                      capture_output=True, text=True)
print(f"  exit={base.returncode}  ({base.stdout.strip().splitlines()[-2]})")
if base.returncode != 0:
    print("BASELINE IS RED — fix the spec before trusting these mutations.")
    sys.exit(2)

survived = []
print()
print("Mutations (each MUST turn the verifier red):")
for name, mutate in MUTATIONS.items():
    mutated = mutate(original)
    if mutated == original:
        print(f"  ERROR   {name}: mutation was a no-op (pattern not found)")
        survived.append(name + " [no-op]")
        continue
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "SPEC.md"
        tmp.write_text(mutated, encoding="utf-8")
        r = subprocess.run([sys.executable, str(VERIFY), str(tmp)],
                           capture_output=True, text=True)
    if r.returncode != 0:
        failed = [l.strip()[6:] for l in r.stdout.splitlines()
                  if l.strip().startswith("FAIL")]
        print(f"  RED     {name}")
        for f in failed[:3]:
            print(f"            caught by: {f}")
    else:
        print(f"  SURVIVED  {name}  <-- verifier cannot detect this")
        survived.append(name)

print()
assert SPEC.read_text(encoding="utf-8") == original, "SPEC.md was modified!"
print("SPEC.md byte-identical after the run: yes")
print(f"{len(MUTATIONS) - len(survived)}/{len(MUTATIONS)} mutations caught")
sys.exit(1 if survived else 0)
