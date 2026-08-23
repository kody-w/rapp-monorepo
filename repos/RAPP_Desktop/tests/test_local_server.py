#!/usr/bin/env python3
"""
Tests for RAPP Local Server

Run: pytest tests/test_local_server.py -v
"""

import os
import sys
import json
import pytest
import tempfile
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add rapp_os to path
sys.path.insert(0, str(Path(__file__).parent.parent / "rapp_os" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "rapp_os"))

TEST_SECRET = "test-secret"


def auth_headers(server):
    return {"X-RAPP-Desktop-Secret": server.secret}


def _test_worker_target(
    user_input,
    user_guid,
    session_guid,
    context_guid,
    conversation_history,
):
    if user_input == "slow":
        time.sleep(30)
    response = "X" * 4_100_000 if user_input == "large" else "Test response"
    return {
        "response": response,
        "voice_response": "",
        "agent_logs": [],
        "agents_used": [],
        "session_guid": "test_session",
        "context_guid": context_guid,
        "received": {
            "user_input": user_input,
            "user_guid": user_guid,
            "session_guid": session_guid,
            "context_guid": context_guid,
            "conversation_history": conversation_history,
        },
    }


def wait_for_worker(server, request_id, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with server.server._workers_lock:
            worker = server.server._workers.get(request_id)
        if worker is not None:
            return worker
        time.sleep(0.02)
    pytest.fail(f"Worker {request_id} did not start")


@pytest.fixture
def mock_brain_stem(tmp_path):
    """Create a mock brain stem for testing."""
    with patch('local_server.RAPP_HOME', tmp_path):
        with patch('brain_stem.RAPP_HOME', tmp_path):
            with patch('brain_stem.AGENTS_DIR', tmp_path / "agents"):
                with patch('brain_stem.CONTEXTS_DIR', tmp_path / "contexts"):
                    with patch('brain_stem.MEMORY_DIR', tmp_path / "memory"):
                        yield


class TestRappLocalServer:
    """Tests for RappLocalServer class."""

    def test_server_initialization(self):
        """Test server initializes with correct defaults."""
        from local_server import RappLocalServer

        server = RappLocalServer(secret=TEST_SECRET)
        assert server.port == 7071
        assert server.server is None
        assert server.thread is None

    def test_server_custom_port(self):
        """Test server with custom port."""
        from local_server import RappLocalServer

        server = RappLocalServer(port=8080, secret=TEST_SECRET)
        assert server.port == 8080


class TestServerEndpoints:
    """Tests for HTTP endpoints."""

    @pytest.fixture
    def running_server(self, tmp_path):
        """Start a server for testing."""
        from local_server import RappLocalServer

        with patch('local_server.process_request') as mock_process:
            mock_process.return_value = {
                "response": "Test response",
                "voice_response": "",
                "agent_logs": [],
                "agents_used": [],
                "session_guid": "test_session",
                "context_guid": "default"
            }

            with patch('local_server.get_brain_stem') as mock_brain:
                mock_brain_instance = MagicMock()
                mock_brain_instance.agent_registry.list_agents.return_value = []
                mock_brain_instance.context_manager.list_contexts.return_value = []
                mock_brain.return_value = mock_brain_instance

                server = RappLocalServer(
                    port=7999,
                    secret=TEST_SECRET,
                    worker_target=_test_worker_target,
                )
                server.start()
                time.sleep(0.2)  # Wait for server to start

                yield server, mock_process

                server.stop()

    def test_health_endpoint(self, running_server):
        """Test /health endpoint returns OK."""
        server, _ = running_server
        response = requests.get(f"http://127.0.0.1:{server.port}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "rapp-brain-stem"

    def test_agents_endpoint(self, running_server):
        """Test /agents endpoint returns agent list."""
        server, _ = running_server
        response = requests.get(
            f"http://127.0.0.1:{server.port}/agents",
            headers=auth_headers(server),
        )
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data

    def test_contexts_endpoint(self, running_server):
        """Test /contexts endpoint returns context list."""
        server, _ = running_server
        response = requests.get(
            f"http://127.0.0.1:{server.port}/contexts",
            headers=auth_headers(server),
        )
        assert response.status_code == 200
        data = response.json()
        assert "contexts" in data

    def test_reload_endpoint(self, running_server):
        """Test /reload endpoint triggers reload."""
        server, _ = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/reload",
            json={},
            headers=auth_headers(server),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reloaded"

    def test_not_found_endpoint(self, running_server):
        """Test unknown endpoint returns 404."""
        server, _ = running_server
        response = requests.get(
            f"http://127.0.0.1:{server.port}/unknown",
            headers=auth_headers(server),
        )
        assert response.status_code == 404

    def test_chat_endpoint(self, running_server):
        """Test the RAPP/1 /chat endpoint."""
        server, mock_process = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/chat",
            json={"user_input": "Hello", "session_id": "desktop-session"},
            headers=auth_headers(server),
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["session_id"] == "test_session"
        assert data["received"]["session_guid"] == "desktop-session"

    def test_chat_endpoint_missing_input(self, running_server):
        """Test chat endpoint requires user_input."""
        server, _ = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/api/rapp",
            json={},
            headers=auth_headers(server),
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_chat_with_message_key(self, running_server):
        """Test chat endpoint accepts 'message' as alternative key."""
        server, mock_process = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/api/rapp",
            json={"message": "Hello via message key"},
            headers=auth_headers(server),
        )
        assert response.status_code == 200

    def test_chat_with_all_params(self, running_server):
        """Test chat endpoint with all parameters."""
        server, mock_process = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/api/chat",
            json={
                "user_input": "Hello",
                "user_guid": "test_user",
                "session_guid": "test_session",
                "context_guid": "test_context",
                "conversation_history": [
                    {"role": "user", "content": "Previous message"}
                ]
            },
            headers=auth_headers(server),
        )
        assert response.status_code == 200

        # Verify all params were passed
        call_kwargs = response.json()["received"]
        assert call_kwargs["user_input"] == "Hello"
        assert call_kwargs["user_guid"] == "test_user"
        assert call_kwargs["session_guid"] == "test_session"
        assert call_kwargs["context_guid"] == "test_context"


class TestCancellation:
    """Chat work is isolated, cancellable, and never serializes the server."""

    @pytest.fixture
    def running_server(self):
        from local_server import RappLocalServer

        server = RappLocalServer(
            port=0,
            secret=TEST_SECRET,
            worker_target=_test_worker_target,
        )
        server.start()
        yield server
        server.stop()

    def test_cancel_ends_exact_worker_and_next_request_is_prompt(
        self,
        running_server,
    ):
        server = running_server
        base_url = f"http://127.0.0.1:{server.port}"
        headers = auth_headers(server)

        with ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(
                requests.post,
                f"{base_url}/chat",
                json={"request_id": "slow-request", "user_input": "slow"},
                headers=headers,
                timeout=10,
            )
            worker = wait_for_worker(server, "slow-request")

            started = time.monotonic()
            health = requests.get(f"{base_url}/health", timeout=2)
            assert health.status_code == 200
            assert time.monotonic() - started < 1

            duplicate = requests.post(
                f"{base_url}/chat",
                json={"request_id": "slow-request", "user_input": "Hello"},
                headers=headers,
                timeout=2,
            )
            assert duplicate.status_code == 409

            started = time.monotonic()
            cancelled = requests.post(
                f"{base_url}/cancel",
                json={"request_id": "slow-request"},
                headers=headers,
                timeout=7,
            )
            assert cancelled.status_code == 200
            assert cancelled.json() == {
                "status": "cancelled",
                "request_id": "slow-request",
                "cancelled": True,
                "worker_ended": True,
            }
            assert time.monotonic() - started < 5
            assert not worker.process.is_alive()
            assert pending.result(timeout=2).status_code == 409

        started = time.monotonic()
        second = requests.post(
            f"{base_url}/chat",
            json={"request_id": "second-request", "user_input": "Hello"},
            headers=headers,
            timeout=7,
        )
        assert second.status_code == 200
        assert second.json()["response"] == "Test response"
        assert time.monotonic() - started < 5

    def test_cancel_requires_authentication(self, running_server):
        response = requests.post(
            f"http://127.0.0.1:{running_server.port}/cancel",
            json={"request_id": "not-authorized"},
            timeout=2,
        )
        assert response.status_code == 401

    def test_client_disconnect_ends_worker(self, running_server):
        import socket

        server = running_server
        body = json.dumps({
            "request_id": "disconnected-request",
            "user_input": "slow",
        }).encode()
        connection = socket.create_connection(("127.0.0.1", server.port))
        connection.sendall(
            (
                "POST /chat HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{server.port}\r\n"
                "Content-Type: application/json\r\n"
                f"X-RAPP-Desktop-Secret: {server.secret}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode()
            + body
        )
        worker = wait_for_worker(server, "disconnected-request")
        connection.close()

        deadline = time.monotonic() + 5
        while worker.process.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert not worker.process.is_alive()
        with server.server._workers_lock:
            assert "disconnected-request" not in server.server._workers

    def test_server_shutdown_ends_workers(self, running_server):
        server = running_server
        base_url = f"http://127.0.0.1:{server.port}"
        with ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(
                requests.post,
                f"{base_url}/chat",
                json={"request_id": "shutdown-request", "user_input": "slow"},
                headers=auth_headers(server),
                timeout=10,
            )
            worker = wait_for_worker(server, "shutdown-request")
            server.stop()
            assert not worker.process.is_alive()
            try:
                pending.result(timeout=2)
            except requests.RequestException:
                pass

    def test_request_and_result_sizes_are_bounded(self, running_server):
        server = running_server
        base_url = f"http://127.0.0.1:{server.port}"
        oversized = requests.post(
            f"{base_url}/chat",
            data=b"X" * 1_000_001,
            headers={
                **auth_headers(server),
                "Content-Type": "application/json",
            },
            timeout=2,
        )
        assert oversized.status_code == 413

        result = requests.post(
            f"{base_url}/chat",
            json={"request_id": "large-result", "user_input": "large"},
            headers=auth_headers(server),
            timeout=7,
        )
        assert result.status_code == 502
        assert result.json()["error"] == "Brainstem result is too large"


class TestBrowserIsolation:
    """The local engine is not a browser API."""

    @pytest.fixture
    def running_server(self):
        """Start a server for browser-isolation testing."""
        from local_server import RappLocalServer

        with patch('local_server.process_request') as mock_process:
            mock_process.return_value = {
                "response": "OK",
                "voice_response": "",
                "agent_logs": [],
                "agents_used": [],
                "session_guid": "",
                "context_guid": ""
            }

            with patch('local_server.get_brain_stem') as mock_brain:
                mock_brain.return_value = MagicMock()

                server = RappLocalServer(port=7998, secret=TEST_SECRET)
                server.start()
                time.sleep(0.2)

                yield server

                server.stop()

    def test_cors_headers_are_not_exposed(self, running_server):
        """A random web page cannot call the local companion engine."""
        response = requests.get(f"http://127.0.0.1:{running_server.port}/health")
        assert "Access-Control-Allow-Origin" not in response.headers

    def test_options_preflight_is_rejected(self, running_server):
        """Browser preflight is rejected instead of granting wildcard CORS."""
        response = requests.options(f"http://127.0.0.1:{running_server.port}/api/rapp")
        assert response.status_code == 403
        assert response.json()["error"] == "Browser access is disabled"

    def test_cross_origin_simple_post_is_rejected(self, running_server):
        """A no-CORS browser POST cannot trigger a local agent."""
        response = requests.post(
            f"http://127.0.0.1:{running_server.port}/chat",
            data='{"user_input":"attack"}',
            headers={
                "Content-Type": "text/plain",
                "Origin": "https://attacker.example",
            },
        )
        assert response.status_code == 403
        assert response.json()["error"] == "Browser access is disabled"

    def test_missing_secret_is_rejected(self, running_server):
        response = requests.post(
            f"http://127.0.0.1:{running_server.port}/chat",
            json={"user_input": "Hello"},
        )
        assert response.status_code == 401


class TestContextCreation:
    """Tests for context creation endpoint."""

    @pytest.fixture
    def running_server(self):
        """Start a server for context testing."""
        from local_server import RappLocalServer

        with patch('local_server.get_brain_stem') as mock_brain:
            mock_context = MagicMock()
            mock_context.guid = "new_context_id"
            mock_context.name = "Test Context"

            mock_brain_instance = MagicMock()
            mock_brain_instance.context_manager.create_context.return_value = mock_context
            mock_brain.return_value = mock_brain_instance

            server = RappLocalServer(port=7997, secret=TEST_SECRET)
            server.start()
            time.sleep(0.2)

            yield server, mock_brain_instance

            server.stop()

    def test_create_context_endpoint(self, running_server):
        """Test /api/context/create endpoint."""
        server, mock_brain = running_server
        response = requests.post(
            f"http://127.0.0.1:{server.port}/api/context/create",
            json={
                "name": "Test Context",
                "agents": ["agent1"],
                "description": "Test description"
            },
            headers=auth_headers(server),
        )
        assert response.status_code == 200
        data = response.json()
        assert "guid" in data
        assert "name" in data


class TestInvalidJSON:
    """Tests for invalid JSON handling."""

    @pytest.fixture
    def running_server(self):
        """Start a server for JSON testing."""
        from local_server import RappLocalServer

        with patch('local_server.get_brain_stem') as mock_brain:
            mock_brain.return_value = MagicMock()

            server = RappLocalServer(port=7996, secret=TEST_SECRET)
            server.start()
            time.sleep(0.2)

            yield server

            server.stop()

    def test_invalid_json_body(self, running_server):
        """Test handling of invalid JSON in request body."""
        response = requests.post(
            f"http://127.0.0.1:{running_server.port}/api/rapp",
            data="not valid json",
            headers={
                "Content-Type": "application/json",
                **auth_headers(running_server),
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid JSON" in data["error"]


class TestServerLifecycle:
    """Tests for server start/stop lifecycle."""

    def test_server_start_stop(self):
        """Test server can be started and stopped."""
        from local_server import RappLocalServer

        with patch('local_server.get_brain_stem') as mock_brain:
            mock_brain.return_value = MagicMock()

            server = RappLocalServer(port=7995, secret=TEST_SECRET)
            server.start()
            time.sleep(0.2)

            # Verify server is running
            try:
                response = requests.get(f"http://127.0.0.1:{server.port}/health", timeout=1)
                assert response.status_code == 200
            except requests.exceptions.ConnectionError:
                pytest.fail("Server did not start")

            # Stop server
            server.stop()
            time.sleep(0.2)

            # Verify server is stopped
            with pytest.raises(requests.exceptions.ConnectionError):
                requests.get(f"http://127.0.0.1:{server.port}/health", timeout=1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
