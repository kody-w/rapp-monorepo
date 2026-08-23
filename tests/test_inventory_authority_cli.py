from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

import pytest

from rapp_sdk.alignment import inspect_alignment
from rapp_sdk.authority import inspect_authority
from rapp_sdk.errors import InventoryError, SpecimenAccessError
from rapp_sdk.inventory import Organism, SafeSpecimen

ROOT = Path(__file__).resolve().parents[1]


def _minimal_authority() -> dict:
    return {
        "normative_source_current": {
            "authority_role": "normative-protocol-authority",
            "repository": "kody-w/rapp-1",
            "repository_url": "https://example.invalid/rapp-1",
            "sha256": "0" * 64,
            "byte_length": 0,
        },
        "map_structural_pin": {},
        "target_structural_pin": {},
        "spine_pin_claim": {},
        "target_status": "unused",
        "owner_actions": "unused",
        "authenticated_registry": {
            "state": "absent",
            "is_section_13_registry": False,
        },
        "retired_public_target": {},
    }


def test_inventory_taxonomy_is_complete() -> None:
    organism = Organism(ROOT)
    assert organism.statistics.repositories == len(organism.manifest["repos"])
    assert organism.statistics.files == sum(item["files"] for item in organism.manifest["repos"])
    assert organism.statistics.bytes == sum(item["bytes"] for item in organism.manifest["repos"])
    assert organism.drift == {"manifest_only": [], "taxonomy_only": []}
    organs = organism.organs()
    assert len(organs) == len({organ["repo"] for organ in organs})
    assert all(organ["system"] for organ in organs)
    authority = organism.authority_paths
    assert authority["normative_source_current"]["sha256"].startswith("cea7847f")
    assert authority["map_structural_pin"]["matches_normative_source_current_bytes"]
    assert not authority["target_structural_pin"]["matches_normative_source_current_bytes"]
    assert not authority["spine_pin_claim"]["commits_equal"]


def test_authority_reports_exact_snapshot_mismatch_and_blockers() -> None:
    report = inspect_authority(str(ROOT))
    assert report.normative_repository == "kody-w/rapp-1"
    assert report.normative_repository_url == "https://github.com/kody-w/rapp-1"
    assert report.normative_source_commit == "afc913ca3fe7dbc9da97871e67240f34416e5929"
    assert report.normative_source_state == "available-current-designated-source"
    assert report.normative_source_byte_length == 41952
    assert report.normative_source_sha256 == (
        "cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a"
    )
    assert report.map_pin_valid and report.map_pin_matches_current
    assert report.map_pin_commit == "d2cd5abed48d3f52b86bbb975ac3558286d1db41"
    assert report.target_pin_valid
    assert report.target_pin_state == "structurally-valid-for-target-but-drifted"
    assert report.spine_observed_pin == "6723c7add2aed36bb68992fc71a56b0a4bd5ad81"
    assert not report.spine_pin_equals_map_current
    assert report.authenticated_registry == "absent"
    assert "owner-publish-authenticated-registry" in report.owner_action_blockers
    assert not report.full_conformance


def test_safe_specimen_refuses_traversal_absolute_directories_and_symlinks() -> None:
    specimen = SafeSpecimen(Organism(ROOT))
    with pytest.raises(SpecimenAccessError):
        specimen.read_bytes("RAPP", "../rapp-1/SPEC.md")
    with pytest.raises(SpecimenAccessError):
        specimen.read_bytes("RAPP", "/etc/passwd")
    with pytest.raises(SpecimenAccessError):
        specimen.read_bytes("RAPP", "tests")

    scratch = ROOT / "tests" / f".specimen-{uuid.uuid4().hex}"
    try:
        (scratch / "repos" / "organ").mkdir(parents=True)
        (scratch / "MANIFEST.json").write_text(
            json.dumps(
                {
                    "schema": "rapp-monorepo/1.0",
                    "repos": [
                        {
                            "repo": "organ",
                            "commit": "0" * 40,
                            "files": 1,
                            "bytes": 1,
                            "skipped_large": [],
                            "withheld": [],
                        }
                    ],
                    "not_captured": [],
                }
            )
        )
        (scratch / "ORGANISM.json").write_text(
            json.dumps(
                {
                    "schema": "rapp-organism/1.0",
                    "snapshot_schema": "rapp-monorepo/1.0",
                    "authority": _minimal_authority(),
                    "conformance": {},
                    "systems": [
                        {
                            "id": "test",
                            "name": "test",
                            "lifecycle": "test",
                            "authority": "none",
                            "organs": ["organ"],
                        }
                    ],
                    "projections": [],
                    "relationships": [],
                    "alignment_conflicts": [],
                }
            )
        )
        (scratch / "repos" / "organ" / "target").write_text("x")
        os.symlink("target", scratch / "repos" / "organ" / "link")
        local = SafeSpecimen(Organism(scratch))
        with pytest.raises(SpecimenAccessError, match="symlink"):
            local.read_bytes("organ", "link")
        assert local.readlink("organ", "link") == "target"
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_specimen_fails_closed_without_no_follow_primitives(monkeypatch) -> None:
    specimen = SafeSpecimen(Organism(ROOT))
    monkeypatch.delattr(os, "O_NOFOLLOW")
    with pytest.raises(SpecimenAccessError, match="lacks descriptor-relative"):
        specimen.read_bytes("rapp-1", "SPEC.md")


def test_specimen_read_bounds_and_short_reads_fail_closed(monkeypatch) -> None:
    specimen = SafeSpecimen(Organism(ROOT))
    for invalid in (-1, True, 1.5):
        with pytest.raises(SpecimenAccessError, match="non-negative integer"):
            specimen.read_bytes("rapp-1", "SPEC.md", max_bytes=invalid)
    monkeypatch.setattr(os, "read", lambda descriptor, count: b"")
    with pytest.raises(SpecimenAccessError, match="short read"):
        specimen.read_bytes("rapp-1", "SPEC.md")


def test_organ_names_and_taxonomy_equality_gate_safe_access() -> None:
    scratch = ROOT / "tests" / f".organ-{uuid.uuid4().hex}"
    try:
        (scratch / "repos" / "safe").mkdir(parents=True)
        manifest = {
            "schema": "rapp-monorepo/1.0",
            "repos": [
                {
                    "repo": "safe",
                    "commit": "0" * 40,
                    "files": 0,
                    "bytes": 0,
                    "skipped_large": [],
                    "withheld": [],
                }
            ],
            "not_captured": [],
        }
        registry = {
            "schema": "rapp-organism/1.0",
            "snapshot_schema": "rapp-monorepo/1.0",
            "authority": _minimal_authority(),
            "conformance": {},
            "systems": [
                {
                    "id": "test",
                    "name": "test",
                    "lifecycle": "test",
                    "authority": "none",
                    "organs": [],
                }
            ],
            "projections": [],
            "relationships": [],
            "alignment_conflicts": [],
        }
        (scratch / "MANIFEST.json").write_text(json.dumps(manifest))
        (scratch / "ORGANISM.json").write_text(json.dumps(registry))
        with pytest.raises(SpecimenAccessError, match="equality"):
            SafeSpecimen(Organism(scratch))
        status = subprocess.run(
            [
                sys.executable,
                "-m",
                "rapp_sdk",
                "--root",
                str(scratch),
                "--json",
                "status",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert status.returncode == 0, status.stderr
        reported = json.loads(status.stdout)
        assert reported["organism"]["architecture_drift"]["manifest_only"] == ["safe"]
        assert (
            reported["authority_report"]["state"]
            == "unavailable-safe-access-refused"
        )
        manifest["repos"][0]["repo"] = "../escape"
        (scratch / "MANIFEST.json").write_text(json.dumps(manifest))
        with pytest.raises(InventoryError, match="organ name"):
            Organism(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_alignment_report_labels_declared_evidence_and_daily_drift() -> None:
    organism = Organism(ROOT)
    report = inspect_alignment(
        str(ROOT),
        now=datetime(2026, 8, 23, tzinfo=timezone.utc),
    ).as_dict()
    assert report["snapshot_organs"] == len(organism.repository_names)
    assert report["semantics"]["live_state"].startswith("declared-cartographer")
    projections = {item["id"]: item for item in report["projections"]}
    assert projections["map"]["freshness"]["state"] == "stale"
    assert projections["spine"]["freshness"]["state"] == "unknown"
    assert projections["map"]["daily_checks"]["captured_commit_matches_manifest"]
    assert projections["spine"]["daily_checks"]["captured_commit_matches_manifest"]
    assert projections["map"]["daily_checks"]["generator_provenance_complete"]
    assert projections["spine"]["daily_checks"]["generator_provenance_complete"]
    assert {item["type"] for item in report["active_legacy_claims"]} == {
        "legacy-frame-claim",
        "legacy-egg-claim",
        "legacy-wire-claim",
    }


def test_cli_status_smoke() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rapp_sdk",
            "--root",
            str(ROOT),
            "--json",
            "status",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert value["trust"]["full_conformance"] is False
    current = value["authority_report"]["normative_source_current"]
    assert current == {
        "repository": "kody-w/rapp-1",
        "url": "https://github.com/kody-w/rapp-1",
        "snapshot_commit": "afc913ca3fe7dbc9da97871e67240f34416e5929",
        "state": "available-current-designated-source",
        "sha256": "cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a",
        "byte_length": 41952,
        "stale_target_may_redefine": False,
    }
    assert value["authority_report"]["map_structural_pin"][
        "matches_normative_source_current_bytes"
    ]
    assert value["authority_report"]["target_structural_pin"]["state"] == (
        "structurally-valid-for-target-but-drifted"
    )
    assert not value["authority_report"]["spine_pin_claim"]["commits_equal"]

    alignment = subprocess.run(
        [
            sys.executable,
            "-m",
            "rapp_sdk",
            "--root",
            str(ROOT),
            "--json",
            "alignment",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert alignment.returncode == 0, alignment.stderr
    alignment_value = json.loads(alignment.stdout)
    assert alignment_value["active_legacy_claims"]
    assert alignment_value["semantics"]["authenticated_acceptance"] is False
