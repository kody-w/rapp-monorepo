#!/bin/bash
# Land every skin in rapp_ui/ into the running kernel's skin directory.
# The factory chat is never touched: skins overlay it and this is reversible
# byte-for-byte with revert-skin.sh.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${BRAINSTEM_DIR:-$HOME/.brainstem/src/rapp_brainstem}/.brainstem_data/rapp_ui"
[ -d "$(dirname "$DEST")" ] || { echo "no brainstem at ${BRAINSTEM_DIR:-$HOME/.brainstem/src/rapp_brainstem} — run scripts/start.sh first"; exit 1; }
mkdir -p "$DEST"
for skin in "$HERE"/rapp_ui/*/; do
  id="$(basename "$skin")"
  [ -f "$skin/index.html" ] || continue
  rm -rf "${DEST:?}/$id"
  cp -R "$skin" "$DEST/$id"
  echo "→ skin '$id' installed — open the rapplications dock in the grail chat"
done
