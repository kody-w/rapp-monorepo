import path from "node:path";
import { fileURLToPath } from "node:url";

import { app, desktopCapturer, session } from "electron";

import { receiveAgentCard, receiveAgentFile } from "./agentshare.ts";
import { announceArrival } from "./arrival.ts";
import { startControlServer, stopControlServer } from "./control.ts";
import { registerIpc, runEngine } from "./ipc.ts";
import { createLogger } from "./logger.ts";
import { ensureWhisperService, stopWhisperService } from "./stt-install.ts";
import { ensureVoiceService, stopVoiceService } from "./voice.ts";
import { createMirrorWindow, mirrorWindow } from "./window.ts";

const log = createLogger("Main");

app.on("open-file", (event, filePath) => {
  event.preventDefault();
  announceArrival(receiveAgentFile(filePath));
});

app.on("open-url", (event, url) => {
  event.preventDefault();
  announceArrival(receiveAgentCard(url));
});

// The mirror speaks without user gestures (reflections, mirrorctl, CDP) —
// playback and its wave metering must never wait on an autoplay gesture.
app.commandLine.appendSwitch("autoplay-policy", "no-user-gesture-required");
const dirname = path.dirname(fileURLToPath(import.meta.url));
/** Repo root in dev; resources dir in a packaged app. */
const appRoot = path.join(dirname, "..");

// One mirror per machine: a second instance would fight over the control port
// and the brainstem agents directory. Hand its arriving agent to the first.
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", (_event, argv) => {
    const window = mirrorWindow();
    if (window) {
      if (window.isMinimized()) window.restore();
      window.focus();
    }
    const arriving = argv.find((a) => a.startsWith("rapp://") || a.endsWith(".py"));
    if (arriving) {
      announceArrival(
        arriving.startsWith("rapp://") ? receiveAgentCard(arriving) : receiveAgentFile(arriving),
      );
    }
  });
}

void app.whenReady().then(async () => {
  app.setAsDefaultProtocolClient("rapp");
  registerIpc();
  startControlServer();

  // Screen watching without a picker: hand getDisplayMedia the primary screen
  // directly — the no-look ethos applied to permission ceremony.
  session.defaultSession.setDisplayMediaRequestHandler((_request, callback) => {
    desktopCapturer
      .getSources({ types: ["screen"] })
      .then((sources) => callback(sources.length ? { video: sources[0] } : {}))
      .catch(() => callback({}));
  });

  await ensureVoiceService(appRoot);
  void ensureWhisperService();
  createMirrorWindow();
  log.info("mirror up");

  // Engine of record: the global brainstem. Never blocks the window — the
  // status panel narrates state while an install (if any) runs. ONE call:
  // concurrent provisioning runs must never race two installers.
  void runEngine().then((v) =>
    v.phase === "ready" ? log.info("engine ready:", v.url) : log.warn("engine:", v.detail ?? v.phase),
  );

  app.on("activate", () => {
    if (app.isReady() && !app.hasSingleInstanceLock()) return;
  });
});

app.on("window-all-closed", () => {
  stopVoiceService();
  stopControlServer();
  app.quit();
});

app.on("before-quit", () => {
  stopVoiceService();
  stopWhisperService();
  stopControlServer();
});
