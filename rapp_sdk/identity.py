"""RAPP/1 identity, kind, and stream grammars."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import UnsupportedAlgorithm

from .errors import ValidationError
from .json_profile import Hb

_LABEL_39 = r"[a-z0-9]+(?:-[a-z0-9]+)*"
_RAPPID_RE = re.compile(
    rf"^rappid:@(?P<owner>{_LABEL_39})/(?P<slug>{_LABEL_39}):(?P<tail>[0-9a-f]{{64}})$"
)
_KIND_RE = re.compile(
    r"^(?P<left>[a-z0-9]+(?:-[a-z0-9]+)*)\."
    r"(?P<right>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
_INSTANCE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Rappid:
    value: str
    owner: str
    slug: str
    tail: str


def validate_rappid(value: str) -> Rappid:
    if not isinstance(value, str):
        raise ValidationError("rappid must be a string")
    match = _RAPPID_RE.fullmatch(value)
    if not match:
        raise ValidationError("rappid does not match the exact RAPP/1 grammar")
    owner = match.group("owner")
    slug = match.group("slug")
    if len(owner) > 39 or len(slug) > 100:
        raise ValidationError("rappid owner or slug exceeds its length limit")
    return Rappid(value, owner, slug, match.group("tail"))


def _validate_label(value: str, maximum: int, what: str) -> None:
    if not _INSTANCE_RE.fullmatch(value) or len(value) > maximum:
        raise ValidationError(f"{what} does not match lclabel grammar")


def validate_kind(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("kind must be a string")
    match = _KIND_RE.fullmatch(value)
    if not match:
        raise ValidationError("kind must contain exactly two lowercase labels")
    if len(match.group("left")) > 64 or len(match.group("right")) > 64:
        raise ValidationError("kind labels may not exceed 64 characters")
    return value


def classify_stream_id(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("stream_id must be a string")
    if value.startswith("net:"):
        label = value[4:]
        _validate_label(label, 64, "swarm stream label")
        return "swarm"
    try:
        validate_rappid(value)
        return "body"
    except ValidationError:
        pass
    split = value.rsplit(":", 1)
    if len(split) == 2:
        validate_rappid(split[0])
        _validate_label(split[1], 64, "memory stream instance")
        return "memory"
    raise ValidationError("stream_id does not match a RAPP/1 stream grammar")


def _format_rappid(owner: str, slug: str, tail: str) -> str:
    _validate_label(owner, 39, "owner")
    _validate_label(slug, 100, "slug")
    return f"rappid:@{owner}/{slug}:{tail}"


def mint_keyless_rappid(owner: str, slug: str, source: uuid.UUID | None = None) -> str:
    """Mint once from RFC 9562 UUIDv4 octets."""

    identity = source or uuid.uuid4()
    if not isinstance(identity, uuid.UUID) or identity.version != 4:
        raise ValidationError("keyless minting requires a UUIDv4")
    if identity.variant != uuid.RFC_4122:
        raise ValidationError("UUID does not use the RFC variant")
    return _format_rappid(owner, slug, Hb("rapp/1:rappid", identity.bytes))


def mint_keyed_rappid(owner: str, slug: str, spki_der: bytes) -> str:
    """Mint once from an X.509 SubjectPublicKeyInfo DER byte string."""

    canonical = canonical_spki_der(spki_der)
    return _format_rappid(owner, slug, Hb("rapp/1:rappid", canonical))


def canonical_spki_der(spki_der: bytes) -> bytes:
    """Parse SPKI and require its input to be the canonical DER re-serialization."""

    if not isinstance(spki_der, bytes) or not spki_der:
        raise ValidationError("SPKI DER must be non-empty bytes")
    try:
        key = serialization.load_der_public_key(spki_der)
        canonical = key.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise ValidationError("SPKI DER is not a parseable public SubjectPublicKeyInfo") from exc
    if canonical != spki_der:
        raise ValidationError("SPKI must use canonical DER SubjectPublicKeyInfo encoding")
    return canonical
