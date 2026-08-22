#!/usr/bin/env python3
"""Prove capture never follows repository links or retains failed output."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aggregate
from verify_snapshot import compute_tree_sha256


class CaptureBoundaryTests(unittest.TestCase):
    def test_symlink_is_preserved_without_copying_its_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            work = root / "work"
            work.mkdir()
            outside = work / "outside.txt"
            outside.write_bytes(b"runner-only content")
            link_value = "../outside.txt"
            ordinary = b"ordinary content"

            def fake_run(cmd, **_kwargs):
                if cmd[:2] == ["git", "clone"]:
                    src = Path(cmd[-1])
                    src.mkdir(parents=True)
                    (src / "ordinary.txt").write_bytes(ordinary)
                    os.symlink(link_value, src / "outside-link")
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                if "rev-parse" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 0, "a" * 40 + "\n", "")
                if "--format=%cI" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 0, "2026-08-21T00:00:00+00:00\n", "")
                raise AssertionError(f"unexpected command: {cmd}")

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "run", fake_run),
                patch.object(
                    aggregate.ip_gate, "screen",
                    lambda _raw, _rel: (True, "")),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", work, max_file_mb=2.0)

            copied_link = out / "repo" / "outside-link"
            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            self.assertTrue(copied_link.is_symlink())
            self.assertEqual(os.readlink(copied_link), link_value)
            self.assertFalse((out / "outside.txt").exists())
            self.assertEqual(
                record["bytes"], len(ordinary) + len(os.fsencode(link_value)))

    def test_failed_clone_removes_stale_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            stale = out / "repo" / "stale.txt"
            stale.parent.mkdir(parents=True)
            stale.write_bytes(b"old snapshot")
            failed = subprocess.CompletedProcess(
                [], 1, "", "network failure")

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "run", lambda *_args, **_kwargs: failed),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", root / "work", max_file_mb=2.0)

            self.assertIsNone(record)
            self.assertIn("clone failed", error)
            self.assertFalse((out / "repo").exists())

    def test_unborn_repository_is_not_reported_as_captured(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            work = root / "work"
            work.mkdir()

            def fake_run(cmd, **_kwargs):
                if cmd[:2] == ["git", "clone"]:
                    Path(cmd[-1]).mkdir(parents=True)
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                if "rev-parse" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 128, "HEAD\n", "unknown revision")
                raise AssertionError(f"unexpected command: {cmd}")

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "run", fake_run),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", work, max_file_mb=2.0)

            self.assertIsNone(record)
            self.assertIn("HEAD commit", error)
            self.assertFalse((out / "repo").exists())

    def test_executable_mode_and_tree_digest_are_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            work = root / "work"
            work.mkdir()
            script = b"#!/bin/sh\necho captured\n"
            ordinary = b"ordinary content\n"

            def fake_run(cmd, **_kwargs):
                if cmd[:2] == ["git", "clone"]:
                    src = Path(cmd[-1])
                    src.mkdir(parents=True)
                    executable = src / "install.sh"
                    executable.write_bytes(script)
                    executable.chmod(0o755)
                    (src / "README.md").write_bytes(ordinary)
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                if "rev-parse" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 0, "a" * 40 + "\n", "")
                if "--format=%cI" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 0, "2026-08-21T00:00:00+00:00\n", "")
                raise AssertionError(f"unexpected command: {cmd}")

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "run", fake_run),
                patch.object(
                    aggregate.ip_gate, "screen",
                    lambda _raw, _rel: (True, "")),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", work, max_file_mb=2.0)

            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            copied = out / "repo" / "install.sh"
            self.assertEqual(copied.stat().st_mode & 0o111, 0o111)
            self.assertEqual(
                record["tree_sha256"],
                compute_tree_sha256([
                    ("README.md", "100644", ordinary),
                    ("install.sh", "100755", script),
                ]),
            )

    def test_main_returns_failure_when_any_repo_is_not_captured(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "repos"
            manifest_path = root / "MANIFEST.json"
            index_path = root / "INDEX.md"
            record = {
                "repo": "good",
                "commit": "a" * 40,
                "committed_at": "2026-08-21T00:00:00+00:00",
                "captured_at": "2026-08-21T00:00:00+00:00",
                "files": 0,
                "bytes": 0,
                "tree_sha256": compute_tree_sha256([]),
                "skipped_large": [],
                "withheld": [],
            }

            def fake_capture(_owner, repo, _work, _max_file_mb):
                if repo == "good":
                    return record, ""
                return None, "clone failed: unavailable"

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "MANIFEST", manifest_path),
                patch.object(aggregate, "INDEX", index_path),
                patch.object(aggregate.ip_gate, "assert_configured"),
                patch.object(aggregate, "members", return_value=["good", "bad"]),
                patch.object(aggregate, "capture", fake_capture),
                patch.object(sys, "argv", ["aggregate.py"]),
            ):
                exit_code = aggregate.main()

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 4)
            self.assertEqual(
                manifest["not_captured"],
                [{"repo": "bad", "reason": "clone failed: unavailable"}],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
