import path from "node:path";
import { fileURLToPath } from "node:url";

import { BrowserWindow, ipcMain, shell, systemPreferences } from "electron";

import { IPC, type ChatTurn, type EngineStateView, type SessionPatch } from "../common/ipc.ts";
import { brainstemUrl, chat, health, loginPoll, loginStart } from "./brainstem.ts";
import { ensureEngine } from "./engine.ts";
import {
  deployAgent,
  distill,
  exportAll,
  normalizeSpec,
  type ForgeSpec,
} from "./forge.ts";
import { activate, licenseState } from "./license.ts";
import { acceptAgent } from "./agentshare.ts";
import { createLogger } from "./logger.ts";
import { decideRehearsal, loadRehearsal, rehearse } from "./rehearsal.ts";
import {
  createSession,
  deleteSession,
  listSessions,
  updateSession,
} from "./sessionstore.ts";
import { setBrainstemUrlOverride } from "./settings.ts";
import { installWhisper } from "./stt-install.ts";
import { transcribe } from "./stt.ts";
import { surgeon } from "./surgeon.ts";
import { installVoice, tts, voiceStatus } from "./voice.ts";
import { createStickyWindow } from "./window.ts";

const log = createLogger("IPC");
const ipcDir = path.dirname(fileURLToPath(import.meta.url));
const msg = (err: unknown) => (err instanceof Error ? err.message : String(err));

/* ── engine provisioning: one shared run, state pushed to every window ── */

let engineView: EngineStateView | null = null;

const pushEngineState = (state: EngineStateView) => {
  engineView = state;
  for (const w of BrowserWindow.getAllWindows()) {
    w.webContents.send(IPC.engineState, state);
  }
};

/** Provision the engine (health check -> install if needed), streaming state
 *  transitions and live installer lines to every window. Concurrency-safe —
 *  ensureEngine shares one in-flight run. */
export async function runEngine(): Promise<EngineStateView> {
  const state = await ensureEngine({
    onState: pushEngineState,
    onLine: (line) => {
      for (const w of BrowserWindow.getAllWindows()) {
        w.webContents.send(IPC.voiceInstallProgress, `brainstem: ${line}`.slice(0, 160));
      }
    },
  });
  return engineView ?? { phase: state.running ? "ready" : "failed", url: state.url, detail: state.error };
}

/** Wire every mirror:* / forge:* channel (skill-recorder registerIpc idiom). */
export function registerIpc(): void {
  // The only door into the brainstem for an agent someone handed you. The
  // renderer can show a card and ask; it cannot install anything itself.
  ipcMain.handle(
    "mirror:accept-arrival",
    (_e, spec: ForgeSpec, opts?: { acceptDangerous?: boolean; force?: boolean }) =>
      acceptAgent(spec, opts ?? {}),
  );

  ipcMain.handle(IPC.health, () => health());

  ipcMain.handle(IPC.chat, (_e, userInput: string, history: ChatTurn[], sessionId: string) =>
    chat(String(userInput ?? ""), Array.isArray(history) ? history : [], String(sessionId ?? "mirror")),
  );

  ipcMain.handle(IPC.tts, async (_e, text: string) => {
    const wav = await tts(String(text ?? ""));
    return wav; // ArrayBuffer | null — structured clone handles both
  });

  ipcMain.handle(IPC.voiceStatus, () => voiceStatus());

  ipcMain.handle(IPC.transcribe, async (_e, wav: ArrayBuffer) => {
    try {
      const text = await transcribe(new Uint8Array(wav));
      return { ok: true, text };
    } catch (err) {
      return { ok: false, error: msg(err) };
    }
  });

  ipcMain.handle(IPC.askMedia, async (_e, kind: "camera" | "microphone") => {
    if (process.platform !== "darwin") return true;
    try {
      // TCC flow: "not-determined" -> the one-time native prompt;
      // "denied"/"restricted" -> open System Settings on the right pane so
      // the user can flip the switch (macOS never re-prompts once denied).
      const status = systemPreferences.getMediaAccessStatus(kind);
      if (status === "granted") return true;
      if (status === "not-determined") return await systemPreferences.askForMediaAccess(kind);
      const pane = kind === "camera" ? "Privacy_Camera" : "Privacy_Microphone";
      void shell.openExternal(`x-apple.systempreferences:com.apple.preference.security?${pane}`);
      return false;
    } catch (err) {
      log.warn("askForMediaAccess failed:", msg(err));
      return false;
    }
  });

  ipcMain.handle(
    IPC.forgeDistill,
    async (_e, history: ChatTurn[], screenContext: string[], sessionId: string) => {
      try {
        const spec = await distill(
          Array.isArray(history) ? history : [],
          Array.isArray(screenContext) ? screenContext : [],
          String(sessionId ?? "mirror"),
        );
        return { ok: true, spec };
      } catch (err) {
        return { ok: false, error: msg(err) };
      }
    },
  );

  ipcMain.handle(IPC.forgeExport, (_e, rawSpec: Record<string, unknown>) => {
    try {
      const spec: ForgeSpec = normalizeSpec(rawSpec);
      return { ok: true, ...exportAll(spec) };
    } catch (err) {
      return { ok: false, error: msg(err) };
    }
  });

  ipcMain.handle(IPC.forgeDeploy, async (_e, rawSpec: Record<string, unknown>, force?: boolean) => {
    try {
      return await deployAgent(normalizeSpec(rawSpec), { force: force === true });
    } catch (err) {
      return { ok: false, error: msg(err) };
    }
  });

  /* ── the Rehearsal: virtual-twin dry-runs before deploy ────────────── */
  ipcMain.handle(IPC.rehearseStart, async (_e, rawSpec: Record<string, unknown>, sessionId: string) => {
    try {
      const transcript = await rehearse(rawSpec, String(sessionId ?? "mirror"), (ev) => {
        for (const w of BrowserWindow.getAllWindows()) w.webContents.send(IPC.rehearsalEvent, ev);
      });
      return { ok: transcript.state === "awaiting-confirmation", transcript };
    } catch (err) {
      return { ok: false, error: msg(err) };
    }
  });
  ipcMain.handle(
    IPC.rehearseDecide,
    (_e, specName: string, verdict: "confirmed" | "rejected", note?: string, method?: string) =>
      decideRehearsal(String(specName), verdict === "rejected" ? "rejected" : "confirmed",
        note ? String(note) : undefined, method ? String(method) : "mirror"),
  );
  ipcMain.handle(IPC.rehearseStatus, (_e, specName: string) => {
    const t = loadRehearsal(String(specName));
    return t ? { ok: true, transcript: t } : { ok: false, error: "never rehearsed" };
  });

  ipcMain.handle(IPC.forgeReveal, (_e, p: string) => {
    if (typeof p === "string" && p) shell.showItemInFolder(p);
  });

  /* ── sessions: every chat keeps running; every window stays in sync ── */
  const broadcast = () => {
    const sessions = listSessions();
    for (const w of BrowserWindow.getAllWindows()) {
      w.webContents.send(IPC.sessionsChanged, sessions);
    }
  };

  ipcMain.handle(IPC.sessionsList, () => listSessions());
  ipcMain.handle(IPC.sessionsCreate, () => {
    const s = createSession();
    broadcast();
    return s;
  });
  ipcMain.handle(IPC.sessionsUpdate, (_e, patch: SessionPatch) => {
    const s = updateSession(patch);
    broadcast();
    return s;
  });
  ipcMain.handle(IPC.sessionsDelete, (_e, id: string) => {
    deleteSession(String(id));
    broadcast();
  });
  ipcMain.handle(IPC.popout, (_e, sessionId: string) => {
    if (typeof sessionId === "string" && sessionId) createStickyWindow(sessionId);
  });

  ipcMain.handle(IPC.openExternal, (_e, url: string) => {
    if (typeof url === "string" && /^https?:\/\//.test(url)) void shell.openExternal(url);
  });

  ipcMain.handle(IPC.surgeonCreate, async () => {
    try {
      return { ok: true, id: await surgeon.create() };
    } catch (err) {
      return { ok: false, error: msg(err) };
    }
  });
  ipcMain.handle(IPC.surgeonSend, (_e, id: string, text: string) =>
    surgeon.send(String(id), String(text ?? "")),
  );
  ipcMain.handle(IPC.surgeonCancel, (_e, id: string) => surgeon.cancel(String(id)));
  ipcMain.handle(IPC.surgeonClose, (_e, id: string) => surgeon.close(String(id)));
  ipcMain.handle(IPC.surgeonList, () => surgeon.list());

  ipcMain.handle(IPC.voiceInstall, () => installVoice(path.join(ipcDir, "..")));
  ipcMain.handle(IPC.sttInstall, () => installWhisper(path.join(ipcDir, "..")));

  ipcMain.handle(IPC.brainLogin, () => loginStart());
  ipcMain.handle(IPC.brainLoginPoll, () => loginPoll());

  ipcMain.handle(IPC.licenseGet, () => licenseState());
  ipcMain.handle(IPC.licenseActivate, (_e, key: string) => activate(String(key ?? "")));

  ipcMain.handle(IPC.engineGet, (): EngineStateView =>
    engineView ?? { phase: "checking", url: brainstemUrl() });
  ipcMain.handle(IPC.engineRetry, () => runEngine());
  ipcMain.handle(IPC.brainstemSetUrl, (_e, url: string) => {
    const u = String(url ?? "").trim();
    if (u && !/^https?:\/\//.test(u)) {
      return { ok: false, error: "URL must start with http:// or https://" };
    }
    setBrainstemUrlOverride(u);
    log.info(u ? `brainstem URL set to ${u}` : "brainstem URL override cleared");
    void runEngine();
    return { ok: true };
  });
}
