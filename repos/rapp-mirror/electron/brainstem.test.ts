import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { brainstemSecret, chat, health, resetSecretCache } from "./brainstem.ts";

/** A fake brainstem that records the last request it saw. */
function fakeBrainstem(): Promise<{ server: http.Server; url: string; last: () => { path?: string; headers?: http.IncomingHttpHeaders; body?: string } }> {
  const seen: { path?: string; headers?: http.IncomingHttpHeaders; body?: string } = {};
  const server = http.createServer((req, res) => {
    seen.path = req.url;
    seen.headers = req.headers;
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      seen.body = body;
      res.setHeader("Content-Type", "application/json");
      if (req.url === "/health") {
        res.end(JSON.stringify({ status: "ok", version: "9.9.9", model: "test-model", agents: ["A"], quarantined: [] }));
      } else if (req.url === "/chat") {
        res.end(JSON.stringify({ response: "pong", agent_logs: "[A] ran", model: "test-model", session_id: "s" }));
      } else {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: "not found" }));
      }
    });
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({ server, url: `http://127.0.0.1:${(server.address() as { port: number }).port}`, last: () => seen }),
    ),
  );
}

test("health and chat speak the rapp envelope and send the secret header", async () => {
  const { server, url, last } = await fakeBrainstem();
  const secretDir = mkdtempSync(path.join(os.tmpdir(), "mirror-secret-"));
  const secretFile = path.join(secretDir, ".brainstem_secret");
  writeFileSync(secretFile, "s3cr3t-token\n");
  const prevUrl = process.env.RAPP_BRAINSTEM_URL;
  const prevSecret = process.env.BRAINSTEM_SECRET_FILE;
  process.env.RAPP_BRAINSTEM_URL = url;
  process.env.BRAINSTEM_SECRET_FILE = secretFile;
  resetSecretCache();
  try {
    assert.equal(brainstemSecret(), "s3cr3t-token");

    const h = await health();
    assert.equal(h.ok, true);
    assert.equal(h.version, "9.9.9");
    assert.equal(last().headers?.["x-brainstem-secret"], "s3cr3t-token");

    const c = await chat("ping", [{ role: "user", content: "hi" }], "sess-1");
    assert.equal(c.ok, true);
    assert.equal(c.response, "pong");
    assert.equal(c.agentLogs, "[A] ran");
    const sent = JSON.parse(last().body || "{}");
    assert.equal(sent.user_input, "ping");
    assert.equal(sent.session_id, "sess-1");
    assert.deepEqual(sent.conversation_history, [{ role: "user", content: "hi" }]);
  } finally {
    server.close();
    if (prevUrl === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prevUrl;
    if (prevSecret === undefined) delete process.env.BRAINSTEM_SECRET_FILE; else process.env.BRAINSTEM_SECRET_FILE = prevSecret;
    resetSecretCache();
  }
});

test("an unreachable brainstem reports ok:false, never throws", async () => {
  const prevUrl = process.env.RAPP_BRAINSTEM_URL;
  process.env.RAPP_BRAINSTEM_URL = "http://127.0.0.1:1"; // nothing listens here
  try {
    const h = await health();
    assert.equal(h.ok, false);
    assert.ok(h.error);
    const c = await chat("x", [], "s");
    assert.equal(c.ok, false);
  } finally {
    if (prevUrl === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prevUrl;
  }
});

test("device-code login start + poll speak the kernel's shapes", async () => {
  const server = http.createServer((req, res) => {
    res.setHeader("Content-Type", "application/json");
    if (req.url === "/login") res.end(JSON.stringify({ user_code: "ABCD-1234", verification_uri: "https://github.com/login/device" }));
    else if (req.url === "/login/poll") res.end(JSON.stringify({ status: "ok" }));
    else res.end(JSON.stringify({}));
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const prev = process.env.RAPP_BRAINSTEM_URL;
  process.env.RAPP_BRAINSTEM_URL = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
  try {
    const { loginStart, loginPoll } = await import("./brainstem.ts");
    const start = await loginStart();
    assert.equal(start.ok, true);
    assert.equal(start.userCode, "ABCD-1234");
    assert.match(start.url ?? "", /github\.com\/login\/device/);
    const poll = await loginPoll();
    assert.equal(poll.ok, true);
  } finally {
    server.close();
    if (prev === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prev;
  }
});
