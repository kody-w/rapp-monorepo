#!/usr/bin/env bash
#
# This repo is a projection of the kernel's CONSTITUTION.md, the same way DOG
# is a projection of GOD. A mirror without a drift check is how canon quietly
# forks — so this byte-compares against upstream and fails if they disagree.
#
# Upstream wins, always. If this fails, fix it here with a traceable commit.
#
set -uo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-kody-w/RAPP}"
UPSTREAM_PATH="${UPSTREAM_PATH:-CONSTITUTION.md}"
RAW_URL="https://raw.githubusercontent.com/$UPSTREAM_REPO/main/$UPSTREAM_PATH"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL="$HERE/CONSTITUTION.md"

fail=0
say() { printf '  %s\n' "$*"; }

printf '\nConstitution drift check\n\n'

[[ -f "$LOCAL" ]] || { say "FAIL  CONSTITUTION.md is missing"; exit 1; }

# The Bill of Rights is derived from Article LVI, so LII must exist here.
if grep -q '^## Article LVI' "$LOCAL"; then
  say "ok    Article LVI is present"
else
  say "FAIL  Article LVI is missing"; fail=1
fi

# Every article the Bill of Rights claims must actually be in the article.
if [[ -f "$HERE/BILL-OF-RIGHTS.md" ]]; then
  count=$(grep -c '^## Article the ' "$HERE/BILL-OF-RIGHTS.md" || true)
  if [[ "$count" == "10" ]]; then
    say "ok    Bill of Rights has 10 articles"
  else
    say "FAIL  Bill of Rights has $count articles, expected 10"; fail=1
  fi

  # The page is generated from the markdown; if they disagree, the page is stale.
  page_count=$(grep -c 'class="a" id="a' "$HERE/docs/index.html" || true)
  if [[ "$page_count" == "$count" ]]; then
    say "ok    the published page matches the document ($count articles)"
  else
    say "FAIL  page has $page_count articles, document has $count — regenerate docs/index.html"; fail=1
  fi
fi

# Fetch upstream. The API is authoritative and uncached; raw.githubusercontent
# caches for ~5 minutes, so a fresh amendment there looks exactly like drift.
fetch_upstream() {
  local out="$1"
  if command -v gh >/dev/null 2>&1 &&
     gh api "repos/$UPSTREAM_REPO/contents/$UPSTREAM_PATH" --jq '.content' 2>/dev/null |
       base64 -d > "$out" 2>/dev/null && [[ -s "$out" ]]; then
    echo "api"; return 0
  fi
  if command -v curl >/dev/null 2>&1 && curl -fsSL "$RAW_URL" -o "$out" 2>/dev/null; then
    echo "raw"; return 0
  fi
  return 1
}

tmp="$(mktemp)"
if source_used="$(fetch_upstream "$tmp")"; then
  if cmp -s "$LOCAL" "$tmp"; then
    say "ok    byte-identical to upstream (via $source_used)"
  else
    say "DRIFT this mirror disagrees with upstream (via $source_used):"
    diff <(sed -n 's/^\(## Article [A-Z0]*\) .*/\1/p' "$tmp") \
         <(sed -n 's/^\(## Article [A-Z0]*\) .*/\1/p' "$LOCAL") | head -20 | sed 's/^/        /'
    say ""
    say "      Upstream wins. Sync with:"
    say "      gh api repos/$UPSTREAM_REPO/contents/$UPSTREAM_PATH --jq .content | base64 -d > CONSTITUTION.md"
    fail=1
  fi
else
  say "skip  upstream unreachable (offline)"
fi
rm -f "$tmp"

printf '\n'
[[ "$fail" -eq 0 ]] && { say "No drift."; printf '\n'; exit 0; }
say "Drift detected."; printf '\n'; exit 1
