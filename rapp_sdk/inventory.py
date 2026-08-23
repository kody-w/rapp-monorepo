"""Strict organism inventory and no-follow specimen content access."""

from __future__ import annotations

import os
import errno
import re
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import InventoryError, SpecimenAccessError
from .json_profile import strict_loads

MANIFEST_SCHEMA = "rapp-monorepo/1.0"
ORGANISM_SCHEMA = "rapp-organism/1.0"
_ORGAN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_GIT_OID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

SYSTEM_LIFECYCLES = frozenset(
    {
        "mixed-snapshot",
        "generated-snapshot",
        "historical-or-retired",
        "experimental-or-incubating",
        "unclassified-incubator",
    }
)
PROJECTION_LIFECYCLES = frozenset(
    {"active-but-observation-stale", "active-but-incomplete"}
)
PRODUCT_LIFECYCLES = frozenset({"active", "retired"})
TARGET_RECORD_CURRENCIES = frozenset(
    {"current-aligned", "current-but-drifted", "historical"}
)
EXCLUSION_REASON_CODES = frozenset(
    {"snapshot-self-recursion", "non-organ-staging-repository"}
)
PROJECTION_ORGANS = {"map": "rapp-map", "spine": "rapp-spine"}
PROJECTION_EXTRACTORS = {
    "map": "members[].repo",
    "spine": "graph.nodes[].repo",
}
PROJECTION_CONTRACTS = {
    "map": {
        "projection_type": "owner-wide-observation-map",
        "authority_kind": "derived-observation",
        "authority_scope": "navigation-and-cartography-only",
    },
    "spine": {
        "projection_type": "routing-and-foundation-index",
        "authority_kind": "curated-generated-projection",
        "authority_scope": "routing-and-navigation-only",
    },
}


def validate_organ_name(name: str) -> str:
    if (
        not isinstance(name, str)
        or not _ORGAN_RE.fullmatch(name)
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or os.sep in name
        or (os.altsep is not None and os.altsep in name)
    ):
        raise InventoryError("organ name contains a separator, dot component, or invalid character")
    return name


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = strict_loads(path.read_bytes())
    except OSError as exc:
        raise InventoryError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be a JSON object")
    return value


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_relative_path(value: Any, label: str) -> str:
    if not _is_nonempty_string(value) or "\\" in value:
        raise InventoryError(f"{label} must be a non-empty relative POSIX path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise InventoryError(f"{label} must be a non-empty relative POSIX path")
    return value


def _validate_observed_at(value: Any, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.endswith("Z"):
        raise InventoryError(f"{label} must be null or a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InventoryError(f"{label} must be a valid UTC timestamp") from exc
    if parsed.utcoffset() is None:
        raise InventoryError(f"{label} must include a UTC offset")


@dataclass(frozen=True)
class SnapshotStatistics:
    repositories: int
    files: int
    bytes: int
    skipped_large: int
    withheld: int
    omissions: int

    def as_dict(self) -> dict[str, int]:
        return {
            "repositories": self.repositories,
            "files": self.files,
            "bytes": self.bytes,
            "skipped_large": self.skipped_large,
            "withheld": self.withheld,
            "omissions": self.omissions,
        }


class Organism:
    """The manifest plus the architecture registry, never captured code."""

    def __init__(
        self,
        root: str | os.PathLike[str],
        *,
        allow_drift: bool = False,
    ):
        if not isinstance(allow_drift, bool):
            raise InventoryError("allow_drift must be a boolean")
        self.root = Path(root).absolute()
        self.allow_drift = allow_drift
        self._gitlinks_by_organ: dict[str, frozenset[str]] = {}
        self.manifest = _load_object(self.root / "MANIFEST.json", "MANIFEST.json")
        self.registry = _load_object(self.root / "ORGANISM.json", "ORGANISM.json")
        self._validate()

    def _validate(self) -> None:
        if self.manifest.get("schema") != MANIFEST_SCHEMA:
            raise InventoryError(f"MANIFEST.json schema must be {MANIFEST_SCHEMA!r}")
        if self.registry.get("schema") != ORGANISM_SCHEMA:
            raise InventoryError(f"ORGANISM.json schema must be {ORGANISM_SCHEMA!r}")
        if self.registry.get("snapshot_schema") != MANIFEST_SCHEMA:
            raise InventoryError("ORGANISM.json snapshot_schema does not match manifest")
        estate_scope = self.registry.get("estate_scope")
        if not isinstance(estate_scope, dict) or set(estate_scope) != {
            "owner",
            "membership",
            "deliberate_exclusions",
        }:
            raise InventoryError("ORGANISM.json estate_scope is incomplete")
        owner = estate_scope["owner"]
        membership = estate_scope["membership"]
        exclusions = estate_scope["deliberate_exclusions"]
        if not _is_nonempty_string(owner):
            raise InventoryError("estate_scope owner must be a non-empty string")
        if not isinstance(membership, dict) or set(membership) != {
            "visibility",
            "archived",
            "name_pattern",
        }:
            raise InventoryError("estate_scope membership is invalid")
        name_pattern = membership["name_pattern"]
        if (
            membership["visibility"] != "public"
            or membership["archived"] is not False
            or not _is_nonempty_string(name_pattern)
        ):
            raise InventoryError("estate_scope membership predicate is invalid")
        try:
            member_pattern = re.compile(name_pattern)
        except re.error as exc:
            raise InventoryError(
                "estate_scope membership name_pattern is invalid"
            ) from exc
        if self.manifest.get("owner") != owner:
            raise InventoryError("manifest owner differs from estate_scope owner")
        if self.manifest.get("membership_pattern") != name_pattern:
            raise InventoryError(
                "manifest membership_pattern differs from ORGANISM estate_scope"
            )
        if not isinstance(exclusions, list) or not exclusions:
            raise InventoryError("estate_scope deliberate_exclusions must be non-empty")
        excluded_names: list[str] = []
        expected_manifest_exclusions: list[dict[str, str]] = []
        for exclusion in exclusions:
            if not isinstance(exclusion, dict) or set(exclusion) != {
                "repository",
                "reason_code",
                "reason",
            }:
                raise InventoryError("each deliberate exclusion has the wrong shape")
            repository = exclusion["repository"]
            if (
                not _is_nonempty_string(repository)
                or repository.count("/") != 1
                or not repository.startswith(f"{owner}/")
                or not _is_nonempty_string(exclusion["reason_code"])
                or exclusion["reason_code"] not in EXCLUSION_REASON_CODES
                or not _is_nonempty_string(exclusion["reason"])
            ):
                raise InventoryError("deliberate exclusion is invalid")
            excluded_name = repository.split("/", 1)[1]
            validate_organ_name(excluded_name)
            if member_pattern.search(excluded_name) is None:
                raise InventoryError(
                    "deliberate exclusion does not match the membership pattern"
                )
            excluded_names.append(excluded_name)
            expected_manifest_exclusions.append(
                {
                    "repo": excluded_name,
                    "reason_code": exclusion["reason_code"],
                    "reason": exclusion["reason"],
                }
            )
        if len(excluded_names) != len(set(excluded_names)):
            raise InventoryError("deliberate exclusions must be unique")
        manifest_exclusions = self.manifest.get("membership_exclusions")
        if manifest_exclusions is not None:
            expected_manifest_exclusions.sort(
                key=lambda item: item["repo"].casefold()
            )
            if manifest_exclusions != {
                "exclude_archived": True,
                "repositories": expected_manifest_exclusions,
            }:
                raise InventoryError(
                    "manifest membership exclusions differ from ORGANISM estate_scope"
                )
        authority = self.registry.get("authority")
        if not isinstance(authority, dict) or not {
            "normative_source_current",
            "map_structural_pin",
            "target_structural_pin",
            "spine_pin_claim",
            "target_status",
            "owner_actions",
            "authenticated_registry",
            "retired_public_target",
        } <= set(authority):
            raise InventoryError("ORGANISM.json authority model is incomplete")
        current = authority["normative_source_current"]
        if (
            not isinstance(current, dict)
            or current.get("authority_role") != "normative-protocol-authority"
            or current.get("repository") != f"{owner}/rapp-1"
            or current.get("organ") != "rapp-1"
            or current.get("snapshot_path") != "repos/rapp-1/SPEC.md"
            or not _is_nonempty_string(current.get("repository_url"))
            or not _COMMIT_RE.fullmatch(str(current.get("snapshot_commit", "")))
            or not _SHA256_RE.fullmatch(str(current.get("sha256", "")))
            or not isinstance(current.get("byte_length"), int)
            or isinstance(current.get("byte_length"), bool)
            or current["byte_length"] <= 0
        ):
            raise InventoryError("normative_source_current is invalid")
        for key in ("map_structural_pin", "target_structural_pin", "spine_pin_claim"):
            if not isinstance(authority[key], dict):
                raise InventoryError(f"{key} must be an object")
        authenticated = authority["authenticated_registry"]
        if (
            not isinstance(authenticated, dict)
            or authenticated.get("is_section_13_registry") is not False
            or authenticated.get("state") != "absent"
        ):
            raise InventoryError("snapshot must not claim an authenticated registry")
        conformance = self.registry.get("conformance")
        if (
            not isinstance(conformance, dict)
            or set(conformance) != {"state", "full_conformance", "reason"}
            or conformance.get("state") != "not-fully-rapp-1-conformant"
            or conformance.get("full_conformance") is not False
            or not _is_nonempty_string(conformance.get("reason"))
        ):
            raise InventoryError(
                "absent authenticated registry requires explicit non-conformance"
            )
        retired_target = authority["retired_public_target"]
        if (
            not isinstance(retired_target, dict)
            or retired_target.get("repository") != f"{owner}/RAPP"
            or not _is_nonempty_string(retired_target.get("product_lifecycle"))
            or retired_target.get("product_lifecycle") not in PRODUCT_LIFECYCLES
            or retired_target.get("product_lifecycle") != "retired"
            or not _is_nonempty_string(
                retired_target.get("target_record_currency")
            )
            or retired_target.get("target_record_currency")
            not in TARGET_RECORD_CURRENCIES
            or retired_target.get("target_record_currency") != "current-but-drifted"
            or retired_target.get("protocol_authority") is not False
            or retired_target.get("may_redefine_rapp_1") is not False
            or not _is_nonempty_string(retired_target.get("replacement_boundary"))
        ):
            raise InventoryError("RAPP product lifecycle or target-record currency is invalid")
        repos = self.manifest.get("repos")
        systems = self.registry.get("systems")
        if (
            not isinstance(repos, list)
            or not repos
            or not isinstance(systems, list)
            or not systems
        ):
            raise InventoryError("manifest repos and organism systems must be arrays")
        names: list[str] = []
        for record in repos:
            if not isinstance(record, dict) or not isinstance(record.get("repo"), str):
                raise InventoryError("each manifest repository must have a string repo")
            validate_organ_name(record["repo"])
            if not isinstance(record.get("commit"), str):
                raise InventoryError("each manifest repository must have a commit pin")
            if not _COMMIT_RE.fullmatch(record["commit"]):
                raise InventoryError("each manifest repository commit must be a 40-hex pin")
            if member_pattern.search(record["repo"]) is None:
                raise InventoryError(
                    "manifest repository does not match the estate membership pattern"
                )
            gitlinks = record.get("gitlinks", [])
            if not isinstance(gitlinks, list):
                raise InventoryError("manifest gitlinks must be an array")
            gitlink_paths: set[str] = set()
            for item in gitlinks:
                if (
                    not isinstance(item, dict)
                    or set(item) != {"path", "commit"}
                    or not isinstance(item.get("path"), str)
                    or not _GIT_OID_RE.fullmatch(str(item.get("commit", "")))
                ):
                    raise InventoryError(
                        "manifest gitlinks must contain path/commit objects"
                    )
                path = _validate_relative_path(
                    item["path"], f"{record['repo']} gitlink path"
                )
                if path in gitlink_paths or any(
                    existing.startswith(path + "/")
                    or path.startswith(existing + "/")
                    for existing in gitlink_paths
                ):
                    raise InventoryError(
                        "manifest gitlink paths must be unique and non-nested"
                    )
                gitlink_paths.add(path)
            self._gitlinks_by_organ[record["repo"]] = frozenset(
                gitlink_paths
            )
            names.append(record["repo"])
        if len(names) != len(set(names)):
            raise InventoryError("manifest repository names must be unique")
        if current["organ"] not in names:
            raise InventoryError("normative rapp-1 organ is absent from the manifest")
        if set(names) & set(excluded_names):
            raise InventoryError("deliberately excluded repositories must not appear in manifest")
        classified: list[str] = []
        system_ids: set[str] = set()
        classification: dict[str, str] = {}
        for system in systems:
            if (
                not isinstance(system, dict)
                or not _is_nonempty_string(system.get("id"))
                or not _is_nonempty_string(system.get("name"))
                or not isinstance(system.get("lifecycle"), str)
                or not _is_nonempty_string(system.get("authority"))
                or not isinstance(system.get("organs"), list)
                or not system["organs"]
            ):
                raise InventoryError("each system requires id/name/lifecycle/authority/organs")
            if system["id"] in system_ids:
                raise InventoryError("system ids must be unique")
            system_ids.add(system["id"])
            if system["lifecycle"] not in SYSTEM_LIFECYCLES:
                raise InventoryError("system lifecycle is outside the constrained vocabulary")
            if not all(isinstance(name, str) for name in system["organs"]):
                raise InventoryError("system organs must be strings")
            for name in system["organs"]:
                validate_organ_name(name)
                classification[name] = system["id"]
            classified.extend(system["organs"])
        if len(classified) != len(set(classified)):
            raise InventoryError("every organ must be classified exactly once")
        manifest_names = set(names)
        taxonomy_names = set(classified)
        if manifest_names != taxonomy_names and not self.allow_drift:
            raise InventoryError(
                "manifest/taxonomy sets differ; pass allow_drift=True only for reporting"
            )
        if (
            "rapp-1" in classification
            and classification["rapp-1"] != "authority-contracts-navigation"
        ):
            raise InventoryError(
                "rapp-1 must be classified in authority-contracts-navigation"
            )
        projections = self.registry.get("projections")
        relationships = self.registry.get("relationships")
        conflicts = self.registry.get("alignment_conflicts")
        if (
            not isinstance(projections, list)
            or not projections
            or not isinstance(relationships, list)
            or not relationships
            or not isinstance(conflicts, list)
            or not conflicts
        ):
            raise InventoryError(
                "ORGANISM.json requires non-empty projections, relationships, and "
                "alignment_conflicts arrays"
            )
        projection_ids: set[str] = set()
        for projection in projections:
            required = {
                "schema",
                "id",
                "organ",
                "projection_type",
                "authority_kind",
                "authority_scope",
                "lifecycle",
                "captured_commit",
                "live_commit",
                "live_evidence",
                "tracked_blobs",
                "coverage",
                "observed_at",
                "generated_artifact",
                "generator",
                "generated_from",
                "coverage_source",
            }
            if (
                not isinstance(projection, dict)
                or not required <= set(projection)
                or not set(projection) <= required | {"omitted_blobs"}
            ):
                raise InventoryError("projection evidence has the wrong machine-readable shape")
            if projection["schema"] != "rapp-projection-evidence/1.0":
                raise InventoryError("projection schema is invalid")
            if (
                not isinstance(projection.get("id"), str)
                or projection["id"] not in PROJECTION_ORGANS
            ):
                raise InventoryError("projection id must be map or spine")
            validate_organ_name(projection["organ"])
            if (
                projection["organ"] not in names
                or projection["organ"] != PROJECTION_ORGANS[projection["id"]]
                or projection["id"] in projection_ids
            ):
                raise InventoryError("projection organ is absent or projection id is duplicated")
            projection_ids.add(projection["id"])
            contract = PROJECTION_CONTRACTS[projection["id"]]
            if any(projection.get(key) != value for key, value in contract.items()):
                raise InventoryError(
                    "projection type and authority must match the subordinate contract"
                )
            if (
                not isinstance(projection.get("lifecycle"), str)
                or projection["lifecycle"] not in PROJECTION_LIFECYCLES
            ):
                raise InventoryError("projection lifecycle is outside the constrained vocabulary")
            if not _COMMIT_RE.fullmatch(str(projection.get("captured_commit", ""))) or not (
                _COMMIT_RE.fullmatch(str(projection.get("live_commit", "")))
            ):
                raise InventoryError("projection commits must be 40-hex pins")
            if (
                projection.get("live_evidence")
                != "declared-cartographer-report-not-dynamically-fetched-by-sdk"
            ):
                raise InventoryError("projection live evidence must remain explicitly declared")
            tracked = projection.get("tracked_blobs")
            if (
                not isinstance(tracked, dict)
                or set(tracked) != {"captured", "live"}
                or any(
                    not isinstance(tracked[key], int)
                    or isinstance(tracked[key], bool)
                    or tracked[key] <= 0
                    for key in ("captured", "live")
                )
                or tracked["captured"] > tracked["live"]
            ):
                raise InventoryError("projection tracked_blobs counts are invalid")
            coverage = projection.get("coverage")
            numerator_key = (
                "captured_organ_overlap" if projection["id"] == "map" else "modeled_organs"
            )
            expected_coverage_keys = (
                {
                    "observed_owner_repositories",
                    "captured_organ_overlap",
                    "snapshot_organs_at_measurement",
                }
                if projection["id"] == "map"
                else {
                    "modeled_organs",
                    "snapshot_organs_at_measurement",
                    "protocol_materials",
                    "required_sources",
                }
            )
            if (
                not isinstance(coverage, dict)
                or set(coverage) != expected_coverage_keys
                or not isinstance(coverage.get(numerator_key), int)
                or isinstance(coverage.get(numerator_key), bool)
                or coverage[numerator_key] <= 0
                or not isinstance(coverage.get("snapshot_organs_at_measurement"), int)
                or isinstance(coverage.get("snapshot_organs_at_measurement"), bool)
                or coverage["snapshot_organs_at_measurement"] <= 0
                or coverage[numerator_key] > coverage["snapshot_organs_at_measurement"]
            ):
                raise InventoryError("projection coverage counts are invalid")
            if projection["id"] == "map":
                observed_repositories = coverage["observed_owner_repositories"]
                if (
                    not isinstance(observed_repositories, int)
                    or isinstance(observed_repositories, bool)
                    or observed_repositories < coverage[numerator_key]
                ):
                    raise InventoryError("Map observed repository count is invalid")
            else:
                for key in ("protocol_materials", "required_sources"):
                    unresolved = coverage[key]
                    if (
                        not isinstance(unresolved, dict)
                        or set(unresolved) != {"unresolved", "total"}
                        or not isinstance(unresolved.get("unresolved"), int)
                        or isinstance(unresolved.get("unresolved"), bool)
                        or not isinstance(unresolved.get("total"), int)
                        or isinstance(unresolved.get("total"), bool)
                        or unresolved["total"] <= 0
                        or not 0 <= unresolved["unresolved"] <= unresolved["total"]
                    ):
                        raise InventoryError("Spine unresolved coverage counts are invalid")
            _validate_observed_at(
                projection.get("observed_at"),
                f"{projection['id']} observed_at",
            )
            _validate_relative_path(
                projection.get("generated_artifact"),
                f"{projection['id']} generated_artifact",
            )
            _validate_relative_path(
                projection.get("generator"),
                f"{projection['id']} generator",
            )
            projection_prefix = f"repos/{projection['organ']}/"
            if (
                not projection["generated_artifact"].startswith(projection_prefix)
                or not projection["generator"].startswith(projection_prefix)
            ):
                raise InventoryError(
                    "projection artifact and generator must belong to its organ"
                )
            if (
                not isinstance(projection["generated_from"], list)
                or not projection["generated_from"]
                or not all(
                    _is_nonempty_string(path)
                    and _validate_relative_path(
                        path, f"{projection['id']} generated_from entry"
                    )
                    and path.startswith(projection_prefix)
                    for path in projection["generated_from"]
                )
            ):
                raise InventoryError("projection generator provenance is incomplete")
            coverage_source = projection.get("coverage_source")
            if (
                not isinstance(coverage_source, dict)
                or set(coverage_source)
                != {
                    "organ",
                    "path",
                    "extractor",
                    "evidence_kind",
                    "missing_reason",
                }
                or coverage_source.get("organ") != projection["organ"]
                or coverage_source.get("extractor")
                != PROJECTION_EXTRACTORS[projection["id"]]
                or coverage_source.get("evidence_kind")
                != "recomputable-from-captured-artifact"
                or not _is_nonempty_string(coverage_source.get("missing_reason"))
            ):
                raise InventoryError("projection coverage_source is invalid")
            _validate_relative_path(
                coverage_source.get("path"),
                f"{projection['id']} coverage_source path",
            )
            omitted_blobs = projection.get("omitted_blobs")
            if omitted_blobs is not None:
                if not isinstance(omitted_blobs, list) or not omitted_blobs:
                    raise InventoryError("omitted_blobs must be absent or non-empty")
                for omission in omitted_blobs:
                    if (
                        not isinstance(omission, dict)
                        or set(omission) != {"path", "reason"}
                        or not _is_nonempty_string(omission.get("path"))
                        or not _is_nonempty_string(omission.get("reason"))
                    ):
                        raise InventoryError("omitted blob evidence is invalid")
        if projection_ids != set(PROJECTION_ORGANS):
            raise InventoryError("both Map and Spine projections are required")
        expected_relationships = [
            {
                "type": "normative-authority",
                "from": f"{owner}/rapp-1",
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
                "from": f"{owner}/RAPP",
                "to": (
                    f"{owner}/rapp-1@"
                    f"{authority['target_structural_pin']['commit']}"
                ),
                "current_normative_bytes": False,
            },
        ]
        if relationships != expected_relationships:
            raise InventoryError(
                "relationships must preserve the one-way authority contract"
            )
        conflict_ids: set[str] = set()
        for conflict in conflicts:
            if (
                not isinstance(conflict, dict)
                or not _is_nonempty_string(conflict.get("id"))
                or not _is_nonempty_string(conflict.get("type"))
                or not _is_nonempty_string(conflict.get("evidence_mode"))
                or conflict.get("evidence_mode")
                not in {"validated-local-records", "evidence-backed-declared-finding"}
                or not isinstance(conflict.get("evidence_paths"), list)
                or not conflict["evidence_paths"]
                or not all(
                    _is_nonempty_string(path)
                    and _validate_relative_path(path, "alignment conflict evidence path")
                    for path in conflict["evidence_paths"]
                )
                or conflict["id"] in conflict_ids
            ):
                raise InventoryError(
                    "alignment conflicts require unique ids and non-empty evidence paths"
                )
            conflict_ids.add(conflict["id"])

    @property
    def repository_names(self) -> tuple[str, ...]:
        return tuple(record["repo"] for record in self.manifest["repos"])

    @property
    def drift(self) -> dict[str, list[str]]:
        manifest = set(self.repository_names)
        taxonomy = {
            name for system in self.registry["systems"] for name in system["organs"]
        }
        return {
            "manifest_only": sorted(manifest - taxonomy),
            "taxonomy_only": sorted(taxonomy - manifest),
        }

    @property
    def statistics(self) -> SnapshotStatistics:
        repos = self.manifest["repos"]
        skipped = sum(len(record.get("skipped_large", [])) for record in repos)
        withheld = sum(len(record.get("withheld", [])) for record in repos)
        not_captured = self.manifest.get("not_captured", [])
        if not isinstance(not_captured, list):
            raise InventoryError("not_captured must be an array")
        return SnapshotStatistics(
            repositories=len(repos),
            files=sum(record["files"] for record in repos),
            bytes=sum(record["bytes"] for record in repos),
            skipped_large=skipped,
            withheld=withheld,
            omissions=skipped + withheld + len(not_captured),
        )

    @property
    def authority_paths(self) -> dict[str, Any]:
        return dict(self.registry["authority"])

    def systems(self) -> list[dict[str, Any]]:
        return [dict(system) for system in self.registry["systems"]]

    def organs(self) -> list[dict[str, Any]]:
        membership = {
            organ: system
            for system in self.registry["systems"]
            for organ in system["organs"]
        }
        result = []
        for record in self.manifest["repos"]:
            item = dict(record)
            system = membership.get(record["repo"])
            item["system"] = system["id"] if system is not None else None
            item["system_lifecycle"] = (
                system["lifecycle"] if system is not None else None
            )
            item["system_authority"] = (
                system["authority"] if system is not None else None
            )
            result.append(item)
        return result

    def omissions(self) -> dict[str, list[Any]]:
        skipped: list[dict[str, str]] = []
        withheld: list[dict[str, Any]] = []
        for record in self.manifest["repos"]:
            skipped.extend(
                {"organ": record["repo"], "entry": entry}
                for entry in record.get("skipped_large", [])
            )
            withheld.extend(
                {"organ": record["repo"], **entry}
                for entry in record.get("withheld", [])
                if isinstance(entry, dict)
            )
        return {
            "skipped_large": skipped,
            "withheld": withheld,
            "not_captured": list(self.manifest.get("not_captured", [])),
        }

    def organ(self, name: str) -> dict[str, Any]:
        validate_organ_name(name)
        for record in self.organs():
            if record["repo"] == name:
                return record
        raise InventoryError(f"unknown organ {name!r}")

    def gitlink_paths(self, name: str) -> frozenset[str]:
        self.organ(name)
        return self._gitlinks_by_organ.get(name, frozenset())

    def summary(self) -> dict[str, Any]:
        return {
            "schema": self.registry["schema"],
            "conformance": self.registry["conformance"],
            "snapshot": {
                "owner": self.manifest.get("owner"),
                "captured_at": self.manifest.get("captured_at"),
                **self.statistics.as_dict(),
            },
            "estate_scope": self.registry["estate_scope"],
            "architecture_drift": self.drift,
            "omissions": self.omissions(),
            "authority": self.authority_paths,
        }

    def projections(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.registry["projections"]]

    def relationships(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.registry["relationships"]]

    def alignment_conflicts(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.registry["alignment_conflicts"]]


class SafeSpecimen:
    """Read-only content access that rejects traversal and every symlink component."""

    def __init__(self, organism: Organism):
        if organism.drift != {"manifest_only": [], "taxonomy_only": []}:
            raise SpecimenAccessError(
                "safe specimen access requires exact manifest/taxonomy equality"
            )
        self.organism = organism

    @staticmethod
    def _require_no_follow_primitives() -> None:
        required_dir_fd = {os.open, os.stat, os.readlink}
        if (
            not hasattr(os, "O_DIRECTORY")
            or not hasattr(os, "O_NOFOLLOW")
            or not required_dir_fd <= os.supports_dir_fd
        ):
            raise SpecimenAccessError(
                "platform lacks descriptor-relative O_DIRECTORY/O_NOFOLLOW primitives"
            )

    @staticmethod
    def _parts(path: str) -> tuple[str, ...]:
        if not isinstance(path, str) or not path:
            raise SpecimenAccessError("path must be a non-empty relative POSIX path")
        if "\\" in path or path.startswith("/"):
            raise SpecimenAccessError("backslashes are forbidden")
        segments = path.split("/")
        if any(part in {"", ".", ".."} for part in segments):
            raise SpecimenAccessError("absolute paths, dot segments, and traversal are forbidden")
        pure = PurePosixPath(path)
        if pure.is_absolute():
            raise SpecimenAccessError("absolute paths, dot segments, and traversal are forbidden")
        return pure.parts

    def _open_parent(self, organ: str, path: str) -> tuple[int, str]:
        self._require_no_follow_primitives()
        self.organism.organ(organ)
        relative_parts = self._parts(path)
        relative = "/".join(relative_parts)
        if any(
            relative == gitlink or relative.startswith(gitlink + "/")
            for gitlink in self.organism.gitlink_paths(organ)
        ):
            raise SpecimenAccessError(
                "specimen path is a gitlink pointer and cannot be traversed"
            )
        parts = ("repos", organ, *relative_parts)
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            descriptor = os.open(self.organism.root, directory_flags)
            for part in parts[:-1]:
                next_descriptor = os.open(part, directory_flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = next_descriptor
            return descriptor, parts[-1]
        except OSError as exc:
            try:
                os.close(descriptor)
            except (UnboundLocalError, OSError):
                pass
            raise SpecimenAccessError(
                "specimen parent is missing, not a directory, or a symlink"
            ) from exc

    def read_bytes(self, organ: str, path: str, *, max_bytes: int | None = None) -> bytes:
        if max_bytes is not None and (
            not isinstance(max_bytes, int)
            or isinstance(max_bytes, bool)
            or max_bytes < 0
        ):
            raise SpecimenAccessError("max_bytes must be a non-negative integer")
        parent, name = self._open_parent(organ, path)
        flags = os.O_RDONLY | os.O_NOFOLLOW
        try:
            descriptor = os.open(name, flags, dir_fd=parent)
            try:
                status = os.fstat(descriptor)
                if not stat.S_ISREG(status.st_mode):
                    raise SpecimenAccessError("specimen target is not a regular file")
                if max_bytes is not None and status.st_size > max_bytes:
                    raise SpecimenAccessError("specimen file exceeds the read bound")
                remaining = status.st_size if max_bytes is None else min(status.st_size, max_bytes)
                chunks: list[bytes] = []
                while remaining:
                    chunk = os.read(descriptor, min(remaining, 1024 * 1024))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
                if remaining:
                    raise SpecimenAccessError("unexpected short read from specimen file")
                return b"".join(chunks)
            finally:
                os.close(descriptor)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise SpecimenAccessError("specimen target is a symlink and was not followed") from exc
            raise SpecimenAccessError(f"cannot read specimen file: {exc}") from exc
        finally:
            os.close(parent)

    def read_text(
        self, organ: str, path: str, *, encoding: str = "utf-8", max_bytes: int | None = None
    ) -> str:
        try:
            return self.read_bytes(organ, path, max_bytes=max_bytes).decode(encoding)
        except UnicodeDecodeError as exc:
            raise SpecimenAccessError(f"specimen file is not valid {encoding}") from exc

    def readlink(self, organ: str, path: str) -> str:
        parent, name = self._open_parent(organ, path)
        try:
            mode = os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode
            if not stat.S_ISLNK(mode):
                raise SpecimenAccessError("specimen target is not a symlink")
            return os.readlink(name, dir_fd=parent)
        except OSError as exc:
            raise SpecimenAccessError(f"cannot inspect specimen symlink: {exc}") from exc
        finally:
            os.close(parent)
