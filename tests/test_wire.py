from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from rapp_sdk.errors import (
    RappRefusal,
    ResponseTooLarge,
    StructuralRefusalOnly,
    WireProtocolError,
)
from rapp_sdk import parse_refusal as public_parse_refusal
from rapp_sdk.wire import ChatClient, ChatRequest, accept_refusal, parse_refusal


class _Server:
    def __init__(self, status: int, body: dict, content_type: str = "application/json"):
        captured = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers["Content-Length"])
                captured.raw_request = self.rfile.read(length)
                captured.request = json.loads(captured.raw_request)
                encoded = json.dumps(body, separators=(",", ":")).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format, *args):
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.request = None
        self.raw_request = None

    @property
    def endpoint(self) -> str:
        return f"http://127.0.0.1:{self.httpd.server_port}/chat"

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)


def test_exact_wire_success_and_unknown_request_members_not_emitted() -> None:
    assert public_parse_refusal is parse_refusal
    server = _Server(
        200, {"response": "ok", "agent_logs": ["one"], "session_id": "session"}
    )
    try:
        result = ChatClient(server.endpoint).chat(
            ChatRequest.from_mapping(
                {
                    "user_input": "hi",
                    "session_id": "s",
                    "idempotency_key": "i",
                    "ignored": "not emitted",
                }
            )
        )
        assert result.as_dict() == {
            "response": "ok",
            "agent_logs": ["one"],
            "session_id": "session",
        }
        assert server.request == {
            "user_input": "hi",
            "session_id": "s",
            "idempotency_key": "i",
        }
        assert server.raw_request == (
            b'{"idempotency_key":"i","session_id":"s","user_input":"hi"}'
        )
    finally:
        server.close()


def test_structural_and_registered_wire_refusal_are_distinct(registry) -> None:
    server = _Server(422, {"error": {"code": "test-refusal", "step": "1a"}})
    try:
        with pytest.raises(StructuralRefusalOnly):
            ChatClient(server.endpoint).chat(ChatRequest("hi"))
        with pytest.raises(RappRefusal) as failure:
            ChatClient(server.endpoint, registry=registry).chat(ChatRequest("hi"))
        assert failure.value.code == "test-refusal"
        assert failure.value.step == "1a"
        structural = parse_refusal({"error": {"code": "unregistered", "step": None}})
        assert structural.code == "unregistered"
        with pytest.raises(WireProtocolError, match="not registered"):
            accept_refusal(structural.as_dict(), registry=registry)
    finally:
        server.close()


@pytest.mark.parametrize(
    "body",
    [
        {"response": "ok", "agent_logs": [], "session_id": "s", "extra": True},
        {"response": "ok", "agent_logs": [1], "session_id": "s"},
    ],
)
def test_wire_rejects_inexact_success(body) -> None:
    server = _Server(200, body)
    try:
        with pytest.raises(WireProtocolError):
            ChatClient(server.endpoint).chat(ChatRequest("hi"))
    finally:
        server.close()


def test_wire_response_bound_and_media_type() -> None:
    server = _Server(
        200, {"response": "x" * 100, "agent_logs": [], "session_id": "s"}
    )
    try:
        with pytest.raises(ResponseTooLarge):
            ChatClient(server.endpoint, max_response_bytes=20).chat(ChatRequest("hi"))
    finally:
        server.close()
    server = _Server(
        200,
        {"response": "ok", "agent_logs": [], "session_id": "s"},
        "text/plain",
    )
    try:
        with pytest.raises(WireProtocolError, match="media type"):
            ChatClient(server.endpoint).chat(ChatRequest("hi"))
    finally:
        server.close()
