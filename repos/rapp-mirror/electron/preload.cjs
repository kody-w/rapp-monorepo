// Preload bridge — CommonJS on purpose (runs in the renderer's isolated world).
// Keep channel strings in sync with common/ipc.ts.
const { contextBridge, ipcRenderer } = require("electron");

const IPC = {
  health: "mirror:health",
  chat: "mirror:chat",
  tts: "mirror:tts",
  voiceStatus: "mirror:voice-status",
  transcribe: "mirror:transcribe",
  askMedia: "mirror:ask-media",
  forgeDistill: "forge:distill",
  forgeExport: "forge:export",
  forgeDeploy: "forge:deploy",
  forgeReveal: "forge:reveal",
  sessionsList: "sessions:list",
  sessionsCreate: "sessions:create",
  sessionsUpdate: "sessions:update",
  sessionsDelete: "sessions:delete",
  sessionsChanged: "sessions:changed",
  popout: "mirror:popout",
  openExternal: "mirror:open-external",
};

contextBridge.exposeInMainWorld("mirror", {
  cameraFrameUrl: process.env.RAPP_MIRROR_FRAME_URL || "",
  preferredMicLabel: process.env.RAPP_MIRROR_MIC_LABEL || "",
  headlessGestures: process.env.RAPP_MIRROR_HEADLESS_GESTURES === "1",
  headlessMic: process.env.RAPP_MIRROR_HEADLESS_MIC === "1",
  health: () => ipcRenderer.invoke(IPC.health),
  chat: (userInput, history, sessionId) => ipcRenderer.invoke(IPC.chat, userInput, history, sessionId),
  tts: (text) => ipcRenderer.invoke(IPC.tts, text),
  voiceStatus: () => ipcRenderer.invoke(IPC.voiceStatus),
  transcribe: (wav) => ipcRenderer.invoke(IPC.transcribe, wav),
  askMedia: (kind) => ipcRenderer.invoke(IPC.askMedia, kind),
  forgeDistill: (history, screenContext, sessionId) =>
    ipcRenderer.invoke(IPC.forgeDistill, history, screenContext, sessionId),
  forgeExport: (spec) => ipcRenderer.invoke(IPC.forgeExport, spec),
  forgeDeploy: (spec, force) => ipcRenderer.invoke(IPC.forgeDeploy, spec, force),
  forgeReveal: (path) => ipcRenderer.invoke(IPC.forgeReveal, path),
  listSessions: () => ipcRenderer.invoke(IPC.sessionsList),
  createSession: () => ipcRenderer.invoke(IPC.sessionsCreate),
  updateSession: (patch) => ipcRenderer.invoke(IPC.sessionsUpdate, patch),
  deleteSession: (id) => ipcRenderer.invoke(IPC.sessionsDelete, id),
  popout: (sessionId) => ipcRenderer.invoke(IPC.popout, sessionId),
  openExternal: (url) => ipcRenderer.invoke(IPC.openExternal, url),
  onSessionsChanged: (cb) => {
    const listener = (_e, sessions) => cb(sessions);
    ipcRenderer.on(IPC.sessionsChanged, listener);
    return () => ipcRenderer.removeListener(IPC.sessionsChanged, listener);
  },
  surgeonCreate: () => ipcRenderer.invoke("surgeon:create"),
  surgeonSend: (id, text) => ipcRenderer.invoke("surgeon:send", id, text),
  surgeonCancel: (id) => ipcRenderer.invoke("surgeon:cancel", id),
  surgeonClose: (id) => ipcRenderer.invoke("surgeon:close", id),
  surgeonList: () => ipcRenderer.invoke("surgeon:list"),
  voiceInstall: () => ipcRenderer.invoke("voice:install"),
  sttInstall: () => ipcRenderer.invoke("stt:install"),
  onVoiceInstallProgress: (cb) => {
    const listener = (_e, line) => cb(line);
    ipcRenderer.on("voice:install-progress", listener);
    return () => ipcRenderer.removeListener("voice:install-progress", listener);
  },
  brainLogin: () => ipcRenderer.invoke("brain:login"),
  brainLoginPoll: () => ipcRenderer.invoke("brain:login-poll"),
  licenseGet: () => ipcRenderer.invoke("license:get"),
  licenseActivate: (key) => ipcRenderer.invoke("license:activate", key),
  engineGet: () => ipcRenderer.invoke("mirror:engine-get"),
  engineRetry: () => ipcRenderer.invoke("mirror:engine-retry"),
  brainstemSetUrl: (url) => ipcRenderer.invoke("mirror:brainstem-set-url", url),
  onEngineState: (cb) => {
    const listener = (_e, state) => cb(state);
    ipcRenderer.on("mirror:engine-state", listener);
    return () => ipcRenderer.removeListener("mirror:engine-state", listener);
  },
  onSurgeonEvent: (cb) => {
    const listener = (_e, ev) => cb(ev);
    ipcRenderer.on("surgeon:event", listener);
    return () => ipcRenderer.removeListener("surgeon:event", listener);
  },
  rehearseStart: (spec, sessionId) => ipcRenderer.invoke("rehearse:start", spec, sessionId),
  rehearseDecide: (specName, verdict, note, method) =>
    ipcRenderer.invoke("rehearse:decide", specName, verdict, note, method),
  rehearseStatus: (specName) => ipcRenderer.invoke("rehearse:status", specName),
  onRehearsalEvent: (cb) => {
    const listener = (_e, ev) => cb(ev);
    ipcRenderer.on("rehearse:event", listener);
    return () => ipcRenderer.removeListener("rehearse:event", listener);
  },
  // An agent arrived by AirDrop or a scanned card. Inspection only — the
  // renderer decides nothing; accepting is a separate, explicit call.
  onAgentArrived: (cb) => {
    const listener = (_e, received) => cb(received);
    ipcRenderer.on("mirror:agent-arrived", listener);
    return () => ipcRenderer.removeListener("mirror:agent-arrived", listener);
  },
  acceptArrival: (spec, opts) => ipcRenderer.invoke("mirror:accept-arrival", spec, opts),
});
