"""Honest structural authority and conformance reporting."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .inventory import Organism, SafeSpecimen
from .json_profile import strict_loads


@dataclass(frozen=True)
class AuthorityReport:
    normative_repository: str
    normative_repository_url: str
    normative_source_commit: str
    normative_source_state: str
    normative_source_sha256: str | None
    normative_source_byte_length: int | None
    map_pin_valid: bool
    map_pin_commit: str | None
    map_pin_matches_current: bool
    target_pin_valid: bool
    target_pin_commit: str | None
    target_pin_sha256: str | None
    target_pin_byte_length: int | None
    target_pin_state: str
    spine_observed_pin: str | None
    spine_pin_equals_map_current: bool
    target_status: str
    authenticated_registry: str
    owner_action_blockers: tuple[str, ...]
    full_conformance: bool
    findings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "normative_source_current": {
                "repository": self.normative_repository,
                "url": self.normative_repository_url,
                "snapshot_commit": self.normative_source_commit,
                "state": self.normative_source_state,
                "sha256": self.normative_source_sha256,
                "byte_length": self.normative_source_byte_length,
                "stale_target_may_redefine": False,
            },
            "map_structural_pin": {
                "valid": self.map_pin_valid,
                "commit": self.map_pin_commit,
                "matches_normative_source_current_bytes": self.map_pin_matches_current,
                "authenticated_registry_acceptance": False,
            },
            "target_structural_pin": {
                "valid_for_target_record": self.target_pin_valid,
                "commit": self.target_pin_commit,
                "sha256": self.target_pin_sha256,
                "byte_length": self.target_pin_byte_length,
                "state": self.target_pin_state,
                "matches_normative_source_current_bytes": self.target_pin_state
                == "aligned-with-normative-source-current",
            },
            "spine_pin_claim": {
                "observed_old_commit": self.spine_observed_pin,
                "map_current_commit": self.map_pin_commit,
                "commits_equal": self.spine_pin_equals_map_current,
                "claim_that_old_pin_equals_map_current": "false"
                if not self.spine_pin_equals_map_current
                else "true",
            },
            "target_status": self.target_status,
            "authenticated_registry": self.authenticated_registry,
            "owner_action_blockers": list(self.owner_action_blockers),
            "full_conformance": self.full_conformance,
            "findings": list(self.findings),
        }


def inspect_authority(root: str) -> AuthorityReport:
    organism = Organism(root)
    specimen = SafeSpecimen(organism)
    model = organism.authority_paths
    current_model = model["normative_source_current"]
    map_model = model["map_structural_pin"]
    target_model = model["target_structural_pin"]
    spine_model = model["spine_pin_claim"]
    normative_source_commit = organism.organ("rapp-1")["commit"]
    findings: list[str] = []
    try:
        authority = strict_loads(specimen.read_bytes("RAPP", "RAPP1_AUTHORITY.json"))
    except Exception as exc:
        authority = {}
        findings.append(f"authority record unavailable or invalid: {exc}")
    standard = authority.get("standard", {}) if isinstance(authority, dict) else {}
    target = authority.get("target", {}) if isinstance(authority, dict) else {}
    registry = authority.get("authenticated_registry", {}) if isinstance(authority, dict) else {}
    offline = authority.get("offline_verification", {}) if isinstance(authority, dict) else {}
    target_pin_valid = (
        isinstance(authority, dict)
        and set(authority)
        == {
            "schema",
            "record_kind",
            "target",
            "standard",
            "offline_verification",
            "authenticated_registry",
            "immutable_grail_boundary",
        }
        and authority.get("schema") == "rapp-authority-pin/1.0"
        and authority.get("record_kind") == "structural-authority-pin"
        and set(target) == {"repository", "status", "status_path"}
        and target.get("repository") == target_model["target"]
        and target.get("status") == "not-yet-fully-rapp-1-conformant"
        and target.get("status_path") == "RAPP1_STATUS.md"
        and set(standard)
        == {
            "repository",
            "commit",
            "path",
            "sha256",
            "byte_length",
            "wire_tag",
            "revision",
            "canonical_url",
            "retrieval_url",
        }
        and standard.get("repository") == "kody-w/rapp-1"
        and standard.get("commit") == target_model["commit"]
        and standard.get("path") == "SPEC.md"
        and standard.get("sha256") == target_model["sha256"]
        and standard.get("byte_length") == target_model["byte_length"]
        and standard.get("wire_tag") == "rapp/1"
        and standard.get("revision") == "rev-5"
        and standard.get("canonical_url")
        == f"https://github.com/kody-w/rapp-1/blob/{target_model['commit']}/SPEC.md"
        and standard.get("retrieval_url")
        == f"https://raw.githubusercontent.com/kody-w/rapp-1/{target_model['commit']}/SPEC.md"
        and offline.get("strategy") == "metadata-fixture"
        and offline.get("vendored_spec_bytes") is False
        and registry.get("is_section_13_registry") is False
    )
    if not target_pin_valid:
        findings.append("RAPP target structural pin record does not match its declared rev-5 pin")
    try:
        spec = specimen.read_bytes("rapp-1", "SPEC.md")
        current_hash = hashlib.sha256(spec).hexdigest()
        current_length = len(spec)
        current_state = "available-current-designated-source"
        if (
            current_hash != current_model["sha256"]
            or current_length != current_model["byte_length"]
            or normative_source_commit != current_model["snapshot_commit"]
        ):
            current_state = "available-current-source-with-registry-drift"
            findings.append(
                "ORGANISM normative-source metadata drifted from the daily manifest/SPEC bytes"
            )
    except Exception as exc:
        current_hash = None
        current_length = None
        current_state = "unavailable"
        findings.append(f"current normative source SPEC unavailable: {exc}")
    try:
        map_pin = strict_loads(specimen.read_bytes("rapp-map", "RAPP1_AUTHORITY.json"))
    except Exception as exc:
        map_pin = {}
        findings.append(f"rapp-map structural pin unavailable or invalid: {exc}")
    map_pin_valid = (
        isinstance(map_pin, dict)
        and set(map_pin)
        == {
            "document_type",
            "repository",
            "commit",
            "spec_path",
            "spec_revision",
            "raw_url",
            "bytes",
            "sha256",
            "authority_scope",
            "structural_pin_only",
            "authenticated_registry_acceptance",
        }
        and map_pin.get("document_type") == "rapp-1-authority-pin"
        and map_pin.get("repository") == current_model["repository"]
        and map_pin.get("commit") == map_model["commit"]
        and map_pin.get("spec_path") == "SPEC.md"
        and map_pin.get("spec_revision") == 5
        and map_pin.get("bytes") == map_model["byte_length"]
        and map_pin.get("sha256") == map_model["sha256"]
        and map_pin.get("raw_url")
        == (
            f"https://raw.githubusercontent.com/{current_model['repository']}/"
            f"{map_model['commit']}/SPEC.md"
        )
        and map_pin.get("structural_pin_only") is True
        and map_pin.get("authenticated_registry_acceptance") is False
    )
    map_matches_current = (
        map_pin_valid
        and current_hash == map_pin.get("sha256")
        and current_length == map_pin.get("bytes")
    )
    target_matches_current = (
        target_pin_valid
        and current_hash == standard.get("sha256")
        and current_length == standard.get("byte_length")
    )
    target_pin_state = (
        "aligned-with-normative-source-current"
        if target_matches_current
        else "structurally-valid-for-target-but-drifted"
        if target_pin_valid
        else "invalid-target-pin-record"
    )
    if not target_matches_current:
        findings.append(
            f"RAPP target pins older {target_model['byte_length']:,}-byte SPEC bytes and drifts from the "
            "user-designated current kody-w/rapp-1 source; the target pin does not redefine the standard"
        )
    if not map_matches_current:
        findings.append("rapp-map pin does not match the captured current normative SPEC bytes")
    try:
        spine_organ, spine_path = spine_model["evidence_path"].split("/", 2)[1:]
        spine_crawl = specimen.read_text(spine_organ, spine_path)
        observed = spine_model["observed_old_commit"]
        spine_observed_pin = observed if observed in spine_crawl else None
    except Exception as exc:
        spine_observed_pin = None
        findings.append(f"rapp-spine pin evidence unavailable: {exc}")
    spine_equals_map = (
        spine_observed_pin is not None
        and map_pin.get("commit") is not None
        and spine_observed_pin == map_pin.get("commit")
    )
    if spine_observed_pin is not None and not spine_equals_map:
        findings.append(
            f"rapp-spine's old {spine_observed_pin[:7]} pin is not equal to "
            f"rapp-map's current {map_pin.get('commit', '')[:7]} pin"
        )
    try:
        status_text = specimen.read_text("RAPP", "RAPP1_STATUS.md")
        first_line = next(line.strip() for line in status_text.splitlines() if line.strip())
        status_state = first_line.lstrip("# ").strip()
    except Exception as exc:
        status_state = "STATUS UNAVAILABLE"
        findings.append(f"target status unavailable: {exc}")
    try:
        actions = strict_loads(specimen.read_bytes("RAPP", "RAPP1_OWNER_ACTIONS.json"))
        ledger_valid = (
            isinstance(actions, dict)
            and actions.get("schema") == "rapp-owner-action-ledger/1.0"
            and actions.get("is_section_13_registry") is False
            and actions.get("authenticated_acceptance_allowed") is False
        )
        blockers = tuple(
            action["id"]
            for action in actions.get("actions", [])
            if isinstance(action, dict)
            and action.get("status") == "owner-action-required"
            and isinstance(action.get("id"), str)
        )
        if not ledger_valid:
            findings.append("owner-action ledger shape or fail-closed state is invalid")
    except Exception as exc:
        blockers = ("owner-action-ledger-unavailable",)
        findings.append(f"owner-action ledger unavailable: {exc}")
    authenticated_registry = "absent"
    findings.append(
        "authenticated acceptance requires the owner-published signed monotonic "
        "section-13 registry and out-of-band anchor"
    )
    return AuthorityReport(
        normative_repository=current_model["repository"],
        normative_repository_url=current_model["repository_url"],
        normative_source_commit=normative_source_commit,
        normative_source_state=current_state,
        normative_source_sha256=current_hash,
        normative_source_byte_length=current_length,
        map_pin_valid=map_pin_valid,
        map_pin_commit=map_pin.get("commit"),
        map_pin_matches_current=map_matches_current,
        target_pin_valid=target_pin_valid,
        target_pin_commit=standard.get("commit"),
        target_pin_sha256=standard.get("sha256"),
        target_pin_byte_length=standard.get("byte_length"),
        target_pin_state=target_pin_state,
        spine_observed_pin=spine_observed_pin,
        spine_pin_equals_map_current=spine_equals_map,
        target_status=status_state,
        authenticated_registry=authenticated_registry,
        owner_action_blockers=blockers,
        full_conformance=False,
        findings=tuple(findings),
    )
