#!/usr/bin/env python3
"""Check every source citation this revision added against the actual files.

RAR is git-clean, so its line numbers are asserted exactly.
rapp-vision is being rewritten by a parallel session, so it is asserted by
IDENTIFIER only — which is exactly why the spec now cites it that way.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path("/private/tmp/claude-501/-Users-kodywildfeuer-Documents-GitHub-"
            "m365-agents-for-python-localFirstTools/"
            "a6328c52-bd98-4aa5-b065-20e583737a46/scratchpad")
RAR = ROOT / "RAR" / "scripts" / "discussion_ratings.py"
RV = ROOT / "rapp-vision" / "scripts" / "rapp_metrics.py"

rar = RAR.read_text(encoding="utf-8").splitlines()
rv_text = RV.read_text(encoding="utf-8")
fails, n = [], 0


def line_says(path, lines, lineno, needle, label):
    global n
    n += 1
    actual = lines[lineno - 1] if 0 < lineno <= len(lines) else "<out of range>"
    if needle in actual:
        print(f"  PASS  {label}\n          {path.name}:{lineno}  {actual.strip()[:88]}")
    else:
        print(f"  FAIL  {label}\n          {path.name}:{lineno} is: {actual.strip()[:88]}")
        fails.append(label)


def file_has(text, needle, label, present=True):
    global n
    n += 1
    if (needle in text) == present:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  (expected present={present})")
        fails.append(label)


print("RAR — git-clean, line numbers asserted exactly")
dirty = subprocess.run(["git", "-C", str(ROOT / "RAR"), "status", "--porcelain"],
                       capture_output=True, text=True).stdout.strip()
n += 1
if dirty:
    print(f"  FAIL  RAR working tree clean (so line cites are stable)\n          {dirty[:200]}")
    fails.append("RAR clean")
else:
    print("  PASS  RAR working tree clean (so line cites are stable)")

# Gap 5 / M39
line_says(RAR, rar, 78, "POSITIVE_REACTIONS = frozenset", "M39/Gap5: :78 POSITIVE_REACTIONS")
line_says(RAR, rar, 79, '"THUMBS_UP", "HEART", "HOORAY", "ROCKET", "LAUGH"',
          "M39/Gap5: :79 the five contents")
line_says(RAR, rar, 272, "def positive_score", "M39/Gap5: :272 positive_score defined")
line_says(RAR, rar, 277, 'total += (group.get("reactors") or {}).get("totalCount", 0)',
          "M39/Gap5: :277 sums reactors across contents")
line_says(RAR, rar, 343, "upvotes = positive_score(", "M39/Gap5: :343 published as upvotes")

# Gap 6 / M40
line_says(RAR, rar, 281, "def marker_comment_of", "M40/Gap6: :281 marker_comment_of")
line_says(RAR, rar, 284, 'if marker in (c.get("body") or "")',
          "M40/Gap6: :284 plain substring containment")
file_has("\n".join(rar[154:170]), "author",
         "M40/Gap6: :155-170 discussion query requests NO author field", present=False)
file_has("\n".join(rar), "viewerDidAuthor",
         "M40/Gap6: RAR has no viewerDidAuthor anywhere", present=False)

# Gap 7 / M38
line_says(RAR, rar, 165, "reactionGroups { content reactors { totalCount } }",
          "M38/Gap7: :165 comment reactions read as bare totalCount")
line_says(RAR, rar, 168, "reactionGroups { content reactors { totalCount } }",
          "M38/Gap7: :168 top-post reactions read as bare totalCount")
line_says(RAR, rar, 310, '.get("totalCount", 0)', "M38/Gap7: :310 signal_counts totalCount")
line_says(RAR, rar, 321, '.get("totalCount", 0)', "M38/Gap7: :321 download_count totalCount")
file_has("\n".join(rar), "__typename",
         "M38/Gap7: '__typename' appears nowhere in RAR", present=False)

# Gap 8 / M37
line_says(RAR, rar, 160, "comments(first: 25)", "M37/Gap8: :160 counting query one page")
line_says(RAR, rar, 200, "comments(first: 25)", "M37/Gap8: :200 provisioner search one page")
line_says(RAR, rar, 153, "pageInfo { hasNextPage endCursor }",
          "M37/Gap8: :153 pageInfo is on DISCUSSIONS, not comments")

print()
print("rapp-vision — actively rewritten; asserted by IDENTIFIER only")
n += 1
print(f"  INFO  file is now {len(rv_text.splitlines())} lines "
      f"(1436 at first read this session, 1635 at pin) — line cites would be stale")
for ident, label in [
    ("def is_machinery_comment", "M40: is_machinery_comment() exists"),
    ("def machinery_authored", "M40: machinery_authored() exists"),
    ("def marker_comment_of", "M40: marker_comment_of() exists"),
    ("def machinery_comment_count", "M10: machinery_comment_count() exists"),
    ("def human_comment_count", "M10: human_comment_count() exists"),
    ("def reviewer_feedback", "Gap A: reviewer_feedback() IS implemented"),
    ("def build_editorial", "Gap A: build_editorial() exists"),
    ("def rubric_health", "Gap A: rubric_health() exists"),
    ("def positive_score", "Gap D: positive_score() exists"),
    ("def signal_counts", "Gap C: signal_counts() exists"),
    ("def watch_count", "Gap C: watch_count() exists"),
    ("viewerDidAuthor", "M40: rapp-vision requests viewerDidAuthor"),
    ("comments(first: 100)", "Gap D: comments read one page deep"),
    ('EDITORIAL_BY = "rapp-vision-rubric/1.0"', "Gap A: keyed by a version-bearing string"),
    ('"github-actions[bot]"', "M40: default machinery author allowlist"),
]:
    file_has(rv_text, ident, label)

# Prose quotes: the source wraps them across lines and prefixes comment lines
# with '#', so strip the prefixes and normalize whitespace before comparing.
import re as _re
rv_flat = " ".join(
    _re.sub(r"^\s*#\s?", "", ln) for ln in rv_text.splitlines()
).replace("  ", " ")
rv_flat = " ".join(rv_flat.split())
for quote, label in [
    ("A marker is a ROUTING LABEL, never proof of who wrote the thing carrying it.",
     "M40: 'ROUTING LABEL' sentence quoted in §7.2/§14"),
    ("the direction of the error is the safe one, but it is an error.",
     "Gap B: KNOWN LIMITS reply sentence quoted verbatim in §14"),
    ("Restoring a number needs nested pagination on the comments connection, "
     "which is a live-API change this file does not make.",
     "M37 row: 'nested pagination' sentence quoted verbatim in §14"),
    ("It is NOT published as ``totalCount`` minus the machinery found on page one: "
     "a machinery comment past position 100 is not in the subtrahend and would be "
     "counted as a human reply, which is a machine's own output landing in a human counter.",
     "M37 row: the truncation rationale quoted verbatim in §14"),
    ("Ownership is checked, PROVENANCE IS NOT.",
     "M40 residual: 'PROVENANCE IS NOT' quoted verbatim"),
    ("comments_truncated", "M37 row: comments_truncated flag exists"),
]:
    file_has(rv_flat, " ".join(quote.split()), label)
file_has(rv_text, "__typename", "Gap C: '__typename' appears nowhere in rapp-vision",
         present=False)
file_has(rv_text, "replies(first", "Gap B: no replies connection requested", present=False)
file_has(rv_text, 'body.startswith(marker) for marker in MACHINERY_MARKERS',
         "M40: anchored startswith test present")

print()
print("=" * 78)
print(f"{n - len(fails)}/{n} citation checks passed")
for f in fails:
    print("  -", f)
print("=" * 78)
sys.exit(1 if fails else 0)
