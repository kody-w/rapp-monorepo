"""Evidence-labeled Map/Spine alignment reporting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import stat
from typing import Any

from .inventory import Organism


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


def inspect_alignment(
    root: str,
    *,
    now: datetime | None = None,
    stale_after_days: int = 7,
) -> AlignmentReport:
    """Compare declared projection evidence with today's captured manifest."""

    organism = Organism(root)
    checked = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not isinstance(stale_after_days, int) or isinstance(stale_after_days, bool):
        raise ValueError("stale_after_days must be an integer")
    if stale_after_days < 0:
        raise ValueError("stale_after_days must be non-negative")
    snapshot_count = len(organism.repository_names)
    root_path = Path(root).absolute()
    projections: list[dict[str, Any]] = []
    for declared in organism.projections():
        projection = dict(declared)
        manifest_commit = organism.organ(projection["organ"])["commit"]
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
        for relative in provenance_paths:
            try:
                mode = os.lstat(root_path / relative).st_mode
                provenance_regular[relative] = stat.S_ISREG(mode)
            except OSError:
                provenance_regular[relative] = False
        projection["daily_checks"]["generator_provenance_regular_files"] = (
            provenance_regular
        )
        projection["daily_checks"]["generator_provenance_complete"] = all(
            provenance_regular.values()
        )
        coverage = projection["coverage"]
        measured = coverage.get("snapshot_organs_at_measurement")
        numerator = coverage.get("captured_organ_overlap", coverage.get("modeled_organs"))
        projection["coverage_relationship"] = {
            "measured": f"{numerator}/{measured}",
            "against_current_snapshot": f"{numerator}/{snapshot_count}",
            "measurement_denominator_matches_current": measured == snapshot_count,
        }
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
