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
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import re
from pathlib import Path

import ip_gate
from verify_snapshot import (
    MANIFEST_INTEGRITY_PROFILE,
    MANIFEST_SCHEMA,
    TreeDigest,
    render_index,
)

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
SKIP_DIRS = {".git"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(cmd, timeout=120, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, **kw)


def _remove_path(path: Path) -> None:
    """Remove a generated path without following a symlink."""
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
        return
    shutil.rmtree(path, ignore_errors=True)


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
    dest = OUT / repo

    def fail(reason: str):
        _remove_path(src)
        # A failed refresh must not leave an older, unlisted snapshot behind.
        _remove_path(dest)
        return None, reason

    try:
        r = run(["git", "clone", "-q", "--depth", "1", "--single-branch",
                 f"https://github.com/{owner}/{repo}.git", str(src)],
                timeout=CLONE_TIMEOUT)
        if r.returncode != 0:
            return fail(f"clone failed: {(r.stderr or '').strip()[:100]}")
    except subprocess.TimeoutExpired:
        return fail(f"clone exceeded {CLONE_TIMEOUT}s")
    except Exception as e:
        return fail(f"{type(e).__name__}: {e}")

    head = run([
        "git", "-C", str(src), "rev-parse", "--verify", "HEAD^{commit}",
    ])
    sha = (head.stdout or "").strip()
    if head.returncode != 0 or not re.fullmatch(
        r"(?:[0-9a-f]{40}|[0-9a-f]{64})", sha
    ):
        return fail("repository has no resolvable HEAD commit")
    committed = run([
        "git", "-C", str(src), "log", "-1", "--format=%cI",
    ])
    when = (committed.stdout or "").strip()
    if committed.returncode != 0 or not when:
        return fail("repository HEAD has no commit timestamp")

    _remove_path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    limit = max_file_mb * 1024 * 1024
    files = bytes_written = 0
    skipped_large: list[str] = []
    withheld: list[dict] = []
    tree_digest = TreeDigest()

    try:
        source_paths = sorted(src.rglob("*"))
    except OSError as e:
        return fail(f"cannot enumerate repository tree: {type(e).__name__}: {e}")

    for path in source_paths:
        rel = path.relative_to(src)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        link_target: str | None = None
        try:
            if path.is_symlink():
                link_target = os.readlink(path)
                raw = os.fsencode(link_target)
                size = len(raw)
                git_mode = "120000"
            else:
                source_mode = path.lstat().st_mode
                if stat.S_ISDIR(source_mode):
                    continue
                if not stat.S_ISREG(source_mode):
                    return fail(f"unsupported tracked file type at {rel}")
                size = path.lstat().st_size
                git_mode = (
                    "100755"
                    if source_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    else "100644"
                )
        except OSError as e:
            return fail(
                f"cannot inspect {rel}: {type(e).__name__}: {str(e)[:120]}"
            )
        if size > limit:
            skipped_large.append(f"{rel} ({size / 1048576:.1f}MB)")
            continue
        if link_target is None:
            try:
                raw = path.read_bytes()
            except OSError as e:
                return fail(
                    f"cannot read {rel}: {type(e).__name__}: {str(e)[:120]}"
                )
        keep, reason = ip_gate.screen(raw, str(rel))
        if not keep:
            # Withheld, not rewritten: everything that ships is byte-faithful
            # to upstream, and everything that does not is named.
            withheld.append({"file": str(rel), "reason": reason})
            continue
        target = dest / rel
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if link_target is None:
                target.write_bytes(raw)
                target.chmod(0o755 if git_mode == "100755" else 0o644)
            else:
                os.symlink(link_target, target)
        except OSError as e:
            return fail(
                f"cannot materialize {rel}: {type(e).__name__}: {str(e)[:120]}"
            )
        tree_digest.add(rel.as_posix(), git_mode, raw)
        files += 1
        bytes_written += len(raw)

    _remove_path(src)
    return {
        "repo": repo,
        "commit": sha,
        "committed_at": when,
        "captured_at": utc_now(),
        "files": files,
        "bytes": bytes_written,
        "tree_sha256": tree_digest.hexdigest(),
        "skipped_large": skipped_large,
        "withheld": withheld,
    }, ""

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
    for existing in sorted(OUT.iterdir()):
        if existing.name not in names:
            print(f"  removing {existing.name} (no longer a public member)")
            _remove_path(existing)

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

    document = {
        "schema": MANIFEST_SCHEMA,
        "integrity_profile": MANIFEST_INTEGRITY_PROFILE,
        "owner": args.owner,
        "captured_at": utc_now(),
        "membership_pattern": MEMBER,
        "max_file_mb": args.max_file_mb,
        "repos": sorted(records, key=lambda r: r["repo"].lower()),
        "not_captured": missing,
    }
    MANIFEST.write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )
    INDEX.write_text(render_index(document), encoding="utf-8")

    total = sum(r["bytes"] for r in records) / 1048576
    print(f"\n{len(records)} captured, {len(missing)} not captured, {total:.0f}MB total")
    if missing:
        print("REFUSING TO PUBLISH: at least one member was not captured")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
