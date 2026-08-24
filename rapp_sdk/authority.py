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
    map_authority_scope: str | None
    map_status: str
    map_status_valid: bool
    target_pin_valid: bool
    target_pin_commit: str | None
    target_pin_sha256: str | None
    target_pin_byte_length: int | None
    target_pin_state: str
    target_product_lifecycle: str
    target_record_currency: str
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
                "authority_scope": self.map_authority_scope,
                "status": self.map_status,
                "status_valid": self.map_status_valid,
                "authenticated_registry_acceptance": False,
            },
            "target_structural_pin": {
                "valid_for_target_record": self.target_pin_valid,
                "commit": self.target_pin_commit,
                "sha256": self.target_pin_sha256,
                "byte_length": self.target_pin_byte_length,
                "state": self.target_pin_state,
                "product_lifecycle": self.target_product_lifecycle,
                "record_currency": self.target_record_currency,
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


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _snapshot_location(path: str) -> tuple[str, str]:
    parts = path.split("/", 2)
    if len(parts) != 3 or parts[0] != "repos":
        raise ValueError("authority evidence path is outside repos/")
    return parts[1], parts[2]


def _status_heading(text: str) -> str:
    first_line = next(line.strip() for line in text.splitlines() if line.strip())
    return first_line.lstrip("# ").strip()


def _target_authority_record_valid(
    authority: Any,
    *,
    current_model: dict[str, Any],
    target_model: dict[str, Any],
    status_valid: bool,
) -> bool:
    if not isinstance(authority, dict) or set(authority) != {
        "schema",
        "record_kind",
        "target",
        "standard",
        "offline_verification",
        "authenticated_registry",
        "immutable_grail_boundary",
    }:
        return False
    target = authority.get("target")
    standard = authority.get("standard")
    offline = authority.get("offline_verification")
    registry = authority.get("authenticated_registry")
    boundary = authority.get("immutable_grail_boundary")
    if (
        authority.get("schema") != "rapp-authority-pin/1.0"
        or authority.get("record_kind") != "structural-authority-pin"
        or not status_valid
        or not isinstance(target, dict)
        or set(target) != {"repository", "status", "status_path"}
        or target.get("repository") != target_model["target"]
        or target.get("status") != "not-yet-fully-rapp-1-conformant"
        or target.get("status_path") != "RAPP1_STATUS.md"
        or not isinstance(standard, dict)
        or set(standard)
        != {
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
        or standard.get("repository") != current_model["repository"]
        or standard.get("commit") != target_model["commit"]
        or standard.get("path") != "SPEC.md"
        or standard.get("sha256") != target_model["sha256"]
        or standard.get("byte_length") != target_model["byte_length"]
        or standard.get("wire_tag") != "rapp/1"
        or standard.get("revision") != "rev-5"
        or standard.get("canonical_url")
        != (
            f"https://github.com/{current_model['repository']}/blob/"
            f"{target_model['commit']}/SPEC.md"
        )
        or standard.get("retrieval_url")
        != (
            f"https://raw.githubusercontent.com/{current_model['repository']}/"
            f"{target_model['commit']}/SPEC.md"
        )
        or not isinstance(offline, dict)
        or set(offline) != {"strategy", "fixture", "vendored_spec_bytes", "reason"}
        or offline.get("strategy") != "metadata-fixture"
        or offline.get("fixture") != "tests/fixtures/rapp1-spec-rev5.json"
        or offline.get("vendored_spec_bytes") is not False
        or not _is_nonempty_string(offline.get("reason"))
        or not isinstance(registry, dict)
        or set(registry) != {"is_section_13_registry", "statement"}
        or registry.get("is_section_13_registry") is not False
        or registry.get("statement")
        != (
            "This record is a structural authority pin only. It is not an "
            "authenticated RAPP/1 section 13 registry and must not be accepted as one."
        )
        or not isinstance(boundary, dict)
        or set(boundary)
        != {
            "repository",
            "tag",
            "pin_record",
            "policy",
            "implementation_policy",
            "frozen",
        }
        or boundary.get("repository") != "kody-w/rapp-installer"
        or boundary.get("tag") != "brainstem-v0.6.9"
        or boundary.get("pin_record") != "KERNEL_PIN.json"
        or boundary.get("policy") != "read-only"
        or not _is_nonempty_string(boundary.get("implementation_policy"))
    ):
        return False
    frozen = boundary.get("frozen")
    return (
        isinstance(frozen, dict)
        and set(frozen)
        == {
            "rapp_brainstem/brainstem.py",
            "rapp_brainstem/agents/basic_agent.py",
            "rapp_brainstem/VERSION",
        }
        and all(
            isinstance(value, str)
            and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            for value in frozen.values()
        )
    )


def _owner_action_ledger_valid(
    actions: Any,
    *,
    current_model: dict[str, Any],
    target_model: dict[str, Any],
) -> bool:
    if not isinstance(actions, dict) or set(actions) != {
        "schema",
        "record_kind",
        "status",
        "authority_state",
        "is_section_13_registry",
        "authenticated_acceptance_allowed",
        "statement",
        "authority",
        "audit_evidence",
        "current_evidence",
        "known_evidence",
        "candidate_namespaces",
        "required_registry_policies",
        "status_blocker_map",
        "actions",
    }:
        return False
    authority = actions.get("authority")
    action_records = actions.get("actions")
    blocker_map = actions.get("status_blocker_map")
    action_keys = {
        "id",
        "title",
        "issue_title",
        "status",
        "why",
        "what",
        "where",
        "when",
        "how",
        "prerequisites",
        "owner_inputs",
        "acceptance_tests",
        "rollback_or_retirement",
    }
    if (
        actions.get("schema") != "rapp-owner-action-ledger/1.0"
        or actions.get("record_kind") != "candidate-owner-action-ledger"
        or actions.get("status") != "candidate"
        or actions.get("authority_state") != "owner-action-required"
        or actions.get("is_section_13_registry") is not False
        or actions.get("authenticated_acceptance_allowed") is not False
        or not _is_nonempty_string(actions.get("statement"))
        or not isinstance(authority, dict)
        or set(authority)
        != {
            "structural_pin",
            "status",
            "constitution",
            "standard_repository",
            "standard_commit",
            "standard_path",
            "standard_sha256",
            "standard_sections",
        }
        or authority.get("structural_pin") != "RAPP1_AUTHORITY.json"
        or authority.get("status") != "RAPP1_STATUS.md"
        or not _is_nonempty_string(authority.get("constitution"))
        or authority.get("standard_repository") != current_model["repository"]
        or authority.get("standard_commit") != target_model["commit"]
        or authority.get("standard_path") != "SPEC.md"
        or authority.get("standard_sha256") != target_model["sha256"]
        or not isinstance(authority.get("standard_sections"), list)
        or not authority["standard_sections"]
        or not all(_is_nonempty_string(item) for item in authority["standard_sections"])
        or not all(
            isinstance(actions.get(key), dict) and bool(actions[key])
            for key in (
                "audit_evidence",
                "current_evidence",
                "known_evidence",
                "candidate_namespaces",
                "required_registry_policies",
            )
        )
        or not isinstance(blocker_map, dict)
        or not blocker_map
        or not all(
            _is_nonempty_string(key) and _is_nonempty_string(value)
            for key, value in blocker_map.items()
        )
        or not isinstance(action_records, list)
        or not action_records
    ):
        return False
    action_ids: list[str] = []
    for action in action_records:
        if (
            not isinstance(action, dict)
            or set(action) != action_keys
            or not _is_nonempty_string(action.get("id"))
            or action.get("status") != "owner-action-required"
            or not all(
                _is_nonempty_string(action.get(key))
                for key in ("title", "issue_title", "why", "what", "when")
            )
            or not isinstance(action.get("where"), dict)
            or not action["where"]
            or not isinstance(action.get("how"), list)
            or not action["how"]
            or not isinstance(action.get("prerequisites"), list)
            or not action["prerequisites"]
            or not isinstance(action.get("owner_inputs"), dict)
            or not action["owner_inputs"]
            or not isinstance(action.get("acceptance_tests"), list)
            or not action["acceptance_tests"]
            or not isinstance(action.get("rollback_or_retirement"), dict)
            or set(action["rollback_or_retirement"])
            != {"on_failure", "retirement_outcome"}
        ):
            return False
        action_ids.append(action["id"])
    return (
        len(action_ids) == len(set(action_ids))
        and set(blocker_map.values()) <= set(action_ids)
        and "owner-publish-authenticated-registry" in action_ids
    )


def inspect_authority(root: str) -> AuthorityReport:
    organism = Organism(root, allow_drift=True)
    specimen = SafeSpecimen(organism)
    model = organism.authority_paths
    current_model = model["normative_source_current"]
    map_model = model["map_structural_pin"]
    target_model = model["target_structural_pin"]
    target_context = model["retired_public_target"]
    spine_model = model["spine_pin_claim"]
    normative_source_commit = organism.organ("rapp-1")["commit"]
    findings: list[str] = []

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
        map_status_organ, map_status_path = _snapshot_location(
            map_model["status_path"]
        )
        map_status = _status_heading(
            specimen.read_text(map_status_organ, map_status_path)
        )
        map_status_valid = map_status == "NOT YET FULLY RAPP/1 CONFORMANT"
    except Exception as exc:
        map_status = "STATUS UNAVAILABLE"
        map_status_valid = False
        findings.append(f"rapp-map status unavailable or invalid: {exc}")

    try:
        target_status_organ, target_status_path = _snapshot_location(
            model["target_status"]
        )
        status_state = _status_heading(
            specimen.read_text(target_status_organ, target_status_path)
        )
        target_status_valid = status_state == "NOT YET FULLY RAPP/1 CONFORMANT"
    except Exception as exc:
        status_state = "STATUS UNAVAILABLE"
        target_status_valid = False
        findings.append(f"target status unavailable or invalid: {exc}")

    try:
        target_organ, target_path = _snapshot_location(target_model["record_path"])
        authority = strict_loads(specimen.read_bytes(target_organ, target_path))
    except Exception as exc:
        authority = {}
        findings.append(f"authority record unavailable or invalid: {exc}")
    standard = authority.get("standard", {}) if isinstance(authority, dict) else {}
    target_pin_valid = _target_authority_record_valid(
        authority,
        current_model=current_model,
        target_model=target_model,
        status_valid=target_status_valid,
    )
    if not target_pin_valid:
        findings.append(
            "RAPP target structural pin or one of its authority subrecords is invalid"
        )

    try:
        map_organ, map_path = _snapshot_location(map_model["record_path"])
        map_pin = strict_loads(specimen.read_bytes(map_organ, map_path))
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
        and map_pin.get("authority_scope") == map_model["authority_scope"]
        and map_pin.get("raw_url")
        == (
            f"https://raw.githubusercontent.com/{current_model['repository']}/"
            f"{map_model['commit']}/SPEC.md"
        )
        and map_pin.get("structural_pin_only") is map_model["structural_pin_only"]
        and map_pin.get("authenticated_registry_acceptance")
        is map_model["authenticated_registry_acceptance"]
        and map_status_valid
    )
    if not map_pin_valid:
        findings.append(
            "rapp-map scope, status, or structural pin does not match its "
            "fail-closed authority contract"
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
    if target_pin_valid and not target_matches_current:
        findings.append(
            f"RAPP target pins older {target_model['byte_length']:,}-byte SPEC bytes and drifts from the "
            "user-designated current kody-w/rapp-1 source; the target pin does not redefine the standard"
        )
    if not map_matches_current:
        findings.append("rapp-map pin does not match the captured current normative SPEC bytes")
    try:
        spine_organ, spine_path = _snapshot_location(spine_model["evidence_path"])
        spine_crawl = specimen.read_text(spine_organ, spine_path)
        observed = spine_model["observed_old_commit"]
        spine_observed_pin = observed if observed in spine_crawl else None
    except Exception as exc:
        spine_observed_pin = None
        findings.append(f"rapp-spine pin evidence unavailable: {exc}")
    spine_equals_map = (
        spine_observed_pin is not None
        and map_pin_valid
        and map_pin.get("commit") is not None
        and spine_observed_pin == map_pin.get("commit")
    )
    if spine_observed_pin is not None and not spine_equals_map:
        findings.append(
            f"rapp-spine's old {spine_observed_pin[:7]} pin is not equal to "
            f"rapp-map's current {map_pin.get('commit', '')[:7]} pin"
        )

    try:
        actions_organ, actions_path = _snapshot_location(model["owner_actions"])
        actions = strict_loads(specimen.read_bytes(actions_organ, actions_path))
        ledger_valid = _owner_action_ledger_valid(
            actions,
            current_model=current_model,
            target_model=target_model,
        )
        if ledger_valid:
            blockers = tuple(action["id"] for action in actions["actions"])
        else:
            blockers = ("owner-action-ledger-invalid",)
            findings.append("owner-action ledger shape or fail-closed state is invalid")
    except Exception as exc:
        blockers = ("owner-action-ledger-unavailable",)
        findings.append(f"owner-action ledger unavailable: {exc}")
    authenticated_registry = model["authenticated_registry"]["state"]
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
        map_authority_scope=map_pin.get("authority_scope"),
        map_status=map_status,
        map_status_valid=map_status_valid,
        target_pin_valid=target_pin_valid,
        target_pin_commit=standard.get("commit"),
        target_pin_sha256=standard.get("sha256"),
        target_pin_byte_length=standard.get("byte_length"),
        target_pin_state=target_pin_state,
        target_product_lifecycle=target_context["product_lifecycle"],
        target_record_currency=target_context["target_record_currency"],
        spine_observed_pin=spine_observed_pin,
        spine_pin_equals_map_current=spine_equals_map,
        target_status=status_state,
        authenticated_registry=authenticated_registry,
        owner_action_blockers=blockers,
        full_conformance=False,
        findings=tuple(findings),
    )
