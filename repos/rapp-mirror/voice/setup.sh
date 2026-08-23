#!/usr/bin/env bash
# One-time setup for the VibeVoice voice service.
# Installs into ~/.rapp-mirror (machine-level, shared by every clone):
#   ~/.rapp-mirror/VibeVoice  — microsoft/VibeVoice clone (code + voice presets)
#   ~/.rapp-mirror/venv       — python venv with the [streamingtts] extras
# The ~0.5B model weights download from Hugging Face on first synthesis.
set -euo pipefail

HOME_DIR="${RAPP_MIRROR_HOME:-$HOME/.rapp-mirror}"
mkdir -p "$HOME_DIR"
cd "$HOME_DIR"

if [ ! -d VibeVoice ]; then
  echo "▸ cloning microsoft/VibeVoice…"
  git clone --depth 1 https://github.com/microsoft/VibeVoice.git
fi

if [ ! -x venv/bin/python ]; then
  echo "▸ creating venv…"
  python3 -m venv venv
  ./venv/bin/pip install --upgrade pip -q
fi

echo "▸ installing VibeVoice [streamingtts] (torch etc. — a few GB, one time)…"
./venv/bin/pip install -q -e "./VibeVoice[streamingtts]"

echo "✓ voice setup complete."
echo "  start it with:  $HOME_DIR/venv/bin/python voice/server.py"
