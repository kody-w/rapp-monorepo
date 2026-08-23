"""RAPP/1 strict I-JSON parsing, RFC 8785 bytes, and domain hashes."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any

import rfc8785

from .errors import CanonicalizationError

MAX_CANONICAL_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_SAFE_INTEGER = (1 << 53) - 1
H_SPACES = frozenset({"rapp/1:particle", "rapp/1:wave", "rapp/1:egg-manifest"})
HB_SPACES = frozenset({"rapp/1:egg", "rapp/1:rappid", "rapp/1:seal"})


def _reject_constant(token: str) -> None:
    raise CanonicalizationError(f"non-finite number token {token!r}")


def _number_from_token(token: str, *, integer: bool) -> int | float:
    try:
        binary64 = float(token)
        original = Decimal(token)
    except (ValueError, OverflowError, InvalidOperation) as exc:
        raise CanonicalizationError(f"invalid number token {token!r}") from exc
    if not math.isfinite(binary64):
        raise CanonicalizationError(f"number is not finite: {token!r}")
    try:
        rendered = rfc8785.dumps(binary64).decode("ascii")
    except Exception as exc:
        raise CanonicalizationError(f"number is outside RFC 8785: {token!r}") from exc
    if Decimal(rendered) != original:
        raise CanonicalizationError(
            f"number does not survive the binary64/JCS round trip: {token!r}"
        )
    if integer and -MAX_SAFE_INTEGER <= int(token) <= MAX_SAFE_INTEGER:
        return int(token)
    return binary64


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CanonicalizationError(f"duplicate object member {key!r}")
        result[key] = value
    return result


def _has_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def _normalize_and_validate(value: Any, container_depth: int, seen: set[int]) -> Any:
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str) and _has_surrogate(value):
            raise CanonicalizationError("unpaired UTF-16 surrogate is forbidden")
        return value
    if isinstance(value, int):
        return _number_from_token(str(value), integer=True)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalizationError("non-finite float is forbidden")
        return value
    if isinstance(value, (list, tuple)):
        next_depth = container_depth + 1
        if next_depth > MAX_DEPTH:
            raise CanonicalizationError(f"JSON nesting depth exceeds {MAX_DEPTH}")
        marker = id(value)
        if marker in seen:
            raise CanonicalizationError("cyclic value is not JSON")
        seen.add(marker)
        try:
            return [_normalize_and_validate(item, next_depth, seen) for item in value]
        finally:
            seen.remove(marker)
    if isinstance(value, Mapping):
        next_depth = container_depth + 1
        if next_depth > MAX_DEPTH:
            raise CanonicalizationError(f"JSON nesting depth exceeds {MAX_DEPTH}")
        marker = id(value)
        if marker in seen:
            raise CanonicalizationError("cyclic value is not JSON")
        seen.add(marker)
        try:
            result: dict[str, Any] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise CanonicalizationError("JSON object keys must be strings")
                if _has_surrogate(key):
                    raise CanonicalizationError("unpaired UTF-16 surrogate is forbidden")
                result[key] = _normalize_and_validate(item, next_depth, seen)
            return result
        finally:
            seen.remove(marker)
    raise CanonicalizationError(f"value of type {type(value).__name__} is not I-JSON")


def canonical_bytes(value: Any) -> bytes:
    """Return the one RAPP/1 RFC 8785 byte string for an I-JSON value."""

    normalized = _normalize_and_validate(value, 0, set())
    try:
        encoded = rfc8785.dumps(normalized)
    except Exception as exc:
        raise CanonicalizationError(f"RFC 8785 canonicalization failed: {exc}") from exc
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise CanonicalizationError(
            f"canonical form exceeds {MAX_CANONICAL_BYTES} bytes"
        )
    return encoded


def strict_loads(data: str | bytes | bytearray) -> Any:
    """Parse the RAPP input-domain profile without repairing invalid input."""

    if isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
        if raw.startswith(b"\xef\xbb\xbf"):
            raise CanonicalizationError("a UTF-8 byte-order mark is forbidden")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CanonicalizationError("JSON must be valid UTF-8") from exc
    elif isinstance(data, str):
        text = data
        if text.startswith("\ufeff"):
            raise CanonicalizationError("a byte-order mark is forbidden")
    else:
        raise TypeError("strict_loads expects str or bytes")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_int=lambda token: _number_from_token(token, integer=True),
            parse_float=lambda token: _number_from_token(token, integer=False),
            parse_constant=_reject_constant,
        )
    except CanonicalizationError:
        raise
    except RecursionError as exc:
        raise CanonicalizationError(
            f"JSON nesting exceeds the RAPP/{MAX_DEPTH} container limit"
        ) from exc
    except (json.JSONDecodeError, UnicodeError, ValueError) as exc:
        raise CanonicalizationError(f"invalid JSON: {exc}") from exc
    canonical_bytes(value)
    return value


def _space_prefix(space: str) -> bytes:
    if not isinstance(space, str) or not space:
        raise CanonicalizationError("hash space must be a non-empty string")
    try:
        encoded = space.encode("ascii")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("hash space must be ASCII") from exc
    if b"\n" in encoded:
        raise CanonicalizationError("hash space must not contain LF")
    return encoded + b"\n"


def H(space: str, value: Any) -> str:
    """Domain-separated SHA-256 over canonical JSON."""

    if space not in H_SPACES:
        raise CanonicalizationError(f"{space!r} is not allocated to H")
    return hashlib.sha256(_space_prefix(space) + canonical_bytes(value)).hexdigest()


def Hb(space: str, octets: bytes | bytearray | memoryview) -> str:
    """Domain-separated SHA-256 over raw octets."""

    if not isinstance(octets, (bytes, bytearray, memoryview)):
        raise TypeError("Hb expects raw octets")
    if space not in HB_SPACES:
        raise CanonicalizationError(f"{space!r} is not allocated to Hb")
    return hashlib.sha256(_space_prefix(space) + bytes(octets)).hexdigest()
