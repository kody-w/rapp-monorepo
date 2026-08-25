#!/bin/bash
# Remove this template's skins from the kernel. The factory grail chat was
# never modified, so removal IS the revert.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${BRAINSTEM_DIR:-$HOME/.brainstem/src/rapp_brainstem}/.brainstem_data/rapp_ui"
for skin in "$HERE"/rapp_ui/*/; do
  id="$(basename "$skin")"
  rm -rf "${DEST:?}/$id" && echo "→ skin '$id' removed — factory chat stands as it always did"
done
