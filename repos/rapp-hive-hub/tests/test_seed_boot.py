"""Every catalog organization seed ships a Brainstem boot Egg that is bound to the exact published seed."""

from __future__ import annotations

import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.organization_seeds import SEED_SLUGS  # noqa: E402

BOOT = ROOT / "seed-src" / "boot"
DEPS = ROOT / ".hive-hub" / "deps"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def egg_hash(data: bytes) -> str:
    """RAPP/1's domain-separated Egg content hash, Hb("rapp/1:egg", octets)."""
    return hashlib.sha256(b"rapp/1:egg\n" + data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_bytes())


class SeedBootTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pins = load(BOOT / "BOOT_PINS.json")
        cls.sdk_pin = load(ROOT / "seed-src" / "SDK_PIN.json")
        cls.organ = (BOOT / "rapp_seed_runner_agent.py").read_bytes()
        cls.hatcher = (BOOT / "hatch_seed.py").read_bytes()
        cls.manifest = load(ROOT / "public-manifest.json")

    def boot(self, slug: str) -> tuple[dict, dict, dict[str, bytes]]:
        doc = load(ROOT / "public-src" / "organization-seed-boots" / f"{slug}.json")
        egg = base64.b64decode(doc["egg"]["base64"], validate=True)
        self.assertEqual(len(egg), doc["egg"]["bytes"])
        self.assertEqual(sha(egg), doc["egg"]["sha256"])
        with zipfile.ZipFile(io.BytesIO(egg)) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        return doc, json.loads(files.pop("manifest.json")), files

    def test_every_catalog_seed_has_one_mint_once_boot_identity(self) -> None:
        self.assertEqual(self.pins["schema"], "hive-hub-seed-boot-pins/1")
        self.assertEqual(set(self.pins["seeds"]), set(SEED_SLUGS))
        for slug, pin in self.pins["seeds"].items():
            self.assertRegex(pin["rappid"], r"^rappid:@hive-hub/[a-z0-9-]+:[0-9a-f]{64}$")
            self.assertEqual(pin["rappid"].split("/", 1)[1].split(":", 1)[0], f"{slug}-boot")
            self.assertRegex(pin["utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
        rappids = [pin["rappid"] for pin in self.pins["seeds"].values()]
        self.assertEqual(len(set(rappids)), len(rappids))

    def test_boot_eggs_carry_the_exact_published_seed_and_organ(self) -> None:
        for slug in SEED_SLUGS:
            with self.subTest(seed=slug):
                doc, manifest, files = self.boot(slug)
                self.assertEqual((doc["kind"], doc["schema"], doc["status"], doc["classification"]),
                                 ("organization-seed-boot", "hive-hub-organization-seed-boot/1", "boot-not-hatched", "public-synthetic"))
                self.assertIs(doc["hatch"]["grantsAuthority"], False)
                self.assertEqual((manifest["variant"], manifest["schema"]), ("organism", "rapp/1-egg"))
                self.assertEqual(manifest["rappid"], self.pins["seeds"][slug]["rappid"])
                self.assertEqual(manifest["created_utc"], self.pins["seeds"][slug]["utc"])
                self.assertEqual({entry["path"]: entry["hash"] for entry in manifest["contents"]},
                                 {path: egg_hash(data) for path, data in files.items()})
                published = (ROOT / "public-src" / "organization-seeds" / f"{slug}.json").read_bytes()
                self.assertEqual(files["seed/record.json"], published)
                self.assertEqual(doc["seed"]["recordSha256"], sha(published))
                self.assertEqual(doc["seed"]["archiveSha256"], json.loads(published)["archive"]["sha256"])
                self.assertEqual(files["agents/rapp_seed_runner_agent.py"], self.organ)
                payload = manifest["payload"]
                self.assertEqual(payload["kind"], "rapp-seed-boot/1")
                self.assertEqual(payload["brainstem"]["organs"], [{"path": "agents/rapp_seed_runner_agent.py", "sha256": sha(self.organ)}])
                self.assertEqual(payload["deps"], {"sdk": self.sdk_pin["sdk"], "protocol": self.sdk_pin["protocol"]})
                self.assertEqual(json.loads(files["rappid.json"])["rappid"], manifest["rappid"])
                self.assertEqual(json.loads(files["twin/profile.json"])["slug"], slug)
                self.assertEqual(doc["brainstem"]["hatcher"], {"path": "hub/boot/hatch_seed.py", "sha256": sha(self.hatcher)})

    def test_the_published_hatcher_is_the_source_and_pins_the_seed_protocol(self) -> None:
        doc = load(ROOT / "public-src" / "boot" / "hatch-seed.json")
        self.assertEqual(doc["content"].encode("utf-8"), self.hatcher)
        self.assertEqual((doc["bytes"], doc["sha256"]), (len(self.hatcher), sha(self.hatcher)))
        text = self.hatcher.decode("utf-8")
        protocol = self.sdk_pin["protocol"]
        self.assertIn(f'"commit": "{protocol["commit"]}"', text)
        self.assertIn(f'"reference_sha256": "{protocol["reference_sha256"]}"', text)
        self.assertIn("--apply", text)
        self.assertNotRegex(text, r"(?i)token|password|secret")

    def test_public_manifest_declares_every_boot(self) -> None:
        entries = {entry["id"]: entry for entry in self.manifest["entries"]}
        for slug in SEED_SLUGS:
            entry = entries[f"organization-seed-boot-{slug}"]
            self.assertEqual((entry["kind"], entry["path"]), ("organization-seed-boot", f"organization-seed-boots/{slug}.json"))
            self.assertEqual(entry["sha256"], sha((ROOT / "public-src" / entry["path"]).read_bytes()))
        self.assertEqual(entries["seed-boot-hatcher"]["path"], "boot/hatch-seed.json")

    def test_generated_seed_pages_offer_the_boot(self) -> None:
        index = load(ROOT / "api" / "hive-hub" / "v1" / "organization-seeds.json")
        self.assertEqual({seed["slug"] for seed in index["seeds"]}, set(SEED_SLUGS))
        for seed in index["seeds"]:
            with self.subTest(seed=seed["slug"]):
                egg = (ROOT / seed["boot"]["egg"]["path"]).read_bytes()
                self.assertEqual(sha(egg), seed["boot"]["egg"]["sha256"])
                page = (ROOT / "hub" / "seeds" / seed["slug"] / "index.html").read_text(encoding="utf-8")
                self.assertIn("Or boot it in a RAPP Brainstem.", page)
                self.assertIn(seed["boot"]["egg"]["sha256"], page)
                self.assertIn(f"hatch_seed.py --egg {seed['slug']}.boot.egg --apply", page)
        self.assertEqual(sha((ROOT / "hub" / "boot" / "hatch_seed.py").read_bytes()), sha(self.hatcher))

    @unittest.skipUnless((DEPS / "rapp-1" / "rapp.py").is_file(), "needs the pinned RAPP/1 checkout at .hive-hub/deps/rapp-1")
    def test_boot_documents_rebuild_byte_for_byte(self) -> None:
        done = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "seed_boot.py"), "build", "--check"],
                              capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])


class _StubBrainstem(BaseHTTPRequestHandler):
    agents: Path

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        self.send_response(200 if self.path == "/health" else 404)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        boundary = self.headers["Content-Type"].split("boundary=", 1)[1].encode()
        parts = {}
        for part in body.split(b"--" + boundary)[1:-1]:
            head, _, data = part.partition(b"\r\n\r\n")
            name = head.split(b'name="', 1)[1].split(b'"', 1)[0].decode()
            filename = head.split(b'filename="', 1)[1].split(b'"', 1)[0].decode() if b"filename=" in head else None
            parts[name] = (filename, data[:-2])
        filename, data = parts["file"]
        ok = self.path == "/agents/import" and hashlib.sha256(data).hexdigest() == parts["sha256"][1].decode()
        if ok:
            (self.agents / filename).write_bytes(data)
        self.send_response(200 if ok else 400)
        self.end_headers()
        self.wfile.write(b"{}")


@unittest.skipUnless((DEPS / "rapp-1" / "rapp.py").is_file() and (DEPS / "rapp-work" / ".git").exists(),
                     "needs the pinned RAPP/1 and RAPP Work SDK checkouts under .hive-hub/deps")
class HatcherTest(unittest.TestCase):
    def test_hatcher_plans_then_applies_only_the_exact_digest(self) -> None:
        spec = importlib.util.spec_from_file_location("hatch_seed_under_test", BOOT / "hatch_seed.py")
        hatcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hatcher)
        real_clone = hatcher.clone_pinned
        local = {"kody-w/rapp-1": DEPS / "rapp-1", "kody-w/rapp-work": DEPS / "rapp-work"}
        hatcher.clone_pinned = lambda repository, commit, target: real_clone(
            str(local[repository.removeprefix("https://github.com/").removesuffix(".git")]), commit, target)
        slug = "turnaround-firm"
        doc = load(ROOT / "public-src" / "organization-seed-boots" / f"{slug}.json")
        with tempfile.TemporaryDirectory(dir=ROOT / ".hive-hub") as scratch:
            home = Path(scratch)
            agents = home / ".brainstem" / "src" / "rapp_brainstem" / "agents"
            agents.mkdir(parents=True)
            (agents.parent / "brainstem.py").write_text("# stub\n")
            egg = home / f"{slug}.boot.egg"
            egg.write_bytes(base64.b64decode(doc["egg"]["base64"]))
            handler = type("Stub", (_StubBrainstem,), {"agents": agents})
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            previous = os.environ.get("HOME")
            os.environ["HOME"] = str(home)
            try:
                def run(*extra: str) -> tuple[int, dict]:
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        code = hatcher.main(["--egg", str(egg), "--port", str(server.server_port), *extra])
                    return code, json.loads(out.getvalue())
                code, planned = run()
                self.assertEqual((code, planned["status"]), (0, "planned"))
                self.assertFalse((home / ".brainstem" / "twin").exists())
                self.assertFalse(planned["plan"]["grants_authority"])
                code, refused = run("--apply", "0" * 64)
                self.assertEqual((code, refused["status"]), (1, "refused"))
                self.assertFalse((home / ".brainstem" / "twin").exists())
                code, hatched = run("--apply", planned["plan_digest"])
                self.assertEqual((code, hatched["status"]), (0, "hatched"), hatched)
                twin = json.loads((home / ".brainstem" / "twin" / "twin.json").read_text())
                self.assertEqual(twin["grown_from"], doc["egg"]["address"])
                self.assertEqual((agents / "rapp_seed_runner_agent.py").read_bytes(), (BOOT / "rapp_seed_runner_agent.py").read_bytes())
                code, again = run()
                self.assertEqual((code, again["status"]), (1, "refused"))
            finally:
                server.shutdown()
                if previous is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = previous


if __name__ == "__main__":
    unittest.main()
