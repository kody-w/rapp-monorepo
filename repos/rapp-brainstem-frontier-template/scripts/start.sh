#!/bin/bash
# Launch this template's Frontier estate: grail Brainstem by reference,
# Frontier shell by reference. Nothing is vendored; everything reverts.
set -euo pipefail

# 1. the grail Brainstem (public one-liner, only if absent)
if [ ! -d "$HOME/.brainstem/src/rapp_brainstem" ]; then
  echo "→ installing the RAPP Brainstem (grail, by reference)"
  curl -sSfL https://raw.githubusercontent.com/kody-w/rapp-installer/main/install.sh | bash
fi

# 2. the Frontier shell (rappid flavor) — reuse a checkout or clone one
FRONTIER_APP_DIR="${FRONTIER_APP_DIR:-}"
if [ -z "$FRONTIER_APP_DIR" ]; then
  for c in "$HOME/Documents/GitHub/aibast-agents-library-rappid-first/beta" \
           "$HOME/Documents/GitHub/aibast-agents-library/beta" \
           "$HOME/.rapp-frontier/beta"; do
    [ -f "$c/package.json" ] && FRONTIER_APP_DIR="$c" && break
  done
fi
if [ -z "$FRONTIER_APP_DIR" ]; then
  echo "→ fetching the Frontier shell (rappid flavor)"
  git clone --depth 1 -b feat/rappid-first-ui \
    https://github.com/kody-w/aibast-agents-library.git "$HOME/.rapp-frontier"
  FRONTIER_APP_DIR="$HOME/.rapp-frontier/beta"
fi

cd "$FRONTIER_APP_DIR"
[ -d node_modules ] || npm install --no-fund --no-audit
echo "→ launching Frontier from $FRONTIER_APP_DIR"
exec npm start
