import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { app, BrowserWindow } from "electron";

import type { VoiceStatus } from "../common/ipc.ts";
import { createLogger } from "./logger.ts";
import { whisperAvailable } from "./stt.ts";

/**
 * The mirror's spoken voice: a local VibeVoice-Realtime-0.5B HTTP service
 * (voice/server.py). This module owns its lifecycle — start it if the
 * ~/.rapp-mirror environment exists (voice/setup.sh creates it), poll its
 * health, and proxy synthesis. The renderer falls back to speechSynthesis
 * whenever the service isn't ready, so everything here is best-effort.
 */

const log = createLogger("Voice");

function voicePort(): string {
  return process.env.VOICE_PORT || "8971";
}
function voiceUrl(): string {
  return process.env.RAPP_VOICE_URL || `http://127.0.0.1:${voicePort()}`;
}
function mirrorHome(): string {
  return process.env.RAPP_MIRROR_HOME || path.join(os.homedir(), ".rapp-mirror");
}

let child: ChildProcess | null = null;

/** Spawn the voice service when its env exists and nothing answers yet. */
export async function ensureVoiceService(appRoot: string): Promise<void> {
  const python = path.join(mirrorHome(), "venv", "bin", "python");
  const server = app.isPackaged
    ? path.join(process.resourcesPath, "voice", "server.py")
    : path.join(appRoot, "voice", "server.py");
  if (!existsSync(python) || !existsSync(server)) {
    log.info("no VibeVoice environment — system voice only (voice/setup.sh to enable)");
    return;
  }
  try {
    const r = await fetch(voiceUrl() + "/health", { signal: AbortSignal.timeout(1500) });
    if (r.ok) {
      log.info("voice service already answering on", voiceUrl());
      return;
    }
  } catch {
    /* not running — start it */
  }
  child = spawn(python, [server], {
    env: { ...process.env, VOICE_PORT: voicePort() },
    stdio: "ignore",
    detached: false,
  });
  log.info("started VibeVoice service pid", child.pid);
}

let installing = false;

function installProgress(line: string): void {
  for (const win of BrowserWindow.getAllWindows()) {
    win.webContents.send("voice:install-progress", line);
  }
}

/** One-click VibeVoice install: runs voice/setup.sh (clone + venv + deps into
 *  ~/.rapp-mirror), streaming progress to the renderer, then starts the
 *  service. The app is fully usable on the system voice throughout. */
export async function installVoice(appRoot: string): Promise<{ ok: boolean; error?: string }> {
  if (installing) return { ok: false, error: "already installing" };
  const setup = app.isPackaged
    ? path.join(process.resourcesPath, "voice", "setup.sh")
    : path.join(appRoot, "voice", "setup.sh");
  if (!existsSync(setup)) return { ok: false, error: `setup script missing at ${setup}` };
  installing = true;
  installProgress("starting VibeVoice install — a few GB, one time…");
  return await new Promise((resolve) => {
    const child = spawn("bash", [setup], { env: { ...process.env } });
    let lastErr = "";
    const onLine = (chunk: Buffer) => {
      const line = chunk.toString().trim().split("\n").pop() ?? "";
      if (line) {
        lastErr = line;
        installProgress(line.slice(0, 160));
      }
    };
    child.stdout.on("data", onLine);
    child.stderr.on("data", onLine);
    child.on("exit", (code) => {
      installing = false;
      if (code === 0) {
        installProgress("installed — starting the voice (first synthesis downloads the model)…");
        void ensureVoiceService(appRoot).then(() => resolve({ ok: true }));
      } else {
        installProgress(`install failed (exit ${code}) — ${lastErr}`);
        resolve({ ok: false, error: lastErr || `exit ${code}` });
      }
    });
    child.on("error", (err) => {
      installing = false;
      resolve({ ok: false, error: err.message });
    });
  });
}

export function stopVoiceService(): void {
  if (child && !child.killed) child.kill();
  child = null;
}

export async function voiceStatus(): Promise<VoiceStatus> {
  const whisper = await whisperAvailable();
  try {
    const r = await fetch(voiceUrl() + "/health", { signal: AbortSignal.timeout(1500) });
    const j = (await r.json()) as { status?: string; speaker?: string; device?: string };
    const vibevoice =
      j.status === "ready" ? "ready" : j.status === "loading" ? "loading" : "error";
    return { vibevoice, speaker: j.speaker, device: j.device, whisper };
  } catch {
    return { vibevoice: "off", whisper };
  }
}

/** Synthesize via VibeVoice; null when unavailable (caller falls back). */
export async function tts(text: string): Promise<ArrayBuffer | null> {
  try {
    const r = await fetch(voiceUrl() + "/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(90_000),
    });
    if (!r.ok) return null;
    return await r.arrayBuffer();
  } catch {
    return null;
  }
}
