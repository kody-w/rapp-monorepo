#!/usr/bin/env python3
"""Stage and prove that Git will publish exactly what the manifest describes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_SCHEMA = "rapp-monorepo/1.0"
MANIFEST_INTEGRITY_PROFILE = "rapp-monorepo-staged-tree/1.0"
SUPPORTED_MODES = {"100644", "100755", "120000"}
TREE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class SnapshotVerificationError(RuntimeError):
    """The staged snapshot does not satisfy its manifest."""


class TreeDigest:
    """A bounded digest of path, Git mode, size, and SHA-256 for every blob."""

    def __init__(self):
        self._entries: list[tuple[str, str, int, str]] = []
        self._paths: set[str] = set()

    def add(self, path: str, mode: str, raw: bytes) -> None:
        self.add_digest(path, mode, len(raw), hashlib.sha256(raw).hexdigest())

    def add_digest(
        self,
        path: str,
        mode: str,
        size: int,
        content_sha256: str,
    ) -> None:
        if path in self._paths:
            raise SnapshotVerificationError(f"duplicate snapshot path: {path}")
        if mode not in SUPPORTED_MODES:
            raise SnapshotVerificationError(
                f"unsupported Git mode {mode} for {path}"
            )
        if size < 0:
            raise SnapshotVerificationError(f"negative size for {path}")
        if not TREE_SHA256.fullmatch(content_sha256):
            raise SnapshotVerificationError(
                f"invalid content SHA-256 for {path}"
            )
        self._paths.add(path)
        self._entries.append((path, mode, size, content_sha256))

    def hexdigest(self) -> str:
        digest = hashlib.sha256()
        for path, mode, size, content_sha256 in sorted(
            self._entries,
            key=lambda entry: os.fsencode(entry[0]),
        ):
            fields = (
                os.fsencode(path),
                mode.encode("ascii"),
                str(size).encode("ascii"),
                bytes.fromhex(content_sha256),
            )
            for field in fields:
                digest.update(len(field).to_bytes(8, "big"))
                digest.update(field)
        return digest.hexdigest()


def compute_tree_sha256(entries: list[tuple[str, str, bytes]]) -> str:
    """Return the canonical tree digest for raw `(path, mode, bytes)` entries."""
    digest = TreeDigest()
    for path, mode, raw in entries:
        digest.add(path, mode, raw)
    return digest.hexdigest()


def _git(
    root: Path,
    *args: str,
    input_bytes: bytes | None = None,
) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        input=input_bytes,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SnapshotVerificationError(
            f"git {' '.join(args)} failed: {detail[:300]}"
        )
    return result.stdout


def _parse_manifest(raw: bytes, source: str) -> dict:
    try:
        document = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise SnapshotVerificationError(
            f"{source} is not UTF-8"
        ) from exc
    except json.JSONDecodeError as exc:
        raise SnapshotVerificationError(
            f"{source} is not valid JSON: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise SnapshotVerificationError("manifest root must be an object")
    if document.get("schema") != MANIFEST_SCHEMA:
        raise SnapshotVerificationError(
            f"manifest schema must be {MANIFEST_SCHEMA!r}"
        )
    if document.get("integrity_profile") != MANIFEST_INTEGRITY_PROFILE:
        raise SnapshotVerificationError(
            "manifest does not declare the staged-tree integrity profile; "
            "regenerate the snapshot before publication"
        )
    for field in ("owner", "captured_at", "membership_pattern"):
        if not isinstance(document.get(field), str) or not document[field]:
            raise SnapshotVerificationError(
                f"manifest {field} must be a non-empty string"
            )
    max_file_mb = document.get("max_file_mb")
    if (
        not isinstance(max_file_mb, (int, float))
        or isinstance(max_file_mb, bool)
        or max_file_mb <= 0
    ):
        raise SnapshotVerificationError(
            "manifest max_file_mb must be a positive number"
        )
    if not isinstance(document.get("repos"), list):
        raise SnapshotVerificationError("manifest repos must be an array")
    if not isinstance(document.get("not_captured"), list):
        raise SnapshotVerificationError(
            "manifest not_captured must be an array"
        )
    return document


@dataclass(frozen=True)
class IndexEntry:
    path: str
    mode: str
    oid: str


def _staged_entries(
    root: Path,
) -> tuple[list[IndexEntry], dict[str, IndexEntry]]:
    output = _git(
        root,
        "ls-files",
        "--stage",
        "-z",
        "--",
        "repos",
        "MANIFEST.json",
        "INDEX.md",
    )
    entries: list[IndexEntry] = []
    metadata: dict[str, IndexEntry] = {}
    seen: set[str] = set()
    for item in output.split(b"\0"):
        if not item:
            continue
        try:
            header, raw_path = item.split(b"\t", 1)
            raw_mode, raw_oid, raw_stage = header.split(b" ", 2)
        except ValueError as exc:
            raise SnapshotVerificationError(
                "git returned a malformed index entry"
            ) from exc
        path = os.fsdecode(raw_path)
        if raw_stage != b"0":
            raise SnapshotVerificationError(
                f"unmerged index entry at {path}"
            )
        if path in seen:
            raise SnapshotVerificationError(f"duplicate index path: {path}")
        seen.add(path)
        entry = IndexEntry(
            path=path,
            mode=raw_mode.decode("ascii"),
            oid=raw_oid.decode("ascii"),
        )
        if path in {"MANIFEST.json", "INDEX.md"}:
            metadata[path] = entry
            continue
        if not path.startswith("repos/"):
            raise SnapshotVerificationError(
                f"unexpected staged snapshot path: {path}"
            )
        entries.append(entry)
    return entries, metadata


class _BlobReader:
    """Read staged blobs through one persistent `git cat-file` process."""

    def __init__(self, root: Path):
        self.root = root
        self.process: subprocess.Popen | None = None
        self.cache: dict[str, tuple[int, str]] = {}

    def __enter__(self):
        self.process = subprocess.Popen(
            ["git", "-C", str(self.root), "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return self

    def describe(self, oid: str) -> tuple[int, str]:
        cached = self.cache.get(oid)
        if cached is not None:
            return cached
        if (
            self.process is None
            or self.process.stdin is None
            or self.process.stdout is None
        ):
            raise SnapshotVerificationError("Git blob reader is not running")
        self.process.stdin.write(oid.encode("ascii") + b"\n")
        self.process.stdin.flush()
        header = self.process.stdout.readline().rstrip(b"\n")
        fields = header.split(b" ")
        if len(fields) != 3 or fields[1] != b"blob":
            raise SnapshotVerificationError(
                f"cannot read staged blob {oid}: "
                f"{header.decode('utf-8', errors='replace')}"
            )
        try:
            size = int(fields[2])
        except ValueError as exc:
            raise SnapshotVerificationError(
                f"invalid staged blob size for {oid}"
            ) from exc
        raw = self.process.stdout.read(size)
        terminator = self.process.stdout.read(1)
        if len(raw) != size or terminator != b"\n":
            raise SnapshotVerificationError(
                f"truncated staged blob {oid}"
            )
        result = (size, hashlib.sha256(raw).hexdigest())
        self.cache[oid] = result
        return result

    def __exit__(self, exc_type, _exc, _traceback):
        if self.process is None:
            return False
        if self.process.stdin is not None:
            self.process.stdin.close()
        stderr = (
            self.process.stderr.read()
            if self.process.stderr is not None
            else b""
        )
        returncode = self.process.wait()
        if self.process.stdout is not None:
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.process.stderr.close()
        if exc_type is None and returncode != 0:
            detail = stderr.decode("utf-8", errors="replace").strip()
            raise SnapshotVerificationError(
                f"git cat-file failed: {detail[:300]}"
            )
        return False


def _manifest_records(document: dict) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for record in document["repos"]:
        if not isinstance(record, dict):
            raise SnapshotVerificationError(
                "every manifest repo entry must be an object"
            )
        name = record.get("repo")
        if (
            not isinstance(name, str)
            or not name
            or name in {".", ".."}
            or "/" in name
            or "\\" in name
        ):
            raise SnapshotVerificationError(
                f"invalid manifest repo name: {name!r}"
            )
        if name in records:
            raise SnapshotVerificationError(
                f"duplicate manifest repo: {name}"
            )
        commit = record.get("commit")
        if not isinstance(commit, str) or not COMMIT_OID.fullmatch(commit):
            raise SnapshotVerificationError(
                f"{name}: manifest commit is missing or invalid"
            )
        committed_at = record.get("committed_at")
        if not isinstance(committed_at, str) or not committed_at:
            raise SnapshotVerificationError(
                f"{name}: manifest committed_at is missing"
            )
        captured_at = record.get("captured_at")
        if not isinstance(captured_at, str) or not captured_at:
            raise SnapshotVerificationError(
                f"{name}: manifest captured_at is missing"
            )
        for field in ("files", "bytes"):
            value = record.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SnapshotVerificationError(
                    f"{name}: manifest {field} must be a non-negative integer"
                )
        tree_sha256 = record.get("tree_sha256")
        if not isinstance(tree_sha256, str) or not TREE_SHA256.fullmatch(
            tree_sha256
        ):
            raise SnapshotVerificationError(
                f"{name}: manifest tree_sha256 is missing or invalid"
            )
        skipped_large = record.get("skipped_large")
        if (
            not isinstance(skipped_large, list)
            or not all(isinstance(item, str) for item in skipped_large)
        ):
            raise SnapshotVerificationError(
                f"{name}: manifest skipped_large must be an array of strings"
            )
        withheld = record.get("withheld")
        if not isinstance(withheld, list) or not all(
            isinstance(item, dict)
            and set(item) == {"file", "reason"}
            and isinstance(item["file"], str)
            and isinstance(item["reason"], str)
            for item in withheld
        ):
            raise SnapshotVerificationError(
                f"{name}: manifest withheld entries must be file/reason objects"
            )
        records[name] = record
    return records


def render_index(document: dict) -> str:
    """Render the one human index corresponding to a validated manifest."""

    records = _manifest_records(document)
    ordered = sorted(records.values(), key=lambda record: record["repo"].lower())
    missing = document["not_captured"]
    total_files = sum(record["files"] for record in ordered)
    total_bytes = sum(record["bytes"] for record in ordered)
    lines = [
        "# What is in here",
        "",
        f"{len(ordered)} public RAPP repositories, captured at HEAD in a single "
        f"pass on {document['captured_at']}.",
        f"{total_files:,} files, {total_bytes / 1048576:.0f} MB.",
        "",
        "Every row is the exact commit this snapshot took. Nothing here is a "
        "guess about what upstream contains — re-clone any row's repo at its "
        "sha to get the full history behind it.",
        "",
        "| repo | commit | upstream commit date | files | MB |",
        "|---|---|---|---|---|",
    ]
    for record in ordered:
        lines.append(
            f"| [`{record['repo']}`](repos/{record['repo']}) | "
            f"`{record['commit'][:8]}` | "
            f"{record['committed_at'][:10]} | {record['files']:,} | "
            f"{record['bytes'] / 1048576:.1f} |"
        )
    dropped = [record for record in ordered if record["skipped_large"]]
    if dropped:
        lines += [
            "",
            "## Files too large for the boat",
            "",
            f"Skipped at the {document['max_file_mb']}MB per-file limit. Named, "
            "not silently dropped — clone the upstream repo if you need one of "
            "these.",
            "",
        ]
        for record in dropped:
            for item in record["skipped_large"]:
                lines.append(f"- `{record['repo']}/{item}`")
    held = [record for record in ordered if record["withheld"]]
    if held:
        lines += [
            "",
            "## Withheld by the gate",
            "",
            "These files exist upstream and are deliberately NOT here. They are "
            "withheld whole rather than rewritten, so that everything this "
            "mirror does carry is byte-identical to its source. The rule is "
            "named; the matched text is not, because quoting a finding "
            "republishes it.",
            "",
        ]
        for record in held:
            for item in record["withheld"]:
                lines.append(
                    f"- `{record['repo']}/{item['file']}` — {item['reason']}"
                )
    if missing:
        lines += [
            "",
            "## Not captured this run",
            "",
            "A snapshot that hides its gaps is a snapshot you cannot trust. "
            "These members were not captured:",
            "",
        ]
        for item in missing:
            lines.append(f"- `{item['repo']}` — {item['reason']}")
    return "\n".join(lines) + "\n"


def verify_staged(
    root: Path = HERE,
    manifest_path: Path | None = None,
) -> dict[str, int]:
    """Verify staged paths, modes, bytes, and contents against MANIFEST.json."""
    root = root.resolve()
    entries, metadata = _staged_entries(root)
    absent_metadata = {"MANIFEST.json", "INDEX.md"} - metadata.keys()
    if absent_metadata:
        raise SnapshotVerificationError(
            "required snapshot metadata is not staged: "
            + ", ".join(sorted(absent_metadata))
        )
    for path, entry in metadata.items():
        if entry.mode not in {"100644", "100755"}:
            raise SnapshotVerificationError(
                f"staged metadata has unsupported mode {entry.mode}: {path}"
            )

    staged_manifest = _git(
        root,
        "cat-file",
        "blob",
        metadata["MANIFEST.json"].oid,
    )
    worktree_manifest_path = manifest_path or root / "MANIFEST.json"
    try:
        worktree_manifest = worktree_manifest_path.read_bytes()
    except FileNotFoundError as exc:
        raise SnapshotVerificationError(
            f"manifest not found: {worktree_manifest_path}"
        ) from exc
    if staged_manifest != worktree_manifest:
        raise SnapshotVerificationError(
            "staged MANIFEST.json differs from the working tree"
        )
    staged_index = _git(
        root,
        "cat-file",
        "blob",
        metadata["INDEX.md"].oid,
    )
    try:
        worktree_index = (root / "INDEX.md").read_bytes()
    except FileNotFoundError as exc:
        raise SnapshotVerificationError("INDEX.md is missing") from exc
    if staged_index != worktree_index:
        raise SnapshotVerificationError(
            "staged INDEX.md differs from the working tree"
        )

    document = _parse_manifest(staged_manifest, "staged MANIFEST.json")
    missing = document["not_captured"]
    if missing:
        raise SnapshotVerificationError(
            f"{len(missing)} repositories were not captured; refusing publication"
        )
    records = _manifest_records(document)
    expected_index = render_index(document).encode("utf-8")
    if staged_index != expected_index:
        raise SnapshotVerificationError(
            "INDEX.md is not the deterministic rendering of MANIFEST.json"
        )

    grouped: dict[str, list[tuple[str, IndexEntry]]] = {
        name: [] for name in records
    }
    for entry in entries:
        parts = entry.path.split("/", 2)
        if len(parts) != 3 or not parts[1] or not parts[2]:
            raise SnapshotVerificationError(
                f"invalid staged snapshot path: {entry.path}"
            )
        repo, relative = parts[1], parts[2]
        if repo not in grouped:
            raise SnapshotVerificationError(
                f"staged repository is absent from the manifest: {repo}"
            )
        if entry.mode not in SUPPORTED_MODES:
            raise SnapshotVerificationError(
                f"{repo}: unsupported staged mode {entry.mode} at {relative}"
            )
        grouped[repo].append((relative, entry))

    errors: list[str] = []
    total_files = 0
    total_bytes = 0
    with _BlobReader(root) as blobs:
        for name, record in records.items():
            digest = TreeDigest()
            byte_count = 0
            repo_entries = grouped[name]
            for relative, entry in repo_entries:
                size, content_sha256 = blobs.describe(entry.oid)
                digest.add_digest(
                    relative,
                    entry.mode,
                    size,
                    content_sha256,
                )
                byte_count += size
            file_count = len(repo_entries)
            total_files += file_count
            total_bytes += byte_count
            if file_count != record["files"]:
                errors.append(
                    f"{name}: staged files {file_count} != "
                    f"manifest files {record['files']}"
                )
            if byte_count != record["bytes"]:
                errors.append(
                    f"{name}: staged bytes {byte_count} != "
                    f"manifest bytes {record['bytes']}"
                )
            actual_digest = digest.hexdigest()
            if actual_digest != record["tree_sha256"]:
                errors.append(
                    f"{name}: staged tree SHA-256 {actual_digest} != "
                    f"manifest tree SHA-256 {record['tree_sha256']}"
                )
    if errors:
        raise SnapshotVerificationError("; ".join(errors[:20]))
    return {
        "repos": len(records),
        "files": total_files,
        "bytes": total_bytes,
    }


@dataclass(frozen=True)
class WorktreeEntry:
    path: str
    mode: str
    source: Path | None = None
    raw: bytes | None = None


def _worktree_entries(root: Path) -> list[WorktreeEntry]:
    paths = [root / "MANIFEST.json", root / "INDEX.md"]
    repos = root / "repos"
    if not repos.is_dir():
        raise SnapshotVerificationError(f"snapshot directory not found: {repos}")
    paths.extend(repos.rglob("*"))

    entries: list[WorktreeEntry] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError as exc:
            raise SnapshotVerificationError(
                f"publishable path disappeared while staging: {relative}"
            ) from exc
        if path.is_symlink():
            entries.append(WorktreeEntry(
                path=relative,
                mode="120000",
                raw=os.fsencode(os.readlink(path)),
            ))
            continue
        if os.path.isdir(path):
            continue
        if not os.path.isfile(path):
            raise SnapshotVerificationError(
                f"unsupported publishable file type: {relative}"
            )
        git_mode = "100755" if mode & 0o111 else "100644"
        entries.append(WorktreeEntry(
            path=relative,
            mode=git_mode,
            source=path,
        ))
    return sorted(entries, key=lambda entry: os.fsencode(entry.path))


def _hash_worktree_entries(
    root: Path,
    entries: list[WorktreeEntry],
) -> list[tuple[str, str, str]]:
    staged: dict[str, tuple[str, str]] = {}
    regular = [entry for entry in entries if entry.source is not None]
    for offset in range(0, len(regular), 128):
        batch = regular[offset:offset + 128]
        output = _git(
            root,
            "hash-object",
            "-w",
            "--no-filters",
            "--",
            *(str(entry.source) for entry in batch),
        )
        oids = output.decode("ascii").splitlines()
        if len(oids) != len(batch):
            raise SnapshotVerificationError(
                "git hash-object returned an unexpected number of object IDs"
            )
        for entry, oid in zip(batch, oids):
            staged[entry.path] = (entry.mode, oid)

    for entry in entries:
        if entry.raw is None:
            continue
        oid = _git(
            root,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=entry.raw,
        ).decode("ascii").strip()
        staged[entry.path] = (entry.mode, oid)

    return [
        (path, mode, oid)
        for path, (mode, oid) in sorted(
            staged.items(),
            key=lambda item: os.fsencode(item[0]),
        )
    ]


def _replace_snapshot_index(
    root: Path,
    entries: list[tuple[str, str, str]],
) -> None:
    existing = _git(
        root,
        "ls-files",
        "-z",
        "--",
        "repos",
        "MANIFEST.json",
        "INDEX.md",
    )
    if existing:
        _git(
            root,
            "update-index",
            "--force-remove",
            "-z",
            "--stdin",
            input_bytes=existing,
        )
    index_info = b"".join(
        mode.encode("ascii")
        + b" "
        + oid.encode("ascii")
        + b"\t"
        + os.fsencode(path)
        + b"\0"
        for path, mode, oid in entries
    )
    _git(
        root,
        "update-index",
        "-z",
        "--index-info",
        input_bytes=index_info,
    )


def stage_and_verify(root: Path = HERE) -> dict[str, int]:
    """Raw-stage only publishable snapshot paths, then verify the index."""
    root = root.resolve()
    worktree_entries = _worktree_entries(root)
    staged_entries = _hash_worktree_entries(root, worktree_entries)
    _replace_snapshot_index(root, staged_entries)
    return verify_staged(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        action="store_true",
        help="raw-stage snapshot paths before verifying the Git index",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=HERE,
        help="repository root (defaults to this script's directory)",
    )
    args = parser.parse_args()
    try:
        summary = (
            stage_and_verify(args.root)
            if args.stage
            else verify_staged(args.root)
        )
    except SnapshotVerificationError as exc:
        print(f"REFUSING TO PUBLISH SNAPSHOT: {exc}", file=sys.stderr)
        return 1
    print(
        "verified staged snapshot: "
        f"{summary['repos']} repos, {summary['files']} files, "
        f"{summary['bytes']} bytes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
