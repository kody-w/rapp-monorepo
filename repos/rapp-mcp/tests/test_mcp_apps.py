#!/usr/bin/env python3
"""MCP Apps (rapp-mcp-spec/2.1) tests for rapp_mcp.py. Zero external deps — run directly:

    python3 tests/test_mcp_apps.py

A rapplication is an agent with a UI beside it (`foo_agent.py` + `foo_agent.ui.html`). Its UI is
a ui:// resource linked to the tool, and the app-only rapp_chat tool appears. Hosts are not asked
to announce MCP Apps first: the official reference host and example servers do not. A folder with
no UI answers exactly as 2.0 did.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable
sys.path.insert(0, HERE)
from test_servers import mcp  # noqa: E402

UI_MIME = "text/html;profile=mcp-app"


def handshake(with_ui):
    caps = {"extensions": {"io.modelcontextprotocol/ui": {"mimeTypes": [UI_MIME]}}} if with_ui else {}
    return [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": caps,
                        "clientInfo": {"name": "tests", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"}]


def call(i, name, args):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}}


def text(result):
    return ((result or {}).get("content") or [{}])[0].get("text", "")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    fails = []
    with tempfile.TemporaryDirectory() as root:
        agents = os.path.join(root, "agents")
        os.makedirs(agents)
        for f in ("hello_agent.py", "hello_agent.ui.html"):
            shutil.copy(os.path.join(REPO, "examples", f), agents)
        os.environ["RAPP_MCP_DATA"] = os.path.join(root, "data")
        os.environ["RAPP_BRAINSTEM_URL"] = f"http://127.0.0.1:{free_port()}"  # nothing listens here
        server = [PY, os.path.join(REPO, "rapp_mcp.py"), agents]
        lists = [{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                 {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}]

        # 1. A folder without any UI is the 2.0 surface, unchanged.
        plain = os.path.join(root, "plain")
        os.makedirs(plain)
        shutil.copy(os.path.join(REPO, "examples", "hello_agent.py"), plain)
        r = mcp([PY, os.path.join(REPO, "rapp_mcp.py"), plain], handshake(True) + lists)
        tools = (r.get(2) or {}).get("tools", [])
        if [t["name"] for t in tools] != ["hello"] or "_meta" in tools[0]:
            fails.append(f"no-UI folder: expected the bare hello tool, got {tools}")
        if "resources" in (r.get(1) or {}).get("capabilities", {}) or (r.get(3) or {}).get("resources"):
            fails.append(f"no-UI folder: resources must stay off, got {r.get(1)} / {r.get(3)}")

        # 2. With a UI beside the agent, any host gets it linked to the tool, plus app-only rapp_chat.
        uri = "ui://rapp-mcp/hello"
        r = mcp(server, handshake(False) + lists + [
            {"jsonrpc": "2.0", "id": 4, "method": "resources/read", "params": {"uri": uri}},
            {"jsonrpc": "2.0", "id": 5, "method": "resources/read", "params": {"uri": "ui://rapp-mcp/nope"}},
            call(6, "rapp_chat", {"user_input": 'Use the hello tool with name="Ada Lovelace". Reply only DONE.'}),
            call(7, "rapp_chat", {"user_input": 'Hello {"name": "Grace"}'}),
            call(8, "rapp_chat", {"user_input": "how are you?"}),
            call(9, "hello", {"name": "model"}),
        ])
        caps = (r.get(1) or {}).get("capabilities", {})
        if "resources" not in caps or "io.modelcontextprotocol/ui" not in caps.get("extensions", {}):
            fails.append(f"UI host: initialize must advertise resources + the UI extension, got {caps}")
        tools = {t["name"]: t for t in (r.get(2) or {}).get("tools", [])}
        if ((tools.get("hello") or {}).get("_meta") or {}).get("ui", {}).get("resourceUri") != uri:
            fails.append(f"UI host: hello must link {uri}, got {tools.get('hello')}")
        if ((tools.get("rapp_chat") or {}).get("_meta") or {}).get("ui", {}).get("visibility") != ["app"]:
            fails.append(f"UI host: rapp_chat must be app-only, got {tools.get('rapp_chat')}")
        res = (r.get(3) or {}).get("resources", [])
        if [(x["uri"], x["mimeType"]) for x in res] != [(uri, UI_MIME)]:
            fails.append(f"UI host: resources/list expected the hello UI, got {res}")
        contents = ((r.get(4) or {}).get("contents") or [{}])[0]
        html = contents.get("text", "")
        if contents.get("mimeType") != UI_MIME:
            fails.append(f"resources/read: wrong mimeType {contents.get('mimeType')!r}")
        shim, ui_script = html.find("rapp-mcp: rapp:* -> MCP Apps"), html.find("A rapplication UI")
        if not (html.lower().find("<head>") < shim < ui_script):
            fails.append("resources/read: the shim must sit first in <head>, before the UI's own script")
        if '"tool": "hello"' not in html or "__RAPP__" in html:
            fails.append("resources/read: shim config not filled in")
        if "code" not in (r.get(5) or {}):
            fails.append(f"resources/read of an unknown uri must be an error, got {r.get(5)}")
        for i, want in ((6, "Hello, Ada Lovelace!"), (7, "Hello, Grace!")):
            got = json.loads(text(r.get(i)) or "{}")
            if got.get("response") != want or got.get("agent_logs") != [want] or not got.get("session_id"):
                fails.append(f"rapp_chat direct call #{i}: expected {want!r} /chat-shaped, got {got}")
        if not (r.get(8) or {}).get("isError") or "No brainstem answered" not in text(r.get(8)):
            fails.append(f"rapp_chat free-form with no brainstem must fail plainly, got {r.get(8)}")
        if text(r.get(9)) != "Hello, model!":
            fails.append(f"the agent tool must still answer the model directly, got {r.get(9)}")

        # 3. Streamable HTTP: sessions, and loopback-only origins.
        port = free_port()
        proc = subprocess.Popen(server + ["--http", str(port)], stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{port}/mcp"
        try:
            def post(body, sid=None, origin=None):
                headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
                if sid:
                    headers["Mcp-Session-Id"] = sid
                if origin:
                    headers["Origin"] = origin
                req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = resp.read()
                        return resp.status, dict(resp.headers), json.loads(raw) if raw else None
                except urllib.error.HTTPError as e:
                    return e.code, dict(e.headers), None

            for _ in range(50):
                try:
                    socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                    break
                except OSError:
                    time.sleep(0.1)
            status, headers, body = post(handshake(True)[0], origin="http://localhost:8080")
            sid = headers.get("Mcp-Session-Id")
            if status != 200 or not sid or headers.get("Access-Control-Allow-Origin") != "http://localhost:8080":
                fails.append(f"HTTP initialize: expected 200 + session + CORS, got {status} {headers}")
            status, _, _ = post(handshake(True)[1], sid)
            if status != 202:
                fails.append(f"HTTP notification: expected 202, got {status}")
            status, _, body = post(lists[0], sid)
            names = {t["name"] for t in ((body or {}).get("result") or {}).get("tools", [])}
            if status != 200 or names != {"hello", "rapp_chat"}:
                fails.append(f"HTTP tools/list: expected hello + rapp_chat, got {status} {names}")
            if post(lists[0])[0] != 404:
                fails.append("HTTP: a request without a session must be refused (404)")
            if post(handshake(True)[0], origin="https://example.com")[0] != 403:
                fails.append("HTTP: a non-loopback browser origin must be refused (403)")
        finally:
            proc.terminate()

    # 4. The injected shim is valid JavaScript.
    node = shutil.which("node")
    if node:
        sys.path.insert(0, REPO)
        sys.argv = ["rapp_mcp.py", REPO]
        import rapp_mcp  # noqa: E402
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(rapp_mcp.SHIM_JS.replace("__RAPP__", "{}"))
        check = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        if check.returncode:
            fails.append(f"shim JS does not parse: {check.stderr.strip()}")

    if fails:
        print("FAILED:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("OK — MCP Apps: 2.0 surface kept for folders without UIs; a rapplication gets the linked ui:// resource with the "
          "shim first, app-only rapp_chat (direct calls + plain failure), and HTTP sessions with loopback-only origins.")


if __name__ == "__main__":
    main()
