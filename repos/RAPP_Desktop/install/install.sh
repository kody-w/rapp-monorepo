#!/usr/bin/env bash
set -euo pipefail

RAPP_HOME="$HOME/.rapp"
RAPP_INSTALL_DIR="$RAPP_HOME/app"
MINIMUM_NODE_VERSION="22.12.0"

log() { printf '[RAPP] %s\n' "$1"; }
fail() { printf '[RAPP] ERROR: %s\n' "$1" >&2; exit 1; }

verify_macos_app() {
  local app_path="$1"
  local signing_info
  [ -d "$app_path" ] || fail "The macOS application bundle was not produced."
  for command in codesign xcrun spctl; do
    command -v "$command" >/dev/null 2>&1 \
      || fail "$command is required to verify the macOS application."
  done
  signing_info="$(codesign --display --verbose=4 "$app_path" 2>&1)" \
    || fail "The macOS application has no valid code signature."
  printf '%s\n' "$signing_info" | grep -q '^Authority=Developer ID Application:' \
    || fail "The macOS application is not signed with a Developer ID Application certificate."
  codesign --verify --deep --strict --verbose=2 "$app_path" \
    || fail "The macOS application signature is invalid."
  xcrun stapler validate "$app_path" \
    || fail "The macOS application has no valid stapled notarization ticket."
  spctl --assess --type execute --verbose=4 "$app_path" \
    || fail "Gatekeeper rejected the macOS application."
}

if [ "${1:-}" = "--verify-macos-bundle" ]; then
  [ "$#" -eq 2 ] || fail "Usage: install.sh --verify-macos-bundle <path-to-app>"
  verify_macos_app "$2"
  log "Developer ID, notarization, and Gatekeeper assessments passed."
  exit 0
fi

case "$(uname -s)" in
  Darwin*) OS="macos" ;;
  Linux*) OS="linux" ;;
  *) fail "RAPP Desktop supports macOS and Linux." ;;
esac

require_supported_node() {
  node -e '
    const [major, minor] = process.versions.node.split(".").map(Number)
    process.exit(major > 22 || (major === 22 && minor >= 12) ? 0 : 1)
  ' || fail "Node.js $MINIMUM_NODE_VERSION or newer is required."
}

install_node() {
  if command -v node >/dev/null 2>&1; then
    require_supported_node
    return
  fi
  log "Installing Node.js LTS..."
  if [ "$OS" = "macos" ] && command -v brew >/dev/null 2>&1; then
    brew install node
    require_supported_node
    return
  fi
  export NVM_DIR="$HOME/.nvm"
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
  # shellcheck source=/dev/null
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  nvm install "$MINIMUM_NODE_VERSION"
  require_supported_node
}

for command in git python3; do
  command -v "$command" >/dev/null 2>&1 || fail "$command is required."
done
install_node

mkdir -p "$RAPP_HOME"
if [ -d "$RAPP_INSTALL_DIR/.git" ]; then
  log "Updating RAPP Desktop..."
  git -C "$RAPP_INSTALL_DIR" pull --ff-only origin main
else
  log "Cloning RAPP Desktop..."
  git clone https://github.com/kody-w/RAPP_Desktop.git "$RAPP_INSTALL_DIR"
fi

log "Building the Electron companion..."
cd "$RAPP_INSTALL_DIR"
npm ci
npm run dist

if [ "$OS" = "macos" ]; then
  APP_PATH="$(find "$RAPP_INSTALL_DIR/release" -maxdepth 3 -type d -name 'RAPP Desktop.app' -print -quit)"
  [ -n "$APP_PATH" ] || fail "The macOS application bundle was not produced."
  log "Verifying Developer ID signature, notarization ticket, and Gatekeeper acceptance..."
  verify_macos_app "$APP_PATH"
fi

log "Preparing the bundled Brainstem fallback..."
python3 -m venv "$RAPP_HOME/venv"
"$RAPP_HOME/venv/bin/python" -m pip install --quiet --upgrade pip
"$RAPP_HOME/venv/bin/python" -m pip install --quiet -r rapp_os/requirements.txt

mkdir -p \
  "$RAPP_HOME/agents" \
  "$RAPP_HOME/skills" \
  "$RAPP_HOME/projects" \
  "$RAPP_HOME/contexts" \
  "$RAPP_HOME/memory"

cat > "$RAPP_HOME/rapp" <<EOF
#!/usr/bin/env bash
exec "$RAPP_HOME/venv/bin/python" "$RAPP_INSTALL_DIR/rapp_os/rapp_os.py" "\$@"
EOF
chmod +x "$RAPP_HOME/rapp"

if [ "$OS" = "macos" ]; then
  mkdir -p "$HOME/Applications"
  rm -rf "$HOME/Applications/RAPP Desktop.app"
  cp -R "$APP_PATH" "$HOME/Applications/RAPP Desktop.app"
  log "Installed RAPP Desktop in $HOME/Applications."
  open "$HOME/Applications/RAPP Desktop.app"
else
  APPIMAGE="$(find "$RAPP_INSTALL_DIR/release" -maxdepth 2 -type f -name '*.AppImage' -print -quit)"
  [ -n "$APPIMAGE" ] || fail "The Linux AppImage was not produced."
  mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
  cp "$APPIMAGE" "$HOME/.local/bin/rapp-desktop"
  chmod +x "$HOME/.local/bin/rapp-desktop"
  cat > "$HOME/.local/share/applications/rapp-desktop.desktop" <<EOF
[Desktop Entry]
Name=RAPP Desktop
Comment=Local-first RAPP AI companion
Exec=$HOME/.local/bin/rapp-desktop
Terminal=false
Type=Application
Categories=Utility;Development;
EOF
  log "Installed RAPP Desktop in $HOME/.local/bin."
fi

log "RAPP Desktop is ready."
