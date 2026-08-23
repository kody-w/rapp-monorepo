"""Deterministic RAPP/1 eggs with bounded recursive verification and safe extraction."""

from __future__ import annotations

import errno
import io
import os
import re
import stat
import struct
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

from .errors import EggValidationError, TrustError
from .identity import Rappid, validate_rappid
from .json_profile import H, Hb, MAX_CANONICAL_BYTES, canonical_bytes, strict_loads
from .trust import SignatureTrust, VerifiedRegistry, parse_detached_jws, verify_detached_jws

MANIFEST_KEYS = frozenset(
    {"schema", "variant", "rappid", "created_utc", "contents", "payload", "sig"}
)
VARIANTS = frozenset(
    {"organism", "rapplication", "session", "invite", "neighborhood", "estate"}
)
JSON_VARIANTS = frozenset({"session", "invite"})
ZIP_VARIANTS = VARIANTS - JSON_VARIANTS
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
MAX_EGG_BYTES = 64 * 1024 * 1024
MAX_ENTRY_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 4096
MAX_NESTING = 8


def _valid_utc(value: Any) -> bool:
    if not isinstance(value, str) or not _UTC_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return value[17:19] != "60"


def _safe_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise EggValidationError("egg content path must be non-empty")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise EggValidationError("egg paths must be relative POSIX paths")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise EggValidationError("egg paths may not contain empty, dot, or traversal segments")
    if unicodedata.normalize("NFC", value) != value:
        raise EggValidationError("new egg paths must be Unicode NFC")
    return value


def _unsigned_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "sig"}


def _validate_manifest(manifest: Any) -> tuple[str, Rappid]:
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS:
        raise EggValidationError("manifest must have exactly the seven RAPP/1 members")
    if manifest["schema"] != "rapp/1-egg" or manifest["variant"] not in VARIANTS:
        raise EggValidationError("egg schema or variant is invalid")
    rappid = validate_rappid(manifest["rappid"])
    if not _valid_utc(manifest["created_utc"]):
        raise EggValidationError("created_utc must use exact millisecond UTC form")
    if not isinstance(manifest["contents"], list) or not isinstance(manifest["payload"], dict):
        raise EggValidationError("contents must be an array and payload an object")
    seen: set[str] = set()
    paths: list[str] = []
    for item in manifest["contents"]:
        if not isinstance(item, dict) or set(item) != {"path", "hash"}:
            raise EggValidationError("each content record must be exactly {path,hash}")
        path = _safe_path(item["path"])
        if path == "manifest.json" or path in seen:
            raise EggValidationError("manifest.json or duplicate content path is forbidden")
        seen.add(path)
        paths.append(path)
        if not isinstance(item["hash"], str) or not _HEX_RE.fullmatch(item["hash"]):
            raise EggValidationError("content hash must be 64 lowercase hex")
    if paths != sorted(paths, key=lambda path: path.encode("utf-8")):
        raise EggValidationError("contents must be UTF-8-byte sorted")
    if manifest["sig"] is not None:
        parse_detached_jws(manifest["sig"])
    canonical_bytes(manifest)
    return manifest["variant"], rappid


@dataclass
class _Budget:
    max_depth: int = MAX_NESTING
    max_bytes: int = MAX_EGG_BYTES
    max_entries: int = MAX_ENTRIES
    bytes_seen: int = 0
    entries_seen: int = 0

    def charge(self, *, depth: int, byte_count: int, entries: int) -> None:
        if depth > self.max_depth:
            raise EggValidationError("egg nesting exceeds configured bound")
        self.bytes_seen += byte_count
        self.entries_seen += entries
        if self.bytes_seen > self.max_bytes:
            raise EggValidationError("recursive egg bytes exceed aggregate bound")
        if self.entries_seen > self.max_entries:
            raise EggValidationError("recursive egg entries exceed aggregate bound")


@dataclass(frozen=True)
class EggInspection:
    manifest: Mapping[str, Any]
    egg_hash: str
    container: str
    files: Mapping[str, bytes]
    children: Mapping[str, "EggInspection"]
    signature_state: str
    semantics: str
    registry_seq: int | None = None
    signature_trust: SignatureTrust | None = None
    aggregate_bytes: int = 0
    aggregate_entries: int = 0


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _validate_variant(
    manifest: Mapping[str, Any],
    files: Mapping[str, bytes],
    children: Mapping[str, EggInspection],
) -> None:
    variant = manifest["variant"]
    paths = set(files)
    payload = manifest["payload"]
    if variant in JSON_VARIANTS and (files or manifest["contents"] != []):
        raise EggValidationError("JSON egg variants require contents=[] and no packed files")
    if variant == "organism":
        if not {"rappid.json", "soul.md"} <= paths:
            raise EggValidationError("organism egg requires rappid.json and soul.md")
    elif variant == "rapplication":
        if not {"rappid.json", "agent.py"} <= paths:
            raise EggValidationError("rapplication egg requires rappid.json and root agent.py")
        allowed = {"rappid.json", "agent.py", "ui.html"}
        if any(path not in allowed and not path.startswith("state/") for path in paths):
            raise EggValidationError("rapplication contains a path outside its ratified layout")
    elif variant == "session":
        if (
            set(payload) != {"runtime", "transcript"}
            or not isinstance(payload["runtime"], str)
            or not isinstance(payload["transcript"], list)
            or not all(isinstance(turn, dict) for turn in payload["transcript"])
        ):
            raise EggValidationError("session payload shape is invalid")
    elif variant == "invite":
        if (
            set(payload) != {"target_rappid", "target_url", "target_kind"}
            or not isinstance(payload["target_url"], str)
            or payload["target_kind"] not in {"neighborhood", "estate"}
        ):
            raise EggValidationError("invite payload shape is invalid")
        validate_rappid(payload["target_rappid"])
        if manifest["sig"] is None:
            raise EggValidationError("invite signature is required")
    elif variant in {"neighborhood", "estate"}:
        member_key = "members" if variant == "neighborhood" else "neighborhoods"
        child_variant = "organism" if variant == "neighborhood" else "neighborhood"
        if set(payload) != {member_key} or not isinstance(payload[member_key], list):
            raise EggValidationError(f"{variant} payload shape is invalid")
        members = payload[member_key]
        if not all(isinstance(member, str) for member in members) or len(members) != len(
            set(members)
        ):
            raise EggValidationError(f"{variant} members must be unique rappids")
        parsed = [validate_rappid(member) for member in members]
        expected = {f"{item.owner}--{item.slug}.egg": item.value for item in parsed}
        if len(expected) != len(parsed):
            raise EggValidationError(
                f"{variant} member rappids collide on owner--slug child filename"
            )
        if set(files) != set(expected) or set(children) != set(expected):
            raise EggValidationError(f"{variant} must contain exactly one root sub-egg per member")
        for path, member in expected.items():
            child = children[path]
            if child.manifest["rappid"] != member:
                raise EggValidationError("sub-egg rappid does not match payload membership")
            if child.manifest["variant"] != child_variant:
                raise EggValidationError(
                    f"{variant} children must use variant {child_variant!r}"
                )


def _patch_utf8_flags(data: bytes) -> bytes:
    result = bytearray(data)
    eocd = result.rfind(b"PK\x05\x06")
    if eocd < 0:
        raise EggValidationError("generated ZIP lacks EOCD")
    count = struct.unpack_from("<H", result, eocd + 10)[0]
    offset = struct.unpack_from("<I", result, eocd + 16)[0]
    for _ in range(count):
        if result[offset : offset + 4] != b"PK\x01\x02":
            raise EggValidationError("generated ZIP central directory is invalid")
        struct.pack_into("<H", result, offset + 8, struct.unpack_from("<H", result, offset + 8)[0] | 0x800)
        local_offset = struct.unpack_from("<I", result, offset + 42)[0]
        struct.pack_into(
            "<H",
            result,
            local_offset + 6,
            struct.unpack_from("<H", result, local_offset + 6)[0] | 0x800,
        )
        name_len, extra_len, comment_len = struct.unpack_from("<HHH", result, offset + 28)
        offset += 46 + name_len + extra_len + comment_len
    return bytes(result)


def _zip_bytes(manifest: Mapping[str, Any], files: Mapping[str, bytes]) -> bytes:
    stream = io.BytesIO()
    ordered = [("manifest.json", canonical_bytes(manifest))]
    ordered.extend((item["path"], files[item["path"]]) for item in manifest["contents"])
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for path, octets in ordered:
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 0
            info.external_attr = 0
            info.extra = b""
            info.comment = b""
            archive.writestr(info, octets)
    return _patch_utf8_flags(stream.getvalue())


def _read_zip(data: bytes, budget: _Budget, depth: int) -> tuple[dict[str, Any], dict[str, bytes]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data), "r")
    except (zipfile.BadZipFile, OSError) as exc:
        raise EggValidationError("egg is not a valid ZIP") from exc
    with archive:
        infos = archive.infolist()
        budget.charge(depth=depth, byte_count=len(data), entries=len(infos))
        if archive.comment:
            raise EggValidationError("ZIP archive comments are forbidden")
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or not names or names[0] != "manifest.json":
            raise EggValidationError("ZIP entry set/order or manifest root is invalid")
        for info in infos:
            _safe_path(info.filename)
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            if (
                info.is_dir()
                or stat.S_ISLNK(unix_mode)
                or info.compress_type != zipfile.ZIP_STORED
                or info.date_time != (1980, 1, 1, 0, 0, 0)
                or info.extra
                or info.comment
                or not (info.flag_bits & 0x800)
                or info.file_size > MAX_ENTRY_BYTES
                or info.compress_size != info.file_size
            ):
                raise EggValidationError("ZIP metadata violates deterministic/safe profile")
        try:
            manifest_octets = archive.read("manifest.json")
        except (KeyError, RuntimeError, zipfile.BadZipFile) as exc:
            raise EggValidationError("cannot read manifest.json") from exc
        if len(manifest_octets) > MAX_CANONICAL_BYTES:
            raise EggValidationError("manifest exceeds canonical profile bound")
        manifest = strict_loads(manifest_octets)
        if canonical_bytes(manifest) != manifest_octets:
            raise EggValidationError("manifest.json bytes are not canonical")
        _validate_manifest(manifest)
        expected_names = ["manifest.json"] + [item["path"] for item in manifest["contents"]]
        if names != expected_names:
            raise EggValidationError("ZIP entries do not exactly equal manifest contents in order")
        files: dict[str, bytes] = {}
        for item in manifest["contents"]:
            try:
                octets = archive.read(item["path"])
            except (RuntimeError, zipfile.BadZipFile) as exc:
                raise EggValidationError("cannot safely read ZIP entry") from exc
            if Hb("rapp/1:egg", octets) != item["hash"]:
                raise EggValidationError(f"content hash mismatch for {item['path']}")
            files[item["path"]] = octets
    if data != _zip_bytes(manifest, files):
        raise EggValidationError("ZIP bytes do not equal deterministic reconstruction")
    return manifest, files


def _process_egg(
    data: bytes,
    *,
    budget: _Budget,
    depth: int,
    registry: VerifiedRegistry | None,
) -> EggInspection:
    if not isinstance(data, bytes) or not data:
        raise EggValidationError("egg must be non-empty bytes")
    if data.startswith(b"PK\x03\x04"):
        manifest, files = _read_zip(data, budget, depth)
        container = "zip"
        if manifest["variant"] not in ZIP_VARIANTS:
            raise EggValidationError("JSON variant may not use ZIP container")
    else:
        budget.charge(depth=depth, byte_count=len(data), entries=1)
        manifest = strict_loads(data)
        if canonical_bytes(manifest) != data:
            raise EggValidationError("JSON egg bytes must be exactly canonical(manifest)")
        _validate_manifest(manifest)
        if manifest["variant"] not in JSON_VARIANTS:
            raise EggValidationError("tree variant must use ZIP container")
        files, container = {}, "json"
    _validate_manifest(manifest)
    children: dict[str, EggInspection] = {}
    if manifest["variant"] in {"neighborhood", "estate"}:
        for path, octets in files.items():
            children[path] = _process_egg(
                octets, budget=budget, depth=depth + 1, registry=registry
            )
    _validate_variant(manifest, files, children)
    signature_trust = None
    if registry is not None:
        registry.require_egg_variant(manifest["variant"])
        if manifest["sig"] is not None:
            signature_trust = verify_detached_jws(
                manifest["sig"],
                canonical_bytes(_unsigned_manifest(manifest)),
                registry,
                artifact_utc=manifest["created_utc"],
                require_estate_owner=manifest["variant"] == "invite",
            )
        elif manifest["variant"] == "invite":
            raise EggValidationError("invite signature is required")
        semantics = "verified-with-authenticated-registry"
        signature_state = "verified" if signature_trust else "absent"
        registry_seq = registry.registry_seq
    else:
        semantics = "structural-inspection"
        signature_state = "present-unverified" if manifest["sig"] else "absent"
        registry_seq = None
    return EggInspection(
        manifest=_freeze_json(manifest),
        egg_hash=H("rapp/1:egg-manifest", _unsigned_manifest(manifest)),
        container=container,
        files=MappingProxyType(dict(files)),
        children=MappingProxyType(children),
        signature_state=signature_state,
        semantics=semantics,
        registry_seq=registry_seq,
        signature_trust=signature_trust,
        aggregate_bytes=budget.bytes_seen,
        aggregate_entries=budget.entries_seen,
    )


def inspect_egg(
    data: bytes,
    *,
    max_depth: int = MAX_NESTING,
    max_aggregate_bytes: int = MAX_EGG_BYTES,
    max_aggregate_entries: int = MAX_ENTRIES,
) -> EggInspection:
    """Recursively inspect once without making an authenticated acceptance claim."""

    return _process_egg(
        data,
        budget=_Budget(max_depth, max_aggregate_bytes, max_aggregate_entries),
        depth=1,
        registry=None,
    )


def accept_egg(
    data: bytes,
    *,
    registry: VerifiedRegistry,
    max_depth: int = MAX_NESTING,
    max_aggregate_bytes: int = MAX_EGG_BYTES,
    max_aggregate_entries: int = MAX_ENTRIES,
) -> EggInspection:
    """Recursively verify once using an opaque authenticated registry proof."""

    if not isinstance(registry, VerifiedRegistry):
        raise TrustError("accept_egg requires a VerifiedRegistry proof")
    return _process_egg(
        data,
        budget=_Budget(max_depth, max_aggregate_bytes, max_aggregate_entries),
        depth=1,
        registry=registry,
    )


def pack_egg(
    *,
    variant: str,
    rappid: str,
    created_utc: str,
    payload: dict[str, Any],
    files: Mapping[str, bytes] | None,
    registry: VerifiedRegistry,
    signer: Callable[[bytes], str] | None = None,
) -> bytes:
    """Produce deterministic bytes under an authenticated registered namespace."""

    if not isinstance(registry, VerifiedRegistry):
        raise TrustError("pack_egg requires a VerifiedRegistry proof")
    registry.require_egg_variant(variant)
    validate_rappid(rappid)
    if not _valid_utc(created_utc) or not isinstance(payload, dict):
        raise EggValidationError("invalid created_utc or payload")
    packed: dict[str, bytes] = {}
    for path, octets in (files or {}).items():
        safe = _safe_path(path)
        if safe == "manifest.json" or not isinstance(octets, bytes):
            raise EggValidationError("packed files must be byte strings excluding manifest.json")
        if len(octets) > MAX_ENTRY_BYTES:
            raise EggValidationError("packed file exceeds entry bound")
        packed[safe] = octets
    manifest: dict[str, Any] = {
        "schema": "rapp/1-egg",
        "variant": variant,
        "rappid": rappid,
        "created_utc": created_utc,
        "contents": [
            {"path": path, "hash": Hb("rapp/1:egg", packed[path])}
            for path in sorted(packed, key=lambda item: item.encode("utf-8"))
        ],
        "payload": payload,
        "sig": None,
    }
    if signer is not None:
        manifest["sig"] = signer(canonical_bytes(_unsigned_manifest(manifest)))
        parse_detached_jws(manifest["sig"])
    octets = canonical_bytes(manifest) if variant in JSON_VARIANTS else _zip_bytes(manifest, packed)
    accept_egg(octets, registry=registry)
    return octets


def _require_extract_primitives() -> None:
    if (
        os.name != "posix"
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or not {os.open, os.mkdir, os.stat, os.unlink, os.rmdir} <= os.supports_dir_fd
    ):
        raise EggValidationError(
            "safe extraction requires descriptor-relative mkdir/open/unlink with "
            "O_DIRECTORY and O_NOFOLLOW"
        )


def _open_absolute_directory(path: Path) -> int:
    if not path.is_absolute():
        raise EggValidationError("internal extraction path must be absolute")
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            next_descriptor = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_child_directory(parent: int, name: str, *, create: bool) -> tuple[int, bool]:
    created = False
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
            created = True
        except FileExistsError:
            pass
    try:
        descriptor = os.open(
            name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent
        )
    except OSError as exc:
        raise EggValidationError("extraction path contains a symlink or non-directory") from exc
    return descriptor, created


def extract_egg(
    data: bytes,
    destination: str | os.PathLike[str],
    *,
    registry: VerifiedRegistry,
) -> list[Path]:
    """Verify first, then extract exclusively through descriptor-relative operations."""

    _require_extract_primitives()
    accepted = accept_egg(data, registry=registry)
    target = Path(destination).absolute()
    parent = _open_absolute_directory(target.parent)
    destination_fd: int | None = None
    created_dirs: list[tuple[str, ...]] = []
    created_files: list[tuple[str, ...]] = []
    try:
        try:
            os.mkdir(target.name, 0o700, dir_fd=parent)
        except FileExistsError as exc:
            raise EggValidationError("extraction destination must not already exist") from exc
        destination_fd = os.open(
            target.name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent,
        )
        written: list[Path] = []
        for relative, octets in accepted.files.items():
            parts = tuple(_safe_path(relative).split("/"))
            directory = os.dup(destination_fd)
            try:
                prefix: list[str] = []
                for part in parts[:-1]:
                    prefix.append(part)
                    next_directory, created = _open_child_directory(directory, part, create=True)
                    if created:
                        created_dirs.append(tuple(prefix))
                    os.close(directory)
                    directory = next_directory
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                try:
                    output = os.open(parts[-1], flags, 0o600, dir_fd=directory)
                except OSError as exc:
                    if exc.errno == errno.ELOOP:
                        raise EggValidationError("extraction target is a symlink") from exc
                    raise
                try:
                    remaining = memoryview(octets)
                    while remaining:
                        count = os.write(output, remaining)
                        if count <= 0:
                            raise EggValidationError("short write while extracting egg")
                        remaining = remaining[count:]
                finally:
                    os.close(output)
                created_files.append(parts)
                written.append(target.joinpath(*parts))
            finally:
                os.close(directory)
        return written
    except Exception:
        if destination_fd is not None:
            for parts in reversed(created_files):
                directory = os.dup(destination_fd)
                try:
                    for part in parts[:-1]:
                        next_directory, _ = _open_child_directory(directory, part, create=False)
                        os.close(directory)
                        directory = next_directory
                    os.unlink(parts[-1], dir_fd=directory)
                except OSError:
                    pass
                finally:
                    os.close(directory)
            for parts in reversed(created_dirs):
                directory = os.dup(destination_fd)
                try:
                    for part in parts[:-1]:
                        next_directory, _ = _open_child_directory(directory, part, create=False)
                        os.close(directory)
                        directory = next_directory
                    os.rmdir(parts[-1], dir_fd=directory)
                except OSError:
                    pass
                finally:
                    os.close(directory)
            os.close(destination_fd)
            destination_fd = None
        try:
            os.rmdir(target.name, dir_fd=parent)
        except OSError:
            pass
        raise
    finally:
        if destination_fd is not None:
            os.close(destination_fd)
        os.close(parent)
