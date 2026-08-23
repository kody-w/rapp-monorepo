#!/usr/bin/env python3
"""
RAPP Local Server - HTTP endpoint for brain stem

Runs locally and provides REST API for RAPP Desktop and external integrations.
"""

import hmac
import json
import multiprocessing
import os
import queue
import secrets
import select
import socket
import threading
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict
from urllib.parse import urlparse

from brain_stem import get_brain_stem, process_request

DEFAULT_PORT = 7071
MAX_BODY_BYTES = 1_000_000
MAX_RESULT_BYTES = 4_000_000
REQUEST_ID_MAX_LENGTH = 128
WORKER_JOIN_TIMEOUT_SECONDS = 5
RAPP_HOME = Path.home() / ".rapp"

WorkerTarget = Callable[..., Dict[str, Any]]


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


def _encode_result(data: Dict[str, Any], status: int = 200):
    try:
        encoded = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError):
        status = 500
        encoded = b'{"error":"Brainstem returned an invalid result"}'
    if len(encoded) > MAX_RESULT_BYTES:
        status = 502
        encoded = b'{"error":"Brainstem result is too large"}'
    return status, encoded


def _run_chat_worker(
    target: WorkerTarget,
    arguments: Dict[str, Any],
    result_queue,
):
    """Process entry point; all arguments are spawn-safe and bounded."""
    try:
        result = target(**arguments)
        if not isinstance(result, dict):
            result_queue.put(
                _encode_result(
                    {"error": "Brainstem returned an invalid result"},
                    500,
                )
            )
            return
        if "session_guid" in result:
            result.setdefault("session_id", result["session_guid"])
        result_queue.put(_encode_result(result))
    except BaseException as error:
        result_queue.put(
            _encode_result(
                {"error": f"Brainstem request failed: {type(error).__name__}"},
                500,
            )
        )


@dataclass
class _ActiveWorker:
    request_id: str
    process: multiprocessing.Process
    result_queue: Any
    cancelled: threading.Event = field(default_factory=threading.Event)
    lock: threading.Lock = field(default_factory=threading.Lock)
    resources_closed: bool = False


class _RappThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address,
        handler_class,
        secret: str,
        worker_target: WorkerTarget,
    ):
        super().__init__(server_address, handler_class)
        self.rapp_secret = secret
        self.worker_target = worker_target
        self.worker_context = multiprocessing.get_context("spawn")
        self._workers: Dict[str, _ActiveWorker] = {}
        self._workers_lock = threading.Lock()

    def start_worker(
        self,
        request_id: str,
        arguments: Dict[str, Any],
    ):
        result_queue = self.worker_context.Queue(maxsize=1)
        process = self.worker_context.Process(
            target=_run_chat_worker,
            args=(self.worker_target, arguments, result_queue),
            name=f"rapp-chat-{request_id[:32]}",
        )
        worker = _ActiveWorker(request_id, process, result_queue)
        with self._workers_lock:
            if request_id in self._workers:
                self._close_worker_resources(worker)
                return None
            self._workers[request_id] = worker
            try:
                process.start()
            except BaseException:
                self._workers.pop(request_id, None)
                self._close_worker_resources(worker)
                raise
        return worker

    def _remove_worker(self, worker: _ActiveWorker):
        with self._workers_lock:
            if self._workers.get(worker.request_id) is worker:
                self._workers.pop(worker.request_id, None)

    @staticmethod
    def _stop_process(process: multiprocessing.Process):
        if process.is_alive():
            process.terminate()
        process.join(WORKER_JOIN_TIMEOUT_SECONDS)
        if process.is_alive():
            process.kill()
            process.join(WORKER_JOIN_TIMEOUT_SECONDS)
        return not process.is_alive()

    @staticmethod
    def _close_worker_resources(worker: _ActiveWorker):
        if worker.resources_closed:
            return
        worker.resources_closed = True
        worker.result_queue.close()
        worker.result_queue.join_thread()

    def finish_worker(self, worker: _ActiveWorker, terminate: bool = False):
        with worker.lock:
            if terminate:
                worker_ended = self._stop_process(worker.process)
            else:
                worker.process.join(WORKER_JOIN_TIMEOUT_SECONDS)
                if worker.process.is_alive():
                    worker_ended = self._stop_process(worker.process)
                else:
                    worker_ended = True
            if worker_ended:
                self._remove_worker(worker)
                self._close_worker_resources(worker)

    def cancel_worker(self, request_id: str):
        with self._workers_lock:
            worker = self._workers.get(request_id)
        if worker is None:
            return {
                "status": "not_found",
                "request_id": request_id,
                "cancelled": False,
                "worker_ended": True,
            }
        with worker.lock:
            worker.cancelled.set()
            worker_ended = self._stop_process(worker.process)
            if worker_ended:
                self._remove_worker(worker)
        return {
            "status": "cancelled" if worker_ended else "error",
            "request_id": request_id,
            "cancelled": worker_ended,
            "worker_ended": worker_ended,
        }

    def cancel_all_workers(self):
        with self._workers_lock:
            request_ids = list(self._workers)
        for request_id in request_ids:
            self.cancel_worker(request_id)


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

    def _send_encoded_json(self, encoded: bytes, status: int = 200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return False
        return True

    def _send_json(self, data: Dict, status: int = 200):
        """Send a bounded JSON response."""
        result_status, encoded = _encode_result(data, status)
        return self._send_encoded_json(encoded, result_status)

    def _read_json_body(self):
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if content_type != "application/json":
            self._send_json(
                {"error": "Content-Type must be application/json"},
                415,
            )
            return None
        if self.headers.get("Transfer-Encoding"):
            self._send_json({"error": "Transfer-Encoding is not supported"}, 400)
            return None
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = -1
        if not 0 <= content_length <= MAX_BODY_BYTES:
            self._send_json({"error": "Request body is too large"}, 413)
            return None
        try:
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            body = raw_body.decode("utf-8")
            data = json.loads(body)
        except UnicodeDecodeError:
            self._send_json({"error": "Request body must be UTF-8"}, 400)
            return None
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return None
        if not isinstance(data, dict):
            self._send_json({"error": "JSON body must be an object"}, 400)
            return None
        return data

    def _request_id(self, data: Dict[str, Any], generate: bool = False):
        request_id = data.get("request_id")
        if request_id is None and generate:
            return f"server-{uuid.uuid4()}"
        if (
            not isinstance(request_id, str)
            or not request_id
            or len(request_id) > REQUEST_ID_MAX_LENGTH
            or request_id.strip() != request_id
            or any(ord(character) < 32 for character in request_id)
        ):
            self._send_json({"error": "A valid request_id is required"}, 400)
            return None
        return request_id

    def _client_disconnected(self):
        try:
            readable, _, _ = select.select([self.connection], [], [], 0)
            if not readable:
                return False
            return self.connection.recv(1, socket.MSG_PEEK) == b""
        except (OSError, ValueError):
            return True

    def do_OPTIONS(self):
        """Reject browser access; Electron talks to this service from main."""
        self._send_json({"error": "Browser access is disabled"}, 403)

    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path

        if path == "/health":
            self._send_json({"status": "ok", "service": "rapp-brain-stem"})
        elif not self._authorized():
            return
        elif path == "/agents":
            brain = get_brain_stem()
            self._send_json({"agents": brain.agent_registry.list_agents()})
        elif path == "/contexts":
            brain = get_brain_stem()
            self._send_json({"contexts": brain.context_manager.list_contexts()})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        if not self._authorized():
            return
        data = self._read_json_body()
        if data is None:
            return

        if path == "/cancel":
            request_id = self._request_id(data)
            if request_id is None:
                return
            result = self.server.cancel_worker(request_id)
            self._send_json(result, 200 if result["worker_ended"] else 500)
            return

        if path in ["/chat", "/api/rapp", "/api/chat", "/api/process"]:
            self._handle_chat(data)
        elif path == "/api/context/create":
            brain = get_brain_stem()
            ctx = brain.context_manager.create_context(
                name=data.get("name", "New Context"),
                agents=data.get("agents", ["*"]),
                skills=data.get("skills", ["*"]),
                description=data.get("description", ""),
                system_prompt=data.get("system_prompt", ""),
            )
            self._send_json({"guid": ctx.guid, "name": ctx.name})
        elif path == "/reload":
            brain = get_brain_stem()
            brain.reload()
            self._send_json({"status": "reloaded"})
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_chat(self, data: Dict[str, Any]):
        user_input = data.get("user_input", data.get("message", ""))
        if not user_input:
            self._send_json({"error": "user_input required"}, 400)
            return
        request_id = self._request_id(data, generate=True)
        if request_id is None:
            return
        arguments = {
            "user_input": user_input,
            "user_guid": data.get("user_guid", "default"),
            "session_guid": data.get(
                "session_id",
                data.get("session_guid", ""),
            ),
            "context_guid": data.get("context_guid", "default"),
            "conversation_history": data.get("conversation_history", []),
        }
        try:
            worker = self.server.start_worker(request_id, arguments)
        except BaseException as error:
            self._send_json(
                {"error": f"Unable to start Brainstem worker: {type(error).__name__}"},
                500,
            )
            return
        if worker is None:
            self._send_json(
                {"error": "A request with this request_id is already active"},
                409,
            )
            return

        terminate = True
        try:
            while True:
                if worker.cancelled.is_set():
                    self._send_json({"error": "Request cancelled"}, 409)
                    return
                if self._client_disconnected():
                    return
                try:
                    status, encoded = worker.result_queue.get(timeout=0.05)
                    terminate = False
                    self._send_encoded_json(encoded, status)
                    return
                except queue.Empty:
                    if worker.process.is_alive():
                        continue
                    if worker.cancelled.is_set():
                        self._send_json({"error": "Request cancelled"}, 409)
                        return
                    try:
                        status, encoded = worker.result_queue.get(timeout=0.2)
                    except queue.Empty:
                        self._send_json(
                            {"error": "Brainstem worker exited without a result"},
                            500,
                        )
                    else:
                        terminate = False
                        self._send_encoded_json(encoded, status)
                    return
        finally:
            self.server.finish_worker(worker, terminate=terminate)

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
        worker_target: WorkerTarget = process_request,
    ):
        self.port = port
        self.secret = secret or _load_or_create_secret(
            secret_file or (RAPP_HOME / "desktop_secret")
        )
        self.worker_target = worker_target
        self.server = None
        self.thread = None

    def start(self):
        """Start the concurrent server in a background thread."""
        self.server = _RappThreadingHTTPServer(
            ("127.0.0.1", self.port),
            RappRequestHandler,
            self.secret,
            self.worker_target,
        )
        self.port = self.server.server_port
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        print(f"RAPP Brain Stem running at http://127.0.0.1:{self.port}")

    def stop(self):
        """Stop the server and every isolated request worker."""
        server = self.server
        if server:
            server.shutdown()
            server.cancel_all_workers()
            server.server_close()
            if self.thread and self.thread is not threading.current_thread():
                self.thread.join(WORKER_JOIN_TIMEOUT_SECONDS)
            self.server = None
            self.thread = None


def main():
    """Run the local server."""
    import signal

    multiprocessing.freeze_support()
    server = RappLocalServer()
    server.start()

    print("Press Ctrl+C to stop")

    def signal_handler(sig, frame):
        print("\nShutting down...")
        server.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
