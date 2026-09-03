"""Minimal RAPP/1 frame primitives for the local Brainstem operator.

Pinned to kody-w/rapp-1 rev-5:
    d2cd5abed48d3f52b86bbb975ac3558286d1db41
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Any

SPEC = "rapp/1"
SOURCE_COMMIT = "d2cd5abed48d3f52b86bbb975ac3558286d1db41"
MAX_CANONICAL_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_SAFE_INTEGER = 2**53 - 1

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:(?:[0-5]\d)\.\d{3}Z$"
)
_LCLABEL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_KIND = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$"
)
_RAPPID = re.compile(
    r"^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)/"
    r"([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$"
)

FRAME_KEYS = {
    "spec",
    "kind",
    "stream_id",
    "seq",
    "utc",
    "payload",
    "payload_hash",
    "frame_hash",
    "prev",
    "prev_wave",
    "sig",
}


def _validate_value(value: Any, depth: int = 1) -> None:
    if depth > MAX_DEPTH:
        raise ValueError(f"RAPP/1 JSON nesting exceeds {MAX_DEPTH}")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ValueError("RAPP/1 integers must round-trip through binary64")
        return
    if isinstance(value, float):
        raise ValueError("RAPP operator frames do not emit floating-point values")
    if isinstance(value, str):
        value.encode("utf-8", "strict")
        return
    if isinstance(value, list):
        for item in value:
            _validate_value(item, depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("RAPP/1 object keys must be strings")
            try:
                key.encode("ascii", "strict")
            except UnicodeEncodeError as exc:
                raise ValueError(
                    "RAPP operator frame keys must be ASCII"
                ) from exc
            _validate_value(item, depth + 1)
        return
    raise ValueError(f"RAPP/1 value is not I-JSON: {type(value).__name__}")


def _canonical(value: Any) -> str:
    if value is None or isinstance(value, (bool, int, str)):
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    if isinstance(value, list):
        return "[" + ",".join(_canonical(item) for item in value) + "]"
    return "{" + ",".join(
        json.dumps(key, ensure_ascii=False)
        + ":"
        + _canonical(value[key])
        for key in sorted(value)
    ) + "}"


def canonical_bytes(value: Any) -> bytes:
    """Return RFC 8785 bytes for the operator's integer-only JSON profile."""
    _validate_value(value)
    encoded = _canonical(value).encode("utf-8")
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise ValueError("RAPP/1 canonical form exceeds 1 MiB")
    return encoded


def canonical(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def H(space: str, value: Any) -> str:
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + canonical_bytes(value)
    ).hexdigest()


def Hb(space: str, octets: bytes) -> str:
    if not isinstance(octets, bytes):
        raise TypeError("Hb requires bytes")
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + octets
    ).hexdigest()


def _validate_owner_slug(owner: str, slug: str) -> None:
    if not (
        isinstance(owner, str)
        and 1 <= len(owner) <= 39
        and _LCLABEL.fullmatch(owner)
    ):
        raise ValueError("RAPP/1 owner must be a lowercase GitHub-login label")
    if not (
        isinstance(slug, str)
        and 1 <= len(slug) <= 100
        and _LCLABEL.fullmatch(slug)
    ):
        raise ValueError("RAPP/1 slug must be a lowercase label")


def mint_rappid(
    owner: str,
    slug: str,
    *,
    uuid_anchor: uuid.UUID | str | None = None,
    spki_der: bytes | None = None,
) -> tuple[str, uuid.UUID | None]:
    """Mint one canonical identity and return its UUID anchor when keyless."""
    _validate_owner_slug(owner, slug)
    if spki_der is not None and uuid_anchor is not None:
        raise ValueError("Choose keyed or keyless RAPPID minting, not both")
    if spki_der is not None:
        return f"rappid:@{owner}/{slug}:{Hb('rapp/1:rappid', spki_der)}", None
    anchor = (
        uuid_anchor
        if isinstance(uuid_anchor, uuid.UUID)
        else uuid.UUID(str(uuid_anchor))
        if uuid_anchor is not None
        else uuid.uuid4()
    )
    return (
        f"rappid:@{owner}/{slug}:{Hb('rapp/1:rappid', anchor.bytes)}",
        anchor,
    )


def rappid_valid(value: str) -> bool:
    match = _RAPPID.fullmatch(value or "")
    if not match:
        return False
    owner, slug, _tail = match.groups()
    return len(owner) <= 39 and len(slug) <= 100


def build_frame(
    kind: str,
    stream_id: str,
    seq: int,
    utc: str,
    payload: dict[str, Any],
    prev: str | None,
    *,
    prev_wave: str | None = None,
    sig: str | None = None,
) -> dict[str, Any]:
    frame = {
        "spec": SPEC,
        "kind": kind,
        "stream_id": stream_id,
        "seq": seq,
        "utc": utc,
        "payload": payload,
        "payload_hash": H("rapp/1:particle", payload),
        "prev": prev,
        "prev_wave": prev_wave,
        "sig": sig,
    }
    preimage = {
        key: frame[key]
        for key in frame
        if key not in {"frame_hash", "sig"}
    }
    frame["frame_hash"] = H("rapp/1:wave", preimage)
    return frame


def verify_frame(
    frame: dict[str, Any],
    *,
    head: dict[str, Any] | None = None,
    stream_id_of_record: str | None = None,
) -> tuple[bool, str | None, str]:
    if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
        return False, "1", "frame must contain exactly the 11 RAPP/1 keys"
    if frame["spec"] != SPEC:
        return False, "1", "spec != rapp/1"
    if not isinstance(frame["kind"], str) or not _KIND.fullmatch(frame["kind"]):
        return False, "1", "invalid kind"
    if not isinstance(frame["stream_id"], str):
        return False, "1", "invalid stream_id type"
    if not (
        isinstance(frame["seq"], int)
        and not isinstance(frame["seq"], bool)
        and 0 <= frame["seq"] <= MAX_SAFE_INTEGER
    ):
        return False, "1", "seq is not uint53"
    if not isinstance(frame["utc"], str) or not _UTC.fullmatch(frame["utc"]):
        return False, "1", "utc is not fixed millisecond UTC"
    if not isinstance(frame["payload"], dict):
        return False, "1", "payload is not an object"
    for field in ("payload_hash", "frame_hash"):
        if not isinstance(frame[field], str) or not _HEX64.fullmatch(frame[field]):
            return False, "1", f"{field} is not lowercase 64-hex"
    for field in ("prev", "prev_wave"):
        value = frame[field]
        if value is not None and (
            not isinstance(value, str) or not _HEX64.fullmatch(value)
        ):
            return False, "1", f"{field} is not null or lowercase 64-hex"
    if (
        stream_id_of_record is not None
        and frame["stream_id"] != stream_id_of_record
    ):
        return False, "1a", "stream_id mismatch"
    try:
        if frame["payload_hash"] != H("rapp/1:particle", frame["payload"]):
            return False, "2", "payload_hash mismatch"
        preimage = {
            key: frame[key]
            for key in frame
            if key not in {"frame_hash", "sig"}
        }
        if frame["frame_hash"] != H("rapp/1:wave", preimage):
            return False, "3", "frame_hash mismatch"
    except (TypeError, ValueError) as exc:
        return False, "1", str(exc)
    if head is None:
        if frame["seq"] != 0 or frame["prev"] is not None:
            return False, "4", "genesis must be seq=0 and prev=null"
    else:
        if frame["seq"] != head["seq"] + 1:
            return False, "4", "seq is not contiguous"
        if frame["prev"] != head["payload_hash"]:
            return False, "4", "prev does not match head particle"
        if frame["utc"] < head["utc"]:
            return False, "4", "utc moved backwards"
    is_swarm = frame["stream_id"].startswith("net:")
    if is_swarm and frame["seq"] > 0:
        if head is not None and frame["prev_wave"] != head["frame_hash"]:
            return False, "5", "prev_wave does not match swarm head"
    elif frame["prev_wave"] is not None:
        return False, "5", "prev_wave must be null off swarm"
    if is_swarm and frame["sig"] is None:
        return False, "6", "swarm frame must be signed"
    return True, None, "ok"
