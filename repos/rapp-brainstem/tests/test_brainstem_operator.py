import copy
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from rapp_operator import rapp1, rappctl


ROOT = Path(__file__).resolve().parent.parent
SERVER_SOURCE = r"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

root = Path(__file__).resolve().parent
version = (root / "VERSION").read_text(encoding="utf-8").strip()
port = int(os.getenv("PORT") or "7071")
if "PORT" not in os.environ:
    for line in (root / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("PORT="):
            port = int(line.split("=", 1)[1])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path != "/health/public":
            self.send_response(404)
            self.end_headers()
            return
        payload = json.dumps({"status": "ok", "version": version}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        json.loads(self.rfile.read(length) or b"{}")
        payload = json.dumps({
            "response": f"fixture alive {version}",
            "agent_logs": "",
            "session_id": "fixture",
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


HTTPServer(("127.0.0.1", port), Handler).serve_forever()
""".lstrip()


def git(source: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def target_for(layout: rappctl.Layout, version: str, tag: str) -> dict:
    commit = git(layout.source_root, "rev-parse", "HEAD")
    return {
        "repository": rappctl.DEFAULT_REPO,
        "tag": tag,
        "commit": commit,
        "tree": git(
            layout.source_root,
            "rev-parse",
            "HEAD:rapp_brainstem",
        ),
        "version": version,
        "version_url": (
            "https://raw.githubusercontent.com/microsoft/"
            f"aibast-agents-library/{commit}/rapp_brainstem/VERSION"
        ),
    }


def install_test_managed_python(home: Path) -> Path:
    managed = home / (
        "venv/Scripts/python.exe"
        if os.name == "nt"
        else "venv/bin/python"
    )
    managed.parent.mkdir(parents=True)
    if os.name == "nt":
        shutil.copy2(sys.executable, managed)
    else:
        managed.symlink_to(sys.executable)
    (home / "venv/pyvenv.cfg").write_text(
        "\n".join(
            (
                f"home = {sys.base_prefix}",
                "include-system-site-packages = true",
                f"version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                f"executable = {sys.executable}",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return managed


def init_runtime(
    home: Path,
    *,
    version: str = "1.0.0",
) -> tuple[rappctl.Layout, dict]:
    source = home / "src"
    runtime = source / "rapp_brainstem"
    runtime.mkdir(parents=True)
    (runtime / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (runtime / "brainstem.py").write_text(SERVER_SOURCE, encoding="utf-8")
    (runtime / "requirements.txt").write_text("", encoding="utf-8")
    (runtime / "soul.md").write_text("default soul\n", encoding="utf-8")
    agents = runtime / "agents"
    agents.mkdir()
    (agents / "builtin_agent.py").write_text(
        "BUILTIN = True\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=source,
        check=True,
        capture_output=True,
    )
    git(source, "config", "user.email", "test@example.com")
    git(source, "config", "user.name", "Test")
    git(source, "add", ".")
    git(source, "commit", "-m", f"fixture {version}")
    tag = f"brainstem-v{version}"
    git(source, "tag", tag)
    (runtime / ".env").write_text(f"PORT={free_port()}\n", encoding="utf-8")
    (agents / "custom_agent.py").write_text(
        "CUSTOM = True\n",
        encoding="utf-8",
    )
    install_test_managed_python(home)
    layout = rappctl.Layout.current(home)
    return layout, target_for(layout, version, tag)


def add_release(
    layout: rappctl.Layout,
    version: str,
) -> dict:
    (layout.runtime_dir / "VERSION").write_text(
        f"{version}\n",
        encoding="utf-8",
    )
    (layout.runtime_dir / "brainstem.py").write_text(
        SERVER_SOURCE + f"\n# release {version}\n",
        encoding="utf-8",
    )
    git(layout.source_root, "add", "rapp_brainstem/VERSION")
    git(layout.source_root, "add", "rapp_brainstem/brainstem.py")
    git(layout.source_root, "commit", "-m", f"fixture {version}")
    tag = f"brainstem-v{version}"
    git(layout.source_root, "tag", tag)
    return target_for(layout, version, tag)


def fake_lock(target: dict, digest: str | None = None) -> dict:
    digest = digest or hashlib.sha256(
        json.dumps(target, sort_keys=True).encode()
    ).hexdigest()
    return {
        "schema": rappctl.INSTALLER_LOCK_SCHEMA,
        "upstream": "https://github.com/microsoft/aibast-agents-library",
        "target": copy.deepcopy(target),
        "artifacts": {
            "macos-linux": {
                "url": (
                    "https://raw.githubusercontent.com/microsoft/"
                    f"aibast-agents-library/{target['commit']}/install.sh"
                ),
                "sha256": "1" * 64,
            },
            "windows": {
                "url": (
                    "https://raw.githubusercontent.com/microsoft/"
                    f"aibast-agents-library/{target['commit']}/install.ps1"
                ),
                "sha256": "2" * 64,
            },
        },
        "bootstrap": {
            "envelope_schema": rappctl.BOOTSTRAP_ENVELOPE_SCHEMA,
            "state_home": rappctl.BOOTSTRAP_STATE_HOME,
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
        },
        "lifecycle": {
            "preferred_target_ref_kind": "exact-commit",
            "repair_fallback_target_ref_kind": "rolling-tag",
            "historical_rollback_target_ref_kind": "exact-commit",
            "exact_commit_installer_arguments": ["--no-launch"],
            "rolling_tag_installer_arguments": [
                "--no-launch",
                "--version",
                target["tag"],
            ],
        },
        "_digest": digest,
        "_path": str(ROOT / "installer-lock.json"),
    }


def install_fake_lock(
    monkeypatch: pytest.MonkeyPatch,
    target: dict,
) -> dict:
    lock = fake_lock(target)
    monkeypatch.setattr(
        rappctl,
        "load_installer_lock",
        lambda: copy.deepcopy(lock),
    )
    monkeypatch.setattr(rappctl, "_verify_target_tag", lambda _target: None)
    return lock


def allow_test_installer_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rappctl, "_is_default_home", lambda _layout: True)


def write_bootstrap_envelope(
    directory: Path,
    lock: dict,
    *,
    actor: str = "github-copilot",
    transform=None,
) -> tuple[Path, str, dict]:
    envelope = rappctl.bootstrap_envelope(
        lock,
        actor,
        "2026-09-02T15:39:22.000Z",
        "windows" if os.name == "nt" else "macos-linux",
    )
    if transform is not None:
        transform(envelope)
    payload = (
        json.dumps(envelope, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest}.json"
    path.write_bytes(payload)
    return path, digest, envelope


def frame_payloads(layout: rappctl.Layout, kind: str) -> list[dict]:
    return [
        frame["payload"]
        for frame in rappctl.EvidenceLog(layout).frames()
        if frame["kind"] == kind
    ]


def stop_if_running(layout: rappctl.Layout) -> None:
    try:
        if rappctl.managed_runtime_state(layout)["state"] == "running":
            rappctl._stop_brainstem(layout)
    except rappctl.OperatorError:
        pass


def test_repository_wraps_grail_without_vendoring_it():
    assert not (ROOT / "install.sh").exists()
    assert not (ROOT / "install.ps1").exists()
    assert not list(ROOT.rglob("brainstem.py"))
    source = (ROOT / "rapp_operator/rappctl.py").read_text(encoding="utf-8")
    assert "microsoft/aibast-agents-library" in source
    assert "brainstem.py" not in {
        path.name for path in (ROOT / "rapp_operator").iterdir()
    }


def test_rapp1_operator_matches_shared_vectors():
    vectors = json.loads(
        (ROOT / "tests/conformance-vectors.json").read_text(encoding="utf-8")
    )
    assert rapp1.SOURCE_COMMIT == vectors["source_commit"]
    for vector in vectors["canonical"]:
        assert rapp1.canonical(vector["value"]) == vector["bytes_utf8"]
        assert rapp1.H("rapp/1:particle", vector["value"]) == vector["particle"]
    vector = vectors["frame"]
    frame = rapp1.build_frame(
        vector["kind"],
        vector["stream_id"],
        vector["seq"],
        vector["utc"],
        vector["payload"],
        vector["prev"],
        prev_wave=vector["prev_wave"],
        sig=vector["sig"],
    )
    assert frame["payload_hash"] == vector["payload_hash"]
    assert frame["frame_hash"] == vector["frame_hash"]
    assert rapp1.verify_frame(
        frame,
        stream_id_of_record=vector["stream_id"],
    ) == (True, None, "ok")


def test_manifest_contract_uses_local_plugin_trust_and_preplan():
    spec = importlib.util.spec_from_file_location(
        "build_manifest",
        ROOT / "tools/build_manifest.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    manifest = module.build_manifest()
    assert manifest["product"]["name"] == "RAPP Brainstem"
    assert manifest["operators"]["golden_path"]["id"] == "github-copilot"
    assert manifest["operators"]["compatibility"][0]["id"] == "claude-code"
    assert "installed marketplace plugin" in manifest["bootstrap"]["trust_anchor"]
    assert manifest["bootstrap"]["plan_contract"]["schema"] == (
        rappctl.BOOTSTRAP_ENVELOPE_SCHEMA
    )
    assert "before the upstream installer" in (
        manifest["bootstrap"]["plan_contract"]["rule"]
    )
    assert "bootstrap" in manifest["artifacts"]
    assert "init" in manifest["artifacts"]["operator"]
    assert "installer_lock" in manifest["artifacts"]["operator"]
    assert manifest["artifacts"]["reviewed_target"]["commit"] == (
        json.loads((ROOT / "installer-lock.json").read_text())["target"]["commit"]
    )
    assert "fetch manifest" not in manifest["bootstrap"]["sequence"]
    assert manifest["bootstrap"]["reconcile_result"].startswith(
        "Installation evidence only"
    )
    assert manifest["bootstrap"]["state_home"] == (
        rappctl.BOOTSTRAP_STATE_HOME
    )
    assert manifest["lifecycle"]["targets"]["rollback"].startswith(
        "historical exact commit"
    )
    assert manifest["runtime"]["environment"]["mode"] == (
        "minimal-child-environment"
    )


def test_generated_bootstraps_are_local_and_python_free_before_installer(
    tmp_path,
):
    spec = importlib.util.spec_from_file_location(
        "build_manifest_bootstrap",
        ROOT / "tools/build_manifest.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    lock, lock_payload = module.read_lock()
    bundle = module.operator_bundle()
    lock_for_operator = copy.deepcopy(lock)
    lock_for_operator["_digest"] = hashlib.sha256(lock_payload).hexdigest()
    for platform_id in ("macos-linux", "windows"):
        assert module.envelope_value(
            lock,
            lock_for_operator["_digest"],
            bundle,
            platform_id,
            "github-copilot",
            "2026-09-02T15:39:22.000Z",
        ) == rappctl.bootstrap_envelope(
            lock_for_operator,
            "github-copilot",
            "2026-09-02T15:39:22.000Z",
            platform_id,
        )
    expected_shell = module.render_bootstrap_sh(
        lock,
        lock_payload,
        bundle,
    )
    expected_windows = module.render_bootstrap_ps1(
        lock,
        lock_payload,
        bundle,
    )
    shell_path = ROOT / "scripts/bootstrap.sh"
    windows_path = ROOT / "scripts/bootstrap.ps1"
    assert shell_path.read_bytes() == expected_shell
    assert windows_path.read_bytes() == expected_windows
    if os.name != "nt":
        subprocess.run(["bash", "-n", str(shell_path)], check=True)

    shell = expected_shell.decode("utf-8")
    windows = expected_windows.decode("utf-8")
    for script in (shell, windows):
        assert "jq" not in script
        assert "/tmp" not in script
        assert "rapp-brainstem-bootstrap-envelope/2" in script
        assert "local-marketplace-plugin" in script
        assert "Live /chat verification is still required" in script
        assert "~/.rapp/operator" not in script
        assert "creation_identity" in script
        assert "FailedDirectory" in script or "FAILED_DIR" in script
        assert "rapp_operator/rappctl.py" in script
    assert "recover_failed_bootstrap" in shell
    assert "Get-ProcessCreationIdentity" in windows
    assert "Release-BootstrapLock" in windows
    shell_installer = shell.index(
        'bash "$INSTALLER_PATH" --no-launch --version installers'
    )
    shell_python = shell.index(
        '"$BRAINSTEM_PYTHON" "$PLUGIN_ROOT/rapp_operator/rappctl.py"'
    )
    assert shell.index('cat >"$ENVELOPE_TEMP"') < shell_installer
    assert shell_installer < shell_python
    assert "python3" not in shell[:shell_installer].lower()
    windows_installer = windows.index(
        "& $PowerShellExe -NoProfile -ExecutionPolicy Bypass"
    )
    windows_python = windows.index(
        "& $BrainstemPython (Join-Path $PluginRoot"
    )
    assert windows.index("$EnvelopeJson =") < windows_installer
    assert windows_installer < windows_python
    assert "python.exe" not in windows[:windows_installer].lower()
    shell_envelope = shell.split(
        'cat >"$ENVELOPE_TEMP" <<EOF\n',
        1,
    )[1].split("\nEOF\n", 1)[0]
    shell_envelope = shell_envelope.replace(
        "$ACTOR",
        "github-copilot",
    ).replace(
        "$CREATED_UTC",
        "2026-09-02T15:39:22.000Z",
    )
    assert json.loads(shell_envelope) == module.envelope_value(
        lock,
        lock_for_operator["_digest"],
        bundle,
        "macos-linux",
        "github-copilot",
        "2026-09-02T15:39:22.000Z",
    )
    windows_envelope = windows.split(
        '$EnvelopeJson = @"\n',
        1,
    )[1].split('\n"@', 1)[0]
    windows_envelope = windows_envelope.replace(
        "$Actor",
        "github-copilot",
    ).replace(
        "$CreatedUtc",
        "2026-09-02T15:39:22.000Z",
    )
    assert json.loads(windows_envelope) == module.envelope_value(
        lock,
        lock_for_operator["_digest"],
        bundle,
        "windows",
        "github-copilot",
        "2026-09-02T15:39:22.000Z",
    )

    if os.name != "nt":
        existing_home = tmp_path / "existing-home"
        (existing_home / ".brainstem").mkdir(parents=True)
        environment = os.environ.copy()
        environment["HOME"] = str(existing_home)
        refused = subprocess.run(
            ["bash", str(shell_path), "--actor", "github-copilot"],
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        assert refused.returncode == 1
        assert "fresh bootstrap refuses existing state" in refused.stderr
        assert not (existing_home / ".rapp").exists()


def test_bundled_lock_pins_immutable_installer_and_exact_target():
    lock = rappctl.load_installer_lock()
    assert lock["schema"] == rappctl.INSTALLER_LOCK_SCHEMA
    assert lock["bootstrap"] == {
        "envelope_schema": rappctl.BOOTSTRAP_ENVELOPE_SCHEMA,
        "state_home": rappctl.BOOTSTRAP_STATE_HOME,
        "target_ref_kind": "rolling-tag",
        "required_installer_arguments": [
            "--no-launch",
            "--version",
            "installers",
        ],
        "verification": (
            "A successful reconcile records installation only. Live "
            "verification requires a later real POST /chat canary."
        ),
    }
    assert lock["lifecycle"] == {
        "preferred_target_ref_kind": "exact-commit",
        "repair_fallback_target_ref_kind": "rolling-tag",
        "historical_rollback_target_ref_kind": "exact-commit",
        "exact_commit_installer_arguments": ["--no-launch"],
        "rolling_tag_installer_arguments": [
            "--no-launch",
            "--version",
            "installers",
        ],
    }
    target = lock["target"]
    assert target == {
        "commit": "c60521e2cacbcbfa585a118c1275093d7bb15b74",
        "repository": rappctl.DEFAULT_REPO,
        "tag": "installers",
        "tree": "3c5bb0d55ca4a5aff8872d30b8108e2438ef808d",
        "version": "0.6.16",
        "version_url": (
            "https://raw.githubusercontent.com/microsoft/"
            "aibast-agents-library/"
            "c60521e2cacbcbfa585a118c1275093d7bb15b74/"
            "rapp_brainstem/VERSION"
        ),
    }
    for artifact in lock["artifacts"].values():
        assert target["commit"] in artifact["url"]
        assert len(artifact["sha256"]) == 64
        int(artifact["sha256"], 16)
    source = (ROOT / "rapp_operator/rappctl.py").read_text(encoding="utf-8")
    assert "RAPP_OPERATOR_MANIFEST_URL" not in source
    assert "_load_operator_manifest" not in source


def test_windows_liveness_never_calls_os_kill(monkeypatch):
    monkeypatch.setattr(rappctl.os, "name", "nt")
    monkeypatch.setattr(rappctl, "_windows_pid_alive", lambda pid: pid == 42)

    def forbidden_kill(*_args):
        raise AssertionError("os.kill must not be used for Windows liveness")

    monkeypatch.setattr(rappctl.os, "kill", forbidden_kill)
    assert rappctl._pid_alive(42) is True
    assert rappctl._pid_alive(43) is False


def test_process_ownership_requires_complete_sidecar_identity(
    tmp_path,
    monkeypatch,
):
    layout, _target = init_runtime(tmp_path / ".brainstem")
    killed = []
    monkeypatch.setattr(
        rappctl,
        "probe_health",
        lambda _layout, timeout=2.0, environment_binding=None: {
            "reachable": True,
            "http_status": 200,
            "status": "ok",
            "version": "1.0.0",
            "port": 54321,
        },
    )
    monkeypatch.setattr(rappctl, "_port_listening", lambda _port: True)
    monkeypatch.setattr(
        rappctl.os,
        "kill",
        lambda *args: killed.append(args),
    )

    assert rappctl._discover_brainstem_pid(layout) is None
    with pytest.raises(rappctl.OperatorError, match="without a matching"):
        rappctl._stop_brainstem(layout)
    assert killed == []

    stale = {
        "schema": rappctl.PID_SCHEMA,
        "pid": 123,
        "creation_identity": "old",
        "executable": "/python",
        "executable_identity": rapp1.H(
            "rapp/process-executable/1",
            {"executable": "/python"},
        ),
        "command_identity": "3" * 64,
        "environment_sha256": "5" * 64,
        "effective_port": 54321,
        "managed_environment_sha256": "6" * 64,
        "nonce": "nonce",
        "started_utc": "2026-09-02T00:00:00.000Z",
    }
    rappctl._atomic_json(layout.pid_file, stale)
    monkeypatch.setattr(
        rappctl,
        "_process_snapshot",
        lambda _pid: {
            "pid": 123,
            "creation_identity": "new",
            "executable": "/other",
            "command_identity": "4" * 64,
        },
    )
    record, status = rappctl._pid_record_state(
        layout,
        cleanup_stale=True,
    )
    assert record is None
    assert status == "stale"
    assert not layout.pid_file.exists()


def test_pid_record_deletion_compares_nonce_and_identity(tmp_path):
    path = tmp_path / "brainstem.pid"
    expected = {"nonce": "first", "pid": 1}
    changed = {"nonce": "second", "pid": 1}
    rappctl._atomic_json(path, changed)
    with pytest.raises(rappctl.OperatorError, match="changed record"):
        rappctl._delete_json_record(path, expected)
    assert json.loads(path.read_text()) == changed


def test_release_identity_detects_managed_byte_changes_but_protects_agents(
    tmp_path,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    clean = rappctl.release_identity(layout)
    assert clean["managed_clean"] is True
    assert rappctl._target_matches_release(target, clean)

    (layout.runtime_dir / "brainstem.py").write_text(
        "tampered\n",
        encoding="utf-8",
    )
    dirty = rappctl.release_identity(layout)
    assert dirty["managed_clean"] is False
    assert dirty["managed_mismatch_count"] == 1
    assert not rappctl._target_matches_release(target, dirty)

    git(
        layout.source_root,
        "checkout",
        "--",
        "rapp_brainstem/brainstem.py",
    )
    builtin = layout.runtime_dir / "agents/builtin_agent.py"
    builtin.write_text("USER MODIFIED = True\n", encoding="utf-8")
    protected = rappctl.release_identity(layout)
    manifest = rappctl.user_zone_manifest(layout)
    assert protected["managed_clean"] is True
    assert "agents/builtin_agent.py" in {
        entry["path"] for entry in manifest["entries"]
    }
    assert "agents/custom_agent.py" in {
        entry["path"] for entry in manifest["entries"]
    }


def test_plan_binds_lock_target_runtime_operator_and_user_state(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    lock = install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "start", "github-copilot")
    assert plan["trust"]["installer_lock_sha256"] == lock["_digest"]
    assert plan["trust"]["installer"]["url"] == (
        lock["artifacts"]["macos-linux"]["url"]
    )
    assert set(plan["trust"]["installer"]) == {"platform", "sha256", "url"}
    assert plan["installer_execution"] is None
    assert plan["target_release"] == target
    assert plan["current_release"] == rappctl.release_identity(layout)
    assert plan["managed_runtime"]["state"] == "stopped"
    assert plan["operator_bundle"]["sha256"]
    assert plan["protected_user_zone"]["digest"]
    assert plan["protected_user_zone"]["allowed_additions"] == []
    assert plan["runtime_environment"]["effective_port"] > 0
    assert all(
        "value" not in entry
        for entry in plan["runtime_environment"]["supported_overrides"]
    )
    assert plan["expected_postconditions"]["runtime_state"] == "running"


def test_apply_rejects_lock_and_user_state_drift_before_mutation(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    lock = install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "start", "github-copilot")
    changed_lock = copy.deepcopy(lock)
    changed_lock["_digest"] = "f" * 64
    monkeypatch.setattr(
        rappctl,
        "load_installer_lock",
        lambda: copy.deepcopy(changed_lock),
    )
    with pytest.raises(rappctl.OperatorError, match="installer-lock"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
    assert not layout.pid_file.exists()

    monkeypatch.setattr(
        rappctl,
        "load_installer_lock",
        lambda: copy.deepcopy(lock),
    )
    second = rappctl.create_plan(layout, "start", "github-copilot")
    (layout.runtime_dir / "soul.md").write_text(
        "changed after plan\n",
        encoding="utf-8",
    )
    with pytest.raises(rappctl.OperatorError, match="protected user state"):
        rappctl.apply_plan(
            layout,
            second["plan_hash"],
            second["plan_hash"],
        )
    assert not layout.pid_file.exists()


def test_installer_invocation_uses_exact_locked_commit(
    tmp_path,
    monkeypatch,
):
    layout = rappctl.Layout.current(tmp_path / ".brainstem")
    target = {
        "repository": rappctl.DEFAULT_REPO,
        "tag": "brainstem-v9.9.9",
        "commit": "a" * 40,
        "tree": "b" * 40,
        "version": "9.9.9",
        "version_url": (
            "https://raw.githubusercontent.com/microsoft/"
            f"aibast-agents-library/{'a' * 40}/rapp_brainstem/VERSION"
        ),
    }
    lock = fake_lock(target)
    installer = tmp_path / "install.sh"
    installer.write_text("#!/bin/sh\n", encoding="utf-8")
    captured = {}
    monkeypatch.setattr(rappctl, "_require_default_home", lambda *_args: None)
    monkeypatch.setattr(
        rappctl,
        "_download_verified_installer",
        lambda _layout, _lock: installer,
    )

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(rappctl.subprocess, "run", fake_run)
    execution = rappctl._installer_execution(
        layout,
        "update",
        target,
        lock,
    )
    rappctl._run_installer(
        layout,
        "update",
        target,
        lock,
        execution,
    )
    assert captured["command"][-1:] == ["--no-launch"]
    assert "--version" not in captured["command"]
    assert captured["env"]["BRAINSTEM_REPO_REF"] == target["commit"]
    assert captured["env"]["BRAINSTEM_REPO_URL"] == target["repository"]
    assert captured["env"]["BRAINSTEM_VERSION_URL"] == target["version_url"]


def test_operation_lock_serializes_across_processes(tmp_path):
    home = tmp_path / ".brainstem"
    code = """
import sys
import time
from rapp_operator.rappctl import Layout, _operation_lock
layout = Layout.current(sys.argv[1])
with _operation_lock(layout, timeout=2):
    print("locked", flush=True)
    time.sleep(1.5)
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT)
    process = subprocess.Popen(
        [sys.executable, "-c", code, str(home)],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "locked"
        layout = rappctl.Layout.current(home)
        with pytest.raises(rappctl.OperatorError, match="operation is busy"):
            with rappctl._operation_lock(layout, timeout=0.1):
                pass
    finally:
        process.wait(timeout=5)
    assert process.returncode == 0


def test_failed_update_restores_exact_release_and_stopped_state(
    tmp_path,
    monkeypatch,
):
    layout, target_v1 = init_runtime(tmp_path / ".brainstem")
    target_v2 = add_release(layout, "2.0.0")
    git(layout.source_root, "checkout", "--force", target_v1["commit"])
    install_fake_lock(monkeypatch, target_v2)
    allow_test_installer_home(monkeypatch)
    marker = layout.venv_dir / "release-marker.txt"
    marker.write_text("v1 environment\n", encoding="utf-8")

    def fake_installer(_layout, _action, target, _lock, _execution):
        git(_layout.source_root, "checkout", "--force", target["commit"])
        marker.write_text("mutated environment\n", encoding="utf-8")

    monkeypatch.setattr(rappctl, "_run_installer", fake_installer)
    plan = rappctl.create_plan(layout, "update", "github-copilot")
    before = rappctl.release_identity(layout)
    monkeypatch.setattr(
        rappctl,
        "_verify_live",
        lambda *_args: (_ for _ in ()).throw(
            rappctl.OperatorError("simulated canary failure")
        ),
    )
    with pytest.raises(rappctl.OperatorError, match="simulated canary"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
    assert rappctl.release_identity(layout) == before
    assert git(layout.source_root, "rev-parse", "HEAD") == target_v1["commit"]
    assert marker.read_text(encoding="utf-8") == "v1 environment\n"
    assert rappctl.managed_runtime_state(layout)["state"] == "stopped"
    failed = frame_payloads(layout, "operator.apply")[-1]
    assert failed["status"] == "failed"
    assert failed["rollback"]["status"] == "succeeded"
    assert failed["rollback"]["managed_environment_restored"] is True
    assert not frame_payloads(layout, "operator.verify")


def test_user_zone_is_backed_up_restored_and_never_logged(
    tmp_path,
    monkeypatch,
):
    layout, target_v1 = init_runtime(tmp_path / ".brainstem")
    target_v2 = add_release(layout, "2.0.0")
    git(layout.source_root, "checkout", "--force", target_v1["commit"])
    secret = "TOP-SECRET-USER-SOUL"
    soul = layout.runtime_dir / "soul.md"
    custom = layout.runtime_dir / "agents/custom_agent.py"
    env_file = layout.runtime_dir / ".env"
    soul.write_text(secret, encoding="utf-8")
    custom.write_text("USER AGENT SECRET\n", encoding="utf-8")
    original = {
        "soul": soul.read_bytes(),
        "agent": custom.read_bytes(),
        "env": env_file.read_bytes(),
    }
    install_fake_lock(monkeypatch, target_v2)
    allow_test_installer_home(monkeypatch)

    def destructive_installer(
        _layout,
        _action,
        target,
        _lock,
        _execution,
    ):
        git(_layout.source_root, "checkout", "--force", target["commit"])
        soul.write_text("clobbered", encoding="utf-8")
        custom.write_text("clobbered", encoding="utf-8")
        env_file.write_bytes(b"\xff")

    monkeypatch.setattr(rappctl, "_run_installer", destructive_installer)
    plan = rappctl.create_plan(layout, "update", "github-copilot")
    with pytest.raises(rappctl.OperatorError, match="Protected user state"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
    assert soul.read_bytes() == original["soul"]
    assert custom.read_bytes() == original["agent"]
    assert env_file.read_bytes() == original["env"]
    backups = list(layout.backups_dir.glob("*/user/manifest.json"))
    assert backups
    assert stat_mode(backups[0].parents[1]) & 0o077 == 0
    frame_bytes = b"".join(path.read_bytes() for path in layout.frames_dir.glob("*"))
    assert secret.encode() not in frame_bytes
    assert b"USER AGENT SECRET" not in frame_bytes


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def test_offline_verify_appends_no_verification_frame(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "verify", "github-copilot")
    with pytest.raises(rappctl.OperatorError, match="not running"):
        rappctl.apply_plan(layout, plan["plan_hash"], None)
    assert frame_payloads(layout, "operator.verify") == []
    assert frame_payloads(layout, "operator.apply")[-1]["status"] == "failed"


def test_real_chat_canary_receipt_contains_only_status_and_hash(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "start", "github-copilot")
    try:
        result = rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
        assert result["status"] == "succeeded"
        assert result["verification"] == "pending-live-canary"
        assert frame_payloads(layout, "operator.verify") == []
        applied = frame_payloads(layout, "operator.apply")[-1]
        assert applied["after_user_zone_count"] == applied[
            "protected_user_zone_count"
        ]
        assert applied["runtime_environment_sha256"] == plan[
            "runtime_environment"
        ]["sha256"]
        verify_plan = rappctl.create_plan(
            layout,
            "verify",
            "github-copilot",
        )
        verified_result = rappctl.apply_plan(
            layout,
            verify_plan["plan_hash"],
            None,
        )
        assert verified_result["status"] == "succeeded"
        verified = frame_payloads(layout, "operator.verify")[-1]
        expected_response = f"fixture alive {target['version']}"
        assert verified["canary"] == {
            "http_status": 200,
            "response_sha256": hashlib.sha256(
                expected_response.encode()
            ).hexdigest(),
        }
        frame_bytes = b"".join(
            path.read_bytes() for path in layout.frames_dir.glob("*")
        )
        assert expected_response.encode() not in frame_bytes
    finally:
        stop_if_running(layout)


def test_reconcile_requires_exact_envelope_and_does_not_claim_verification(
    tmp_path,
    monkeypatch,
):
    staged, target = init_runtime(tmp_path / "staged" / ".brainstem")
    layout = rappctl.Layout.current(tmp_path / "actual" / ".brainstem")
    lock = install_fake_lock(monkeypatch, target)
    allow_test_installer_home(monkeypatch)
    envelope_path, envelope_sha256, _envelope = write_bootstrap_envelope(
        tmp_path / "operator/envelopes",
        lock,
    )
    layout.source_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(staged.source_root, layout.source_root)
    shutil.copytree(staged.venv_dir, layout.venv_dir, symlinks=True)
    result = rappctl.reconcile_install(
        layout,
        "github-copilot",
        envelope_path,
        envelope_sha256,
    )
    assert result["verification"] == "pending-live-canary"
    assert frame_payloads(layout, "operator.verify") == []
    applied = frame_payloads(layout, "operator.apply")[-1]
    assert applied["status"] == "succeeded"
    assert applied["plan_hash"] == envelope_sha256
    assert applied["bootstrap_envelope_sha256"] == envelope_sha256
    assert applied["operator_bundle_sha256"] == (
        rappctl._operator_bundle_identity()["sha256"]
    )
    assert applied["installer_arguments"] == [
        "--no-launch",
        "--version",
        target["tag"],
    ]
    assert applied["protected_user_state"] == (
        "initialized-from-no-prior-state"
    )
    assert applied["live_verification"] == (
        "pending-real-post-chat-canary"
    )
    start_plan = rappctl.create_plan(
        layout,
        "start",
        "github-copilot",
    )
    try:
        started = rappctl.apply_plan(
            layout,
            start_plan["plan_hash"],
            start_plan["plan_hash"],
        )
        assert started["status"] == "succeeded"
        assert started["verification"] == "pending-live-canary"
        assert frame_payloads(layout, "operator.verify") == []
        verify_plan = rappctl.create_plan(
            layout,
            "verify",
            "github-copilot",
        )
        verified_result = rappctl.apply_plan(
            layout,
            verify_plan["plan_hash"],
            None,
        )
        assert verified_result["status"] == "succeeded"
        verified = frame_payloads(layout, "operator.verify")
        assert len(verified) == 1
        assert verified[0]["plan_hash"] == verify_plan["plan_hash"]
        assert verified[0]["canary"]["http_status"] == 200
    finally:
        stop_if_running(layout)


def test_reconcile_rejects_envelope_actor_bundle_and_release_drift(
    tmp_path,
    monkeypatch,
):
    staged, target = init_runtime(tmp_path / "staged" / ".brainstem")
    layout = rappctl.Layout.current(tmp_path / "actual" / ".brainstem")
    lock = install_fake_lock(monkeypatch, target)
    allow_test_installer_home(monkeypatch)
    monkeypatch.setattr(
        rappctl,
        "probe_health",
        lambda _layout, timeout=2.0, environment_binding=None: {
            "reachable": False,
            "http_status": None,
            "status": "offline",
            "version": None,
            "port": 7071,
        },
    )
    monkeypatch.setattr(rappctl, "_port_listening", lambda _port: False)
    layout.source_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(staged.source_root, layout.source_root)

    actor_path, actor_digest, _ = write_bootstrap_envelope(
        tmp_path / "actor/envelopes",
        lock,
        actor="claude-code",
    )
    with pytest.raises(rappctl.OperatorError, match="actor does not match"):
        rappctl.reconcile_install(
            layout,
            "github-copilot",
            actor_path,
            actor_digest,
        )
    assert frame_payloads(layout, "operator.apply") == []

    installer_path, installer_digest, _ = write_bootstrap_envelope(
        tmp_path / "installer/envelopes",
        lock,
        transform=lambda value: value["installer"].update(
            {"sha256": "e" * 64}
        ),
    )
    with pytest.raises(rappctl.OperatorError, match="installer URL or SHA-256"):
        rappctl.reconcile_install(
            layout,
            "github-copilot",
            installer_path,
            installer_digest,
        )
    assert frame_payloads(layout, "operator.apply") == []

    bundle_path, bundle_digest, _ = write_bootstrap_envelope(
        tmp_path / "bundle/envelopes",
        lock,
        transform=lambda value: value["operator_bundle"].update(
            {"sha256": "f" * 64}
        ),
    )
    with pytest.raises(rappctl.OperatorError, match="operator bundle"):
        rappctl.reconcile_install(
            layout,
            "github-copilot",
            bundle_path,
            bundle_digest,
        )
    assert frame_payloads(layout, "operator.apply") == []

    exact_path, exact_digest, _ = write_bootstrap_envelope(
        tmp_path / "release/envelopes",
        lock,
    )
    (layout.runtime_dir / "VERSION").write_text(
        "9.9.9\n",
        encoding="utf-8",
    )
    with pytest.raises(rappctl.OperatorError, match="exact reviewed"):
        rappctl.reconcile_install(
            layout,
            "github-copilot",
            exact_path,
            exact_digest,
        )
    assert frame_payloads(layout, "operator.apply") == []


def test_rollback_candidates_require_matching_canary_evidence(tmp_path):
    layout, target = init_runtime(tmp_path / ".brainstem")
    release = rappctl.release_identity(layout)
    release.pop("managed_environment")
    release["release_hash"] = "c" * 64
    log = rappctl.EvidenceLog(layout)
    log.ensure()
    log.append(
        "operator.apply",
        {
            "event": "brainstem.lifecycle.apply",
            "actor": {"id": "github-copilot"},
            "action": "install",
            "plan_hash": "a" * 64,
            "status": "succeeded",
            "after_release": release,
            "target_release": target,
        },
    )
    with pytest.raises(rappctl.OperatorError, match="successful canary"):
        rappctl._previous_release(log, {"release_hash": "different"})
    log.append(
        "operator.verify",
        {
            "event": "brainstem.lifecycle.verified",
            "actor": {"id": "github-copilot"},
            "action": "install",
            "plan_hash": "a" * 64,
            "status": "succeeded",
            "release": release,
            "target_release": target,
            "canary": {
                "http_status": 200,
                "response_sha256": "b" * 64,
            },
        },
    )
    assert rappctl._previous_release(
        log,
        {"release_hash": "different"},
    ) == target


def test_lifecycle_targets_exact_commits_and_repair_fallback_is_current_only(
    tmp_path,
):
    layout, target_v1 = init_runtime(tmp_path / ".brainstem")
    target_v2 = add_release(layout, "2.0.0")
    lock = fake_lock(target_v2)
    update = rappctl._installer_execution(
        layout,
        "update",
        target_v2,
        lock,
    )
    rollback = rappctl._installer_execution(
        layout,
        "rollback",
        target_v1,
        lock,
    )
    assert update == {
        "arguments": ["--no-launch"],
        "repository_ref": {
            "kind": "exact-commit",
            "value": target_v2["commit"],
        },
    }
    assert rollback["repository_ref"] == {
        "kind": "exact-commit",
        "value": target_v1["commit"],
    }

    broken = rappctl.Layout.current(tmp_path / "broken" / ".brainstem")
    fallback = rappctl._installer_execution(
        broken,
        "repair",
        target_v2,
        lock,
    )
    assert fallback == {
        "arguments": ["--no-launch", "--version", target_v2["tag"]],
        "repository_ref": {
            "kind": "rolling-tag",
            "value": target_v2["tag"],
        },
    }
    with pytest.raises(rappctl.OperatorError, match="Historical repair"):
        rappctl._installer_execution(
            broken,
            "repair",
            target_v1,
            lock,
        )


def test_historical_rollback_validation_does_not_resolve_old_rolling_tag(
    tmp_path,
    monkeypatch,
):
    layout, target_v1 = init_runtime(tmp_path / ".brainstem")
    release_v1 = rappctl.release_identity(layout)
    log = rappctl.EvidenceLog(layout)
    log.ensure()
    log.append(
        "operator.apply",
        {
            "event": "brainstem.lifecycle.apply",
            "actor": {"id": "github-copilot"},
            "action": "update",
            "plan_hash": "a" * 64,
            "status": "succeeded",
            "after_release": release_v1,
            "target_release": target_v1,
        },
    )
    log.append(
        "operator.verify",
        {
            "event": "brainstem.lifecycle.verified",
            "actor": {"id": "github-copilot"},
            "action": "update",
            "plan_hash": "a" * 64,
            "status": "succeeded",
            "release": release_v1,
            "target_release": target_v1,
            "canary": {
                "http_status": 200,
                "response_sha256": "b" * 64,
            },
        },
    )
    target_v2 = add_release(layout, "2.0.0")
    install_fake_lock(monkeypatch, target_v2)
    allow_test_installer_home(monkeypatch)
    plan = rappctl.create_plan(layout, "rollback", "github-copilot")
    assert plan["target_release"] == target_v1
    assert plan["installer_execution"]["repository_ref"] == {
        "kind": "exact-commit",
        "value": target_v1["commit"],
    }

    def forbidden_tag_check(_target):
        raise AssertionError("historical rollback must not resolve its old tag")

    monkeypatch.setattr(rappctl, "_verify_target_tag", forbidden_tag_check)
    rappctl._validate_plan_bindings(layout, plan)


def test_runtime_environment_is_minimal_hashed_and_plan_bound(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    secret = "DO-NOT-WRITE-THIS-TOKEN"
    voice_password = "DO-NOT-WRITE-THIS-VOICE-PASSWORD"
    chosen_port = free_port()
    monkeypatch.setenv("UNBOUND_PROCESS_SECRET", "not-for-brainstem")
    monkeypatch.setenv("GITHUB_TOKEN", secret)
    monkeypatch.setenv("VOICE_ZIP_PASSWORD", voice_password)
    monkeypatch.setenv("GITHUB_MODEL", "fixture-model")
    monkeypatch.setenv("PORT", str(chosen_port))

    child, binding = rappctl.runtime_environment(layout)
    assert "UNBOUND_PROCESS_SECRET" not in child
    assert child["GITHUB_TOKEN"] == secret
    assert binding["effective_port"] == chosen_port
    assert {entry["name"] for entry in binding["supported_overrides"]} == set(
        rappctl.SUPPORTED_RUNTIME_OVERRIDES
    )
    assert all(
        set(entry) == {"name", "present", "source", "value_sha256"}
        for entry in binding["supported_overrides"]
    )

    plan = rappctl.create_plan(layout, "start", "github-copilot")
    assert plan["managed_runtime"]["health"]["port"] == chosen_port
    plan_bytes = (layout.plans_dir / f"{plan['plan_hash']}.json").read_bytes()
    frame_bytes = b"".join(
        path.read_bytes() for path in layout.frames_dir.glob("*.json")
    )
    assert secret.encode() not in plan_bytes + frame_bytes
    assert voice_password.encode() not in plan_bytes + frame_bytes
    monkeypatch.setenv("GITHUB_MODEL", "drifted-model")
    with pytest.raises(rappctl.OperatorError, match="runtime environment"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
    assert not layout.pid_file.exists()


def test_planned_restart_rebinds_a_safely_owned_process_after_env_drift(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    start = rappctl.create_plan(layout, "start", "github-copilot")
    try:
        rappctl.apply_plan(
            layout,
            start["plan_hash"],
            start["plan_hash"],
        )
        old_port = start["runtime_environment"]["effective_port"]
        new_port = free_port()
        assert new_port != old_port
        monkeypatch.setenv("PORT", str(new_port))
        drifted = rappctl.managed_runtime_state(layout)
        assert drifted["state"] == "running"
        assert drifted["lifecycle_owned"] is False
        restart = rappctl.create_plan(
            layout,
            "restart",
            "github-copilot",
        )
        result = rappctl.apply_plan(
            layout,
            restart["plan_hash"],
            restart["plan_hash"],
        )
        assert result["status"] == "succeeded"
        rebound = rappctl.managed_runtime_state(layout)
        assert rebound["lifecycle_owned"] is True
        assert rebound["health"]["port"] == new_port
        assert rebound["health"]["reachable"] is True
    finally:
        stop_if_running(layout)


def test_managed_environment_identity_and_no_interpreter_fallback(tmp_path):
    layout, target = init_runtime(tmp_path / ".brainstem")
    release = rappctl.release_identity(layout)
    environment = release["managed_environment"]
    assert environment["ready"] is True
    assert environment["interpreter"]["python_version"]
    assert len(environment["interpreter"]["executable_sha256"]) == 64
    assert len(environment["dependencies_sha256"]) == 64
    assert environment["dependency_count"] >= 0
    assert rappctl._target_matches_release(target, release)

    managed = rappctl._brainstem_python_path(layout)
    managed.unlink()
    with pytest.raises(rappctl.OperatorError, match="unrelated interpreter"):
        rappctl._brainstem_python(layout)
    assert rappctl.managed_environment_identity(layout)["ready"] is False


def test_new_protected_file_fails_and_is_removed_by_rollback(
    tmp_path,
    monkeypatch,
):
    layout, target_v1 = init_runtime(tmp_path / ".brainstem")
    target_v2 = add_release(layout, "2.0.0")
    git(layout.source_root, "checkout", "--force", target_v1["commit"])
    install_fake_lock(monkeypatch, target_v2)
    allow_test_installer_home(monkeypatch)
    injected = layout.runtime_dir / "credentials.json"

    def adding_installer(
        _layout,
        _action,
        target,
        _lock,
        _execution,
    ):
        git(_layout.source_root, "checkout", "--force", target["commit"])
        injected.write_text('{"secret":"new"}\n', encoding="utf-8")

    monkeypatch.setattr(rappctl, "_run_installer", adding_installer)
    plan = rappctl.create_plan(layout, "update", "github-copilot")
    with pytest.raises(rappctl.OperatorError, match="Protected user state"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
    assert not injected.exists()
    failed = frame_payloads(layout, "operator.apply")[-1]
    assert failed["rollback"]["status"] == "succeeded"
    assert failed["protected_user_zone_count"] == plan[
        "protected_user_zone"
    ]["count"]


def test_only_explicit_plan_bound_protected_additions_are_allowed(tmp_path):
    layout, _target = init_runtime(tmp_path / ".brainstem")
    before = rappctl.user_zone_manifest(layout)
    generated = layout.runtime_dir / ".brainstem_secret"
    generated.write_text("generated\n", encoding="utf-8")
    after = rappctl._verify_user_preserved(
        layout,
        before,
        [".brainstem_secret"],
    )
    assert after["count"] == before["count"] + 1
    unexpected = layout.runtime_dir / "credentials.json"
    unexpected.write_text("{}\n", encoding="utf-8")
    with pytest.raises(rappctl.OperatorError, match="Protected user state"):
        rappctl._verify_user_preserved(
            layout,
            before,
            [".brainstem_secret"],
        )


def test_verify_plan_rolls_back_an_unplanned_protected_write(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    start = rappctl.create_plan(layout, "start", "github-copilot")
    try:
        rappctl.apply_plan(
            layout,
            start["plan_hash"],
            start["plan_hash"],
        )
        verify = rappctl.create_plan(layout, "verify", "github-copilot")
        injected = layout.runtime_dir / "credentials.json"

        def mutating_canary(
            _layout,
            timeout=30.0,
            environment_binding=None,
        ):
            injected.write_text("{}\n", encoding="utf-8")
            return {
                "http_status": 200,
                "response_sha256": "a" * 64,
            }

        monkeypatch.setattr(rappctl, "_chat_canary", mutating_canary)
        with pytest.raises(rappctl.OperatorError, match="Protected user state"):
            rappctl.apply_plan(layout, verify["plan_hash"], None)
        assert not injected.exists()
        failed = frame_payloads(layout, "operator.apply")[-1]
        assert failed["action"] == "verify"
        assert failed["rollback"]["status"] == "succeeded"
        assert rappctl.managed_runtime_state(layout)["state"] == "running"
    finally:
        stop_if_running(layout)


def test_healthy_manual_process_is_chat_only_and_never_adopted(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    child_environment, binding = rappctl.runtime_environment(layout)
    process = subprocess.Popen(
        [
            str(rappctl._brainstem_python(layout)),
            str(layout.runtime_dir / "brainstem.py"),
        ],
        cwd=layout.runtime_dir,
        env=child_environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 10
        state = None
        while time.monotonic() < deadline:
            state = rappctl.managed_runtime_state(
                layout,
                environment_binding=binding,
            )
            if state["health"]["reachable"]:
                break
            time.sleep(0.05)
        assert state is not None
        assert state["state"] == "unknown-process"
        assert state["health"]["reachable"] is True
        canary = rappctl._chat_canary(
            layout,
            environment_binding=binding,
        )
        assert canary["http_status"] == 200
        assert not layout.pid_file.exists()
        with pytest.raises(rappctl.OperatorError, match="without a matching"):
            rappctl.create_plan(layout, "restart", "github-copilot")
        assert not layout.pid_file.exists()
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_operator_bundle_drift_forces_replan_from_current_plugin(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "start", "github-copilot")
    changed = copy.deepcopy(plan["operator_bundle"])
    changed["sha256"] = "f" * 64
    monkeypatch.setattr(rappctl, "_operator_bundle_identity", lambda: changed)
    with pytest.raises(rappctl.OperatorError, match="local operator bundle"):
        rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )


def test_legacy_copied_operator_cannot_be_lifecycle_authority(tmp_path):
    legacy = tmp_path / ".rapp/operator"
    (legacy / "rapp_operator").mkdir(parents=True)
    for name in ("__init__.py", "rapp1.py", "rappctl.py"):
        shutil.copy2(
            ROOT / "rapp_operator" / name,
            legacy / "rapp_operator" / name,
        )
    shutil.copy2(ROOT / "installer-lock.json", legacy / "installer-lock.json")
    result = subprocess.run(
        [
            sys.executable,
            str(legacy / "rapp_operator/rappctl.py"),
            "--home",
            str(tmp_path / ".brainstem"),
            "status",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "complete installed RAPP Brainstem marketplace plugin" in result.stdout


@pytest.mark.skipif(os.name == "nt", reason="POSIX bootstrap recovery")
def test_failed_shell_bootstrap_restores_absent_state_and_stale_lock(
    tmp_path,
):
    spec = importlib.util.spec_from_file_location(
        "build_manifest_recovery",
        ROOT / "tools/build_manifest.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    target = {
        "repository": rappctl.DEFAULT_REPO,
        "tag": "installers",
        "commit": "a" * 40,
        "tree": "b" * 40,
        "version": "9.9.9",
        "version_url": (
            "https://raw.githubusercontent.com/microsoft/"
            f"aibast-agents-library/{'a' * 40}/rapp_brainstem/VERSION"
        ),
    }
    installer_payload = (
        b"#!/usr/bin/env bash\n"
        b"mkdir -p \"$HOME/.brainstem\"\n"
        b"printf 'partial\\n' > \"$HOME/.brainstem/partial.txt\"\n"
        b"exit 23\n"
    )
    lock = fake_lock(target)
    lock.pop("_digest")
    lock.pop("_path")
    lock["artifacts"]["macos-linux"] = {
        "url": "https://example.invalid/install.sh",
        "sha256": hashlib.sha256(installer_payload).hexdigest(),
    }
    lock_payload = (
        json.dumps(lock, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    plugin = tmp_path / "plugin"
    (plugin / "scripts").mkdir(parents=True)
    (plugin / "rapp_operator").mkdir()
    for name in ("__init__.py", "rapp1.py", "rappctl.py"):
        shutil.copy2(
            ROOT / "rapp_operator" / name,
            plugin / "rapp_operator" / name,
        )
    (plugin / "installer-lock.json").write_bytes(lock_payload)
    bootstrap = plugin / "scripts/bootstrap.sh"
    bootstrap.write_bytes(
        module.render_bootstrap_sh(
            lock,
            lock_payload,
            module.operator_bundle(),
        )
    )
    bootstrap.chmod(0o755)
    installer = tmp_path / "fixture-installer.sh"
    installer.write_bytes(installer_payload)
    installer.chmod(0o755)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_curl = fake_bin / "curl"
    fake_curl.write_text(
        """#!/usr/bin/env bash
output=""
while [ "$#" -gt 0 ]; do
    if [ "$1" = "--output" ]; then
        output="$2"
        shift 2
        continue
    fi
    shift
done
if [ -z "$output" ]; then
    exit 22
fi
cat "$FAKE_INSTALLER_SOURCE" > "$output"
""",
        encoding="utf-8",
    )
    fake_curl.chmod(0o755)
    home = tmp_path / "home"
    stale_lock = home / ".rapp/brainstem-bootstrap/.bootstrap.lock"
    stale_lock.parent.mkdir(parents=True)
    stale_lock.write_text(
        "\n".join(
            (
                "schema=rapp-brainstem-bootstrap-lock/1",
                "pid=99999999",
                "creation_identity=ps-lstart:stale",
                "nonce=stale",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "FAKE_INSTALLER_SOURCE": str(installer),
            "HOME": str(home),
            "PATH": f"{fake_bin}:{environment['PATH']}",
        }
    )
    result = subprocess.run(
        ["bash", str(bootstrap), "--actor", "github-copilot"],
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 23
    assert not (home / ".brainstem").exists()
    quarantines = list(
        (home / ".rapp/brainstem-bootstrap/failed").iterdir()
    )
    assert len(quarantines) == 1
    assert (quarantines[0] / "partial.txt").read_text() == "partial\n"
    assert stat_mode(quarantines[0]) & 0o077 == 0
    assert not stale_lock.exists()
    assert "partial bootstrap quarantined" in result.stderr


def test_hash_bound_artifacts_are_lf_normalized_even_with_crlf_input():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    for suffix in ("py", "json", "sh", "ps1", "md", "html", "txt", "yml", "yaml"):
        assert f"*.{suffix} text eol=lf" in attributes
    hash_bound = [
        "rapp_operator/rappctl.py",
        "installer-lock.json",
        "scripts/bootstrap.sh",
        "scripts/bootstrap.ps1",
        "skills/rapp-brainstem/SKILL.md",
        "skills/rapp-brainstem/CLAUDE.md",
    ]
    for path in hash_bound:
        result = subprocess.run(
            ["git", "check-attr", "text", "eol", "--", path],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        assert "text: set" in result.stdout
        assert "eol: lf" in result.stdout
        assert b"\r\n" not in (ROOT / path).read_bytes()
        lf = subprocess.run(
            ["git", "hash-object", f"--path={path}", "--stdin"],
            cwd=ROOT,
            input=b"alpha\nbeta\n",
            capture_output=True,
            check=True,
        ).stdout
        crlf = subprocess.run(
            ["git", "hash-object", f"--path={path}", "--stdin"],
            cwd=ROOT,
            input=b"alpha\r\nbeta\r\n",
            capture_output=True,
            check=True,
        ).stdout
        assert lf == crlf


def test_non_default_home_rejects_installer_actions_but_allows_status(
    tmp_path,
    monkeypatch,
):
    layout = rappctl.Layout.current(tmp_path / "custom-home")
    target = {
        "repository": rappctl.DEFAULT_REPO,
        "tag": "fixture",
        "commit": "a" * 40,
        "tree": "b" * 40,
        "version": "1.0.0",
        "version_url": (
            "https://raw.githubusercontent.com/microsoft/"
            f"aibast-agents-library/{'a' * 40}/rapp_brainstem/VERSION"
        ),
    }
    install_fake_lock(monkeypatch, target)
    monkeypatch.setattr(
        rappctl,
        "probe_health",
        lambda _layout, timeout=2.0, environment_binding=None: {
            "reachable": False,
            "http_status": None,
            "status": "offline",
            "version": None,
            "port": 45678,
        },
    )
    monkeypatch.setattr(rappctl, "_port_listening", lambda _port: False)
    status = rappctl.inspect(layout)
    assert status["release"]["installed"] is False
    with pytest.raises(rappctl.OperatorError, match="non-default --home"):
        rappctl._require_default_home(layout, "bootstrap")


def test_idempotency_rechecks_live_postconditions(
    tmp_path,
    monkeypatch,
):
    layout, target = init_runtime(tmp_path / ".brainstem")
    install_fake_lock(monkeypatch, target)
    plan = rappctl.create_plan(layout, "start", "github-copilot")
    try:
        first = rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
        assert first["status"] == "succeeded"
        assert first["verification"] == "pending-live-canary"
        second = rappctl.apply_plan(
            layout,
            plan["plan_hash"],
            plan["plan_hash"],
        )
        assert second["status"] == "already_applied"
        assert second["verification"] == "pending-live-canary"
        rappctl._stop_brainstem(layout)
        with pytest.raises(rappctl.OperatorError, match="no longer satisfies"):
            rappctl.apply_plan(
                layout,
                plan["plan_hash"],
                plan["plan_hash"],
            )
    finally:
        stop_if_running(layout)


def test_corrupt_evidence_fails_closed(tmp_path):
    layout, _target = init_runtime(tmp_path / ".brainstem")
    log = rappctl.EvidenceLog(layout)
    log.ensure()
    frame_file = sorted(layout.frames_dir.glob("*.json"))[-1]
    frame = json.loads(frame_file.read_text(encoding="utf-8"))
    frame["payload"]["privacy"] = "tampered"
    frame_file.write_text(json.dumps(frame), encoding="utf-8")
    with pytest.raises(rappctl.OperatorError, match="chain failed"):
        log.verify()


def test_marketplace_manifests_are_shared_and_plugin_manifests_match():
    copilot_marketplace = (
        ROOT / ".github/plugin/marketplace.json"
    ).read_bytes()
    claude_marketplace = (
        ROOT / ".claude-plugin/marketplace.json"
    ).read_bytes()
    assert copilot_marketplace == claude_marketplace
    marketplace = json.loads(copilot_marketplace)
    assert marketplace["name"] == "rapp"
    assert marketplace["plugins"] == [
        {
            "name": "rapp-brainstem",
            "displayName": "RAPP Brainstem",
            "description": (
                "Give the user their Brainstem and operate it through the AI "
                "they already use."
            ),
            "version": "0.2.1",
            "source": "./",
            "category": "productivity",
            "tags": [
                "rapp",
                "brainstem",
                "agents",
                "setup",
                "maintenance",
            ],
        }
    ]
    assert (
        ROOT / "plugin.json"
    ).read_bytes() == (
        ROOT / ".claude-plugin/plugin.json"
    ).read_bytes()


def test_public_story_has_one_product_and_one_instruction():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (
        ROOT / "skills/rapp-brainstem/SKILL.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join((page, readme, skill)).lower()
    assert "give me my brainstem" in combined
    assert "your ai changes." in combined
    assert "your brainstem stays." in combined
    assert "one brainstem. any ai." in combined
    assert "personless" not in combined
    assert "harness" not in combined
    assert "rapp drive" not in combined
    assert (
        "Never execute `~/.rapp/operator/rapp_operator/rappctl.py`"
        in skill
    )
    assert "healthy Brainstem with `runtime.state == \"unknown-process\"`" in skill
    assert "Never run fresh bootstrap" in " ".join(skill.split())


def test_public_page_keeps_ai_setup_primary_and_manual_install_external():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    normalized = " ".join(page.split())
    prompt = (
        "Open https://kody-w.github.io/rapp-brainstem/ and give me my "
        "RAPP Brainstem."
    )
    assert prompt in normalized
    assert "http://localhost:7071/health/public" in page
    assert "POST /chat" in page
    assert "https://aka.ms/rappinstall" in page
    assert "curl -fsSL" not in page
    assert "irm https://" not in page
