#!/usr/bin/env bash
# Start the RAPP Mirror desktop app (dev mode: Vite + Electron).
# The engine is the GLOBAL RAPP brainstem on :7071 — if one is installed the
# mirror simply works with it; on a fresh machine the app pulls one from the
# grail kernel repo automatically on first launch.
set -euo pipefail
cd "$(dirname "$0")"

[ -d node_modules ] || npm install --no-audit --no-fund
exec npm run dev
