"""Evidence-labeled Map/Spine alignment reporting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .inventory import Organism, SafeSpecimen
from .json_profile import strict_loads


@dataclass(frozen=True)
class AlignmentReport:
    generated_at: str
    snapshot_organs: int
    taxonomy_drift: dict[str, list[str]]
    projections: tuple[dict[str, Any], ...]
    conflicts: tuple[dict[str, Any], ...]
    relationships: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        legacy_types = {"legacy-frame-claim", "legacy-egg-claim", "legacy-wire-claim"}
        return {
            "semantics": {
                "live_state": "declared-cartographer-evidence-not-dynamically-fetched",
                "conflicts": "validated records or evidence-backed declared findings",
                "coverage": (
                    "recomputed-from-captured-artifact-or-explicitly-not-recomputed"
                ),
                "component_coverage": (
                    "manifest-derived-captured-files-versus-all-omitted-blobs"
                ),
                "generator_derivation": (
                    "not-performed-captured-code-is-never-executed"
                ),
                "authenticated_acceptance": False,
            },
            "generated_at": self.generated_at,
            "snapshot_organs": self.snapshot_organs,
            "taxonomy_drift": self.taxonomy_drift,
            "projections": list(self.projections),
            "generator_provenance": [
                {
                    "projection": item["id"],
                    "artifact": item["generated_artifact"],
                    "generator": item["generator"],
                    "generated_from": item["generated_from"],
                    "input_paths_present": item["daily_checks"][
                        "generator_provenance_paths_present"
                    ],
                    "derivation_check": item["daily_checks"][
                        "generator_derivation_check"
                    ],
                }
                for item in self.projections
            ],
            "active_legacy_claims": [
                item for item in self.conflicts if item["type"] in legacy_types
            ],
            "authority_pin_conflicts": [
                item for item in self.conflicts if item["type"] == "authority-pin-conflict"
            ],
            "conflicts": list(self.conflicts),
            "relationships": list(self.relationships),
        }


def _source_repository_names(
    source: Any,
    *,
    extractor: str,
    owner: str,
) -> set[str]:
    if not isinstance(source, dict):
        raise ValueError("coverage source must be a JSON object")
    if extractor == "members[].repo":
        records = source.get("members")
    elif extractor == "graph.nodes[].repo":
        graph = source.get("graph")
        records = graph.get("nodes") if isinstance(graph, dict) else None
    else:
        raise ValueError(f"unsupported coverage extractor {extractor!r}")
    if not isinstance(records, list) or not records:
        raise ValueError("coverage source records must be a non-empty array")
    repositories: set[str] = set()
    owner_prefix = f"{owner}/"
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("coverage source records must be objects")
        repository = record.get("repo")
        if repository is None:
            continue
        if not isinstance(repository, str) or not repository.startswith(owner_prefix):
            raise ValueError("coverage source repository is outside the declared estate owner")
        name = repository[len(owner_prefix) :]
        if not name or "/" in name:
            raise ValueError("coverage source repository identifier is invalid")
        repositories.add(name)
    if not repositories:
        raise ValueError("coverage source did not yield any repository identifiers")
    return repositories


def _recompute_projection_coverage(
    organism: Organism,
    projection: dict[str, Any],
) -> dict[str, Any]:
    source = projection["coverage_source"]
    evidence = {
        "state": "not-recomputed",
        "artifact": f"repos/{source['organ']}/{source['path']}",
        "extractor": source["extractor"],
        "evidence_kind": source["evidence_kind"],
    }
    if organism.drift != {"manifest_only": [], "taxonomy_only": []}:
        return {
            **evidence,
            "reason": "manifest/taxonomy drift prevents SafeSpecimen evidence access",
            "covered_organs": None,
            "missing_organs": None,
        }
    try:
        specimen = SafeSpecimen(organism)
        parsed = strict_loads(specimen.read_bytes(source["organ"], source["path"]))
        source_names = _source_repository_names(
            parsed,
            extractor=source["extractor"],
            owner=organism.registry["estate_scope"]["owner"],
        )
    except Exception as exc:
        return {
            **evidence,
            "reason": f"captured coverage evidence unavailable or invalid: {exc}",
            "covered_organs": None,
            "missing_organs": None,
        }
    manifest_names = set(organism.repository_names)
    covered = sorted(manifest_names & source_names)
    missing = sorted(manifest_names - source_names)
    coverage = projection["coverage"]
    numerator_key = (
        "captured_organ_overlap" if projection["id"] == "map" else "modeled_organs"
    )
    return {
        **evidence,
        "state": "recomputed-from-captured-artifact",
        "source_repository_count": len(source_names),
        "covered_organs": covered,
        "covered_organ_count": len(covered),
        "declared_covered_organ_count": coverage[numerator_key],
        "declared_count_matches_recomputed": len(covered) == coverage[numerator_key],
        "missing_organs": [
            {"organ": name, "reason": source["missing_reason"]} for name in missing
        ],
        "missing_organ_count": len(missing),
        "source_repositories_outside_snapshot_count": len(source_names - manifest_names),
    }


def inspect_alignment(
    root: str,
    *,
    now: datetime | None = None,
    stale_after_days: int = 7,
) -> AlignmentReport:
    """Compare declared projection evidence with today's captured manifest."""

    organism = Organism(root, allow_drift=True)
    checked = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not isinstance(stale_after_days, int) or isinstance(stale_after_days, bool):
        raise ValueError("stale_after_days must be an integer")
    if stale_after_days < 0:
        raise ValueError("stale_after_days must be non-negative")
    snapshot_count = len(organism.repository_names)
    try:
        provenance_specimen: SafeSpecimen | None = SafeSpecimen(organism)
        provenance_unavailable: str | None = None
    except Exception as exc:
        provenance_specimen = None
        provenance_unavailable = str(exc)
    projections: list[dict[str, Any]] = []
    for declared in organism.projections():
        projection = dict(declared)
        manifest_record = organism.organ(projection["organ"])
        manifest_commit = manifest_record["commit"]
        manifest_omissions = organism.omitted_blobs(projection["organ"])
        tracked = projection["tracked_blobs"]
        projection["component_coverage"] = {
            "captured": manifest_record["files"],
            "declared_live": tracked["live"],
            "state": "complete" if not manifest_omissions else "incomplete",
            "manifest_reconciled": (
                tracked["captured"] == manifest_record["files"]
                and tracked["live"]
                == manifest_record["files"] + len(manifest_omissions)
            ),
            "evidence_source": (
                f"MANIFEST.json repos[{projection['organ']!r}] file and omission counts"
            ),
        }
        projection["omission_evidence"] = {
            "source": (
                f"MANIFEST.json repos[{projection['organ']!r}]."
                "{skipped_large,withheld}"
            ),
            "count": len(manifest_omissions),
            "blobs": manifest_omissions,
        }
        projection["daily_checks"] = {
            "captured_commit_matches_manifest": projection["captured_commit"]
            == manifest_commit,
            "manifest_commit": manifest_commit,
            "live_commit_check": "not-performed-use-declared-evidence",
            "current_snapshot_organs": snapshot_count,
        }
        provenance_paths = [
            projection["generated_artifact"],
            projection["generator"],
            *projection["generated_from"],
        ]
        provenance_regular: dict[str, bool] = {}
        provenance_errors: dict[str, str] = {}
        projection_prefix = f"repos/{projection['organ']}/"
        for relative in provenance_paths:
            specimen_relative = relative.removeprefix(projection_prefix)
            try:
                if provenance_specimen is None:
                    raise ValueError(provenance_unavailable or "safe access unavailable")
                provenance_regular[relative] = provenance_specimen.is_regular_file(
                    projection["organ"], specimen_relative
                )
            except Exception as exc:
                provenance_regular[relative] = False
                provenance_errors[relative] = str(exc)
        projection["daily_checks"]["generator_provenance_regular_files"] = (
            provenance_regular
        )
        projection["daily_checks"]["generator_provenance_errors"] = (
            provenance_errors
        )
        paths_present = bool(provenance_regular) and all(
            provenance_regular.values()
        )
        projection["daily_checks"]["generator_provenance_paths_present"] = (
            paths_present
        )
        projection["daily_checks"]["generator_derivation_check"] = (
            "not-performed-captured-code-is-never-executed"
        )
        projection["daily_checks"]["generator_provenance_complete"] = False
        coverage = projection["coverage"]
        measured = coverage.get("snapshot_organs_at_measurement")
        numerator = coverage.get("captured_organ_overlap", coverage.get("modeled_organs"))
        projection["coverage_relationship"] = {
            "measured": f"{numerator}/{measured}",
            "against_current_snapshot": f"{numerator}/{snapshot_count}",
            "measurement_denominator_matches_current": measured == snapshot_count,
        }
        projection["coverage_evidence"] = _recompute_projection_coverage(
            organism, projection
        )
        observed_at = projection.get("observed_at")
        if observed_at is None:
            projection["freshness"] = {
                "state": "unknown",
                "age_days": None,
                "reason": "projection declares no observation timestamp",
            }
        else:
            observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
            age_days = (checked - observed.astimezone(timezone.utc)).total_seconds() / 86400
            projection["freshness"] = {
                "state": (
                    "future-dated"
                    if age_days < 0
                    else "stale"
                    if age_days > stale_after_days
                    else "current"
                ),
                "age_days": round(age_days, 3),
                "stale_after_days": stale_after_days,
            }
        projections.append(projection)
    return AlignmentReport(
        generated_at=checked.isoformat().replace("+00:00", "Z"),
        snapshot_organs=snapshot_count,
        taxonomy_drift=organism.drift,
        projections=tuple(projections),
        conflicts=tuple(organism.alignment_conflicts()),
        relationships=tuple(organism.relationships()),
    )
