#!/usr/bin/env node
// Verify the live rapp/1 biography, its static pointers, and the sealed legacy audit chain.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  H, SPEC, canonical, parseJsonExact, verifyFrame,
} from "./_rapp1.mjs";
import {
  FRAMES_DIR, RAPPID_PATH, REPO_ROOT, frameFileName, listFrameFiles, sha8,
} from "./_frame.mjs";

const HEX64 = /^[0-9a-f]{64}$/;
const UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
const LEGACY_UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;
const RAPPID = /^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)\/([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$/;
const INDEX_KEYS = new Set(["spec", "stream_id", "generated", "count", "head", "frames"]);
const POINTER_KEYS = new Set(["seq", "payload_hash", "frame_hash", "utc", "kind"]);
const INDEX_FRAME_KEYS = new Set([
  "seq", "path", "utc", "kind", "payload_hash", "frame_hash", "prev", "prev_wave",
]);
const VITALS_KEYS = new Set(["spec", "stream_id", "updated", "head", "health"]);
const LEGACY_FRAME_KEYS = new Set([
  "spec", "kind", "seq", "ts", "twin_id", "kernel_version",
  "payload", "sha256", "parent_sha", "sig",
]);
const LEGACY_KINDS = new Set(["body.pulse", "body.pulse.reconstructed"]);
const SEAL_KEYS = new Set([
  "spec", "note", "sealed_head_seq", "seal", "seal_space", "superseded_by",
]);

const problems = [];
const liveHistory = [];
const liveFrames = new Map();

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  if (!isObject(value)) return false;
  const keys = Object.keys(value);
  return keys.length === expected.size && keys.every((key) => expected.has(key));
}

function addProblem(section, file, msg) {
  problems.push({ section, file, msg });
}

function readExact(filePath) {
  return parseJsonExact(fs.readFileSync(filePath, "utf8"));
}

function numericJsonFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory)
    .filter((name) => /^\d+\.json$/.test(name))
    .sort((a, b) => Number.parseInt(a, 10) - Number.parseInt(b, 10));
}

function doctrineErrors(frame, reconstructedKind) {
  const errors = [];
  const mode = frame.payload?.provenance?.mode;
  if (frame.kind === reconstructedKind) {
    if (mode !== "reconstructed") {
      errors.push(`provenance: reconstructed frame declares mode ${JSON.stringify(mode)}`);
    }
    const evidence = frame.payload?.provenance?.evidence;
    if (!Array.isArray(evidence) || evidence.length === 0) {
      errors.push("provenance: reconstructed frame carries no evidence[]");
    }
  } else if (frame.kind === "body.pulse" && mode !== "witnessed") {
    errors.push(`provenance: witnessed frame declares mode ${JSON.stringify(mode)}`);
  }

  const events = Array.isArray(frame.payload?.events) ? frame.payload.events : [];
  const gappedRepos = new Set();
  const changedRepos = new Set();
  for (const event of events) {
    if (event?.type === "observation-gap" && typeof event.source === "string") {
      const match = event.source.match(/^repo:[^/]+\/(.+)$/);
      if (match) gappedRepos.add(match[1]);
    }
    if ((event?.type === "birth" || event?.type === "vanish") && Array.isArray(event.repos)) {
      for (const name of event.repos) changedRepos.add(name);
    }
  }
  for (const name of frame.payload?.census?.born || []) changedRepos.add(name);
  for (const name of frame.payload?.census?.vanished || []) changedRepos.add(name);
  for (const name of changedRepos) {
    if (gappedRepos.has(name)) {
      errors.push(`gap-derived biography: repo "${name}" has a born/vanish change and a same-frame observation-gap`);
    }
  }
  return errors;
}

let bodyId = null;
try {
  const identity = readExact(RAPPID_PATH);
  bodyId = identity?.rappid;
  if (!(typeof bodyId === "string" && RAPPID.test(bodyId))) {
    addProblem("live", "rappid.json", `invalid canonical rappid ${JSON.stringify(bodyId)}`);
  }
} catch (error) {
  addProblem("live", "rappid.json", `unreadable/invalid JSON: ${error.message}`);
}

const files = listFrameFiles();
if (files.length === 0) addProblem("live", "frames/", "no live frames found");

let liveHead = null;
let firstWitnessedSeq = null;
for (let index = 0; index < files.length; index++) {
  const file = files[index];
  const errors = [];
  let frame;
  try {
    frame = readExact(path.join(FRAMES_DIR, file));
  } catch (error) {
    errors.push(`unreadable/invalid exact-domain JSON: ${error.message}`);
    liveHistory.push({ seq: index, file, kind: "?", hash: "--------", errors });
    addProblem("live", `frames/${file}`, errors[0]);
    continue;
  }

  if (file !== frameFileName(frame.seq)) {
    errors.push(`layout: filename ${file} does not match seq ${JSON.stringify(frame.seq)}`);
  }
  const checked = verifyFrame(frame, liveHead, { swarm: false, streamId: bodyId });
  if (!checked.ok) errors.push(`rapp/1 step ${checked.step}: ${checked.reason}`);
  errors.push(...doctrineErrors(frame, "body.pulse-reconstructed"));

  if (frame.kind === "body.pulse" && firstWitnessedSeq === null) firstWitnessedSeq = frame.seq;
  liveFrames.set(frame.seq, frame);
  liveHead = frame;
  liveHistory.push({
    seq: frame.seq,
    file,
    kind: frame.kind,
    hash: sha8(frame.frame_hash),
    errors,
  });
  for (const message of errors) addProblem("live", `frames/${file}`, message);
}

if (firstWitnessedSeq !== null) {
  for (const history of liveHistory) {
    if (history.kind === "body.pulse-reconstructed" && history.seq > firstWitnessedSeq) {
      const message = `provenance: reconstructed frame follows first witnessed seq ${firstWitnessedSeq}`;
      history.errors.push(message);
      addProblem("live", `frames/${history.file}`, message);
    }
  }
}

function comparePointer(pointer, head, label, section) {
  if (!hasExactKeys(pointer, POINTER_KEYS)) {
    addProblem(section, label, "head pointer must have exactly seq,payload_hash,frame_hash,utc,kind");
    return;
  }
  if (!head) {
    addProblem(section, label, "head pointer exists but the chain has no readable head");
    return;
  }
  for (const key of POINTER_KEYS) {
    if (pointer[key] !== head[key]) {
      addProblem(section, label, `${key} ${JSON.stringify(pointer[key])} != chain head ${JSON.stringify(head[key])}`);
    }
  }
}

const indexPath = path.join(FRAMES_DIR, "index.json");
try {
  const index = readExact(indexPath);
  if (!hasExactKeys(index, INDEX_KEYS)) {
    addProblem("index", "frames/index.json", "manifest key set is not the rapp/1 index shape");
  }
  if (index.spec !== "rapp-frame-index/1.0") {
    addProblem("index", "frames/index.json", `spec ${JSON.stringify(index.spec)} != rapp-frame-index/1.0`);
  }
  if (index.stream_id !== bodyId) {
    addProblem("index", "frames/index.json", `stream_id ${JSON.stringify(index.stream_id)} != ${bodyId}`);
  }
  if (!(typeof index.generated === "string" && UTC.test(index.generated))) {
    addProblem("index", "frames/index.json", "generated is not fixed-millisecond UTC");
  }
  if (index.count !== files.length) {
    addProblem("index", "frames/index.json", `count ${JSON.stringify(index.count)} != ${files.length}`);
  }
  comparePointer(index.head, liveHead, "frames/index.json", "index");

  if (!Array.isArray(index.frames)) {
    addProblem("index", "frames/index.json", "frames must be an array");
  } else {
    if (index.frames.length !== files.length) {
      addProblem("index", "frames/index.json", `frames length ${index.frames.length} != ${files.length}`);
    }
    for (let i = 0; i < index.frames.length; i++) {
      const entry = index.frames[i];
      const label = `frames/index.json entry ${i}`;
      if (!hasExactKeys(entry, INDEX_FRAME_KEYS)) {
        addProblem("index", label, "entry key set is not the rapp/1 index-entry shape");
        continue;
      }
      if (entry.seq !== i) addProblem("index", label, `seq ${entry.seq} != ordered position ${i}`);
      const frame = liveFrames.get(entry.seq);
      if (!frame) {
        addProblem("index", label, `lists missing/unreadable live frame seq ${entry.seq}`);
        continue;
      }
      const expected = {
        seq: frame.seq,
        path: `frames/${frameFileName(frame.seq)}`,
        utc: frame.utc,
        kind: frame.kind,
        payload_hash: frame.payload_hash,
        frame_hash: frame.frame_hash,
        prev: frame.prev,
        prev_wave: frame.prev_wave,
      };
      for (const key of INDEX_FRAME_KEYS) {
        if (entry[key] !== expected[key]) {
          addProblem("index", label, `${key} ${JSON.stringify(entry[key])} != ${JSON.stringify(expected[key])}`);
        }
      }
    }
  }
} catch (error) {
  addProblem("index", "frames/index.json", `unreadable/invalid exact-domain JSON: ${error.message}`);
}

const vitalsPath = path.join(REPO_ROOT, "vitals.json");
try {
  const vitals = readExact(vitalsPath);
  if (!hasExactKeys(vitals, VITALS_KEYS)) {
    addProblem("vitals", "vitals.json", "vitals key set is not spec,stream_id,updated,head,health");
  }
  if (vitals.spec !== "rapp-body-vitals/1.0") {
    addProblem("vitals", "vitals.json", `spec ${JSON.stringify(vitals.spec)} != rapp-body-vitals/1.0`);
  }
  if (vitals.stream_id !== bodyId) {
    addProblem("vitals", "vitals.json", `stream_id ${JSON.stringify(vitals.stream_id)} != ${bodyId}`);
  }
  if (!(typeof vitals.updated === "string" && UTC.test(vitals.updated))) {
    addProblem("vitals", "vitals.json", "updated is not fixed-millisecond UTC");
  }
  if (!isObject(vitals.health)) addProblem("vitals", "vitals.json", "health must be an object");
  comparePointer(vitals.head, liveHead, "vitals.json", "vitals");
} catch (error) {
  addProblem("vitals", "vitals.json", `unreadable/invalid exact-domain JSON: ${error.message}`);
}

function legacyCanonical(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(legacyCanonical).join(",")}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${legacyCanonical(value[key])}`).join(",")}}`;
}

function legacyPayloadHash(payload) {
  return crypto.createHash("sha256").update(legacyCanonical(payload), "utf8").digest("hex");
}

const legacyDir = path.join(FRAMES_DIR, "legacy");
const legacyFiles = numericJsonFiles(legacyDir);
const legacyFrames = new Map();
let legacyHead = null;
let legacyStreamId = null;
let legacyFirstWitnessed = null;
let legacyRulesOk = true;

if (legacyFiles.length === 0) {
  addProblem("legacy", "frames/legacy/", "sealed audit chain has no frames");
  legacyRulesOk = false;
}

for (let index = 0; index < legacyFiles.length; index++) {
  const file = legacyFiles[index];
  const label = `frames/legacy/${file}`;
  let frame;
  try {
    frame = readExact(path.join(legacyDir, file));
  } catch (error) {
    addProblem("legacy", label, `unreadable/invalid JSON: ${error.message}`);
    legacyRulesOk = false;
    continue;
  }
  const errors = [];
  if (!hasExactKeys(frame, LEGACY_FRAME_KEYS)) errors.push("legacy envelope key set mismatch");
  if (frame.spec !== "rapp-frame/2.0") errors.push(`legacy spec ${JSON.stringify(frame.spec)} != rapp-frame/2.0`);
  if (!LEGACY_KINDS.has(frame.kind)) errors.push(`unknown legacy kind ${JSON.stringify(frame.kind)}`);
  if (!(Number.isSafeInteger(frame.seq) && frame.seq >= 0)) errors.push("legacy seq not uint53");
  if (file !== frameFileName(frame.seq)) errors.push(`filename ${file} does not match seq ${JSON.stringify(frame.seq)}`);
  if (frame.seq !== index) errors.push(`legacy seq ${frame.seq} is not contiguous at ${index}`);
  if (!(typeof frame.ts === "string" && LEGACY_UTC.test(frame.ts))) errors.push("legacy ts is not UTC");
  if (!(typeof frame.twin_id === "string" && RAPPID.test(frame.twin_id))) errors.push("legacy twin_id is not a rappid");
  if (legacyStreamId === null) legacyStreamId = frame.twin_id;
  else if (frame.twin_id !== legacyStreamId) errors.push("legacy twin_id changed within sealed chain");
  if (typeof frame.kernel_version !== "string") errors.push("legacy kernel_version is not a string");
  if (!isObject(frame.payload)) errors.push("legacy payload is not an object");
  if (!(typeof frame.sha256 === "string" && HEX64.test(frame.sha256))) errors.push("legacy sha256 is not 64hex");
  if (!(frame.parent_sha === null || (typeof frame.parent_sha === "string" && HEX64.test(frame.parent_sha)))) {
    errors.push("legacy parent_sha is not null|64hex");
  }
  if (isObject(frame.payload) && legacyPayloadHash(frame.payload) !== frame.sha256) {
    errors.push("legacy payload sha256 mismatch");
  }
  const expectedParent = legacyHead ? legacyHead.sha256 : null;
  if (frame.parent_sha !== expectedParent) errors.push("legacy parent_sha linkage mismatch");
  if (legacyHead && frame.ts < legacyHead.ts) errors.push("legacy ts is non-monotonic");
  errors.push(...doctrineErrors(frame, "body.pulse.reconstructed"));

  if (frame.kind === "body.pulse" && legacyFirstWitnessed === null) legacyFirstWitnessed = frame.seq;
  const live = liveFrames.get(frame.seq);
  if (live && canonical(live.payload) !== canonical(frame.payload)) {
    errors.push("migrated rapp/1 payload differs from sealed legacy payload");
  }
  legacyFrames.set(frame.seq, frame);
  legacyHead = frame;
  for (const message of errors) addProblem("legacy", label, message);
  if (errors.length) legacyRulesOk = false;
}

if (legacyFirstWitnessed !== null) {
  for (const frame of legacyFrames.values()) {
    if (frame.kind === "body.pulse.reconstructed" && frame.seq > legacyFirstWitnessed) {
      addProblem("legacy", `frames/legacy/${frame.seq}.json`, `reconstructed frame follows first witnessed seq ${legacyFirstWitnessed}`);
      legacyRulesOk = false;
    }
  }
}

let legacySealOk = true;
const sealPath = path.join(legacyDir, "SEAL.json");
try {
  const seal = readExact(sealPath);
  if (!hasExactKeys(seal, SEAL_KEYS)) {
    addProblem("legacy", "frames/legacy/SEAL.json", "seal key set mismatch");
    legacySealOk = false;
  }
  if (seal.spec !== SPEC) {
    addProblem("legacy", "frames/legacy/SEAL.json", `spec ${JSON.stringify(seal.spec)} != ${SPEC}`);
    legacySealOk = false;
  }
  if (seal.seal_space !== "rapp/1:seal") {
    addProblem("legacy", "frames/legacy/SEAL.json", `seal_space ${JSON.stringify(seal.seal_space)} != rapp/1:seal`);
    legacySealOk = false;
  }
  if (!(typeof seal.seal === "string" && HEX64.test(seal.seal))) {
    addProblem("legacy", "frames/legacy/SEAL.json", "seal is not 64hex");
    legacySealOk = false;
  }
  if (!legacyHead || seal.sealed_head_seq !== legacyHead.seq) {
    addProblem("legacy", "frames/legacy/SEAL.json", `sealed_head_seq ${JSON.stringify(seal.sealed_head_seq)} != legacy head ${legacyHead?.seq ?? "none"}`);
    legacySealOk = false;
  }
  if (legacyFiles.length !== seal.sealed_head_seq + 1) {
    addProblem("legacy", "frames/legacy/SEAL.json", `sealed chain has ${legacyFiles.length} files, expected ${seal.sealed_head_seq + 1}`);
    legacySealOk = false;
  }
  if (legacyHead && seal.seal !== H(seal.seal_space, legacyHead)) {
    addProblem("legacy", "frames/legacy/SEAL.json", "seal does not match canonical legacy head");
    legacySealOk = false;
  }
} catch (error) {
  addProblem("legacy", "frames/legacy/SEAL.json", `unreadable/invalid exact-domain JSON: ${error.message}`);
  legacySealOk = false;
}

const reconstructed = liveHistory.filter((item) => item.kind === "body.pulse-reconstructed").length;
const witnessed = liveHistory.filter((item) => item.kind === "body.pulse").length;
console.log(`body biography — ${files.length} live frame(s) [${reconstructed} reconstructed, ${witnessed} witnessed]`);
console.log(`stream_id: ${bodyId || "INVALID"}`);
console.log("");
for (const item of liveHistory) {
  const ok = item.errors.length === 0;
  console.log(`  ${ok ? "ok" : "XX"} [${String(item.seq).padStart(2)}] ${String(item.kind).padEnd(25)} wave@${item.hash}`);
  if (!ok) for (const error of item.errors) console.log(`       ! ${error}`);
}
console.log("");

const indexOk = !problems.some((problem) => problem.section === "index");
const vitalsOk = !problems.some((problem) => problem.section === "vitals");
console.log(`static pointers — index ${indexOk ? "OK" : "FAIL"} · vitals ${vitalsOk ? "OK" : "FAIL"}`);
console.log(`legacy audit — ${legacyFiles.length} frame(s) · rules ${legacyRulesOk ? "OK" : "FAIL"} · SEAL ${legacySealOk ? "OK" : "FAIL"}`);
console.log("");

if (problems.length === 0) {
  console.log(`VERDICT: OK — all ${files.length} live frame(s) verify; index + vitals agree; sealed legacy audit chain verifies. head: seq ${liveHead.seq} wave@${sha8(liveHead.frame_hash)}`);
  process.exit(0);
}

console.error(`VERDICT: FAIL — ${problems.length} problem(s):`);
for (const problem of problems) {
  console.error(`  [${problem.section}] ${problem.file}: ${problem.msg}`);
}
process.exit(1);
