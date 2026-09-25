"""Hatchery tests. Offline: the engine is a local git repository with a tiny stand-in brainstem that speaks the
same /health and /chat as the real one. No network, no sign-in, nothing outside a temporary folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hatchery  # noqa: E402
from hatchery import Hatchling, HatcheryError, list_hatchlings, rapp1, release  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hatchery-test-"))
ENGINE = TMP / "engine-repo"

BRAINSTEM = r'''import glob, json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))

def text(name):
    path = os.path.join(HERE, name)
    return open(path).read().strip() if os.path.exists(path) else ""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/health":
            return self.send({"error": "not found"}, 404)
        agents = sorted(os.path.basename(p)[:-len("_agent.py")]
                        for p in glob.glob(os.path.join(HERE, "agents", "**", "*_agent.py"), recursive=True))
        self.send({"status": "ok", "copilot": "\u2713", "model": "stand-in", "agents": agents,
                   "soul": text("soul.md"), "version": text("VERSION"),
                   "token": bool(os.environ.get("GITHUB_TOKEN"))})

    def do_POST(self):
        size = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(size) or b"{}")
        if self.path != "/chat":
            return self.send({"error": "not found"}, 404)
        self.send({"response": "echo: " + body.get("user_input", ""), "session_id": body.get("session_id") or "s-1",
                   "agent_logs": "[Hello] ran", "model": "stand-in",
                   "history_sent": len(body.get("conversation_history", []))})

HTTPServer(("127.0.0.1", int(os.environ["PORT"])), Handler).serve_forever()
'''


def git(*args, cwd=ENGINE):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def make_engine():
    b = ENGINE / "rapp_brainstem"
    (b / "agents" / "experimental").mkdir(parents=True)
    (b / "brainstem.py").write_text(BRAINSTEM)
    (b / "requirements.txt").write_text("")
    (b / "soul.md").write_text("You are the engine's default soul.")
    (b / "agents" / "basic_agent.py").write_text("class BasicAgent:\n    pass\n")
    (b / "agents" / "hello_agent.py").write_text("# the engine's own agent\n")
    (b / "agents" / "experimental" / "lab_agent.py").write_text("# an experimental engine agent\n")
    (b / "VERSION").write_text("1")
    git("init", "-q", "-b", "main")
    git("-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
    git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "engine v1")
    first = git("rev-parse", "HEAD")
    (b / "VERSION").write_text("2")
    git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-am", "engine v2")
    return first, git("rev-parse", "HEAD")


def make_egg(path, soul=b"You are Desk.", agent=b"# the egg's agent\n"):
    rappid = rapp1.mint_rappid("tester", "desk")
    files = {"rappid.json": rapp1.canonical({"schema": "rapp/1", "rappid": rappid}).encode("utf-8"),
             "soul.md": soul, "agents/desk_agent.py": agent}
    payload = {"engine": {"name": "rapp-brainstem", "version": "", "source": "other", "commit": ""},
               "memory_included": False, "settings_needed": [], "made_with": "hatchery-tests"}
    blob = rapp1.pack_egg("organism", rappid, "2026-09-24T12:00:00.000Z", files=files, payload=payload)
    assert rapp1.verify_egg(blob)[0]
    path.write_bytes(blob)
    return rappid


class HatcheryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v1, cls.v2 = make_engine()
        hatchery.ROOT = TMP / "hatchlings"
        hatchery.CACHE = TMP / "cache"
        hatchery.INSTALLED = TMP / "no-installed-brainstem"
        os.environ["HATCHERY_PYTHON"] = sys.executable
        os.environ["GITHUB_TOKEN"] = "test-token"

    def tearDown(self):
        release("all", include_kept=True)

    def test_hatch_chat_release(self):
        bs = Hatchling(name="basic", source=str(ENGINE), sign_in=False).hatch()
        h = bs.health()
        self.assertEqual((h["version"], h["model"], h["token"]), ("2", "stand-in", True))
        self.assertEqual(h["agents"], ["basic", "hello", "lab"])
        self.assertEqual(bs.commit, self.v2)
        r = bs.chat("hello")
        self.assertEqual((r.response, r.session_id, r.agents_called), ("echo: hello", "s-1", ["Hello"]))
        self.assertEqual(bs.chat("again").raw["history_sent"], 2)
        rows = list_hatchlings()
        self.assertEqual([(x["name"], x["running"], x["kept"]) for x in rows], [("basic", True, False)])
        pid, folder = bs.pid, bs.dir
        bs.release()
        self.assertFalse(folder.exists())
        self.assertFalse(hatchery._alive(pid))

    def test_the_engine_is_pinned_and_can_never_be_pushed_to(self):
        with Hatchling(name="pinned", source=str(ENGINE), ref=self.v1[:10], sign_in=False) as bs:
            self.assertEqual(bs.health()["version"], "1")
            self.assertEqual(bs.commit, self.v1)
            engine = bs.dir / "engine"
            self.assertEqual(git("remote", "get-url", "--push", "origin", cwd=engine), hatchery.PUSH_BLOCK)
            self.assertEqual(git("remote", "get-url", "origin", cwd=engine), str(ENGINE.resolve()))
            (bs.brainstem_dir / "agents" / "scratch_agent.py").write_text("# local only\n")
        self.assertEqual(git("rev-parse", "HEAD"), self.v2)
        self.assertEqual(git("status", "--porcelain"), "")

    def test_an_egg_hatches_bare_with_its_own_instance_identity(self):
        egg = TMP / "tester--desk.egg"
        artifact = make_egg(egg)
        with Hatchling(name="from-egg", egg=egg, source=str(ENGINE), sign_in=False) as bs:
            h = bs.health()
            self.assertEqual(h["agents"], ["basic", "desk"])
            self.assertEqual(h["soul"], "You are Desk.")
            self.assertTrue((bs.dir / "parked-agents" / "experimental" / "lab_agent.py").is_file())
            instance = json.loads((bs.dir / "instance.json").read_text())
            self.assertEqual(instance["artifact"], artifact)
            self.assertNotEqual(instance["rappid"], artifact)
            self.assertTrue(instance["grown_from"])

    def test_a_tampered_egg_is_refused(self):
        egg = TMP / "bad.egg"
        make_egg(egg)
        blob = bytearray(egg.read_bytes())
        blob[len(blob) // 2] ^= 0xFF
        egg.write_bytes(bytes(blob))
        with self.assertRaises(HatcheryError):
            Hatchling(egg=egg, source=str(ENGINE))

    def test_stop_start_and_a_soul_and_agents_laid_in(self):
        soul = TMP / "soul.md"
        soul.write_text("You are Scout.")
        agent = TMP / "scout_agent.py"
        agent.write_text("# scout\n")
        bs = Hatchling(name="scout", source=str(ENGINE), bare=True, soul=soul, agents=[agent], sign_in=False).hatch()
        self.assertEqual((bs.health()["soul"], bs.health()["agents"]), ("You are Scout.", ["basic", "scout"]))
        port = bs.port
        Hatchling.attach("scout").stop()
        self.assertEqual([x["running"] for x in list_hatchlings()], [False])
        again = Hatchling.attach("scout").start()
        self.assertEqual((again.port, again.health()["soul"]), (port, "You are Scout."))

    def test_kept_twins_survive_release_all(self):
        Hatchling(name="twin", source=str(ENGINE), keep=True, sign_in=False).hatch()
        Hatchling(name="short", source=str(ENGINE), sign_in=False).hatch()
        self.assertEqual(release("all"), ["short"])
        self.assertEqual([(x["name"], x["kept"]) for x in list_hatchlings()], [("twin", True)])

    def test_guards(self):
        with self.assertRaises(HatcheryError):
            Hatchling(name="Not Valid", source=str(ENGINE), sign_in=False).hatch()
        with self.assertRaises(HatcheryError):
            Hatchling(name="nowhere", source=str(TMP / "missing"), sign_in=False).hatch()
        self.assertFalse((hatchery.ROOT / "nowhere").exists())
        with self.assertRaises(HatcheryError):
            Hatchling(name="nosuchref", source=str(ENGINE), ref="deadbeef", sign_in=False).hatch()
        self.assertFalse((hatchery.ROOT / "nosuchref").exists())

    def test_the_cli(self):
        from hatchery.__main__ import main
        self.assertEqual(main(["hatch", "--name", "cli", "--source", str(ENGINE), "--no-sign-in"]), 0)
        self.assertEqual(main(["keep", "cli"]), 0)
        self.assertTrue(Hatchling.attach("cli").kept)
        self.assertEqual(main(["release", "cli"]), 0)
        self.assertEqual(list_hatchlings(), [])
        self.assertEqual(main(["chat", "nobody", "hi"]), 1)

    def test_the_vendored_reference_implementation_is_verbatim(self):
        import hashlib
        pkg = Path(hatchery.__file__).parent
        record = json.loads((pkg / "rapp1.vendor.json").read_text())
        self.assertEqual(hashlib.sha256((pkg / "rapp1.py").read_bytes()).hexdigest(), record["sha256"])


if __name__ == "__main__":
    unittest.main()
