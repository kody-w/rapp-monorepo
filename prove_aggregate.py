#!/usr/bin/env python3
"""Prove capture never follows repository links or retains failed output."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aggregate


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
                if cmd[-2:] == ["rev-parse", "HEAD"]:
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
