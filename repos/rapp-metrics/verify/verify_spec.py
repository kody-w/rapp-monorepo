#!/usr/bin/env python3
"""Structural verifier for rapp-metrics SPEC.md.

Checks only things that are true or false in the file itself:
  1. every ```json fenced block parses
  2. the conformance checklist is 1..N contiguous with no gaps/dupes
  3. every M<n>/S<n>/F<n>/E<n>/R<n>/L<n>/PR<n> referenced is also DEFINED
  4. the stated invariant/item counts match the actual ones
  5. per-defect assertions: the specific text each fix was supposed to add
"""
import json
import re
import sys
from pathlib import Path

SPEC = Path(sys.argv[1] if len(sys.argv) > 1 else
            "/private/tmp/claude-501/-Users-kodywildfeuer-Documents-GitHub-"
            "m365-agents-for-python-localFirstTools/"
            "a6328c52-bd98-4aa5-b065-20e583737a46/scratchpad/rapp-metrics/SPEC.md")
text = SPEC.read_text(encoding="utf-8")
lines = text.splitlines()
fails, checks = [], 0


def ok(label, cond, detail=""):
    global checks
    checks += 1
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' — ' + detail) if detail else ''}")
        fails.append(label)


print("=" * 78)
print("1. every ```json fenced block parses")
print("=" * 78)
blocks, fence, buf, start = [], None, [], 0
for i, ln in enumerate(lines, 1):
    m = re.match(r"^```(\w*)\s*$", ln)
    if m and fence is None:
        fence, buf, start = m.group(1), [], i
    elif ln.strip() == "```" and fence is not None:
        blocks.append((fence, start, "\n".join(buf)))
        fence = None
    elif fence is not None:
        buf.append(ln)
for lang, ln0, body in blocks:
    if lang == "json":
        try:
            json.loads(body)
            ok(f"json block at line {ln0} parses", True)
        except Exception as exc:
            ok(f"json block at line {ln0} parses", False, str(exc))
print(f"  ({sum(1 for b in blocks if b[0]=='json')} json blocks; "
      f"{sum(1 for b in blocks if b[0]=='jsonc')} jsonc blocks skipped by design)")

print()
print("=" * 78)
print("2. conformance checklist numbering is contiguous")
print("=" * 78)
start = next(i for i, l in enumerate(lines) if l.startswith("## 13."))
end = next(i for i, l in enumerate(lines) if l.startswith("## 14."))
items = [int(m.group(1)) for l in lines[start:end]
         if (m := re.match(r"^(\d+)\. ", l))]
ok("checklist starts at 1", items and items[0] == 1, str(items[:3]))
ok("checklist has no gaps or duplicates",
   items == list(range(1, len(items) + 1)),
   f"got {len(items)} items, first divergence at "
   f"{next((a for a, b in zip(items, range(1, len(items)+1)) if a != b), None)}")
n_items = len(items)
print(f"  ({n_items} checklist items)")

print()
print("=" * 78)
print("3. every referenced identifier is also defined")
print("=" * 78)
body_start = next(i for i, l in enumerate(lines) if l.startswith("## 1."))
defined = {}
for prefix in ("M", "S", "F", "E", "R", "L", "P", "PR", "I", "T", "C-R", "C-W"):
    defined[prefix] = set()
for ln in lines:
    for m in re.finditer(r"\*\*(C-[RW]|PR|[MSFERLPIT])(\d+)\.?\s*[.,—]", ln):
        defined[m.group(1)].add(int(m.group(2)))
for prefix in ("M", "S", "F", "E", "R", "L", "PR", "I", "T", "P", "C-R", "C-W"):
    refs = set()
    pat = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(prefix)}(\d+)\b")
    for ln in lines[body_start:]:
        for m in pat.finditer(ln):
            # skip things like "M365"/years and the PR/P overlap
            refs.add(int(m.group(1)))
    if prefix == "P":
        refs -= defined["PR"]
    missing = sorted(r for r in refs if r not in defined[prefix])
    ok(f"all {prefix}<n> references defined",
       not missing, f"undefined: {[prefix + str(x) for x in missing]}")
n_invariants = max(defined["M"])
print(f"  (M1..M{n_invariants}: {len(defined['M'])} invariants defined)")

print()
print("=" * 78)
print("4. stated counts match reality")
print("=" * 78)
ok("§4 states the real invariant count",
   f"§9 is forty invariants" in text.replace(" ", " ") or
   "forty invariants" in text, "expected 'forty invariants'")
ok("invariant count really is 40", n_invariants == 40 and len(defined["M"]) == 40,
   f"max M = {n_invariants}, defined = {len(defined['M'])}")
ok("§13 header claims 67-item checklist consistent with body",
   n_items == 67, f"checklist has {n_items} items")
ok("changelog states 40 invariants", "40 invariants" in text)
ok("changelog states 67-item checklist", "67-item conformance checklist" in text)
ok("no stale '36 invariants' / '62-item'",
   "36 invariants" not in text and "62-item" not in text)

print()
print("=" * 78)
print("5. per-defect assertions")
print("=" * 78)

# defect 1 — reactor classification + honest residual
ok("D1: M38 defines reactor classification",
   "**M38 — Reactors MUST be classified" in text)
ok("D1: M38 mandates __typename query with reactor pagination",
   "reactors(first: 100) { totalCount nodes { __typename }" in text)
ok("D1: non-User reactors dropped",
   "is not `User`" in text and "`Bot`, `Organization`, `Mannequin`" in text)
flat = re.sub(r"\s+", " ", text)   # prose wraps; assert on normalized whitespace
ok("D1: §1.1 states the residual honestly",
   'no *declared* machine actor is in a human counter' in flat
   and 'not "no machine actor is"' in flat)
ok("D1: §1.1 forbids counting_rules claiming more than M38 checks",
   "claim more than M38 can check is making a false statement" in flat)
ok("D1: §12 bounds the identity read (PR9)",
   "**PR9." in text and "`__typename` **only**" in text)
ok("D1: checklist item 63 tests classification",
   re.search(r"^63\. \*\*Every reactor is classified", text, re.M) is not None)
ok("D1: unclassifiable counter -> null, not totalCount",
   "never as the unclassified `totalCount`" in text)

# defect 2 — endorsement is one reaction content
ok("D2: §3 defines endorsement as exactly one reaction content",
   "**Exactly one named reaction content**" in text)
ok("D2: M39 forbids multi-content sums",
   "**M39 — No counter is a sum of two or more reaction contents" in text)
ok("D2: R7 states the same rule in §7.3",
   "**R7. No counter MAY be the sum of two or more reaction contents" in text)
ok("D2: endorsement surface entry exists in the registry shape",
   '"kind": "endorsement"' in text and '"object": "top_post"' in text)
ok("D2: S8 requires the endorsement surface",
   "**S8.** A surface of kind `endorsement` is **REQUIRED**" in text)
ok("D2: RAR 5-content sum named as non-conforming",
   "NOT a conforming `endorsements` value" in text
   or "not a conforming `endorsements` value" in text)
ok("D2: RAR Gap 5 exists", "| **Gap 5** |" in text)
ok("D2: checklist item 64 tests the no-sum rule",
   re.search(r"^64\. \*\*No published counter is a sum", text, re.M) is not None)

# defect 3 — conversation must include replies
ok("D3: M10 formula includes replies",
   "replies.totalCount" in text or "Σ over comments of replies.totalCount" in text)
ok("D3: M10 requires the replies connection in the query",
   "replies(first: M)" in text)
ok("D3: M10 explains comments.totalCount is top-level only",
   "counts **top-level** comments" in text)
ok("D3: rapp-vision reply gap recorded in §14",
   "Gap B — replies to the machine review are counted nowhere" in text)
ok("D3: §14 quotes rapp-vision's own KNOWN LIMITS",
   "the direction of the error is the safe one, but it is an error" in text)
ok("D3: checklist item 5 fixture covers a reply under a marker comment",
   "nested under one of the marker comments" in text)
ok("D3: stale 'implemented, in the sharper' reply claim removed",
   'Machinery excluded from conversation | implemented, in the sharper "comments carrying a marker" form (M10) |'
   not in text)

# defect 4 — anchored + author-bound marker, exhaustive lookup
ok("D4: M40 requires head-anchored marker",
   "**M40 — Marker recognition is anchored AND author-bound.**" in text
   and "first non-whitespace token" in text)
ok("D4: M40 requires collector authorship",
   "`collector_logins`" in text and "viewerDidAuthor" in text)
ok("D4: S1 forbids substring containment",
   "Substring containment anywhere in a body is **NOT** sufficient" in text)
ok("D4: quote-reply hazard named",
   "Quote reply" in text and "quote-replying" in text)
ok("D4: unmarked machine comment hazard named",
   "comments *without* a\nmarker" in text or "comments **without** a marker" in text
   or "comments *without* a marker" in text)
ok("D4: M37 requires exhaustive marker lookup",
   "**M37 — Marker lookup MUST be exhaustive.**" in text)
ok("D4: M37 forbids provisioning off a partial page",
   "MUST NOT** create a surface comment on the basis of a partial page" in text)
ok("D4: collector_logins is a REQUIRED snapshot field",
   '"collector_logins"' in text and "**F12.**" in text)
ok("D4: F6 carves out collector_logins so it does not violate itself",
   "One exception, and only one:" in text)
ok("D4: RAR first:25 gap recorded", "| **Gap 8** |" in text
   and "comments(first: 25)" in text)
ok("D4: checklist items 65 and 66 exist",
   re.search(r"^65\. \*\*A marker is recognized only when", text, re.M) is not None
   and re.search(r"^66\. \*\*Marker lookup is exhaustive", text, re.M) is not None)

# defect 5 — reviewer_id derivable
ok("D5: S9 requires reviewer_id on every review surface",
   "**S9. Every `review` surface MUST declare a `reviewer_id`" in text)
ok("D5: review surface entry carries reviewer_id",
   '"reviewer_id": "rubric"' in text)
ok("D5: panel rule stated (single synthetic reviewer_id)",
   "single synthetic `reviewer_id`" in text)
ok("D5: §8.5 keys reviewer_feedback by a roster id, not a rubric string",
   '"rapp-vision-rubric/1.0": {' not in text and '"rubric": {' in text)
ok("D5: §8.5 shows the roster entry the id resolves to",
   '{ "id": "rubric", "name": "The Rubric",' in text)
ok("D5: E5 binds the surface id space to the roster",
   "The same id space spans both documents." in text)
ok("D5: reviewer_id must not embed rubric_version",
   "**MUST NOT** embed `rubric_version`" in text
   or "MUST NOT** embed the rubric version" in text)
ok("D5: checklist item 67 exists",
   re.search(r"^67\. \*\*Every `review` surface declares a `reviewer_id`", text,
             re.M) is not None)

print()
print("=" * 78)
print(f"{checks - len(fails)}/{checks} checks passed")
if fails:
    print("FAILED:")
    for f in fails:
        print("  -", f)
print("=" * 78)
sys.exit(1 if fails else 0)
