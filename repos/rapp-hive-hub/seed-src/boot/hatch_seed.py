#!/usr/bin/env python3
"""hatch_seed.py — hatch a Hive Hub seed boot Egg into this machine's standard RAPP Brainstem.

    python3 hatch_seed.py --egg <slug>.boot.egg [--port 7071] [--owner-label owner] [--install-soul]
    python3 hatch_seed.py --egg <slug>.boot.egg [same options] --apply <plan_digest>

A boot Egg is a RAPP/1 organism Egg (payload kind rapp-seed-boot/1): one organization seed's exact record, a soul
written from it, and the generic SeedRunner organ. The first run only plans: it verifies the Egg and prints every
effect, how to reverse it, and a plan_digest; nothing in the Brainstem changes. Repeating the command with
--apply <that exact digest> recomputes the plan and, only if it is identical, hatches:

1. clones RAPP/1 at the pinned commit and checks its reference implementation's exact SHA-256;
2. verifies the Egg with that reference (organism variant, rapp-seed-boot/1 payload, every file commitment);
3. creates ~/.brainstem/twin/: the seed record, twin.json with a freshly minted instance RAPPID and grown_from set to
   the Egg's address, a RAPP/1 birth frame, and the RAPP Work SDK checkout at the seed's pinned commit;
4. imports SeedRunner through the Brainstem's own POST /agents/import, which rejects bytes that miss its SHA-256.

Nothing is activated. Ask your Brainstem to run the seed: SeedRunner verifies it, plans it, and shows you an
activation digest, and nothing is created until you approve that exact digest. --install-soul also makes the seed's
soul the Brainstem's soul (the previous soul.md is kept beside it). One seed per Brainstem home.

Standard library only. Needs git, HTTPS access to github.com for the two pinned checkouts, and a running Brainstem
(curl -fsSL https://kody-w.github.io/rapp-installer/install.sh | bash).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

RAPP1 = {"repository": "https://github.com/kody-w/rapp-1.git", "commit": "591e014ad39e223b00ab343ae26e5d9a867ebeee",
         "reference_sha256": "1a04362b02f14c1e37b70c6b4f72d79e92df1cc9c2b5b394e8e1b141fc0b6050"}
PAYLOAD_KIND = "rapp-seed-boot/1"


class HatchRefused(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HatchRefused(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_ms() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def clone_pinned(repository: str, commit: str, target: Path) -> None:
    require(not target.exists(), f"{target} already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    quiet = {"stdout": subprocess.DEVNULL, "stderr": subprocess.PIPE, "check": True}
    subprocess.run(["git", "clone", "--quiet", "--no-checkout", repository, str(target)], **quiet)
    subprocess.run(["git", "-C", str(target), "checkout", "--quiet", "--detach", commit], **quiet)
    head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
    require(head == commit, f"{target}: expected {commit}, got {head}")


def load_rapp(checkout: Path):
    """Import RAPP/1's reference implementation only after checking its exact pinned bytes."""
    path = checkout / "rapp.py"
    require(sha256(path.read_bytes()) == RAPP1["reference_sha256"], f"{path} is not the pinned RAPP/1 reference implementation")
    spec = importlib.util.spec_from_file_location("rapp1_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hatch_root(egg: bytes, root: Path, rapp, rapp1_checkout: Path, *, owner_label: str, clone=clone_pinned) -> dict:
    """Verify a boot Egg and grow its twin root. rapp1_checkout (the verified RAPP/1 clone) is moved into the root."""
    ok, step, why = rapp.verify_egg(egg)
    require(ok, f"the egg fails RAPP/1 verification at step {step}: {why}")
    manifest, files = rapp.read_egg(egg)
    require(manifest["variant"] == "organism" and manifest["payload"].get("kind") == PAYLOAD_KIND, "not a seed boot egg")
    deps = manifest["payload"]["deps"]
    require(deps["protocol"]["commit"] == RAPP1["commit"] and deps["protocol"]["reference_sha256"] == RAPP1["reference_sha256"],
            "the egg pins a different RAPP/1 than this hatcher")
    organs = manifest["payload"]["brainstem"]["organs"]
    for organ in organs:
        require(sha256(files[organ["path"]]) == organ["sha256"], f"{organ['path']} does not match its declared SHA-256")
    require(not root.exists(), f"{root} already exists: this Brainstem already hatched a seed")
    address = rapp.egg_address(manifest)
    profile = json.loads(files["twin/profile.json"])
    root.mkdir(parents=True)
    for path, data in files.items():
        if path.startswith("seed/"):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_bytes(data)
    (root / "egg").mkdir()
    (root / "egg" / f"{address}.egg").write_bytes(egg)
    hatched = utc_ms()
    twin = {**{k: v for k, v in profile.items() if k != "schema"}, "schema": "rapp-twin/1", "owner_label": owner_label,
            "instance_rappid": rapp.mint_rappid(owner_label, profile["slug"]), "artifact_rappid": manifest["rappid"],
            "grown_from": address, "hatched_utc": hatched}
    (root / "twin.json").write_text(json.dumps(twin, indent=1) + "\n", encoding="utf-8")
    birth = rapp.build_frame("twin.birth", twin["instance_rappid"], 0, hatched, {"grown_from": address, "seed": profile["slug"]}, prev=None)
    (root / "state").mkdir()
    (root / "state" / "frames.jsonl").write_text(rapp.canonical(birth) + "\n", encoding="utf-8")
    shutil.move(str(rapp1_checkout), str(root / "deps" / "rapp-1"))
    clone(deps["sdk"]["repository"], deps["sdk"]["commit"], root / "deps" / "rapp-work")
    return {"twin": twin, "manifest": manifest, "files": files, "address": address}


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def plan(egg: bytes, rapp, *, home: Path, port: int, owner_label: str, install_soul: bool) -> dict:
    ok, step, why = rapp.verify_egg(egg)
    require(ok, f"the egg fails RAPP/1 verification at step {step}: {why}")
    manifest, files = rapp.read_egg(egg)
    require(manifest["variant"] == "organism" and manifest["payload"].get("kind") == PAYLOAD_KIND, "not a seed boot egg")
    root, brainstem = home / "twin", home / "src" / "rapp_brainstem"
    require(not root.exists(), f"{root} already exists: this Brainstem already hatched a seed")
    profile = json.loads(files["twin/profile.json"])
    deps = manifest["payload"]["deps"]
    organs = [{"name": Path(o["path"]).name, "sha256": o["sha256"]} for o in manifest["payload"]["brainstem"]["organs"]]
    for organ in organs:
        require(not (brainstem / "agents" / organ["name"]).exists(), f"agents/{organ['name']} already exists in this Brainstem")
    effects = [f"create {root} (seed record, twin.json, RAPP/1 birth frame, this egg)",
               f"clone {RAPP1['repository']} at {RAPP1['commit']} into {root / 'deps' / 'rapp-1'}",
               f"clone {deps['sdk']['repository']} at {deps['sdk']['commit']} into {root / 'deps' / 'rapp-work'}",
               *[f"import agents/{o['name']} (sha256 {o['sha256']}) through POST http://127.0.0.1:{port}/agents/import" for o in organs]]
    reverse = [f"delete {root}", *[f"delete {brainstem / 'agents' / o['name']}" for o in organs]]
    if install_soul:
        kept = brainstem / f"soul.md.before-{profile['slug']}"
        effects.append(f"replace {brainstem / 'soul.md'} with the seed's soul (sha256 {sha256(files['soul.md'])}), keeping the old one as {kept.name}")
        reverse.append(f"restore {kept} as soul.md")
    return {"schema": "hive-hub-seed-hatch-plan/1", "seed": profile["slug"], "egg_sha256": sha256(egg), "egg_address": rapp.egg_address(manifest),
            "artifact_rappid": manifest["rappid"], "owner_label": owner_label, "port": port, "twin_root": str(root),
            "organs": organs, "effects": effects, "reverse": reverse, "grants_authority": False,
            "activation": "none: SeedRunner shows an activation digest later, and nothing is created until the owner approves it"}


def import_organ(port: int, name: str, data: bytes, digest: str) -> int:
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"sha256\"\r\n\r\n{digest}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            "Content-Type: text/x-python\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(f"http://127.0.0.1:{port}/agents/import", data=body, method="POST",
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.status


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--egg", required=True, type=Path)
    parser.add_argument("--port", type=int, default=7071)
    parser.add_argument("--owner-label", default="owner")
    parser.add_argument("--install-soul", action="store_true")
    parser.add_argument("--apply", metavar="PLAN_DIGEST", help="hatch only if the recomputed plan has exactly this digest")
    args = parser.parse_args(argv)
    home = Path.home() / ".brainstem"
    brainstem = home / "src" / "rapp_brainstem"
    staging = home / ".hatch-rapp-1"
    try:
        require((brainstem / "brainstem.py").is_file(), f"no standard Brainstem under {home} (install it first)")
        with urllib.request.urlopen(f"http://127.0.0.1:{args.port}/health", timeout=10) as response:
            require(response.status == 200, f"no Brainstem answering on port {args.port}")
        if staging.exists():
            shutil.rmtree(staging)
        clone_pinned(RAPP1["repository"], RAPP1["commit"], staging)
        egg = args.egg.read_bytes()
        rapp = load_rapp(staging)
        proposal = plan(egg, rapp, home=home, port=args.port, owner_label=args.owner_label, install_soul=args.install_soul)
        digest = sha256(canonical(proposal))
        if args.apply is None:
            shutil.rmtree(staging)
            print(json.dumps({"status": "planned", "plan": proposal, "plan_digest": digest,
                              "next": "review every effect; to hatch, repeat this exact command with --apply " + digest}, indent=1))
            return 0
        require(args.apply == digest, "the plan changed or the digest is not this plan's exact digest; nothing was changed")
        hatched = hatch_root(egg, home / "twin", rapp, staging, owner_label=args.owner_label)
        if args.install_soul:
            soul = brainstem / "soul.md"
            if soul.is_file():
                shutil.copyfile(soul, brainstem / f"soul.md.before-{hatched['twin']['slug']}")
            soul.write_bytes(hatched["files"]["soul.md"])
        imported = [{"organ": Path(o["path"]).name, "status": import_organ(args.port, Path(o["path"]).name, hatched["files"][o["path"]], o["sha256"])}
                    for o in hatched["manifest"]["payload"]["brainstem"]["organs"]]
    except (HatchRefused, OSError, subprocess.CalledProcessError, KeyError, ValueError) as error:
        if staging.exists() and not (home / "twin").exists():
            shutil.rmtree(staging, ignore_errors=True)
        print(json.dumps({"status": "refused", "reason": str(error)}))
        return 1
    twin = hatched["twin"]
    print(json.dumps({"status": "hatched", "plan_digest": digest, "seed": twin["slug"], "instance_rappid": twin["instance_rappid"],
                      "grown_from": hatched["address"], "twin_root": str(home / "twin"), "imported": imported,
                      "soul_installed": args.install_soul, "reverse": proposal["reverse"],
                      "next": "ask your Brainstem to run the seed; approve only the exact activation digest SeedRunner shows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
