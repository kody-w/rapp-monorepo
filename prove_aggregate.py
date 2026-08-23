#!/usr/bin/env python3
"""Prove source enumeration and capture preserve the raw Git contract."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aggregate
from verify_snapshot import (
    MANIFEST_INTEGRITY_PROFILE,
    MANIFEST_SCHEMA,
    compute_tree_sha256,
    render_index,
    stage_and_verify,
)


class CaptureBoundaryTests(unittest.TestCase):
    def git(self, root: Path, *args: str, check: bool = True):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def init_repo(self, root: Path) -> None:
        root.mkdir(parents=True)
        self.git(root, "init", "-q")
        self.git(root, "config", "user.name", "snapshot-test")
        self.git(root, "config", "user.email", "snapshot-test@example.invalid")

    def commit(self, root: Path, message: str = "fixture") -> None:
        self.git(root, "add", "-A")
        self.git(root, "commit", "-qm", message)

    def local_run(self, source: Path):
        real_run = aggregate.run

        def run(cmd, **kwargs):
            if cmd[:2] == ["git", "clone"]:
                cmd = list(cmd)
                cmd[-2] = source.resolve().as_uri()
            return real_run(cmd, **kwargs)

        return run

    def capture_repo(
        self,
        root: Path,
        source: Path,
        screen=lambda _raw, _path: (True, ""),
        screen_path=lambda _path: (True, ""),
    ):
        out = root / "out"
        work = root / "work"
        work.mkdir()
        with (
            patch.object(aggregate, "OUT", out),
            patch.object(aggregate, "run", self.local_run(source)),
            patch.object(aggregate.ip_gate, "screen", screen),
            patch.object(
                aggregate.ip_gate,
                "screen_path",
                screen_path,
            ),
        ):
            record, error = aggregate.capture(
                "owner", "repo", work, max_file_mb=2.0
            )
        return out, record, error

    def test_symlink_is_preserved_without_copying_its_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            outside = root / "outside.txt"
            outside.write_bytes(b"runner-only content")
            link_value = "../outside.txt"
            ordinary = b"ordinary content"
            (source / "ordinary.txt").write_bytes(ordinary)
            os.symlink(link_value, source / "outside-link")
            self.commit(source)

            out, record, error = self.capture_repo(root, source)

            copied_link = out / "repo" / "outside-link"
            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            self.assertTrue(copied_link.is_symlink())
            self.assertEqual(os.readlink(copied_link), link_value)
            self.assertFalse((out / "outside.txt").exists())
            self.assertEqual(
                record["bytes"], len(ordinary) + len(os.fsencode(link_value))
            )

    def test_failed_clone_removes_stale_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            stale = out / "repo" / "stale.txt"
            stale.parent.mkdir(parents=True)
            stale.write_bytes(b"old snapshot")
            failed = subprocess.CompletedProcess(
                [], 1, "", "network failure"
            )

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(
                    aggregate, "run", lambda *_args, **_kwargs: failed
                ),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", root / "work", max_file_mb=2.0
                )

            self.assertIsNone(record)
            self.assertIn("clone failed", error)
            self.assertFalse((out / "repo").exists())

    def test_unborn_repository_is_not_reported_as_captured(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)

            out, record, error = self.capture_repo(root, source)

            self.assertIsNone(record)
            self.assertIn("HEAD commit", error)
            self.assertFalse((out / "repo").exists())

    def test_executable_mode_and_tree_digest_are_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            script = b"#!/bin/sh\necho captured\n"
            ordinary = b"ordinary content\n"
            executable = source / "install.sh"
            executable.write_bytes(script)
            executable.chmod(0o755)
            (source / "README.md").write_bytes(ordinary)
            self.commit(source)

            out, record, error = self.capture_repo(root, source)

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

    def test_tracked_cache_paths_are_captured_instead_of_silently_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            bytecode = b"tracked cache bytes"
            cached = source / "__pycache__" / "module.pyc"
            cached.parent.mkdir()
            cached.write_bytes(bytecode)
            self.commit(source)

            out, record, error = self.capture_repo(root, source)

            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            self.assertEqual(record["files"], 1)
            self.assertEqual(
                (out / "repo" / "__pycache__" / "module.pyc").read_bytes(),
                bytecode,
            )

    def test_git_attributes_cannot_smudge_captured_blob_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            attributes = b"payload.txt text eol=crlf\n"
            payload = b"line one\nline two\n"
            (source / ".gitattributes").write_bytes(attributes)
            (source / "payload.txt").write_bytes(payload)
            self.commit(source)
            upstream_blob = subprocess.check_output([
                "git", "-C", str(source), "cat-file", "blob", "HEAD:payload.txt",
            ])

            out, record, error = self.capture_repo(root, source)

            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            self.assertEqual(upstream_blob, payload)
            self.assertEqual(
                (out / "repo" / "payload.txt").read_bytes(),
                upstream_blob,
            )

    def test_tracked_gitlink_is_preserved_without_copying_target_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            child = root / "child"
            self.init_repo(child)
            (child / "child.txt").write_text("child\n", encoding="utf-8")
            self.commit(child)
            child_commit = self.git(child, "rev-parse", "HEAD").stdout.strip()

            source = root / "source"
            self.init_repo(source)
            gitmodules = (
                '[submodule "deps/child"]\n'
                "\tpath = deps/child\n"
                f"\turl = {child.resolve().as_uri()}\n"
            )
            (source / ".gitmodules").write_text(
                gitmodules,
                encoding="utf-8",
            )
            self.git(source, "add", ".gitmodules")
            self.git(
                source,
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{child_commit},deps/child",
            )
            self.git(source, "commit", "-qm", "gitlink")

            out, record, error = self.capture_repo(root, source)

            self.assertEqual(error, "")
            self.assertIsNotNone(record)
            self.assertEqual(record["files"], 2)
            self.assertEqual(
                record["bytes"],
                len(gitmodules.encode()) + len(bytes.fromhex(child_commit)),
            )
            self.assertEqual(record["gitlinks"], [{
                "path": "deps/child",
                "commit": child_commit,
            }])
            self.assertEqual(
                record["tree_sha256"],
                compute_tree_sha256([
                    (".gitmodules", "100644", gitmodules.encode()),
                    ("deps/child", "160000", bytes.fromhex(child_commit)),
                ]),
            )
            self.assertFalse((out / "repo" / "deps" / "child").exists())
            self.assertEqual(
                list((out / "repo").rglob("child.txt")),
                [],
            )

    def test_gitlink_capture_and_raw_stage_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            child = root / "child"
            self.init_repo(child)
            (child / "target.txt").write_text("do not copy\n", encoding="utf-8")
            self.commit(child)
            child_commit = self.git(child, "rev-parse", "HEAD").stdout.strip()

            source = root / "source"
            self.init_repo(source)
            self.git(
                source,
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{child_commit},openclaw",
            )
            self.git(source, "commit", "-qm", "gitlink-only superproject")

            destination = root / "destination"
            self.init_repo(destination)
            self.git(destination, "commit", "--allow-empty", "-qm", "base")
            (destination / "repos").mkdir()
            work = root / "work"
            work.mkdir()
            with (
                patch.object(aggregate, "OUT", destination / "repos"),
                patch.object(aggregate, "run", self.local_run(source)),
                patch.object(
                    aggregate.ip_gate,
                    "screen",
                    lambda _raw, _path: (True, ""),
                ),
                patch.object(
                    aggregate.ip_gate,
                    "screen_path",
                    lambda _path: (True, ""),
                ),
            ):
                record, error = aggregate.capture(
                    "owner", "demo", work, max_file_mb=2.0
                )
            self.assertEqual(error, "")
            document = {
                "schema": MANIFEST_SCHEMA,
                "integrity_profile": MANIFEST_INTEGRITY_PROFILE,
                "owner": "owner",
                "captured_at": "2026-08-23T00:00:00+00:00",
                "membership_pattern": "^demo$",
                "max_file_mb": 2.0,
                "repos": [record],
                "not_captured": [],
            }
            (destination / "MANIFEST.json").write_text(
                json.dumps(document, indent=2) + "\n",
                encoding="utf-8",
            )
            (destination / "INDEX.md").write_text(
                render_index(document),
                encoding="utf-8",
            )

            summary = stage_and_verify(destination)

            staged = self.git(
                destination,
                "ls-files",
                "--stage",
                "--",
                "repos/demo/openclaw",
            ).stdout.split()
            self.assertEqual(staged[:2], ["160000", child_commit])
            self.assertEqual(summary["files"], 1)
            self.assertFalse(
                (destination / "repos" / "demo" / "openclaw").exists()
            )
            self.assertEqual(
                list((destination / "repos").rglob("target.txt")),
                [],
            )
            self.assertNotEqual(
                self.git(
                    destination,
                    "cat-file",
                    "-e",
                    child_commit,
                    check=False,
                ).returncode,
                0,
            )

    def test_gitlink_path_gate_still_withholds_the_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            commit = "8" * 40
            self.git(
                source,
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{commit},private-notes/dependency",
            )
            self.git(source, "commit", "-qm", "withheld gitlink")

            out, record, error = self.capture_repo(
                root,
                source,
                screen_path=lambda _path: (
                    False,
                    "path matches a configured withhold rule",
                ),
            )

            self.assertEqual(error, "")
            self.assertEqual(record["files"], 0)
            self.assertEqual(record["bytes"], 0)
            self.assertEqual(record["gitlinks"], [])
            self.assertEqual(record["withheld"], [{
                "file": "private-notes/dependency",
                "reason": "path matches a configured withhold rule",
            }])
            self.assertFalse(
                (out / "repo" / "private-notes" / "dependency").exists()
            )

    def test_source_blob_error_fails_and_removes_partial_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            self.init_repo(source)
            (source / "a.txt").write_bytes(b"captured first")
            fragile = b"present in Git"
            (source / "fragile.txt").write_bytes(fragile)
            self.commit(source)
            out = root / "out"
            work = root / "work"
            work.mkdir()
            original_read = aggregate._GitBlobReader.read

            def fail_fragile(reader, oid, expected_size):
                raw = original_read(reader, oid, expected_size)
                if raw == fragile:
                    raise OSError("simulated source blob failure")
                return raw

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "run", self.local_run(source)),
                patch.object(
                    aggregate.ip_gate,
                    "screen",
                    lambda _raw, _path: (True, ""),
                ),
                patch.object(aggregate._GitBlobReader, "read", fail_fragile),
            ):
                record, error = aggregate.capture(
                    "owner", "repo", work, max_file_mb=2.0
                )

            self.assertIsNone(record)
            self.assertIn("cannot read Git blob at fragile.txt", error)
            self.assertFalse((out / "repo").exists())

    def test_public_inventory_paginates_to_count_without_private_inflation(self):
        first_page = [{
            "name": f"other-{index:03d}",
            "private": False,
            "archived": False,
        } for index in range(aggregate.REST_PAGE_SIZE)]
        second_page = [
            {"name": "rapp-final", "private": False, "archived": False},
            {"name": "rapp-monorepo", "private": False, "archived": False},
            {"name": "rapp-aibast-stage", "private": False, "archived": False},
            {"name": "rapp-shape-aibast", "private": False, "archived": False},
            {"name": "rapp-archived", "private": False, "archived": True},
        ]
        endpoints = []
        commands = []

        def fake_run(cmd, **_kwargs):
            self.assertEqual(cmd[:4], ["gh", "api", "--method", "GET"])
            commands.append(list(cmd))
            endpoint = cmd[-1]
            endpoints.append(endpoint)
            if endpoint == "/users/kody-w":
                payload = {"public_repos": len(first_page) + len(second_page)}
            elif "page=1&" in endpoint:
                payload = first_page
            elif "page=2&" in endpoint:
                payload = second_page
            else:
                raise AssertionError(f"unexpected endpoint: {endpoint}")
            return subprocess.CompletedProcess(
                cmd, 0, json.dumps(payload), ""
            )

        with patch.object(aggregate, "run", fake_run):
            names = aggregate.members("kody-w", "rapp-monorepo")

        self.assertEqual(names, ["rapp-aibast-stage", "rapp-final"])
        self.assertEqual(len(endpoints), 3)
        self.assertTrue(any("page=1&" in item for item in endpoints))
        self.assertTrue(any("page=2&" in item for item in endpoints))
        self.assertFalse(any("--limit" in cmd for cmd in commands))

    def test_public_inventory_rejects_incomplete_pagination(self):
        page = [{
            "name": f"repo-{index:03d}",
            "private": False,
            "archived": False,
        } for index in range(99)]

        def fake_run(cmd, **_kwargs):
            endpoint = cmd[-1]
            payload = {"public_repos": 100} if endpoint == "/users/kody-w" else page
            return subprocess.CompletedProcess(
                cmd, 0, json.dumps(payload), ""
            )

        with (
            patch.object(aggregate, "run", fake_run),
            self.assertRaisesRegex(RuntimeError, "pagination was incomplete"),
        ):
            aggregate.members("kody-w", "rapp-monorepo")

    def test_public_inventory_rejects_a_private_repository(self):
        responses = {
            "/users/kody-w": {"public_repos": 1},
            (
                "/users/kody-w/repos?per_page=100&page=1"
                "&sort=full_name&direction=asc"
            ): [{
                "name": "rapp-private",
                "private": True,
                "archived": False,
            }],
        }

        def fake_run(cmd, **_kwargs):
            return subprocess.CompletedProcess(
                cmd, 0, json.dumps(responses[cmd[-1]]), ""
            )

        with (
            patch.object(aggregate, "run", fake_run),
            self.assertRaisesRegex(RuntimeError, "non-public"),
        ):
            aggregate.members("kody-w", "rapp-monorepo")

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
                "gitlinks": [],
            }

            def fake_capture(_owner, repo, _work, _max_file_mb):
                if repo == "good":
                    return record, ""
                return None, "clone failed: unavailable"

            with (
                patch.object(aggregate, "OUT", out),
                patch.object(aggregate, "MANIFEST", manifest_path),
                patch.object(aggregate, "INDEX", index_path),
                patch.object(aggregate, "self_name", return_value="rapp-monorepo"),
                patch.object(aggregate.ip_gate, "assert_configured"),
                patch.object(
                    aggregate, "members", return_value=["good", "bad"]
                ),
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
            self.assertEqual(
                manifest["membership_exclusions"],
                {
                    "exclude_archived": True,
                    "repositories": [
                        {
                            "repo": "rapp-monorepo",
                            "reason_code": "snapshot-self-recursion",
                            "reason": (
                                "The aggregate repository cannot capture itself "
                                "without recursive, non-point-in-time content."
                            ),
                        },
                        {
                            "repo": "rapp-shape-aibast",
                            "reason_code": "non-organ-staging-repository",
                            "reason": (
                                "AIBAST library-layout shape staging is an "
                                "external delivery rehearsal, not a RAPP "
                                "organism organ."
                            ),
                        },
                    ],
                },
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
