#!/usr/bin/env python3
"""Prove the staged Git tree exactly matches the generated snapshot contract."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_snapshot import (
    MANIFEST_INTEGRITY_PROFILE,
    MANIFEST_SCHEMA,
    SnapshotVerificationError,
    compute_tree_sha256,
    render_index,
    stage_and_verify,
    verify_staged,
)


class SnapshotIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "snapshot-test")
        self.git("config", "user.email", "snapshot-test@example.invalid")
        self.git("commit", "--allow-empty", "-qm", "base")
        (self.root / "repos" / "demo").mkdir(parents=True)
        (self.root / "INDEX.md").write_text("# test index\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args, check=True):
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def write_manifest(
        self,
        entries,
        not_captured=None,
        schema=MANIFEST_SCHEMA,
        integrity_profile=MANIFEST_INTEGRITY_PROFILE,
    ):
        total_bytes = sum(len(raw) for _, _, raw in entries)
        manifest = {
            "schema": schema,
            "integrity_profile": integrity_profile,
            "owner": "test-owner",
            "captured_at": "2026-08-21T00:00:00+00:00",
            "membership_pattern": "^demo$",
            "max_file_mb": 2.0,
            "repos": [{
                "repo": "demo",
                "commit": "a" * 40,
                "committed_at": "2026-08-21T00:00:00+00:00",
                "captured_at": "2026-08-21T00:00:00+00:00",
                "files": len(entries),
                "bytes": total_bytes,
                "tree_sha256": compute_tree_sha256(entries),
                "skipped_large": [],
                "withheld": [],
            }],
            "not_captured": not_captured or [],
        }
        (self.root / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "INDEX.md").write_text(
            render_index(manifest),
            encoding="utf-8",
        )

    def test_force_staging_includes_nested_ignored_files_but_not_gate_rules(self):
        ignored = b"tracked upstream but ignored here\n"
        ignore_rule = b"hidden.txt\n"
        repo = self.root / "repos" / "demo"
        (repo / ".gitignore").write_bytes(ignore_rule)
        (repo / "hidden.txt").write_bytes(ignored)
        (self.root / ".gate-rules").write_text(
            '{"content":["do-not-stage"]}\n',
            encoding="utf-8",
        )
        entries = [
            (".gitignore", "100644", ignore_rule),
            ("hidden.txt", "100644", ignored),
        ]
        self.write_manifest(entries)

        self.git("add", "-A", "--", "repos", "MANIFEST.json", "INDEX.md")
        with self.assertRaisesRegex(
            SnapshotVerificationError, "demo.*files"
        ):
            verify_staged(self.root)

        self.git("reset", "-q")
        summary = stage_and_verify(self.root)
        staged = self.git("ls-files", "--cached").stdout.splitlines()

        self.assertEqual(summary["repos"], 1)
        self.assertEqual(summary["files"], 2)
        self.assertIn("repos/demo/hidden.txt", staged)
        self.assertNotIn(".gate-rules", staged)

    def test_raw_bytes_survive_nested_git_attributes(self):
        attributes = b"payload.txt text eol=crlf\n"
        payload = b"line one\nline two\n"
        repo = self.root / "repos" / "demo"
        (repo / ".gitattributes").write_bytes(attributes)
        (repo / "payload.txt").write_bytes(payload)
        self.write_manifest([
            (".gitattributes", "100644", attributes),
            ("payload.txt", "100644", payload),
        ])

        stage_and_verify(self.root)

        oid = self.git(
            "rev-parse", ":repos/demo/payload.txt"
        ).stdout.strip()
        staged = subprocess.check_output(
            ["git", "-C", str(self.root), "cat-file", "blob", oid]
        )
        self.assertEqual(staged, payload)

    def test_executable_mode_survives_raw_staging(self):
        script = b"#!/bin/sh\necho executable\n"
        path = self.root / "repos" / "demo" / "run.sh"
        path.write_bytes(script)
        path.chmod(0o755)
        self.write_manifest([("run.sh", "100755", script)])

        stage_and_verify(self.root)

        mode = self.git(
            "ls-files", "--stage", "--", "repos/demo/run.sh"
        ).stdout.split(" ", 1)[0]
        self.assertEqual(mode, "100755")

    def test_symlink_target_survives_raw_staging(self):
        target = "../outside.txt"
        path = self.root / "repos" / "demo" / "outside-link"
        path.symlink_to(target)
        raw_target = target.encode()
        self.write_manifest([("outside-link", "120000", raw_target)])

        stage_and_verify(self.root)

        mode, oid, _stage_path = self.git(
            "ls-files", "--stage", "--", "repos/demo/outside-link"
        ).stdout.split(maxsplit=2)
        self.assertEqual(mode, "120000")
        staged = self.git("cat-file", "blob", oid).stdout
        self.assertEqual(staged, target)

    def test_staging_does_not_modify_shared_git_attributes(self):
        payload = b"raw bytes\n"
        path = self.root / "repos" / "demo" / "payload.txt"
        path.write_bytes(payload)
        self.write_manifest([("payload.txt", "100644", payload)])
        attributes = self.root / ".git" / "info" / "attributes"
        attributes.parent.mkdir(parents=True, exist_ok=True)
        sentinel = b"*.txt text eol=crlf\n"
        attributes.write_bytes(sentinel)
        attributes.chmod(0o444)
        try:
            stage_and_verify(self.root)
        finally:
            attributes.chmod(0o644)

        self.assertEqual(attributes.read_bytes(), sentinel)

    def test_verifier_uses_the_staged_manifest(self):
        original = b"original\n"
        changed = b"changed after manifest staging\n"
        path = self.root / "repos" / "demo" / "payload.txt"
        path.write_bytes(original)
        self.write_manifest([("payload.txt", "100644", original)])
        stage_and_verify(self.root)

        path.write_bytes(changed)
        self.write_manifest([("payload.txt", "100644", changed)])
        self.git("add", "-f", "--", "repos/demo/payload.txt")

        with self.assertRaises(SnapshotVerificationError):
            verify_staged(self.root)

    def test_verifier_rejects_a_missing_staged_entry(self):
        payload = b"must be present\n"
        path = self.root / "repos" / "demo" / "payload.txt"
        path.write_bytes(payload)
        self.write_manifest([("payload.txt", "100644", payload)])
        stage_and_verify(self.root)
        self.git("rm", "--cached", "-q", "--", "repos/demo/payload.txt")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "demo.*files"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_any_failed_capture(self):
        self.write_manifest(
            [],
            not_captured=[{"repo": "demo-missing", "reason": "clone failed"}],
        )
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "not captured"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_an_unknown_manifest_schema(self):
        self.write_manifest([], schema="rapp-monorepo/99.0")
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "manifest schema"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_a_legacy_manifest_without_integrity_profile(self):
        self.write_manifest([], integrity_profile=None)
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "integrity profile"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_an_index_not_rendered_from_manifest(self):
        self.write_manifest([])
        (self.root / "INDEX.md").write_text("# unrelated\n", encoding="utf-8")
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "deterministic rendering"
        ):
            verify_staged(self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
