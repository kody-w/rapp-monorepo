from __future__ import annotations

import copy
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


def _minimal_scope() -> dict:
    return {
        "owner": "kody-w",
        "membership": {
            "visibility": "public",
            "archived": False,
            "name_pattern": "(?i)^(rapp|RAR$|organ|safe)",
        },
        "deliberate_exclusions": [
            {
                "repository": "kody-w/rapp-monorepo",
                "reason_code": "snapshot-self-recursion",
                "reason": "test scope excludes recursive self-capture",
            }
        ],
    }


def _minimal_authority() -> dict:
    return {
        "normative_source_current": {
            "authority_role": "normative-protocol-authority",
            "repository": "kody-w/rapp-1",
            "repository_url": "https://example.invalid/rapp-1",
            "organ": "rapp-1",
            "snapshot_path": "repos/rapp-1/SPEC.md",
            "snapshot_commit": "0" * 40,
            "sha256": "0" * 64,
            "byte_length": 1,
        },
        "map_structural_pin": {},
        "target_structural_pin": {"commit": "0" * 40},
        "spine_pin_claim": {},
        "target_status": "unused",
        "owner_actions": "unused",
        "authenticated_registry": {
            "state": "absent",
            "is_section_13_registry": False,
        },
        "retired_public_target": {
            "repository": "kody-w/RAPP",
            "product_lifecycle": "retired",
            "target_record_currency": "current-but-drifted",
            "replacement_boundary": "test SDK",
            "protocol_authority": False,
            "may_redefine_rapp_1": False,
        },
    }


def _minimal_projection(projection_id: str) -> dict:
    is_map = projection_id == "map"
    organ = "rapp-map" if is_map else "rapp-spine"
    return {
        "schema": "rapp-projection-evidence/1.0",
        "id": projection_id,
        "organ": organ,
        "projection_type": (
            "owner-wide-observation-map"
            if is_map
            else "routing-and-foundation-index"
        ),
        "authority_kind": (
            "derived-observation"
            if is_map
            else "curated-generated-projection"
        ),
        "authority_scope": (
            "navigation-and-cartography-only"
            if is_map
            else "routing-and-navigation-only"
        ),
        "lifecycle": (
            "active-but-observation-stale" if is_map else "active-but-incomplete"
        ),
        "captured_commit": "0" * 40,
        "live_commit": "0" * 40,
        "live_evidence": "declared-cartographer-report-not-dynamically-fetched-by-sdk",
        "tracked_blobs": {"captured": 1, "live": 1},
        "coverage": (
            {
                "observed_owner_repositories": 1,
                "captured_organ_overlap": 1,
                "snapshot_organs_at_measurement": 1,
            }
            if is_map
            else {
                "modeled_organs": 1,
                "snapshot_organs_at_measurement": 1,
                "protocol_materials": {"unresolved": 0, "total": 1},
                "required_sources": {"unresolved": 0, "total": 1},
            }
        ),
        "observed_at": "2026-01-01T00:00:00Z" if is_map else None,
        "generated_artifact": f"repos/{organ}/generated.json",
        "generator": f"repos/{organ}/generate.py",
        "generated_from": [f"repos/{organ}/source.json"],
        "coverage_source": {
            "organ": organ,
            "path": "generated.json",
            "extractor": "members[].repo" if is_map else "graph.nodes[].repo",
            "evidence_kind": "recomputable-from-captured-artifact",
            "missing_reason": "not modeled by the test projection",
        },
    }


def _minimal_registry(*extra_organs: str) -> dict:
    systems = [
        {
            "id": "authority-contracts-navigation",
            "name": "Authority",
            "lifecycle": "mixed-snapshot",
            "authority": "classification grants no authority",
            "organs": ["rapp-1", "rapp-map", "rapp-spine"],
        }
    ]
    if extra_organs:
        systems.append(
            {
                "id": "unclassified-incubator",
                "name": "Test organs",
                "lifecycle": "unclassified-incubator",
                "authority": "none",
                "organs": list(extra_organs),
            }
        )
    return {
        "schema": "rapp-organism/1.0",
        "snapshot_schema": "rapp-monorepo/1.0",
        "estate_scope": _minimal_scope(),
        "authority": _minimal_authority(),
        "conformance": {
            "state": "not-fully-rapp-1-conformant",
            "full_conformance": False,
            "reason": "authenticated registry absent",
        },
        "systems": systems,
        "projections": [_minimal_projection("map"), _minimal_projection("spine")],
        "relationships": [
            {
                "type": "normative-authority",
                "from": "kody-w/rapp-1",
                "to": "rapp/1",
                "state": "current-user-designated-source",
            },
            {
                "type": "projection-of",
                "from": "map",
                "to": "captured-organism",
                "authority": False,
            },
            {
                "type": "projection-of",
                "from": "spine",
                "to": "captured-organism",
                "authority": False,
            },
            {
                "type": "structural-pin-for-stale-target",
                "from": "kody-w/RAPP",
                "to": f"kody-w/rapp-1@{'0' * 40}",
                "current_normative_bytes": False,
            },
        ],
        "alignment_conflicts": [
            {
                "id": "test-conflict",
                "type": "authority-pin-conflict",
                "evidence_mode": "validated-local-records",
                "evidence_paths": ["repos/rapp-1/SPEC.md"],
            }
        ],
    }


def _manifest_record(name: str) -> dict:
    return {
        "repo": name,
        "commit": "0" * 40,
        "files": 0,
        "bytes": 0,
        "skipped_large": [],
        "withheld": [],
    }


def _minimal_manifest(*extra_organs: str) -> dict:
    return {
        "schema": "rapp-monorepo/1.0",
        "owner": "kody-w",
        "membership_pattern": "(?i)^(rapp|RAR$|organ|safe)",
        "repos": [
            _manifest_record(name)
            for name in ("rapp-1", "rapp-map", "rapp-spine", *extra_organs)
        ],
        "not_captured": [],
    }


def _write_minimal_root(
    root: Path,
    *,
    manifest: dict | None = None,
    registry: dict | None = None,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "MANIFEST.json").write_text(
        json.dumps(manifest or _minimal_manifest("organ"))
    )
    (root / "ORGANISM.json").write_text(
        json.dumps(registry or _minimal_registry("organ"))
    )


def _captured_repo_stats(root: Path) -> tuple[int, int]:
    files = 0
    byte_length = 0
    for directory, child_directories, child_files in os.walk(
        root, followlinks=False
    ):
        directory_path = Path(directory)
        for name in list(child_directories):
            path = directory_path / name
            if path.is_symlink():
                status = path.lstat()
                files += 1
                byte_length += status.st_size
                child_directories.remove(name)
        for name in child_files:
            status = (directory_path / name).lstat()
            files += 1
            byte_length += status.st_size
    return files, byte_length


def test_inventory_taxonomy_is_complete() -> None:
    organism = Organism(ROOT)
    assert organism.statistics.repositories == len(organism.manifest["repos"])
    captured_names = {
        item.name
        for item in (ROOT / "repos").iterdir()
        if item.is_dir() and not item.is_symlink()
    }
    assert captured_names == set(organism.repository_names)
    captured_files = 0
    captured_bytes = 0
    for record in organism.manifest["repos"]:
        stats = _captured_repo_stats(ROOT / "repos" / record["repo"])
        assert stats == (record["files"], record["bytes"])
        captured_files += stats[0]
        captured_bytes += stats[1]
    assert organism.statistics.files == captured_files
    assert organism.statistics.bytes == captured_bytes
    assert organism.drift == {"manifest_only": [], "taxonomy_only": []}
    organs = organism.organs()
    assert len(organs) == len({organ["repo"] for organ in organs})
    assert all(organ["system"] for organ in organs)
    assert all(organ["system_lifecycle"] for organ in organs)
    assert all(organ["system_authority"] for organ in organs)
    assert organism.organ("rapp-1")["system"] == "authority-contracts-navigation"
    exclusions = {
        item["repository"]: item
        for item in organism.registry["estate_scope"]["deliberate_exclusions"]
    }
    assert exclusions["kody-w/rapp-shape-aibast"]["reason_code"] == (
        "non-organ-staging-repository"
    )
    assert "rapp-shape-aibast" not in organism.repository_names
    authority = organism.authority_paths
    assert authority["normative_source_current"]["sha256"].startswith("cea7847f")
    assert authority["map_structural_pin"]["matches_normative_source_current_bytes"]
    assert not authority["target_structural_pin"]["matches_normative_source_current_bytes"]
    assert not authority["spine_pin_claim"]["commits_equal"]


def test_architecture_registry_rejects_false_or_vacuous_contracts() -> None:
    scratch = ROOT / "tests" / f".architecture-{uuid.uuid4().hex}"

    def rejected(mutator, match: str) -> None:
        registry = _minimal_registry("organ")
        mutator(registry)
        _write_minimal_root(scratch, registry=registry)
        with pytest.raises(InventoryError, match=match):
            Organism(scratch)

    try:
        rejected(
            lambda registry: registry["conformance"].update(
                {
                    "state": "fully-rapp-1-conformant",
                    "full_conformance": True,
                }
            ),
            "non-conformance",
        )
        rejected(
            lambda registry: registry["systems"][0].update(
                {"lifecycle": "whatever-is-current"}
            ),
            "constrained vocabulary",
        )
        rejected(
            lambda registry: registry["authority"]["retired_public_target"].update(
                {"product_lifecycle": "active"}
            ),
            "product lifecycle",
        )
        rejected(
            lambda registry: registry["estate_scope"].update(
                {"deliberate_exclusions": []}
            ),
            "deliberate_exclusions must be non-empty",
        )
        rejected(lambda registry: registry.update({"projections": []}), "non-empty")
        rejected(
            lambda registry: registry.update(
                {"projections": [registry["projections"][0]]}
            ),
            "both Map and Spine",
        )
        rejected(
            lambda registry: registry["projections"][0].update(
                {"generated_from": []}
            ),
            "generator provenance",
        )
        rejected(
            lambda registry: registry["projections"][0].update(
                {
                    "authority_kind": "normative-protocol-authority",
                    "authority_scope": "full-rapp-1-authority",
                }
            ),
            "subordinate contract",
        )
        rejected(
            lambda registry: registry["projections"][0].update(
                {"observed_at": "not-a-date"}
            ),
            "UTC timestamp",
        )
        rejected(
            lambda registry: registry["projections"][1]["coverage"].update(
                {"protocol_materials": {}}
            ),
            "unresolved coverage",
        )
        rejected(lambda registry: registry.update({"relationships": []}), "non-empty")
        rejected(
            lambda registry: registry["relationships"][1].update(
                {"authority": True}
            ),
            "one-way authority contract",
        )
        rejected(
            lambda registry: registry.update({"alignment_conflicts": []}),
            "non-empty",
        )

        def move_normative_source(registry: dict) -> None:
            registry["systems"][0]["organs"].remove("rapp-1")
            registry["systems"][1]["organs"].append("rapp-1")

        rejected(move_normative_source, "authority-contracts-navigation")
        with pytest.raises(InventoryError, match="allow_drift must be a boolean"):
            Organism(ROOT, allow_drift=1)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


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
    assert report.target_product_lifecycle == "retired"
    assert report.target_record_currency == "current-but-drifted"
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
            json.dumps(_minimal_manifest("organ"))
        )
        (scratch / "ORGANISM.json").write_text(
            json.dumps(_minimal_registry("organ"))
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
        manifest = _minimal_manifest("safe")
        registry = _minimal_registry()
        (scratch / "MANIFEST.json").write_text(json.dumps(manifest))
        (scratch / "ORGANISM.json").write_text(json.dumps(registry))
        with pytest.raises(InventoryError, match="manifest/taxonomy sets differ"):
            Organism(scratch)
        reporting = Organism(scratch, allow_drift=True)
        assert reporting.drift == {"manifest_only": ["safe"], "taxonomy_only": []}
        assert reporting.summary()["architecture_drift"]["manifest_only"] == ["safe"]
        alignment = inspect_alignment(str(scratch)).as_dict()
        assert alignment["taxonomy_drift"]["manifest_only"] == ["safe"]
        assert all(
            projection["coverage_evidence"]["state"] == "not-recomputed"
            for projection in alignment["projections"]
        )
        with pytest.raises(SpecimenAccessError, match="equality"):
            SafeSpecimen(reporting)
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
        assert reported["organism"]["architecture_drift"]["manifest_only"] == [
            "safe"
        ]
        assert (
            reported["authority_report"]["state"]
            == "unavailable-safe-access-refused"
        )
        next(item for item in manifest["repos"] if item["repo"] == "safe")["repo"] = (
            "../escape"
        )
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
    assert report["semantics"]["coverage"].startswith(
        "recomputed-from-captured-artifact"
    )
    assert report["semantics"]["generator_derivation"].startswith("not-performed")
    projections = {item["id"]: item for item in report["projections"]}
    assert projections["map"]["freshness"]["state"] == "stale"
    assert projections["spine"]["freshness"]["state"] == "unknown"
    assert projections["map"]["daily_checks"]["captured_commit_matches_manifest"]
    assert projections["spine"]["daily_checks"]["captured_commit_matches_manifest"]
    for projection in projections.values():
        checks = projection["daily_checks"]
        assert checks["generator_provenance_paths_present"]
        assert not checks["generator_provenance_complete"]
        assert checks["generator_derivation_check"].startswith("not-performed")
    manifest_names = set(organism.repository_names)
    map_source = json.loads((ROOT / "repos/rapp-map/estate-map.json").read_text())
    map_source_names = {
        item["repo"].removeprefix("kody-w/") for item in map_source["members"]
    }
    spine_source = json.loads((ROOT / "repos/rapp-spine/crawl.json").read_text())
    spine_source_names = {
        item["repo"].removeprefix("kody-w/")
        for item in spine_source["graph"]["nodes"]
        if "repo" in item
    }
    expected_missing = {
        "map": sorted(manifest_names - map_source_names),
        "spine": sorted(manifest_names - spine_source_names),
    }
    for projection_id, expected in expected_missing.items():
        evidence = projections[projection_id]["coverage_evidence"]
        assert evidence["state"] == "recomputed-from-captured-artifact"
        assert evidence["declared_count_matches_recomputed"]
        assert evidence["missing_organ_count"] == len(expected)
        assert [item["organ"] for item in evidence["missing_organs"]] == expected
        assert all(item["reason"] for item in evidence["missing_organs"])
    assert projections["map"]["coverage_evidence"]["missing_organ_count"] == 45
    assert projections["spine"]["coverage_evidence"]["missing_organ_count"] == 155
    assert {item["type"] for item in report["active_legacy_claims"]} == {
        "legacy-frame-claim",
        "legacy-egg-claim",
        "legacy-wire-claim",
    }


def test_alignment_labels_coverage_that_cannot_be_recomputed(monkeypatch) -> None:
    def unavailable(*args, **kwargs):
        raise SpecimenAccessError("forced unavailable evidence")

    monkeypatch.setattr(SafeSpecimen, "read_bytes", unavailable)
    report = inspect_alignment(str(ROOT)).as_dict()
    for projection in report["projections"]:
        evidence = projection["coverage_evidence"]
        assert evidence["state"] == "not-recomputed"
        assert "forced unavailable evidence" in evidence["reason"]
        assert evidence["missing_organs"] is None


def test_cli_status_smoke() -> None:
    implicit_root = subprocess.run(
        [sys.executable, "-m", "rapp_sdk", "--json", "status"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert implicit_root.returncode == 2
    assert "--root is required" in implicit_root.stderr

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
    assert value["authority_report"]["target_structural_pin"][
        "product_lifecycle"
    ] == "retired"
    assert value["authority_report"]["target_structural_pin"][
        "record_currency"
    ] == "current-but-drifted"
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
