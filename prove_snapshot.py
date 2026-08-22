#!/usr/bin/env python3
"""Prove the staged Git tree exactly matches the generated snapshot contract."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_snapshot import (
    SnapshotVerificationError,
    compute_tree_sha256,
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

    def write_manifest(self, entries, not_captured=None):
        total_bytes = sum(len(raw) for _, _, raw in entries)
        manifest = {
            "schema": "rapp-monorepo/1.0",
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
