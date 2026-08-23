#!/usr/bin/env bash
# One-click hearing for the mirror: whisper.cpp + an English model.
#   - binary via Homebrew (whisper-cpp provides whisper-server)
#   - model -> ~/.rapp-mirror/whisper/ggml-small.en.bin (~466 MB, one time)
# The app starts/stops whisper-server itself once these exist.
set -euo pipefail

HOME_DIR="${RAPP_MIRROR_HOME:-$HOME/.rapp-mirror}"
MODEL_DIR="$HOME_DIR/whisper"
MODEL="$MODEL_DIR/ggml-small.en.bin"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required (https://brew.sh) — install it, then click again."
  exit 1
fi

if ! command -v whisper-server >/dev/null 2>&1 && ! [ -x /opt/homebrew/bin/whisper-server ]; then
  echo "▸ installing whisper-cpp via Homebrew…"
  brew install whisper-cpp
else
  echo "▸ whisper-cpp already installed"
fi

mkdir -p "$MODEL_DIR"
if [ ! -f "$MODEL" ]; then
  echo "▸ downloading the small.en model (~466 MB, one time)…"
  curl -fL --progress-bar -o "$MODEL.part" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin"
  mv "$MODEL.part" "$MODEL"
else
  echo "▸ model already present"
fi

echo "✓ hearing installed — the mirror starts whisper-server itself."
