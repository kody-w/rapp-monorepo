#!/usr/bin/env python3
"""Fail-closed lifecycle control for the unchanged public RAPP Brainstem."""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import json
import os
import re
import secrets
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

try:
    from rapp1 import (
        H,
        build_frame,
        canonical_bytes,
        mint_rappid,
        rappid_valid,
        verify_frame,
    )
except ImportError:  # pragma: no cover - package import path
    from .rapp1 import (
        H,
        build_frame,
        canonical_bytes,
        mint_rappid,
        rappid_valid,
        verify_frame,
    )


OPERATOR_VERSION = "3.0.0"
PLAN_SCHEMA = "rapp-operator-plan/2"
BOOTSTRAP_ENVELOPE_SCHEMA = "rapp-brainstem-bootstrap-envelope/2"
INSTALLER_LOCK_SCHEMA = "rapp-brainstem-installer-lock/3"
STATUS_SCHEMA = "rapp-operator-status/1"
PID_SCHEMA = "rapp-brainstem-process/2"
LEGACY_PID_SCHEMA = "rapp-brainstem-process/1"
LOCK_SCHEMA = "rapp-brainstem-operation-lock/1"
USER_STATE_SCHEMA = "rapp-brainstem-user-state/1"
RUNTIME_ENVIRONMENT_SCHEMA = "rapp-brainstem-runtime-environment/1"
MANAGED_ENVIRONMENT_SCHEMA = "rapp-brainstem-managed-environment/1"
DEFAULT_REPO = "https://github.com/microsoft/aibast-agents-library.git"
CANARY_INPUT = "Confirm my Brainstem is alive and name one capability."
SUPPORTED_ACTIONS = {
    "start",
    "restart",
    "verify",
    "update",
    "repair",
    "rollback",
}
INSTALLER_ACTIONS = {"update", "repair", "rollback"}
TRANSACTIONAL_ACTIONS = set(SUPPORTED_ACTIONS)
_HEX40 = set("0123456789abcdef")
_HEX64 = set("0123456789abcdef")
_SAFE_TAG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
_SAFE_VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?$")
_SAFE_ACTOR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UTC_MILLIS = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d\.\d{3}Z$"
)
BOOTSTRAP_STATE_HOME = "~/.rapp/brainstem-bootstrap"
SUPPORTED_RUNTIME_OVERRIDES = (
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
_POSIX_CHILD_ENVIRONMENT = (
    "HOME",
    "PATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TMPDIR",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "NO_PROXY",
    "https_proxy",
    "http_proxy",
    "no_proxy",
)
_WINDOWS_CHILD_ENVIRONMENT = (
    "USERPROFILE",
    "SystemRoot",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "PATH",
    "TEMP",
    "TMP",
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMDATA",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "NO_PROXY",
    "https_proxy",
    "http_proxy",
    "no_proxy",
)
TRUST_ANCHOR = {
    "kind": "local-marketplace-plugin",
    "plugin": "rapp-brainstem",
    "authority": "executing-plugin-bundle",
}
BOOTSTRAP_PRECONDITIONS = {
    "brainstem_release": "absent",
    "managed_runtime": "stopped",
    "protected_user_state": "absent",
}
BOOTSTRAP_POSTCONDITIONS = {
    "brainstem_release": "exact-target",
    "live_verification": "required-separately",
    "managed_runtime": "stopped",
}


class OperatorError(RuntimeError):
    """A fail-closed lifecycle error safe to show to the local operator."""


@dataclass(frozen=True)
class Layout:
    home: Path
    venv_dir: Path
    source_root: Path
    runtime_dir: Path
    evidence_dir: Path
    frames_dir: Path
    operator_dir: Path
    plans_dir: Path
    backups_dir: Path
    identity_file: Path
    lock_file: Path
    operation_lock_file: Path
    pid_file: Path
    log_file: Path

    @classmethod
    def current(cls, home: str | Path | None = None) -> "Layout":
        resolved_home = Path(
            home or os.environ.get("BRAINSTEM_HOME") or "~/.brainstem"
        ).expanduser()
        source_root = resolved_home / "src"
        runtime_dir = source_root / "rapp_brainstem"
        evidence_dir = resolved_home / "evidence"
        operator_dir = resolved_home / "operator"
        return cls(
            home=resolved_home,
            venv_dir=resolved_home / "venv",
            source_root=source_root,
            runtime_dir=runtime_dir,
            evidence_dir=evidence_dir,
            frames_dir=evidence_dir / "frames",
            operator_dir=operator_dir,
            plans_dir=operator_dir / "plans",
            backups_dir=operator_dir / "backups",
            identity_file=evidence_dir / "rappid.json",
            lock_file=evidence_dir / ".append.lock",
            operation_lock_file=operator_dir / ".operation.lock",
            pid_file=operator_dir / "brainstem.pid",
            log_file=operator_dir / "brainstem.log",
        )


@dataclass
class TransactionSnapshot:
    transaction_id: str
    action: str
    backup_root: Path
    release_backup: Path
    release_present: bool
    venv_backup: Path
    venv_present: bool
    before_release: dict[str, Any]
    before_runtime: dict[str, Any]
    before_environment: dict[str, Any]
    before_user: dict[str, Any]


def fixed_utc(now: datetime | None = None) -> str:
    value = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return (
        value.strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{value.microsecond // 1000:03d}Z"
    )


def _atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temp_path = Path(temp_name)
    try:
        try:
            os.fchmod(fd, mode)
        except (AttributeError, OSError):
            pass
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_write(
        path,
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def _create_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError as exc:
        raise OperatorError(f"Refusing to replace existing record {path}") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _same_path(left: Path, right: Path) -> bool:
    left_value = os.path.normcase(str(left.expanduser().resolve(strict=False)))
    right_value = os.path.normcase(str(right.expanduser().resolve(strict=False)))
    return left_value == right_value


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def _is_default_home(layout: Layout) -> bool:
    return _same_path(layout.home, Path.home() / ".brainstem")


def _require_default_home(layout: Layout, action: str) -> None:
    if (
        action == "bootstrap" or action in INSTALLER_ACTIONS
    ) and not _is_default_home(layout):
        raise OperatorError(
            "The unchanged upstream installer hardcodes ~/.brainstem; "
            "installer-backed actions reject a non-default --home"
        )


def _valid_hex(value: Any, length: int) -> bool:
    alphabet = _HEX40 if length == 40 else _HEX64
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in alphabet for character in value)
    )


def _sequence_digest(
    space: str,
    schema: str,
    entries: list[Any],
) -> str:
    digest = hashlib.sha256()
    digest.update(space.encode("ascii") + b"\n")
    digest.update(schema.encode("ascii") + b"\n")
    digest.update(str(len(entries)).encode("ascii") + b"\n")
    for entry in entries:
        payload = canonical_bytes(entry)
        digest.update(str(len(payload)).encode("ascii") + b":")
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def _plugin_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    required = (
        root / "plugin.json",
        root / "installer-lock.json",
        root / "scripts/bootstrap.sh",
        root / "scripts/bootstrap.ps1",
        root / "skills/rapp-brainstem/SKILL.md",
    )
    if any(not path.is_file() or path.is_symlink() for path in required):
        raise OperatorError(
            "rappctl must run directly from a complete installed "
            "RAPP Brainstem marketplace plugin bundle"
        )
    try:
        plugin = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorError("Installed plugin metadata is unreadable") from exc
    if plugin.get("name") != "rapp-brainstem":
        raise OperatorError("Installed plugin metadata is not RAPP Brainstem")
    return root


def _installer_lock_path() -> Path:
    return _plugin_root() / "installer-lock.json"


def load_installer_lock() -> dict[str, Any]:
    path = _installer_lock_path()
    payload = path.read_bytes()
    try:
        lock = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorError("Bundled installer-lock.json is unreadable") from exc
    if lock.get("schema") != INSTALLER_LOCK_SCHEMA:
        raise OperatorError("Bundled installer lock has an unsupported schema")
    target = lock.get("target")
    if not isinstance(target, dict):
        raise OperatorError("Bundled installer lock has no exact target")
    required_target = {
        "repository",
        "tag",
        "commit",
        "tree",
        "version",
        "version_url",
    }
    if set(target) != required_target:
        raise OperatorError("Bundled installer target is incomplete")
    if target["repository"] != DEFAULT_REPO:
        raise OperatorError("Bundled installer target repository is not trusted")
    if not _valid_hex(target["commit"], 40) or not _valid_hex(
        target["tree"], 40
    ):
        raise OperatorError("Bundled installer target Git identity is invalid")
    if not isinstance(target["tag"], str) or not target["tag"]:
        raise OperatorError("Bundled installer target tag is invalid")
    if not isinstance(target["version"], str) or not target["version"]:
        raise OperatorError("Bundled installer target version is invalid")
    _validate_target_descriptor(target)
    artifacts = lock.get("artifacts")
    if (
        not isinstance(artifacts, dict)
        or set(artifacts) != {"macos-linux", "windows"}
    ):
        raise OperatorError("Bundled installer artifacts are missing")
    for platform_id in ("macos-linux", "windows"):
        artifact = artifacts.get(platform_id)
        if not isinstance(artifact, dict) or set(artifact) != {"url", "sha256"}:
            raise OperatorError(f"Bundled lock has no {platform_id} installer")
        if not isinstance(artifact.get("url"), str) or not artifact["url"]:
            raise OperatorError("Bundled installer URL is invalid")
        if not _valid_hex(artifact.get("sha256"), 64):
            raise OperatorError("Bundled installer SHA-256 is invalid")
        if f"/{target['commit']}/" not in artifact["url"]:
            raise OperatorError(
                "Bundled installer URL is not addressed by the reviewed commit"
            )
        filename = "install.ps1" if platform_id == "windows" else "install.sh"
        expected_url = (
            "https://raw.githubusercontent.com/microsoft/"
            f"aibast-agents-library/{target['commit']}/{filename}"
        )
        if artifact["url"] != expected_url:
            raise OperatorError("Bundled installer URL is not the exact Grail path")
    bootstrap = lock.get("bootstrap")
    expected_bootstrap = {
        "envelope_schema": BOOTSTRAP_ENVELOPE_SCHEMA,
        "state_home": BOOTSTRAP_STATE_HOME,
        "target_ref_kind": "rolling-tag",
        "required_installer_arguments": [
            "--no-launch",
            "--version",
            target["tag"],
        ],
        "verification": (
            "A successful reconcile records installation only. Live "
            "verification requires a later real POST /chat canary."
        ),
    }
    if bootstrap != expected_bootstrap:
        raise OperatorError("Bundled installer bootstrap policy is invalid")
    expected_lifecycle = {
        "preferred_target_ref_kind": "exact-commit",
        "repair_fallback_target_ref_kind": "rolling-tag",
        "historical_rollback_target_ref_kind": "exact-commit",
        "exact_commit_installer_arguments": ["--no-launch"],
        "rolling_tag_installer_arguments": [
            "--no-launch",
            "--version",
            target["tag"],
        ],
    }
    if lock.get("lifecycle") != expected_lifecycle:
        raise OperatorError("Bundled installer lifecycle policy is invalid")
    lock["_digest"] = hashlib.sha256(payload).hexdigest()
    lock["_path"] = str(path)
    return lock


def _installer_artifact_for_platform(
    lock: dict[str, Any],
    platform_id: str,
) -> dict[str, str]:
    if platform_id not in {"macos-linux", "windows"}:
        raise OperatorError("Unsupported bootstrap platform")
    artifact = lock["artifacts"][platform_id]
    return {
        "platform": platform_id,
        "url": artifact["url"],
        "sha256": artifact["sha256"],
    }


def _installer_artifact(lock: dict[str, Any]) -> dict[str, str]:
    platform_id = "windows" if os.name == "nt" else "macos-linux"
    return _installer_artifact_for_platform(lock, platform_id)


def _bootstrap_installer_for_platform(
    lock: dict[str, Any],
    platform_id: str,
) -> dict[str, Any]:
    return {
        **_installer_artifact_for_platform(lock, platform_id),
        "arguments": list(lock["bootstrap"]["required_installer_arguments"]),
        "repository_ref": {
            "kind": "rolling-tag",
            "value": lock["target"]["tag"],
        },
    }


def _validate_target_descriptor(target: Any) -> None:
    if not isinstance(target, dict):
        raise OperatorError("Target release descriptor is invalid")
    if target.get("repository") != DEFAULT_REPO:
        raise OperatorError("Target release repository is not trusted")
    if not _valid_hex(target.get("commit"), 40):
        raise OperatorError("Target release commit is invalid")
    if not _valid_hex(target.get("tree"), 40):
        raise OperatorError("Target release tree is invalid")
    for field in ("tag", "version", "version_url"):
        if not isinstance(target.get(field), str) or not target[field]:
            raise OperatorError(f"Target release {field} is invalid")
    if (
        not _SAFE_TAG.fullmatch(target["tag"])
        or ".." in target["tag"]
        or not _SAFE_VERSION.fullmatch(target["version"])
    ):
        raise OperatorError("Target release tag or version is unsafe")
    expected_version_url = (
        "https://raw.githubusercontent.com/microsoft/"
        f"aibast-agents-library/{target['commit']}/"
        "rapp_brainstem/VERSION"
    )
    if target["version_url"] != expected_version_url:
        raise OperatorError(
            "Target VERSION URL is not addressed by the target commit"
        )


def _operator_bundle_identity() -> dict[str, Any]:
    _plugin_root()
    operator_dir = Path(__file__).resolve().parent
    entries = []
    for name in ("__init__.py", "rapp1.py", "rappctl.py"):
        path = operator_dir / name
        if not path.is_file():
            raise OperatorError("The local operator bundle is incomplete")
        entries.append(
            {
                "name": name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    identity = {
        "schema": "rapp-brainstem-operator-bundle/1",
        "files": entries,
    }
    identity["sha256"] = H("rapp/operator-bundle/1", identity)
    return identity


def bootstrap_envelope(
    lock: dict[str, Any],
    actor: str,
    created_utc: str,
    platform_id: str,
    operator_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(actor, str) or not _SAFE_ACTOR.fullmatch(actor):
        raise OperatorError("Bootstrap actor is invalid")
    if not isinstance(created_utc, str) or not _UTC_MILLIS.fullmatch(
        created_utc
    ):
        raise OperatorError("Bootstrap envelope timestamp is invalid")
    return {
        "action": "bootstrap",
        "actor": actor,
        "bootstrap_state_home": BOOTSTRAP_STATE_HOME,
        "created_utc": created_utc,
        "installer": _bootstrap_installer_for_platform(lock, platform_id),
        "installer_lock": {
            "schema": INSTALLER_LOCK_SCHEMA,
            "sha256": lock["_digest"],
        },
        "operator_bundle": operator_bundle or _operator_bundle_identity(),
        "postconditions": dict(BOOTSTRAP_POSTCONDITIONS),
        "preconditions": dict(BOOTSTRAP_PRECONDITIONS),
        "schema": BOOTSTRAP_ENVELOPE_SCHEMA,
        "target_release": dict(lock["target"]),
        "trust_anchor": dict(TRUST_ANCHOR),
    }


def _json_without_duplicate_keys(payload: bytes) -> dict[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise OperatorError(
                    f"Bootstrap envelope repeats the JSON key {key!r}"
                )
            value[key] = item
        return value

    try:
        parsed = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=object_pairs,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorError("Bootstrap envelope is unreadable") from exc
    if not isinstance(parsed, dict):
        raise OperatorError("Bootstrap envelope must be a JSON object")
    return parsed


def _load_bootstrap_envelope(
    path_value: str | Path,
    expected_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    if not _valid_hex(expected_sha256, 64):
        raise OperatorError("Bootstrap envelope SHA-256 is invalid")
    path = Path(path_value).expanduser()
    try:
        path_stat = path.lstat()
    except FileNotFoundError as exc:
        raise OperatorError("Bootstrap envelope does not exist") from exc
    if not stat.S_ISREG(path_stat.st_mode) or stat.S_ISLNK(path_stat.st_mode):
        raise OperatorError("Bootstrap envelope must be a regular local file")
    if path.name != f"{expected_sha256}.json":
        raise OperatorError(
            "Bootstrap envelope filename is not its exact SHA-256"
        )
    payload = path.read_bytes()
    if not payload or len(payload) > 128 * 1024:
        raise OperatorError("Bootstrap envelope has an invalid size")
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if actual_sha256 != expected_sha256:
        raise OperatorError("Bootstrap envelope SHA-256 does not match")
    return _json_without_duplicate_keys(payload), payload


def _validate_bootstrap_envelope(
    layout: Layout,
    actor: str,
    envelope_path: str | Path,
    envelope_sha256: str,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    envelope, _payload = _load_bootstrap_envelope(
        envelope_path,
        envelope_sha256,
    )
    lock = load_installer_lock()
    platform_id = "windows" if os.name == "nt" else "macos-linux"
    created_utc = envelope.get("created_utc")
    if not isinstance(created_utc, str):
        raise OperatorError("Bootstrap envelope timestamp is missing")
    expected = bootstrap_envelope(
        lock,
        actor,
        created_utc,
        platform_id,
    )
    if envelope != expected:
        if envelope.get("actor") != actor:
            raise OperatorError("Bootstrap envelope actor does not match")
        if envelope.get("installer_lock") != expected["installer_lock"]:
            raise OperatorError("Bootstrap envelope installer lock drifted")
        if envelope.get("installer") != expected["installer"]:
            raise OperatorError(
                "Bootstrap envelope installer URL or SHA-256 drifted"
            )
        if envelope.get("target_release") != expected["target_release"]:
            raise OperatorError("Bootstrap envelope target release drifted")
        if envelope.get("operator_bundle") != expected["operator_bundle"]:
            raise OperatorError("Bootstrap envelope operator bundle drifted")
        raise OperatorError("Bootstrap envelope contract is invalid")
    current = release_identity(layout)
    _assert_exact_target(envelope["target_release"], current)
    _verify_local_target_tag(
        layout,
        envelope["target_release"],
        required=True,
    )
    runtime = managed_runtime_state(layout, cleanup_stale=False)
    _require_known_runtime(runtime)
    if runtime["state"] != "stopped":
        raise OperatorError(
            "Bootstrap reconcile requires the --no-launch stopped state"
        )
    return envelope, lock, current, runtime


def _windows_pid_alive(pid: int) -> bool:
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    still_active = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetExitCodeProcess.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(
        process_query_limited_information,
        False,
        pid,
    )
    if not handle:
        return ctypes.get_last_error() == 5
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return _windows_pid_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _command_line(pid: int) -> str:
    if os.name == "nt":
        command = (
            "$p=Get-CimInstance Win32_Process -Filter \"ProcessId = "
            f"{pid}\"; if ($p) {{ [Console]::Out.Write($p.CommandLine) }}"
        )
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            return ""
        result = subprocess.run(
            [shell, "-NoProfile", "-Command", command],
            text=True,
            capture_output=True,
            check=False,
        )
    else:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            text=True,
            capture_output=True,
            check=False,
        )
    return result.stdout.strip() if result.returncode == 0 else ""


def _windows_process_snapshot(pid: int) -> dict[str, Any] | None:
    import ctypes
    from ctypes import wintypes

    if not _windows_pid_alive(pid):
        return None
    process_query_limited_information = 0x1000
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel32.OpenProcess(
        process_query_limited_information,
        False,
        pid,
    )
    if not handle:
        raise OperatorError(
            f"Cannot inspect process {pid} strongly enough to prove ownership"
        )
    try:
        created = wintypes.FILETIME()
        exited = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not kernel32.GetProcessTimes(
            handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            raise OperatorError("Could not read Windows process creation identity")
        creation_ticks = (
            int(created.dwHighDateTime) << 32
        ) | int(created.dwLowDateTime)
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(
            handle,
            0,
            buffer,
            ctypes.byref(size),
        ):
            raise OperatorError("Could not read Windows process executable")
        executable = buffer.value
    finally:
        kernel32.CloseHandle(handle)
    command = _command_line(pid)
    if not command:
        raise OperatorError("Could not read Windows process command identity")
    return {
        "pid": pid,
        "creation_identity": f"windows-filetime:{creation_ticks}",
        "executable": os.path.normcase(executable),
        "command_identity": H(
            "rapp/process-command/1",
            {"command": command},
        ),
    }


def _posix_process_snapshot(pid: int) -> dict[str, Any] | None:
    if not _pid_alive(pid):
        return None
    proc_root = Path("/proc") / str(pid)
    creation_identity = ""
    executable = ""
    if proc_root.is_dir():
        try:
            stat_text = (proc_root / "stat").read_text(encoding="utf-8")
            closing_paren = stat_text.rfind(")")
            stat_fields = stat_text[closing_paren + 2 :].split()
            if closing_paren < 0 or len(stat_fields) <= 19:
                raise ValueError("invalid /proc stat")
            if stat_fields[0] == "Z":
                return None
            creation_identity = f"proc-starttime:{stat_fields[19]}"
            executable = os.readlink(proc_root / "exe")
        except (OSError, IndexError, ValueError):
            creation_identity = ""
    if not creation_identity:
        state_result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "state="],
            text=True,
            capture_output=True,
            check=False,
        )
        if (
            state_result.returncode != 0
            or not state_result.stdout.strip()
            or state_result.stdout.strip().startswith("Z")
        ):
            return None
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "lstart="],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        creation_identity = f"ps-lstart:{result.stdout.strip()}"
    if not executable:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm="],
            text=True,
            capture_output=True,
            check=False,
        )
        executable = result.stdout.strip() if result.returncode == 0 else ""
    command = _command_line(pid)
    if not executable or not command:
        raise OperatorError(
            f"Cannot inspect process {pid} strongly enough to prove ownership"
        )
    return {
        "pid": pid,
        "creation_identity": creation_identity,
        "executable": str(Path(executable).resolve(strict=False)),
        "command_identity": H(
            "rapp/process-command/1",
            {"command": command},
        ),
    }


def _process_snapshot(pid: int) -> dict[str, Any] | None:
    if pid <= 0:
        return None
    if os.name == "nt":
        return _windows_process_snapshot(pid)
    return _posix_process_snapshot(pid)


def _process_record(
    snapshot: dict[str, Any],
    environment_binding: dict[str, Any],
    managed_environment: dict[str, Any],
) -> dict[str, Any]:
    executable = snapshot["executable"]
    return {
        "schema": PID_SCHEMA,
        "pid": snapshot["pid"],
        "creation_identity": snapshot["creation_identity"],
        "executable": executable,
        "executable_identity": H(
            "rapp/process-executable/1",
            {"executable": executable},
        ),
        "command_identity": snapshot["command_identity"],
        "environment_sha256": environment_binding["sha256"],
        "effective_port": environment_binding["effective_port"],
        "managed_environment_sha256": managed_environment["sha256"],
        "nonce": secrets.token_hex(32),
        "started_utc": fixed_utc(),
    }


def _validate_process_record(record: dict[str, Any]) -> None:
    common = {
        "schema",
        "pid",
        "creation_identity",
        "executable",
        "executable_identity",
        "command_identity",
        "nonce",
        "started_utc",
    }
    schema = record.get("schema")
    if schema == PID_SCHEMA:
        required = common | {
            "environment_sha256",
            "effective_port",
            "managed_environment_sha256",
        }
    elif schema == LEGACY_PID_SCHEMA:
        required = common
    else:
        required = set()
    if set(record) != required:
        raise OperatorError("Managed PID record is invalid")
    if not isinstance(record.get("pid"), int) or record["pid"] <= 0:
        raise OperatorError("Managed PID record has an invalid PID")
    for field in (
        "creation_identity",
        "executable",
        "nonce",
        "started_utc",
    ):
        if not isinstance(record.get(field), str) or not record[field]:
            raise OperatorError(f"Managed PID record has an invalid {field}")
    for field in ("executable_identity", "command_identity"):
        if not _valid_hex(record.get(field), 64):
            raise OperatorError(f"Managed PID record has an invalid {field}")
    if schema == PID_SCHEMA:
        for field in ("environment_sha256", "managed_environment_sha256"):
            if not _valid_hex(record.get(field), 64):
                raise OperatorError(
                    f"Managed PID record has an invalid {field}"
                )
        if (
            not isinstance(record.get("effective_port"), int)
            or not 1 <= record["effective_port"] <= 65535
        ):
            raise OperatorError(
                "Managed PID record has an invalid effective_port"
            )


def _record_matches_snapshot(
    record: dict[str, Any],
    snapshot: dict[str, Any] | None,
) -> bool:
    if snapshot is None:
        return False
    executable_identity = H(
        "rapp/process-executable/1",
        {"executable": snapshot["executable"]},
    )
    return (
        snapshot["pid"] == record["pid"]
        and snapshot["creation_identity"] == record["creation_identity"]
        and snapshot["executable"] == record["executable"]
        and executable_identity == record["executable_identity"]
        and snapshot["command_identity"] == record["command_identity"]
    )


def _delete_json_record(path: Path, expected: dict[str, Any]) -> None:
    try:
        with path.open("rb") as handle:
            descriptor_stat = os.fstat(handle.fileno())
            payload = handle.read()
    except FileNotFoundError:
        return
    try:
        current = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorError(f"Refusing to delete changed record {path}") from exc
    if current != expected:
        raise OperatorError(f"Refusing to delete changed record {path}")
    try:
        path_stat = path.stat()
    except FileNotFoundError:
        return
    if (
        path_stat.st_dev != descriptor_stat.st_dev
        or path_stat.st_ino != descriptor_stat.st_ino
    ):
        raise OperatorError(f"Refusing to delete replaced record {path}")
    path.unlink()


def _pid_record_state(
    layout: Layout,
    *,
    cleanup_stale: bool,
) -> tuple[dict[str, Any] | None, str]:
    if not layout.pid_file.is_file():
        return None, "missing"
    try:
        record = json.loads(layout.pid_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperatorError("Managed PID record is unreadable") from exc
    if not isinstance(record, dict):
        raise OperatorError("Managed PID record is invalid")
    _validate_process_record(record)
    snapshot = _process_snapshot(record["pid"])
    if _record_matches_snapshot(record, snapshot):
        return (
            record,
            "owned" if record["schema"] == PID_SCHEMA else "legacy-owned",
        )
    if cleanup_stale:
        _delete_json_record(layout.pid_file, record)
    return None, "stale"


def _record_alive(record: dict[str, Any]) -> bool:
    return _record_matches_snapshot(
        record,
        _process_snapshot(record["pid"]),
    )


def _windows_terminate_owned(record: dict[str, Any]) -> None:
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    process_terminate = 0x0001
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel32.OpenProcess(
        process_query_limited_information | process_terminate,
        False,
        record["pid"],
    )
    if not handle:
        raise OperatorError("Could not open the owned Windows process")
    try:
        snapshot = _windows_process_snapshot(record["pid"])
        if not _record_matches_snapshot(record, snapshot):
            raise OperatorError(
                "Managed PID identity changed; refusing to terminate it"
            )
        if not kernel32.TerminateProcess(handle, 0):
            raise OperatorError("Could not terminate the owned Windows process")
    finally:
        kernel32.CloseHandle(handle)


def _terminate_owned(record: dict[str, Any]) -> None:
    snapshot = _process_snapshot(record["pid"])
    if not _record_matches_snapshot(record, snapshot):
        raise OperatorError(
            "Managed PID identity changed; refusing to terminate it"
        )
    if os.name == "nt":
        _windows_terminate_owned(record)
    else:
        os.kill(record["pid"], signal.SIGTERM)


def _reap_child(pid: int) -> None:
    if os.name == "nt":
        return
    try:
        os.waitpid(pid, os.WNOHANG)
    except (AttributeError, ChildProcessError, OSError):
        pass


def _lock_owner() -> dict[str, Any]:
    snapshot = _process_snapshot(os.getpid())
    if snapshot is None:
        raise OperatorError("Could not establish operation-lock process identity")
    return {
        "schema": LOCK_SCHEMA,
        "pid": snapshot["pid"],
        "creation_identity": snapshot["creation_identity"],
        "nonce": secrets.token_hex(32),
        "utc": fixed_utc(),
    }


def _lock_is_alive(record: dict[str, Any]) -> bool:
    if (
        not isinstance(record, dict)
        or record.get("schema") != LOCK_SCHEMA
        or not isinstance(record.get("pid"), int)
        or not isinstance(record.get("creation_identity"), str)
    ):
        return True
    snapshot = _process_snapshot(record["pid"])
    return bool(
        snapshot
        and snapshot["creation_identity"] == record["creation_identity"]
    )


@contextlib.contextmanager
def _exclusive_process_lock(
    path: Path,
    label: str,
    timeout: float = 10.0,
) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    owner = _lock_owner()
    while True:
        try:
            descriptor = os.open(
                path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(owner, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            break
        except FileExistsError:
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                current = None
            if isinstance(current, dict) and not _lock_is_alive(current):
                _delete_json_record(path, current)
                continue
            if time.monotonic() >= deadline:
                raise OperatorError(f"{label} is busy")
            time.sleep(0.05)
    try:
        yield
    finally:
        _delete_json_record(path, owner)


@contextlib.contextmanager
def _append_lock(path: Path, timeout: float = 10.0) -> Iterator[None]:
    with _exclusive_process_lock(path, "RAPP/1 evidence stream", timeout):
        yield


@contextlib.contextmanager
def _operation_lock(layout: Layout, timeout: float = 30.0) -> Iterator[None]:
    with _exclusive_process_lock(
        layout.operation_lock_file,
        "Brainstem lifecycle operation",
        timeout,
    ):
        yield


def _git(layout: Layout, *args: str) -> str | None:
    if not (layout.source_root / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(layout.source_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _tracked_entries(layout: Layout) -> dict[str, dict[str, str]]:
    if not (layout.source_root / ".git").exists():
        return {}
    result = subprocess.run(
        [
            "git",
            "-C",
            str(layout.source_root),
            "ls-tree",
            "-r",
            "-z",
            "HEAD",
            "--",
            "rapp_brainstem",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {}
    entries: dict[str, dict[str, str]] = {}
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, object_type, object_id = metadata.decode("ascii").split()
            path = raw_path.decode("utf-8", "strict")
        except (ValueError, UnicodeDecodeError):
            raise OperatorError("Could not parse the installed Git tree")
        prefix = "rapp_brainstem/"
        if object_type != "blob" or not path.startswith(prefix):
            continue
        entries[path[len(prefix):]] = {
            "mode": mode,
            "blob": object_id,
        }
    return entries


def _path_blob(path: Path) -> str | None:
    try:
        path_stat = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(path_stat.st_mode):
        payload = os.readlink(path).encode("utf-8")
    elif stat.S_ISREG(path_stat.st_mode):
        payload = path.read_bytes()
    else:
        return None
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _is_explicit_user_path(relative: str) -> bool:
    path = Path(relative)
    parts = path.parts
    if not parts:
        return False
    top = parts[0]
    name = parts[-1]
    if top == "soul.md":
        return True
    if top == ".env" or (top.startswith(".env.") and top != ".env.example"):
        return True
    if top in {
        ".brainstem_data",
        ".data",
        ".memory",
        "memory",
        "memories",
        "data",
        "tokens",
        "config",
        "state",
    }:
        return True
    if top.startswith((".copilot_", ".brainstem_")):
        return True
    if name in {
        ".copilot_token",
        "copilot_token",
        "voice.zip",
        "credentials.json",
        "config.json",
        "config.yaml",
        "config.yml",
        "config.toml",
        "memory.json",
        "tokens.json",
    }:
        return True
    lowered = name.lower()
    if any(marker in lowered for marker in ("token", "credential", "secret")):
        return True
    return name.endswith((".db", ".sqlite", ".sqlite3"))


def _iter_runtime_paths(layout: Layout) -> Iterator[tuple[str, Path]]:
    if not layout.runtime_dir.is_dir():
        return
    for root, directories, files in os.walk(
        layout.runtime_dir,
        followlinks=False,
    ):
        root_path = Path(root)
        for name in sorted(directories + files):
            path = root_path / name
            relative = path.relative_to(layout.runtime_dir).as_posix()
            yield relative, path


def _user_path_set(
    layout: Layout,
    tracked: dict[str, dict[str, str]] | None = None,
) -> set[str]:
    tracked = tracked if tracked is not None else _tracked_entries(layout)
    paths: set[str] = set()
    actual_paths: dict[str, Path] = dict(_iter_runtime_paths(layout) or ())
    for relative, actual_path in actual_paths.items():
        if _is_explicit_user_path(relative):
            paths.add(relative)
        try:
            is_real_directory = stat.S_ISDIR(actual_path.lstat().st_mode)
        except FileNotFoundError:
            is_real_directory = False
        if relative.startswith("agents/") and not is_real_directory:
            tracked_entry = tracked.get(relative)
            if tracked_entry is None:
                paths.add(relative)
            elif _path_blob(actual_paths[relative]) != tracked_entry["blob"]:
                paths.add(relative)
    for relative, tracked_entry in tracked.items():
        if _is_explicit_user_path(relative):
            paths.add(relative)
        if relative.startswith("agents/"):
            actual = layout.runtime_dir / Path(relative)
            if _path_blob(actual) != tracked_entry["blob"]:
                paths.add(relative)
    return paths


def _manifest_entry_at(root: Path, relative: str) -> dict[str, Any]:
    path = root / Path(relative)
    try:
        path_stat = path.lstat()
    except FileNotFoundError:
        return {"path": relative, "kind": "absent"}
    mode = stat.S_IMODE(path_stat.st_mode)
    if stat.S_ISLNK(path_stat.st_mode):
        target = os.readlink(path).encode("utf-8")
        return {
            "path": relative,
            "kind": "symlink",
            "mode": mode,
            "sha256": hashlib.sha256(target).hexdigest(),
        }
    if stat.S_ISDIR(path_stat.st_mode):
        return {
            "path": relative,
            "kind": "directory",
            "mode": mode,
        }
    if stat.S_ISREG(path_stat.st_mode):
        payload = path.read_bytes()
        return {
            "path": relative,
            "kind": "file",
            "mode": mode,
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    raise OperatorError("Protected user state contains an unsupported file type")


def _manifest_entry(layout: Layout, relative: str) -> dict[str, Any]:
    return _manifest_entry_at(layout.runtime_dir, relative)


def _finish_user_manifest(entries: list[dict[str, Any]]) -> dict[str, Any]:
    entries.sort(key=lambda entry: entry["path"])
    base = {
        "schema": USER_STATE_SCHEMA,
        "entries": entries,
    }
    return {
        **base,
        "count": len(entries),
        "digest": _sequence_digest(
            "rapp/brainstem-user-state/1",
            USER_STATE_SCHEMA,
            entries,
        ),
    }


def user_zone_manifest(layout: Layout) -> dict[str, Any]:
    tracked = _tracked_entries(layout)
    entries = [
        _manifest_entry(layout, relative)
        for relative in sorted(_user_path_set(layout, tracked))
    ]
    return _finish_user_manifest(entries)


def _bound_user_manifest(
    layout: Layout,
    before: dict[str, Any],
) -> dict[str, Any]:
    return _finish_user_manifest(
        [
            _manifest_entry(layout, entry["path"])
            for entry in before.get("entries", [])
        ]
    )


def _parse_dotenv_value(name: str, raw_value: str) -> str:
    value = raw_value.strip()
    if "${" in value:
        raise OperatorError(
            f"Supported runtime override {name} must be a literal value"
        )
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        match = re.fullmatch(
            r"""((?:'(?:\\.|[^'])*')|(?:"(?:\\.|[^"])*"))(?:\s+#.*)?""",
            value,
        )
        if match is None:
            raise OperatorError(
                f"Supported runtime override {name} has unsupported quoting"
            )
        try:
            parsed = ast.literal_eval(match.group(1))
        except (SyntaxError, ValueError) as exc:
            raise OperatorError(
                f"Supported runtime override {name} has invalid quoting"
            ) from exc
        if not isinstance(parsed, str):
            raise OperatorError(
                f"Supported runtime override {name} is not a string"
            )
        value = parsed
    else:
        value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
    if "\x00" in value or "\r" in value or "\n" in value:
        raise OperatorError(
            f"Supported runtime override {name} contains invalid bytes"
        )
    return value


def _dotenv_runtime_overrides(layout: Layout) -> dict[str, str]:
    path = layout.runtime_dir / ".env"
    if not path.is_file():
        return {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise OperatorError("Brainstem .env is unreadable") from exc
    values: dict[str, str] = {}
    assignment = re.compile(
        r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$"
    )
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = assignment.match(stripped)
        if match is None:
            continue
        name, raw_value = match.groups()
        if name in SUPPORTED_RUNTIME_OVERRIDES:
            values[name] = _parse_dotenv_value(name, raw_value)
    return values


def _environment_value_hash(
    name: str,
    value: str,
    *,
    present: bool = True,
) -> str:
    return H(
        "rapp/runtime-environment-value/1",
        {
            "name": name,
            "present": present,
            "value": value if present else None,
        },
    )


def _base_child_environment() -> tuple[dict[str, str], list[dict[str, Any]]]:
    names = (
        _WINDOWS_CHILD_ENVIRONMENT
        if os.name == "nt"
        else _POSIX_CHILD_ENVIRONMENT
    )
    environment: dict[str, str] = {}
    entries: list[dict[str, Any]] = []
    for name in names:
        if name not in os.environ:
            continue
        value = os.environ[name]
        environment[name] = value
        entries.append(
            {
                "name": name,
                "source": "process",
                "value_sha256": _environment_value_hash(name, value),
            }
        )
    home_name = "USERPROFILE" if os.name == "nt" else "HOME"
    if home_name not in environment:
        value = str(Path.home())
        environment[home_name] = value
        entries.append(
            {
                "name": home_name,
                "source": "operator-default",
                "value_sha256": _environment_value_hash(home_name, value),
            }
        )
    if "PATH" not in environment and "Path" not in environment:
        environment["PATH"] = os.defpath
        entries.append(
            {
                "name": "PATH",
                "source": "operator-default",
                "value_sha256": _environment_value_hash("PATH", os.defpath),
            }
        )
    entries.sort(key=lambda item: item["name"].lower())
    return environment, entries


def _effective_port(overrides: dict[str, str]) -> int:
    value = overrides.get("PORT", "7071").strip()
    try:
        port = int(value)
    except ValueError:
        return 7071
    return port if 1 <= port <= 65535 else 7071


def runtime_environment(
    layout: Layout,
) -> tuple[dict[str, str], dict[str, Any]]:
    environment, base_entries = _base_child_environment()
    dotenv = _dotenv_runtime_overrides(layout)
    effective_values: dict[str, str] = {}
    override_entries = []
    for name in SUPPORTED_RUNTIME_OVERRIDES:
        if name in os.environ:
            source = "process"
            value = os.environ[name]
            present = True
        elif name in dotenv:
            source = "dotenv"
            value = dotenv[name]
            present = True
        else:
            source = "default"
            value = ""
            present = False
        if present:
            environment[name] = value
            effective_values[name] = value
        override_entries.append(
            {
                "name": name,
                "present": present,
                "source": source,
                "value_sha256": _environment_value_hash(
                    name,
                    value,
                    present=present,
                ),
            }
        )
    base = {
        "schema": RUNTIME_ENVIRONMENT_SCHEMA,
        "base": base_entries,
        "supported_overrides": override_entries,
        "effective_port": _effective_port(effective_values),
    }
    binding = {
        **base,
        "sha256": H("rapp/runtime-environment/1", base),
    }
    return environment, binding


def _environment_enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _planned_user_zone_additions(
    action: str,
    before: dict[str, Any],
    child_environment: dict[str, str],
) -> list[str]:
    before_paths = {entry["path"] for entry in before["entries"]}
    additions = []
    starts_runtime = action in {
        "start",
        "restart",
        "update",
        "repair",
        "rollback",
    }
    if (
        starts_runtime
        and _environment_enabled(
            child_environment.get("BRAINSTEM_LAN_MODE")
        )
        and ".brainstem_secret" not in before_paths
    ):
        additions.append(".brainstem_secret")
    return additions


def _brainstem_python_path(layout: Layout) -> Path:
    relative = (
        Path("Scripts") / "python.exe"
        if os.name == "nt"
        else Path("bin") / "python"
    )
    return layout.venv_dir / relative


def managed_environment_identity(
    layout: Layout,
    *,
    required: bool = False,
) -> dict[str, Any]:
    managed = _brainstem_python_path(layout)
    requirements = layout.runtime_dir / "requirements.txt"
    requirements_sha256 = (
        hashlib.sha256(requirements.read_bytes()).hexdigest()
        if requirements.is_file()
        else None
    )
    relative_python = (
        "venv/Scripts/python.exe"
        if os.name == "nt"
        else "venv/bin/python"
    )
    base: dict[str, Any] = {
        "schema": MANAGED_ENVIRONMENT_SCHEMA,
        "managed_python": relative_python,
        "requirements_sha256": requirements_sha256,
        "ready": False,
    }
    if not managed.is_file():
        identity = {
            **base,
            "status": "managed-python-missing",
        }
        identity["sha256"] = H("rapp/managed-environment/1", identity)
        if required:
            raise OperatorError("Brainstem-managed Python is missing")
        return identity
    script = """
import importlib.metadata
import json
import platform
import re
import sys

packages = []
for distribution in importlib.metadata.distributions():
    name = distribution.metadata.get("Name") or getattr(distribution, "name", "")
    normalized = re.sub(r"[-_.]+", "-", str(name)).lower()
    packages.append([normalized, str(distribution.version)])
packages.sort()
print(json.dumps({
    "cache_tag": sys.implementation.cache_tag,
    "dependencies": packages,
    "executable": sys.executable,
    "implementation": sys.implementation.name,
    "python_version": platform.python_version(),
}, sort_keys=True))
""".strip()
    environment, _entries = _base_child_environment()
    cwd = layout.runtime_dir if layout.runtime_dir.is_dir() else layout.home
    try:
        result = subprocess.run(
            [str(managed), "-I", "-c", script],
            cwd=cwd,
            env=environment,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        payload = json.loads(result.stdout) if result.returncode == 0 else None
        if not isinstance(payload, dict):
            raise ValueError("invalid managed Python identity")
        executable = Path(str(payload.pop("executable")))
        if not _same_path(executable, managed):
            try:
                same_executable = executable.samefile(managed)
            except OSError:
                same_executable = False
            if not same_executable:
                raise ValueError("managed Python resolved to another interpreter")
        dependencies = payload.pop("dependencies")
        if not isinstance(dependencies, list):
            raise ValueError("invalid dependency inventory")
        interpreter = {
            "implementation": payload["implementation"],
            "python_version": payload["python_version"],
            "cache_tag": payload["cache_tag"],
            "executable_sha256": hashlib.sha256(
                managed.read_bytes()
            ).hexdigest(),
        }
        identity = {
            **base,
            "ready": requirements_sha256 is not None,
            "status": "ready" if requirements_sha256 is not None else (
                "requirements-missing"
            ),
            "interpreter": interpreter,
            "interpreter_sha256": H(
                "rapp/managed-interpreter/1",
                interpreter,
            ),
            "dependency_count": len(dependencies),
            "dependencies_sha256": _sequence_digest(
                "rapp/managed-dependencies/1",
                "managed-dependencies/1",
                dependencies,
            ),
        }
    except (
        KeyError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ):
        identity = {
            **base,
            "status": "managed-python-unusable",
        }
    identity["sha256"] = H("rapp/managed-environment/1", identity)
    if required and not identity["ready"]:
        raise OperatorError(
            "Brainstem-managed Python or its runtime requirements are unusable"
        )
    return identity


def release_identity(layout: Layout) -> dict[str, Any]:
    version_file = layout.runtime_dir / "VERSION"
    brainstem_file = layout.runtime_dir / "brainstem.py"
    installed = version_file.is_file() and brainstem_file.is_file()
    version = None
    if version_file.is_file():
        try:
            version = version_file.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            version = None
    commit = _git(layout, "rev-parse", "HEAD")
    tree = _git(layout, "rev-parse", "HEAD:rapp_brainstem")
    tracked = _tracked_entries(layout)
    user_paths = _user_path_set(layout, tracked)
    expected_entries = []
    actual_entries = []
    mismatches = []
    for relative, entry in sorted(tracked.items()):
        if _is_explicit_user_path(relative) or relative in user_paths:
            continue
        expected_entries.append(
            {
                "path": relative,
                "mode": entry["mode"],
                "blob": entry["blob"],
            }
        )
        actual_blob = _path_blob(layout.runtime_dir / Path(relative))
        actual_entries.append(
            {
                "path": relative,
                "mode": entry["mode"],
                "blob": actual_blob,
            }
        )
        if actual_blob != entry["blob"]:
            mismatches.append(relative)
    managed_clean = bool(tracked) and not mismatches
    managed_environment = managed_environment_identity(layout)
    identity = {
        "installed": installed,
        "version": version,
        "source_commit": commit,
        "source_tree": tree,
        "managed_clean": managed_clean,
        "managed_expected_digest": _sequence_digest(
            "rapp/brainstem-managed-expected/1",
            "managed-expected/1",
            expected_entries,
        )
        if tracked
        else None,
        "managed_digest": _sequence_digest(
            "rapp/brainstem-managed-actual/1",
            "managed-actual/1",
            actual_entries,
        )
        if tracked
        else None,
        "managed_mismatch_count": len(mismatches),
        "managed_mismatch_digest": _sequence_digest(
            "rapp/brainstem-managed-mismatches/1",
            "managed-mismatches/1",
            mismatches,
        )
        if mismatches
        else None,
        "managed_environment": managed_environment,
    }
    identity["release_hash"] = (
        H("rapp/brainstem-release/2", identity) if installed else None
    )
    return identity


def _target_matches_release(
    target: dict[str, Any],
    release: dict[str, Any],
) -> bool:
    return bool(
        _target_source_matches_release(target, release)
        and release.get("managed_environment", {}).get("ready") is True
    )


def _target_source_matches_release(
    target: dict[str, Any],
    release: dict[str, Any],
) -> bool:
    return bool(
        release.get("installed")
        and release.get("version") == target.get("version")
        and release.get("source_commit") == target.get("commit")
        and release.get("source_tree") == target.get("tree")
        and release.get("managed_clean") is True
    )


def _assert_exact_target(
    target: dict[str, Any],
    release: dict[str, Any],
) -> None:
    if not _target_matches_release(target, release):
        raise OperatorError(
            "Installed Brainstem does not match the exact reviewed "
            "version/commit/tree, managed bytes, or managed environment"
        )


def _read_port(
    layout: Layout,
    environment_binding: dict[str, Any] | None = None,
) -> int:
    binding = environment_binding or runtime_environment(layout)[1]
    port = binding.get("effective_port")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise OperatorError("Runtime environment has an invalid effective port")
    return port


def probe_health(
    layout: Layout,
    timeout: float = 2.0,
    environment_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    port = _read_port(layout, environment_binding)
    url = f"http://127.0.0.1:{port}/health/public"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status_code = getattr(response, "status", response.getcode())
            payload = json.loads(response.read().decode("utf-8"))
        return {
            "reachable": status_code == 200 and payload.get("status") == "ok",
            "http_status": status_code,
            "status": payload.get("status"),
            "version": payload.get("version"),
            "port": port,
        }
    except urllib.error.HTTPError as exc:
        return {
            "reachable": False,
            "http_status": exc.code,
            "status": "offline",
            "version": None,
            "port": port,
        }
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        urllib.error.URLError,
    ):
        return {
            "reachable": False,
            "http_status": None,
            "status": "offline",
            "version": None,
            "port": port,
        }


def _port_listening(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(0.4)
        return client.connect_ex(("127.0.0.1", port)) == 0


def managed_runtime_state(
    layout: Layout,
    *,
    cleanup_stale: bool = False,
    environment_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    binding = environment_binding or runtime_environment(layout)[1]
    health = probe_health(
        layout,
        environment_binding=binding,
    )
    record, record_status = _pid_record_state(
        layout,
        cleanup_stale=cleanup_stale,
    )
    listening = _port_listening(health["port"])
    if record is not None:
        state = "running"
        record_hash = H("rapp/process-record/1", record)
    elif health["reachable"] or listening:
        state = "unknown-process"
        record_hash = None
    else:
        state = "stopped"
        record_hash = None
    environment_bound = bool(
        record is not None
        and record.get("schema") == PID_SCHEMA
        and record.get("environment_sha256") == binding["sha256"]
    )
    managed_environment = managed_environment_identity(layout)
    managed_environment_bound = bool(
        record is not None
        and record.get("schema") == PID_SCHEMA
        and record.get("managed_environment_sha256")
        == managed_environment["sha256"]
    )
    return {
        "state": state,
        "pid_record": record_status,
        "process_record_hash": record_hash,
        "environment_binding_sha256": binding["sha256"],
        "effective_port": binding["effective_port"],
        "managed_environment_sha256": managed_environment["sha256"],
        "environment_bound": environment_bound,
        "managed_environment_bound": managed_environment_bound,
        "lifecycle_owned": bool(
            record is not None
            and environment_bound
            and managed_environment_bound
        ),
        "health": health,
        "port_listening": listening,
    }


def _require_known_runtime(state: dict[str, Any]) -> None:
    if state.get("state") == "unknown-process":
        raise OperatorError(
            "The Brainstem port is occupied without a matching sidecar-created "
            "PID record; refusing to adopt, stop, or restart that process"
        )


def _discover_brainstem_pid(layout: Layout) -> int | None:
    record, _status = _pid_record_state(layout, cleanup_stale=False)
    return record["pid"] if record is not None else None


def _stop_brainstem(
    layout: Layout,
    environment_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    binding = environment_binding or runtime_environment(layout)[1]
    state = managed_runtime_state(
        layout,
        cleanup_stale=True,
        environment_binding=binding,
    )
    _require_known_runtime(state)
    record, _status = _pid_record_state(layout, cleanup_stale=True)
    if record is None:
        return {"changed": False, "state": "stopped"}
    _terminate_owned(record)
    deadline = time.monotonic() + 10
    while _record_alive(record) and time.monotonic() < deadline:
        time.sleep(0.1)
    if _record_alive(record):
        raise OperatorError("Owned Brainstem process did not stop")
    _reap_child(record["pid"])
    _delete_json_record(layout.pid_file, record)
    health = probe_health(layout, environment_binding=binding)
    ports = {health["port"]}
    if isinstance(record.get("effective_port"), int):
        ports.add(record["effective_port"])
    if health["reachable"] or any(_port_listening(port) for port in ports):
        raise OperatorError(
            "A different process appeared on the Brainstem port after stop"
        )
    return {"changed": True, "state": "stopped"}


def _start_brainstem(
    layout: Layout,
    expected_environment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    child_environment, environment_binding = runtime_environment(layout)
    if (
        expected_environment is not None
        and expected_environment != environment_binding
    ):
        raise OperatorError("Plan drift: runtime environment changed")
    managed_environment = managed_environment_identity(layout, required=True)
    state = managed_runtime_state(
        layout,
        cleanup_stale=True,
        environment_binding=environment_binding,
    )
    _require_known_runtime(state)
    if state["state"] == "running":
        if not state["lifecycle_owned"]:
            raise OperatorError(
                "The running Brainstem is not bound to the current sidecar "
                "environment; a sidecar-owned restart is required"
            )
        if not state["health"]["reachable"]:
            raise OperatorError(
                "The owned Brainstem process is running but unhealthy; "
                "use restart or repair"
            )
        return {
            "changed": False,
            "state": "running",
            "health": state["health"],
        }
    script = layout.runtime_dir / "brainstem.py"
    if not script.is_file():
        raise OperatorError("Brainstem runtime is not installed")
    layout.log_file.parent.mkdir(parents=True, exist_ok=True)
    command = [str(_brainstem_python(layout)), str(script)]
    creationflags = 0
    if os.name == "nt":
        creationflags = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    with layout.log_file.open("ab") as log:
        process = subprocess.Popen(
            command,
            cwd=layout.runtime_dir,
            env=child_environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=os.name != "nt",
            creationflags=creationflags,
        )
    snapshot = None
    identity_deadline = time.monotonic() + 5
    while time.monotonic() < identity_deadline:
        if process.poll() is not None:
            raise OperatorError(
                f"Brainstem exited during startup; inspect {layout.log_file}"
            )
        snapshot = _process_snapshot(process.pid)
        if snapshot is not None:
            break
        time.sleep(0.05)
    if snapshot is None:
        process.terminate()
        raise OperatorError("Could not capture the new Brainstem process identity")
    record = _process_record(
        snapshot,
        environment_binding,
        managed_environment,
    )
    try:
        _create_json_exclusive(layout.pid_file, record)
    except Exception:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        raise
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if process.poll() is not None:
            _delete_json_record(layout.pid_file, record)
            raise OperatorError(
                f"Brainstem exited during startup; inspect {layout.log_file}"
            )
        health = probe_health(
            layout,
            timeout=1.0,
            environment_binding=environment_binding,
        )
        if health["reachable"]:
            return {
                "changed": True,
                "state": "running",
                "health": health,
            }
        time.sleep(0.5)
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    _delete_json_record(layout.pid_file, record)
    raise OperatorError(
        f"Brainstem did not become healthy; inspect {layout.log_file}"
    )


def _restart_brainstem(
    layout: Layout,
    expected_environment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    binding = expected_environment or runtime_environment(layout)[1]
    stopped = _stop_brainstem(layout, binding)
    started = _start_brainstem(layout, binding)
    return {
        "changed": stopped["changed"] or started["changed"],
        "state": "running",
        "health": started["health"],
    }


def _brainstem_python(layout: Layout) -> Path:
    managed = _brainstem_python_path(layout)
    if not managed.is_file():
        raise OperatorError(
            "Brainstem-managed Python is missing; refusing an unrelated "
            "interpreter fallback"
        )
    return managed


def _chat_canary(
    layout: Layout,
    timeout: float = 30.0,
    environment_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    port = _read_port(layout, environment_binding)
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/chat",
        data=json.dumps({"user_input": CANARY_INPUT}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", response.getcode())
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise OperatorError(
            f"Brainstem /chat canary returned HTTP {exc.code}"
        ) from exc
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        urllib.error.URLError,
    ) as exc:
        raise OperatorError("Brainstem /chat canary did not complete") from exc
    response_text = payload.get("response")
    if not (200 <= status_code < 300):
        raise OperatorError(
            f"Brainstem /chat canary returned HTTP {status_code}"
        )
    if not isinstance(response_text, str) or not response_text.strip():
        raise OperatorError("Brainstem /chat canary returned an empty response")
    return {
        "http_status": status_code,
        "response_sha256": hashlib.sha256(
            response_text.encode("utf-8")
        ).hexdigest(),
    }


def _verify_live(
    layout: Layout,
    release: dict[str, Any],
    expected_environment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _child_environment, binding = runtime_environment(layout)
    if expected_environment is not None and expected_environment != binding:
        raise OperatorError("Plan drift: runtime environment changed")
    state = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=binding,
    )
    _require_known_runtime(state)
    if state["state"] != "running":
        raise OperatorError("Brainstem is not running")
    if not state["lifecycle_owned"]:
        raise OperatorError(
            "Brainstem is reachable but is not owned by the current sidecar "
            "environment"
        )
    health = state["health"]
    if not health["reachable"]:
        raise OperatorError("Brainstem public health is not reachable")
    if health.get("version") not in (None, release.get("version")):
        raise OperatorError("Brainstem health reports the wrong release version")
    canary = _chat_canary(layout, environment_binding=binding)
    return {
        "health": health,
        "canary": canary,
    }


def _download_verified_installer(
    layout: Layout,
    lock: dict[str, Any] | None = None,
) -> Path:
    lock = lock or load_installer_lock()
    artifact = _installer_artifact(lock)
    suffix = ".ps1" if artifact["platform"] == "windows" else ".sh"
    download_dir = layout.operator_dir / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    target = download_dir / f"installer-{secrets.token_hex(16)}{suffix}"
    try:
        with urllib.request.urlopen(artifact["url"], timeout=60) as response:
            payload = response.read()
        actual_hash = hashlib.sha256(payload).hexdigest()
        if actual_hash != artifact["sha256"]:
            raise OperatorError(
                "Installer SHA-256 does not match bundled installer-lock.json"
            )
        _atomic_write(target, payload, mode=0o700)
        return target
    except (OSError, OperatorError, urllib.error.URLError):
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        raise


def _verify_target_tag(target_release: dict[str, Any]) -> None:
    _validate_target_descriptor(target_release)
    tag_ref = f"refs/tags/{target_release['tag']}"
    result = subprocess.run(
        [
            "git",
            "ls-remote",
            "--tags",
            target_release["repository"],
            tag_ref,
            f"{tag_ref}^{{}}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise OperatorError("Could not resolve the reviewed target tag")
    resolved = {
        line.split()[0]
        for line in result.stdout.splitlines()
        if len(line.split()) >= 2
    }
    if target_release["commit"] not in resolved:
        raise OperatorError(
            "Reviewed target tag does not resolve to the locked commit"
        )


def _verify_local_target_tag(
    layout: Layout,
    target_release: dict[str, Any],
    *,
    required: bool = False,
) -> None:
    if not (layout.source_root / ".git").exists():
        if required:
            raise OperatorError(
                "Installed source has no Git metadata for the locked target tag"
            )
        return
    local = _git(
        layout,
        "rev-parse",
        "--verify",
        f"refs/tags/{target_release['tag']}^{{commit}}",
    )
    if local is None:
        if required:
            raise OperatorError(
                "Installed source does not contain the locked target tag"
            )
        return
    if local != target_release["commit"]:
        raise OperatorError(
            "Local target tag does not resolve to the locked commit"
        )


def _installer_execution(
    layout: Layout,
    action: str,
    target_release: dict[str, Any],
    lock: dict[str, Any],
) -> dict[str, Any]:
    if action == "bootstrap":
        reference_kind = "rolling-tag"
    elif (
        action == "repair"
        and not (layout.source_root / ".git").exists()
    ):
        if target_release != lock["target"]:
            raise OperatorError(
                "Historical repair without Git metadata cannot use a rolling tag"
            )
        reference_kind = "rolling-tag"
    else:
        reference_kind = "exact-commit"
    if reference_kind == "exact-commit":
        arguments = list(
            lock["lifecycle"]["exact_commit_installer_arguments"]
        )
        reference = target_release["commit"]
    else:
        arguments = list(
            lock["lifecycle"]["rolling_tag_installer_arguments"]
        )
        reference = target_release["tag"]
    return {
        "arguments": arguments,
        "repository_ref": {
            "kind": reference_kind,
            "value": reference,
        },
    }


def _run_installer(
    layout: Layout,
    action: str,
    target_release: dict[str, Any],
    lock: dict[str, Any] | None = None,
    execution: dict[str, Any] | None = None,
) -> None:
    _require_default_home(layout, action)
    _validate_target_descriptor(target_release)
    lock = lock or load_installer_lock()
    expected_execution = _installer_execution(
        layout,
        action,
        target_release,
        lock,
    )
    if execution is not None and execution != expected_execution:
        raise OperatorError("Installer execution no longer matches the plan")
    execution = expected_execution
    installer_arguments = execution["arguments"]
    environment = os.environ.copy()
    environment["BRAINSTEM_REPO_URL"] = target_release["repository"]
    environment["BRAINSTEM_REPO_REF"] = execution["repository_ref"]["value"]
    environment["BRAINSTEM_VERSION_URL"] = target_release["version_url"]
    installer_temp = (
        layout.operator_dir
        / "installer-tmp"
        / secrets.token_hex(16)
    )
    installer_temp.mkdir(parents=True, exist_ok=False)
    try:
        installer_temp.chmod(0o700)
    except OSError:
        pass
    environment["TMPDIR"] = str(installer_temp)
    environment["TMP"] = str(installer_temp)
    environment["TEMP"] = str(installer_temp)
    installer: Path | None = None
    try:
        installer = _download_verified_installer(layout, lock)
        if os.name == "nt":
            shell = shutil.which("powershell") or shutil.which("pwsh")
            if not shell:
                raise OperatorError("PowerShell is required by the installer")
            command = [
                shell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(installer),
                *installer_arguments,
            ]
        else:
            command = [
                "bash",
                str(installer),
                *installer_arguments,
            ]
        result = subprocess.run(
            command,
            cwd=layout.home,
            env=environment,
            stdout=sys.stderr,
            stderr=sys.stderr,
            check=False,
        )
    finally:
        if installer is not None:
            try:
                installer.unlink()
            except FileNotFoundError:
                pass
        shutil.rmtree(installer_temp, ignore_errors=True)
    if result.returncode != 0:
        raise OperatorError(
            f"Installer failed with exit code {result.returncode}"
        )


class EvidenceLog:
    def __init__(self, layout: Layout):
        self.layout = layout

    def _read_identity(self) -> dict[str, Any] | None:
        if not self.layout.identity_file.is_file():
            return None
        try:
            identity = json.loads(
                self.layout.identity_file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise OperatorError(f"Invalid RAPPID record: {exc}") from exc
        if (
            identity.get("schema") != "rapp/1"
            or not rappid_valid(identity.get("rappid", ""))
        ):
            raise OperatorError("Invalid RAPP/1 identity record")
        return identity

    def _frames(self) -> list[dict[str, Any]]:
        if not self.layout.frames_dir.is_dir():
            return []
        frames = []
        for path in sorted(self.layout.frames_dir.glob("*.json")):
            try:
                frame = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise OperatorError(
                    f"Unreadable RAPP/1 frame {path.name}"
                ) from exc
            seq = frame.get("seq")
            frame_hash = frame.get("frame_hash")
            if not isinstance(seq, int) or not isinstance(frame_hash, str):
                raise OperatorError(
                    f"Invalid RAPP/1 frame filename: {path.name}"
                )
            expected = f"{seq:020d}-{frame_hash}.json"
            if path.name != expected:
                raise OperatorError(
                    f"RAPP/1 frame filename mismatch: {path.name}"
                )
            frames.append(frame)
        return frames

    def _verify_unlocked(
        self,
        identity: dict[str, Any],
        frames: list[dict[str, Any]],
    ) -> dict[str, Any]:
        head = None
        for frame in frames:
            ok, step, reason = verify_frame(
                frame,
                head=head,
                stream_id_of_record=identity["rappid"],
            )
            if not ok:
                raise OperatorError(
                    f"RAPP/1 chain failed at step {step}: {reason}"
                )
            head = frame
        return {
            "valid": True,
            "frames": len(frames),
            "head": head["frame_hash"] if head else None,
        }

    def _append_unlocked(
        self,
        identity: dict[str, Any],
        frames: list[dict[str, Any]],
        kind: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        head = frames[-1] if frames else None
        utc = fixed_utc()
        if head is not None and utc < head["utc"]:
            utc = head["utc"]
        frame = build_frame(
            kind,
            identity["rappid"],
            0 if head is None else head["seq"] + 1,
            utc,
            payload,
            None if head is None else head["payload_hash"],
        )
        ok, step, reason = verify_frame(
            frame,
            head=head,
            stream_id_of_record=identity["rappid"],
        )
        if not ok:
            raise OperatorError(
                f"Refusing invalid RAPP/1 frame at step {step}: {reason}"
            )
        target = self.layout.frames_dir / (
            f"{frame['seq']:020d}-{frame['frame_hash']}.json"
        )
        _atomic_write(target, canonical_bytes(frame))
        return frame

    def initialize(
        self,
        proposed: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with _append_lock(self.layout.lock_file):
            identity = self._read_identity()
            frames = self._frames()
            if identity is None:
                if frames:
                    raise OperatorError(
                        "RAPP/1 frames exist without an identity"
                    )
                if proposed is None:
                    rappid, anchor = mint_rappid(
                        "aibast",
                        "brainstem-instance",
                    )
                    identity = {
                        "schema": "rapp/1",
                        "rappid": rappid,
                        "kind": "brainstem-instance",
                        "uuid_anchor": str(anchor),
                        "frames": "frames/",
                    }
                else:
                    identity = proposed
                    if (
                        identity.get("schema") != "rapp/1"
                        or not rappid_valid(identity.get("rappid", ""))
                    ):
                        raise OperatorError(
                            "Plan contains an invalid RAPP/1 identity"
                        )
                _atomic_json(self.layout.identity_file, identity)
            elif proposed is not None and identity != proposed:
                raise OperatorError(
                    "Plan instance identity does not match this Brainstem"
                )
            self._verify_unlocked(identity, frames)
            if not frames:
                self._append_unlocked(
                    identity,
                    [],
                    "body.pulse",
                    {
                        "event": "brainstem.instance.created",
                        "actor": {"id": "rappctl"},
                        "operator_version": OPERATOR_VERSION,
                        "privacy": "local-only",
                    },
                )
            return identity

    def ensure(self) -> dict[str, Any]:
        return self.initialize()

    def verify(self) -> dict[str, Any]:
        identity = self._read_identity()
        if identity is None:
            return {"valid": False, "frames": 0, "head": None}
        return self._verify_unlocked(identity, self._frames())

    def append(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.ensure()
        with _append_lock(self.layout.lock_file):
            identity = self._read_identity()
            if identity is None:
                raise OperatorError(
                    "RAPP/1 identity disappeared during append"
                )
            frames = self._frames()
            self._verify_unlocked(identity, frames)
            return self._append_unlocked(identity, frames, kind, payload)

    def frames(self) -> list[dict[str, Any]]:
        identity = self._read_identity()
        if identity is None:
            return []
        frames = self._frames()
        self._verify_unlocked(identity, frames)
        return frames


def inspect(layout: Layout) -> dict[str, Any]:
    evidence = EvidenceLog(layout)
    identity = evidence._read_identity()
    chain = evidence.verify()
    user_state = user_zone_manifest(layout)
    _child_environment, environment_binding = runtime_environment(layout)
    operator_bundle = _operator_bundle_identity()
    return {
        "schema": STATUS_SCHEMA,
        "operator_version": OPERATOR_VERSION,
        "operator_authority": {
            "trust_anchor": dict(TRUST_ANCHOR),
            "bundle_sha256": operator_bundle["sha256"],
        },
        "rapp_spec": "rapp/1",
        "instance_rappid": identity["rappid"] if identity else None,
        "release": release_identity(layout),
        "runtime": managed_runtime_state(
            layout,
            cleanup_stale=False,
            environment_binding=environment_binding,
        ),
        "runtime_environment": environment_binding,
        "evidence": chain,
        "protected_user_zone": {
            "digest": user_state["digest"],
            "count": user_state["count"],
        },
        "ownership": {
            "runtime": "rappctl-managed",
            "soul": "user-owned",
            "agents": "user-owned when untracked or user-modified",
            "memory": "user-owned",
            "config": "user-owned",
        },
    }


def _plan_steps(action: str) -> list[str]:
    return {
        "bootstrap": [
            "back up protected user state before installation",
            "invoke the unchanged installer at the verified rolling tag",
            "verify exact commit, tree, version, managed bytes, and environment",
            "start only a sidecar-owned process",
            "verify public health and a real POST /chat canary",
        ],
        "start": [
            "start only a sidecar-owned Brainstem process",
            "verify public health",
            "leave live POST /chat verification to a separate verify plan",
        ],
        "restart": [
            "stop only the process matching the complete PID record",
            "start a newly recorded Brainstem process",
            "verify public health",
            "leave live POST /chat verification to a separate verify plan",
        ],
        "verify": [
            "verify RAPP/1 evidence and managed runtime bytes",
            "verify public health and a real POST /chat canary",
        ],
        "update": [
            "back up the exact release, managed environment, and protected user state",
            "invoke the unchanged installer at the exact reviewed commit",
            "verify exact target, environment, and protected user state",
            "verify public health and a real POST /chat canary",
            "restore the prior running or stopped state",
        ],
        "repair": [
            "back up the exact release, managed environment, and protected user state",
            "invoke the unchanged installer at the exact reviewed commit when Git metadata supports it",
            "verify exact target, environment, and protected user state",
            "verify public health and a real POST /chat canary",
            "restore the prior running or stopped state",
        ],
        "rollback": [
            "select a release with matching successful verification evidence",
            "back up the pre-rollback release, managed environment, and protected user state",
            "invoke the unchanged installer at the historical exact commit",
            "verify public health and a real POST /chat canary",
            "restore the pre-rollback release on any failure",
        ],
    }[action]


def _canary_evidence_valid(value: Any) -> bool:
    return bool(
        isinstance(value, dict)
        and isinstance(value.get("http_status"), int)
        and 200 <= value["http_status"] < 300
        and _valid_hex(value.get("response_sha256"), 64)
    )


def _verified_releases(log: EvidenceLog) -> list[dict[str, Any]]:
    applies: dict[str, dict[str, Any]] = {}
    verified = []
    for frame in log.frames():
        payload = frame.get("payload", {})
        plan_hash = payload.get("plan_hash")
        if (
            frame.get("kind") == "operator.apply"
            and payload.get("status") == "succeeded"
            and isinstance(plan_hash, str)
        ):
            applies[plan_hash] = payload
            continue
        if (
            frame.get("kind") != "operator.verify"
            or payload.get("status") != "succeeded"
            or not isinstance(plan_hash, str)
            or not _canary_evidence_valid(payload.get("canary"))
        ):
            continue
        apply_payload = applies.get(plan_hash)
        release = payload.get("release")
        target = payload.get("target_release")
        if (
            not isinstance(apply_payload, dict)
            or not isinstance(release, dict)
            or not isinstance(target, dict)
            or apply_payload.get("after_release", {}).get("release_hash")
            != release.get("release_hash")
        ):
            continue
        try:
            _validate_target_descriptor(target)
        except OperatorError:
            continue
        release_matches = (
            _target_matches_release(target, release)
            if "managed_environment" in release
            else _target_source_matches_release(target, release)
        )
        if not release_matches:
            continue
        verified.append(
            {
                "release": release,
                "target": target,
                "plan_hash": plan_hash,
            }
        )
    return verified


def _previous_release(
    log: EvidenceLog,
    current: dict[str, Any],
) -> dict[str, Any]:
    current_hash = current.get("release_hash")
    candidates = [
        candidate
        for candidate in _verified_releases(log)
        if candidate["release"].get("release_hash") != current_hash
    ]
    if not candidates:
        raise OperatorError(
            "No previous release with matching successful canary evidence "
            "is available"
        )
    return candidates[-1]["target"]


def _target_for_current(
    log: EvidenceLog,
    lock: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    if _target_matches_release(lock["target"], current):
        return dict(lock["target"])
    for candidate in reversed(_verified_releases(log)):
        if (
            candidate["release"].get("release_hash")
            == current.get("release_hash")
        ):
            return candidate["target"]
    raise OperatorError(
        "The installed release has no exact verified target identity"
    )


def _new_instance_identity() -> dict[str, Any]:
    rappid, anchor = mint_rappid("aibast", "brainstem-instance")
    return {
        "schema": "rapp/1",
        "rappid": rappid,
        "kind": "brainstem-instance",
        "uuid_anchor": str(anchor),
        "frames": "frames/",
    }


def _expected_postconditions(
    action: str,
    current: dict[str, Any],
    runtime: dict[str, Any],
    target: dict[str, Any],
    user_state: dict[str, Any],
    allowed_additions: list[str],
    environment_binding: dict[str, Any],
) -> dict[str, Any]:
    if action in INSTALLER_ACTIONS:
        release_condition = {
            "mode": "exact-target",
            "target": target,
        }
    else:
        release_condition = {
            "mode": "unchanged",
            "release_hash": current.get("release_hash"),
        }
    if action in {"update", "repair", "rollback"}:
        final_state = runtime["state"]
    elif action == "verify":
        final_state = "running"
    else:
        final_state = "running"
    return {
        "release": release_condition,
        "runtime_state": final_state,
        "protected_user_zone_digest": user_state["digest"],
        "protected_user_zone_count": user_state["count"],
        "protected_user_zone_allowed_additions": allowed_additions,
        "runtime_environment_sha256": environment_binding["sha256"],
        "effective_port": environment_binding["effective_port"],
        "allow_user_zone_initialization": (
            action == "bootstrap" and not current["installed"]
        ),
        "live_chat_canary": action not in {"start", "restart"},
    }


def create_plan(layout: Layout, action: str, actor: str) -> dict[str, Any]:
    if action not in SUPPORTED_ACTIONS:
        raise OperatorError(f"Unsupported action: {action}")
    if not isinstance(actor, str) or not _SAFE_ACTOR.fullmatch(actor):
        raise OperatorError("Lifecycle actor is invalid")
    _require_default_home(layout, action)
    log = EvidenceLog(layout)
    identity = log._read_identity()
    frames = log._frames()
    if identity is None and frames:
        raise OperatorError("RAPP/1 frames exist without an identity")
    if identity is not None:
        log._verify_unlocked(identity, frames)
    lock = load_installer_lock()
    current = release_identity(layout)
    child_environment, environment_binding = runtime_environment(layout)
    runtime = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=environment_binding,
    )
    _require_known_runtime(runtime)
    user_state = user_zone_manifest(layout)
    if (
        runtime["state"] == "running"
        and not runtime["lifecycle_owned"]
        and not (
            runtime["pid_record"] in {"owned", "legacy-owned"}
            and action == "restart"
        )
    ):
        raise OperatorError(
            "The running Brainstem is chat-only until a sidecar-owned restart "
            "establishes the current environment binding"
        )
    if action == "bootstrap" and current["installed"]:
        raise OperatorError("Brainstem is already installed; bootstrap refused")
    if action in {"start", "restart", "verify", "update", "repair", "rollback"}:
        if not current["installed"]:
            raise OperatorError("Brainstem runtime is not installed")
    if action == "update" and _target_matches_release(lock["target"], current):
        raise OperatorError(
            "Brainstem is already at the exact reviewed target; "
            "use verify or repair"
        )
    if action == "repair" and _target_matches_release(lock["target"], current):
        if runtime["health"]["reachable"]:
            raise OperatorError(
                "Brainstem already satisfies the reviewed release and health "
                "postconditions"
            )
    if action == "rollback":
        target = _previous_release(log, current)
    elif action in INSTALLER_ACTIONS:
        target = dict(lock["target"])
    elif current["installed"]:
        target = _target_for_current(log, lock, current)
    else:
        target = dict(lock["target"])
    installer_execution = (
        _installer_execution(layout, action, target, lock)
        if action in INSTALLER_ACTIONS
        else None
    )
    allowed_additions = _planned_user_zone_additions(
        action,
        user_state,
        child_environment,
    )
    proposed_identity = identity or _new_instance_identity()
    trust = {
        "installer_lock_sha256": lock["_digest"],
        "installer": _installer_artifact(lock),
        "reviewed_target": dict(lock["target"]),
    }
    base = {
        "schema": PLAN_SCHEMA,
        "action": action,
        "actor": actor,
        "created_utc": fixed_utc(),
        "instance_rappid": proposed_identity["rappid"],
        "instance_identity": proposed_identity,
        "current_release": current,
        "managed_runtime": runtime,
        "trust": trust,
        "target_release": target,
        "installer_execution": installer_execution,
        "operator_bundle": _operator_bundle_identity(),
        "runtime_environment": environment_binding,
        "protected_user_zone": {
            "digest": user_state["digest"],
            "count": user_state["count"],
            "allowed_additions": allowed_additions,
        },
        "expected_postconditions": _expected_postconditions(
            action,
            current,
            runtime,
            target,
            user_state,
            allowed_additions,
            environment_binding,
        ),
        "consent": {
            "required": action != "verify",
            "binding": "exact-plan-hash",
        },
        "steps": _plan_steps(action),
        "user_zone_writes": False,
    }
    plan = dict(base)
    plan["plan_hash"] = H("rapp/operator-plan/3", base)
    _atomic_write(
        layout.plans_dir / f"{plan['plan_hash']}.json",
        canonical_bytes(plan),
    )
    log.initialize(proposed_identity)
    log.append(
        "operator.plan",
        {
            "event": "brainstem.lifecycle.plan",
            "actor": {"id": actor},
            "action": action,
            "plan_hash": plan["plan_hash"],
            "current_release": current,
            "managed_runtime": runtime,
            "installer_lock_sha256": trust["installer_lock_sha256"],
            "installer_sha256": trust["installer"]["sha256"],
            "installer_execution": installer_execution,
            "target_release": target,
            "operator_bundle_sha256": plan["operator_bundle"]["sha256"],
            "protected_user_zone_digest": user_state["digest"],
            "protected_user_zone_count": user_state["count"],
            "protected_user_zone_allowed_additions": allowed_additions,
            "runtime_environment": environment_binding,
            "expected_postconditions": plan["expected_postconditions"],
            "user_zone_writes": False,
        },
    )
    return plan


def _load_plan(layout: Layout, plan_hash: str) -> dict[str, Any]:
    path = layout.plans_dir / f"{plan_hash}.json"
    if not path.is_file():
        raise OperatorError("Unknown plan hash")
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperatorError("Stored plan is unreadable") from exc
    actual_hash = plan.pop("plan_hash", None)
    expected_hash = H("rapp/operator-plan/3", plan)
    plan["plan_hash"] = actual_hash
    if (
        plan.get("schema") != PLAN_SCHEMA
        or actual_hash != plan_hash
        or expected_hash != plan_hash
    ):
        raise OperatorError("Stored plan hash does not verify")
    return plan


def _prior_apply(
    log: EvidenceLog,
    plan_hash: str,
    *,
    require_verification: bool = False,
) -> dict[str, Any] | None:
    frames = log.frames()
    latest = None
    for frame in reversed(frames):
        payload = frame.get("payload", {})
        if (
            frame.get("kind") == "operator.apply"
            and payload.get("plan_hash") == plan_hash
        ):
            latest = frame
            break
    if latest is None or latest["payload"].get("status") != "succeeded":
        return None
    if not require_verification:
        return latest
    for frame in frames:
        payload = frame.get("payload", {})
        if (
            frame.get("seq", -1) > latest.get("seq", -1)
            and frame.get("kind") == "operator.verify"
            and payload.get("plan_hash") == plan_hash
            and payload.get("status") == "succeeded"
            and _canary_evidence_valid(payload.get("canary"))
            and payload.get("release", {}).get("release_hash")
            == latest["payload"].get("after_release", {}).get("release_hash")
        ):
            return latest
    return None


def _validate_plan_bindings(
    layout: Layout,
    plan: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    lock = load_installer_lock()
    artifact = _installer_artifact(lock)
    if plan["trust"].get("installer_lock_sha256") != lock["_digest"]:
        raise OperatorError("Plan drift: bundled installer-lock.json changed")
    if plan["trust"].get("installer") != artifact:
        raise OperatorError("Plan drift: exact installer URL or SHA-256 changed")
    if plan["trust"].get("reviewed_target") != lock["target"]:
        raise OperatorError("Plan drift: reviewed target release changed")
    if plan.get("operator_bundle") != _operator_bundle_identity():
        raise OperatorError("Plan drift: local operator bundle changed")
    child_environment, environment_binding = runtime_environment(layout)
    if plan.get("runtime_environment") != environment_binding:
        raise OperatorError("Plan drift: runtime environment changed")
    current = release_identity(layout)
    if plan.get("current_release") != current:
        raise OperatorError("Plan drift: installed release state changed")
    runtime = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=environment_binding,
    )
    if plan.get("managed_runtime") != runtime:
        raise OperatorError("Plan drift: managed runtime state changed")
    _require_known_runtime(runtime)
    user_state = user_zone_manifest(layout)
    planned_user = plan.get("protected_user_zone", {})
    allowed_additions = planned_user.get("allowed_additions")
    if (
        planned_user.get("digest") != user_state["digest"]
        or planned_user.get("count") != user_state["count"]
        or not isinstance(allowed_additions, list)
        or allowed_additions
        != _planned_user_zone_additions(
            plan["action"],
            user_state,
            child_environment,
        )
    ):
        raise OperatorError("Plan drift: protected user state changed")
    if plan["action"] in {"bootstrap", "update", "repair"}:
        if plan.get("target_release") != lock["target"]:
            raise OperatorError("Plan drift: mutation target is not reviewed")
    if plan["action"] == "rollback":
        verified_targets = [
            item["target"] for item in _verified_releases(EvidenceLog(layout))
        ]
        if plan.get("target_release") not in verified_targets:
            raise OperatorError(
                "Plan drift: rollback target no longer has verification evidence"
            )
    if plan["action"] in INSTALLER_ACTIONS:
        if os.name == "nt" and _path_is_within(
            Path(sys.executable),
            layout.venv_dir,
        ):
            raise OperatorError(
                "Windows installer-backed lifecycle operations must run the "
                "current plugin operator outside ~/.brainstem/venv so that "
                "the exact managed environment can be restored"
            )
        expected_execution = _installer_execution(
            layout,
            plan["action"],
            plan["target_release"],
            lock,
        )
        if plan.get("installer_execution") != expected_execution:
            raise OperatorError(
                "Plan drift: installer execution target changed"
            )
        if plan["action"] in {"bootstrap", "update", "repair"}:
            _verify_target_tag(lock["target"])
    elif plan.get("installer_execution") is not None:
        raise OperatorError("Plan drift: unexpected installer execution")
    return lock, user_state


def _make_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def _copy_user_entry(
    layout: Layout,
    backup_files: Path,
    entry: dict[str, Any],
) -> None:
    if entry["kind"] == "absent":
        return
    source = layout.runtime_dir / Path(entry["path"])
    destination = backup_files / Path(entry["path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if entry["kind"] == "directory":
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copystat(source, destination, follow_symlinks=False)
    elif entry["kind"] == "symlink":
        destination.symlink_to(os.readlink(source))
    elif entry["kind"] == "file":
        shutil.copy2(source, destination, follow_symlinks=False)
    else:
        raise OperatorError("Unsupported user backup entry")


def _capture_transaction(
    layout: Layout,
    plan: dict[str, Any],
    before_user: dict[str, Any],
) -> TransactionSnapshot:
    transaction_id = secrets.token_hex(16)
    backup_root = layout.backups_dir / transaction_id
    _make_private_directory(backup_root)
    before_release = release_identity(layout)
    before_runtime = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=plan["runtime_environment"],
    )
    release_backup = backup_root / "release" / "source"
    release_present = layout.source_root.exists()
    if release_present:
        release_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            layout.source_root,
            release_backup,
            symlinks=True,
        )
    venv_backup = backup_root / "runtime" / "venv"
    venv_present = layout.venv_dir.exists()
    if venv_present:
        venv_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            layout.venv_dir,
            venv_backup,
            symlinks=True,
        )
    user_root = backup_root / "user"
    user_files = user_root / "files"
    user_files.mkdir(parents=True, exist_ok=True)
    try:
        user_root.chmod(0o700)
        user_files.chmod(0o700)
    except OSError:
        pass
    _atomic_json(user_root / "manifest.json", before_user)
    for entry in before_user["entries"]:
        _copy_user_entry(layout, user_files, entry)
        if _manifest_entry_at(user_files, entry["path"]) != entry:
            raise OperatorError(
                "Durable protected user-state backup did not verify"
            )
    rebound = _bound_user_manifest(layout, before_user)
    current_user = user_zone_manifest(layout)
    if (
        rebound["digest"] != before_user["digest"]
        or current_user["digest"] != before_user["digest"]
        or current_user["count"] != before_user["count"]
    ):
        raise OperatorError(
            "Protected user state drifted while its backup was created"
        )
    if release_identity(layout) != before_release:
        raise OperatorError(
            "Release or managed environment drifted while its backup was created"
        )
    snapshot = TransactionSnapshot(
        transaction_id=transaction_id,
        action=plan["action"],
        backup_root=backup_root,
        release_backup=release_backup,
        release_present=release_present,
        venv_backup=venv_backup,
        venv_present=venv_present,
        before_release=before_release,
        before_runtime=before_runtime,
        before_environment=plan["runtime_environment"],
        before_user=before_user,
    )
    _atomic_json(
        backup_root / "transaction.json",
        {
            "schema": "rapp-brainstem-transaction-backup/1",
            "transaction_id": transaction_id,
            "action": plan["action"],
            "created_utc": fixed_utc(),
            "release_present": release_present,
            "venv_present": venv_present,
            "before_release": snapshot.before_release,
            "before_runtime_state": snapshot.before_runtime["state"],
            "protected_user_zone_digest": before_user["digest"],
            "protected_user_zone_count": before_user["count"],
            "managed_environment_sha256": before_release[
                "managed_environment"
            ]["sha256"],
        },
    )
    return snapshot


def _remove_path(path: Path) -> None:
    try:
        path_stat = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISDIR(path_stat.st_mode) and not stat.S_ISLNK(path_stat.st_mode):
        shutil.rmtree(path)
    else:
        path.unlink()


def _restore_user_state(
    layout: Layout,
    snapshot: TransactionSnapshot,
) -> None:
    current = user_zone_manifest(layout)
    before_paths = {
        entry["path"] for entry in snapshot.before_user["entries"]
    }
    for entry in sorted(
        current["entries"],
        key=lambda value: value["path"].count("/"),
        reverse=True,
    ):
        if entry["path"] not in before_paths:
            _remove_path(layout.runtime_dir / Path(entry["path"]))
    backup_files = snapshot.backup_root / "user" / "files"
    for entry in sorted(
        snapshot.before_user["entries"],
        key=lambda value: value["path"].count("/"),
        reverse=True,
    ):
        destination = layout.runtime_dir / Path(entry["path"])
        _remove_path(destination)
    for entry in sorted(
        snapshot.before_user["entries"],
        key=lambda value: value["path"].count("/"),
    ):
        if entry["kind"] == "absent":
            continue
        source = backup_files / Path(entry["path"])
        destination = layout.runtime_dir / Path(entry["path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        if entry["kind"] == "directory":
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copystat(source, destination, follow_symlinks=False)
        elif entry["kind"] == "symlink":
            destination.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, destination, follow_symlinks=False)


def _restore_release(
    layout: Layout,
    snapshot: TransactionSnapshot,
) -> None:
    restore_parent = layout.operator_dir / "restore"
    restore_parent.mkdir(parents=True, exist_ok=True)
    staged = restore_parent / f"{snapshot.transaction_id}-staged"
    displaced = restore_parent / f"{snapshot.transaction_id}-displaced"
    _remove_path(staged)
    _remove_path(displaced)
    if snapshot.release_present:
        shutil.copytree(
            snapshot.release_backup,
            staged,
            symlinks=True,
        )
    if layout.source_root.exists():
        os.replace(layout.source_root, displaced)
    try:
        if snapshot.release_present:
            layout.source_root.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, layout.source_root)
        restored = release_identity(layout)
        source_fields = {
            key: value
            for key, value in restored.items()
            if key not in {"managed_environment", "release_hash"}
        }
        expected_source_fields = {
            key: value
            for key, value in snapshot.before_release.items()
            if key not in {"managed_environment", "release_hash"}
        }
        if source_fields != expected_source_fields:
            raise OperatorError(
                "Restored source does not match the pre-operation release"
            )
    except Exception:
        if layout.source_root.exists():
            _remove_path(layout.source_root)
        if displaced.exists():
            os.replace(displaced, layout.source_root)
        raise
    if displaced.exists():
        failed_copy = snapshot.backup_root / "failed-release"
        _remove_path(failed_copy)
        os.replace(displaced, failed_copy)


def _restore_venv(
    layout: Layout,
    snapshot: TransactionSnapshot,
) -> None:
    restore_parent = layout.operator_dir / "restore"
    restore_parent.mkdir(parents=True, exist_ok=True)
    staged = restore_parent / f"{snapshot.transaction_id}-venv-staged"
    displaced = restore_parent / f"{snapshot.transaction_id}-venv-displaced"
    _remove_path(staged)
    _remove_path(displaced)
    if snapshot.venv_present:
        shutil.copytree(
            snapshot.venv_backup,
            staged,
            symlinks=True,
        )
    if layout.venv_dir.exists():
        os.replace(layout.venv_dir, displaced)
    try:
        if snapshot.venv_present:
            layout.venv_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, layout.venv_dir)
        restored = managed_environment_identity(layout)
        if restored != snapshot.before_release["managed_environment"]:
            raise OperatorError(
                "Restored managed environment does not match its backup"
            )
    except Exception:
        if layout.venv_dir.exists():
            _remove_path(layout.venv_dir)
        if displaced.exists():
            os.replace(displaced, layout.venv_dir)
        raise
    if displaced.exists():
        failed_copy = snapshot.backup_root / "failed-venv"
        _remove_path(failed_copy)
        os.replace(displaced, failed_copy)


def _verify_user_preserved(
    layout: Layout,
    before: dict[str, Any],
    allowed_additions: list[str] | None = None,
) -> dict[str, Any]:
    allowed = set(allowed_additions or [])
    current = user_zone_manifest(layout)
    before_entries = {
        entry["path"]: entry for entry in before.get("entries", [])
    }
    current_entries = {
        entry["path"]: entry for entry in current.get("entries", [])
    }
    changed = [
        path
        for path, entry in before_entries.items()
        if current_entries.get(path) != entry
    ]
    new_paths = sorted(set(current_entries) - set(before_entries))
    unexpected = [path for path in new_paths if path not in allowed]
    if changed or unexpected:
        raise OperatorError(
            "Protected user state changed during the lifecycle operation"
        )
    return current


def _state_category(state: dict[str, Any]) -> str:
    return str(state.get("state"))


def _restore_transaction(
    layout: Layout,
    snapshot: TransactionSnapshot,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {
        "status": "failed",
        "release_restored": False,
        "managed_environment_restored": False,
        "user_state_restored": False,
        "runtime_state_restored": False,
    }
    try:
        current_state = managed_runtime_state(
            layout,
            cleanup_stale=True,
            environment_binding=snapshot.before_environment,
        )
        _require_known_runtime(current_state)
        if current_state["state"] == "running":
            _stop_brainstem(layout, snapshot.before_environment)
        current_release = release_identity(layout)
        source_keys = {
            key
            for key in snapshot.before_release
            if key not in {"managed_environment", "release_hash"}
        }
        if any(
            current_release.get(key) != snapshot.before_release.get(key)
            for key in source_keys
        ):
            _restore_release(layout, snapshot)
        outcome["release_restored"] = True
        if (
            snapshot.action in INSTALLER_ACTIONS
            or managed_environment_identity(layout)
            != snapshot.before_release["managed_environment"]
        ):
            _restore_venv(layout, snapshot)
        outcome["managed_environment_restored"] = True
        _restore_user_state(layout, snapshot)
        restored_user = user_zone_manifest(layout)
        if (
            restored_user["digest"] != snapshot.before_user["digest"]
            or restored_user["count"] != snapshot.before_user["count"]
        ):
            raise OperatorError("Protected user-state restoration did not verify")
        outcome["user_state_restored"] = True
        desired_state = _state_category(snapshot.before_runtime)
        if desired_state == "running":
            _start_brainstem(layout, snapshot.before_environment)
            if snapshot.before_runtime["health"]["reachable"]:
                restored_release = release_identity(layout)
                restored_runtime = managed_runtime_state(
                    layout,
                    cleanup_stale=False,
                    environment_binding=snapshot.before_environment,
                )
                if (
                    not restored_runtime["lifecycle_owned"]
                    or not restored_runtime["health"]["reachable"]
                    or restored_runtime["health"].get("version")
                    not in (None, restored_release.get("version"))
                ):
                    raise OperatorError(
                        "Restored runtime public health did not verify"
                    )
        elif desired_state == "stopped":
            stopped = managed_runtime_state(layout, cleanup_stale=True)
            if stopped["state"] != "stopped":
                raise OperatorError("Stopped runtime state was not restored")
        else:
            raise OperatorError(
                "Cannot restore a transaction that began with an unknown process"
            )
        if release_identity(layout) != snapshot.before_release:
            raise OperatorError("Pre-operation release restoration did not verify")
        final_user = user_zone_manifest(layout)
        if (
            final_user["digest"] != snapshot.before_user["digest"]
            or final_user["count"] != snapshot.before_user["count"]
        ):
            raise OperatorError(
                "Pre-operation protected user state did not remain restored"
            )
        if (
            managed_runtime_state(
                layout,
                cleanup_stale=False,
                environment_binding=snapshot.before_environment,
            )["state"]
            != desired_state
        ):
            raise OperatorError("Pre-operation running state did not verify")
        outcome["runtime_state_restored"] = True
        outcome["status"] = "succeeded"
        return outcome
    except Exception as exc:
        outcome["error"] = str(exc).replace(str(layout.home), "~/.brainstem")
        return outcome


def _execute_action(
    layout: Layout,
    plan: dict[str, Any],
    lock: dict[str, Any],
    snapshot: TransactionSnapshot | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    action = plan["action"]
    before_release = release_identity(layout)
    environment_binding = plan["runtime_environment"]
    before_runtime = managed_runtime_state(
        layout,
        cleanup_stale=True,
        environment_binding=environment_binding,
    )
    _require_known_runtime(before_runtime)
    if action == "verify":
        if not before_release["installed"] or not before_release["managed_clean"]:
            raise OperatorError(
                "Brainstem release is incomplete or managed bytes are modified"
            )
        EvidenceLog(layout).verify()
        live = _verify_live(
            layout,
            before_release,
            environment_binding,
        )
        return (
            {"changed": False, "state": "verified"},
            live,
        )
    if snapshot is None:
        raise OperatorError("Mutation transaction snapshot is missing")
    if action == "start":
        result = _start_brainstem(layout, environment_binding)
        return result, None
    if action == "restart":
        result = _restart_brainstem(layout, environment_binding)
        return result, None
    if action not in INSTALLER_ACTIONS:
        raise OperatorError(f"Unsupported action: {action}")
    if before_runtime["state"] == "running":
        _stop_brainstem(layout, environment_binding)
    target = plan["target_release"]
    _run_installer(
        layout,
        action,
        target,
        lock,
        plan["installer_execution"],
    )
    after_install = release_identity(layout)
    _assert_exact_target(target, after_install)
    if action in {"bootstrap", "update", "rollback"}:
        if after_install.get("release_hash") == before_release.get("release_hash"):
            raise OperatorError(
                "Installer did not change the release when an exact target "
                "transition was required"
            )
    allowed_additions = plan["protected_user_zone"]["allowed_additions"]
    _verify_user_preserved(
        layout,
        snapshot.before_user,
        allowed_additions,
    )
    started = _start_brainstem(layout, environment_binding)
    live = _verify_live(layout, after_install, environment_binding)
    after_user = _verify_user_preserved(
        layout,
        snapshot.before_user,
        allowed_additions,
    )
    final_state = "running"
    if (
        action in {"update", "repair", "rollback"}
        and snapshot.before_runtime["state"] == "stopped"
    ):
        _stop_brainstem(layout, environment_binding)
        final_state = "stopped"
    result = {
        "changed": (
            before_release.get("release_hash")
            != after_install.get("release_hash")
        ),
        "state": final_state,
        "start_changed": started["changed"],
        "protected_user_zone_digest": after_user["digest"],
        "protected_user_zone_count": after_user["count"],
        "runtime_environment_sha256": environment_binding["sha256"],
    }
    return result, live


def _assert_postconditions(
    layout: Layout,
    plan: dict[str, Any],
    snapshot: TransactionSnapshot | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _child_environment, environment_binding = runtime_environment(layout)
    expected = plan["expected_postconditions"]
    if (
        environment_binding != plan["runtime_environment"]
        or environment_binding["sha256"]
        != expected["runtime_environment_sha256"]
        or environment_binding["effective_port"] != expected["effective_port"]
    ):
        raise OperatorError("Runtime environment changed during apply")
    release = release_identity(layout)
    runtime = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=environment_binding,
    )
    user_state = user_zone_manifest(layout)
    release_condition = expected["release"]
    if release_condition["mode"] == "exact-target":
        _assert_exact_target(release_condition["target"], release)
    elif release.get("release_hash") != release_condition.get("release_hash"):
        raise OperatorError("Release changed despite an unchanged postcondition")
    if runtime["state"] != expected["runtime_state"]:
        raise OperatorError("Managed runtime did not reach its planned state")
    if runtime["state"] == "running" and not runtime["health"]["reachable"]:
        raise OperatorError("Managed runtime is running but public health failed")
    if runtime["state"] == "running" and not runtime["lifecycle_owned"]:
        raise OperatorError(
            "Managed runtime is not bound to the planned environment"
        )
    if snapshot is not None:
        user_state = _verify_user_preserved(
            layout,
            snapshot.before_user,
            expected["protected_user_zone_allowed_additions"],
        )
    elif (
        user_state["digest"] != expected["protected_user_zone_digest"]
        or user_state["count"] != expected["protected_user_zone_count"]
    ):
        raise OperatorError(
            "Protected user state changed during the lifecycle operation"
        )
    return release, runtime, user_state


def _prior_postconditions_hold(
    layout: Layout,
    plan: dict[str, Any],
    prior: dict[str, Any],
    *,
    require_live: bool = True,
) -> bool:
    payload = prior.get("payload", {})
    current_release = release_identity(layout)
    if payload.get("after_release") != current_release:
        return False
    current_user = user_zone_manifest(layout)
    if (
        payload.get("after_user_zone_digest") != current_user["digest"]
        or payload.get("after_user_zone_count") != current_user["count"]
    ):
        return False
    _child_environment, environment_binding = runtime_environment(layout)
    if environment_binding != plan.get("runtime_environment"):
        return False
    if (
        payload.get("runtime_environment_sha256")
        != environment_binding["sha256"]
    ):
        return False
    expected_state = payload.get("after_runtime_state")
    current_runtime = managed_runtime_state(
        layout,
        cleanup_stale=False,
        environment_binding=environment_binding,
    )
    if current_runtime["state"] != expected_state:
        return False
    if expected_state == "running":
        if not current_runtime["health"]["reachable"]:
            return False
        if require_live:
            try:
                _verify_live(
                    layout,
                    current_release,
                    environment_binding,
                )
            except OperatorError:
                return False
    return True


def apply_plan(
    layout: Layout,
    plan_hash: str,
    approval: str | None,
) -> dict[str, Any]:
    plan = _load_plan(layout, plan_hash)
    if plan["consent"]["required"] and approval != plan_hash:
        raise OperatorError("Approval must equal the exact plan hash")
    _require_default_home(layout, plan["action"])
    with _operation_lock(layout):
        log = EvidenceLog(layout)
        log.initialize(plan.get("instance_identity"))
        prior = _prior_apply(log, plan_hash, require_verification=True)
        if prior is not None:
            if _prior_postconditions_hold(layout, plan, prior):
                return {
                    "status": "already_converged",
                    "plan_hash": plan_hash,
                    "result": prior["payload"].get("result"),
                    "frame_hash": prior["frame_hash"],
                }
            raise OperatorError(
                "Previously applied plan no longer satisfies its "
                "postconditions; create a new plan"
            )
        prior_pending = _prior_apply(log, plan_hash)
        if prior_pending is not None and plan["action"] in {"start", "restart"}:
            if _prior_postconditions_hold(
                layout,
                plan,
                prior_pending,
                require_live=False,
            ):
                return {
                    "status": "already_applied",
                    "verification": "pending-live-canary",
                    "plan_hash": plan_hash,
                    "result": prior_pending["payload"].get("result"),
                    "frame_hash": prior_pending["frame_hash"],
                }
            raise OperatorError(
                "Previously applied plan no longer satisfies its "
                "postconditions; create a new plan"
            )
        lock, before_user = _validate_plan_bindings(layout, plan)
        snapshot = None
        if plan["action"] in TRANSACTIONAL_ACTIONS:
            snapshot = _capture_transaction(layout, plan, before_user)
        before_release = release_identity(layout)
        before_runtime = managed_runtime_state(
            layout,
            cleanup_stale=False,
            environment_binding=plan["runtime_environment"],
        )
        try:
            result, live = _execute_action(layout, plan, lock, snapshot)
            after_release, after_runtime, after_user = _assert_postconditions(
                layout,
                plan,
                snapshot,
            )
            apply_frame = log.append(
                "operator.apply",
                {
                    "event": "brainstem.lifecycle.apply",
                    "actor": {"id": plan["actor"]},
                    "action": plan["action"],
                    "plan_hash": plan_hash,
                    "status": "succeeded",
                    "result": result,
                    "before_release": before_release,
                    "after_release": after_release,
                    "target_release": plan["target_release"],
                    "installer_execution": plan["installer_execution"],
                    "before_runtime_state": before_runtime["state"],
                    "after_runtime_state": after_runtime["state"],
                    "runtime_environment_sha256": plan[
                        "runtime_environment"
                    ]["sha256"],
                    "effective_port": plan["runtime_environment"][
                        "effective_port"
                    ],
                    "protected_user_zone_digest": before_user["digest"],
                    "protected_user_zone_count": before_user["count"],
                    "after_user_zone_digest": after_user["digest"],
                    "after_user_zone_count": after_user["count"],
                    "protected_user_state": "preserved",
                    "user_zone_writes": False,
                },
            )
            response = {
                "status": "succeeded",
                "plan_hash": plan_hash,
                "result": result,
                "frame_hash": apply_frame["frame_hash"],
            }
            if live is None:
                response["verification"] = "pending-live-canary"
                return response
            verification = log.append(
                "operator.verify",
                {
                    "event": "brainstem.lifecycle.verified",
                    "actor": {"id": plan["actor"]},
                    "action": plan["action"],
                    "plan_hash": plan_hash,
                    "status": "succeeded",
                    "release": after_release,
                    "target_release": plan["target_release"],
                    "health": live["health"],
                    "canary": live["canary"],
                    "protected_user_zone_digest": after_user["digest"],
                    "protected_user_zone_count": after_user["count"],
                    "runtime_environment_sha256": plan[
                        "runtime_environment"
                    ]["sha256"],
                    "managed_environment_sha256": after_release[
                        "managed_environment"
                    ]["sha256"],
                },
            )
            response["verification_frame_hash"] = verification["frame_hash"]
            return response
        except Exception as exc:
            rollback = (
                _restore_transaction(layout, snapshot)
                if snapshot is not None
                else {"status": "not-required"}
            )
            log.append(
                "operator.apply",
                {
                    "event": "brainstem.lifecycle.apply",
                    "actor": {"id": plan["actor"]},
                    "action": plan["action"],
                    "plan_hash": plan_hash,
                    "status": "failed",
                    "error": str(exc).replace(
                        str(layout.home),
                        "~/.brainstem",
                    ),
                    "before_release": before_release,
                    "after_release": release_identity(layout),
                    "target_release": plan["target_release"],
                    "installer_execution": plan["installer_execution"],
                    "protected_user_zone_digest": before_user["digest"],
                    "protected_user_zone_count": before_user["count"],
                    "runtime_environment_sha256": plan[
                        "runtime_environment"
                    ]["sha256"],
                    "rollback": rollback,
                    "user_zone_writes": False,
                },
            )
            if rollback.get("status") == "failed":
                raise OperatorError(
                    f"{exc}; rollback also failed: {rollback.get('error')}"
                ) from exc
            raise


def reconcile_install(
    layout: Layout,
    actor: str,
    envelope_path: str | Path,
    envelope_sha256: str,
) -> dict[str, Any]:
    _require_default_home(layout, "bootstrap")
    with _operation_lock(layout):
        envelope, lock, current, runtime = _validate_bootstrap_envelope(
            layout,
            actor,
            envelope_path,
            envelope_sha256,
        )
        log = EvidenceLog(layout)
        identity = log.ensure()
        prior = _prior_apply(log, envelope_sha256)
        if prior is not None:
            payload = prior["payload"]
            if (
                payload.get("after_release") == current
                and payload.get("bootstrap_envelope_sha256")
                == envelope_sha256
            ):
                return {
                    "status": "already_converged",
                    "release": current,
                    "evidence": log.verify(),
                    "instance_rappid": identity["rappid"],
                    "verification": "pending-live-canary",
                }
            raise OperatorError(
                "Reconciled bootstrap release no longer matches its receipt"
            )
        envelope, lock, current, runtime = _validate_bootstrap_envelope(
            layout,
            actor,
            envelope_path,
            envelope_sha256,
        )
        current_user = user_zone_manifest(layout)
        frame = log.append(
            "operator.apply",
            {
                "event": "brainstem.lifecycle.apply",
                "actor": {"id": envelope["actor"]},
                "action": "bootstrap",
                "plan_hash": envelope_sha256,
                "bootstrap_envelope_sha256": envelope_sha256,
                "status": "succeeded",
                "result": {
                    "changed": True,
                    "state": "installed",
                    "verification": "pending-live-canary",
                },
                "before_release": {
                    "installed": False,
                    "release_hash": None,
                },
                "after_release": current,
                "target_release": envelope["target_release"],
                "before_runtime_state": "stopped",
                "after_runtime_state": runtime["state"],
                "installer_lock_sha256": lock["_digest"],
                "installer": envelope["installer"],
                "installer_sha256": envelope["installer"]["sha256"],
                "installer_arguments": envelope["installer"]["arguments"],
                "installer_repository_ref": envelope["installer"][
                    "repository_ref"
                ],
                "operator_bundle_sha256": envelope["operator_bundle"]["sha256"],
                "protected_user_zone_digest": None,
                "protected_user_zone_count": 0,
                "after_user_zone_digest": current_user["digest"],
                "after_user_zone_count": current_user["count"],
                "protected_user_state": "initialized-from-no-prior-state",
                "managed_environment_sha256": current[
                    "managed_environment"
                ]["sha256"],
                "live_verification": "pending-real-post-chat-canary",
                "user_zone_writes": False,
            },
        )
        return {
            "status": "succeeded",
            "action": "bootstrap",
            "release": current,
            "frame_hash": frame["frame_hash"],
            "instance_rappid": identity["rappid"],
            "verification": "pending-live-canary",
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rappctl")
    parser.add_argument(
        "--home",
        help="Override the Brainstem home directory for read-only/custom use",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    plan = subparsers.add_parser("plan")
    plan.add_argument("action", choices=sorted(SUPPORTED_ACTIONS))
    plan.add_argument(
        "--actor",
        default=os.environ.get("RAPP_OPERATOR_ACTOR", "github-copilot"),
    )

    apply_command = subparsers.add_parser("apply")
    apply_command.add_argument("plan_hash")
    apply_command.add_argument("--approve")

    reconcile = subparsers.add_parser("reconcile")
    reconcile.add_argument("--envelope", required=True)
    reconcile.add_argument("--envelope-sha256", required=True)
    reconcile.add_argument(
        "--actor",
        default=os.environ.get("RAPP_OPERATOR_ACTOR", "github-copilot"),
    )
    return parser


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = _parser().parse_args(argv)
    layout = Layout.current(args.home)
    if args.command == "status":
        return inspect(layout)
    if args.command == "plan":
        return create_plan(layout, args.action, args.actor)
    if args.command == "apply":
        return apply_plan(layout, args.plan_hash, args.approve)
    if args.command == "reconcile":
        return reconcile_install(
            layout,
            args.actor,
            args.envelope,
            args.envelope_sha256,
        )
    raise OperatorError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    try:
        result = run(argv)
    except (
        OSError,
        OperatorError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
