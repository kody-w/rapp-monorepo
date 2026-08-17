import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import type { EngineStateView } from "../common/ipc.ts";
import { createLogger } from "./logger.ts";
import { brainstemUrl, health } from "./brainstem.ts";

/**
 * The mirror's engine is the GLOBAL RAPP brainstem (the grail install at
 * ~/.brainstem, port 7071). If one is already installed and running, the
 * mirror simply layers over it — nothing is touched. If none exists, the
 * grail Pages installer provisions one (global mode auto-starts it). If one
 * exists but isn't running, the installer is re-run — it is kernel-preserving
 * by design and relaunches the server.
 *
 * Electron-free on purpose (like brainstem.ts/sessionstore.ts) so plain-node
 * tests can exercise every path; window plumbing lives in the callers via
 * the EngineCallbacks hooks.
 *
 * Env override: `RAPP_INSTALLER_URL`.
 */

const log = createLogger("Engine");

const INSTALLER_URL = () =>
  process.env.RAPP_INSTALLER_URL || "https://kody-w.github.io/RAPP/installer/install.sh";

const INSTALL_TIMEOUT_MS = 420_000;
const PREFLIGHT_TIMEOUT_MS = 15_000;
/** How much installer output to keep for the failure report. */
const TAIL_LINES = 12;

export interface EngineState {
  url: string;
  running: boolean;
  installed: boolean;
  /** What ensureEngine did: "none" | "installed" | "failed" | "unavailable". */
  action: "none" | "installed" | "failed" | "unavailable";
  error?: string;
}

export interface EngineCallbacks {
  /** One trimmed line of live installer output. */
  onLine?: (line: string) => void;
  /** Provisioning state transitions (checking -> installing -> settled). */
  onState?: (state: EngineStateView) => void;
}

export function toView(state: EngineState): EngineStateView {
  const phase = state.action === "none" || state.action === "installed"
    ? ("ready" as const)
    : state.action;
  return { phase, url: state.url, detail: state.error };
}

function globalInstallDir(): string {
  return path.join(os.homedir(), ".brainstem");
}

/**
 * Pre-flight the installer URL. The grail installer can be withdrawn (it then
 * serves a "410 Gone" refusal script that exits 78) — running that through
 * `curl | bash` would only fail invisibly, so detect it up front and report
 * the refusal itself.
 */
async function preflightInstaller(): Promise<{ ok: boolean; reason?: string }> {
  try {
    const r = await fetch(INSTALLER_URL(), { signal: AbortSignal.timeout(PREFLIGHT_TIMEOUT_MS) });
    if (!r.ok) return { ok: false, reason: `installer URL returned HTTP ${r.status}` };
    const body = await r.text();
    if (/410 Gone/i.test(body)) {
      // The refusal lives inside a printf script — strip the shell quoting.
      const line = body.split("\n").find((l) => /410 Gone/i.test(l))
        ?.trim().replace(/\\$/, "").trim().replace(/^"|"$/g, "");
      return { ok: false, reason: `installer is currently withdrawn — ${line || "410 Gone"}` };
    }
    return { ok: true };
  } catch (err) {
    return { ok: false, reason: `installer unreachable: ${err instanceof Error ? err.message : String(err)}` };
  }
}

let inflight: Promise<EngineState> | null = null;

/** Make sure a global brainstem answers on :7071 — installing one from the
 *  grail kernel repo only when the machine has none. Never restarts or
 *  touches a live install. Concurrency-safe: overlapping calls share one
 *  provisioning run (so two callers can never race two installers). */
export function ensureEngine(cb?: EngineCallbacks): Promise<EngineState> {
  if (inflight) return inflight;
  inflight = run(cb ?? {}).finally(() => {
    inflight = null;
  });
  return inflight;
}

async function run(cb: EngineCallbacks): Promise<EngineState> {
  const url = brainstemUrl();
  const installed = existsSync(globalInstallDir());
  cb.onState?.({ phase: "checking", url });

  if ((await health()).ok) {
    log.info("global brainstem already live at", url, "— layering over it");
    const state: EngineState = { url, running: true, installed: true, action: "none" };
    cb.onState?.(toView(state));
    return state;
  }

  const settle = (state: EngineState): EngineState => {
    cb.onState?.(toView(state));
    return state;
  };

  const preflight = await preflightInstaller();
  if (!preflight.ok) {
    log.warn("engine installer pre-flight:", preflight.reason);
    return settle({ url, running: false, installed, action: "unavailable", error: preflight.reason });
  }

  log.info(installed
    ? "global brainstem installed but not answering — re-running the grail installer (kernel-preserving)"
    : "no global brainstem — installing from the grail kernel repo…");
  cb.onState?.({ phase: "installing", url, detail: installed ? "waking your brainstem…" : "planting your brainstem (one time)…" });
  cb.onLine?.(installed ? "waking your brainstem…" : "planting your brainstem (one time)…");
  // fresh Macs: spawning git triggers Apple's Command Line Tools dialog — a
  // click, not a terminal.
  spawn("git", ["--version"], { stdio: "ignore" }).on("error", () => undefined);

  const tail: string[] = [];
  const outcome = await new Promise<{ code: number | null; timedOut: boolean }>((resolve) => {
    const child = spawn(
      "bash",
      ["-c", `curl -fsSL "${INSTALLER_URL()}" | RAPP_NO_BROWSER=1 bash`],
      { stdio: "pipe" },
    );
    const onChunk = (c: Buffer) => {
      for (const raw of c.toString().split("\n")) {
        const line = raw.trim();
        if (!line) continue;
        tail.push(line);
        if (tail.length > TAIL_LINES) tail.shift();
        cb.onLine?.(line);
      }
    };
    child.stdout?.on("data", onChunk);
    child.stderr?.on("data", onChunk);
    const timer = setTimeout(() => { child.kill(); resolve({ code: null, timedOut: true }); }, INSTALL_TIMEOUT_MS);
    child.on("exit", (code) => { clearTimeout(timer); resolve({ code, timedOut: false }); });
    child.on("error", (err) => { clearTimeout(timer); tail.push(String(err.message)); resolve({ code: -1, timedOut: false }); });
  });

  // A failed installer must fail HERE, with its own words — not dribble into
  // a blind health poll that can only say "did not answer".
  if (outcome.timedOut) {
    return settle({
      url, running: false, installed: existsSync(globalInstallDir()), action: "failed",
      error: `installer timed out after ${INSTALL_TIMEOUT_MS / 60000} minutes — last output: ${tail.slice(-3).join(" | ") || "(none)"}`,
    });
  }
  if (outcome.code !== 0) {
    return settle({
      url, running: false, installed: existsSync(globalInstallDir()), action: "failed",
      error: `installer exited with code ${outcome.code}: ${tail.slice(-5).join(" | ") || "(no output)"}`,
    });
  }

  for (let i = 0; i < 15; i++) {
    if ((await health()).ok) {
      log.info("engine live at", url);
      return settle({ url, running: true, installed: true, action: "installed" });
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  return settle({
    url,
    running: false,
    installed: existsSync(globalInstallDir()),
    action: "failed",
    error: "installer finished but the brainstem never answered /health — check ~/.brainstem logs",
  });
}
