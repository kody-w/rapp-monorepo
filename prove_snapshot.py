#!/usr/bin/env python3
"""Prove the staged Git tree exactly matches the generated snapshot contract."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_snapshot import (
    MANIFEST_INTEGRITY_PROFILE,
    MANIFEST_MIGRATION_ONLY_PROFILE,
    MANIFEST_SCHEMA,
    SnapshotVerificationError,
    compute_tree_sha256,
    render_gitmodules,
    render_index,
    stage_and_verify,
    verify_staged,
)

GITLINK_URL = "https://example.invalid/dependency.git"
DEFAULT_MEMBERSHIP_EXCLUSIONS = object()


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
        self.membership_exclusions = {
            "exclude_archived": True,
            "repositories": [{
                "repo": "demo-excluded",
                "reason_code": "fixture-exclusion",
                "reason": "test-only named exclusion",
            }],
        }
        (self.root / "ORGANISM.json").write_text(
            json.dumps({
                "estate_scope": {
                    "owner": "test-owner",
                    "membership": {
                        "visibility": "public",
                        "archived": False,
                        "name_pattern": "^demo",
                    },
                    "deliberate_exclusions": [{
                        "repository": "test-owner/demo-excluded",
                        "reason_code": "fixture-exclusion",
                        "reason": "test-only named exclusion",
                    }],
                },
            }),
            encoding="utf-8",
        )
        self.git("add", "-f", "--", "ORGANISM.json")

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
        skipped_large=None,
        withheld=None,
        membership_exclusions=DEFAULT_MEMBERSHIP_EXCLUSIONS,
        gitlinks=None,
    ):
        link_entries = [
            (item["path"], "160000", bytes.fromhex(item["commit"]))
            for item in (gitlinks or [])
        ]
        digest_entries = [*entries, *link_entries]
        total_bytes = sum(len(raw) for _, _, raw in digest_entries)
        record = {
            "repo": "demo",
            "commit": "a" * 40,
            "committed_at": "2026-08-21T00:00:00+00:00",
            "captured_at": "2026-08-21T00:00:00+00:00",
            "files": len(digest_entries),
            "bytes": total_bytes,
            "tree_sha256": compute_tree_sha256(digest_entries),
            "skipped_large": skipped_large or [],
            "withheld": withheld or [],
        }
        if gitlinks is not None:
            record["gitlinks"] = gitlinks
        manifest = {
            "schema": schema,
            "integrity_profile": integrity_profile,
            "owner": "test-owner",
            "captured_at": "2026-08-21T00:00:00+00:00",
            "membership_pattern": "^demo",
            "max_file_mb": 2.0,
            "repos": [record],
            "not_captured": not_captured or [],
        }
        if membership_exclusions is DEFAULT_MEMBERSHIP_EXCLUSIONS:
            membership_exclusions = self.membership_exclusions
        if membership_exclusions is not None:
            manifest["membership_exclusions"] = membership_exclusions
        (self.root / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "INDEX.md").write_text(
            render_index(manifest),
            encoding="utf-8",
        )
        gitmodules_path = self.root / ".gitmodules"
        gitmodules_path.unlink(missing_ok=True)
        root_gitmodules = render_gitmodules(manifest)
        if root_gitmodules:
            gitmodules_path.write_text(
                root_gitmodules,
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

    def test_gitlink_is_raw_staged_without_target_or_object(self):
        commit = "1" * 40
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": commit,
                "url": GITLINK_URL,
            }],
        )
        expected_gitmodules = (self.root / ".gitmodules").read_bytes()
        attributes = self.root / ".git" / "info" / "attributes"
        attributes.parent.mkdir(parents=True, exist_ok=True)
        attributes.write_bytes(b".gitmodules text eol=crlf\n")

        summary = stage_and_verify(self.root)

        mode, oid, _stage_path = self.git(
            "ls-files",
            "--stage",
            "--",
            "repos/demo/vendor/dependency",
        ).stdout.split(maxsplit=2)
        self.assertEqual((mode, oid), ("160000", commit))
        self.assertEqual(summary["files"], 1)
        self.assertEqual(summary["bytes"], len(bytes.fromhex(commit)))
        self.assertFalse(
            (self.root / "repos" / "demo" / "vendor" / "dependency").exists()
        )
        self.assertNotEqual(
            self.git("cat-file", "-e", commit, check=False).returncode,
            0,
        )
        index = (self.root / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("`demo/vendor/dependency`", index)
        self.assertIn(f"`{commit}`", index)
        self.assertIn(f"`{GITLINK_URL}`", index)
        root_gitmodules = (self.root / ".gitmodules").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'path = "repos/demo/vendor/dependency"',
            root_gitmodules,
        )
        self.assertIn(f'url = "{GITLINK_URL}"', root_gitmodules)
        staged_gitmodules = subprocess.check_output([
            "git",
            "-C",
            str(self.root),
            "show",
            ":.gitmodules",
        ])
        self.assertEqual(staged_gitmodules, expected_gitmodules)
        self.assertEqual(
            root_gitmodules.encode(),
            expected_gitmodules,
        )
        cleanup = self.git(
            "submodule",
            "foreach",
            "--recursive",
            "true",
            check=False,
        )
        self.assertEqual(cleanup.returncode, 0, cleanup.stderr)
        self.assertNotIn("No url found", cleanup.stderr)

    def test_manifest_rejects_unsafe_gitlink_paths(self):
        for path in ("safe\n- forged", "vendor/\udcff"):
            with (
                self.subTest(path=repr(path)),
                self.assertRaisesRegex(
                    SnapshotVerificationError,
                    "path/commit/url",
                ),
            ):
                self.write_manifest(
                    [],
                    gitlinks=[{
                        "path": path,
                        "commit": "1" * 40,
                        "url": GITLINK_URL,
                    }],
                )

    def test_root_gitmodules_rendering_is_deterministic(self):
        links = [
            {
                "path": "zeta/dependency",
                "commit": "a" * 40,
                "url": "https://example.invalid/zeta.git",
            },
            {
                "path": "alpha/dependency",
                "commit": "b" * 40,
                "url": "ssh://git@example.invalid/alpha.git",
            },
        ]
        self.write_manifest([], gitlinks=links)
        first = (self.root / ".gitmodules").read_bytes()

        self.write_manifest([], gitlinks=list(reversed(links)))
        second = (self.root / ".gitmodules").read_bytes()

        self.assertEqual(first, second)
        self.assertEqual(first.count(b'[submodule "snapshot-'), 2)
        self.assertLess(
            first.index(b"repos/demo/alpha/dependency"),
            first.index(b"repos/demo/zeta/dependency"),
        )

    def test_root_gitmodules_uses_safe_sections_and_escaped_paths(self):
        path = 'vendor/quoted"name\\part'
        self.write_manifest(
            [],
            gitlinks=[{
                "path": path,
                "commit": "e" * 40,
                "url": GITLINK_URL,
            }],
        )

        parsed = self.git(
            "config",
            "--file",
            str(self.root / ".gitmodules"),
            "--get-regexp",
            r"^submodule\..*\.path$",
        ).stdout.strip()
        key, value = parsed.split(" ", 1)

        self.assertRegex(
            key,
            r"^submodule\.snapshot-[0-9a-f]{64}\.path$",
        )
        self.assertEqual(value, f"repos/demo/{path}")

    def test_verifier_rejects_gitmodules_projection_mismatch(self):
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": "c" * 40,
                "url": GITLINK_URL,
            }],
        )
        stage_and_verify(self.root)
        (self.root / ".gitmodules").write_text(
            '[submodule "forged"]\n'
            '\tpath = "repos/demo/vendor/dependency"\n'
            '\turl = "https://example.invalid/forged.git"\n',
            encoding="utf-8",
        )
        self.git("add", "-f", "--", ".gitmodules")

        with self.assertRaisesRegex(
            SnapshotVerificationError,
            "not the deterministic manifest projection",
        ):
            verify_staged(self.root)

    def test_gitlinks_require_root_gitmodules(self):
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": "d" * 40,
                "url": GITLINK_URL,
            }],
        )
        (self.root / ".gitmodules").unlink()

        with self.assertRaisesRegex(
            SnapshotVerificationError,
            "require staged root .gitmodules",
        ):
            stage_and_verify(self.root)

    def test_stale_root_gitmodules_is_rejected_without_gitlinks(self):
        self.write_manifest([])
        (self.root / ".gitmodules").write_text(
            '[submodule "stale"]\n'
            '\tpath = "repos/demo/stale"\n'
            f'\turl = "{GITLINK_URL}"\n',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError,
            "manifest has no gitlinks",
        ):
            stage_and_verify(self.root)

    def test_verifier_rejects_a_missing_manifest_gitlink(self):
        commit = "2" * 40
        path = "repos/demo/vendor/dependency"
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": commit,
                "url": GITLINK_URL,
            }],
        )
        stage_and_verify(self.root)
        self.git("update-index", "--force-remove", "--", path)

        with self.assertRaisesRegex(
            SnapshotVerificationError, "gitlink is missing.*vendor/dependency"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_an_extra_staged_gitlink(self):
        commit = "3" * 40
        self.write_manifest([])
        stage_and_verify(self.root)
        self.git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{commit},repos/demo/extra",
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError, "extra staged gitlink.*extra"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_a_wrong_gitlink_oid(self):
        expected = "4" * 40
        actual = "5" * 40
        path = "repos/demo/vendor/dependency"
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": expected,
                "url": GITLINK_URL,
            }],
        )
        stage_and_verify(self.root)
        self.git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{actual},{path}",
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError, "gitlink.*OID.*!= manifest OID"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_a_wrong_gitlink_mode(self):
        commit = "6" * 40
        path = self.root / "repos" / "demo" / "vendor" / "dependency"
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": commit,
                "url": GITLINK_URL,
            }],
        )
        stage_and_verify(self.root)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not a gitlink\n")
        self.git("add", "-f", "--", "repos/demo/vendor/dependency")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "has mode 100644, expected 160000"
        ):
            verify_staged(self.root)

    def test_manifest_rejects_a_gitlink_declared_omitted(self):
        commit = "7" * 40
        with self.assertRaisesRegex(
            SnapshotVerificationError, "gitlink is also declared omitted"
        ):
            self.write_manifest(
                [],
                gitlinks=[{
                    "path": "vendor/dependency",
                    "commit": commit,
                    "url": GITLINK_URL,
                }],
                withheld=[{
                    "file": "vendor/dependency",
                    "reason": "matches configured path rule",
                }],
            )

    def test_staging_rejects_materialized_gitlink_target_content(self):
        commit = "9" * 40
        target = (
            self.root
            / "repos"
            / "demo"
            / "vendor"
            / "dependency"
            / "target.txt"
        )
        target.parent.mkdir(parents=True)
        target.write_bytes(b"must not be copied\n")
        self.write_manifest(
            [],
            gitlinks=[{
                "path": "vendor/dependency",
                "commit": commit,
                "url": GITLINK_URL,
            }],
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError, "collides with materialized path"
        ):
            stage_and_verify(self.root)

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

    def test_verifier_rejects_a_staged_path_declared_withheld(self):
        payload = b"must not travel\n"
        path = self.root / "repos" / "demo" / "secret.txt"
        path.write_bytes(payload)
        self.write_manifest(
            [("secret.txt", "100644", payload)],
            withheld=[{
                "file": "secret.txt",
                "reason": "matches configured content rule 1",
            }],
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError, "declared omitted.*secret.txt"
        ):
            stage_and_verify(self.root)

    def test_verifier_rejects_a_staged_path_declared_too_large(self):
        payload = b"must not travel\n"
        path = self.root / "repos" / "demo" / "large.bin"
        path.write_bytes(payload)
        self.write_manifest(
            [("large.bin", "100644", payload)],
            skipped_large=["large.bin (3.0MB)"],
        )

        with self.assertRaisesRegex(
            SnapshotVerificationError, "declared omitted.*large.bin"
        ):
            stage_and_verify(self.root)

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

    def test_verifier_accepts_recorded_membership_exclusions(self):
        self.write_manifest(
            [],
            membership_exclusions=self.membership_exclusions,
        )

        summary = stage_and_verify(self.root)

        self.assertEqual(summary["repos"], 1)

    def test_current_profile_requires_membership_exclusions(self):
        self.write_manifest([], membership_exclusions=None)

        with self.assertRaisesRegex(
            SnapshotVerificationError, "require membership_exclusions"
        ):
            stage_and_verify(self.root)

    def test_verifier_rejects_membership_contract_drift(self):
        self.write_manifest(
            [],
            membership_exclusions={
                "exclude_archived": True,
                "repositories": [{
                    "repo": "demo-other",
                    "reason_code": "fixture-exclusion",
                    "reason": "not the reviewed exclusion",
                }],
            },
        )
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "differs from staged ORGANISM"
        ):
            verify_staged(self.root)

    def test_verifier_rejects_a_legacy_manifest_without_integrity_profile(self):
        self.write_manifest([], integrity_profile=None)
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "migration-only"
        ):
            verify_staged(self.root)

    def test_migration_only_manifest_cannot_publish(self):
        self.write_manifest(
            [],
            integrity_profile=MANIFEST_MIGRATION_ONLY_PROFILE,
        )
        self.git("add", "-A", "--", "MANIFEST.json", "INDEX.md")

        with self.assertRaisesRegex(
            SnapshotVerificationError, "migration-only.*cannot be published"
        ):
            verify_staged(self.root)

    def test_verifier_binds_scope_to_staged_organism(self):
        self.write_manifest([])
        expected = stage_and_verify(self.root)
        organism = json.loads(
            (self.root / "ORGANISM.json").read_text(encoding="utf-8")
        )
        organism["estate_scope"]["membership"]["name_pattern"] = "^other"
        organism["estate_scope"]["deliberate_exclusions"] = [{
            "repository": "test-owner/other-excluded",
            "reason_code": "other-exclusion",
            "reason": "divergent worktree contract",
        }]
        (self.root / "ORGANISM.json").write_text(
            json.dumps(organism),
            encoding="utf-8",
        )

        self.assertEqual(verify_staged(self.root), expected)

        self.git("add", "-f", "--", "ORGANISM.json")
        with self.assertRaisesRegex(
            SnapshotVerificationError,
            "differs from staged ORGANISM",
        ):
            verify_staged(self.root)

    def test_verifier_requires_staged_organism_metadata(self):
        self.write_manifest([])
        stage_and_verify(self.root)
        self.git("rm", "--cached", "-q", "--", "ORGANISM.json")

        with self.assertRaisesRegex(
            SnapshotVerificationError,
            "required snapshot metadata.*ORGANISM",
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
