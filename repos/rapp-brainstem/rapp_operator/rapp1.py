"""Minimal RAPP/1 frame primitives for the local Brainstem operator.

Conforms to kody-w/rapp-1 rev-17 (the five-implementation erratum):
    f6bafe76735ba73510518810c8bc8cd133dcf527
"""

from __future__ import annotations

import base64
import decimal
import hashlib
import json
import re
import unicodedata
import uuid
from typing import Any

SPEC = "rapp/1"
SOURCE_COMMIT = "f6bafe76735ba73510518810c8bc8cd133dcf527"
MAX_CANONICAL_BYTES = 1024 * 1024
MAX_JSON_INPUT_BYTES = 64 * 1024 * 1024
MAX_DEPTH = 64
MAX_SAFE_INTEGER = 2**53 - 1

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UTC = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})"
    r"T([0-9]{2}):([0-9]{2}):([0-9]{2})\.[0-9]{3}Z",
    re.ASCII,
)
_LCLABEL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_KIND = re.compile(
    r"^([a-z0-9]+(?:-[a-z0-9]+)*)\.([a-z0-9]+(?:-[a-z0-9]+)*)$"
)
_RAPPID = re.compile(
    r"^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)/"
    r"([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$"
)
_B64URL = re.compile(r"^[A-Za-z0-9_-]*$")

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

# §4 (b), RFC 7493 §2.1: surrogates and the 66 noncharacters are not I-JSON.
_NOT_IJSON_CHAR = re.compile(
    "[\ud800-\udfff\ufdd0-\ufdef"
    + "".join(
        chr(plane << 16 | 0xFFFE) + chr(plane << 16 | 0xFFFF)
        for plane in range(17)
    )
    + "]"
)


def _ijson_string(value: str) -> str:
    bad = _NOT_IJSON_CHAR.search(value)
    if bad:
        raise ValueError(
            f"U+{ord(bad.group()):04X} is a surrogate or noncharacter, "
            "outside I-JSON (§4 (b))"
        )
    return json.dumps(value, ensure_ascii=False)


def _number_to_string(x: float) -> str:
    """ECMA-262 Number::toString of a finite binary64 (RFC 8785 §3.2.2.3)."""
    if x != x or x in (float("inf"), float("-inf")):
        raise ValueError("NaN and infinities are outside the §4 domain")
    if x == 0:
        return "0"
    mantissa, _, exponent = repr(abs(x)).partition("e")
    whole, _, fraction = mantissa.partition(".")
    digits = (whole + fraction).lstrip("0")
    n = len(whole) + int(exponent or 0) - (
        len(whole) + len(fraction) - len(digits)
    )
    digits = digits.rstrip("0")
    k = len(digits)
    if k <= n <= 21:
        text = digits + "0" * (n - k)
    elif 0 < n <= 21:
        text = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        text = "0." + "0" * -n + digits
    else:
        text = (
            digits[0]
            + ("." + digits[1:] if k > 1 else "")
            + "e"
            + ("+" if n > 0 else "-")
            + str(abs(n - 1))
        )
    return ("-" if x < 0 else "") + text


def _canonical(value: Any) -> str:
    if value is None or isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, int):
        if abs(value) <= MAX_SAFE_INTEGER:
            return json.dumps(value)
        try:
            as_binary64 = float(value)
        except OverflowError:
            as_binary64 = None
        if as_binary64 != value:
            raise ValueError(
                "RAPP/1 integers must be exactly binary64 (§4 (c))"
            )
        return _number_to_string(as_binary64)
    if isinstance(value, float):
        return _number_to_string(value)
    if isinstance(value, str):
        return _ijson_string(value)
    if isinstance(value, list):
        return "[" + ",".join(_canonical(item) for item in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("RAPP/1 object keys must be strings")
        # RFC 8785 orders member names by UTF-16 code units.
        keys = sorted(
            value,
            key=lambda key: key.encode("utf-16-be", "surrogatepass"),
        )
        return "{" + ",".join(
            _ijson_string(key) + ":" + _canonical(value[key])
            for key in keys
        ) + "}"
    raise ValueError(f"RAPP/1 value is not I-JSON: {type(value).__name__}")


def _container_depth(value: Any, limit: int = MAX_DEPTH) -> int:
    """§4 (d): the root is depth 1 and only objects and arrays add a level."""
    deepest, stack = 0, [(value, 1)]
    while stack and deepest <= limit:
        current, depth = stack.pop()
        if isinstance(current, dict):
            current = list(current.values())
        if isinstance(current, list):
            deepest = max(deepest, depth)
            stack.extend((item, depth + 1) for item in current)
    return deepest


def canonical_bytes(value: Any) -> bytes:
    """Return the RFC 8785 (JCS) bytes of a §4 I-JSON value."""
    if _container_depth(value) > MAX_DEPTH:
        raise ValueError(f"RAPP/1 JSON nesting exceeds {MAX_DEPTH}")
    encoded = _canonical(value).encode("utf-8")
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise ValueError("RAPP/1 canonical form exceeds 1 MiB")
    return encoded


def canonical(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def _json_number(token: str) -> float:
    """§4 (c): a number token is its nearest binary64 and must round-trip."""
    d = float(token)
    if d != d or d in (float("inf"), float("-inf")):
        raise ValueError(f"number {token[:40]} is not a finite binary64")
    try:
        same = decimal.Decimal(token) == decimal.Decimal(_number_to_string(d))
    except ArithmeticError:
        mantissa = token.lower().partition("e")[0]
        same = not any(char in "123456789" for char in mantissa)
    if not same:
        raise ValueError(
            f"number {token[:40]} does not survive the binary64 round trip"
        )
    return d


def _json_int(token: str) -> Any:
    if token == "-0":
        return -0.0  # rev-17 E-9: -0 is never the integer 0
    d = _json_number(token)
    value = int(token)
    return value if value == d else int(d)


def _json_constant(token: str) -> Any:
    raise ValueError(f"{token} is not a JSON number (§4 (c))")


def parse_json(blob: bytes | str) -> Any:
    """Parse one §4 I-JSON text; refuse (never repair) anything outside it."""
    if isinstance(blob, (bytes, bytearray)):
        if len(blob) > MAX_JSON_INPUT_BYTES:
            raise ValueError("JSON text exceeds the 64 MiB input guard")
        if blob.startswith(b"\xef\xbb\xbf"):
            raise ValueError("JSON text starts with a byte-order mark (§4)")
        try:
            text = bytes(blob).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"JSON text is not UTF-8 (§4): {exc}") from None
    elif isinstance(blob, str):
        if len(blob) > MAX_JSON_INPUT_BYTES:
            raise ValueError("JSON text exceeds the 64 MiB input guard")
        text = blob
    else:
        raise ValueError("JSON text must be octets or a str")
    if text.startswith("\ufeff"):
        raise ValueError("JSON text starts with a byte-order mark (§4)")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in items:
            if key in result:
                raise ValueError(f"duplicate JSON member: {key!r}")
            result[key] = item
        return result

    try:
        value = json.loads(
            text,
            object_pairs_hook=pairs,
            parse_float=_json_number,
            parse_int=_json_int,
            parse_constant=_json_constant,
        )
    except RecursionError:
        raise ValueError(f"RAPP/1 JSON nesting exceeds {MAX_DEPTH}") from None
    canonical_bytes(value)  # §4 (b) characters, (d) depth and 1 MiB
    return value


# §5 (rev-17 E-7): each tag belongs to exactly one function.
H_SPACES = frozenset({
    "rapp/1:particle",
    "rapp/1:wave",
    "rapp/1:egg-manifest",
    "rapp/1:sealed-aad",
    "rapp/1:sealed-key-request",
})
HB_SPACES = frozenset({
    "rapp/1:egg",
    "rapp/1:rappid",
    "rapp/1:grail",
    "rapp/1:seal",
})


def H(space: str, value: Any) -> str:
    if not (isinstance(space, str) and space in H_SPACES):
        raise ValueError(f"§5: H is not used with the tag {space!r}")
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + canonical_bytes(value)
    ).hexdigest()


def Hb(space: str, octets: bytes) -> str:
    if not (isinstance(space, str) and space in HB_SPACES):
        raise ValueError(f"§5: Hb is not used with the tag {space!r}")
    if not isinstance(octets, bytes):
        raise TypeError("Hb requires bytes")
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + octets
    ).hexdigest()


def tagged_digest(space: str, value: Any) -> str:
    """The operator's own tagged record digest; never a §5 address space."""
    if (
        not isinstance(space, str)
        or space in H_SPACES
        or space in HB_SPACES
        or "\n" in space
    ):
        raise ValueError(f"operator digest tag {space!r} is not allowed")
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + canonical_bytes(value)
    ).hexdigest()


# §6.2 (rev-17 E-8): the only SPKI octets a keyed mint accepts.
_ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")
_P256_SPKI_PREFIX = bytes.fromhex(
    "3059301306072a8648ce3d020106082a8648ce3d030107034200"
)
_ED25519_P = 2**255 - 19
_ED25519_D = -121665 * pow(121666, _ED25519_P - 2, _ED25519_P) % _ED25519_P
_P256_P = 2**256 - 2**224 + 2**192 + 2**96 - 1
_P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B


def _ed25519_point_decodes(key: bytes) -> bool:
    p = _ED25519_P
    y = int.from_bytes(key, "little") & (2**255 - 1)
    sign = key[31] >> 7
    if y >= p:
        return False
    u = (y * y - 1) % p
    v = (_ED25519_D * y * y + 1) % p
    x = u * pow(v, 3, p) * pow(u * pow(v, 7, p), (p - 5) // 8, p) % p
    if (v * x * x - u) % p != 0:
        if (v * x * x + u) % p != 0:
            return False
        x = x * pow(2, (p - 1) // 4, p) % p
    return not (x == 0 and sign == 1)


def _p256_point_on_curve(point: bytes) -> bool:
    p = _P256_P
    x = int.from_bytes(point[1:33], "big")
    y = int.from_bytes(point[33:65], "big")
    return x < p and y < p and (y * y - (x * x * x - 3 * x + _P256_B)) % p == 0


def spki_valid(spki_der: Any) -> bool:
    """True iff the octets are the exact DER SPKI of a §10 key (§6.2)."""
    if not isinstance(spki_der, (bytes, bytearray)):
        return False
    spki_der = bytes(spki_der)
    if len(spki_der) == 44 and spki_der.startswith(_ED25519_SPKI_PREFIX):
        return _ed25519_point_decodes(spki_der[12:])
    if (
        len(spki_der) == 91
        and spki_der.startswith(_P256_SPKI_PREFIX)
        and spki_der[26] == 0x04
    ):
        return _p256_point_on_curve(spki_der[26:])
    return False


def _validate_owner_slug(owner: Any, slug: Any) -> None:
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
        if not spki_valid(spki_der):
            raise ValueError(
                "§6.2: a keyed mint needs the exact DER SPKI of an Ed25519 "
                "key or of a P-256 key with an uncompressed on-curve point"
            )
        tail = Hb("rapp/1:rappid", bytes(spki_der))
        return f"rappid:@{owner}/{slug}:{tail}", None
    anchor = (
        uuid_anchor
        if isinstance(uuid_anchor, uuid.UUID)
        else uuid.UUID(str(uuid_anchor))
        if uuid_anchor is not None
        else uuid.uuid4()
    )
    octets = anchor.bytes
    if octets[6] >> 4 != 4 or octets[8] >> 6 != 0b10:
        raise ValueError("§6.2: keyless mint octets are not a UUIDv4")
    return (
        f"rappid:@{owner}/{slug}:{Hb('rapp/1:rappid', octets)}",
        anchor,
    )


def rappid_valid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    match = _RAPPID.fullmatch(value)
    if not match:
        return False
    owner, slug, _tail = match.groups()
    return len(owner) <= 39 and len(slug) <= 100


def kind_valid(kind: Any) -> bool:
    """§6.1.1 kind: two lclabels of 1-64 characters."""
    match = _KIND.fullmatch(kind) if isinstance(kind, str) else None
    return bool(
        match
        and len(match.group(1)) <= 64
        and len(match.group(2)) <= 64
    )


def stream_form(stream_id: Any) -> str | None:
    """§6.1.1: memory-stream, body-stream, swarm-stream, or None."""
    if not isinstance(stream_id, str):
        return None
    if stream_id.startswith("net:"):
        return "swarm-stream" if _LCLABEL.fullmatch(stream_id[4:]) else None
    if rappid_valid(stream_id):
        return "body-stream"
    head, sep, instance = stream_id.rpartition(":")
    if (
        sep
        and rappid_valid(head)
        and _LCLABEL.fullmatch(instance)
        and len(instance) <= 64
    ):
        return "memory-stream"
    return None


def utc_valid(value: Any) -> bool:
    """§7.4 (rev-17 E-1): YYYY-MM-DDTHH:MM:SS.mmmZ, ASCII, calendar-valid."""
    if not isinstance(value, str) or len(value) != 24 or not value.isascii():
        return False
    match = _UTC.fullmatch(value)
    if not match:
        return False
    year, month, day, hour, minute, second = (
        int(group) for group in match.groups()
    )
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    days = (31, 29 if leap else 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31)
    return (
        1 <= month <= 12
        and 1 <= day <= days[month - 1]
        and hour <= 23
        and minute <= 59
        and second <= 59
    )


def _names_ok(value: Any) -> None:
    """§4 (rev-17 E-5, E-6): payload member names are NFC and assigned."""
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for name, item in current.items():
                if not isinstance(name, str):
                    raise ValueError("payload member names must be strings")
                if not unicodedata.is_normalized("NFC", name):
                    raise ValueError(f"payload member name is not NFC: {name!r}")
                if any(unicodedata.category(char) == "Cn" for char in name):
                    raise ValueError(
                        f"payload member name is unassigned Unicode: {name!r}"
                    )
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)


def _b64url_decode(value: Any) -> bytes:
    if (
        not isinstance(value, str)
        or "=" in value
        or not _B64URL.fullmatch(value)
        or len(value) % 4 == 1
    ):
        raise ValueError("base64url value must be unpadded")
    decoded = base64.b64decode(
        value + "=" * (-len(value) % 4),
        altchars=b"-_",
        validate=True,
    )
    if base64.urlsafe_b64encode(decoded).rstrip(b"=").decode() != value:
        raise ValueError("base64url value is not canonical")
    return decoded


def parse_detached_jws(sig: Any) -> tuple[dict[str, Any], str, bytes]:
    """§10: a detached compact JWS with the RAPP protected-header profile."""
    parts = sig.split(".") if isinstance(sig, str) else []
    if len(parts) != 3 or parts[1] != "":
        raise ValueError("JWS must use detached compact serialization")
    header_octets = _b64url_decode(parts[0])
    header = parse_json(header_octets)
    if not isinstance(header, dict) or set(header) != {
        "alg", "b64", "crit", "kid",
    }:
        raise ValueError("JWS protected header must have exactly alg,b64,crit,kid")
    if header["alg"] not in {"EdDSA", "ES256"}:
        raise ValueError("JWS alg must be EdDSA or ES256")
    if header["b64"] is not False or header["crit"] != ["b64"]:
        raise ValueError("JWS must use b64=false with crit=['b64']")
    if not rappid_valid(header["kid"]):
        raise ValueError("JWS kid must be a valid keyed RAPPID")
    if header_octets != canonical_bytes(header):
        raise ValueError("JWS protected header is not canonical")
    signature = _b64url_decode(parts[2])
    if len(signature) != 64:
        raise ValueError("JWS signature must be exactly 64 octets")
    return header, parts[0], signature


def _uint53(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 0 <= value <= MAX_SAFE_INTEGER
    )


def _hex64_or_null(value: Any) -> bool:
    return value is None or (
        isinstance(value, str) and bool(_HEX64.fullmatch(value))
    )


def _is_regenesis(kind: Any) -> bool:
    return isinstance(kind, str) and kind.partition(".")[2] == "re-genesis"


def _regenesis_payload_error(payload: Any) -> str | None:
    """§12.1 step 2 (rev-17 E-22): the one re-genesis payload shape."""
    if not isinstance(payload, dict) or set(payload) != {"migrated_from"}:
        return 're-genesis payload must be exactly {"migrated_from": {...}}'
    moved = payload["migrated_from"]
    if not isinstance(moved, dict) or set(moved) != {
        "stream_id", "terminal_seal", "terminal_seq",
    }:
        return "re-genesis migrated_from must be stream_id, terminal_seal, terminal_seq"
    if stream_form(moved["stream_id"]) is None:
        return "re-genesis migrated_from.stream_id is not a §6.1.1 stream_id"
    if not (
        isinstance(moved["terminal_seal"], str)
        and _HEX64.fullmatch(moved["terminal_seal"])
    ):
        return "re-genesis migrated_from.terminal_seal is not 64 lowercase hex"
    if not _uint53(moved["terminal_seq"]):
        return "re-genesis migrated_from.terminal_seq is not a uint53"
    return None


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
    """§11 Producer: refuse (never repair) a frame a consumer would refuse."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object (§7.1)")
    if 1 + _container_depth(payload) > MAX_DEPTH:
        raise ValueError(f"RAPP/1 frame nesting exceeds {MAX_DEPTH}")
    _names_ok(payload)
    if not kind_valid(kind):
        raise ValueError(f"kind {kind!r} is not a §6.1.1 kind")
    form = stream_form(stream_id)
    if form is None:
        raise ValueError(f"stream_id {stream_id!r} is not a §6.1.1 stream_id")
    if not _uint53(seq):
        raise ValueError("seq must be a uint53 (§7.4)")
    if not utc_valid(utc):
        raise ValueError("utc must be a valid fixed millisecond UTC (§7.4)")
    for name, value in (("prev", prev), ("prev_wave", prev_wave)):
        if not _hex64_or_null(value):
            raise ValueError(f"{name} must be null or lowercase 64-hex")
    if sig is not None:
        try:
            parse_detached_jws(sig)
        except Exception as exc:
            raise ValueError(f"sig is not a §10 detached JWS: {exc}") from exc
    if (seq == 0) != (prev is None):
        raise ValueError("only the genesis has seq 0 and prev null (§7.4)")
    if (prev_wave is not None) != (form == "swarm-stream" and seq > 0):
        raise ValueError("prev_wave is set iff a swarm-stream frame has seq > 0")
    if form == "swarm-stream" and sig is None:
        raise ValueError("a swarm-stream frame must be signed (§8)")
    if _is_regenesis(kind):
        if seq != 0 or prev is not None or sig is None:
            raise ValueError("a re-genesis frame is an owner-signed genesis")
        why = _regenesis_payload_error(payload)
        if why:
            raise ValueError(why)
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
    canonical_bytes(frame)  # §4 (d): the whole frame stays within 1 MiB
    return frame


def verify_frame(
    frame: dict[str, Any],
    *,
    head: dict[str, Any] | None = None,
    stream_id_of_record: str | None = None,
    signature_verifier: Any = None,
) -> tuple[bool, str | None, str]:
    """§7.5 consumer checklist without a §13 registry.

    A present sig verifies only through `signature_verifier(unsigned, sig)`,
    which returns a bool or (bool, reason); without one it is refused.
    """
    if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
        return False, "1", "frame must contain exactly the 11 RAPP/1 keys"
    if frame["spec"] != SPEC:
        return False, "1", "spec != rapp/1"
    if not kind_valid(frame["kind"]):
        return False, "1", "invalid kind"
    form = stream_form(frame["stream_id"])
    if form is None:
        return False, "1", "stream_id is not a §6.1.1 stream_id"
    if not _uint53(frame["seq"]):
        return False, "1", "seq is not uint53"
    if not utc_valid(frame["utc"]):
        return False, "1", "utc is not fixed millisecond UTC"
    if not isinstance(frame["payload"], dict):
        return False, "1", "payload is not an object"
    for field in ("payload_hash", "frame_hash"):
        if not isinstance(frame[field], str) or not _HEX64.fullmatch(frame[field]):
            return False, "1", f"{field} is not lowercase 64-hex"
    for field in ("prev", "prev_wave"):
        if not _hex64_or_null(frame[field]):
            return False, "1", f"{field} is not null or lowercase 64-hex"
    if frame["sig"] is not None:
        try:
            parse_detached_jws(frame["sig"])
        except Exception as exc:
            return False, "1", f"sig is not a §10 detached JWS: {exc}"
    regenesis = _is_regenesis(frame["kind"])
    if regenesis:
        why = _regenesis_payload_error(frame["payload"])
        if why:
            return False, "1", why
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
    if regenesis and (frame["seq"] != 0 or frame["prev"] is not None):
        return False, "4", "a re-genesis frame must be a genesis"
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
    is_swarm = form == "swarm-stream"
    if is_swarm and frame["seq"] > 0:
        if head is not None and frame["prev_wave"] != head["frame_hash"]:
            return False, "5", "prev_wave does not match swarm head"
    elif frame["prev_wave"] is not None:
        return False, "5", "prev_wave must be null off swarm"
    if is_swarm and frame["sig"] is None:
        return False, "6", "swarm frame must be signed"
    if regenesis and frame["sig"] is None:
        return False, "6", "a re-genesis frame must be owner-signed"
    if frame["sig"] is not None:
        if signature_verifier is None:
            return False, "6", "a signed frame needs a signature verifier"
        unsigned = {key: frame[key] for key in frame if key != "sig"}
        try:
            result = signature_verifier(unsigned, frame["sig"])
        except Exception as exc:
            return False, "6", f"signature verifier failed: {exc}"
        good = result[0] if isinstance(result, tuple) else result
        if not good:
            return False, "6", "signature refused"
    return True, None, "ok"
