"""RAPP/1 detached JWS and section-13 registry verification."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import sqlite3
import threading
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from .errors import TrustError, ValidationError
from .identity import (
    canonical_spki_der,
    classify_stream_id,
    validate_kind,
    validate_rappid,
)
from .json_profile import Hb, canonical_bytes, strict_loads

_B64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
_PROVISIONAL_RAPPID_RE = re.compile(
    r"^rappid:@(?P<owner>[a-z0-9]+(?:-[a-z0-9]+)*)/"
    r"(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*):[0-9a-f]{32}$"
)
_HEADER_KEYS = frozenset({"alg", "b64", "crit", "kid"})
_REGISTRY_KEYS = frozenset({"schema", "registry_seq", "entries", "sig"})
_UINT53_MAX = (1 << 53) - 1
_PROOF_SEAL = object()


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    if not value or "=" in value or not _B64URL_RE.fullmatch(value):
        raise ValidationError("JWS segment is not unpadded base64url")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, binascii.Error) as exc:
        raise ValidationError("invalid JWS base64url") from exc
    if _b64url_encode(decoded) != value:
        raise ValidationError("JWS segment is not canonical base64url")
    return decoded


def _standard_b64_decode(value: Any) -> bytes:
    if not isinstance(value, str) or not value:
        raise TrustError("spki_der_b64 must be non-empty standard base64")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise TrustError("spki_der_b64 is invalid") from exc
    if base64.b64encode(decoded).decode("ascii") != value:
        raise TrustError("spki_der_b64 is not canonical standard base64")
    return canonical_spki_der(decoded)


def _uint53(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= _UINT53_MAX


def _valid_utc(value: Any) -> bool:
    if not isinstance(value, str) or not _UTC_RE.fullmatch(value) or value[17:19] == "60":
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return True


def _require_exact(entry: Mapping[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    keys = set(entry)
    if not required <= keys or not keys <= required | optional:
        raise TrustError(
            f"registry {entry.get('type', 'entry')!r} has wrong members: {sorted(keys)}"
        )


@dataclass(frozen=True)
class DetachedJWS:
    compact: str
    protected_segment: str
    header: Mapping[str, Any]
    signature: bytes

    def signing_input(self, payload: bytes) -> bytes:
        return self.protected_segment.encode("ascii") + b"." + payload


def parse_detached_jws(value: str) -> DetachedJWS:
    if not isinstance(value, str):
        raise ValidationError("sig must be a string")
    parts = value.split(".")
    if len(parts) != 3 or parts[1] != "":
        raise ValidationError("JWS must be detached compact serialization")
    header_octets = _b64url_decode(parts[0])
    signature = _b64url_decode(parts[2])
    header = strict_loads(header_octets)
    if not isinstance(header, dict) or set(header) != _HEADER_KEYS:
        raise ValidationError("JWS protected header has the wrong members")
    if canonical_bytes(header) != header_octets:
        raise ValidationError("JWS protected header is not canonical JSON")
    if header["alg"] not in {"EdDSA", "ES256"}:
        raise ValidationError("JWS alg must be EdDSA or ES256")
    if header["b64"] is not False or header["crit"] != ["b64"]:
        raise ValidationError("JWS must use b64=false with crit=['b64']")
    validate_rappid(header["kid"])
    if len(signature) != 64:
        raise ValidationError("RAPP/1 EdDSA and ES256 signatures are 64 octets")
    return DetachedJWS(value, parts[0], MappingProxyType(header), signature)


def _verify_with_spki(
    jws: DetachedJWS | str,
    payload: bytes,
    spki_der: bytes,
    expected_kid: str,
    *,
    allow_untagged_binding: bool = False,
) -> DetachedJWS:
    parsed = parse_detached_jws(jws) if isinstance(jws, str) else jws
    if parsed.header["kid"] != expected_kid:
        raise TrustError(f"signature kid must be {expected_kid}")
    canonical = canonical_spki_der(spki_der)
    expected_tail = validate_rappid(expected_kid).tail
    if Hb("rapp/1:rappid", canonical) != expected_tail:
        if not allow_untagged_binding or hashlib.sha256(canonical).hexdigest() != expected_tail:
            raise TrustError("SPKI does not bind to the expected rappid tail")
    from cryptography.hazmat.primitives import serialization

    key = serialization.load_der_public_key(canonical)
    signing_input = parsed.signing_input(payload)
    try:
        if parsed.header["alg"] == "EdDSA":
            if not isinstance(key, ed25519.Ed25519PublicKey):
                raise TrustError("EdDSA JWS does not resolve to an Ed25519 key")
            key.verify(parsed.signature, signing_input)
        else:
            if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
                key.curve, ec.SECP256R1
            ):
                raise TrustError("ES256 JWS does not resolve to a P-256 key")
            r = int.from_bytes(parsed.signature[:32], "big")
            s = int.from_bytes(parsed.signature[32:], "big")
            key.verify(encode_dss_signature(r, s), signing_input, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as exc:
        raise TrustError("JWS signature did not verify") from exc
    return parsed


class RegistrySequenceStore(Protocol):
    """Atomic monotonic persistence boundary for verified registry sequences."""

    def check_and_store(
        self, key: str, sequence: int, registry_hash: str, entries: list[dict[str, Any]]
    ) -> None: ...


def _entry_key(entry: Mapping[str, Any]) -> tuple[Any, ...]:
    entry_type = entry["type"]
    fields = {
        "protocol": ("name",),
        "kind": ("kind",),
        "egg-variant": ("variant",),
        "error-code": ("code",),
        "genesis": ("stream_id", "frame_hash"),
        "spki": ("rappid", "spki_der_b64"),
        "tombstone": ("rappid", "revoked_utc"),
        "re-anchor": ("old_rappid", "new_rappid", "utc"),
        "estate_owner": ("rappid",),
        "master-plan": ("repo", "path"),
    }[entry_type]
    return (entry_type, *(entry[field] for field in fields))


def _check_append_only(
    previous: list[dict[str, Any]], current: list[dict[str, Any]]
) -> None:
    current_by_key = {_entry_key(entry): entry for entry in current}
    if len(current_by_key) != len(current):
        raise TrustError("registry contains duplicate entry identities")
    for old in previous:
        key = _entry_key(old)
        if key not in current_by_key:
            if old["type"] == "estate_owner":
                current_owners = {
                    entry["rappid"]
                    for entry in current
                    if entry["type"] == "estate_owner"
                }
                if any(
                    entry["type"] == "re-anchor"
                    and entry["old_rappid"] == old["rappid"]
                    and entry["new_rappid"] in current_owners
                    for entry in current
                ):
                    continue
            raise TrustError("registry append-only history removed or renamed an entry")
        new = current_by_key[key]
        if new == old:
            continue
        allowed = dict(old)
        if allowed.get("deprecated") is False:
            allowed["deprecated"] = True
        if new != allowed:
            raise TrustError("registry append-only history mutated an existing entry")


class MemoryRegistrySequenceStore:
    """Process-persistent test/development store; production should use SQLite."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[int, str, list[dict[str, Any]]]] = {}
        self._lock = threading.Lock()

    def check_and_store(
        self, key: str, sequence: int, registry_hash: str, entries: list[dict[str, Any]]
    ) -> None:
        with self._lock:
            previous = self._values.get(key)
            if previous is not None:
                if sequence < previous[0]:
                    raise TrustError("registry rollback refused")
                if sequence == previous[0] and registry_hash != previous[1]:
                    raise TrustError("different registry bytes at an already verified sequence")
                if sequence > previous[0]:
                    _check_append_only(previous[2], entries)
            snapshot = strict_loads(canonical_bytes(entries))
            self._values[key] = (sequence, registry_hash, snapshot)


class SQLiteRegistrySequenceStore:
    """Cross-process monotonic state using an immediate SQLite transaction."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(Path(path).absolute())
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS registry_state "
                "(key TEXT PRIMARY KEY, sequence INTEGER NOT NULL, registry_hash TEXT NOT NULL,"
                "entries_json TEXT NOT NULL)"
            )

    def check_and_store(
        self, key: str, sequence: int, registry_hash: str, entries: list[dict[str, Any]]
    ) -> None:
        with sqlite3.connect(self.path, isolation_level=None) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT sequence, registry_hash, entries_json FROM registry_state WHERE key=?",
                (key,),
            ).fetchone()
            if row is not None:
                if sequence < row[0]:
                    connection.execute("ROLLBACK")
                    raise TrustError("registry rollback refused")
                if sequence == row[0] and registry_hash != row[1]:
                    connection.execute("ROLLBACK")
                    raise TrustError("different registry bytes at an already verified sequence")
                if sequence > row[0]:
                    _check_append_only(json.loads(row[2]), entries)
            entries_json = canonical_bytes(entries).decode("utf-8")
            connection.execute(
                "INSERT INTO registry_state(key,sequence,registry_hash,entries_json) VALUES(?,?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET sequence=excluded.sequence,"
                "registry_hash=excluded.registry_hash,entries_json=excluded.entries_json",
                (key, sequence, registry_hash, entries_json),
            )
            connection.execute("COMMIT")


@dataclass(frozen=True)
class _OwnerTenure:
    rappid: str
    start_utc: str
    end_utc: str | None

    def contains(self, utc: str) -> bool:
        return self.start_utc <= utc and (self.end_utc is None or utc < self.end_utc)


@dataclass(frozen=True)
class TrustedProvisionalResolution:
    """Explicit out-of-band evidence that a provisional id resolved to an owner."""

    provisional_rappid: str
    owner: str
    source: str

    def __post_init__(self) -> None:
        match = _PROVISIONAL_RAPPID_RE.fullmatch(self.provisional_rappid)
        if (
            match is None
            or self.owner != match.group("owner")
            or not isinstance(self.source, str)
            or not self.source
        ):
            raise ValidationError("trusted provisional resolution is invalid")


@dataclass(frozen=True)
class GenesisRegistration:
    stream_id: str
    frame_hash: str
    old_stream_id: str | None = None
    new_stream_id: str | None = None


class VerifiedRegistry:
    """Opaque proof created only after cryptographic, freshness, and rollback checks."""

    __slots__ = (
        "_anchor",
        "_source",
        "_sequence",
        "_registry_hash",
        "_verified_at",
        "_fetched_at",
        "_kind_families",
        "_active_kinds",
        "_egg_variants",
        "_error_codes",
        "_spki",
        "_tombstones",
        "_tenures",
        "_genesis",
        "_retired_streams",
        "_reanchor_cutovers",
        "_reanchor_cases",
        "_raw",
        "_seal",
        "_locked",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError("VerifiedRegistry proofs are produced only by verify_registry()")

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_locked", False):
            raise AttributeError("VerifiedRegistry is frozen")
        object.__setattr__(self, name, value)

    @property
    def anchor(self) -> str:
        self._assert_valid()
        return self._anchor

    @property
    def source(self) -> str:
        self._assert_valid()
        return self._source

    @property
    def registry_seq(self) -> int:
        self._assert_valid()
        return self._sequence

    @property
    def registry_hash(self) -> str:
        self._assert_valid()
        return self._registry_hash

    @property
    def verified_at(self) -> datetime:
        self._assert_valid()
        return self._verified_at

    @property
    def fetched_at(self) -> datetime:
        self._assert_valid()
        return self._fetched_at

    def _assert_valid(self) -> None:
        if getattr(self, "_seal", None) is not _PROOF_SEAL:
            raise TrustError("VerifiedRegistry object was not produced by verify_registry()")

    def kind_family(self, kind: str) -> str:
        self._assert_valid()
        try:
            return self._kind_families[kind]
        except KeyError as exc:
            raise TrustError(f"kind {kind!r} is not registered") from exc

    def active_kind_family(self, kind: str) -> str:
        family = self.kind_family(kind)
        if kind not in self._active_kinds:
            raise TrustError(f"kind {kind!r} is deprecated and cannot be produced")
        return family

    def require_egg_variant(self, variant: str) -> None:
        self._assert_valid()
        if variant not in self._egg_variants:
            raise TrustError(f"egg variant {variant!r} is not registered")

    def require_error_code(self, code: str) -> None:
        self._assert_valid()
        if code not in self._error_codes:
            raise TrustError(f"error code {code!r} is not registered")

    def genesis_for(self, stream_id: str) -> str:
        return self.genesis_registration(stream_id).frame_hash

    def genesis_registration(self, stream_id: str) -> GenesisRegistration:
        self._assert_valid()
        try:
            return self._genesis[stream_id]
        except KeyError as exc:
            raise TrustError(f"stream {stream_id!r} has no sole registered genesis") from exc

    def is_stream_retired(self, stream_id: str) -> bool:
        self._assert_valid()
        return stream_id in self._retired_streams

    def spki_for(self, rappid: str) -> bytes:
        self._assert_valid()
        try:
            return self._spki[rappid]
        except KeyError as exc:
            raise TrustError(f"no registered SPKI for {rappid}") from exc

    def owner_at(self, utc: str) -> str:
        self._assert_valid()
        owners = [tenure.rappid for tenure in self._tenures if tenure.contains(utc)]
        if len(owners) != 1:
            raise TrustError("registry does not prove exactly one estate owner at artifact utc")
        return owners[0]

    def revoked_at(self, rappid: str) -> str | None:
        self._assert_valid()
        return self._tombstones.get(rappid)

    def reanchored_at(self, rappid: str) -> str | None:
        self._assert_valid()
        return self._reanchor_cutovers.get(rappid)

    def reanchor_case(self, rappid: str) -> str | None:
        self._assert_valid()
        return self._reanchor_cases.get(rappid)


@dataclass(frozen=True)
class SignatureTrust:
    kid: str
    registry_seq: int
    owner_tenure_verified: bool


def _build_owner_tenures(
    current_owner: str, reanchors: list[dict[str, Any]], bootstrap_anchor: str
) -> tuple[tuple[_OwnerTenure, ...], set[int]]:
    by_new: dict[str, tuple[int, dict[str, Any]]] = {}
    for index, entry in enumerate(reanchors):
        new = entry["new_rappid"]
        if new in by_new:
            raise TrustError("ambiguous owner succession re-anchor chain")
        by_new[new] = (index, entry)
    chain: list[tuple[int, dict[str, Any]]] = []
    cursor = current_owner
    seen: set[str] = set()
    while cursor in by_new:
        if cursor in seen:
            raise TrustError("cyclic owner succession")
        seen.add(cursor)
        item = by_new[cursor]
        chain.append(item)
        cursor = item[1]["old_rappid"]
    if cursor != bootstrap_anchor:
        raise TrustError(
            "estate-owner succession does not descend from the out-of-band anchor"
        )
    chain.reverse()
    tenures: list[_OwnerTenure] = []
    start = "0001-01-01T00:00:00.000Z"
    owner = cursor
    for _, entry in chain:
        if entry["old_rappid"] != owner or entry["utc"] < start:
            raise TrustError("invalid owner succession order")
        tenures.append(_OwnerTenure(owner, start, entry["utc"]))
        owner = entry["new_rappid"]
        start = entry["utc"]
    tenures.append(_OwnerTenure(owner, start, None))
    if owner != current_owner:
        raise TrustError("owner succession does not terminate at current estate owner")
    return tuple(tenures), {index for index, _ in chain}


def _owner_at(tenures: tuple[_OwnerTenure, ...], utc: str) -> str:
    values = [tenure.rappid for tenure in tenures if tenure.contains(utc)]
    if len(values) != 1:
        raise TrustError("owner succession is ambiguous at utc")
    return values[0]


def _validate_registry_entries(
    entries: Any,
    anchor: str,
    provisional_resolutions: Mapping[str, TrustedProvisionalResolution],
) -> tuple[
    dict[str, str],
    frozenset[str],
    frozenset[str],
    frozenset[str],
    dict[str, bytes],
    dict[str, str],
    tuple[_OwnerTenure, ...],
    dict[str, GenesisRegistration],
    frozenset[str],
    str,
    dict[str, str],
    dict[str, str],
]:
    if not isinstance(entries, list):
        raise TrustError("registry entries must be an array")
    kind_families: dict[str, str] = {}
    active_kinds: set[str] = set()
    egg_variants: set[str] = set()
    error_codes: set[str] = set()
    spki: dict[str, bytes] = {}
    tombstones: dict[str, str] = {}
    live_genesis: dict[str, GenesisRegistration] = {}
    genesis_statuses: dict[str, list[bool]] = {}
    mapped_genesis_history: list[GenesisRegistration] = []
    owners: list[str] = []
    tombstone_entries: list[dict[str, Any]] = []
    reanchors: list[dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, dict) or not isinstance(raw.get("type"), str):
            raise TrustError("each registry entry must be an object with type")
        entry_type = raw["type"]
        if entry_type == "protocol":
            _require_exact(
                raw, {"type", "name", "spec_repo", "spec_path", "spec_hash", "deprecated"}
            )
            if (
                not all(isinstance(raw[key], str) and raw[key] for key in ("name", "spec_repo", "spec_path"))
                or not isinstance(raw["deprecated"], bool)
                or not isinstance(raw["spec_hash"], str)
                or not _HEX_RE.fullmatch(raw["spec_hash"])
            ):
                raise TrustError("invalid protocol registry entry")
        elif entry_type == "kind":
            _require_exact(raw, {"type", "kind", "family", "deprecated"})
            validate_kind(raw["kind"])
            if raw["family"] not in {"memory", "body", "swarm"} or not isinstance(
                raw["deprecated"], bool
            ):
                raise TrustError("invalid kind registry entry")
            prior_family = kind_families.get(raw["kind"])
            if prior_family is not None and prior_family != raw["family"]:
                raise TrustError("kind family binding cannot change")
            kind_families[raw["kind"]] = raw["family"]
            if not raw["deprecated"]:
                active_kinds.add(raw["kind"])
        elif entry_type == "egg-variant":
            _require_exact(raw, {"type", "variant", "deprecated"})
            if not isinstance(raw["variant"], str) or not isinstance(raw["deprecated"], bool):
                raise TrustError("invalid egg-variant entry")
            if not raw["deprecated"] and raw["variant"] in egg_variants:
                raise TrustError("duplicate live egg variant")
            if not raw["deprecated"]:
                egg_variants.add(raw["variant"])
        elif entry_type == "error-code":
            _require_exact(raw, {"type", "code"})
            if not isinstance(raw["code"], str) or not raw["code"] or raw["code"] in error_codes:
                raise TrustError("invalid or duplicate error-code entry")
            error_codes.add(raw["code"])
        elif entry_type == "genesis":
            _require_exact(
                raw,
                {"type", "stream_id", "frame_hash", "deprecated"},
                {"old_stream_id", "new_stream_id"},
            )
            classify_stream_id(raw["stream_id"])
            if (
                not isinstance(raw["frame_hash"], str)
                or not _HEX_RE.fullmatch(raw["frame_hash"])
                or not isinstance(raw["deprecated"], bool)
            ):
                raise TrustError("invalid genesis registry entry")
            for optional in ("old_stream_id", "new_stream_id"):
                if optional in raw:
                    classify_stream_id(raw[optional])
            has_old = "old_stream_id" in raw
            has_new = "new_stream_id" in raw
            if has_old != has_new:
                raise TrustError("genesis stream mapping requires both old_stream_id and new_stream_id")
            if has_new and raw["new_stream_id"] != raw["stream_id"]:
                raise TrustError("genesis new_stream_id must equal the registered stream_id")
            genesis_statuses.setdefault(raw["stream_id"], []).append(raw["deprecated"])
            registration = GenesisRegistration(
                stream_id=raw["stream_id"],
                frame_hash=raw["frame_hash"],
                old_stream_id=raw.get("old_stream_id"),
                new_stream_id=raw.get("new_stream_id"),
            )
            if has_old:
                mapped_genesis_history.append(registration)
            if not raw["deprecated"]:
                if raw["stream_id"] in live_genesis:
                    raise TrustError("stream has multiple non-deprecated genesis entries")
                live_genesis[raw["stream_id"]] = registration
        elif entry_type == "spki":
            _require_exact(raw, {"type", "rappid", "spki_der_b64", "deprecated"})
            identity = validate_rappid(raw["rappid"])
            if not isinstance(raw["deprecated"], bool):
                raise TrustError("invalid SPKI deprecated marker")
            der = _standard_b64_decode(raw["spki_der_b64"])
            if raw["rappid"] in spki and spki[raw["rappid"]] != der:
                raise TrustError("conflicting SPKI entries")
            spki[raw["rappid"]] = der
        elif entry_type == "tombstone":
            _require_exact(raw, {"type", "rappid", "revoked_utc", "sig"})
            validate_rappid(raw["rappid"])
            if not _valid_utc(raw["revoked_utc"]):
                raise TrustError("invalid tombstone utc")
            parse_detached_jws(raw["sig"])
            if raw["rappid"] in tombstones:
                raise TrustError("duplicate tombstone")
            tombstones[raw["rappid"]] = raw["revoked_utc"]
            tombstone_entries.append(raw)
        elif entry_type == "re-anchor":
            _require_exact(
                raw,
                {"type", "old_rappid", "new_rappid", "case", "utc", "sig"},
                {"old_key_sig"},
            )
            if raw["case"] not in {"upgrade", "rotation", "compromise", "tag-migrate"}:
                raise TrustError("invalid re-anchor case")
            if raw["case"] == "upgrade":
                if not isinstance(raw["old_rappid"], str) or not _PROVISIONAL_RAPPID_RE.fullmatch(
                    raw["old_rappid"]
                ):
                    raise TrustError("upgrade re-anchor old_rappid must be canonical provisional form")
            else:
                validate_rappid(raw["old_rappid"])
            validate_rappid(raw["new_rappid"])
            if not _valid_utc(raw["utc"]):
                raise TrustError("invalid re-anchor utc")
            parse_detached_jws(raw["sig"])
            if (raw["case"] == "rotation") != ("old_key_sig" in raw):
                raise TrustError("rotation alone requires old_key_sig")
            if "old_key_sig" in raw:
                parse_detached_jws(raw["old_key_sig"])
            reanchors.append(raw)
        elif entry_type == "estate_owner":
            _require_exact(raw, {"type", "rappid"})
            owners.append(validate_rappid(raw["rappid"]).value)
        elif entry_type == "master-plan":
            _require_exact(raw, {"type", "repo", "path"})
            if not isinstance(raw["repo"], str) or not raw["repo"] or not isinstance(
                raw["path"], str
            ) or not raw["path"]:
                raise TrustError("invalid master-plan entry")
        else:
            raise TrustError(f"unknown registry entry type {entry_type!r}")
    if len(owners) != 1:
        raise TrustError("registry must contain exactly one current estate_owner")
    current_owner = owners[0]
    if anchor not in spki:
        raise TrustError("registry lacks SPKI entry for out-of-band anchor")
    if current_owner not in spki:
        raise TrustError("registry lacks SPKI entry for current estate owner")
    reanchor_cutovers: dict[str, str] = {}
    reanchor_cases: dict[str, str] = {}
    tag_migrate_old: set[str] = set()
    for entry in reanchors:
        old = entry["old_rappid"]
        if old in reanchor_cutovers:
            raise TrustError("a rappid may be re-anchored only once")
        reanchor_cutovers[old] = entry["utc"]
        reanchor_cases[old] = entry["case"]
        if entry["case"] == "compromise":
            if old not in tombstones:
                raise TrustError(
                    "compromise re-anchor requires same-registry tombstone"
                )
            if tombstones[old] > entry["utc"]:
                raise TrustError(
                    "compromise tombstone must take effect no later than re-anchor"
                )
        if entry["case"] == "tag-migrate":
            tag_migrate_old.add(old)
            if old not in spki or hashlib.sha256(spki[old]).hexdigest() != validate_rappid(old).tail:
                raise TrustError("tag-migrate old SPKI does not prove the untagged tail")
        if entry["case"] == "upgrade":
            resolution = provisional_resolutions.get(old)
            owner_match = _PROVISIONAL_RAPPID_RE.fullmatch(old)
            if (
                resolution is None
                or owner_match is None
                or resolution.owner != owner_match.group("owner")
            ):
                raise TrustError(
                    "upgrade re-anchor requires explicit trusted provisional-owner resolution"
                )
    for identity, der in spki.items():
        tail = validate_rappid(identity).tail
        if identity in tag_migrate_old:
            if hashlib.sha256(der).hexdigest() != tail:
                raise TrustError("tag-migrate SPKI proof is invalid")
        elif Hb("rapp/1:rappid", der) != tail:
            raise TrustError("registry SPKI does not bind to rappid")
    identity_reanchors = {
        (entry["old_rappid"], entry["new_rappid"]) for entry in reanchors
    }
    retired_streams: set[str] = set()
    for registration in mapped_genesis_history:
        old_stream = registration.old_stream_id
        new_stream = registration.new_stream_id
        old_family = classify_stream_id(old_stream)
        new_family = classify_stream_id(new_stream)
        if old_family != new_family or old_family == "swarm":
            raise TrustError("genesis identity mapping must preserve a non-swarm stream family")
        if old_family == "body":
            old_identity, old_instance = old_stream, None
            new_identity, new_instance = new_stream, None
        else:
            old_identity, old_instance = old_stream.rsplit(":", 1)
            new_identity, new_instance = new_stream.rsplit(":", 1)
        if old_instance != new_instance:
            raise TrustError("genesis identity mapping must preserve memory instance")
        if (old_identity, new_identity) not in identity_reanchors:
            raise TrustError(
                "genesis stream mapping requires a verified identity re-anchor"
            )
        old_statuses = genesis_statuses.get(old_stream, [])
        if not old_statuses or not all(old_statuses):
            raise TrustError(
                "mapped old stream must retain only deprecated genesis entries"
            )
        if old_stream in retired_streams:
            raise TrustError("old stream is mapped more than once")
        retired_streams.add(old_stream)
    tenures, succession_indexes = _build_owner_tenures(
        current_owner, reanchors, anchor
    )
    if any(
        reanchors[index]["case"] == "compromise" for index in succession_indexes
    ):
        raise TrustError(
            "estate-owner root compromise requires a newly supplied out-of-band anchor"
        )
    for index, entry in enumerate(reanchors):
        expected_owner = (
            entry["old_rappid"]
            if index in succession_indexes
            else _owner_at(tenures, entry["utc"])
        )
        _verify_with_spki(
            entry["sig"],
            canonical_bytes({k: v for k, v in entry.items() if k != "sig"}),
            spki.get(expected_owner, b""),
            expected_owner,
        )
        if entry["case"] == "rotation":
            _verify_with_spki(
                entry["old_key_sig"],
                canonical_bytes(
                    {k: v for k, v in entry.items() if k not in {"sig", "old_key_sig"}}
                ),
                spki.get(entry["old_rappid"], b""),
                entry["old_rappid"],
            )
    for entry in tombstone_entries:
        owner = _owner_at(tenures, entry["revoked_utc"])
        _verify_with_spki(
            entry["sig"],
            canonical_bytes({k: v for k, v in entry.items() if k != "sig"}),
            spki.get(owner, b""),
            owner,
        )
    return (
        kind_families,
        frozenset(active_kinds),
        frozenset(egg_variants),
        frozenset(error_codes),
        spki,
        tombstones,
        tenures,
        live_genesis,
        frozenset(retired_streams),
        current_owner,
        reanchor_cutovers,
        reanchor_cases,
    )


def _new_proof(
    *,
    anchor: str,
    source: str,
    sequence: int,
    registry_hash: str,
    verified_at: datetime,
    fetched_at: datetime,
    kind_families: dict[str, str],
    active_kinds: frozenset[str],
    egg_variants: frozenset[str],
    error_codes: frozenset[str],
    spki: dict[str, bytes],
    tombstones: dict[str, str],
    tenures: tuple[_OwnerTenure, ...],
    genesis: dict[str, GenesisRegistration],
    retired_streams: frozenset[str],
    reanchor_cutovers: dict[str, str],
    reanchor_cases: dict[str, str],
    raw: Mapping[str, Any],
) -> VerifiedRegistry:
    proof = object.__new__(VerifiedRegistry)
    object.__setattr__(proof, "_anchor", anchor)
    object.__setattr__(proof, "_source", source)
    object.__setattr__(proof, "_sequence", sequence)
    object.__setattr__(proof, "_registry_hash", registry_hash)
    object.__setattr__(proof, "_verified_at", verified_at)
    object.__setattr__(proof, "_fetched_at", fetched_at)
    object.__setattr__(
        proof, "_kind_families", MappingProxyType(dict(kind_families))
    )
    object.__setattr__(proof, "_active_kinds", active_kinds)
    object.__setattr__(proof, "_egg_variants", egg_variants)
    object.__setattr__(proof, "_error_codes", error_codes)
    object.__setattr__(proof, "_spki", MappingProxyType(dict(spki)))
    object.__setattr__(proof, "_tombstones", MappingProxyType(dict(tombstones)))
    object.__setattr__(proof, "_tenures", tenures)
    object.__setattr__(proof, "_genesis", MappingProxyType(dict(genesis)))
    object.__setattr__(proof, "_retired_streams", retired_streams)
    object.__setattr__(
        proof, "_reanchor_cutovers", MappingProxyType(dict(reanchor_cutovers))
    )
    object.__setattr__(proof, "_reanchor_cases", MappingProxyType(dict(reanchor_cases)))
    object.__setattr__(proof, "_raw", MappingProxyType(dict(raw)))
    object.__setattr__(proof, "_seal", _PROOF_SEAL)
    object.__setattr__(proof, "_locked", True)
    return proof


def verify_registry(
    raw_registry: bytes,
    *,
    out_of_band_anchor: str,
    anchor_spki_der: bytes,
    state: RegistrySequenceStore,
    source: str,
    fetched_at: datetime,
    now: datetime,
    max_age_seconds: int,
    trusted_provisional_resolutions: tuple[TrustedProvisionalResolution, ...] = (),
) -> VerifiedRegistry:
    """Verify exact registry shape, anchor signature, freshness, and monotonic state."""

    if type(state) not in {MemoryRegistrySequenceStore, SQLiteRegistrySequenceStore}:
        raise TrustError("state must be an SDK monotonic registry state store")
    anchor = validate_rappid(out_of_band_anchor).value
    canonical_anchor_spki = canonical_spki_der(anchor_spki_der)
    if Hb("rapp/1:rappid", canonical_anchor_spki) != validate_rappid(anchor).tail:
        raise TrustError("out-of-band anchor does not bind to supplied SPKI")
    parsed_source = urllib.parse.urlsplit(source)
    if (
        parsed_source.scheme != "https"
        or not parsed_source.netloc
        or parsed_source.username is not None
        or parsed_source.password is not None
        or parsed_source.fragment
    ):
        raise TrustError("registry source must be an explicit credential-free HTTPS URL")
    if (
        not isinstance(fetched_at, datetime)
        or not isinstance(now, datetime)
        or fetched_at.tzinfo is None
        or now.tzinfo is None
    ):
        raise TrustError("fetched_at and now must be timezone-aware datetimes")
    fetched = fetched_at.astimezone(timezone.utc)
    checked = now.astimezone(timezone.utc)
    if not isinstance(max_age_seconds, int) or isinstance(max_age_seconds, bool) or max_age_seconds < 0:
        raise TrustError("max_age_seconds must be a non-negative integer")
    age = (checked - fetched).total_seconds()
    if age < 0 or age > max_age_seconds:
        raise TrustError("registry evidence is future-dated or stale")
    registry = strict_loads(raw_registry)
    if not isinstance(registry, dict) or set(registry) != _REGISTRY_KEYS:
        raise TrustError("registry must have exactly schema, registry_seq, entries, sig")
    if registry["schema"] != "rapp/1-registry" or not _uint53(registry["registry_seq"]):
        raise TrustError("registry schema or registry_seq is invalid")
    if not isinstance(registry["entries"], list):
        raise TrustError("registry entries must be an array")
    _check_append_only([], registry["entries"])
    parsed_root_sig = parse_detached_jws(registry["sig"])
    resolutions: dict[str, TrustedProvisionalResolution] = {}
    for resolution in trusted_provisional_resolutions:
        if not isinstance(resolution, TrustedProvisionalResolution):
            raise TrustError(
                "trusted_provisional_resolutions must contain explicit resolution records"
            )
        if resolution.provisional_rappid in resolutions:
            raise TrustError("duplicate provisional-owner resolution")
        resolutions[resolution.provisional_rappid] = resolution
    (
        kind_families,
        active_kinds,
        egg_variants,
        error_codes,
        spki,
        tombstones,
        tenures,
        genesis,
        retired_streams,
        current_owner,
        reanchor_cutovers,
        reanchor_cases,
    ) = _validate_registry_entries(registry["entries"], anchor, resolutions)
    if spki[anchor] != canonical_anchor_spki:
        raise TrustError("registry anchor SPKI differs from out-of-band SPKI")
    _verify_with_spki(
        parsed_root_sig,
        canonical_bytes({key: value for key, value in registry.items() if key != "sig"}),
        spki[current_owner],
        current_owner,
    )
    registry_hash = hashlib.sha256(canonical_bytes(registry)).hexdigest()
    state_key = hashlib.sha256(
        f"rapp/1-registry-state\n{anchor}".encode("utf-8")
    ).hexdigest()
    state.check_and_store(
        state_key, registry["registry_seq"], registry_hash, registry["entries"]
    )
    return _new_proof(
        anchor=anchor,
        source=source,
        sequence=registry["registry_seq"],
        registry_hash=registry_hash,
        verified_at=checked,
        fetched_at=fetched,
        kind_families=kind_families,
        active_kinds=active_kinds,
        egg_variants=egg_variants,
        error_codes=error_codes,
        spki=spki,
        tombstones=tombstones,
        tenures=tenures,
        genesis=genesis,
        retired_streams=retired_streams,
        reanchor_cutovers=reanchor_cutovers,
        reanchor_cases=reanchor_cases,
        raw=registry,
    )


def verify_detached_jws(
    jws: DetachedJWS | str,
    payload: bytes,
    registry: VerifiedRegistry,
    *,
    artifact_utc: str,
    require_estate_owner: bool = False,
) -> SignatureTrust:
    """Verify a detached signature against one opaque verified registry proof."""

    if not isinstance(registry, VerifiedRegistry):
        raise TrustError("a VerifiedRegistry proof is required")
    if not _valid_utc(artifact_utc):
        raise TrustError("artifact utc is invalid")
    parsed = parse_detached_jws(jws) if isinstance(jws, str) else jws
    kid = parsed.header["kid"]
    spki = registry.spki_for(kid)
    revoked_utc = registry.revoked_at(kid)
    if revoked_utc is not None and artifact_utc >= revoked_utc:
        raise TrustError("signing key was tombstoned at artifact utc")
    reanchor_utc = registry.reanchored_at(kid)
    if reanchor_utc is not None and artifact_utc >= reanchor_utc:
        raise TrustError("signing key was superseded by re-anchor at artifact utc")
    owner_verified = False
    if require_estate_owner:
        if registry.owner_at(artifact_utc) != kid:
            raise TrustError("signature kid was not estate owner at artifact utc")
        owner_verified = True
    _verify_with_spki(
        parsed,
        payload,
        spki,
        kid,
        allow_untagged_binding=registry.reanchor_case(kid) == "tag-migrate",
    )
    return SignatureTrust(
        kid=kid,
        registry_seq=registry.registry_seq,
        owner_tenure_verified=owner_verified,
    )
