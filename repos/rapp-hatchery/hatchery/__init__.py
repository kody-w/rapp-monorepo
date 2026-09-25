"""Brainstem Hatchery: hatch a RAPP brainstem just in time.

    from hatchery import Hatchling

    with Hatchling(egg="you--my-desk.egg") as bs:     # on the grail engine the egg expects, pinned
        print(bs.chat("What can you do?").response)

A hatchling is a brainstem hatched on demand. It is the unmodified grail engine (kody-w/rapp-installer) at
a pinned ref, plus whatever you hatch into it: nothing, a soul and agents, or a rapp/1 organism egg. It runs
on its own loopback port in ~/.brainstem/hatchlings/<name>, beside the brainstem you installed on :7071.
It never writes to that brainstem; it only reuses its GitHub sign-in. Release a hatchling when you are
done, or keep it: a hatchling you keep is a twin.

The engine is fetched once into a local mirror, and each hatchling is a cheap local clone of it, detached
at the pinned commit with its push URL disabled, so nothing a hatchling does can reach the grail. Python
packages are installed once per set of engine requirements and shared.

Standard library only.
"""
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from . import rapp1   # the RAPP reference implementation, vendored verbatim (see rapp1.vendor.json)

__all__ = ["Hatchling", "ChatResult", "HatcheryError", "list_hatchlings", "release", "SOURCES"]
__version__ = "0.1.0"

SOURCES = {
    "grail": "https://github.com/kody-w/rapp-installer.git",
    "canary": "https://github.com/kody-w/rapp-canary.git",
}
ROOT = Path(os.getenv("HATCHERY_ROOT", Path.home() / ".brainstem" / "hatchlings")).expanduser()
CACHE = Path(os.getenv("HATCHERY_CACHE", Path.home() / ".brainstem" / "hatchery")).expanduser()
INSTALLED = Path.home() / ".brainstem" / "src" / "rapp_brainstem"   # read for its sign-in only, never written
FIRST_PORT = 7120
PUSH_BLOCK = "DISABLED-hatchling-is-read-only"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
# Mirrors the web UI (index.html cappedHistory), so multi-turn use sends what a real session sends.
UI_HISTORY_MSGS = 40
UI_HISTORY_CHARS = 60000


class HatcheryError(RuntimeError):
    pass


@dataclass
class ChatResult:
    response: str
    agent_logs: str
    session_id: str
    model: str
    raw: dict = field(repr=False)

    @property
    def agents_called(self):
        """Agent names that ran this turn, from the [Name] prefixes in agent_logs."""
        names = []
        for line in (self.agent_logs or "").splitlines():
            if line.startswith("[") and "]" in line:
                name = line[1:line.index("]")]
                if name not in names:
                    names.append(name)
        return names


# ── small helpers ────────────────────────────────────────────────────────────

def _port_busy(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _alive(pid):
    if not pid:
        return False
    if hasattr(os, "WNOHANG"):
        try:                                   # reap our own child if it has exited (else it lingers as a zombie)
            if os.waitpid(pid, os.WNOHANG)[0] == pid:
                return False
        except ChildProcessError:
            pass                               # not our child: hatched by another process
        except OSError:
            pass
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read(path, default=None):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return default


def _utc():
    t = time.time()
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + f".{int(t * 1000) % 1000:03d}Z"


def _git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise HatcheryError(f"git {' '.join(args[:2])} failed: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout.strip()


def _fetch(where, limit=64 * 1024 * 1024):
    """Bytes of a local file or an https URL (for example an egg in a catalog)."""
    where = str(where)
    if where.startswith("http://"):
        raise HatcheryError("refusing plain http; use an https URL")
    if where.startswith("https://"):
        try:
            with urllib.request.urlopen(where, timeout=60) as r:
                data = r.read(limit + 1)
        except (urllib.error.URLError, OSError) as e:
            raise HatcheryError(f"could not download {where}: {e}")
        if len(data) > limit:
            raise HatcheryError(f"{where} is larger than {limit} bytes")
        return data
    path = Path(where).expanduser()
    if not path.is_file():
        raise HatcheryError(f"file not found: {path}")
    return path.read_bytes()


@contextmanager
def _lock(path, timeout=600):
    """A directory lock, so two hatchlings never build the same mirror or venv at once."""
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    while True:
        try:
            path.mkdir()
            break
        except FileExistsError:
            if time.time() > deadline:
                raise HatcheryError(f"timed out waiting for {path}; remove it if no hatchery is running")
            time.sleep(0.2)
    try:
        yield
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _saved_token():
    """GITHUB_TOKEN, else the installed brainstem's sign-in, else one the hatchery saved earlier."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token
    for f in (INSTALLED / ".copilot_token", CACHE / ".copilot_token"):
        try:
            token = json.loads(f.read_text()).get("access_token", "")
        except (OSError, ValueError, AttributeError):
            continue
        if token:
            return token
    return ""


# ── the engine: a local mirror of the grail, pinned per hatchling ────────────

def _engine_url(source):
    if source in SOURCES:
        return SOURCES[source]
    if re.match(r"^(https://|ssh://|git@)", source):
        return source
    path = Path(source).expanduser()
    if (path / ".git").exists() or (path / "HEAD").is_file():
        return str(path.resolve())
    raise HatcheryError(f"unknown engine source {source!r}: use grail, canary, a git URL or a local repository")


def _resolve(mirror, ref):
    # --git-dir, not -C: the mirror is bare, and safe.bareRepository=explicit refuses implicit bare repositories.
    r = subprocess.run(["git", f"--git-dir={mirror}", "rev-parse", "--verify", "-q", f"{ref or 'HEAD'}^{{commit}}"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _engine(source, ref):
    """(url, mirror, commit): the engine's mirror refreshed as needed and the ref resolved to a commit.

    A pinned commit already in the mirror needs no network. The default head, or a branch or tag, is
    refreshed first because it may have moved; offline, the mirror's copy is used."""
    url = _engine_url(source)
    mirror = CACHE / "engines" / (hashlib.sha256(url.encode()).hexdigest()[:16] + ".git")
    with _lock(mirror.with_suffix(".lock")):
        if not mirror.exists():
            tmp = mirror.with_suffix(".partial")
            shutil.rmtree(tmp, ignore_errors=True)
            _git("clone", "-q", "--mirror", url, str(tmp))
            tmp.rename(mirror)
        pinned = bool(ref) and re.fullmatch(r"[0-9a-f]{7,40}", ref) is not None
        commit = _resolve(mirror, ref) if pinned else None
        if commit is None:
            subprocess.run(["git", f"--git-dir={mirror}", "fetch", "-q", "--prune", "origin"], capture_output=True)
            commit = _resolve(mirror, ref)
        if commit is None and pinned:
            subprocess.run(["git", f"--git-dir={mirror}", "fetch", "-q", "origin", ref], capture_output=True)
            commit = _resolve(mirror, ref)
    if commit is None:
        raise HatcheryError(f"{ref or 'HEAD'} is not in {url}")
    return url, mirror, commit


def _base_python():
    for candidate in (os.getenv("HATCHERY_PYTHON"), shutil.which("python3.11"),
                      "/opt/homebrew/bin/python3.11", "/usr/local/bin/python3.11", sys.executable):
        if candidate and Path(candidate).exists():
            return candidate
    raise HatcheryError("no Python found; set HATCHERY_PYTHON")


def _venv_for(requirements):
    """A venv shared by every hatchling whose engine has these requirements (built once, then instant)."""
    base = _base_python()
    wanted = requirements.read_bytes() if requirements.is_file() else b""
    version = subprocess.run([base, "-c", "import sys; print(sys.version.split()[0])"],
                             capture_output=True, text=True).stdout.strip()
    venv = CACHE / "venvs" / hashlib.sha256(wanted + version.encode()).hexdigest()[:16]
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    with _lock(venv.with_suffix(".lock")):
        if not (venv / ".ready").exists():
            shutil.rmtree(venv, ignore_errors=True)
            subprocess.run([base, "-m", "venv", str(venv)], check=True, capture_output=True)
            if wanted.strip():
                r = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r",
                                    str(requirements)], capture_output=True, text=True)
                if r.returncode != 0:
                    shutil.rmtree(venv, ignore_errors=True)
                    raise HatcheryError(f"pip could not install the engine's requirements: {r.stderr.strip()[-600:]}")
            (venv / ".ready").write_text(version)
    return str(py)


# ── hatchlings ───────────────────────────────────────────────────────────────

class Hatchling:
    """One brainstem hatched just in time. A context manager releases it on exit unless kept."""

    def __init__(self, name=None, source=None, ref=None, egg=None, agents=(), soul=None, bare=None, env=None,
                 port=None, keep=False, sign_in=True, start_timeout=90):
        self.name = name
        self.egg = egg
        self._egg = self._read_egg(egg) if egg else None
        engine = ((self._egg or ({}, {}))[0].get("payload") or {}).get("engine") or {}
        from_egg = engine.get("source") in SOURCES
        self.source = str(source or (engine["source"] if from_egg else "grail"))
        self.ref = ref or (engine.get("commit") or None if from_egg and not source else None)
        self.agents = [Path(a).expanduser() for a in agents]
        self.soul = Path(soul).expanduser() if soul else None
        self.bare = bool(egg) if bare is None else bool(bare)
        self.env = {k: str(v) for k, v in (env or {}).items()}
        self.port = port
        self.kept = bool(keep)
        self.sign_in = sign_in
        self.start_timeout = start_timeout
        self.engine_url = None
        self.commit = None
        self.pid = None
        self.python = None
        self.created_utc = None
        self.session_id = None
        self.history = []

    # paths
    @property
    def dir(self):
        return ROOT / self.name

    @property
    def brainstem_dir(self):
        return self.dir / "engine" / "rapp_brainstem"

    @property
    def log_path(self):
        return self.dir / "server.log"

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"

    # lifecycle
    def hatch(self):
        """Fetch the engine at its pinned ref, lay in the egg, soul and agents, start it, and wait for it."""
        ROOT.mkdir(parents=True, exist_ok=True)
        taken = {int(r["port"]) for r in list_hatchlings() if str(r["port"]).isdigit()}
        if self.port is None:
            self.port = FIRST_PORT
            while _port_busy(self.port) or self.port in taken:
                self.port += 1
        elif _port_busy(self.port) or self.port in taken:
            raise HatcheryError(f"port {self.port} is already in use")
        self.name = self.name or f"hatchling-{self.port}"
        if not NAME.match(self.name):
            raise HatcheryError(f"name {self.name!r} must be lowercase letters, digits and hyphens")
        if self.dir.exists():
            raise HatcheryError(f"{self.dir} already exists; release('{self.name}') first")
        self.dir.mkdir(parents=True)
        try:
            self.engine_url, mirror, self.commit = _engine(self.source, self.ref)
            engine = self.dir / "engine"
            _git("clone", "-q", "--no-checkout", str(mirror), str(engine))
            _git("-C", str(engine), "remote", "set-url", "origin", self.engine_url)
            _git("-C", str(engine), "remote", "set-url", "--push", "origin", PUSH_BLOCK)
            _git("-C", str(engine), "checkout", "-q", "--detach", self.commit)
            if not (self.brainstem_dir / "brainstem.py").is_file():
                raise HatcheryError(f"{self.engine_url} at {self.commit[:12]} has no rapp_brainstem/brainstem.py")
            self._lay_in()
            self.created_utc = _utc()
            self.python = _venv_for(self.brainstem_dir / "requirements.txt")
            self._save()
            self.start()
        except BaseException:
            self.release(quiet=True)
            raise
        return self

    def _lay_in(self):
        agents_dir = self.brainstem_dir / "agents"
        if self.bare:            # park the engine's own agents; basic_agent.py is the base class and stays
            parked = self.dir / "parked-agents"
            for f in sorted(agents_dir.rglob("*_agent.py")):
                if f.name != "basic_agent.py":
                    dest = parked / f.relative_to(agents_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    f.rename(dest)
        if self._egg:
            manifest, files = self._egg
            for path, octets in files.items():
                if path == "rappid.json":
                    continue          # the egg's identity; the instance gets its own below (§9.4)
                dest = self.brainstem_dir / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(octets)
            parts = rapp1.rappid_parts(manifest["rappid"])
            (self.dir / "instance.json").write_text(json.dumps({
                "rappid": rapp1.mint_rappid(parts["owner"], parts["slug"]),
                "artifact": manifest["rappid"],
                "grown_from": rapp1.egg_address(manifest),
            }, indent=2) + "\n")
        if self.soul:
            if not self.soul.is_file():
                raise HatcheryError(f"soul file not found: {self.soul}")
            shutil.copy(self.soul, self.brainstem_dir / "soul.md")
        for a in self.agents:
            self.add_agent(a)

    @staticmethod
    def _read_egg(egg):
        blob = _fetch(egg)
        ok, step, why = rapp1.verify_egg(blob)
        if not ok:
            raise HatcheryError(f"egg failed verification at {step}: {why}")
        manifest, files = rapp1.read_egg(blob)
        if manifest["variant"] != "organism":
            raise HatcheryError(f"expected an organism egg, got {manifest['variant']}")
        return manifest, files

    def start(self):
        """Start (or restart) the brainstem process and wait until it answers."""
        if _alive(self.pid):
            return self
        if _port_busy(self.port):
            raise HatcheryError(f"port {self.port} is already in use")
        env = {k: v for k, v in os.environ.items() if k not in ("SOUL_PATH", "AGENTS_PATH")}
        env.update(PORT=str(self.port), BRAINSTEM_LAN_MODE="false", BRAINSTEM_ALLOWED_HOSTS="")
        token = _saved_token()
        if token:
            env["GITHUB_TOKEN"] = token
        env.update(self.env)
        python = self.python if self.python and Path(self.python).exists() else _venv_for(
            self.brainstem_dir / "requirements.txt")
        self.python = python
        with open(self.log_path, "ab") as log:
            proc = subprocess.Popen([python, "brainstem.py"], cwd=self.brainstem_dir, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        self.pid = proc.pid
        self._save()
        deadline = time.time() + self.start_timeout
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                health = self.health()
            except HatcheryError:
                time.sleep(0.4)
                continue
            if self.sign_in and health.get("copilot") != "\u2713":
                self._device_sign_in()
            return self
        tail = "\n".join((_read(self.log_path, "") or "").splitlines()[-20:])
        raise HatcheryError(f"{self.name} did not answer on :{self.port}. Last log lines:\n{tail}")

    def _device_sign_in(self, timeout=900):
        """No saved sign-in on this machine: run GitHub's device login once and keep it for later hatchlings."""
        started = self._request("POST", "/login", {}, timeout=30)
        if started.get("error"):
            raise HatcheryError(f"could not start GitHub sign-in: {started['error']}")
        print(f"\nSign in to GitHub Copilot for this brainstem:\n  1. Open {started.get('verification_uri')}\n"
              f"  2. Enter the code {started.get('user_code')}\n", file=sys.stderr, flush=True)
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(5)
            r = self._request("POST", "/login/poll", {}, timeout=30)
            if r.get("status") == "ok":
                saved = self.brainstem_dir / ".copilot_token"
                if saved.exists():
                    CACHE.mkdir(parents=True, exist_ok=True)
                    shutil.copy(saved, CACHE / ".copilot_token")
                    os.chmod(CACHE / ".copilot_token", 0o600)
                return
            if r.get("status") in ("expired", "error"):
                raise HatcheryError(f"GitHub sign-in failed: {r.get('error') or r.get('status')}")
        raise HatcheryError("GitHub sign-in timed out")

    def stop(self):
        """Stop the process; the hatchling's files stay, and start() brings it back."""
        pid = self.pid
        if _alive(pid):
            try:
                os.killpg(pid, signal.SIGTERM)
            except OSError:
                os.kill(pid, signal.SIGTERM)
            for _ in range(20):
                if not _alive(pid):
                    break
                time.sleep(0.25)
            if _alive(pid):
                try:
                    os.killpg(pid, signal.SIGKILL)
                except OSError:
                    pass
        self.pid = None
        if self.name and self.dir.exists():
            self._save()
        return self

    def keep(self):
        """Keep this hatchling: it becomes a twin, and release('all') leaves it alone."""
        self.kept = True
        self._save()
        return self

    def release(self, quiet=False):
        """Stop it and delete its folder. The engine it was hatched from is untouched."""
        if not self.name or not self.dir.exists():
            return
        if self.dir.resolve().parent != ROOT.resolve():
            if quiet:
                return
            raise HatcheryError(f"refusing to delete {self.dir}: it is not inside {ROOT}")
        self.stop()
        shutil.rmtree(self.dir)

    def __enter__(self):
        return self.hatch()

    def __exit__(self, *exc):
        if not self.kept:
            self.release()

    def _save(self):
        (self.dir / "hatchling.json").write_text(json.dumps({
            "name": self.name, "port": self.port, "pid": self.pid, "source": self.source,
            "engine_url": self.engine_url, "ref": self.ref, "commit": self.commit, "kept": self.kept,
            "bare": self.bare, "egg": str(self.egg) if self.egg else None, "python": self.python,
            "created_utc": self.created_utc, "hatchery": __version__,
        }, indent=2) + "\n")

    @classmethod
    def attach(cls, name):
        """The Hatchling object for one that already exists (from another script or the CLI)."""
        meta_path = ROOT / name / "hatchling.json"
        try:
            meta = json.loads(meta_path.read_text())
        except (OSError, ValueError):
            raise HatcheryError(f"no hatchling named {name}")
        h = cls(name=name, source=meta.get("source"), ref=meta.get("ref"), port=meta.get("port"),
                keep=meta.get("kept"), bare=meta.get("bare"))
        h.egg, h.engine_url, h.commit = meta.get("egg"), meta.get("engine_url"), meta.get("commit")
        h.pid, h.python, h.created_utc = meta.get("pid"), meta.get("python"), meta.get("created_utc")
        try:
            conv = json.loads((h.dir / "conversation.json").read_text())
            h.session_id, h.history = conv.get("session_id"), conv.get("history", [])
        except (OSError, ValueError):
            pass
        return h

    # using it
    def _request(self, method, path, body=None, timeout=300):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return json.loads(e.read().decode())
            except ValueError:
                raise HatcheryError(f"{method} {path} returned {e.code}")
        except (urllib.error.URLError, OSError) as e:
            raise HatcheryError(f"{self.url} is not answering: {e}")

    def health(self):
        return self._request("GET", "/health", timeout=3)

    def add_agent(self, path):
        """Drop an agent file in; the brainstem picks it up on the next request."""
        path = Path(path).expanduser()
        if not path.is_file():
            raise HatcheryError(f"agent file not found: {path}")
        dest = self.brainstem_dir / "agents" / path.name
        shutil.copy(path, dest)
        return dest

    def chat(self, message, timeout=300):
        """Send one message, continuing this hatchling's conversation like the web UI does."""
        history = self.history[-UI_HISTORY_MSGS:]
        while len(history) > 1 and sum(len(m["content"]) for m in history) > UI_HISTORY_CHARS:
            history = history[1:]
        body = {"user_input": message, "conversation_history": history}
        if self.session_id:
            body["session_id"] = self.session_id
        raw = self._request("POST", "/chat", body, timeout=timeout)
        if "error" in raw and "response" not in raw:
            raise HatcheryError(f"chat failed: {raw['error']}")
        self.session_id = raw.get("session_id", self.session_id)
        reply = raw.get("response", "")
        self.history += [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
        if self.dir.exists():
            (self.dir / "conversation.json").write_text(
                json.dumps({"session_id": self.session_id, "history": self.history}, indent=2))
        return ChatResult(reply, raw.get("agent_logs", ""), self.session_id or "", raw.get("model", ""), raw)

    def log(self, lines=40):
        return "\n".join((_read(self.log_path, "") or "").splitlines()[-lines:])

    def __repr__(self):
        return f"<Hatchling {self.name} {self.url} {self.source}@{(self.commit or '?')[:12]}>"


def list_hatchlings():
    rows = []
    if ROOT.exists():
        for meta_path in sorted(ROOT.glob("*/hatchling.json")):
            try:
                meta = json.loads(meta_path.read_text())
            except (OSError, ValueError):
                continue
            rows.append({"name": meta.get("name") or meta_path.parent.name, "port": meta.get("port"),
                         "running": _alive(meta.get("pid")), "kept": bool(meta.get("kept")),
                         "source": meta.get("source"), "commit": (meta.get("commit") or "")[:12],
                         "egg": meta.get("egg"), "dir": str(meta_path.parent)})
    return rows


def release(name, include_kept=False):
    """Release one hatchling by name, or name='all' for every one that isn't kept (include_kept for all)."""
    rows = list_hatchlings()
    names = [r["name"] for r in rows if include_kept or not r["kept"]] if name == "all" else [name]
    for n in names:
        Hatchling.attach(n).release()
    return names
