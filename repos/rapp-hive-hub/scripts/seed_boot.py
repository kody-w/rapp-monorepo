#!/usr/bin/env python3
"""Give every catalog organization seed a Brainstem boot: pinned identities, deterministic boot Eggs, and proof.

    python3 scripts/seed_boot.py pin    [--rapp1-path P]        mint a boot identity once for each seed lacking one
    python3 scripts/seed_boot.py build  [--rapp1-path P] [--check]
                                                                write (or verify) public-src/organization-seed-boots/
    python3 scripts/seed_boot.py prove  [--rapp1-path P] [--sdk-path P] [--scratch DIR] [--slug S ...]
                                                                hatch every boot Egg into a scratch root and run it

A boot Egg is a RAPP/1 organism Egg (payload kind rapp-seed-boot/1) packed by RAPP/1's pinned reference: the seed's
exact record, a soul written from it, and the generic SeedRunner organ (seed-src/boot/rapp_seed_runner_agent.py).
Its artifact RAPPID and packing time are minted once (seed-src/boot/BOOT_PINS.json), so every build packs
byte-identical Eggs. People hatch one with seed-src/boot/hatch_seed.py (published at hub/boot/hatch_seed.py);
`prove` runs that same hatcher into scratch roots, loads SeedRunner from each Egg's own bytes, and walks the seed
flow: verify_seed, plan, a refused wrong digest, activate with the plan's exact digest, tasks. Nothing here grants
authority, activates a seed, or touches the network (prove clones the local pinned checkouts).
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.file_integrity import read_regular_bytes  # noqa: E402
from scripts.organization_seeds import SEED_SLUGS, build_seed, json_bytes, require, sha  # noqa: E402

BOOT = ROOT / "seed-src" / "boot"
PINS = BOOT / "BOOT_PINS.json"
ORGAN = "rapp_seed_runner_agent.py"
OUT = ROOT / "public-src" / "organization-seed-boots"
HATCHER_DOC = ROOT / "public-src" / "boot" / "hatch-seed.json"
PUBLISHER = "hive-hub"
INSTALLER = "curl -fsSL https://kody-w.github.io/rapp-installer/install.sh | bash"
MAX_BYTES = 1_048_576


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HATCHER = load_module(BOOT / "hatch_seed.py", "hive_hub_hatch_seed")


def rapp_reference(rapp1_path: Path):
    pin = json.loads(read_regular_bytes(ROOT / "seed-src" / "SDK_PIN.json"))["protocol"]
    require(HATCHER.RAPP1["commit"] == pin["commit"] and HATCHER.RAPP1["reference_sha256"] == pin["reference_sha256"],
            "hatch_seed.py pins a different RAPP/1 than seed-src/SDK_PIN.json")
    return HATCHER.load_rapp(rapp1_path)


def soul(record: dict) -> str:
    return (f"# {record['name']}\n\nYou are {record['name']}, a RAPP Brainstem hatched from the Hive Hub organization seed "
            f"`{record['slug']}`. {record['tagline']}\n\nMission: {record['mission']}\n\n## How you work\n\n"
            "- SeedRunner runs your seed: `status` first, then `verify_seed`, `plan`, and `activate` with the owner's exact\n"
            "  activation digest. Then work the case board: `tasks`, `claim` a ready task, do it, `deliver` each output, `complete`.\n\n"
            "## Never\n\n- Never call `activate` unless the owner's latest message contains that exact digest. Show digests; do not invent them.\n"
            "- Never read or write outside your own root, and never push, publish or deploy.\n")


def read_pins() -> dict:
    if not PINS.exists():
        return {"schema": "hive-hub-seed-boot-pins/1", "publisher": PUBLISHER, "seeds": {}}
    pins = json.loads(read_regular_bytes(PINS))
    require(pins.get("schema") == "hive-hub-seed-boot-pins/1" and pins.get("publisher") == PUBLISHER, "invalid BOOT_PINS.json")
    return pins


def pack(slug: str, pin: dict, rapp) -> tuple[bytes, dict, bytes]:
    record = build_seed(slug, ROOT)
    record_bytes = json_bytes(record)
    require(read_regular_bytes(ROOT / "public-src" / "organization-seeds" / f"{slug}.json") == record_bytes,
            f"public-src/organization-seeds/{slug}.json is stale; run scripts/organization_seeds.py first")
    organ = read_regular_bytes(BOOT / ORGAN)
    profile = {"schema": "rapp-twin-profile/1", "name": record["name"], "slug": slug, "owner_label": "owner",
               "seed_archive_sha256": record["archive"]["sha256"]}
    files = {"seed/record.json": record_bytes, "soul.md": soul(record).encode(), f"agents/{ORGAN}": organ,
             "twin/profile.json": json_bytes(profile),
             "rappid.json": json_bytes({"schema": "rapp/1", "rappid": pin["rappid"], "kind": "seed-boot-organism", "name": record["name"]})}
    payload = {"kind": HATCHER.PAYLOAD_KIND,
               "seed": {"slug": slug, "name": record["name"], "world_id": record["organization"]["scaffold"]["world_id"],
                        "archive_sha256": record["archive"]["sha256"], "record": "seed/record.json"},
               "brainstem": {"installer": INSTALLER, "min_version": "0.6.16", "soul": "soul.md",
                             "organs": [{"path": f"agents/{ORGAN}", "sha256": sha(organ)}]},
               "deps": {"sdk": record["dependencies"]["sdk"], "protocol": record["dependencies"]["protocol"]},
               "hatch": "verify this egg; mint a fresh instance rappid; record grown_from; import each organ via POST /agents/import with its sha256"}
    egg = rapp.pack_egg("organism", pin["rappid"], pin["utc"], files=files, payload=payload)
    ok, step, why = rapp.verify_egg(egg)
    require(ok, f"{slug}: packed egg fails RAPP/1 verification at step {step}: {why}")
    return egg, record, organ


def document(slug: str, pin: dict, rapp) -> dict:
    egg, record, organ = pack(slug, pin, rapp)
    manifest, _ = rapp.read_egg(egg)
    return {"kind": "organization-seed-boot", "schema": "hive-hub-organization-seed-boot/1", "classification": "public-synthetic",
            "status": "boot-not-hatched", "slug": slug, "name": record["name"],
            "seed": {"archiveSha256": record["archive"]["sha256"], "recordSha256": sha(json_bytes(record))},
            "egg": {"variant": "organism", "payloadKind": HATCHER.PAYLOAD_KIND, "rappid": pin["rappid"], "utc": pin["utc"],
                    "address": rapp.egg_address(manifest), "bytes": len(egg), "sha256": sha(egg),
                    "base64": base64.b64encode(egg).decode("ascii")},
            "organ": {"name": "SeedRunner", "path": f"agents/{ORGAN}", "sha256": sha(organ)},
            "brainstem": {"installer": INSTALLER, "minVersion": "0.6.16",
                          "hatcher": {"path": "hub/boot/hatch_seed.py", "sha256": sha(read_regular_bytes(BOOT / "hatch_seed.py"))}},
            "hatch": {"grantsAuthority": False, "effects": [
                "Creates ~/.brainstem/twin with this seed record, a fresh instance RAPPID and a RAPP/1 birth frame",
                "Clones RAPP/1 and the RAPP Work SDK at the seed's pinned commits",
                "Imports SeedRunner through the Brainstem's POST /agents/import with its SHA-256",
                "Activates nothing: the owner approves SeedRunner's exact activation digest first"]}}


def cmd_pin(args) -> dict:
    rapp = rapp_reference(args.rapp1_path)
    pins = read_pins()
    minted = []
    for slug in SEED_SLUGS:
        if slug not in pins["seeds"]:
            pins["seeds"][slug] = {"rappid": rapp.mint_rappid(PUBLISHER, f"{slug}-boot"), "utc": HATCHER.utc_ms()}
            minted.append(slug)
    require(set(pins["seeds"]) == set(SEED_SLUGS), "BOOT_PINS.json names a seed that is not in the catalog")
    pins["seeds"] = dict(sorted(pins["seeds"].items()))
    PINS.write_bytes(json_bytes(pins))
    return {"pinned": len(pins["seeds"]), "minted": minted}


def hatcher_document() -> dict:
    data = read_regular_bytes(BOOT / "hatch_seed.py")
    return {"kind": "boot-hatcher-document", "name": "hatch_seed.py", "mediaType": "text/x-python",
            "bytes": len(data), "sha256": sha(data), "content": data.decode("utf-8")}


def cmd_build(args) -> dict:
    rapp = rapp_reference(args.rapp1_path)
    pins = read_pins()
    require(set(pins["seeds"]) == set(SEED_SLUGS), "every catalog seed needs a boot pin (run: seed_boot.py pin)")
    outputs = [(HATCHER_DOC, json_bytes(hatcher_document()))]
    outputs += [(OUT / f"{slug}.json", json_bytes(document(slug, pins["seeds"][slug], rapp))) for slug in SEED_SLUGS]
    for target, encoded in outputs:
        require(len(encoded) <= MAX_BYTES, f"{target.name}: boot document exceeds the bounded JSON transport size")
        if args.check:
            require(target.exists() and read_regular_bytes(target) == encoded, f"stale seed boot document: {target.name}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                read_regular_bytes(target)
            target.write_bytes(encoded)
    return {"boots": len(SEED_SLUGS), "mode": "checked" if args.check else "built"}


def load_organ(data: bytes, slug: str):
    name = f"hive_hub_seed_runner_{slug.replace('-', '_')}"
    module = types.ModuleType(name)
    module.__file__ = ORGAN
    sys.modules[name] = module
    exec(compile(data, ORGAN, "exec"), module.__dict__)
    return module.SeedRunnerAgent()


def prove_one(slug: str, egg: bytes, scratch: Path, rapp1_path: Path, sdk_path: Path) -> dict:
    rapp = rapp_reference(rapp1_path)
    root = scratch / slug / "twin"
    staging = scratch / slug / "rapp-1"
    HATCHER.clone_pinned(str(rapp1_path), HATCHER.RAPP1["commit"], staging)
    local = {HATCHER.RAPP1["repository"].removesuffix(".git"): rapp1_path}

    def clone_local(repository: str, commit: str, target: Path) -> None:
        source = local.get(repository.removesuffix(".git"), sdk_path)
        HATCHER.clone_pinned(str(source), commit, target)

    hatched = HATCHER.hatch_root(egg, root, HATCHER.load_rapp(staging), staging, owner_label="seed-conformance", clone=clone_local)
    organ = hatched["manifest"]["payload"]["brainstem"]["organs"][0]
    agent = load_organ(hatched["files"][organ["path"]], slug)
    previous = os.environ.get("RAPP_TWIN_ROOT")
    os.environ["RAPP_TWIN_ROOT"] = str(root)
    try:
        call = lambda **kw: json.loads(agent.perform(**kw))  # noqa: E731
        for action in ("status", "verify_seed", "plan"):
            step = call(action=action)
            require(step["ok"], f"{slug}: {action} refused: {step['summary']}")
            if action == "plan":
                digest = step["activation_digest"]
        require(not call(action="activate", approve="0" * 64)["ok"], f"{slug}: a wrong activation digest was accepted")
        activated = call(action="activate", approve=digest)
        require(activated["ok"], f"{slug}: activate refused: {activated['summary']}")
        tasks = call(action="tasks")["tasks"]
    finally:
        if previous is None:
            os.environ.pop("RAPP_TWIN_ROOT", None)
        else:
            os.environ["RAPP_TWIN_ROOT"] = previous
    record = json.loads(hatched["files"]["seed/record.json"])
    receipt = json.loads((root / "state" / "activation.json").read_text(encoding="utf-8"))
    members = len(record["workspaces"]) + 1
    rappids = {m["rappid"] for m in receipt["members"]}
    require(receipt["pointers"] == members - 1 and len(rappids) == members, f"{slug}: membership mismatch after activation")
    require(receipt["world_id"] == record["organization"]["scaffold"]["world_id"], f"{slug}: activation left the seed's world")
    require(hatched["twin"]["grown_from"] == hatched["address"] and hatched["twin"]["instance_rappid"] not in rappids,
            f"{slug}: hatched identity is not distinct from its members")
    ready = [t["id"] for t in tasks if t["state"] == "ready"]
    require(len(tasks) == record["counts"]["tasks"] and ready, f"{slug}: the case board is not live")
    return {"seed": slug, "members": members, "pointers": receipt["pointers"], "tasks": len(tasks), "ready": len(ready),
            "egg_address": hatched["address"]}


def cmd_prove(args) -> dict:
    slugs = args.slug or list(SEED_SLUGS)
    (ROOT / ".hive-hub").mkdir(exist_ok=True)
    scratch = Path(args.scratch).resolve() if args.scratch else Path(tempfile.mkdtemp(prefix="seed-boot-prove-", dir=ROOT / ".hive-hub"))
    rows = []
    try:
        for slug in slugs:
            doc = json.loads(read_regular_bytes(OUT / f"{slug}.json"))
            egg = base64.b64decode(doc["egg"]["base64"], validate=True)
            require(sha(egg) == doc["egg"]["sha256"] and len(egg) == doc["egg"]["bytes"], f"{slug}: boot egg commitment mismatch")
            rows.append(prove_one(slug, egg, scratch, args.rapp1_path, args.sdk_path))
            print(f"PASS {slug}: {rows[-1]['members']} native identities, {rows[-1]['pointers']} pointers, "
                  f"{rows[-1]['tasks']} tasks ({rows[-1]['ready']} ready)", file=sys.stderr, flush=True)
    finally:
        if not args.keep:
            shutil.rmtree(scratch, ignore_errors=True)
    return {"proved": len(rows), "seeds": rows, "activation": "scratch only"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("pin", "build", "prove"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--rapp1-path", type=Path, default=ROOT / ".hive-hub/deps/rapp-1")
        if name == "build":
            cmd.add_argument("--check", action="store_true")
        if name == "prove":
            cmd.add_argument("--sdk-path", type=Path, default=ROOT / ".hive-hub/deps/rapp-work")
            cmd.add_argument("--scratch")
            cmd.add_argument("--keep", action="store_true")
            cmd.add_argument("--slug", action="append")
    args = parser.parse_args()
    result = {"pin": cmd_pin, "build": cmd_build, "prove": cmd_prove}[args.command](args)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
