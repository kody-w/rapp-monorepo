"""Strict organism inventory and no-follow specimen content access."""

from __future__ import annotations

import os
import errno
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import InventoryError, SpecimenAccessError
from .json_profile import strict_loads

MANIFEST_SCHEMA = "rapp-monorepo/1.0"
ORGANISM_SCHEMA = "rapp-organism/1.0"
_ORGAN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")


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

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).absolute()
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
            or not isinstance(current.get("repository"), str)
            or not current.get("repository")
            or not isinstance(current.get("repository_url"), str)
            or not isinstance(current.get("sha256"), str)
            or not isinstance(current.get("byte_length"), int)
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
        repos = self.manifest.get("repos")
        systems = self.registry.get("systems")
        if not isinstance(repos, list) or not isinstance(systems, list):
            raise InventoryError("manifest repos and organism systems must be arrays")
        names: list[str] = []
        for record in repos:
            if not isinstance(record, dict) or not isinstance(record.get("repo"), str):
                raise InventoryError("each manifest repository must have a string repo")
            validate_organ_name(record["repo"])
            if not isinstance(record.get("commit"), str):
                raise InventoryError("each manifest repository must have a commit pin")
            names.append(record["repo"])
        if len(names) != len(set(names)):
            raise InventoryError("manifest repository names must be unique")
        classified: list[str] = []
        system_ids: set[str] = set()
        for system in systems:
            if (
                not isinstance(system, dict)
                or not isinstance(system.get("id"), str)
                or not isinstance(system.get("name"), str)
                or not isinstance(system.get("lifecycle"), str)
                or not isinstance(system.get("authority"), str)
                or not isinstance(system.get("organs"), list)
            ):
                raise InventoryError("each system requires id/name/lifecycle/authority/organs")
            if system["id"] in system_ids:
                raise InventoryError("system ids must be unique")
            system_ids.add(system["id"])
            if not all(isinstance(name, str) for name in system["organs"]):
                raise InventoryError("system organs must be strings")
            for name in system["organs"]:
                validate_organ_name(name)
            classified.extend(system["organs"])
        if len(classified) != len(set(classified)):
            raise InventoryError("every organ must be classified exactly once")
        projections = self.registry.get("projections")
        relationships = self.registry.get("relationships")
        conflicts = self.registry.get("alignment_conflicts")
        if not isinstance(projections, list) or not isinstance(relationships, list) or not isinstance(
            conflicts, list
        ):
            raise InventoryError(
                "ORGANISM.json requires projections, relationships, and alignment_conflicts arrays"
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
            }
            if (
                not isinstance(projection, dict)
                or not required <= set(projection)
                or not set(projection) <= required | {"omitted_blobs"}
            ):
                raise InventoryError("projection evidence has the wrong machine-readable shape")
            if projection["schema"] != "rapp-projection-evidence/1.0":
                raise InventoryError("projection schema is invalid")
            validate_organ_name(projection["organ"])
            if projection["organ"] not in names or projection["id"] in projection_ids:
                raise InventoryError("projection organ is absent or projection id is duplicated")
            projection_ids.add(projection["id"])
            if not isinstance(projection["generated_from"], list) or not projection[
                "generated_from"
            ]:
                raise InventoryError("projection generator provenance is incomplete")
        if not all(isinstance(item, dict) and isinstance(item.get("type"), str) for item in relationships):
            raise InventoryError("relationships require typed objects")
        if not all(
            isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and isinstance(item.get("type"), str)
            and isinstance(item.get("evidence_mode"), str)
            for item in conflicts
        ):
            raise InventoryError("alignment conflicts require id/type/evidence_mode")

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
            organ: system["id"]
            for system in self.registry["systems"]
            for organ in system["organs"]
        }
        result = []
        for record in self.manifest["repos"]:
            item = dict(record)
            item["system"] = membership.get(record["repo"])
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

    def summary(self) -> dict[str, Any]:
        return {
            "schema": self.registry["schema"],
            "conformance": self.registry["conformance"],
            "snapshot": {
                "owner": self.manifest.get("owner"),
                "captured_at": self.manifest.get("captured_at"),
                **self.statistics.as_dict(),
            },
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
        parts = ("repos", organ, *self._parts(path))
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
