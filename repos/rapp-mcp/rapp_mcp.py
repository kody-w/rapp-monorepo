#!/usr/bin/env python3
"""rapp-mcp — serve drop-in `*_agent.py` files as MCP tools, in any MCP host.

A single, dependency-free MCP (Model Context Protocol) server that exposes a folder of
`agent.py` files to ANY MCP client (Claude Desktop, GitHub Copilot CLI, Cursor, and
anything else that speaks MCP).

Point it at a folder of `*_agent.py` files. Each `*_agent.py` at the top of the folder
becomes an MCP tool; a file in any subfolder is parked and not served. Drop a new
`*_agent.py` at the top of the folder and it hotloads — agents are re-scanned on every
tools/list and tools/call, so there's nothing to restart. The bytes are the contract: the
same file behaves identically on every machine.

USAGE
    python3 rapp_mcp.py /path/to/agents              stdio (what MCP hosts launch)
    python3 rapp_mcp.py /path/to/agents --http 3001  Streamable HTTP on 127.0.0.1:3001/mcp

MCP APPS (rapplications). An agent with a UI beside it (`foo_agent.py` + `foo_agent.ui.html`)
is a rapplication. Its UI is served as a `ui://rapp-mcp/<name>` resource linked to the agent's
tool (MCP Apps, io.modelcontextprotocol/ui), so an MCP Apps host draws it in a sandboxed iframe;
other hosts ignore the link. A small shim injected into the page translates the rapplication's
own `rapp:*` messages (and its `fetch('/chat')`) into MCP Apps calls, so the UI runs unchanged.
A folder with no `*.ui.html` gets exactly the 2.0 surface.

MCP client config, e.g.:
    {
      "mcpServers": {
        "rapp-mcp": {
          "command": "python3",
          "args": ["/abs/path/rapp_mcp.py", "/abs/path/to/agents"]
        }
      }
    }

Agents are single-file `*_agent.py` defining a class that extends BasicAgent with
`self.name`, `self.metadata` (a JSON-Schema function definition), and `perform(**kwargs)`.
"""
import glob
import importlib.util
import json
import os
import re
import sys
import time
import traceback
import types
import urllib.error
import urllib.request
import uuid

SERVER_NAME = "rapp-mcp"
SERVER_VERSION = "2.1.0"  # tracks the stable rapp-mcp-spec/2.1
PROTOCOL = "2024-11-05"

UI_EXTENSION = "io.modelcontextprotocol/ui"
UI_MIME = "text/html;profile=mcp-app"
UI_SUFFIX = ".ui.html"
CHAT_TOOL = "rapp_chat"
BRAINSTEM_URL = os.environ.get("RAPP_BRAINSTEM_URL", "http://localhost:7071").rstrip("/")

_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
if "--http" in sys.argv:
    _i = sys.argv.index("--http")
    if len(sys.argv) > _i + 1 and sys.argv[_i + 1].isdigit() and sys.argv[_i + 1] in _ARGS:
        _ARGS.remove(sys.argv[_i + 1])
AGENTS_DIR = os.path.abspath(_ARGS[0]) if _ARGS else os.getcwd()
DATA_DIR = os.environ.get("RAPP_MCP_DATA", os.path.join(os.path.expanduser("~"), ".rapp_mcp_data"))


def log(msg):
    # MCP uses stdout for protocol; logs go to stderr.
    sys.stderr.write(f"[rapp-mcp] {msg}\n")
    sys.stderr.flush()


# ── Shims so brainstem agents load standalone (basic_agent + local storage) ───────
class BasicAgent:
    def __init__(self, name=None, metadata=None):
        if name and not getattr(self, "name", None):
            self.name = name
        if metadata and not getattr(self, "metadata", None):
            self.metadata = metadata

    def perform(self, **kwargs):
        raise NotImplementedError


class _LocalStorage:
    """Minimal stand-in for utils.azure_file_storage.AzureFileStorageManager."""
    def __init__(self, *a, **k):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._f = os.path.join(DATA_DIR, "store.json")

    def _read(self):
        try:
            return json.load(open(self._f))
        except Exception:
            return {}

    def read_json(self, *a, **k):
        return self._read()

    def write_json(self, data, *a, **k):
        json.dump(data, open(self._f, "w"))

    def __getattr__(self, _):  # tolerate other calls
        return lambda *a, **k: None


def _register_shims():
    if "agents" not in sys.modules:
        m = types.ModuleType("agents"); m.__path__ = [AGENTS_DIR]; sys.modules["agents"] = m
    ba = types.ModuleType("agents.basic_agent"); ba.BasicAgent = BasicAgent
    sys.modules["agents.basic_agent"] = ba
    sys.modules["agents"].basic_agent = ba
    baf = types.ModuleType("basic_agent"); baf.BasicAgent = BasicAgent
    sys.modules["basic_agent"] = baf
    if "utils" not in sys.modules:
        u = types.ModuleType("utils"); u.__path__ = []; sys.modules["utils"] = u
    afs = types.ModuleType("utils.azure_file_storage"); afs.AzureFileStorageManager = _LocalStorage
    sys.modules["utils.azure_file_storage"] = afs
    sys.modules["utils"].azure_file_storage = afs


# ── Loader (hotload: re-scanned each request) ─────────────────────────────────────
AGENT_FILES = {}  # agent name -> the *_agent.py it was loaded from, refreshed by load_agents()


def load_agents():
    global AGENT_FILES
    _register_shims()
    if AGENTS_DIR not in sys.path:
        sys.path.insert(0, AGENTS_DIR)
    agents, files = {}, {}
    # Only top-level *_agent.py files are live; every subfolder is organization (parked).
    for fp in sorted(glob.glob(os.path.join(AGENTS_DIR, "*_agent.py"))):
        base = os.path.basename(fp)
        if base == "basic_agent.py":
            continue
        try:
            modname = "agentpy_" + base[:-3] + "_" + str(abs(hash(fp)))
            spec = importlib.util.spec_from_file_location(modname, fp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for attr in dir(mod):
                cls = getattr(mod, attr)
                if (isinstance(cls, type) and hasattr(cls, "perform")
                        and attr not in ("BasicAgent", "object") and not attr.startswith("_")):
                    try:
                        inst = cls()
                        if getattr(inst, "name", None) and getattr(inst, "metadata", None):
                            agents[inst.name] = inst
                            files[inst.name] = fp
                    except Exception:
                        pass
        except Exception as e:
            log(f"failed to load {base}: {e}")
    AGENT_FILES = files  # one rebind, so a concurrent HTTP request never sees a half-built map
    return agents


# ── MCP Apps: a rapplication's UI as a ui:// resource ─────────────────────────────
def ui_file(name):
    fp = AGENT_FILES.get(name)
    if fp:
        ui = fp[:-3] + UI_SUFFIX
        if os.path.isfile(ui):
            return ui
    return None


def ui_uri(name):
    return f"ui://{SERVER_NAME}/{name}"


def tool_defs(agents):
    out = []
    for name, inst in agents.items():
        md = inst.metadata or {}
        tool = {
            "name": name,
            "description": md.get("description", name),
            "inputSchema": md.get("parameters", {"type": "object", "properties": {}}),
        }
        if ui_file(name):
            uri = ui_uri(name)
            tool["_meta"] = {"ui": {"resourceUri": uri}, "ui/resourceUri": uri}
        out.append(tool)
    if any(ui_file(n) for n in agents):
        out.append({
            "name": CHAT_TOOL,
            "description": ("For rapplication views only: one brainstem /chat turn. A direct call "
                            "('Use the <Agent> tool with k=v ...' or '<Agent> {json}') runs that agent "
                            "here; anything else goes to the local brainstem."),
            "inputSchema": {"type": "object", "properties": {
                "user_input": {"type": "string"}, "session_id": {"type": "string"}},
                "required": ["user_input"]},
            "_meta": {"ui": {"visibility": ["app"]}},
        })
    return out


def ui_resources(agents):
    out = []
    for name, inst in agents.items():
        if ui_file(name):
            out.append({"uri": ui_uri(name), "name": name, "mimeType": UI_MIME,
                        "description": (inst.metadata or {}).get("description", name)})
    return out


def read_ui(uri, agents):
    for name in agents:
        if ui_uri(name) == uri and ui_file(name):
            with open(ui_file(name), encoding="utf-8") as f:
                html = f.read()
            return {"uri": uri, "mimeType": UI_MIME, "text": inject_shim(html, name)}
    return None


def inject_shim(html, name):
    """Put the rapp:* -> MCP Apps shim first in <head>, so it runs before the UI's own scripts."""
    config = json.dumps({"tool": name, "chat_tool": CHAT_TOOL, "server": SERVER_NAME,
                         "version": SERVER_VERSION}).replace("</", "<\\/")
    tag = "<script>/* rapp-mcp: rapp:* -> MCP Apps */\n" + SHIM_JS.replace("__RAPP__", config) + "</script>"
    for pattern in (r"<head(\s[^>]*)?>", r"<html(\s[^>]*)?>"):
        m = re.search(pattern, html, re.I)
        if m:
            return html[:m.end()] + tag + html[m.end():]
    return tag + html


# The shim speaks MCP Apps (JSON-RPC over postMessage) to the host on the UI's behalf.
# The UI keeps talking to `parent` in rapp:* messages; the shim stands in for `parent`.
SHIM_JS = r"""(function () {
  "use strict";
  var RAPP = __RAPP__;
  var host = window.parent;
  if (!host || host === window) return;            // opened standalone: leave the UI alone
  var seq = 0, pending = {}, ready = false, queue = [], ctx = {};
  var session = "rapp-mcp-" + Math.random().toString(36).slice(2, 10);

  function send(m) { host.postMessage(m, "*"); }
  function rpc(method, params) {
    return new Promise(function (resolve, reject) {
      var id = "rapp-" + (++seq);
      pending[id] = { resolve: resolve, reject: reject };
      send({ jsonrpc: "2.0", id: id, method: method, params: params || {} });
    });
  }
  function notify(method, params) { send({ jsonrpc: "2.0", method: method, params: params || {} }); }
  function toUi(data) { window.dispatchEvent(new MessageEvent("message", { data: data, origin: location.origin })); }
  function text(result) {
    return ((result && result.content) || []).filter(function (c) { return c.type === "text"; })
      .map(function (c) { return c.text; }).join("\n");
  }
  function callTool(name, args) {
    return rpc("tools/call", { name: name, arguments: args || {} }).then(function (r) {
      if (r && r.isError) throw new Error(text(r) || (name + " failed"));
      return text(r);
    });
  }
  function chat(body) {
    return callTool(RAPP.chat_tool, { user_input: String(body.user_input || body.message || ""),
                                      session_id: body.session_id || session }).then(JSON.parse);
  }
  function cartridge() {
    return { type: "rapp:cartridge", schema: "rapp-cartridge/1.0",
             rapp: { id: RAPP.tool, name: RAPP.tool },
             context: { user: null, tether: { active: false, base: null },
                        session: { id: session, conversation_history: [] },
                        origin: { vbrainstem: null, host: "mcp-apps", server: RAPP.server },
                        host_context: ctx },
             capabilities: { can_invoke_agent: true, can_proxy_fetch: false, can_post_chat: true } };
  }

  function fromUi(m) {
    if (!m || typeof m !== "object") return;
    if (!ready) { queue.push(m); return; }
    var id = m.id;
    if (m.type === "rapp:hello") { toUi({ type: "rapp:ready" }); }
    else if (m.type === "rapp:get_cartridge") { toUi(cartridge()); }
    else if (m.type === "rapp:invoke") {
      callTool(m.tool || m.agent || RAPP.tool, m.args || {})
        .then(function (r) { toUi({ type: "rapp:invoke:result", id: id, result: r }); },
              function (e) { toUi({ type: "rapp:invoke:result", id: id, error: e.message }); });
    } else if (m.rapp === "invoke") {
      var args = Object.assign({}, m.args || {}); if (m.action) args.action = m.action;
      callTool(RAPP.tool, args)
        .then(function (r) { toUi({ rapp: "result", id: id, result: r }); },
              function (e) { toUi({ rapp: "result", id: id, result: JSON.stringify({ ok: false, error: e.message }) }); });
    } else if (m.type === "rapp:chat") {
      chat({ user_input: m.message })
        .then(function (d) { toUi({ type: "rapp:chat:result", id: id, reply: d.response }); },
              function (e) { toUi({ type: "rapp:chat:result", id: id, error: e.message }); });
    } else if (m.type === "rapp:fetch") {
      toUi({ type: "rapp:fetch:result", id: id, status: 0,
             error: "MCP Apps hosts do not proxy fetches; declare the domain in the view's CSP instead" });
    } else if (m.type === "rapp:bridge") {
      var done = function (status, body) { toUi({ type: "rapp:bridge:result", id: id, status: status, body: body }); };
      if (/\/chat\/?$/.test(m.path || "")) chat(m.body || {}).then(function (d) { done(200, d); }, function (e) { done(502, { error: e.message }); });
      else done(404, { error: (m.path || "") + " isn't available inside an MCP Apps host" });
    }
  }

  // The UI's stand-in parent. `parent` is a replaceable window attribute.
  try { window.parent = { postMessage: function (m) { fromUi(m); } }; } catch (e) {}

  // UIs that call the brainstem directly (fetch('/chat')) go through the same chat tool.
  var realFetch = window.fetch && window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || "";
    if (/^\/(chat|health)\/?(\?|$)/.test(url)) {
      var json = function (status, body) {
        return new Response(JSON.stringify(body), { status: status, headers: { "Content-Type": "application/json" } });
      };
      if (/^\/health/.test(url)) return Promise.resolve(json(200, { status: "ok", runtime: "mcp-apps", agents: [RAPP.tool] }));
      var body = {}; try { body = JSON.parse((init && init.body) || "{}"); } catch (e) {}
      var go = function () { return chat(body).then(function (d) { return json(200, d); },
                                                     function (e) { return json(502, { error: e.message }); }); };
      return ready ? go() : new Promise(function (r) { queue.push({ __fetch: function () { go().then(r); } }); });
    }
    return realFetch(input, init);
  };

  window.addEventListener("message", function (ev) {
    if (ev.source !== host) return;                  // only the real host speaks JSON-RPC to the shim
    var m = ev.data;
    if (!m || m.jsonrpc !== "2.0") return;
    if (m.id != null && pending[m.id] && !m.method) {
      var p = pending[m.id]; delete pending[m.id];
      m.error ? p.reject(new Error(m.error.message || "host error")) : p.resolve(m.result);
    } else if (m.method === "ui/notifications/tool-input") {
      toUi({ type: "rapp:tool-input", args: (m.params || {}).arguments || {} });
    } else if (m.method === "ui/notifications/tool-result") {
      toUi({ type: "rapp:tool-result", result: text(m.params), is_error: !!(m.params || {}).isError });
    } else if (m.method === "ui/notifications/host-context-changed") {
      Object.assign(ctx, m.params || {}); theme();
    } else if (m.method && m.id != null) {           // ping, ui/resource-teardown, ...
      send({ jsonrpc: "2.0", id: m.id, result: {} });
    }
  });

  function theme() { if (ctx.theme) document.documentElement.style.colorScheme = ctx.theme; }
  function size() {
    var d = document.documentElement;
    notify("ui/notifications/size-changed", { width: Math.ceil(d.scrollWidth), height: Math.ceil(d.scrollHeight) });
  }

  rpc("ui/initialize", { appInfo: { name: RAPP.tool, version: RAPP.version },
                         appCapabilities: { availableDisplayModes: ["inline", "fullscreen"] },
                         protocolVersion: "2026-01-26" })
    .then(function (r) {
      ctx = (r && r.hostContext) || {};
      notify("ui/notifications/initialized", {});
      ready = true; theme();
      toUi(cartridge());
      queue.splice(0).forEach(function (m) { m.__fetch ? m.__fetch() : fromUi(m); });
      if (window.ResizeObserver) new ResizeObserver(size).observe(document.documentElement);
      size();
    }, function () {});
})();
"""


# ── rapp_chat: the /chat a rapplication view expects, answered through MCP ────────
_CALL_WITH = re.compile(r"\buse\s+the\s+([A-Za-z_][\w-]*)\s+tool\s+with\b", re.I)
_KV = re.compile(r'\s*([A-Za-z_]\w*)=("(?:[^"\\]|\\.)*"|[^\s"]+)')


def _bare(v):
    v = v.rstrip(".,;")
    try:
        return json.loads(v)
    except ValueError:
        return v


def parse_direct_call(text, agents):
    """'Use the X tool with k=v k2="v 2"' or 'X {json}' naming a served agent -> (name, args)."""
    by_lower = {n.lower(): n for n in agents}
    m = _CALL_WITH.search(text)
    if m and m.group(1).lower() in by_lower:
        args, pos = {}, m.end()
        while True:
            kv = _KV.match(text, pos)
            if not kv:
                break
            raw = kv.group(2)
            args[kv.group(1)] = json.loads(raw) if raw.startswith('"') else _bare(raw)
            pos = kv.end()
        return by_lower[m.group(1).lower()], args
    m = re.match(r"\s*([A-Za-z_][\w-]*)\s+(\{.*\})\s*$", text, re.S)
    if m and m.group(1).lower() in by_lower:
        try:
            args = json.loads(m.group(2))
        except ValueError:
            return None
        if isinstance(args, dict):
            return by_lower[m.group(1).lower()], args
    return None


def rapp_chat(args, agents):
    user_input = str(args.get("user_input") or "")
    session_id = str(args.get("session_id") or f"rapp-mcp-{uuid.uuid4().hex[:12]}")
    direct = parse_direct_call(user_input, agents)
    if direct:
        name, call = direct
        out = agents[name].perform(**call)
        out = out if isinstance(out, str) else json.dumps(out)
        return {"response": out, "agent_logs": [out], "session_id": session_id}
    body = json.dumps({"user_input": user_input, "session_id": session_id}).encode()
    req = urllib.request.Request(f"{BRAINSTEM_URL}/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.loads(r.read())
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise RuntimeError(f"No brainstem answered at {BRAINSTEM_URL}/chat ({e}). Direct calls "
                           "('Use the <Agent> tool with k=v' or '<Agent> {json}') work without one.")
    return {"response": data.get("response", ""), "agent_logs": data.get("agent_logs") or [],
            "session_id": data.get("session_id") or session_id}


# ── MCP JSON-RPC (shared by stdio and HTTP) ───────────────────────────────────────
def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _text_result(mid, text, is_error=False):
    result = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def handle(req, session=None):
    session = {} if session is None else session
    mid = req.get("id")
    method = req.get("method")
    if method == "initialize":
        caps = {"tools": {"listChanged": True}}
        agents = load_agents()
        if any(ui_file(n) for n in agents):
            caps["resources"] = {}
            caps["extensions"] = {UI_EXTENSION: {"mimeTypes": [UI_MIME]}}
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL,
            "capabilities": caps,
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        agents = load_agents()
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tool_defs(agents)}}
    if method == "resources/list":
        agents = load_agents()
        return {"jsonrpc": "2.0", "id": mid,
                "result": {"resources": ui_resources(agents)}}
    if method == "resources/read":
        uri = (req.get("params") or {}).get("uri")
        content = read_ui(uri, load_agents())
        if not content:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32002, "message": f"Resource not found: {uri}"}}
        return {"jsonrpc": "2.0", "id": mid, "result": {"contents": [content]}}
    if method == "tools/call":
        params = req.get("params", {}) or {}
        name = params.get("name")
        args = params.get("arguments", {}) or {}
        agents = load_agents()
        if name == CHAT_TOOL and name not in agents and any(ui_file(n) for n in agents):
            try:
                return _text_result(mid, json.dumps(rapp_chat(args, agents)))
            except Exception as e:
                return _text_result(mid, str(e), True)
        inst = agents.get(name)
        if not inst:
            return _text_result(mid, f"Unknown agent tool '{name}'.", True)
        try:
            result = inst.perform(**args)
            text = result if isinstance(result, str) else json.dumps(result)
            return _text_result(mid, text)
        except Exception as e:
            tb = traceback.format_exc().splitlines()[-3:]
            return _text_result(mid, f"{name} error: {e}\n" + "\n".join(tb), True)
    if method and method.startswith("notifications/"):
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}


# ── Streamable HTTP (for hosts and test harnesses that connect by URL) ────────────
_LOOPBACK = re.compile(r"^(https?://)?(localhost|127\.0\.0\.1|\[::1\])(:\d+)?/?$")


def serve_http(port):
    """POST /mcp on 127.0.0.1 only. A browser origin must be loopback: agents run local code."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    sessions = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _origin_ok(self):
            origin = self.headers.get("Origin")
            host_ok = _LOOPBACK.match(self.headers.get("Host", ""))
            return bool(host_ok) and (origin is None or _LOOPBACK.match(origin))

        def _cors(self):
            origin = self.headers.get("Origin")
            if origin:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers",
                             "content-type, accept, mcp-session-id, mcp-protocol-version, last-event-id")
            self.send_header("Access-Control-Expose-Headers", "mcp-session-id")

        def _reply(self, status, body=None, sid=None):
            data = json.dumps(body).encode() if body is not None else b""
            self.send_response(status)
            self._cors()
            if sid:
                self.send_header("Mcp-Session-Id", sid)
            if body is not None:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self):
            self._reply(204 if self._origin_ok() else 403)

        def do_GET(self):
            self._reply(405 if self._origin_ok() else 403)

        def do_DELETE(self):
            sessions.pop(self.headers.get("Mcp-Session-Id"), None)
            self._reply(200 if self._origin_ok() else 403)

        def do_POST(self):
            if not self._origin_ok():
                return self._reply(403, {"error": "rapp-mcp accepts loopback origins only"})
            if self.path.split("?")[0].rstrip("/") != "/mcp":
                return self._reply(404, {"error": "POST /mcp"})
            try:
                msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"null")
            except ValueError:
                return self._reply(400, {"jsonrpc": "2.0", "id": None,
                                         "error": {"code": -32700, "message": "Parse error"}})
            batch = msg if isinstance(msg, list) else [msg]
            sid = self.headers.get("Mcp-Session-Id")
            if any(isinstance(r, dict) and r.get("method") == "initialize" for r in batch):
                sid = uuid.uuid4().hex
                sessions[sid] = {}
            session = sessions.get(sid)
            if session is None:
                return self._reply(404, {"jsonrpc": "2.0", "id": None,
                                         "error": {"code": -32001, "message": "Unknown or missing Mcp-Session-Id"}})
            out = [r for r in (handle(req, session) for req in batch if isinstance(req, dict)) if r is not None]
            if not out:
                return self._reply(202, None, sid)
            self._reply(200, out if isinstance(msg, list) else out[0], sid)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    log(f"serving *_agent.py from {AGENTS_DIR} at http://127.0.0.1:{port}/mcp")
    server.serve_forever()


def main():
    if "--http" in sys.argv:
        i = sys.argv.index("--http")
        port = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 3001
        return serve_http(port)
    log(f"serving *_agent.py from {AGENTS_DIR}")
    session = {}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        resp = handle(req, session)
        if resp is not None:
            send(resp)


if __name__ == "__main__":
    main()
