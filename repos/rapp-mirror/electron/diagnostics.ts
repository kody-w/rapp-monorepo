import { appendFileSync, existsSync, mkdirSync, renameSync, statSync } from "node:fs";
import os from "node:os";
import path from "node:path";

/**
 * The evidence ledger — the mirror's answer to "did that actually happen?".
 *
 * Zero telemetry: nothing leaves the machine, ever. Everything the mirror does
 * lands here as a redacted JSONL line under `~/.rapp-mirror/logs/`, plus a
 * bounded in-memory ring the control plane serves over `/events?since=<seq>`
 * so an autonomous agent can tell "worked" from "silently did nothing".
 *
 * Env override: `RAPP_MIRROR_LOGS`.
 */

export type DiagnosticLevel = "info" | "warn" | "error";

export interface DiagnosticEvent {
  /** Monotonic within a process run — the cursor an agent polls. */
  seq: number;
  at: string;
  component: string;
  level: DiagnosticLevel;
  message: string;
  detail?: unknown;
}

export interface DiagnosticsSnapshot {
  seq: number;
  logPath: string;
  recent: DiagnosticEvent[];
  errors: DiagnosticEvent[];
}

const RING_MAX = 500;
const ERROR_MAX = 50;
const FILE_MAX_BYTES = 512_000;

let seq = 0;
let ring: DiagnosticEvent[] = [];
let errors: DiagnosticEvent[] = [];
/** One failed write is enough; never spam a broken disk on every log line. */
let writesDisabled = false;

export function logsDir(): string {
  return (
    process.env.RAPP_MIRROR_LOGS ||
    path.join(process.env.RAPP_MIRROR_HOME || path.join(os.homedir(), ".rapp-mirror"), "logs")
  );
}

export function logPath(): string {
  return path.join(logsDir(), "mirror.jsonl");
}

/** Drop anything that looks like the per-install brainstem secret. Values are
 *  matched by key name, so a renamed secret still cannot ride along. */
const SECRET_KEY = /secret|token|password|authorization|api[-_]?key/i;

function redact(value: unknown, depth = 0): unknown {
  if (depth > 4) return "[deep]";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map((v) => redact(v, depth + 1));
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = SECRET_KEY.test(k) ? "[redacted]" : redact(v, depth + 1);
    }
    return out;
  }
  return value;
}

/** Secrets also leak through prose ("failed with X-Brainstem-Secret: sk-…").
 *  Scrub the value that follows any secret-ish label. */
function redactText(text: string): string {
  return text.replace(
    /((?:secret|token|password|authorization|api[-_]?key)\s*[:=]\s*)(\S+)/gi,
    "$1[redacted]",
  );
}

function rotateIfLarge(file: string): void {
  try {
    if (existsSync(file) && statSync(file).size > FILE_MAX_BYTES) {
      renameSync(file, file + ".1");
    }
  } catch {
    // A rotation we cannot perform must not stop us recording the event.
  }
}

/** Record an event. Never throws — a broken disk must not break the mirror. */
export function record(event: Omit<DiagnosticEvent, "seq" | "at">): DiagnosticEvent {
  const full: DiagnosticEvent = {
    ...event,
    message: redactText(event.message),
    detail: event.detail === undefined ? undefined : redact(event.detail),
    seq: ++seq,
    at: new Date().toISOString(),
  };

  ring.push(full);
  if (ring.length > RING_MAX) ring = ring.slice(-RING_MAX);
  if (full.level === "error") {
    errors.push(full);
    if (errors.length > ERROR_MAX) errors = errors.slice(-ERROR_MAX);
  }

  if (!writesDisabled) {
    try {
      const file = logPath();
      mkdirSync(path.dirname(file), { recursive: true });
      rotateIfLarge(file);
      appendFileSync(file, JSON.stringify(full) + "\n");
    } catch {
      writesDisabled = true;
    }
  }
  return full;
}

/** Everything newer than a cursor — the poll an autonomous agent makes. */
export function eventsSince(cursor: number, limit = RING_MAX): DiagnosticEvent[] {
  return ring.filter((e) => e.seq > cursor).slice(0, limit);
}

export function diagnosticsSnapshot(): DiagnosticsSnapshot {
  return { seq, logPath: logPath(), recent: [...ring], errors: [...errors] };
}

/** Test seam: forget everything and re-enable writes for a fresh log dir. */
export function resetDiagnostics(): void {
  seq = 0;
  ring = [];
  errors = [];
  writesDisabled = false;
}
