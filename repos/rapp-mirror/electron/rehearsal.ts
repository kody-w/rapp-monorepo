import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import type {
  RehearsalDecision,
  RehearsalEvent,
  RehearsalRunState,
  RehearsalStepRecord,
  RehearsalTranscript,
  RehearsalVerdict,
  RehearsalWorld,
  WorldChange,
  WorldEntity,
} from "../common/ipc.ts";
import { chat, health } from "./brainstem.ts";
import { exportsRoot, extractJson, normalizeSpec, specHash, type ForgeSpec } from "./forge.ts";
import { createLogger } from "./logger.ts";

/**
 * The Rehearsal — the virtual twin. Before a forged automation touches the
 * real world, the brainstem plays the world: one SEED call invents the
 * smallest believable business context (from the spec ONLY — raw screen OCR
 * never enters the twin, a deliberate PII firewall), one strictly-contracted
 * call per step executes it against that world, and one VERDICT call judges
 * whether the final world satisfies the intent. The ENGINE applies every
 * data change itself — refusing unknown entities and stale `before` values —
 * so what the user confirms is concrete before→after data, never prose.
 *
 * A rehearsal is a SIMULATION and the transcript says so (`simulated: true`).
 * The human countersign ("fully done") is stamped against the spec's content
 * hash; deployAgent refuses any spec without a confirmed, hash-matching
 * rehearsal unless explicitly forced (recorded, never the default).
 */

const log = createLogger("Rehearsal");

const MAX_ENTITIES = 12;
const MAX_CHANGES_PER_STEP = 8;

/* ── storage ─────────────────────────────────────────────────────────── */

/** Gate authority dir: one <spec.name>.json per spec, newest run wins. */
export function rehearsalsDir(): string {
  return (
    process.env.MIRROR_REHEARSALS_DIR ||
    path.join(process.env.RAPP_MIRROR_HOME || path.join(os.homedir(), ".rapp-mirror"), "rehearsals")
  );
}

function recordPath(specName: string): string {
  return path.join(rehearsalsDir(), `${specName}.json`);
}

/** Corrupt-file-safe load of the latest rehearsal for a spec. */
export function loadRehearsal(specName: string): RehearsalTranscript | null {
  try {
    const file = recordPath(specName);
    if (!existsSync(file)) return null;
    const parsed = JSON.parse(readFileSync(file, "utf8")) as RehearsalTranscript;
    return parsed && parsed.version === "rehearsal/1" ? parsed : null;
  } catch {
    return null;
  }
}

/** Persist tmp+rename (the sessionstore idiom) and mirror a human-shippable
 *  copy (rehearsal.json + rehearsal.md) beside the other forge artifacts. */
export function saveRehearsal(t: RehearsalTranscript): string {
  const dir = rehearsalsDir();
  mkdirSync(dir, { recursive: true });
  const file = recordPath(t.specName);
  const tmp = file + ".tmp";
  writeFileSync(tmp, JSON.stringify(t, null, 2));
  renameSync(tmp, file);
  try {
    const exportDir = path.join(exportsRoot(), t.specName);
    if (existsSync(exportDir)) {
      writeFileSync(path.join(exportDir, "rehearsal.json"), JSON.stringify(t, null, 2));
      writeFileSync(path.join(exportDir, "rehearsal.md"), renderRehearsalMd(t));
    }
  } catch (err) {
    log.warn("export copy failed:", err instanceof Error ? err.message : String(err));
  }
  return file;
}

/* ── world normalization + the deterministic reducer ─────────────────── */

/** Envelope-clean: model text never carries |||VOICE|||/|||HOLO||| markers
 *  into transcripts or narration. */
export function cleanLine(raw: unknown, max = 300): string {
  return String(raw ?? "").split("|||")[0].replace(/\s+/g, " ").trim().slice(0, max);
}

/** Clamp whatever the model returned into a valid world (normalizeSpec idiom). */
export function normalizeWorld(raw: unknown): RehearsalWorld {
  const entities = (Array.isArray((raw as { entities?: unknown })?.entities)
    ? ((raw as { entities: unknown[] }).entities)
    : [])
    .map((e): WorldEntity => {
      const r = (e ?? {}) as Record<string, unknown>;
      return {
        id: cleanLine(r.id || r.name, 40).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, ""),
        kind: cleanLine(r.kind, 40) || "thing",
        name: cleanLine(r.name || r.id, 80) || "unnamed",
        state: cleanLine(r.state, 120),
        detail: cleanLine(r.detail, 240),
      };
    })
    .filter((e) => e.id)
    .slice(0, MAX_ENTITIES);
  const seen = new Set<string>();
  return { entities: entities.filter((e) => !seen.has(e.id) && seen.add(e.id)) };
}

/** Apply model-proposed changes to the world — the engine decides, not the
 *  model: unknown entity, unknown field, or a `before` that doesn't match
 *  the live value is refused and recorded. Returns a NEW world. */
export function applyChanges(
  world: RehearsalWorld,
  rawChanges: unknown,
): { world: RehearsalWorld; applied: WorldChange[]; invalid: string[] } {
  const next: RehearsalWorld = { entities: world.entities.map((e) => ({ ...e })) };
  const applied: WorldChange[] = [];
  const invalid: string[] = [];
  const fields = new Set(["state", "detail", "name"]);
  for (const raw of (Array.isArray(rawChanges) ? rawChanges : []).slice(0, MAX_CHANGES_PER_STEP)) {
    const c = (raw ?? {}) as Record<string, unknown>;
    const id = cleanLine(c.entity, 40).toLowerCase();
    const field = String(c.field ?? "");
    const entity = next.entities.find((e) => e.id === id || e.name.toLowerCase() === id);
    if (!entity) {
      invalid.push(`unknown entity "${id}"`);
      continue;
    }
    if (!fields.has(field)) {
      invalid.push(`unknown field "${field}" on "${id}"`);
      continue;
    }
    const key = field as "state" | "detail" | "name";
    const before = cleanLine(c.before, key === "detail" ? 240 : 120);
    const after = cleanLine(c.after, key === "detail" ? 240 : 120);
    if (entity[key] !== before) {
      invalid.push(`stale before on "${id}.${key}" (world says "${entity[key]}", model said "${before}")`);
      continue;
    }
    entity[key] = after;
    applied.push({ entity: entity.id, field: key, before, after });
  }
  return { world: next, applied, invalid };
}

/* ── the three prompt contracts ──────────────────────────────────────── */

const specJson = (spec: ForgeSpec) => JSON.stringify(spec, null, 1);

function seedPrompt(spec: ForgeSpec): string {
  return `You are the Virtual Twin inside RAPP Mirror, rehearsing an automation BEFORE it deploys.
From the spec below (and nothing else), invent the smallest believable business world this
automation would run in — the moment just BEFORE the job starts.

Respond with ONLY a JSON object, no prose, no code fences, shaped exactly:
{"scenario":"One vivid sentence setting the scene","world":{"entities":[{"id":"kebab-case","kind":"inbox|record|document|queue|system|person|other","name":"Short name","state":"current state, concrete","detail":"one concrete specific"}]},"sampleInputs":{"param_name":"plausible sample value"}}

Rules: 3-${MAX_ENTITIES} entities; make them concrete and countable ("7 receipts pending", not "some items");
sampleInputs has exactly one plausible value for each declared parameter.

## The spec
${specJson(spec)}`;
}

function stepPrompt(spec: ForgeSpec, world: RehearsalWorld, stepIndex: number, sampleInputs: Record<string, unknown>): string {
  const step = spec.steps[stepIndex];
  return `You are the Virtual Twin inside RAPP Mirror, mid-rehearsal. Apply ONLY this one step of the
automation to the frozen world below — do not perform any other step.

Respond with ONLY a JSON object, no prose, no code fences, shaped exactly:
{"action":"What the automation does, one sentence","observation":"What the world shows afterward, one concrete sentence","status":"ok","changes":[{"entity":"entity-id","field":"state","before":"EXACT current value","after":"new value"}]}

Rules: status is "ok", or "blocked" when the world makes this step impossible (then say why in a "note" field);
each change's "before" must copy the entity's CURRENT value verbatim from the world below;
fields limited to state|detail|name; 0-${MAX_CHANGES_PER_STEP} changes; only touch entities that exist.

## Overall intent
${spec.intent}

## Bound inputs
${JSON.stringify(sampleInputs)}

## Step ${stepIndex + 1} of ${spec.steps.length}: ${step.title}
${step.detail}

## The world right now
${JSON.stringify(world, null, 1)}`;
}

function verdictPrompt(spec: ForgeSpec, world: RehearsalWorld, steps: RehearsalStepRecord[]): string {
  return `You are the Virtual Twin inside RAPP Mirror, judging a finished rehearsal. Decide whether the
final world below shows the intent FULLY satisfied — the whole job done, not merely attempted.

Respond with ONLY a JSON object, no prose, no code fences, shaped exactly:
{"complete":true,"summary":"One honest sentence on what the automation accomplished","gaps":["anything the intent asked for that the final world does not show"]}

## The intent
${spec.intent}

## What each step reported
${steps.map((s) => `${s.index + 1}. ${s.title}: ${s.status}${s.note ? ` (${s.note})` : ""}`).join("\n")}

## The final world
${JSON.stringify(world, null, 1)}`;
}

/* ── strict-JSON brainstem calls (the distill idiom) ─────────────────── */

type StrictResult =
  | { ok: true; data: Record<string, unknown> }
  | { ok: false; transport: boolean; error: string };

async function strictJson(prompt: string, sessionId: string): Promise<StrictResult> {
  const first = await chat(prompt, [], sessionId);
  if (!first.ok || !first.response) {
    return { ok: false, transport: true, error: first.error || "the brainstem gave no answer" };
  }
  let json = extractJson(first.response);
  if (!json) {
    const retry = await chat(
      "Your previous reply was not a JSON object. Respond with ONLY the JSON object now — no prose, no code fences.",
      [
        { role: "user", content: prompt.slice(0, 4000) },
        { role: "assistant", content: first.response.slice(0, 2000) },
      ],
      sessionId,
    );
    if (retry.ok && retry.response) json = extractJson(retry.response);
  }
  if (!json) return { ok: false, transport: false, error: "the twin never produced valid JSON" };
  try {
    return { ok: true, data: JSON.parse(json) as Record<string, unknown> };
  } catch {
    return { ok: false, transport: false, error: "the twin's JSON did not parse" };
  }
}

/* ── the run ─────────────────────────────────────────────────────────── */

function normalizeSampleInputs(raw: unknown, spec: ForgeSpec): Record<string, string | number | boolean> {
  const out: Record<string, string | number | boolean> = {};
  const src = (raw ?? {}) as Record<string, unknown>;
  for (const p of spec.parameters) {
    const v = src[p.name];
    if (p.type === "boolean") out[p.name] = Boolean(v);
    else if (p.type === "integer" || p.type === "number") out[p.name] = Number(v) || 0;
    else out[p.name] = cleanLine(v, 120) || "example";
  }
  return out;
}

/** Run the whole rehearsal: seed → steps → verdict → awaiting-confirmation.
 *  Fail-closed: transport failure lands in `error`, twin noise in `stalled`,
 *  and neither can ever be confirmed. */
export async function rehearse(
  rawSpec: Record<string, unknown> | ForgeSpec,
  sessionId = "mirror",
  onEvent?: (ev: RehearsalEvent) => void,
): Promise<RehearsalTranscript> {
  const spec = normalizeSpec(rawSpec as Record<string, unknown>);
  const session = `${sessionId}-rehearsal`;
  const engineHealth = await health();
  const t: RehearsalTranscript = {
    version: "rehearsal/1",
    runId: `${spec.name}-${Date.now().toString(36)}`,
    specName: spec.name,
    specHash: specHash(spec),
    spec,
    simulated: true,
    engine: {
      model: engineHealth.model || "unknown",
      app: `rapp-mirror@${process.env.npm_package_version || "dev"}`,
    },
    startedAt: Date.now(),
    state: "seeding",
    scenario: "",
    sampleInputs: {},
    world0: { entities: [] },
    steps: [],
    finalWorld: null,
    verdict: null,
    decision: { status: "pending" },
  };
  const emit = (ev: RehearsalEvent) => onEvent?.(ev);
  const land = (state: RehearsalRunState, error?: string): RehearsalTranscript => {
    t.state = state;
    if (error) t.error = error;
    t.finishedAt = Date.now();
    saveRehearsal(t);
    emit({ kind: "state", state });
    return t;
  };
  emit({ kind: "state", state: "seeding" });

  const seed = await strictJson(seedPrompt(spec), session);
  if (!seed.ok) return land(seed.transport ? "error" : "stalled", `seeding: ${seed.error}`);
  t.scenario = cleanLine(seed.data.scenario, 200) || `A rehearsal of "${spec.title}".`;
  t.world0 = normalizeWorld(seed.data.world);
  if (!t.world0.entities.length) return land("stalled", "seeding: the twin invented an empty world");
  t.sampleInputs = normalizeSampleInputs(seed.data.sampleInputs, spec);
  emit({ kind: "seed", scenario: t.scenario, world: t.world0, sampleInputs: t.sampleInputs });

  t.state = "running";
  emit({ kind: "state", state: "running" });
  let world = t.world0;
  for (let i = 0; i < spec.steps.length; i++) {
    const res = await strictJson(stepPrompt(spec, world, i, t.sampleInputs), session);
    if (!res.ok) return land(res.transport ? "error" : "stalled", `step ${i + 1}: ${res.error}`);
    const { world: nextWorld, applied, invalid } = applyChanges(world, res.data.changes);
    world = nextWorld;
    const record: RehearsalStepRecord = {
      index: i,
      title: spec.steps[i].title,
      action: cleanLine(res.data.action, 240) || spec.steps[i].detail,
      observation: cleanLine(res.data.observation, 240),
      status: String(res.data.status) === "blocked" ? "blocked" : "ok",
      changes: applied,
    };
    const note = cleanLine(res.data.note, 200);
    if (note) record.note = note;
    if (invalid.length) record.invalid = invalid;
    t.steps.push(record);
    saveRehearsal(t);
    emit({ kind: "step", step: record });
    if (record.status === "blocked") break; // the twin says the job cannot proceed
  }
  t.finalWorld = world;

  t.state = "judging";
  emit({ kind: "state", state: "judging" });
  const judged = await strictJson(verdictPrompt(spec, world, t.steps), session);
  if (!judged.ok) return land(judged.transport ? "error" : "stalled", `judging: ${judged.error}`);
  const blocked = t.steps.some((s) => s.status === "blocked") || t.steps.length < spec.steps.length;
  t.verdict = {
    complete: Boolean(judged.data.complete) && !blocked,
    summary: cleanLine(judged.data.summary, 300) || "The rehearsal finished.",
    gaps: (Array.isArray(judged.data.gaps) ? judged.data.gaps : []).map((g) => cleanLine(g, 200)).filter(Boolean).slice(0, 8),
  };
  emit({ kind: "verdict", verdict: t.verdict });
  log.info("rehearsed", spec.name, t.verdict.complete ? "(complete)" : "(incomplete)", `${t.steps.length} steps`);
  return land("awaiting-confirmation");
}

/* ── the countersign + the gate ──────────────────────────────────────── */

/** Stamp the human verdict. Legal ONLY from awaiting-confirmation — an
 *  errored, stalled, or already-decided run can never be (re)confirmed. */
export function decideRehearsal(
  specName: string,
  verdict: "confirmed" | "rejected",
  note?: string,
  method?: string,
): { ok: boolean; transcript?: RehearsalTranscript; error?: string } {
  const t = loadRehearsal(specName);
  if (!t) return { ok: false, error: `no rehearsal on record for "${specName}" — rehearse first` };
  if (t.state !== "awaiting-confirmation") {
    return { ok: false, error: `rehearsal is "${t.state}" — only awaiting-confirmation can be decided` };
  }
  const decision: RehearsalDecision = { status: verdict, at: Date.now() };
  const n = cleanLine(note, 300);
  if (n) decision.note = n;
  if (method) decision.method = cleanLine(method, 20);
  t.decision = decision;
  t.state = verdict;
  saveRehearsal(t);
  log.info(verdict, specName, n ? `— ${n}` : "");
  return { ok: true, transcript: t };
}

export interface GateResult {
  allowed: boolean;
  forced?: boolean;
  reason?: string;
}

/** The deploy gate — consulted inside deployAgent() so the UI, the control
 *  plane, and mirrorctl are all covered by the same check. */
export function rehearsalGate(spec: ForgeSpec, force = false): GateResult {
  if (force) {
    log.warn("gate FORCED for", spec.name, "— deploying unrehearsed");
    return { allowed: true, forced: true };
  }
  const t = loadRehearsal(spec.name);
  if (!t) return { allowed: false, reason: `"${spec.name}" has never been rehearsed — rehearse it, confirm "fully done", then deploy (or force)` };
  if (t.state !== "confirmed" || t.decision.status !== "confirmed") {
    return { allowed: false, reason: `the rehearsal of "${spec.name}" is ${t.state}, not confirmed` };
  }
  if (t.specHash !== specHash(spec)) {
    return { allowed: false, reason: `"${spec.name}" changed since its confirmed rehearsal — rehearse the new version` };
  }
  return { allowed: true };
}

/* ── revision: a rejection feeds the objection back into the spec ────── */

/** Re-distill the spec with the human objection folded in; the revised spec
 *  starts unrehearsed (new hash) and must earn its own confirmation. */
export async function revise(
  rawSpec: Record<string, unknown> | ForgeSpec,
  objection: string,
  sessionId = "mirror",
): Promise<ForgeSpec> {
  const spec = normalizeSpec(rawSpec as Record<string, unknown>);
  const prompt = `You are the Forge inside RAPP Mirror. The automation spec below was REJECTED in rehearsal.
Revise it so the objection is addressed — keep everything that worked, change only what must change.

Respond with ONLY a JSON object, no prose, no code fences, in exactly the spec shape:
{"name":"...","title":"...","description":"...","intent":"...","steps":[{"title":"...","detail":"..."}],"parameters":[{"name":"...","description":"...","type":"string","required":true}]}

## The rejected spec
${specJson(spec)}

## The objection (from the person who watched the rehearsal)
${cleanLine(objection, 400) || "It did not complete the job."}`;
  const res = await strictJson(prompt, `${sessionId}-rehearsal-revise`);
  if (!res.ok) throw new Error(`revision failed — ${res.error}`);
  return normalizeSpec(res.data);
}

/* ── the human-readable transcript ───────────────────────────────────── */

export function renderRehearsalMd(t: RehearsalTranscript): string {
  const lines = [
    `# Rehearsal — ${t.specName}`,
    "",
    `> **VIRTUAL** — this is a simulated dry-run (${t.engine.model} via ${t.engine.app}), not an execution.`,
    "",
    `**Scenario:** ${t.scenario}`,
    "",
  ];
  if (Object.keys(t.sampleInputs).length) {
    lines.push("**Sample inputs:** " + Object.entries(t.sampleInputs).map(([k, v]) => `\`${k}\` = ${JSON.stringify(v)}`).join(", "), "");
  }
  lines.push("## The run", "");
  for (const s of t.steps) {
    lines.push(`${s.index + 1}. **${s.title}** — ${s.action} ${s.status === "blocked" ? "🚫 blocked" : "✓"}${s.note ? ` (${s.note})` : ""}`);
    for (const c of s.changes) lines.push(`   - ${c.entity}.${c.field}: "${c.before}" → "${c.after}"`);
    if (s.observation) lines.push(`   - _${s.observation}_`);
  }
  lines.push("", "## Verdict", "");
  if (t.verdict) {
    lines.push(t.verdict.complete ? `✅ **Complete** — ${t.verdict.summary}` : `⚠️ **Incomplete** — ${t.verdict.summary}`);
    for (const g of t.verdict.gaps) lines.push(`- gap: ${g}`);
  } else {
    lines.push(`(no verdict — run ${t.state}${t.error ? `: ${t.error}` : ""})`);
  }
  lines.push(
    "",
    `**Decision:** ${t.decision.status}${t.decision.note ? ` — ${t.decision.note}` : ""}${t.decision.method ? ` (by ${t.decision.method})` : ""}`,
    "",
    `<sub>spec ${t.specHash.slice(0, 12)} · run ${t.runId} · rehearsal/1</sub>`,
    "",
  );
  return lines.join("\n");
}
