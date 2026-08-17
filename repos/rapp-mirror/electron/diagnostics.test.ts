import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";

import {
  diagnosticsSnapshot,
  eventsSince,
  logPath,
  record,
  resetDiagnostics,
} from "./diagnostics.ts";

let dir = "";

beforeEach(() => {
  dir = mkdtempSync(path.join(os.tmpdir(), "mirror-diag-"));
  process.env.RAPP_MIRROR_LOGS = dir;
  resetDiagnostics();
});

afterEach(() => {
  delete process.env.RAPP_MIRROR_LOGS;
  resetDiagnostics();
});

test("record stamps a monotonic seq and an ISO timestamp", () => {
  const a = record({ component: "Forge", level: "info", message: "one" });
  const b = record({ component: "Forge", level: "info", message: "two" });
  assert.equal(a.seq + 1, b.seq);
  assert.ok(!Number.isNaN(Date.parse(a.at)));
});

test("events are appended to a durable JSONL file that survives a reset", () => {
  record({ component: "Deploy", level: "info", message: "wrote agent" });
  const file = logPath();
  assert.ok(existsSync(file), `expected a log at ${file}`);
  resetDiagnostics();
  const lines = readFileSync(file, "utf8").trim().split("\n");
  assert.equal(JSON.parse(lines[0]).message, "wrote agent");
});

test("eventsSince returns only newer events, so an agent can poll a cursor", () => {
  record({ component: "A", level: "info", message: "first" });
  const cursor = record({ component: "A", level: "info", message: "second" }).seq;
  record({ component: "A", level: "info", message: "third" });
  const fresh = eventsSince(cursor);
  assert.deepEqual(
    fresh.map((e) => e.message),
    ["third"],
  );
});

test("the brainstem secret is redacted before it ever reaches the ledger", () => {
  record({
    component: "Brainstem",
    level: "error",
    message: "failed with X-Brainstem-Secret: sk-supersecret-value",
    detail: { "x-brainstem-secret": "sk-supersecret-value", token: "sk-supersecret-value" },
  });
  const dump = readFileSync(logPath(), "utf8");
  assert.ok(!dump.includes("sk-supersecret-value"), "secret leaked into the ledger");
  assert.ok(dump.includes("[redacted]"));
});

test("snapshot separates recent errors from the general stream", () => {
  record({ component: "A", level: "info", message: "fine" });
  record({ component: "B", level: "error", message: "broke" });
  const snap = diagnosticsSnapshot();
  assert.equal(snap.errors.length, 1);
  assert.equal(snap.errors[0].message, "broke");
  assert.equal(snap.seq, 2);
  assert.equal(snap.logPath, logPath());
});

test("the in-memory ring is bounded so long sessions cannot grow without limit", () => {
  for (let i = 0; i < 1200; i++) record({ component: "Loop", level: "info", message: `n${i}` });
  const snap = diagnosticsSnapshot();
  assert.ok(snap.recent.length <= 500, `ring grew to ${snap.recent.length}`);
  assert.equal(snap.seq, 1200);
  assert.equal(snap.recent.at(-1)?.message, "n1199");
});

test("a corrupt or unwritable log directory never throws into the caller", () => {
  const blocked = path.join(dir, "blocked");
  writeFileSync(blocked, "i am a file, not a directory");
  process.env.RAPP_MIRROR_LOGS = blocked;
  resetDiagnostics();
  assert.doesNotThrow(() => record({ component: "A", level: "info", message: "still fine" }));
  assert.equal(diagnosticsSnapshot().recent.at(-1)?.message, "still fine");
});

test("an oversized log file is rotated rather than growing forever", () => {
  const big = "x".repeat(2000);
  for (let i = 0; i < 400; i++) record({ component: "Big", level: "info", message: big });
  const size = readFileSync(logPath(), "utf8").length;
  assert.ok(size < 1_000_000, `log grew to ${size} bytes without rotation`);
});
