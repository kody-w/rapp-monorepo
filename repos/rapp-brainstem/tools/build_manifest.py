#!/usr/bin/env python3
"""Build the public contract and zero-prerequisite bootstrap scripts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "rapp-operator.json"
LOCK = ROOT / "installer-lock.json"
BOOTSTRAP_SH = ROOT / "scripts/bootstrap.sh"
BOOTSTRAP_PS1 = ROOT / "scripts/bootstrap.ps1"
PAGES = "https://kody-w.github.io/rapp-brainstem"
LOCK_SCHEMA = "rapp-brainstem-installer-lock/3"
ENVELOPE_SCHEMA = "rapp-brainstem-bootstrap-envelope/2"
BOOTSTRAP_STATE_HOME = "~/.rapp/brainstem-bootstrap"
OPERATOR_PATHS = (
    "rapp_operator/__init__.py",
    "rapp_operator/rapp1.py",
    "rapp_operator/rappctl.py",
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_lock() -> tuple[dict, bytes]:
    payload = LOCK.read_bytes()
    lock = json.loads(payload.decode("utf-8"))
    if lock.get("schema") != LOCK_SCHEMA:
        raise ValueError("unsupported installer lock schema")
    return lock, payload


def operator_bundle() -> dict:
    files = []
    for path in OPERATOR_PATHS:
        payload = (ROOT / path).read_bytes()
        files.append(
            {
                "name": Path(path).name,
                "sha256": sha256(payload),
            }
        )
    base = {
        "schema": "rapp-brainstem-operator-bundle/1",
        "files": files,
    }
    canonical = json.dumps(
        base,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        **base,
        "sha256": sha256(b"rapp/operator-bundle/1\n" + canonical),
    }


def envelope_value(
    lock: dict,
    lock_digest: str,
    bundle: dict,
    platform_id: str,
    actor: str,
    created_utc: str,
) -> dict:
    artifact = lock["artifacts"][platform_id]
    return {
        "action": "bootstrap",
        "actor": actor,
        "bootstrap_state_home": BOOTSTRAP_STATE_HOME,
        "created_utc": created_utc,
        "installer": {
            "arguments": list(
                lock["bootstrap"]["required_installer_arguments"]
            ),
            "platform": platform_id,
            "repository_ref": {
                "kind": "rolling-tag",
                "value": lock["target"]["tag"],
            },
            "sha256": artifact["sha256"],
            "url": artifact["url"],
        },
        "installer_lock": {
            "schema": LOCK_SCHEMA,
            "sha256": lock_digest,
        },
        "operator_bundle": bundle,
        "postconditions": {
            "brainstem_release": "exact-target",
            "live_verification": "required-separately",
            "managed_runtime": "stopped",
        },
        "preconditions": {
            "brainstem_release": "absent",
            "managed_runtime": "stopped",
            "protected_user_state": "absent",
        },
        "schema": ENVELOPE_SCHEMA,
        "target_release": lock["target"],
        "trust_anchor": {
            "authority": "executing-plugin-bundle",
            "kind": "local-marketplace-plugin",
            "plugin": "rapp-brainstem",
        },
    }


def render_bootstrap_sh(
    lock: dict,
    lock_payload: bytes,
    bundle: dict,
) -> bytes:
    lock_digest = sha256(lock_payload)
    target = lock["target"]
    artifact = lock["artifacts"]["macos-linux"]
    envelope = json.dumps(
        envelope_value(
            lock,
            lock_digest,
            bundle,
            "macos-linux",
            "__RAPP_ACTOR__",
            "__RAPP_CREATED_UTC__",
        ),
        indent=2,
        sort_keys=True,
    )
    envelope = envelope.replace(
        '"__RAPP_ACTOR__"',
        '"$ACTOR"',
    ).replace(
        '"__RAPP_CREATED_UTC__"',
        '"$CREATED_UTC"',
    )
    expected_hashes = "\n".join(
        (
            f"assert_hash \"$PLUGIN_ROOT/{path}\" "
            f"{shlex.quote(entry['sha256'])}"
        )
        for path, entry in zip(OPERATOR_PATHS, bundle["files"], strict=True)
    )
    template = r"""#!/usr/bin/env bash
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

assert_hash "$LOCK_PATH" @LOCK_DIGEST@
@EXPECTED_OPERATOR_HASHES@

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
@ENVELOPE_JSON@
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
    --output "$INSTALLER_PATH" @INSTALLER_URL@
chmod 700 "$INSTALLER_PATH"
assert_hash "$INSTALLER_PATH" @INSTALLER_SHA256@

WORK_DIR="$BOOTSTRAP_STATE_HOME/work/$ENVELOPE_SHA256-$$"
ensure_real_directory "$BOOTSTRAP_STATE_HOME/work"
ensure_real_directory "$WORK_DIR"
export TMPDIR="$WORK_DIR"
export TMP="$WORK_DIR"
export TEMP="$WORK_DIR"
export BRAINSTEM_REPO_URL=@REPOSITORY@
export BRAINSTEM_REPO_REF=@TARGET_TAG@
export BRAINSTEM_VERSION_URL=@VERSION_URL@

MUTATION_STARTED=1
bash "$INSTALLER_PATH" --no-launch --version @TARGET_TAG@

BRAINSTEM_PYTHON="$BRAINSTEM_HOME/venv/bin/python"
[ -x "$BRAINSTEM_PYTHON" ] || fail "the installed RAPP Brainstem Python is missing"

"$BRAINSTEM_PYTHON" "$PLUGIN_ROOT/rapp_operator/rappctl.py" \
    reconcile \
    --actor "$ACTOR" \
    --envelope "$ENVELOPE_PATH" \
    --envelope-sha256 "$ENVELOPE_SHA256"

printf 'RAPP Brainstem installed and reconciled. Live /chat verification is still required.\n' >&2
"""
    replacements = {
        "@LOCK_DIGEST@": shlex.quote(lock_digest),
        "@EXPECTED_OPERATOR_HASHES@": expected_hashes,
        "@ENVELOPE_JSON@": envelope,
        "@INSTALLER_URL@": shlex.quote(artifact["url"]),
        "@INSTALLER_SHA256@": shlex.quote(artifact["sha256"]),
        "@REPOSITORY@": shlex.quote(target["repository"]),
        "@TARGET_TAG@": shlex.quote(target["tag"]),
        "@VERSION_URL@": shlex.quote(target["version_url"]),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    if re.search(r"@[A-Z][A-Z_]+@", template):
        raise ValueError("unresolved macOS/Linux bootstrap template marker")
    return template.encode("utf-8")


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_bootstrap_ps1(
    lock: dict,
    lock_payload: bytes,
    bundle: dict,
) -> bytes:
    lock_digest = sha256(lock_payload)
    target = lock["target"]
    artifact = lock["artifacts"]["windows"]
    envelope = json.dumps(
        envelope_value(
            lock,
            lock_digest,
            bundle,
            "windows",
            "__RAPP_ACTOR__",
            "__RAPP_CREATED_UTC__",
        ),
        indent=2,
        sort_keys=True,
    )
    envelope = envelope.replace(
        '"__RAPP_ACTOR__"',
        '"$Actor"',
    ).replace(
        '"__RAPP_CREATED_UTC__"',
        '"$CreatedUtc"',
    )
    source_checks = "\n".join(
        (
            f"Assert-Hash (Join-Path $PluginRoot {ps_quote(path)}) "
            f"{ps_quote(entry['sha256'])}"
        )
        for path, entry in zip(OPERATOR_PATHS, bundle["files"], strict=True)
    )
    template = r"""[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')]
    [string]$Actor = 'github-copilot'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
    [Net.ServicePointManager]::SecurityProtocol = `
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {}

function Fail([string]$Message) {
    throw "RAPP Brainstem bootstrap failed: $Message"
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-RegularFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "trusted local file is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Fail "trusted local file is a reparse point: $Path"
    }
}

function Assert-Hash([string]$Path, [string]$Expected) {
    Assert-RegularFile $Path
    if ((Get-Sha256 $Path) -ne $Expected) {
        Fail "trusted local file hash mismatch: $Path"
    }
}

function Ensure-RealDirectory([string]$Path) {
    [void](New-Item -ItemType Directory -Path $Path -Force)
    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        Fail "refusing non-directory or reparse-point path: $Path"
    }
}

function Protect-PrivateDirectory([string]$Path) {
    try {
        $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
        $security = New-Object Security.AccessControl.DirectorySecurity
        $security.SetAccessRuleProtection($true, $false)
        $rule = New-Object -TypeName Security.AccessControl.FileSystemAccessRule `
            -ArgumentList @(
                $sid,
                [Security.AccessControl.FileSystemRights]::FullControl,
                [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit',
                [Security.AccessControl.PropagationFlags]::None,
                [Security.AccessControl.AccessControlType]::Allow
            )
        [void]$security.AddAccessRule($rule)
        Set-Acl -LiteralPath $Path -AclObject $security
    } catch {
        Fail "could not make bootstrap state private: $Path"
    }
}

function Write-Utf8NoBom([string]$Path, [string]$Value) {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($Path, $Value, $encoding)
}

function Get-ProcessCreationIdentity([int]$ProcessId) {
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Exists = $false; Identity = $null }
    }
    try {
        $ticks = $process.StartTime.ToUniversalTime().Ticks
        return [pscustomobject]@{
            Exists = $true
            Identity = "windows-start-ticks:$ticks"
        }
    } catch {
        return [pscustomobject]@{ Exists = $true; Identity = $null }
    }
}

function Acquire-BootstrapLock([string]$Path, [string]$StateHome) {
    $owner = Get-ProcessCreationIdentity $PID
    if (-not $owner.Exists -or -not $owner.Identity) {
        Fail 'cannot establish bootstrap process creation identity'
    }
    $record = [ordered]@{
        schema = 'rapp-brainstem-bootstrap-lock/1'
        pid = $PID
        creation_identity = $owner.Identity
        nonce = [Guid]::NewGuid().ToString('N')
    }
    $candidate = Join-Path $StateHome ".bootstrap-lock-owner-$PID-$($record.nonce)"
    Write-Utf8NoBom $candidate (($record | ConvertTo-Json -Compress) + "`n")
    $script:BootstrapLockOwnerHash = Get-Sha256 $candidate
    try {
        [IO.File]::Move($candidate, $Path)
        $script:BootstrapLockHeld = $true
        return
    } catch [IO.IOException] {
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is not a regular file'
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is a reparse point'
    }
    $currentHash = Get-Sha256 $Path
    try {
        $current = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is unreadable; refusing unsafe recovery'
    }
    $propertyNames = @(
        $current.PSObject.Properties.Name | Sort-Object
    )
    if (
        ($propertyNames -join ',') -ne 'creation_identity,nonce,pid,schema' -or
        $current.schema -ne 'rapp-brainstem-bootstrap-lock/1' -or
        -not (
            $current.pid -is [int] -or
            $current.pid -is [long]
        ) -or
        [string]::IsNullOrWhiteSpace([string]$current.creation_identity) -or
        [string]::IsNullOrWhiteSpace([string]$current.nonce)
    ) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock record is invalid'
    }
    $snapshot = Get-ProcessCreationIdentity ([int]$current.pid)
    if ($snapshot.Exists -and -not $snapshot.Identity) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock owner cannot be inspected safely'
    }
    if (
        $snapshot.Exists -and
        $snapshot.Identity -eq [string]$current.creation_identity
    ) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'another RAPP Brainstem bootstrap is active'
    }
    Assert-Hash $Path $currentHash
    Remove-Item -LiteralPath $Path -Force
    try {
        [IO.File]::Move($candidate, $Path)
    } catch {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'another RAPP Brainstem bootstrap won the recovered lock'
    }
    $script:BootstrapLockHeld = $true
}

function Release-BootstrapLock([string]$Path) {
    if (-not $script:BootstrapLockHeld) { return }
    Assert-Hash $Path $script:BootstrapLockOwnerHash
    Remove-Item -LiteralPath $Path -Force
    $script:BootstrapLockHeld = $false
}

$ScriptDirectory = $PSScriptRoot
$PluginRoot = Split-Path -Parent $ScriptDirectory
$LockPath = Join-Path $PluginRoot 'installer-lock.json'
if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    Fail 'USERPROFILE is not set'
}
$UserHome = $env:USERPROFILE
$BootstrapStateHome = Join-Path $UserHome '.rapp/brainstem-bootstrap'
$EnvelopeDirectory = Join-Path $BootstrapStateHome 'envelopes'
$DownloadDirectory = Join-Path $BootstrapStateHome 'downloads'
$FailedDirectory = Join-Path $BootstrapStateHome 'failed'
$BrainstemHome = Join-Path $UserHome '.brainstem'

Assert-Hash $LockPath @LOCK_DIGEST@
@EXPECTED_OPERATOR_HASHES@

if (Test-Path -LiteralPath $BrainstemHome) {
    Fail "$BrainstemHome already exists; fresh bootstrap refuses existing state"
}
try {
    $health = Invoke-WebRequest -Uri 'http://127.0.0.1:7071/health/public' `
        -UseBasicParsing -TimeoutSec 2
    if ($health.StatusCode -eq 200) {
        Fail 'a RAPP Brainstem is already reachable'
    }
} catch {
    if ($_.Exception.Message -like 'RAPP Brainstem bootstrap failed:*') {
        throw
    }
}

Ensure-RealDirectory (Join-Path $UserHome '.rapp')
Ensure-RealDirectory $BootstrapStateHome
Ensure-RealDirectory $EnvelopeDirectory
Ensure-RealDirectory $DownloadDirectory
Ensure-RealDirectory $FailedDirectory
Protect-PrivateDirectory $BootstrapStateHome
Protect-PrivateDirectory $EnvelopeDirectory
Protect-PrivateDirectory $DownloadDirectory
Protect-PrivateDirectory $FailedDirectory

$CreatedUtc = [DateTime]::UtcNow.ToString(
    'yyyy-MM-ddTHH:mm:ss.fffZ',
    [Globalization.CultureInfo]::InvariantCulture
)

$EnvelopeTemporary = Join-Path $EnvelopeDirectory ".bootstrap-envelope.$PID"
$EnvelopeSha256 = $null
$InstallerPath = $null
$WorkDirectory = $null
$BootstrapLock = Join-Path $BootstrapStateHome '.bootstrap.lock'
$script:BootstrapLockHeld = $false
$script:BootstrapLockOwnerHash = $null
$MutationStarted = $false
$BootstrapSucceeded = $false
$FailureId = [DateTime]::UtcNow.ToString(
    'yyyyMMddTHHmmssZ',
    [Globalization.CultureInfo]::InvariantCulture
) + "-$PID"
Acquire-BootstrapLock $BootstrapLock $BootstrapStateHome
try {
    if (Test-Path -LiteralPath $BrainstemHome) {
        Fail 'RAPP Brainstem state appeared before planning'
    }
    $EnvelopeJson = @"
@ENVELOPE_JSON@
"@
    Write-Utf8NoBom $EnvelopeTemporary $EnvelopeJson
    $EnvelopeSha256 = Get-Sha256 $EnvelopeTemporary
    $EnvelopePath = Join-Path $EnvelopeDirectory "$EnvelopeSha256.json"
    if (Test-Path -LiteralPath $EnvelopePath) {
        Assert-Hash $EnvelopePath $EnvelopeSha256
        Remove-Item -LiteralPath $EnvelopeTemporary -Force
    } else {
        Move-Item -LiteralPath $EnvelopeTemporary -Destination $EnvelopePath
    }
    $EnvelopeTemporary = $null

    if (Test-Path -LiteralPath $BrainstemHome) {
        Fail 'RAPP Brainstem state appeared after planning'
    }

    $InstallerPath = Join-Path $DownloadDirectory "installer-$EnvelopeSha256-$PID.ps1"
    Invoke-WebRequest -Uri @INSTALLER_URL@ -OutFile $InstallerPath `
        -UseBasicParsing -TimeoutSec 120
    Assert-Hash $InstallerPath @INSTALLER_SHA256@

    Ensure-RealDirectory (Join-Path $BootstrapStateHome 'work')
    $WorkDirectory = Join-Path $BootstrapStateHome "work/$EnvelopeSha256-$PID"
    Ensure-RealDirectory $WorkDirectory
    $env:TEMP = $WorkDirectory
    $env:TMP = $WorkDirectory
    $env:TMPDIR = $WorkDirectory
    $env:BRAINSTEM_REPO_URL = @REPOSITORY@
    $env:BRAINSTEM_REPO_REF = @TARGET_TAG@
    $env:BRAINSTEM_VERSION_URL = @VERSION_URL@
    $env:BRAINSTEM_HOME = $BrainstemHome

    $PowerShellExe = [Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
    $MutationStarted = $true
    & $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $InstallerPath `
        '--no-launch' '--version' @TARGET_TAG@
    if ($LASTEXITCODE -ne 0) {
        Fail "upstream installer exited with code $LASTEXITCODE"
    }

    $BrainstemPython = Join-Path $BrainstemHome 'venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $BrainstemPython -PathType Leaf)) {
        Fail 'the installed RAPP Brainstem Python is missing'
    }

    & $BrainstemPython (Join-Path $PluginRoot 'rapp_operator/rappctl.py') `
        'reconcile' '--actor' $Actor '--envelope' $EnvelopePath `
        '--envelope-sha256' $EnvelopeSha256
    if ($LASTEXITCODE -ne 0) {
        Fail "bootstrap reconciliation exited with code $LASTEXITCODE"
    }
    $BootstrapSucceeded = $true
    Write-Host 'RAPP Brainstem installed and reconciled. Live /chat verification is still required.'
} finally {
    $lockFailure = $null
    try {
        Release-BootstrapLock $BootstrapLock
    } catch {
        $BootstrapSucceeded = $false
        $lockFailure = $_
    }
    if ($EnvelopeTemporary -and (Test-Path -LiteralPath $EnvelopeTemporary)) {
        Remove-Item -LiteralPath $EnvelopeTemporary -Force -ErrorAction SilentlyContinue
    }
    if ($InstallerPath -and (Test-Path -LiteralPath $InstallerPath)) {
        Remove-Item -LiteralPath $InstallerPath -Force -ErrorAction SilentlyContinue
    }
    if ($WorkDirectory -and (Test-Path -LiteralPath $WorkDirectory)) {
        Remove-Item -LiteralPath $WorkDirectory -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (
        -not $BootstrapSucceeded -and
        $MutationStarted -and
        (Test-Path -LiteralPath $BrainstemHome)
    ) {
        $suffix = if ($EnvelopeSha256) { $EnvelopeSha256 } else { 'no-envelope' }
        $quarantine = Join-Path $FailedDirectory "$FailureId-$suffix"
        try {
            Move-Item -LiteralPath $BrainstemHome -Destination $quarantine -ErrorAction Stop
            Write-Warning "RAPP Brainstem partial bootstrap quarantined at $quarantine"
        } catch {
            Remove-Item -LiteralPath $BrainstemHome -Recurse -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $BrainstemHome) {
                Write-Error 'RAPP Brainstem bootstrap recovery could not restore the absent state'
            }
        }
    }
    if ($lockFailure) {
        throw $lockFailure
    }
}
"""
    replacements = {
        "@LOCK_DIGEST@": ps_quote(lock_digest),
        "@EXPECTED_OPERATOR_HASHES@": source_checks,
        "@ENVELOPE_JSON@": envelope,
        "@INSTALLER_SHA256@": ps_quote(artifact["sha256"]),
        "@INSTALLER_URL@": ps_quote(artifact["url"]),
        "@REPOSITORY@": ps_quote(target["repository"]),
        "@TARGET_TAG@": ps_quote(target["tag"]),
        "@VERSION_URL@": ps_quote(target["version_url"]),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    if re.search(r"@[A-Z][A-Z_]+@", template):
        raise ValueError("unresolved Windows bootstrap template marker")
    return template.encode("utf-8")


def local_artifact(path: str, payload: bytes | None = None) -> dict[str, str]:
    content = payload if payload is not None else (ROOT / path).read_bytes()
    return {
        "path": path,
        "url": f"{PAGES}/{path}",
        "sha256": sha256(content),
    }


def build_manifest() -> dict:
    lock, lock_payload = read_lock()
    bundle = operator_bundle()
    bootstrap_sh = render_bootstrap_sh(lock, lock_payload, bundle)
    bootstrap_ps1 = render_bootstrap_ps1(lock, lock_payload, bundle)
    copilot_prompt = (
        f"Open {PAGES}/ and give me my RAPP Brainstem. Own the complete "
        "setup, use the installed marketplace plugin as the local trust "
        "anchor, verify the real /chat path, and leave me only unavoidable "
        "sign-in or consent."
    )
    claude_prompt = (
        f"Open {PAGES}/ and give me my RAPP Brainstem using the Claude Code "
        "compatibility path. Follow the same RAPP/1 operator contract and "
        "verify the real /chat path."
    )
    return {
        "schema": "rapp-operator/1",
        "rapp_spec": "rapp/1",
        "product": {
            "name": "RAPP Brainstem",
            "operator": "AI-operated setup and lifecycle",
            "promise": "Teach your AI once. Keep the capability across assistants.",
            "entrypoint": f"{PAGES}/",
            "operating_model": (
                "The person steers their chosen AI; the AI performs the "
                "operational work."
            ),
        },
        "operators": {
            "golden_path": {
                "id": "github-copilot",
                "status": "golden",
                "prompt": copilot_prompt,
                "contract_url": f"{PAGES}/skills/rapp-brainstem/SKILL.md",
            },
            "compatibility": [
                {
                    "id": "claude-code",
                    "status": "compatibility",
                    "prompt": claude_prompt,
                    "contract_url": (
                        f"{PAGES}/skills/rapp-brainstem/CLAUDE.md"
                    ),
                }
            ],
        },
        "distribution": {
            "marketplace": {
                "source": "kody-w/rapp-brainstem",
                "name": "rapp",
                "plugin": "rapp-brainstem",
            },
            "github_copilot": {
                "install": [
                    "copilot plugin marketplace add kody-w/rapp-brainstem",
                    "copilot plugin install rapp-brainstem@rapp",
                ],
            },
            "claude_code": {
                "install": [
                    "claude plugin marketplace add kody-w/rapp-brainstem",
                    "claude plugin install rapp-brainstem@rapp",
                ],
            },
            "rule": (
                "The AI performs marketplace registration and plugin "
                "installation. Do not hand these commands to the user."
            ),
        },
        "artifacts": {
            "bootstrap": {
                "macos-linux": local_artifact(
                    "scripts/bootstrap.sh",
                    bootstrap_sh,
                ),
                "windows": local_artifact(
                    "scripts/bootstrap.ps1",
                    bootstrap_ps1,
                ),
            },
            "installers": lock["artifacts"],
            "reviewed_target": lock["target"],
            "operator": {
                "init": local_artifact("rapp_operator/__init__.py"),
                "rappctl": local_artifact("rapp_operator/rappctl.py"),
                "rapp1": local_artifact("rapp_operator/rapp1.py"),
                "installer_lock": local_artifact("installer-lock.json"),
            },
            "contracts": {
                "github-copilot": local_artifact(
                    "skills/rapp-brainstem/SKILL.md"
                ),
                "claude-code": local_artifact(
                    "skills/rapp-brainstem/CLAUDE.md"
                ),
            },
        },
        "bootstrap": {
            "state_home": BOOTSTRAP_STATE_HOME,
            "trust_anchor": (
                "The installed marketplace plugin and its bundled bootstrap "
                "script, operator files, and installer-lock.json on every use. "
                "No copied operator is lifecycle authority; the remote manifest "
                "is informational only."
            ),
            "plan_contract": {
                "schema": ENVELOPE_SCHEMA,
                "rule": (
                    "Persist an envelope binding actor, local lock digest, "
                    "exact installer, target release, and operator bundle "
                    "hashes before the upstream installer mutates the machine."
                ),
                "macos-linux": (
                    "scripts/bootstrap.sh --actor github-copilot"
                ),
                "windows": (
                    "scripts/bootstrap.ps1 -Actor github-copilot"
                ),
            },
            "sequence": [
                "resolve the bootstrap script inside the installed marketplace plugin",
                "verify the adjacent local installer lock and operator bundle",
                "persist the exact bootstrap envelope before Brainstem mutation",
                "download the commit-addressed upstream installer from the local lock",
                "verify the exact installer SHA-256 from the local lock",
                "run the unchanged installer with --no-launch and the currently verified rolling tag",
                "restore the absent ~/.brainstem state into private quarantine on any failed mutation",
                "use the newly installed Brainstem Python to run the current plugin operator and reconcile the exact envelope",
                "plan and apply start, then verify public health and a real POST /chat canary",
            ],
            "python": {
                "macos-linux": "~/.brainstem/venv/bin/python",
                "windows": "~/.brainstem/venv/Scripts/python.exe",
            },
            "reconcile_result": (
                "Installation evidence only; live verification remains pending "
                "until a later real POST /chat canary."
            ),
            "failure_recovery": (
                "Fresh setup records PID plus process creation identity in its "
                "lock and restores the pre-bootstrap absent state on failure."
            ),
        },
        "runtime": {
            "health_url": "http://127.0.0.1:7071/health/public",
            "chat_url": "http://127.0.0.1:7071/chat",
            "chat_request": {
                "user_input": "string",
                "conversation_history": "optional array",
                "session_id": "optional string",
            },
            "chat_response": {
                "response": "string",
                "agent_logs": "string",
                "session_id": "string",
            },
            "kernel_rule": (
                "The upstream Grail brainstem.py and one-liner remain the "
                "runtime authorities. The operator wraps them; it does not "
                "vendor, edit, or fork them."
            ),
            "environment": {
                "mode": "minimal-child-environment",
                "supported_overrides": list(
                    (
                        "PORT",
                        "SOUL_PATH",
                        "AGENTS_PATH",
                        "GITHUB_MODEL",
                        "BRAINSTEM_LAN_MODE",
                        "BRAINSTEM_ALLOWED_HOSTS",
                        "GITHUB_TOKEN",
                        "VOICE_MODE",
                        "VOICE_ZIP_PASSWORD",
                    )
                ),
                "binding": (
                    "Plans contain names, sources, presence, and value hashes "
                    "only; values are never written to plans or evidence."
                ),
            },
        },
        "lifecycle": {
            "transaction": "inspect -> plan -> locked apply -> live verify",
            "serialization": "one cross-process lifecycle operation at a time",
            "rollback": (
                "Restore the exact prior source, ~/.brainstem/venv identity, "
                "protected user state, and prior running/stopped state on every "
                "apply failure."
            ),
            "targets": {
                "fresh_bootstrap": "currently verified rolling tag",
                "update": "exact reviewed commit",
                "repair": (
                    "exact reviewed commit when Git metadata supports it; the "
                    "current verified rolling tag only for broken-source repair"
                ),
                "rollback": "historical exact commit from verified evidence",
            },
            "protected_user_zone": (
                "Every operation verifies the complete post-operation manifest "
                "digest and count. New paths require explicit plan-bound "
                "enumeration; bootstrap initialization is separate."
            ),
            "existing_manual_install": (
                "A healthy externally started Brainstem remains immediately "
                "usable through /chat without process adoption. Lifecycle "
                "mutation waits for sidecar ownership."
            ),
            "actions": [
                "bootstrap",
                "start",
                "restart",
                "verify",
                "update",
                "repair",
                "rollback",
            ],
            "evidence": {
                "spec": "rapp/1",
                "location": "~/.brainstem/evidence",
                "append_only": True,
                "private_by_default": True,
            },
        },
        "consent": {
            "read_only": "No additional confirmation.",
            "machine_mutation": (
                "The user's natural-language request is intent. Apply only "
                "the exact plan or bootstrap-envelope hash derived from it."
            ),
            "identity_or_privilege": (
                "The user completes unavoidable GitHub, operating-system, or "
                "tenant authorization directly."
            ),
        },
        "ownership": {
            "runtime": "operator-managed",
            "soul": "user-owned",
            "agents": "user-owned",
            "memory": "user-owned",
            "secrets": "never copied into plans, frames, prompts, or logs",
        },
        "support_matrix": {
            "github_copilot": {
                "role": "golden path",
                "surfaces": ["Copilot CLI", "VS Code Agent mode"],
            },
            "claude_code": {
                "role": "compatibility backup",
                "surfaces": ["Claude Code"],
            },
        },
    }


def render_manifest() -> bytes:
    return (
        json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def generated_outputs() -> dict[Path, bytes]:
    lock, lock_payload = read_lock()
    bundle = operator_bundle()
    return {
        BOOTSTRAP_SH: render_bootstrap_sh(lock, lock_payload, bundle),
        BOOTSTRAP_PS1: render_bootstrap_ps1(lock, lock_payload, bundle),
        OUTPUT: render_manifest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = generated_outputs()
    if args.check:
        stale = [
            path.relative_to(ROOT)
            for path, expected in outputs.items()
            if not path.is_file() or path.read_bytes() != expected
        ]
        if BOOTSTRAP_SH.is_file() and not os.access(BOOTSTRAP_SH, os.X_OK):
            stale.append(BOOTSTRAP_SH.relative_to(ROOT))
        if stale:
            names = ", ".join(str(path) for path in dict.fromkeys(stale))
            print(f"generated artifacts are stale: {names}")
            return 1
        return 0
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        if path == BOOTSTRAP_SH:
            path.chmod(0o755)
        print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
