#!/usr/bin/env bash
set -euo pipefail
umask 077

fail() {
    printf 'RAPP Brainstem bootstrap failed: %s\n' "$*" >&2
    exit 1
}

hash_file() {
    local path="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$path" | awk '{print tolower($1)}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$path" | awk '{print tolower($1)}'
    elif command -v openssl >/dev/null 2>&1; then
        openssl dgst -sha256 "$path" | sed 's/^.*= //' | tr '[:upper:]' '[:lower:]'
    else
        fail "no SHA-256 utility is available"
    fi
}

assert_regular_file() {
    if [ ! -f "$1" ] || [ -L "$1" ]; then
        fail "trusted local file is missing or is a symlink: $1"
    fi
}

assert_hash() {
    local path="$1" expected="$2" actual
    assert_regular_file "$path"
    actual="$(hash_file "$path")"
    if [ "$actual" != "$expected" ]; then
        fail "trusted local file hash mismatch: $path"
    fi
}

ensure_real_directory() {
    mkdir -p "$1"
    if [ ! -d "$1" ] || [ -L "$1" ]; then
        fail "refusing non-directory or symlink path: $1"
    fi
}

process_creation_identity() {
    local pid="$1" fields value
    if [ -r "/proc/$pid/stat" ]; then
        fields="$(sed -E 's/^[0-9]+ \(.*\) //' "/proc/$pid/stat" 2>/dev/null || true)"
        value="$(printf '%s\n' "$fields" | awk '{print $20}')"
        [ -n "$value" ] || return 1
        printf 'proc-starttime:%s' "$value"
        return 0
    fi
    value="$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || true)"
    [ -n "$value" ] || return 1
    printf 'ps-lstart:%s' "$value"
}

lock_field() {
    local path="$1" name="$2"
    sed -n "s/^${name}=//p" "$path"
}

acquire_bootstrap_lock() {
    local candidate owner_creation owner_nonce current_hash
    local owner_pid recorded_creation recorded_nonce current_creation
    candidate="$BOOTSTRAP_STATE_HOME/.bootstrap-lock-owner.$$"
    owner_creation="$(process_creation_identity "$$")" \
        || fail "cannot establish bootstrap process creation identity"
    owner_nonce="$$-${RANDOM:-0}-$CREATED_UTC"
    cat >"$candidate" <<EOF
schema=rapp-brainstem-bootstrap-lock/1
pid=$$
creation_identity=$owner_creation
nonce=$owner_nonce
EOF
    chmod 600 "$candidate"
    BOOTSTRAP_LOCK_OWNER_HASH="$(hash_file "$candidate")"
    if ln "$candidate" "$BOOTSTRAP_LOCK_PATH" 2>/dev/null; then
        rm -f -- "$candidate"
        BOOTSTRAP_LOCK_HELD=1
        return 0
    fi
    rm -f -- "$candidate"
    assert_regular_file "$BOOTSTRAP_LOCK_PATH"
    current_hash="$(hash_file "$BOOTSTRAP_LOCK_PATH")"
    [ "$(lock_field "$BOOTSTRAP_LOCK_PATH" schema)" = "rapp-brainstem-bootstrap-lock/1" ] \
        || fail "bootstrap lock is unreadable; refusing unsafe recovery"
    owner_pid="$(lock_field "$BOOTSTRAP_LOCK_PATH" pid)"
    recorded_creation="$(lock_field "$BOOTSTRAP_LOCK_PATH" creation_identity)"
    recorded_nonce="$(lock_field "$BOOTSTRAP_LOCK_PATH" nonce)"
    case "$owner_pid" in
        ""|*[!0-9]*) fail "bootstrap lock has an invalid PID" ;;
    esac
    [ -n "$recorded_creation" ] \
        || fail "bootstrap lock has no process creation identity"
    [ -n "$recorded_nonce" ] || fail "bootstrap lock has no nonce"
    current_creation="$(process_creation_identity "$owner_pid" 2>/dev/null || true)"
    if [ -n "$current_creation" ] && [ "$current_creation" = "$recorded_creation" ]; then
        fail "another RAPP Brainstem bootstrap is active"
    fi
    if [ -z "$current_creation" ] && kill -0 "$owner_pid" 2>/dev/null; then
        fail "bootstrap lock owner cannot be inspected safely"
    fi
    assert_hash "$BOOTSTRAP_LOCK_PATH" "$current_hash"
    rm -f -- "$BOOTSTRAP_LOCK_PATH"
    cat >"$candidate" <<EOF
schema=rapp-brainstem-bootstrap-lock/1
pid=$$
creation_identity=$owner_creation
nonce=$owner_nonce
EOF
    chmod 600 "$candidate"
    BOOTSTRAP_LOCK_OWNER_HASH="$(hash_file "$candidate")"
    ln "$candidate" "$BOOTSTRAP_LOCK_PATH" 2>/dev/null \
        || fail "another RAPP Brainstem bootstrap won the recovered lock"
    rm -f -- "$candidate"
    BOOTSTRAP_LOCK_HELD=1
}

release_bootstrap_lock() {
    local actual
    [ "${BOOTSTRAP_LOCK_HELD:-0}" = "1" ] || return 0
    [ -f "$BOOTSTRAP_LOCK_PATH" ] && [ ! -L "$BOOTSTRAP_LOCK_PATH" ] \
        || return 1
    actual="$(hash_file "$BOOTSTRAP_LOCK_PATH")" || return 1
    [ "$actual" = "$BOOTSTRAP_LOCK_OWNER_HASH" ] || return 1
    rm -f -- "$BOOTSTRAP_LOCK_PATH"
    BOOTSTRAP_LOCK_HELD=0
}

ACTOR="github-copilot"
while [ "$#" -gt 0 ]; do
    case "$1" in
        --actor)
            [ "$#" -ge 2 ] || fail "--actor requires a value"
            ACTOR="$2"
            shift 2
            ;;
        *)
            fail "unsupported argument: $1"
            ;;
    esac
done
case "$ACTOR" in
    ""|*[!A-Za-z0-9._-]*) fail "actor contains unsupported characters" ;;
esac
[ "${#ACTOR}" -le 128 ] || fail "actor is too long"

for command_name in bash curl awk sed tr mv mkdir chmod date uname dirname pwd cat rm ln ps; do
    command -v "$command_name" >/dev/null 2>&1 || fail "required system command is unavailable: $command_name"
done

case "$(uname -s 2>/dev/null || true)" in
    Darwin|Linux) ;;
    *) fail "scripts/bootstrap.sh supports only macOS and Linux" ;;
esac

[ -n "${HOME:-}" ] || fail "HOME is not set"
case "$HOME" in
    /*) ;;
    *) fail "HOME must be an absolute path" ;;
esac

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)"
PLUGIN_ROOT="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd -P)"
LOCK_PATH="$PLUGIN_ROOT/installer-lock.json"
BOOTSTRAP_STATE_HOME="$HOME/.rapp/brainstem-bootstrap"
ENVELOPE_DIR="$BOOTSTRAP_STATE_HOME/envelopes"
DOWNLOAD_DIR="$BOOTSTRAP_STATE_HOME/downloads"
FAILED_DIR="$BOOTSTRAP_STATE_HOME/failed"
BOOTSTRAP_LOCK_PATH="$BOOTSTRAP_STATE_HOME/.bootstrap.lock"
BRAINSTEM_HOME="$HOME/.brainstem"
export BRAINSTEM_HOME

assert_hash "$LOCK_PATH" e699ad5978cb91b7014011392c3e0619169e239d3418b9e8bdc2098588badf55
assert_hash "$PLUGIN_ROOT/rapp_operator/__init__.py" 4da21ba688c0d6306dddc09f0db442993139b6906e0732b6ed48da184546aba3
assert_hash "$PLUGIN_ROOT/rapp_operator/rapp1.py" c3a30e448eb7b9ebfa7cca3b5b1e8cfa67486a0f78de8add7efb330b7efa9779
assert_hash "$PLUGIN_ROOT/rapp_operator/rappctl.py" c6cea66c4e695f844b187ef4568a9cd0b5dc65909a4557d398165cbb52b36115

[ ! -e "$BRAINSTEM_HOME" ] || fail "$BRAINSTEM_HOME already exists; fresh bootstrap refuses existing state"
if curl --fail --silent --show-error --max-time 2 \
    "http://127.0.0.1:7071/health/public" >/dev/null 2>&1; then
    fail "a RAPP Brainstem is already reachable"
fi

ensure_real_directory "$HOME/.rapp"
ensure_real_directory "$BOOTSTRAP_STATE_HOME"
ensure_real_directory "$ENVELOPE_DIR"
ensure_real_directory "$DOWNLOAD_DIR"
ensure_real_directory "$FAILED_DIR"
chmod 700 "$BOOTSTRAP_STATE_HOME" "$ENVELOPE_DIR" "$DOWNLOAD_DIR" "$FAILED_DIR"

CREATED_UTC="$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')"
FAILURE_ID="$(date -u '+%Y%m%dT%H%M%SZ')-$$"
ENVELOPE_TEMP="$ENVELOPE_DIR/.bootstrap-envelope.$$"
INSTALLER_PATH=""
WORK_DIR=""
BOOTSTRAP_LOCK_HELD=0
BOOTSTRAP_LOCK_OWNER_HASH=""
MUTATION_STARTED=0
recover_failed_bootstrap() {
    local quarantine
    [ "$MUTATION_STARTED" = "1" ] || return 0
    [ -e "$BRAINSTEM_HOME" ] || return 0
    quarantine="$FAILED_DIR/$FAILURE_ID-${ENVELOPE_SHA256:-no-envelope}"
    if mv "$BRAINSTEM_HOME" "$quarantine" 2>/dev/null; then
        chmod -R go-rwx "$quarantine" 2>/dev/null || true
        printf 'RAPP Brainstem partial bootstrap quarantined at %s\n' "$quarantine" >&2
        return 0
    fi
    rm -rf -- "$BRAINSTEM_HOME"
    [ ! -e "$BRAINSTEM_HOME" ] \
        || printf 'RAPP Brainstem bootstrap recovery could not restore the absent state\n' >&2
}
cleanup() {
    local status=$?
    [ -z "${ENVELOPE_TEMP:-}" ] || rm -f -- "$ENVELOPE_TEMP"
    [ -z "${INSTALLER_PATH:-}" ] || rm -f -- "$INSTALLER_PATH"
    [ -z "${WORK_DIR:-}" ] || rm -rf -- "$WORK_DIR"
    if ! release_bootstrap_lock; then
        printf 'RAPP Brainstem bootstrap lock changed; refusing to remove it\n' >&2
        status=1
    fi
    [ "$status" -eq 0 ] || recover_failed_bootstrap
    trap - EXIT
    exit "$status"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

acquire_bootstrap_lock
[ ! -e "$BRAINSTEM_HOME" ] || fail "RAPP Brainstem state appeared before planning"

cat >"$ENVELOPE_TEMP" <<EOF
{
  "action": "bootstrap",
  "actor": "$ACTOR",
  "bootstrap_state_home": "~/.rapp/brainstem-bootstrap",
  "created_utc": "$CREATED_UTC",
  "installer": {
    "arguments": [
      "--no-launch",
      "--version",
      "installers"
    ],
    "platform": "macos-linux",
    "repository_ref": {
      "kind": "rolling-tag",
      "value": "installers"
    },
    "sha256": "1b65de71288b203a8ab6b6f10db3402a3ec1f42889eb3eee6036b7f061c695e2",
    "url": "https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/install.sh"
  },
  "installer_lock": {
    "schema": "rapp-brainstem-installer-lock/3",
    "sha256": "e699ad5978cb91b7014011392c3e0619169e239d3418b9e8bdc2098588badf55"
  },
  "operator_bundle": {
    "files": [
      {
        "name": "__init__.py",
        "sha256": "4da21ba688c0d6306dddc09f0db442993139b6906e0732b6ed48da184546aba3"
      },
      {
        "name": "rapp1.py",
        "sha256": "c3a30e448eb7b9ebfa7cca3b5b1e8cfa67486a0f78de8add7efb330b7efa9779"
      },
      {
        "name": "rappctl.py",
        "sha256": "c6cea66c4e695f844b187ef4568a9cd0b5dc65909a4557d398165cbb52b36115"
      }
    ],
    "schema": "rapp-brainstem-operator-bundle/1",
    "sha256": "d007f602e1429f04aa60bd40bb63ba6756a1f1fc684fd8b8f469bd393dcb8e77"
  },
  "postconditions": {
    "brainstem_release": "exact-target",
    "live_verification": "required-separately",
    "managed_runtime": "stopped"
  },
  "preconditions": {
    "brainstem_release": "absent",
    "managed_runtime": "stopped",
    "protected_user_state": "absent"
  },
  "schema": "rapp-brainstem-bootstrap-envelope/2",
  "target_release": {
    "commit": "c60521e2cacbcbfa585a118c1275093d7bb15b74",
    "repository": "https://github.com/microsoft/aibast-agents-library.git",
    "tag": "installers",
    "tree": "3c5bb0d55ca4a5aff8872d30b8108e2438ef808d",
    "version": "0.6.16",
    "version_url": "https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/rapp_brainstem/VERSION"
  },
  "trust_anchor": {
    "authority": "executing-plugin-bundle",
    "kind": "local-marketplace-plugin",
    "plugin": "rapp-brainstem"
  }
}
EOF
ENVELOPE_SHA256="$(hash_file "$ENVELOPE_TEMP")"
ENVELOPE_PATH="$ENVELOPE_DIR/$ENVELOPE_SHA256.json"
if [ -e "$ENVELOPE_PATH" ]; then
    assert_hash "$ENVELOPE_PATH" "$ENVELOPE_SHA256"
    rm -f -- "$ENVELOPE_TEMP"
else
    mv "$ENVELOPE_TEMP" "$ENVELOPE_PATH"
fi
ENVELOPE_TEMP=""

[ ! -e "$BRAINSTEM_HOME" ] || fail "RAPP Brainstem state appeared after planning"
INSTALLER_PATH="$DOWNLOAD_DIR/installer-$ENVELOPE_SHA256-$$.sh"
curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location \
    --output "$INSTALLER_PATH" https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/install.sh
chmod 700 "$INSTALLER_PATH"
assert_hash "$INSTALLER_PATH" 1b65de71288b203a8ab6b6f10db3402a3ec1f42889eb3eee6036b7f061c695e2

WORK_DIR="$BOOTSTRAP_STATE_HOME/work/$ENVELOPE_SHA256-$$"
ensure_real_directory "$BOOTSTRAP_STATE_HOME/work"
ensure_real_directory "$WORK_DIR"
export TMPDIR="$WORK_DIR"
export TMP="$WORK_DIR"
export TEMP="$WORK_DIR"
export BRAINSTEM_REPO_URL=https://github.com/microsoft/aibast-agents-library.git
export BRAINSTEM_REPO_REF=installers
export BRAINSTEM_VERSION_URL=https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/rapp_brainstem/VERSION

MUTATION_STARTED=1
bash "$INSTALLER_PATH" --no-launch --version installers

BRAINSTEM_PYTHON="$BRAINSTEM_HOME/venv/bin/python"
[ -x "$BRAINSTEM_PYTHON" ] || fail "the installed RAPP Brainstem Python is missing"

"$BRAINSTEM_PYTHON" "$PLUGIN_ROOT/rapp_operator/rappctl.py" \
    reconcile \
    --actor "$ACTOR" \
    --envelope "$ENVELOPE_PATH" \
    --envelope-sha256 "$ENVELOPE_SHA256"

printf 'RAPP Brainstem installed and reconciled. Live /chat verification is still required.\n' >&2
