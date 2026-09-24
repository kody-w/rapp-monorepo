"""
rapp_seed_runner_agent.py — boot and run a RAPP Work organization seed from inside a Brainstem.

A twin hatched from a seed Egg keeps its own seed record, pinned dependency checkouts and hive under
~/.brainstem/twin/ (or RAPP_TWIN_ROOT). This organ runs the Hive Hub seed flow the way hive-network describes
it, with the twin's own pinned RAPP Work SDK and RAPP/1 checkouts:

  verify_seed   every package byte, the deterministic archive, the manifest commitments, inert status
  plan          qualify the pinned checkouts, plan the native Organization and every member Workspace
  activate      apply only the owner-approved plan set (sha256 of state/plans/MANIFEST.json), copy each member's
                work/ templates create-only, register same-world pointers, verify
  tasks, claim, deliver, complete   work the case task board: deliver copies an artifact from this twin's root
                into a claimed task's declared output, complete verifies and hashes every output

Seed files stay inert data: nothing inside a seed is imported or executed. Standalone: `python
rapp_seed_runner_agent.py` prints the runner status and exits 0.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # pragma: no cover — standalone / openrappter fallback
    try:
        from basic_agent import BasicAgent  # type: ignore
    except ImportError:
        class BasicAgent:  # type: ignore
            def __init__(self, name=None, metadata=None):
                self.name = name or getattr(self, "name", "BasicAgent")
                self.metadata = metadata or getattr(self, "metadata", {})

            def system_context(self):
                return None


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/rapp_seed_runner_agent",
    "version": "0.1.0",
    "display_name": "SeedRunner",
    "description": "Boots a RAPP Work organization seed inside a Brainstem: verify, plan, owner-approved activation, and task work.",
    "author": "@kody-w",
    "tags": ["rapp-work", "seed", "hive", "egg", "twin", "experimental"],
    "category": "core",
    "quality_tier": "experimental",
    "requires_env": [],
    "example_call": "Boot my seed: verify it and show me the activation plan",
}

ACTIONS = ["status", "verify_seed", "plan", "activate", "tasks", "claim", "deliver", "complete"]
LABEL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CLEAN_ENV_KEYS = ("PATH", "TMPDIR")


def _root() -> Path:
    return Path(os.environ.get("RAPP_TWIN_ROOT") or Path.home() / ".brainstem" / "twin").expanduser().resolve()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _reply(ok: bool, summary: str, **extra) -> str:
    return json.dumps({"ok": ok, "summary": summary, **extra}, ensure_ascii=False, default=str)


class Refused(RuntimeError):
    pass


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise Refused(message)


def _relative(value: str) -> str:
    path = PurePosixPath(value)
    _require(isinstance(value, str) and value and not path.is_absolute() and "\\" not in value and ":" not in value
             and all(part not in {"", ".", "..", ".git"} for part in path.parts), f"unsafe relative path {value!r}")
    return value


def _deterministic_zip(files: dict[str, bytes]) -> bytes:
    """Byte-identical to the Hive Hub seed builder's archive (stored, sorted, 2000-01-01, 0644)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for relative, data in sorted(files.items()):
            entry = zipfile.ZipInfo(relative, (2000, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return buffer.getvalue()


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    env = {"PATH": os.environ.get("PATH", os.defpath), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_NO_REPLACE_OBJECTS": "1"}
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args], text=True, env=env).strip()


def _qualify(root: Path, commit: str) -> None:
    """The same exact-checkout proof Hive Hub's native exercise uses: pinned commit, clean, no hidden index flags,
    every tracked blob byte-identical to its commit, no ignored importable code."""
    _require(root.is_dir() and not root.is_symlink(), f"{root.name}: dependency checkout missing")
    _require(_git(root, "rev-parse", "HEAD") == commit, f"{root.name}: not at pinned commit {commit}")
    _require(not _git(root, "status", "--porcelain", "--untracked-files=all"), f"{root.name}: checkout is dirty")
    _require(all(line.startswith("H ") for line in _git(root, "ls-files", "-v").splitlines()), f"{root.name}: hidden index flags")
    for line in _git(root, "ls-tree", "-r", "HEAD").splitlines():
        metadata, relative = line.split("\t", 1)
        mode, kind, object_id = metadata.split()
        _require(kind == "blob" and mode in {"100644", "100755"}, f"{root.name}: unqualified entry {relative}")
        data = (root / relative).read_bytes()
        blob = f"blob {len(data)}\0".encode("ascii") + data
        _require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == object_id, f"{root.name}: {relative} differs from its commit")
    ignored = _git(root, "ls-files", "--others", "--ignored", "--exclude-standard").splitlines()
    _require(not any(Path(item).suffix in {".py", ".so", ".pyd"} for item in ignored), f"{root.name}: ignored importable code")


SDK_SCRIPT = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
request = json.load(open(sys.argv[2], encoding="utf-8"))
op = request["op"]
if op in ("plan", "apply"):
    from rapp_work import scaffold
    out = {}
    for item in request["members"]:
        inputs = {**item["scaffold"], "owner_label": request["owner_label"], "root": item["root"]}
        if op == "apply":
            inputs.update(apply=True, plan=item["plan"], plan_sha256=item["plan_sha256"])
        out[item["id"]] = scaffold(inputs)
    print(json.dumps(out, sort_keys=True, default=str))
elif op == "register":
    from rapp_work import Organization, Workspace
    organization = Organization.load(request["organization"])
    registered = []
    for path in request["workspaces"]:
        workspace = Workspace.load(path)
        checked = workspace.verify()
        if checked.get("status") != "verified":
            raise SystemExit(f"workspace {path} failed verify")
        plan = organization.plan_register(workspace)
        organization.apply_register(workspace, plan, plan_sha256=plan.sha256)
        registered.append({"path": path, "plan_sha256": plan.sha256})
    checked = organization.verify()
    pointers = [{"world_id": p.get("world_id"), "rappid": p.get("rappid")} for p in organization.pointers()]
    print(json.dumps({"registered": registered, "verify": checked, "pointers": pointers}, sort_keys=True, default=str))
elif op == "verify":
    from rapp_work import Organization
    organization = Organization.load(request["organization"])
    checked = organization.verify()
    pointers = [{"world_id": p.get("world_id"), "rappid": p.get("rappid")} for p in organization.pointers()]
    print(json.dumps({"verify": checked, "pointers": pointers}, sort_keys=True, default=str))
"""


class SeedRunnerAgent(BasicAgent):
    def __init__(self):
        self.name = "SeedRunner"
        self.metadata = {
            "name": self.name,
            "description": (
                "Boots and runs this twin's RAPP Work organization seed. status shows where the seed is; verify_seed checks "
                "every byte; plan returns the activation digest to show the owner; activate needs that exact digest from "
                "the owner's own message; tasks/claim/complete work the case task board with evidence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ACTIONS, "description": "Seed step to run."},
                    "approve": {"type": "string", "description": "activate: the exact activation digest the owner approved."},
                    "task": {"type": "string", "description": "claim/complete: task id from the board."},
                    "assignee": {"type": "string", "description": "claim: who works the task (default this twin)."},
                    "output": {"type": "string", "description": "deliver: one of the task's declared outputs, e.g. deliverables/brief/BRIEF.md."},
                    "source": {"type": "string", "description": "deliver: path of the produced artifact inside this twin's root (absolute, or relative to the twin root)."},
                    "content": {"type": "string", "description": "deliver: text content to write instead of copying a file (for briefs and notes)."},
                    "notes": {"type": "string", "description": "complete: what was done and where the evidence is."},
                },
                "required": ["action"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    # ---------- state ----------
    @staticmethod
    def _paths(root: Path) -> dict:
        return {"twin": root / "twin.json", "record": root / "seed" / "record.json", "state": root / "state",
                "plans": root / "state" / "plans", "hive": root / "hive", "deps": root / "deps",
                "verified": root / "state" / "seed-verified.json", "activation": root / "state" / "activation.json"}

    def _record(self, root: Path) -> dict:
        path = self._paths(root)["record"]
        _require(path.is_file(), "no seed record at seed/record.json (was this twin hatched?)")
        return _read_json(path)

    def _twin(self, root: Path) -> dict:
        path = self._paths(root)["twin"]
        return _read_json(path) if path.is_file() else {}

    def _board_path(self, root: Path, record: dict) -> Path:
        casework = next(m for m in record["workspaces"] if m["id"] == "casework")
        return root / "hive" / _relative(casework["directory"]) / "work" / "task-board.json"

    def _members(self, root: Path, record: dict) -> list[dict]:
        org = record["organization"]
        members = [{"id": "organization", "directory": org["directory"], "scaffold": org["scaffold"], "template": None}]
        members += [{"id": m["id"], "directory": m["directory"], "scaffold": m["scaffold"], "template": m["template"]}
                    for m in record["workspaces"]]
        for m in members:
            _relative(m["directory"])
            m["root"] = str(root / "hive" / m["directory"])
        return members

    def _sdk(self, root: Path, request: dict) -> dict:
        record = self._record(root)
        sdk = self._paths(root)["deps"] / "rapp-work"
        env = {k: os.environ[k] for k in CLEAN_ENV_KEYS if k in os.environ}
        env.update(LC_ALL="C", LANG="C", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0",
                   RAPP_WORK_NETWORK_DEFAULT="disabled", RAPP_WORK_EXTERNAL_EFFECTS="refuse")
        request_file = self._paths(root)["state"] / "sdk-request.json"
        _write_json(request_file, request)
        try:
            run = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", SDK_SCRIPT, str(sdk / "src"), str(request_file)],
                                 cwd=str(sdk), env=env, capture_output=True, text=True, timeout=900)
        finally:
            request_file.unlink(missing_ok=True)
        _require(run.returncode == 0, f"SDK {request['op']} failed (exit {run.returncode}): {run.stdout[-300:]}")
        _require(bool(record), "no record")
        return json.loads(run.stdout)

    # ---------- verification ----------
    def _verify(self, root: Path) -> tuple[dict, dict[str, bytes]]:
        record = self._record(root)
        _require(record.get("schema") == "hive-hub-organization-seed/1", "not a hive-hub-organization-seed/1 record")
        files: dict[str, bytes] = {}
        for entry in record["files"]:
            path = _relative(entry["path"])
            _require(path not in files, f"duplicate package file {path}")
            data = entry["content"].encode("utf-8")
            _require(len(data) == entry["bytes"] and _sha(data) == entry["sha256"], f"file hash mismatch: {path}")
            files[path] = data
        _require(len(files) == record["counts"]["packageFiles"], "package file count mismatch")
        archive = base64.b64decode(record["archive"]["base64"], validate=True)
        _require(len(archive) == record["archive"]["bytes"] and _sha(archive) == record["archive"]["sha256"], "archive hash mismatch")
        _require(archive == _deterministic_zip(files), "archive differs from the file inventory")
        manifest = json.loads(files["seed.json"])
        _require(manifest["status"] == "seed-not-activated" and manifest["authority"] == "inert-starter-data", "seed claims activation")
        _require({e["path"] for e in manifest["inventory"]} == set(files) - {"seed.json"}, "manifest does not cover every file")
        for e in manifest["inventory"]:
            _require(_sha(files[e["path"]]) == e["sha256"] and len(files[e["path"]]) == e["bytes"], f"manifest mismatch: {e['path']}")
        for task in record["tasks"]:
            _require(task["state"] == ("ready" if not task["depends_on"] else "blocked") and task["assignee"] is None
                     and task["completed_evidence"] == [], "seed invents completed or assigned work")
        pinned = self._twin(root).get("seed_archive_sha256")
        if pinned:
            _require(pinned == record["archive"]["sha256"], "seed archive differs from the one this twin was hatched with")
        return record, files

    # ---------- actions ----------
    def perform(self, **kwargs) -> str:
        root = _root()
        action = kwargs.get("action", "status")
        if action not in ACTIONS:
            return _reply(False, f"unknown action {action!r}", actions=ACTIONS)
        try:
            return getattr(self, f"_do_{action}")(root, kwargs)
        except (Refused, ValueError, KeyError, OSError, subprocess.SubprocessError, StopIteration) as error:
            return _reply(False, f"refused: {error}")

    def _do_status(self, root: Path, kw: dict) -> str:
        p = self._paths(root)
        if not p["record"].is_file():
            return _reply(True, "no seed installed in this Brainstem yet", twin_root=str(root))
        record = self._record(root)
        twin = self._twin(root)
        state = {"seed": record["slug"], "name": record["name"], "world_id": record["organization"]["scaffold"]["world_id"],
                 "instance_rappid": twin.get("instance_rappid"), "grown_from": twin.get("grown_from"),
                 "verified": p["verified"].is_file(), "planned": (p["plans"] / "MANIFEST.json").is_file(),
                 "activated": p["activation"].is_file()}
        if state["activated"]:
            board = _read_json(self._board_path(root, record))
            counts = {}
            for t in board["tasks"]:
                counts[t["state"]] = counts.get(t["state"], 0) + 1
            state["tasks"] = counts
            state["ready"] = [t["id"] for t in board["tasks"] if t["state"] == "ready"]
            nxt = "work the ready tasks" if state["ready"] else ("all tasks done" if counts.get("done") == len(board["tasks"]) else "finish in-progress tasks")
        elif state["planned"]:
            nxt = "show the owner the activation digest; activate only with the owner's exact digest"
        elif state["verified"]:
            nxt = "plan"
        else:
            nxt = "verify_seed"
        return _reply(True, f"{record['name']}: next step is {nxt}", **state, next=nxt)

    def _do_verify_seed(self, root: Path, kw: dict) -> str:
        record, files = self._verify(root)
        result = {"seed": record["slug"], "archive_sha256": record["archive"]["sha256"], "package_files": len(files),
                  "teams": record["counts"]["teams"], "workspaces": record["counts"]["workspaces"], "tasks": record["counts"]["tasks"],
                  "verified_utc": _now()}
        _write_json(self._paths(root)["verified"], result)
        return _reply(True, f"seed {record['slug']} verified: {len(files)} files, {record['counts']['tasks']} tasks, inert", **result, next="plan")

    def _do_plan(self, root: Path, kw: dict) -> str:
        record, _ = self._verify(root)
        p = self._paths(root)
        deps = record["dependencies"]
        _qualify(p["deps"] / "rapp-work", deps["sdk"]["commit"])
        _qualify(p["deps"] / "rapp-1", deps["protocol"]["commit"])
        _require(_sha((p["deps"] / "rapp-work" / deps["sdk"]["entrypoint"]).read_bytes()) == deps["sdk"]["entrypoint_sha256"], "SDK entrypoint bytes mismatch")
        _require(_sha((p["deps"] / "rapp-1" / "SPEC.md").read_bytes()) == deps["protocol"]["specification_sha256"]
                 and _sha((p["deps"] / "rapp-1" / "rapp.py").read_bytes()) == deps["protocol"]["reference_sha256"], "RAPP/1 bytes mismatch")
        _require(not p["activation"].is_file(), "already activated")
        members = self._members(root, record)
        for m in members:
            _require(not Path(m["root"]).exists(), f"{m['directory']} already exists")
        (root / "hive" / "workspaces").mkdir(parents=True, exist_ok=True)
        owner = self._twin(root).get("owner_label") or "owner"
        planned = self._sdk(root, {"op": "plan", "owner_label": owner, "members": [{k: m[k] for k in ("id", "scaffold", "root")} for m in members]})
        manifest = []
        for m in members:
            envelope = planned[m["id"]]
            _require(envelope.get("status") == "planned", f"{m['id']}: SDK did not plan ({envelope.get('refusal')})")
            result = envelope["result"]
            plan = result["plan"]
            _require(plan.get("network") is False and not result.get("effects"), f"{m['id']}: plan requests network or effects")
            _write_json(p["plans"] / f"{m['id']}.json", {"member": m["id"], "root": m["root"], "scaffold": m["scaffold"], "envelope": envelope})
            manifest.append({"id": m["id"], "slug": m["scaffold"]["slug"], "kind": m["scaffold"]["kind"], "mode": m["scaffold"]["mode"],
                             "world_id": m["scaffold"]["world_id"], "rappid": plan["subject"]["rappid"],
                             "plan_sha256": result["plan_sha256"], "actions": len(plan["actions"])})
        data = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
        (p["plans"] / "MANIFEST.json").write_bytes(data)
        digest = _sha(data)
        return _reply(True, f"activation planned for {len(manifest)} members; show the owner this digest and wait for approval",
                      activation_digest=digest, owner_label=owner, members=[{k: e[k] for k in ("id", "slug", "rappid")} for e in manifest],
                      next="activate with the owner's exact digest")

    def _do_activate(self, root: Path, kw: dict) -> str:
        record, files = self._verify(root)
        p = self._paths(root)
        _require(not p["activation"].is_file(), "already activated")
        manifest_path = p["plans"] / "MANIFEST.json"
        _require(manifest_path.is_file(), "no plan yet: run plan first")
        digest = _sha(manifest_path.read_bytes())
        _require(kw.get("approve") == digest, "approval digest does not match the planned activation exactly")
        members = self._members(root, record)
        saved = {m["id"]: _read_json(p["plans"] / f"{m['id']}.json") for m in members}
        owner = self._twin(root).get("owner_label") or "owner"
        applied = self._sdk(root, {"op": "apply", "owner_label": owner, "members": [
            {"id": m["id"], "scaffold": m["scaffold"], "root": m["root"],
             "plan": saved[m["id"]]["envelope"]["result"]["plan"], "plan_sha256": saved[m["id"]]["envelope"]["result"]["plan_sha256"]}
            for m in members]})
        for m in members:
            _require(applied[m["id"]].get("status") == "applied", f"{m['id']}: apply refused ({applied[m['id']].get('refusal')})")
        copied = 0
        for m in members:
            if not m["template"]:
                continue
            prefix = _relative(m["template"]) + "/"
            for path, data in sorted(files.items()):
                if not path.startswith(prefix):
                    continue
                relative = _relative(path[len(prefix):])
                _require(relative.startswith("work/"), f"template escaped the work namespace: {path}")
                target = Path(m["root"]) / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, "xb") as out:
                    out.write(data)
                copied += 1
        registered = self._sdk(root, {"op": "register", "organization": members[0]["root"], "workspaces": [m["root"] for m in members[1:]]})
        world = record["organization"]["scaffold"]["world_id"]
        pointers = registered["pointers"]
        _require(registered["verify"].get("pointers") == len(members) - 1, "membership count mismatch after registration")
        _require(all(ptr["world_id"] == world for ptr in pointers), "a pointer crosses the world boundary")
        receipt = {"activated_utc": _now(), "activation_digest": digest, "seed": record["slug"], "seed_archive_sha256": record["archive"]["sha256"],
                   "world_id": world, "members": [{"id": m["id"], "rappid": saved[m["id"]]["envelope"]["result"]["plan"]["subject"]["rappid"]} for m in members],
                   "template_files": copied, "pointers": len(pointers), "approved_by": kw.get("assignee") or "owner"}
        _write_json(p["activation"], receipt)
        board = _read_json(self._board_path(root, record))
        ready = [t["id"] for t in board["tasks"] if t["state"] == "ready"]
        return _reply(True, f"hive activated: {len(members)} native identities in world {world}, {len(pointers)} pointers, {copied} template files",
                      **{k: receipt[k] for k in ("world_id", "members", "pointers")}, ready=ready, next="work the ready tasks")

    def _board(self, root: Path) -> tuple[dict, Path, dict]:
        record = self._record(root)
        _require(self._paths(root)["activation"].is_file(), "the hive is not activated yet")
        path = self._board_path(root, record)
        return _read_json(path), path, record

    def _do_tasks(self, root: Path, kw: dict) -> str:
        board, _, _ = self._board(root)
        rows = [{"id": t["id"], "team": t["team"], "state": t["state"], "title": t["title"], "depends_on": t["depends_on"],
                 "outputs": t["outputs"], "assignee": t["assignee"]} for t in board["tasks"]]
        done = sum(t["state"] == "done" for t in board["tasks"])
        return _reply(True, f"{done}/{len(rows)} tasks done; ready: {', '.join(r['id'] for r in rows if r['state'] == 'ready') or 'none'}", tasks=rows)

    def _do_claim(self, root: Path, kw: dict) -> str:
        board, path, _ = self._board(root)
        task = next((t for t in board["tasks"] if t["id"] == kw.get("task")), None)
        _require(task is not None, f"no task {kw.get('task')!r}")
        _require(task["state"] == "ready", f"task {task['id']} is {task['state']}, not ready")
        task.update(state="in-progress", assignee=kw.get("assignee") or self._twin(root).get("name") or "twin")
        _write_json(path, board)
        return _reply(True, f"claimed {task['id']}: {task['title']}", instructions=task["instructions"], inputs=task["inputs"],
                      outputs=task["outputs"], acceptance=task["acceptance"], work_dir=str(path.parent))

    def _do_deliver(self, root: Path, kw: dict) -> str:
        board, path, _ = self._board(root)
        task = next((t for t in board["tasks"] if t["id"] == kw.get("task")), None)
        _require(task is not None, f"no task {kw.get('task')!r}")
        _require(task["state"] == "in-progress", f"task {task['id']} is {task['state']}; claim it first")
        output = kw.get("output")
        _require(output in task["outputs"], f"{output!r} is not a declared output of {task['id']}: {task['outputs']}")
        target = path.parent / _relative(output)
        if kw.get("content") is not None:
            data = str(kw["content"]).encode("utf-8")
        else:
            raw = Path(str(kw.get("source") or ""))
            source = (raw if raw.is_absolute() else root / raw).resolve()
            _require(source == root or root in source.parents, "source must be inside this twin's root")
            _require(source.is_file(), f"source {kw.get('source')!r} not found")
            data = source.read_bytes()
        _require(len(data) > 0, "refusing to deliver an empty artifact")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        remaining = [o for o in task["outputs"] if not (path.parent / o).is_file()]
        return _reply(True, f"delivered {output} ({len(data)} bytes, sha256 {_sha(data)[:12]})",
                      remaining_outputs=remaining, next="complete" if not remaining else "deliver the remaining outputs")

    def _do_complete(self, root: Path, kw: dict) -> str:
        board, path, _ = self._board(root)
        task = next((t for t in board["tasks"] if t["id"] == kw.get("task")), None)
        _require(task is not None, f"no task {kw.get('task')!r}")
        _require(task["state"] == "in-progress", f"task {task['id']} is {task['state']}; claim it first")
        work = path.parent
        evidence = []
        for output in task["outputs"]:
            target = work / _relative(output)
            _require(target.is_file() and target.stat().st_size > 0, f"output {output} is missing or empty under casework/work/")
            data = target.read_bytes()
            evidence.append({"path": output, "bytes": len(data), "sha256": _sha(data)})
        if kw.get("notes"):
            evidence.append({"note": kw["notes"][:2000]})
        task.update(state="done", completed_evidence=evidence, completed_utc=_now())
        done = {t["id"] for t in board["tasks"] if t["state"] == "done"}
        unblocked = []
        for t in board["tasks"]:
            if t["state"] == "blocked" and set(t["depends_on"]) <= done:
                t["state"] = "ready"
                unblocked.append(t["id"])
        _write_json(path, board)
        return _reply(True, f"completed {task['id']} with {len([e for e in evidence if 'sha256' in e])} evidence file(s)", unblocked=unblocked)

    def system_context(self):
        try:
            state = json.loads(self._do_status(_root(), {}))
            if state.get("seed"):
                return f"Seed {state['name']} ({state['world_id']}): next step is {state['next']}."
        except Exception:
            return None
        return None


if __name__ == "__main__":
    print(SeedRunnerAgent().perform(action="status"))
