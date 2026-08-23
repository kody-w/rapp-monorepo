"""Exact synchronous RAPP/1 POST /chat types and bounded HTTP client."""

from __future__ import annotations

import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from .errors import (
    RappRefusal,
    ResponseTooLarge,
    StructuralRefusalOnly,
    ValidationError,
    WireProtocolError,
    WireTransportError,
)
from .json_profile import canonical_bytes, strict_loads
from .trust import VerifiedRegistry

_SUCCESS_KEYS = frozenset({"response", "agent_logs", "session_id"})
_REFUSAL_STEPS = frozenset({"1", "1a", "2", "3", "4", "5", "6", None})


@dataclass(frozen=True)
class ChatRequest:
    user_input: str
    session_id: str | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.user_input, str):
            raise ValidationError("user_input is required and must be a string")
        for name in ("session_id", "idempotency_key"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ValidationError(f"{name} must be a string when present")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ChatRequest":
        """Ignore unknown input members as required by RAPP/1 §8."""

        if not isinstance(value, Mapping) or "user_input" not in value:
            raise ValidationError("request requires user_input")
        return cls(
            user_input=value["user_input"],
            session_id=value.get("session_id"),
            idempotency_key=value.get("idempotency_key"),
        )

    def as_dict(self) -> dict[str, str]:
        result = {"user_input": self.user_input}
        if self.session_id is not None:
            result["session_id"] = self.session_id
        if self.idempotency_key is not None:
            result["idempotency_key"] = self.idempotency_key
        return result


@dataclass(frozen=True)
class ChatSuccess:
    response: str
    agent_logs: tuple[str, ...]
    session_id: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "response": self.response,
            "agent_logs": list(self.agent_logs),
            "session_id": self.session_id,
        }


@dataclass(frozen=True)
class Refusal:
    code: str
    step: str | None

    def as_dict(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "step": self.step}}


def parse_success(value: Any) -> ChatSuccess:
    if not isinstance(value, dict) or set(value) != _SUCCESS_KEYS:
        raise WireProtocolError("HTTP 200 body must have exactly the three success members")
    if (
        not isinstance(value["response"], str)
        or not isinstance(value["session_id"], str)
        or not isinstance(value["agent_logs"], list)
        or not all(isinstance(log, str) for log in value["agent_logs"])
    ):
        raise WireProtocolError("HTTP 200 body has invalid RAPP/1 member types")
    return ChatSuccess(value["response"], tuple(value["agent_logs"]), value["session_id"])


def parse_refusal(value: Any) -> Refusal:
    """Parse exact refusal structure without claiming registered-code conformance."""
    if (
        not isinstance(value, dict)
        or set(value) != {"error"}
        or not isinstance(value["error"], dict)
        or set(value["error"]) != {"code", "step"}
    ):
        raise WireProtocolError("HTTP 422 body must be exactly {error:{code,step}}")
    code = value["error"]["code"]
    step = value["error"]["step"]
    if not isinstance(code, str) or not code or step not in _REFUSAL_STEPS:
        raise WireProtocolError("HTTP 422 code or step has an invalid type or value")
    return Refusal(code, step)


def accept_refusal(value: Any, *, registry: VerifiedRegistry) -> Refusal:
    """Accept a refusal only when its exact code is in a verified registry."""

    if not isinstance(registry, VerifiedRegistry):
        raise WireProtocolError("conformant refusal acceptance requires VerifiedRegistry")
    refusal = parse_refusal(value)
    try:
        registry.require_error_code(refusal.code)
    except Exception as exc:
        raise WireProtocolError(f"refusal error code is not registered: {refusal.code}") from exc
    return refusal


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ChatClient:
    def __init__(
        self,
        endpoint: str,
        *,
        timeout: float = 30.0,
        max_response_bytes: int = 1024 * 1024,
        registry: VerifiedRegistry | None = None,
    ):
        parsed = urllib.parse.urlsplit(endpoint)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.path != "/chat"
            or parsed.query
            or parsed.fragment
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValidationError("endpoint must be an explicit http(s) URL ending exactly in /chat")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValidationError("timeout must be positive")
        if not isinstance(max_response_bytes, int) or max_response_bytes <= 0:
            raise ValidationError("max_response_bytes must be positive")
        self.endpoint = endpoint
        self.timeout = float(timeout)
        self.max_response_bytes = max_response_bytes
        if registry is not None and not isinstance(registry, VerifiedRegistry):
            raise ValidationError("registry must be a VerifiedRegistry proof")
        self.registry = registry
        self._opener = urllib.request.build_opener(_NoRedirect)

    def _read(self, response) -> bytes:
        length = response.headers.get("Content-Length")
        if length:
            try:
                if int(length) > self.max_response_bytes:
                    raise ResponseTooLarge("RAPP/1 response exceeds configured bound")
            except ValueError as exc:
                raise WireProtocolError("invalid Content-Length") from exc
        data = response.read(self.max_response_bytes + 1)
        if len(data) > self.max_response_bytes:
            raise ResponseTooLarge("RAPP/1 response exceeds configured bound")
        return data

    @staticmethod
    def _require_json(response) -> None:
        content_type = response.headers.get("Content-Type", "")
        media_type = content_type.split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise WireProtocolError("RAPP/1 response media type must be application/json")

    def chat(self, request: ChatRequest | Mapping[str, Any]) -> ChatSuccess:
        if not isinstance(request, ChatRequest):
            request = ChatRequest.from_mapping(request)
        payload = canonical_bytes(request.as_dict())
        outgoing = urllib.request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            response = self._opener.open(outgoing, timeout=self.timeout)
            with response:
                self._require_json(response)
                body = self._read(response)
                status = response.status
        except urllib.error.HTTPError as exc:
            with exc:
                self._require_json(exc)
                body = self._read(exc)
                status = exc.code
        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
            raise WireTransportError(f"POST /chat failed: {exc}") from exc
        try:
            decoded = strict_loads(body)
        except Exception as exc:
            raise WireProtocolError(f"response is not strict I-JSON: {exc}") from exc
        if status == 200:
            return parse_success(decoded)
        if status == 422:
            structural = parse_refusal(decoded)
            if self.registry is None:
                raise StructuralRefusalOnly(structural.code, structural.step)
            refusal = accept_refusal(decoded, registry=self.registry)
            raise RappRefusal(refusal.code, refusal.step)
        raise WireProtocolError(f"RAPP/1 permits HTTP 200 success or HTTP 422 refusal, got {status}")
