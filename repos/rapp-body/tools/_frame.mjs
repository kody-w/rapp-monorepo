// tools/_frame.mjs — body frame construction, persistence, and pulse helpers.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  SPEC, KINDS, canonical, buildFrame as buildRapp1Frame, parseJsonExact, verifyFrame,
} from "./_rapp1.mjs";

export { SPEC };
export const KIND_WITNESSED = "body.pulse";
export const KIND_RECONSTRUCTED = "body.pulse-reconstructed";

// REPO_ROOT is this repo's root (tools/ lives directly under it). RAPP_BODY_ROOT
// overrides it so a ceremony can run against a throwaway body without
// touching the live frames.
export const REPO_ROOT = process.env.RAPP_BODY_ROOT
  ? path.resolve(process.env.RAPP_BODY_ROOT)
  : path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const FRAMES_DIR = path.join(REPO_ROOT, "frames");
export const RAPPID_PATH = path.join(REPO_ROOT, "rappid.json");

export const canonicalize = canonical;

export function sha256Hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

export function sha8(sha) {
  return String(sha).slice(0, 8);
}

// The body's stream identity is minted once in rappid.json. There is deliberately no
// owner/slug-derived fallback: the canonical suffix is an opaque join key.
export function readBodyId() {
  const record = parseJsonExact(fs.readFileSync(RAPPID_PATH, "utf8"));
  if (!record || typeof record.rappid !== "string") {
    throw new Error("rappid.json does not contain a rappid string");
  }
  return record.rappid;
}

// Construct through the protocol primitive, then run the same consumer checklist used by
// the gate and chain verifier. Non-genesis callers must supply the actual current head.
export function buildFrame({
  kind, seq, utc, payload, head = null, prev,
  stream_id = readBodyId(), prev_wave = null, sig = null,
}) {
  if (!KINDS.has(kind)) throw new Error(`unknown rapp/1 frame kind: ${kind}`);
  const frame = buildRapp1Frame({
    kind,
    stream_id,
    seq,
    utc,
    payload,
    prev: prev === undefined ? (head ? head.payload_hash : null) : prev,
    prev_wave,
    sig,
  });
  const checked = verifyFrame(frame, head, { swarm: false, streamId: stream_id });
  if (!checked.ok) {
    throw new Error(`constructed frame failed rapp/1 verify step ${checked.step}: ${checked.reason}`);
  }
  return frame;
}

export function frameFileName(seq) {
  return `${seq}.json`;
}

// List published frame files (<seq>.json), sorted by numeric seq ascending.
export function listFrameFiles(dir = FRAMES_DIR) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => /^\d+\.json$/.test(f))
    .sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
}

export function readFrameFile(fp) {
  return parseJsonExact(fs.readFileSync(fp, "utf8"));
}

// Read the whole chain (in seq order) as parsed frame objects.
export function readChain(dir = FRAMES_DIR) {
  return listFrameFiles(dir).map((f) => readFrameFile(path.join(dir, f)));
}

export function writeFrame(frame, dir = FRAMES_DIR) {
  fs.mkdirSync(dir, { recursive: true });
  const fp = path.join(dir, frameFileName(frame.seq));
  fs.writeFileSync(fp, JSON.stringify(frame, null, 2) + "\n");
  return fp;
}

// frames/index.json — the manifest: ONE fetch loads the whole timeline map.
export function writeIndex(frames, dir = FRAMES_DIR) {
  const head = frames[frames.length - 1] || null;
  const index = {
    spec: "rapp-frame-index/1.0",
    stream_id: readBodyId(),
    generated: new Date().toISOString(),
    count: frames.length,
    head: head ? {
      seq: head.seq,
      payload_hash: head.payload_hash,
      frame_hash: head.frame_hash,
      utc: head.utc,
      kind: head.kind,
    } : null,
    frames: frames.map((f) => ({
      seq: f.seq,
      path: `frames/${frameFileName(f.seq)}`,
      utc: f.utc,
      kind: f.kind,
      payload_hash: f.payload_hash,
      frame_hash: f.frame_hash,
      prev: f.prev,
      prev_wave: f.prev_wave,
    })),
  };
  fs.writeFileSync(path.join(dir, "index.json"), JSON.stringify(index, null, 2) + "\n");
  return index;
}

// vitals.json — the static-API surface: latest-frame pointer + current health rollup.
export function writeVitals(frame, health, root = REPO_ROOT) {
  const vitals = {
    spec: "rapp-body-vitals/1.0",
    stream_id: readBodyId(),
    updated: new Date().toISOString(),
    head: frame
      ? {
          seq: frame.seq,
          payload_hash: frame.payload_hash,
          frame_hash: frame.frame_hash,
          utc: frame.utc,
          kind: frame.kind,
        }
      : null,
    health: health || {},
  };
  fs.writeFileSync(path.join(root, "vitals.json"), JSON.stringify(vitals, null, 2) + "\n");
  return vitals;
}

// The "material" fingerprint used by the no-churn rule: skeleton + census(structure) +
// vitals, with all volatile timestamps and derived fields stripped, so an identical
// body produces an identical fingerprint regardless of when it was observed.
//
// DOCTRINE (observation gaps are transport, not biography): the fingerprint MUST ignore
// every transient observation artifact — `reachable`, `stale`, `status`, `head_stale` —
// and the events array entirely. A repo that is merely unreadable this run carries its
// last-known `head_sha` forward, so its material is byte-identical to the previous frame
// and produces NO churn. Only a real biographical change (a moved head_sha, a bumped spec
// version, a confirmed vanish that drops a repo from the census) moves the fingerprint.
export function materialFingerprint(payload) {
  const p = payload || {};
  const sk = p.skeleton || {};
  const material = {
    skeleton: {
      spec_version: sk.spec_version ?? null,
      mirrors_identical: sk.mirrors_identical ?? null,
      homes: sk.homes
        ? Object.fromEntries(Object.entries(sk.homes).map(([k, v]) => [k, v && v.sha256 || null]))
        : null,
      spine: sk.spine || null,
    },
    // per-repo material = identity + layer + head_sha ONLY. NO reachable/stale/status:
    // those are observation state, not biography. head_sha is the effective (carried-
    // forward when stale) value, so a rate-limited run fingerprints identically.
    census: (p.census?.repos || [])
      .map((r) => ({
        name: r.name,
        layer: r.layer ?? null,
        category: r.category ?? null,
        head_sha: r.head_sha ?? null,
      }))
      .sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0)),
    vitals: {
      sync: p.vitals?.sync ?? null,
      drift_issues: p.vitals?.drift_issues
        ? { open: p.vitals.drift_issues.open ?? null, high: p.vitals.drift_issues.high ?? null }
        : null,
      mirrors_identical: p.vitals?.mirrors_identical ?? null,
    },
  };
  return sha256Hex(canonicalize(material));
}
