#!/bin/bash
# The whole package in one pull: the grail Brainstem, the grail Electron
# template, and the Frontier shell — cloned, installed, launched.
#   curl -sSfL https://raw.githubusercontent.com/kody-w/rapp-brainstem-frontier-template/main/scripts/bootstrap.sh | bash
set -euo pipefail
DEST="${RAPP_ESTATE_DIR:-$HOME/rapp-frontier-estate}"
if [ ! -d "$DEST/.git" ]; then
  echo "→ pulling the grail Electron template"
  git clone --depth 1 https://github.com/kody-w/rapp-brainstem-frontier-template.git "$DEST"
fi
cd "$DEST"
bash scripts/start.sh &
STARTED=$!
# give the kernel a moment, then land the template's skins over the grail chat
for i in $(seq 1 30); do
  curl -sf -m 2 http://127.0.0.1:7071/health >/dev/null 2>&1 && break
  sleep 2
done
bash scripts/install-skin.sh || true
wait $STARTED
