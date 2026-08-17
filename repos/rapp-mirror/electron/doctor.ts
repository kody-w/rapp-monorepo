import { accessSync, mkdirSync, readFileSync } from "node:fs";
import { constants } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { health } from "./brainstem.ts";
import { brainstemAgentsDir, exportsRoot } from "./forge.ts";
import { rehearsalsDir } from "./rehearsal.ts";
import { whisperAvailable, whisperUrl } from "./stt.ts";

export type CheckStatus = "ok" | "degraded" | "unavailable";

export interface DoctorCheck {
  id: string;
  title: string;
  status: CheckStatus;
  /** What is actually true, with real values. */
  detail: string;
  /** What the human/agent should do; omitted when ok. */
  nextAction?: string;
}

export interface DoctorReport {
  /** True only when no check is unavailable. */
  ok: boolean;
  at: string;
  app: string;
  checks: DoctorCheck[];
}

const INSTALLER_URL = () =>
  process.env.RAPP_INSTALLER_URL || "https://kody-w.github.io/RAPP/installer/install.sh";

function msg(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

/** The app's own version. `import.meta.url` is not a file URL once the main
 *  process is bundled, so try the module's own directory first and fall back
 *  to the working tree — a doctor that cannot name the build is useless. */
function packageVersion(): string {
  const candidates: string[] = [];
  try {
    candidates.push(path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "package.json"));
  } catch {
    // Bundled: import.meta.url is not a file URL. The cwd fallbacks below win.
  }
  candidates.push(
    path.join(process.cwd(), "package.json"),
    path.join(process.cwd(), "..", "package.json"),
  );
  for (const file of candidates) {
    try {
      const pkg = JSON.parse(readFileSync(file, "utf8")) as { name?: string; version?: string };
      if (pkg.version && pkg.name === "rapp-mirror") return pkg.version;
    } catch {
      // Try the next candidate.
    }
  }
  return "unknown";
}

async function checked(id: string, title: string, fn: () => Promise<DoctorCheck> | DoctorCheck): Promise<DoctorCheck> {
  try {
    return await fn();
  } catch (err) {
    return {
      id,
      title,
      status: "unavailable",
      detail: `check failed: ${msg(err)}`,
      nextAction: "Fix the reported error, then run mirrorctl doctor again.",
    };
  }
}

function refusalLine(body: string): string {
  const line = body.split(/\r?\n/).find((l) => /410 Gone|refuses to fetch/i.test(l)) || body;
  return line
    .replace(/\\n/g, " ")
    .replace(/^printf\s+['"][^'"]*['"]\s*/i, "")
    .replace(/^['"]|['"]$/g, "")
    .trim()
    .slice(0, 240);
}

async function engineCheck(): Promise<DoctorCheck> {
  const h = await health();
  if (h.ok) {
    return {
      id: "engine",
      title: "Brainstem engine",
      status: "ok",
      detail: `brainstem ${h.version || "unknown version"}; model ${h.model || "unknown"}; ${(h.agents || []).length} agents`,
    };
  }
  return {
    id: "engine",
    title: "Brainstem engine",
    status: "unavailable",
    detail: `brainstem did not answer health: ${h.error || h.status || "unknown error"}`,
    nextAction: "Start the brainstem, fix RAPP_BRAINSTEM_URL, or run the installer once it is available.",
  };
}

async function installerCheck(): Promise<DoctorCheck> {
  const url = INSTALLER_URL();
  const r = await fetch(url, { signal: AbortSignal.timeout(10_000) });
  const body = await r.text();
  if (/410 Gone|refuses to fetch/i.test(body)) {
    const refusal = refusalLine(body);
    return {
      id: "installer",
      title: "Brainstem installer",
      status: "unavailable",
      detail: `installer at ${url} refused: "${refusal}"`,
      nextAction: "Install a brainstem another way, or set RAPP_INSTALLER_URL to a working installer.",
    };
  }
  if (!r.ok) {
    return {
      id: "installer",
      title: "Brainstem installer",
      status: "unavailable",
      detail: `installer at ${url} returned HTTP ${r.status}`,
      nextAction: "Set RAPP_INSTALLER_URL to a reachable installer or install a brainstem another way.",
    };
  }
  return {
    id: "installer",
    title: "Brainstem installer",
    status: "ok",
    detail: `installer at ${url} returned HTTP ${r.status} with ${body.length} bytes`,
  };
}

async function voiceCheck(): Promise<DoctorCheck> {
  let v: Awaited<ReturnType<typeof import("./voice.ts")["voiceStatus"]>>;
  try {
    const voice = await import("./voice.ts");
    v = await voice.voiceStatus();
  } catch (err) {
    return {
      id: "voice",
      title: "Voice output",
      status: "degraded",
      detail: `VibeVoice status could not be queried: ${msg(err)}`,
      nextAction: "Run this inside the Electron app, or start/install VibeVoice when spoken output is required; captions still work.",
    };
  }
  const detail = `VibeVoice ${v.vibevoice}; speaker ${v.speaker || "unknown"}; device ${v.device || "unknown"}; whisper ${v.whisper ? "available" : "absent"}`;
  if (v.vibevoice === "ready") {
    return { id: "voice", title: "Voice output", status: "ok", detail };
  }
  return {
    id: "voice",
    title: "Voice output",
    status: "degraded",
    detail,
    nextAction: "Start or install VibeVoice when spoken output is required; the mirror still works with captions.",
  };
}

async function hearingCheck(): Promise<DoctorCheck> {
  const available = await whisperAvailable();
  if (available) {
    return { id: "hearing", title: "Voice input", status: "ok", detail: `whisper server answered at ${whisperUrl()}` };
  }
  return {
    id: "hearing",
    title: "Voice input",
    status: "degraded",
    detail: `no whisper server answered at ${whisperUrl()}`,
    nextAction: "Start whisper.cpp if voice input is required; typed input still works.",
  };
}

function writableDirCheck(id: string, title: string, dir: string, create: boolean): DoctorCheck {
  if (create) mkdirSync(dir, { recursive: true });
  accessSync(dir, constants.W_OK);
  return { id, title, status: "ok", detail: `${dir} exists and is writable` };
}

function nodeCheck(): DoctorCheck {
  return { id: "node", title: "Node.js", status: "ok", detail: `running ${process.version}` };
}

export async function runDoctor(): Promise<DoctorReport> {
  const checks = await Promise.all([
    checked("engine", "Brainstem engine", engineCheck),
    checked("installer", "Brainstem installer", installerCheck),
    checked("voice", "Voice output", voiceCheck),
    checked("hearing", "Voice input", hearingCheck),
    checked("agentsDir", "Brainstem agents dir", () =>
      writableDirCheck("agentsDir", "Brainstem agents dir", brainstemAgentsDir(), false)),
    checked("exports", "Exports dir", () =>
      writableDirCheck("exports", "Exports dir", exportsRoot(), true)),
    checked("rehearsals", "Rehearsals dir", () =>
      writableDirCheck("rehearsals", "Rehearsals dir", rehearsalsDir(), true)),
    checked("node", "Node.js", nodeCheck),
  ]);
  return {
    ok: checks.every((c) => c.status !== "unavailable"),
    at: new Date().toISOString(),
    app: packageVersion(),
    checks,
  };
}
