#!/usr/bin/env python3
"""
RAPP Local Server - HTTP endpoint for brain stem

Runs locally and provides REST API for RAPP Desktop and external integrations.
"""

import json
import hmac
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Any
import threading

from brain_stem import process_request, get_brain_stem

DEFAULT_PORT = 7071
MAX_BODY_BYTES = 1_000_000
RAPP_HOME = Path.home() / ".rapp"


def _load_or_create_secret(path: Path) -> str:
    configured = os.getenv("RAPP_DESKTOP_SECRET")
    if configured:
        value = configured
    else:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            value = path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            value = secrets.token_hex(32)
            try:
                descriptor = os.open(
                    path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
            except FileExistsError:
                value = path.read_text(encoding="utf-8").strip()
            else:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(value + "\n")
        path.chmod(0o600)
    if len(value) < 32:
        raise RuntimeError("RAPP Desktop secret is invalid")
    return value


class RappRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for RAPP local server."""

    def _discard_request_body(self):
        if self.command != "POST":
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return
        if 0 < content_length <= MAX_BODY_BYTES:
            self.rfile.read(content_length)

    def _authorized(self):
        if self.headers.get("Origin") or self.headers.get("Sec-Fetch-Site"):
            self._discard_request_body()
            self._send_json({"error": "Browser access is disabled"}, 403)
            return False
        supplied = self.headers.get("X-RAPP-Desktop-Secret", "")
        expected = getattr(self.server, "rapp_secret", "")
        if not expected or not hmac.compare_digest(supplied, expected):
            self._discard_request_body()
            self._send_json({"error": "Unauthorized"}, 401)
            return False
        return True

    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Reject browser access; Electron talks to this service from main."""
        self._send_json({"error": "Browser access is disabled"}, 403)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/health':
            self._send_json({"status": "ok", "service": "rapp-brain-stem"})

        elif not self._authorized():
            return

        elif path == '/agents':
            brain = get_brain_stem()
            agents = brain.agent_registry.list_agents()
            self._send_json({"agents": agents})

        elif path == '/contexts':
            brain = get_brain_stem()
            contexts = brain.context_manager.list_contexts()
            self._send_json({"contexts": contexts})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        if not self._authorized():
            return
        content_type = self.headers.get('Content-Type', '').split(';', 1)[0].strip()
        if content_type != 'application/json':
            self._send_json({"error": "Content-Type must be application/json"}, 415)
            return

        # Read body
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            content_length = -1
        if not 0 <= content_length <= MAX_BODY_BYTES:
            self._send_json({"error": "Request body is too large"}, 413)
            return
        body = self.rfile.read(content_length).decode() if content_length else '{}'

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if path in ['/chat', '/api/rapp', '/api/chat', '/api/process']:
            # Main RAPP endpoint
            user_input = data.get('user_input', data.get('message', ''))
            if not user_input:
                self._send_json({"error": "user_input required"}, 400)
                return

            result = process_request(
                user_input=user_input,
                user_guid=data.get('user_guid', 'default'),
                session_guid=data.get('session_id', data.get('session_guid', '')),
                context_guid=data.get('context_guid', 'default'),
                conversation_history=data.get('conversation_history', [])
            )
            if "session_guid" in result:
                result.setdefault("session_id", result["session_guid"])
            self._send_json(result)

        elif path == '/api/context/create':
            # Create new context
            brain = get_brain_stem()
            ctx = brain.context_manager.create_context(
                name=data.get('name', 'New Context'),
                agents=data.get('agents', ['*']),
                skills=data.get('skills', ['*']),
                description=data.get('description', ''),
                system_prompt=data.get('system_prompt', '')
            )
            self._send_json({
                "guid": ctx.guid,
                "name": ctx.name
            })

        elif path == '/reload':
            brain = get_brain_stem()
            brain.reload()
            self._send_json({"status": "reloaded"})

        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class RappLocalServer:
    """Local HTTP server for RAPP brain stem."""

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        secret: str = None,
        secret_file: Path = None,
    ):
        self.port = port
        self.secret = secret or _load_or_create_secret(
            secret_file or (RAPP_HOME / "desktop_secret")
        )
        self.server = None
        self.thread = None

    def start(self):
        """Start the server in a background thread."""
        self.server = HTTPServer(('127.0.0.1', self.port), RappRequestHandler)
        self.server.rapp_secret = self.secret
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"RAPP Brain Stem running at http://127.0.0.1:{self.port}")

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server = None


def main():
    """Run the local server."""
    import signal

    server = RappLocalServer()
    server.start()

    print("Press Ctrl+C to stop")

    def signal_handler(sig, frame):
        print("\nShutting down...")
        server.stop()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep main thread alive
    while True:
        try:
            threading.Event().wait(1)
        except KeyboardInterrupt:
            break

    server.stop()


if __name__ == "__main__":
    main()
