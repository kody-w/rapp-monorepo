#!/usr/bin/env python3
"""aggregate.py — pull every public RAPP repo into this one, on a schedule.

The promise this repo makes: clone THIS, go to a desert island, and you have
the whole RAPP estate as it stood when the snapshot ran — no drift between
pieces, because every piece was captured in the same pass and the commit each
one came from is written down.

    python3 aggregate.py            capture everything into repos/
    python3 aggregate.py --dry-run  enumerate and size it, write nothing

WHAT IT TAKES
  Every PUBLIC, non-archived repo under the owner whose name matches the
  estate pattern (see MEMBERSHIP). Visibility is resolved AT RUN TIME, never
  from a checked-in list — a repo that goes private disappears from the next
  snapshot on its own, which is the only way this stays honest.

WHAT IT LEAVES BEHIND
  History. Each member is captured at HEAD only: this is a snapshot of the
  estate, not a backup of its git. The commit sha is recorded per repo in
  MANIFEST.json so any piece can be traced back and re-cloned in full.

  Large files, over --max-file-mb. A desert-island copy is worth more if it
  fits on the boat. Everything skipped is NAMED in the manifest — a snapshot
  that silently drops content is worse than one that admits its edges.

THE GATE
  This repo is PUBLIC and it mirrors everything, which means it would mirror
  a mistake too — into a second public location, with its own history, where
  undoing it is harder. So every captured file goes through ip_gate before it
  is written, and the gate FAILS CLOSED: if its rules are not configured, the
  run refuses rather than publishing unscreened content.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import re
from pathlib import Path

import ip_gate

HERE = Path(__file__).resolve().parent
OUT = HERE / "repos"
MANIFEST = HERE / "MANIFEST.json"
INDEX = HERE / "INDEX.md"

OWNER = os.environ.get("RAPP_OWNER", "kody-w")

# MEMBERSHIP — what counts as "a RAPP repo". Deliberately a name pattern, so
# a new repo joins the estate by being named like one; nothing to update here.
MEMBER = r"(?i)^(rapp|rappter|openrappter|RAR$|twin|brainstem|wildhaven)"

# Named exclusions, applied after MEMBER. A repo can match the estate's naming
# convention and still not belong in a single "here is everything RAPP"
# download: staging repos that rehearse deliveries into a third party's layout
# carry that third party's packaged artifacts, and "one clone, everything" is a
# very different distribution posture for those than a staging repo is. They
# stay public where they are; they do not get amplified from here.
NOT_MEMBERS = re.compile(r"(?i)aibast")

CLONE_TIMEOUT = int(os.environ.get("RAPP_CLONE_TIMEOUT", "600"))
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".next"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(cmd, timeout=120, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, **kw)


def self_name() -> str:
    """This repository's own name, from its remote — NOT its directory name.

    The first version compared against the directory name, which is whatever
    the checkout happens to be called, so the mirror matched the membership
    pattern and cloned ITSELF: repos/rapp-monorepo/repos/... Every run would
    have nested another copy inside the last one and doubled the snapshot.
    The remote is the only name that is actually this repo's identity.
    """
    r = run(["git", "-C", str(HERE), "remote", "get-url", "origin"], timeout=30)
    url = (r.stdout or "").strip()
    if url:
        return url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    return os.environ.get("RAPP_SELF_NAME", "rapp-monorepo")


def members(owner: str) -> list[str]:
    r = run(["gh", "repo", "list", owner, "--limit", "1000", "--json",
             "name,visibility,isArchived"], timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"gh repo list failed: {(r.stderr or '')[:160]}")
    pat = re.compile(MEMBER)
    me = self_name()
    return sorted(
        x["name"] for x in json.loads(r.stdout)
        if x["visibility"] == "PUBLIC" and not x["isArchived"]
        and pat.search(x["name"]) and not NOT_MEMBERS.search(x["name"])
        and x["name"] != me
    )


def capture(owner, repo, work: Path, max_file_mb: float):
    """Snapshot one repo. Returns (record, error)."""
    src = work / repo
    try:
        r = run(["git", "clone", "-q", "--depth", "1", "--single-branch",
                 f"https://github.com/{owner}/{repo}.git", str(src)],
                timeout=CLONE_TIMEOUT)
        if r.returncode != 0:
            shutil.rmtree(src, ignore_errors=True)
            return None, f"clone failed: {(r.stderr or '').strip()[:100]}"
    except subprocess.TimeoutExpired:
        shutil.rmtree(src, ignore_errors=True)
        return None, f"clone exceeded {CLONE_TIMEOUT}s"
    except Exception as e:
        shutil.rmtree(src, ignore_errors=True)
        return None, f"{type(e).__name__}: {e}"

    sha = run(["git", "-C", str(src), "rev-parse", "HEAD"]).stdout.strip()
    when = run(["git", "-C", str(src), "log", "-1", "--format=%cI"]).stdout.strip()

    dest = OUT / repo
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    limit = max_file_mb * 1024 * 1024
    files = bytes_written = 0
    skipped_large: list[str] = []
    withheld: list[dict] = []

    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > limit:
            skipped_large.append(f"{rel} ({size / 1048576:.1f}MB)")
            continue
        raw = path.read_bytes()
        keep, reason = ip_gate.screen(raw, str(rel))
        if not keep:
            # Withheld, not rewritten: everything that ships is byte-faithful
            # to upstream, and everything that does not is named.
            withheld.append({"file": str(rel), "reason": reason})
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        files += 1
        bytes_written += len(raw)

    shutil.rmtree(src, ignore_errors=True)
    return {
        "repo": repo,
        "commit": sha,
        "committed_at": when,
        "captured_at": utc_now(),
        "files": files,
        "bytes": bytes_written,
        "skipped_large": skipped_large,
        "withheld": withheld,
    }, ""


def write_index(records, missing, args):
    total_files = sum(r["files"] for r in records)
    total_bytes = sum(r["bytes"] for r in records)
    lines = [
        "# What is in here",
        "",
        f"{len(records)} public RAPP repositories, captured at HEAD in a single "
        f"pass on {utc_now()}.",
        f"{total_files:,} files, {total_bytes / 1048576:.0f} MB.",
        "",
        "Every row is the exact commit this snapshot took. Nothing here is a "
        "guess about what upstream contains — re-clone any row's repo at its "
        "sha to get the full history behind it.",
        "",
        "| repo | commit | upstream commit date | files | MB |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(records, key=lambda x: x["repo"].lower()):
        lines.append(
            f"| [`{r['repo']}`](repos/{r['repo']}) | `{r['commit'][:8]}` | "
            f"{(r['committed_at'] or '')[:10]} | {r['files']:,} | "
            f"{r['bytes'] / 1048576:.1f} |")
    dropped = [r for r in records if r["skipped_large"]]
    if dropped:
        lines += ["", "## Files too large for the boat", "",
                  f"Skipped at the {args.max_file_mb}MB per-file limit. Named, "
                  "not silently dropped — clone the upstream repo if you need "
                  "one of these.", ""]
        for r in dropped:
            for f in r["skipped_large"]:
                lines.append(f"- `{r['repo']}/{f}`")
    held = [r for r in records if r["withheld"]]
    if held:
        lines += ["", "## Withheld by the gate", "",
                  "These files exist upstream and are deliberately NOT here. "
                  "They are withheld whole rather than rewritten, so that "
                  "everything this mirror does carry is byte-identical to its "
                  "source. The rule is named; the matched text is not, because "
                  "quoting a finding republishes it.", ""]
        for r in held:
            for w in r["withheld"]:
                lines.append(f"- `{r['repo']}/{w['file']}` — {w['reason']}")
    if missing:
        lines += ["", "## Not captured this run", "",
                  "A snapshot that hides its gaps is a snapshot you cannot "
                  "trust. These members were not captured:", ""]
        for m in missing:
            lines.append(f"- `{m['repo']}` — {m['reason']}")
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-file-mb", type=float, default=2.0)
    ap.add_argument("--owner", default=OWNER)
    args = ap.parse_args()

    try:
        ip_gate.assert_configured()
    except ip_gate.GateNotConfigured as e:
        print(f"REFUSING TO AGGREGATE: {e}")
        return 3

    names = members(args.owner)
    print(f"{len(names)} public RAPP repos under {args.owner}")
    if args.dry_run:
        for n in names:
            print(f"  {n}")
        return 0

    OUT.mkdir(exist_ok=True)
    # Anything that used to be a member and is not one now (went private,
    # archived, renamed) must LEAVE the snapshot. A monorepo that keeps
    # serving a repo its owner took private is the drift it exists to prevent.
    for existing in sorted(p for p in OUT.iterdir() if p.is_dir()):
        if existing.name not in names:
            print(f"  removing {existing.name} (no longer a public member)")
            shutil.rmtree(existing, ignore_errors=True)

    records, missing = [], []
    work = Path(tempfile.mkdtemp(prefix="rapp-mono-"))
    try:
        for i, name in enumerate(names, 1):
            rec, err = capture(args.owner, name, work, args.max_file_mb)
            if err:
                missing.append({"repo": name, "reason": err})
                print(f"  [{i}/{len(names)}] {name}: NOT CAPTURED — {err}")
                continue
            records.append(rec)
            note = (f" — {len(rec['withheld'])} file(s) WITHHELD by the gate"
                    if rec["withheld"] else "")
            print(f"  [{i}/{len(names)}] {name}: {rec['files']} files, "
                  f"{rec['bytes'] / 1048576:.1f}MB{note}", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    MANIFEST.write_text(json.dumps({
        "schema": "rapp-monorepo/1.0",
        "owner": args.owner,
        "captured_at": utc_now(),
        "membership_pattern": MEMBER,
        "max_file_mb": args.max_file_mb,
        "repos": sorted(records, key=lambda r: r["repo"].lower()),
        "not_captured": missing,
    }, indent=2) + "\n", encoding="utf-8")
    write_index(records, missing, args)

    total = sum(r["bytes"] for r in records) / 1048576
    print(f"\n{len(records)} captured, {len(missing)} not captured, {total:.0f}MB total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
