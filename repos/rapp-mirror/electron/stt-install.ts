import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { app, BrowserWindow } from "electron";

import { createLogger } from "./logger.ts";
import { whisperAvailable } from "./stt.ts";

const log = createLogger("WhisperInstall");

/* ── one-click hearing: whisper.cpp managed by the app ───────────────── */

function installProgress(line: string): void {
  for (const win of BrowserWindow.getAllWindows()) {
    win.webContents.send("voice:install-progress", line);
  }
}

function whisperBinary(): string | null {
  for (const c of ["/opt/homebrew/bin/whisper-server", "/usr/local/bin/whisper-server"]) {
    if (existsSync(c)) return c;
  }
  return null;
}

function whisperModel(): string {
  const home = process.env.RAPP_MIRROR_HOME || path.join(os.homedir(), ".rapp-mirror");
  return path.join(home, "whisper", "ggml-small.en.bin");
}

let whisperChild: ChildProcess | null = null;
let sttInstalling = false;

/** Start whisper-server if hearing is installed and nothing answers yet
 *  (never fights an already-running server, e.g. the user's own). */
export async function ensureWhisperService(): Promise<void> {
  if (await whisperAvailable()) return;
  const bin = whisperBinary();
  if (!bin || !existsSync(whisperModel())) return;
  whisperChild = spawn(bin, ["-m", whisperModel(), "--host", "127.0.0.1", "--port", "8765", "-t", "4"], {
    stdio: "ignore",
  });
  log.info("started whisper-server pid", whisperChild.pid);
}

export function stopWhisperService(): void {
  if (whisperChild && !whisperChild.killed) whisperChild.kill();
  whisperChild = null;
}

/** One-click install: brew whisper-cpp + model download, streamed progress,
 *  then start the server so HEAR flips on without a restart. */
export async function installWhisper(appRoot: string): Promise<{ ok: boolean; error?: string }> {
  if (sttInstalling) return { ok: false, error: "already installing" };
  const setup = app.isPackaged
    ? path.join(process.resourcesPath, "voice", "setup-whisper.sh")
    : path.join(appRoot, "voice", "setup-whisper.sh");
  if (!existsSync(setup)) return { ok: false, error: `setup script missing at ${setup}` };
  sttInstalling = true;
  installProgress("installing hearing (whisper.cpp + model)…");
  return await new Promise((resolve) => {
    const child = spawn("bash", [setup], { env: { ...process.env } });
    let lastLine = "";
    const onLine = (chunk: Buffer) => {
      const line = chunk.toString().trim().split("\n").pop() ?? "";
      if (line) {
        lastLine = line;
        installProgress(line.slice(0, 160));
      }
    };
    child.stdout.on("data", onLine);
    child.stderr.on("data", onLine);
    child.on("exit", (code) => {
      sttInstalling = false;
      if (code === 0) {
        void ensureWhisperService().then(() => resolve({ ok: true }));
      } else {
        resolve({ ok: false, error: lastLine || `exit ${code}` });
      }
    });
    child.on("error", (err) => {
      sttInstalling = false;
      resolve({ ok: false, error: err.message });
    });
  });
}
