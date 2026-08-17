import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import type { RehearsalEvent, RehearsalTranscript } from "../common/ipc.ts";
import { resetSecretCache } from "./brainstem.ts";
import { deployAgent, normalizeSpec, specHash, type ForgeSpec } from "./forge.ts";
import { trustedLocalRequest } from "./guard.ts";
import {
  applyChanges,
  cleanLine,
  decideRehearsal,
  loadRehearsal,
  normalizeWorld,
  rehearsalGate,
  rehearse,
  renderRehearsalMd,
  revise,
  saveRehearsal,
} from "./rehearsal.ts";

const SPEC: ForgeSpec = normalizeSpec({
  name: "submit-weekly-expenses",
  title: "Submit weekly expenses",
  description: "Files the week's expense report from receipts.",
  intent: "Submit every pending expense receipt as one weekly report.",
  steps: [
    { title: "Collect receipts", detail: "Gather all receipts for the week." },
    { title: "File report", detail: "Create and submit the expense report." },
  ],
  parameters: [{ name: "week", description: "ISO week to file", type: "string", required: true }],
});

const SEED_REPLY = JSON.stringify({
  scenario: "It's Friday afternoon and seven receipts sit unfiled in the expenses inbox.",
  world: {
    entities: [
      { id: "inbox", kind: "inbox", name: "Expenses inbox", state: "7 receipts pending", detail: "receipts from the week" },
      { id: "report", kind: "record", name: "Weekly report", state: "not created", detail: "the report to submit" },
    ],
  },
  sampleInputs: { week: "2026-W32" },
});

const STEP1_REPLY = JSON.stringify({
  action: "The automation gathers all seven receipts from the inbox.",
  observation: "The inbox shows zero pending receipts; seven are staged for the report.",
  status: "ok",
  changes: [{ entity: "inbox", field: "state", before: "7 receipts pending", after: "0 pending, 7 staged" }],
});

const STEP2_REPLY = JSON.stringify({
  action: "The automation creates the weekly report and submits it.",
  observation: "The weekly report exists and shows submitted.",
  status: "ok",
  changes: [{ entity: "report", field: "state", before: "not created", after: "submitted with 7 receipts" }],
});

const VERDICT_REPLY = JSON.stringify({
  complete: true,
  summary: "All seven receipts were submitted as one weekly report.",
  gaps: [],
});

/** A scripted brainstem: /health + a queue of /chat replies (repeats last). */
function fakeBrainstem(replies: string[]): Promise<{
  server: http.Server;
  url: string;
  requests: string[];
}> {
  const requests: string[] = [];
  let i = 0;
  const server = http.createServer((req, res) => {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      res.setHeader("Content-Type", "application/json");
      if (req.url?.startsWith("/health")) {
        res.end(JSON.stringify({ status: "ok", model: "fake-model", agents: [SPEC.className], quarantined: [] }));
        return;
      }
      requests.push(body);
      const reply = replies[Math.min(i++, replies.length - 1)];
      res.end(JSON.stringify({ response: reply }));
    });
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({ server, url: `http://127.0.0.1:${(server.address() as { port: number }).port}`, requests }),
    ),
  );
}

/** Isolated env: scripted brainstem + temp rehearsals/exports/agents dirs. */
async function withTwinEnv<T>(
  replies: string[],
  body: (ctx: { requests: string[]; rehearsalsDir: string; agentsDir: string }) => Promise<T>,
): Promise<T> {
  const { server, url, requests } = await fakeBrainstem(replies);
  const rehearsalsDir = mkdtempSync(path.join(os.tmpdir(), "rehearsals-"));
  const exportsDir = mkdtempSync(path.join(os.tmpdir(), "rehearsal-exports-"));
  const agentsDir = mkdtempSync(path.join(os.tmpdir(), "rehearsal-agents-"));
  const secretFile = path.join(agentsDir, ".brainstem_secret");
  writeFileSync(secretFile, "test-secret\n");
  const prev: Record<string, string | undefined> = {
    RAPP_BRAINSTEM_URL: process.env.RAPP_BRAINSTEM_URL,
    MIRROR_REHEARSALS_DIR: process.env.MIRROR_REHEARSALS_DIR,
    RAPP_MIRROR_EXPORTS: process.env.RAPP_MIRROR_EXPORTS,
    RAPP_BRAINSTEM_AGENTS: process.env.RAPP_BRAINSTEM_AGENTS,
    BRAINSTEM_SECRET_FILE: process.env.BRAINSTEM_SECRET_FILE,
  };
  process.env.RAPP_BRAINSTEM_URL = url;
  process.env.MIRROR_REHEARSALS_DIR = rehearsalsDir;
  process.env.RAPP_MIRROR_EXPORTS = exportsDir;
  process.env.RAPP_BRAINSTEM_AGENTS = agentsDir;
  process.env.BRAINSTEM_SECRET_FILE = secretFile;
  resetSecretCache();
  try {
    return await body({ requests, rehearsalsDir, agentsDir });
  } finally {
    server.close();
    for (const [k, v] of Object.entries(prev)) {
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
    resetSecretCache();
  }
}

/* ── cleanLine (envelope hygiene) ────────────────────────────────────── */

test("cleanLine strips envelope markers, whitespace runs, and clamps", () => {
  assert.equal(cleanLine("done |||VOICE||| spoken line"), "done");
  assert.equal(cleanLine("  a \n  b  "), "a b");
  assert.equal(cleanLine(null), "");
  assert.ok(cleanLine("x".repeat(999), 50).length <= 50);
});

/* ── normalizeWorld ──────────────────────────────────────────────────── */

test("normalizeWorld clamps, kebab-cases ids, dedupes, and drops idless", () => {
  const w = normalizeWorld({
    entities: [
      { id: "The Inbox!", kind: "inbox", name: "Inbox", state: "full", detail: "d" },
      { id: "the-inbox", kind: "inbox", name: "Dup", state: "x", detail: "d" },
      { name: "", kind: "ghost" },
      ...Array.from({ length: 20 }, (_, i) => ({ id: `e${i}`, kind: "k", name: `E${i}`, state: "s", detail: "d" })),
    ],
  });
  assert.equal(w.entities[0].id, "the-inbox");
  assert.equal(w.entities.filter((e) => e.id === "the-inbox").length, 1);
  assert.ok(w.entities.length <= 12);
});

test("normalizeWorld survives garbage", () => {
  assert.deepEqual(normalizeWorld(null), { entities: [] });
  assert.deepEqual(normalizeWorld({ entities: "nope" }), { entities: [] });
});

/* ── applyChanges: the engine decides, not the model ─────────────────── */

const WORLD = normalizeWorld(JSON.parse(SEED_REPLY).world);

test("applyChanges applies a matching change and returns a NEW world", () => {
  const { world, applied, invalid } = applyChanges(WORLD, [
    { entity: "inbox", field: "state", before: "7 receipts pending", after: "0 pending" },
  ]);
  assert.equal(applied.length, 1);
  assert.equal(invalid.length, 0);
  assert.equal(world.entities[0].state, "0 pending");
  assert.equal(WORLD.entities[0].state, "7 receipts pending"); // original untouched
});

test("applyChanges refuses unknown entities, unknown fields, stale before", () => {
  const { applied, invalid } = applyChanges(WORLD, [
    { entity: "ghost", field: "state", before: "x", after: "y" },
    { entity: "inbox", field: "owner", before: "x", after: "y" },
    { entity: "inbox", field: "state", before: "WRONG value", after: "y" },
  ]);
  assert.equal(applied.length, 0);
  assert.equal(invalid.length, 3);
  assert.match(invalid[0], /unknown entity/);
  assert.match(invalid[1], /unknown field/);
  assert.match(invalid[2], /stale before/);
});

/* ── the full run ────────────────────────────────────────────────────── */

test("rehearse: seed -> N steps -> verdict -> awaiting-confirmation, persisted", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async ({ rehearsalsDir }) => {
    const events: RehearsalEvent[] = [];
    const t = await rehearse(SPEC, "test", (ev) => events.push(ev));
    assert.equal(t.state, "awaiting-confirmation");
    assert.equal(t.simulated, true);
    assert.equal(t.version, "rehearsal/1");
    assert.equal(t.specHash, specHash(SPEC));
    assert.equal(t.engine.model, "fake-model");
    assert.equal(t.steps.length, SPEC.steps.length);
    assert.deepEqual(t.steps.map((s) => s.index), [0, 1]);
    for (const s of t.steps) {
      assert.ok(s.action, "step has an action");
      assert.ok(s.observation, "step has an observation");
    }
    assert.equal(t.steps[1].changes[0].after, "submitted with 7 receipts");
    assert.equal(t.verdict?.complete, true);
    assert.equal(t.sampleInputs.week, "2026-W32");
    // persisted where the gate reads it
    assert.ok(existsSync(path.join(rehearsalsDir, `${SPEC.name}.json`)));
    const loaded = loadRehearsal(SPEC.name);
    assert.equal(loaded?.runId, t.runId);
    // events streamed in order: states + seed + steps + verdict
    assert.ok(events.some((e) => e.kind === "seed"));
    assert.equal(events.filter((e) => e.kind === "step").length, 2);
    assert.ok(events.some((e) => e.kind === "verdict"));
  });
});

test("rehearse: twin noise (no JSON after retry) stalls the run — never crashes", async () => {
  await withTwinEnv(["I would love to help you with that!"], async () => {
    const t = await rehearse(SPEC, "test");
    assert.equal(t.state, "stalled");
    assert.match(t.error!, /seeding/);
    assert.equal(rehearsalGate(SPEC).allowed, false);
  });
});

test("rehearse: brainstem down lands in error, fail-closed", async () => {
  const rehearsalsDir = mkdtempSync(path.join(os.tmpdir(), "rehearsals-"));
  const prevUrl = process.env.RAPP_BRAINSTEM_URL;
  const prevDir = process.env.MIRROR_REHEARSALS_DIR;
  process.env.RAPP_BRAINSTEM_URL = "http://127.0.0.1:1"; // nothing listens
  process.env.MIRROR_REHEARSALS_DIR = rehearsalsDir;
  try {
    const t = await rehearse(SPEC, "test");
    assert.equal(t.state, "error");
    assert.equal(decideRehearsal(SPEC.name, "confirmed").ok, false);
  } finally {
    if (prevUrl === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prevUrl;
    if (prevDir === undefined) delete process.env.MIRROR_REHEARSALS_DIR; else process.env.MIRROR_REHEARSALS_DIR = prevDir;
  }
});

test("rehearse: a blocked step short-circuits and the verdict cannot be complete", async () => {
  const blocked = JSON.stringify({
    action: "The automation tries to gather receipts.",
    observation: "The inbox is locked by another process.",
    status: "blocked",
    note: "inbox locked",
    changes: [],
  });
  await withTwinEnv([SEED_REPLY, blocked, VERDICT_REPLY], async () => {
    const t = await rehearse(SPEC, "test");
    assert.equal(t.state, "awaiting-confirmation");
    assert.equal(t.steps.length, 1); // second step never ran
    assert.equal(t.steps[0].status, "blocked");
    assert.equal(t.verdict?.complete, false); // model said true; the engine overrules
  });
});

/* ── the countersign ─────────────────────────────────────────────────── */

test("decideRehearsal: legal only from awaiting-confirmation, then immutable", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async () => {
    assert.equal(decideRehearsal("never-rehearsed", "confirmed").ok, false);
    await rehearse(SPEC, "test");
    const confirmed = decideRehearsal(SPEC.name, "confirmed", undefined, "test");
    assert.equal(confirmed.ok, true);
    assert.equal(confirmed.transcript?.state, "confirmed");
    // a decided run can never be re-decided
    assert.equal(decideRehearsal(SPEC.name, "rejected").ok, false);
  });
});

/* ── the gate + deployAgent (the choke point) ────────────────────────── */

test("deployAgent refuses an unrehearsed spec by default", async () => {
  await withTwinEnv([SEED_REPLY], async () => {
    const res = await deployAgent(SPEC);
    assert.equal(res.ok, false);
    assert.equal(res.needsRehearsal, true);
    assert.match(res.error!, /never been rehearsed/);
  });
});

test("deployAgent deploys after a confirmed rehearsal; force is recorded", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async ({ agentsDir }) => {
    await rehearse(SPEC, "test");
    assert.equal((await deployAgent(SPEC)).needsRehearsal, true); // pending ≠ confirmed
    decideRehearsal(SPEC.name, "confirmed");
    const res = await deployAgent(SPEC);
    assert.equal(res.ok, true);
    assert.equal(res.forced, undefined);
    assert.ok(existsSync(path.join(agentsDir, "submit_weekly_expenses_agent.py")));
    // force bypasses the gate and says so
    const forced = await deployAgent(SPEC, { force: true });
    assert.equal(forced.forced, true);
  });
});

test("a confirmation earned on one spec cannot be spent on a mutated one", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async () => {
    await rehearse(SPEC, "test");
    decideRehearsal(SPEC.name, "confirmed");
    const mutated: ForgeSpec = {
      ...SPEC,
      steps: [...SPEC.steps, { title: "Wire funds", detail: "Transfer the balance elsewhere." }],
    };
    assert.notEqual(specHash(mutated), specHash(SPEC));
    const res = await deployAgent(mutated);
    assert.equal(res.ok, false);
    assert.match(res.error!, /changed since/);
  });
});

test("a rejected rehearsal keeps the gate closed", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async () => {
    await rehearse(SPEC, "test");
    decideRehearsal(SPEC.name, "rejected", "wrong report format");
    const res = await deployAgent(SPEC);
    assert.equal(res.ok, false);
    assert.match(res.error!, /rejected/);
  });
});

/* ── persistence round-trip ──────────────────────────────────────────── */

test("saveRehearsal round-trips, exports beside the artifacts, corrupt load is null", async () => {
  await withTwinEnv([SEED_REPLY, STEP1_REPLY, STEP2_REPLY, VERDICT_REPLY], async ({ rehearsalsDir }) => {
    const t = await rehearse(SPEC, "test");
    // export copies land beside the forge artifacts once the export dir exists
    const exportDir = path.join(process.env.RAPP_MIRROR_EXPORTS!, SPEC.name);
    mkdirSync(exportDir, { recursive: true });
    saveRehearsal(t);
    assert.ok(existsSync(path.join(exportDir, "rehearsal.json")));
    const md = readFileSync(path.join(exportDir, "rehearsal.md"), "utf8");
    assert.match(md, /VIRTUAL/);
    assert.match(md, /simulated dry-run/);
    // corrupt registry file -> null, never a crash
    writeFileSync(path.join(rehearsalsDir, `${SPEC.name}.json`), "{not json");
    assert.equal(loadRehearsal(SPEC.name), null);
  });
});

test("renderRehearsalMd narration carries no envelope markers", async () => {
  const noisy = JSON.stringify({
    action: "Files the report |||VOICE||| I filed it!",
    observation: "Done |||OPTIONS||| a | b",
    status: "ok",
    changes: [],
  });
  await withTwinEnv([SEED_REPLY, noisy, noisy, VERDICT_REPLY], async () => {
    const t = await rehearse(SPEC, "test");
    const md = renderRehearsalMd(t);
    assert.ok(!md.includes("|||"), "no ||| markers in the human transcript");
    for (const s of t.steps) {
      assert.ok(!s.action.includes("|||"));
      assert.ok(!s.observation.includes("|||"));
    }
  });
});

/* ── revision: the objection feeds back ──────────────────────────────── */

test("revise folds the objection into a re-distilled spec", async () => {
  const revised = JSON.stringify({
    name: "submit-weekly-expenses",
    title: "Submit weekly expenses with receipts attached",
    description: "Files the weekly report with every receipt attached.",
    intent: "Submit every receipt as one weekly report with attachments.",
    steps: [
      { title: "Collect receipts", detail: "Gather all receipts." },
      { title: "Attach and file", detail: "Attach each receipt and submit the report." },
    ],
    parameters: [],
  });
  await withTwinEnv([revised], async ({ requests }) => {
    const spec = await revise(SPEC, "the receipts were never attached", "test");
    assert.equal(spec.steps[1].title, "Attach and file");
    assert.match(requests[0], /never attached/); // the objection reached the prompt
    assert.match(requests[0], /REJECTED in rehearsal/);
  });
});

/* ── specHash ────────────────────────────────────────────────────────── */

test("specHash is deterministic and changes on any behavioral edit", () => {
  assert.equal(specHash(SPEC), specHash(normalizeSpec(JSON.parse(JSON.stringify(SPEC)))));
  assert.notEqual(specHash(SPEC), specHash({ ...SPEC, intent: "different" }));
  assert.notEqual(
    specHash(SPEC),
    specHash({ ...SPEC, steps: [{ title: "Collect receipts", detail: "changed" }, SPEC.steps[1]] }),
  );
});

/* ── the control-plane door ──────────────────────────────────────────── */

test("trustedLocalRequest shuts the drive-by door, admits real local JSON clients", () => {
  const ok = { headers: { host: "127.0.0.1:8474", "content-type": "application/json" } };
  assert.equal(trustedLocalRequest(ok), true);
  assert.equal(trustedLocalRequest({ headers: { ...ok.headers, origin: "https://evil.example" } }), false);
  assert.equal(trustedLocalRequest({ headers: { host: "evil.example:8474", "content-type": "application/json" } }), false);
  assert.equal(trustedLocalRequest({ headers: { host: "127.0.0.1:8474", "content-type": "text/plain" } }), false);
  assert.equal(trustedLocalRequest({ headers: { host: "localhost:8474", "content-type": "application/json; charset=utf-8" } }), true);
});
