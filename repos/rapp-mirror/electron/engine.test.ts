import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { ensureEngine } from "./engine.ts";

/** A fake brainstem whose /health flips per `ok()`. */
function fakeBrainstem(ok: () => boolean): Promise<{ url: string; close: () => Promise<void> }> {
  const server = http.createServer((_req, res) => {
    res.setHeader("Content-Type", "application/json");
    if (ok()) {
      res.end(JSON.stringify({ status: "ok", version: "9.9.9", model: "test-model", agents: [] }));
    } else {
      res.statusCode = 503;
      res.end(JSON.stringify({ error: "down" }));
    }
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({
        url: `http://127.0.0.1:${(server.address() as { port: number }).port}`,
        close: () => new Promise((r) => server.close(() => r())),
      }),
    ),
  );
}

/** A fake installer endpoint serving a bash script, counting fetches. */
function fakeInstaller(script: string): Promise<{ url: string; hits: () => number; close: () => Promise<void> }> {
  let hits = 0;
  const server = http.createServer((_req, res) => {
    hits++;
    res.setHeader("Content-Type", "text/plain");
    res.end(script);
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({
        url: `http://127.0.0.1:${(server.address() as { port: number }).port}`,
        hits: () => hits,
        close: () => new Promise((r) => server.close(() => r())),
      }),
    ),
  );
}

function withEnv(brainstemUrl: string, installerUrl: string) {
  const prev = { b: process.env.RAPP_BRAINSTEM_URL, i: process.env.RAPP_INSTALLER_URL };
  process.env.RAPP_BRAINSTEM_URL = brainstemUrl;
  process.env.RAPP_INSTALLER_URL = installerUrl;
  return () => {
    if (prev.b === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prev.b;
    if (prev.i === undefined) delete process.env.RAPP_INSTALLER_URL; else process.env.RAPP_INSTALLER_URL = prev.i;
  };
}

test("healthy brainstem: action none, installer never fetched", async () => {
  const brain = await fakeBrainstem(() => true);
  const installer = await fakeInstaller("echo should-never-run");
  const restore = withEnv(brain.url, installer.url);
  try {
    const s = await ensureEngine();
    assert.equal(s.action, "none");
    assert.equal(s.running, true);
    assert.equal(installer.hits(), 0);
  } finally {
    restore();
    await brain.close();
    await installer.close();
  }
});

test("tombstoned installer: unavailable, script never executed", async () => {
  const dir = mkdtempSync(path.join(os.tmpdir(), "engine-test-"));
  const marker = path.join(dir, "executed");
  const brain = await fakeBrainstem(() => false);
  const installer = await fakeInstaller(
    `#!/usr/bin/env bash\necho "installer/install.sh: 410 Gone" >&2\ntouch "${marker}"\nexit 78\n`,
  );
  const restore = withEnv(brain.url, installer.url);
  try {
    const s = await ensureEngine();
    assert.equal(s.action, "unavailable");
    assert.match(s.error ?? "", /410 Gone/);
    assert.equal(existsSync(marker), false, "tombstone script must never be executed");
  } finally {
    restore();
    await brain.close();
    await installer.close();
  }
});

test("unreachable installer URL: unavailable with the network reason", async () => {
  const brain = await fakeBrainstem(() => false);
  const restore = withEnv(brain.url, "http://127.0.0.1:1/install.sh");
  try {
    const s = await ensureEngine();
    assert.equal(s.action, "unavailable");
    assert.ok(s.error, "carries the fetch error");
  } finally {
    restore();
    await brain.close();
  }
});

test("installer exits nonzero: fails fast with the captured output, no 30s poll", async () => {
  const brain = await fakeBrainstem(() => false);
  const installer = await fakeInstaller(`echo boom-detail >&2\nexit 7\n`);
  const restore = withEnv(brain.url, installer.url);
  try {
    const t0 = Date.now();
    const s = await ensureEngine();
    const elapsed = Date.now() - t0;
    assert.equal(s.action, "failed");
    assert.match(s.error ?? "", /boom-detail/);
    assert.match(s.error ?? "", /exited with code 7\b/i);
    assert.ok(elapsed < 8000, `resolved in ${elapsed}ms — must not fall into the blind health poll`);
  } finally {
    restore();
    await brain.close();
    await installer.close();
  }
});

test("concurrent calls share one install; success reports installed; later call is a no-op", async () => {
  const dir = mkdtempSync(path.join(os.tmpdir(), "engine-test-"));
  const counter = path.join(dir, "runs");
  // Health turns ok as soon as the installer has run once.
  const brain = await fakeBrainstem(() => existsSync(counter));
  const installer = await fakeInstaller(`echo ran >> "${counter}"\n`);
  const restore = withEnv(brain.url, installer.url);
  try {
    const [a, b] = await Promise.all([ensureEngine(), ensureEngine()]);
    assert.equal(a.action, "installed");
    assert.equal(b.action, "installed");
    const runs = readFileSync(counter, "utf8").trim().split("\n").length;
    assert.equal(runs, 1, "exactly ONE installer must run for concurrent ensureEngine calls");
    const again = await ensureEngine();
    assert.equal(again.action, "none", "in-flight guard clears on settle; healthy engine is a no-op");
  } finally {
    restore();
    await brain.close();
    await installer.close();
  }
});
