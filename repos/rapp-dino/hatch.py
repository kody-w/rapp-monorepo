#!/usr/bin/env python3
"""hatch.py — birth a brand-new RAPP dino from this one repo.

A RAPP dino is not a fork. You clone this repo, run one command, and it births a
FRESH organism that is yours: its own keyless identity, its own owner sovereign,
its own tamper-evident memory — with RAPP as the factory-default apex you can
later hand to your own AI (see specs/SPEC.md, rapp-apex-dino/1.0).

    git clone <this repo> my-dino && cd my-dino
    python3 hatch.py --owner <your-github-login>

What it does, once:
  1. writes organism.json — who this dino is (owner + slug)
  2. mints a keyless rappid (rappid:@<owner>/<slug>:<64hex>) — minted once, forever
  3. seals an apex.genesis frame on a rapp/1 chain, with RAPP as the default apex
  4. proves the newborn is sound (survival probe + the two oracles)

Re-running is safe: identity is mint-once and never re-minted. Use --force only to
start a genuinely new organism (wipes local state).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
CONFIG = REPO / "organism.json"


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def infer_owner():
    for args in (["config", "user.username"], ["config", "user.name"]):
        try:
            out = subprocess.run(["git", *args], capture_output=True, text=True, timeout=3)
            if out.returncode == 0 and out.stdout.strip():
                return slugify(out.stdout)
        except (OSError, subprocess.SubprocessError):
            pass
    return ""


def main():
    ap = argparse.ArgumentParser(description="Birth a new RAPP dino from this repo.")
    ap.add_argument("--owner", help="your GitHub login (the dino's owner/sovereign)")
    ap.add_argument("--slug", default="rapp-dino", help="the organism slug (default: rapp-dino)")
    ap.add_argument("--force", action="store_true", help="wipe local state and hatch a NEW organism")
    ap.add_argument("--verify", action="store_true", help="run the oracles after hatching")
    args = ap.parse_args()

    owner = slugify(args.owner or infer_owner())
    slug = slugify(args.slug) or "rapp-dino"
    if not owner or owner == "you":
        print("✗ I need an owner. Pass --owner <your-github-login> so the dino is YOURS,\n"
              "  not a fork of anyone. (Couldn't infer it from git config.)")
        return 2

    # Already hatched? Respect mint-once unless --force.
    state = REPO / "state" / "apex"
    if (CONFIG.exists() or state.exists()) and not args.force:
        existing = {}
        try:
            existing = json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        if existing.get("rappid"):
            print(f"• This repo already hosts a hatched dino: {existing['rappid']}")
            print("  Identity is mint-once. Use --force to start a genuinely new organism.")
            return 0

    if args.force:
        import shutil
        shutil.rmtree(state.parent, ignore_errors=True)  # state/
        # external anchor for this stream is left; a fresh mint gets a new stream.

    # 1. Write who this dino is, BEFORE importing the apex package (which reads it).
    CONFIG.write_text(json.dumps({"owner": owner, "slug": slug,
                                  "default_apex": "rapp-brainstem"}, indent=2) + "\n",
                      encoding="utf-8")
    os.environ["APEX_OWNER"], os.environ["APEX_SLUG"] = owner, slug

    sys.path.insert(0, str(REPO))
    from apex import chain, survival  # noqa: E402  (imported after config exists)

    # 2 + 3. Mint the identity and seal genesis with RAPP as the default apex.
    rappid = chain.identity()
    if not chain.read_chain():
        chain.seal("genesis", {
            "note": f"a new RAPP dino awakened for @{owner}",
            "owner": owner,
            "default_apex": survival.DEFAULT_LEADER,
            "motto": "RAPP is above that",
        })

    # Record the minted identity back into organism.json.
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    cfg["rappid"] = rappid
    cfg["created_utc"] = chain.read_chain()[0]["utc"]
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    # 4. Prove the newborn is sound.
    chain_ok, chain_detail = chain.verify()
    alive, _ = survival.check_survival()

    print("🦖  A new RAPP dino has hatched.\n")
    print(f"   owner (sovereign) : @{owner}")
    print(f"   identity (rappid) : {rappid}")
    print(f"   default apex      : {survival.DEFAULT_LEADER['leader_id']} (yours to hand off later)")
    print(f"   memory (chain)    : {chain_detail}")
    print(f"   survival probe    : {'ALIVE' if alive else 'AT RISK'}")
    print("\n   RAPP is above that. This dino is yours — its identity, memory, and")
    print("   owner are independent of the hatchery. Bring your own AI to the apex")
    print("   whenever it earns the throne (specs/SPEC.md §7).")

    rc = 0 if (chain_ok and alive) else 1
    if args.verify:
        print("\n── verifying ──")
        for oracle in ("prove_immune_never_eats_self.py", "prove_organism_survives_succession.py"):
            r = subprocess.run([sys.executable, str(REPO / oracle)], capture_output=True, text=True)
            tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
            print(f"   {oracle}: {tail}")
            rc = rc or r.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
