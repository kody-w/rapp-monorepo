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

  Checkout transformations. Files and modes come from the cloned Git index
  and raw blobs, never the worktree, so attributes and smudge filters cannot
  change what the recorded commit authenticates. Tracked gitlinks are kept as
  exact mode-160000 commit pointers without cloning or dereferencing targets.

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
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import ip_gate
from verify_snapshot import (
    MANIFEST_INTEGRITY_PROFILE,
    MANIFEST_SCHEMA,
    SUPPORTED_MODES,
    TreeDigest,
    render_index,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "repos"
MANIFEST = HERE / "MANIFEST.json"
INDEX = HERE / "INDEX.md"
ORGANISM = HERE / "ORGANISM.json"

OWNER = os.environ.get("RAPP_OWNER", "kody-w")

CLONE_TIMEOUT = int(os.environ.get("RAPP_CLONE_TIMEOUT", "600"))
REST_PAGE_SIZE = 100
COMMIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


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


def _api_json(endpoint: str):
    r = run(["gh", "api", "--method", "GET", endpoint], timeout=180)
    if r.returncode != 0:
        raise RuntimeError(
            f"GitHub REST request failed for {endpoint}: "
            f"{(r.stderr or '').strip()[:160]}"
        )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"GitHub REST request returned invalid JSON for {endpoint}"
        ) from exc


def _public_repositories(owner: str) -> list[dict]:
    """Return a count-verified, completely paginated public inventory."""
    encoded_owner = quote(owner, safe="")
    account = _api_json(f"/users/{encoded_owner}")
    if not isinstance(account, dict):
        raise RuntimeError("GitHub owner metadata must be an object")
    expected = account.get("public_repos")
    if (
        not isinstance(expected, int)
        or isinstance(expected, bool)
        or expected < 0
    ):
        raise RuntimeError("GitHub owner metadata has no valid public_repos count")

    repositories: list[dict] = []
    seen: set[str] = set()
    page = 1
    while True:
        endpoint = (
            f"/users/{encoded_owner}/repos?per_page={REST_PAGE_SIZE}"
            f"&page={page}&sort=full_name&direction=asc"
        )
        items = _api_json(endpoint)
        if not isinstance(items, list):
            raise RuntimeError(f"GitHub repository page {page} must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise RuntimeError(
                    f"GitHub repository page {page} contains a non-object"
                )
            name = item.get("name")
            if not isinstance(name, str) or not name:
                raise RuntimeError(
                    f"GitHub repository page {page} contains an invalid name"
                )
            if item.get("private") is not False:
                raise RuntimeError(
                    f"public repository endpoint returned non-public repo {name}"
                )
            key = name.casefold()
            if key in seen:
                raise RuntimeError(
                    f"GitHub pagination returned duplicate repository {name}"
                )
            seen.add(key)
            repositories.append(item)
        if len(items) < REST_PAGE_SIZE:
            break
        page += 1

    if len(repositories) != expected:
        raise RuntimeError(
            "GitHub public repository pagination was incomplete: "
            f"expected {expected}, received {len(repositories)}"
        )
    return repositories


def _membership_contract(owner: str, self_repo: str) -> tuple[re.Pattern, list[dict]]:
    """Load the one reviewed membership policy consumed by docs, SDK, and publisher."""

    try:
        document = json.loads(ORGANISM.read_text(encoding="utf-8"))
        scope = document["estate_scope"]
        membership = scope["membership"]
        exclusions = scope["deliberate_exclusions"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("ORGANISM.json has no usable estate membership contract") from exc
    if (
        scope.get("owner") != owner
        or membership.get("visibility") != "public"
        or membership.get("archived") is not False
        or not isinstance(membership.get("name_pattern"), str)
        or not membership["name_pattern"]
        or not isinstance(exclusions, list)
    ):
        raise RuntimeError("ORGANISM.json estate membership contract is invalid")
    try:
        pattern = re.compile(membership["name_pattern"])
    except re.error as exc:
        raise RuntimeError("ORGANISM.json membership pattern is invalid") from exc

    normalized: list[dict] = []
    seen: set[str] = set()
    for item in exclusions:
        if (
            not isinstance(item, dict)
            or set(item) != {"repository", "reason_code", "reason"}
            or not isinstance(item["repository"], str)
            or item["repository"].count("/") != 1
            or not item["repository"].startswith(f"{owner}/")
            or not isinstance(item["reason_code"], str)
            or not item["reason_code"]
            or not isinstance(item["reason"], str)
            or not item["reason"]
        ):
            raise RuntimeError("ORGANISM.json contains an invalid membership exclusion")
        name = item["repository"].split("/", 1)[1]
        key = name.casefold()
        if key in seen or pattern.search(name) is None:
            raise RuntimeError("ORGANISM.json membership exclusions are duplicate or out of scope")
        seen.add(key)
        normalized.append({
            "repo": name,
            "reason_code": item["reason_code"],
            "reason": item["reason"],
        })
    if self_repo.casefold() not in seen:
        raise RuntimeError("ORGANISM.json must explicitly exclude the snapshot repository")
    return pattern, sorted(normalized, key=lambda item: item["repo"].casefold())


def members(owner: str, self_repo: str | None = None) -> list[str]:
    repositories = _public_repositories(owner)
    me = self_repo or self_name()
    pattern, exclusions = _membership_contract(owner, me)
    excluded = {item["repo"].casefold() for item in exclusions}
    return sorted(
        x["name"] for x in repositories
        if not x.get("archived", False)
        and pattern.search(x["name"])
        and x["name"].casefold() not in excluded
    )


@dataclass(frozen=True)
class SourceIndexEntry:
    path: str
    mode: str
    oid: str


def _source_index_entries(src: Path) -> list[SourceIndexEntry]:
    result = subprocess.run(
        ["git", "-C", str(src), "ls-files", "--stage", "-z"],
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git ls-files failed: {detail[:200]}")

    entries: list[SourceIndexEntry] = []
    seen: set[str] = set()
    for item in result.stdout.split(b"\0"):
        if not item:
            continue
        try:
            header, raw_path = item.split(b"\t", 1)
            raw_mode, raw_oid, raw_stage = header.split(b" ", 2)
            mode = raw_mode.decode("ascii")
            oid = raw_oid.decode("ascii")
        except (UnicodeDecodeError, ValueError) as exc:
            raise RuntimeError("git returned a malformed source index entry") from exc
        path = os.fsdecode(raw_path)
        if raw_stage != b"0":
            raise RuntimeError(f"unmerged source index entry at {path}")
        if (
            not path
            or path.startswith("/")
            or any(part in {"", ".", ".."} for part in path.split("/"))
        ):
            raise RuntimeError(f"unsafe source index path: {path!r}")
        if path in seen:
            raise RuntimeError(f"duplicate source index path: {path}")
        seen.add(path)
        if mode not in SUPPORTED_MODES:
            raise RuntimeError(f"unsupported Git mode {mode} at {path}")
        if not COMMIT_OID.fullmatch(oid):
            raise RuntimeError(f"invalid Git object ID at {path}")
        entries.append(SourceIndexEntry(path=path, mode=mode, oid=oid))
    return entries


class _GitBlobReader:
    """Read raw source blobs without invoking checkout filters."""

    def __init__(self, src: Path):
        self.src = src
        self.info: subprocess.Popen | None = None
        self.contents: subprocess.Popen | None = None
        self.sizes: dict[str, int] = {}

    def __enter__(self):
        common = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        self.info = subprocess.Popen(
            ["git", "-C", str(self.src), "cat-file", "--batch-check"],
            **common,
        )
        self.contents = subprocess.Popen(
            ["git", "-C", str(self.src), "cat-file", "--batch"],
            **common,
        )
        return self

    @staticmethod
    def _header(process: subprocess.Popen, oid: str) -> int:
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Git blob reader is not running")
        process.stdin.write(oid.encode("ascii") + b"\n")
        process.stdin.flush()
        header = process.stdout.readline().rstrip(b"\n")
        fields = header.split(b" ")
        if len(fields) != 3 or fields[1] != b"blob":
            raise RuntimeError(
                f"cannot read Git blob {oid}: "
                f"{header.decode('utf-8', errors='replace')}"
            )
        try:
            return int(fields[2])
        except ValueError as exc:
            raise RuntimeError(f"invalid Git blob size for {oid}") from exc

    def size(self, oid: str) -> int:
        cached = self.sizes.get(oid)
        if cached is not None:
            return cached
        if self.info is None:
            raise RuntimeError("Git blob reader is not running")
        size = self._header(self.info, oid)
        self.sizes[oid] = size
        return size

    def read(self, oid: str, expected_size: int) -> bytes:
        if self.contents is None or self.contents.stdout is None:
            raise RuntimeError("Git blob reader is not running")
        size = self._header(self.contents, oid)
        if size != expected_size:
            raise RuntimeError(
                f"Git blob {oid} changed size from {expected_size} to {size}"
            )
        raw = self.contents.stdout.read(size)
        terminator = self.contents.stdout.read(1)
        if len(raw) != size or terminator != b"\n":
            raise RuntimeError(f"truncated Git blob {oid}")
        return raw

    def __exit__(self, exc_type, _exc, _traceback):
        failures: list[str] = []
        for process in (self.info, self.contents):
            if process is None:
                continue
            if process.stdin is not None:
                process.stdin.close()
            stderr = (
                process.stderr.read()
                if process.stderr is not None
                else b""
            )
            returncode = process.wait()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            if returncode != 0:
                failures.append(
                    stderr.decode("utf-8", errors="replace").strip()[:200]
                )
        if exc_type is None and failures:
            raise RuntimeError(f"git cat-file failed: {'; '.join(failures)}")
        return False


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
        r = run(["git", "clone", "-q", "--no-checkout", "--depth", "1",
                 "--single-branch", f"https://github.com/{owner}/{repo}.git",
                 str(src)],
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
    if head.returncode != 0 or not COMMIT_OID.fullmatch(sha):
        return fail("repository has no resolvable HEAD commit")
    committed = run([
        "git", "-C", str(src), "log", "-1", "--format=%cI",
    ])
    when = (committed.stdout or "").strip()
    if committed.returncode != 0 or not when:
        return fail("repository HEAD has no commit timestamp")

    indexed = run(["git", "-C", str(src), "read-tree", "HEAD"])
    if indexed.returncode != 0:
        return fail(
            f"cannot populate source Git index: "
            f"{(indexed.stderr or '').strip()[:120]}"
        )
    try:
        source_entries = _source_index_entries(src)
    except (OSError, RuntimeError) as e:
        return fail(f"cannot enumerate source Git index: {str(e)[:240]}")

    _remove_path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    limit = max_file_mb * 1024 * 1024
    files = bytes_written = 0
    skipped_large: list[str] = []
    withheld: list[dict] = []
    gitlinks: list[dict] = []
    tree_digest = TreeDigest()

    try:
        blobs = _GitBlobReader(src)
        with blobs:
            for entry in source_entries:
                if entry.mode == "160000":
                    keep, reason = ip_gate.screen_path(entry.path)
                    if not keep:
                        withheld.append({
                            "file": entry.path,
                            "reason": reason,
                        })
                        continue
                    raw_oid = bytes.fromhex(entry.oid)
                    gitlinks.append({
                        "path": entry.path,
                        "commit": entry.oid,
                    })
                    tree_digest.add(entry.path, entry.mode, raw_oid)
                    files += 1
                    bytes_written += len(raw_oid)
                    continue
                try:
                    size = blobs.size(entry.oid)
                except (OSError, RuntimeError) as e:
                    raise RuntimeError(
                        f"cannot inspect Git blob at {entry.path}: "
                        f"{type(e).__name__}: {str(e)[:120]}"
                    ) from e
                if size > limit:
                    skipped_large.append(
                        f"{entry.path} ({size / 1048576:.1f}MB)"
                    )
                    continue
                try:
                    raw = blobs.read(entry.oid, size)
                except (OSError, RuntimeError) as e:
                    raise RuntimeError(
                        f"cannot read Git blob at {entry.path}: "
                        f"{type(e).__name__}: {str(e)[:120]}"
                    ) from e
                keep, reason = ip_gate.screen(raw, entry.path)
                if not keep:
                    withheld.append({"file": entry.path, "reason": reason})
                    continue
                target = dest / entry.path
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if entry.mode == "120000":
                        os.symlink(os.fsdecode(raw), target)
                    else:
                        target.write_bytes(raw)
                        target.chmod(0o755 if entry.mode == "100755" else 0o644)
                except OSError as e:
                    raise RuntimeError(
                        f"cannot materialize {entry.path}: "
                        f"{type(e).__name__}: {str(e)[:120]}"
                    ) from e
                tree_digest.add(entry.path, entry.mode, raw)
                files += 1
                bytes_written += len(raw)
    except (OSError, RuntimeError) as e:
        return fail(f"cannot read source Git objects: {type(e).__name__}: {e}")

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
        "gitlinks": gitlinks,
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

    me = self_name()
    membership_pattern, membership_exclusions = _membership_contract(
        args.owner, me
    )
    names = members(args.owner, me)
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
        "membership_pattern": membership_pattern.pattern,
        "membership_exclusions": {
            "exclude_archived": True,
            "repositories": membership_exclusions,
        },
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
