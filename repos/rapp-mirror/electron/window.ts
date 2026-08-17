import path from "node:path";
import { fileURLToPath } from "node:url";

import { BrowserWindow, shell } from "electron";

const dirname = path.dirname(fileURLToPath(import.meta.url));

/** The main mirror window, once it exists — arriving agents need somewhere to
 *  be announced, and the main process must not guess at window identity. */
let main: BrowserWindow | null = null;

export function mirrorWindow(): BrowserWindow | null {
  return main && !main.isDestroyed() ? main : null;
}

/** The mirror window: one dark, chrome-light surface (skill-recorder idiom:
 *  dev server URL when Vite is driving, packaged file otherwise). */
export function createMirrorWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 960,
    minHeight: 640,
    backgroundColor: "#050809",
    titleBarStyle: process.platform === "darwin" ? "hiddenInset" : "default",
    webPreferences: {
      preload: path.join(dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  // Transcript links open in the system browser, never as popup windows.
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//.test(url)) void shell.openExternal(url);
    return { action: "deny" };
  });
  const devUrl = process.env.VITE_DEV_SERVER_URL;
  if (devUrl) {
    void win.loadURL(devUrl);
  } else {
    void win.loadFile(path.join(dirname, "..", "dist", "index.html"));
  }
  main = win;
  win.on("closed", () => {
    if (main === win) main = null;
  });
  return win;
}

/**
 * A popped-out sticky mirror: one session in a small, frameless, always-on-top
 * note that follows you across Spaces (darwin). Loads the SAME renderer entry
 * as the main window — `?session=<id>&sticky=1` tells it which conversation to
 * resume and to render the sticky chrome.
 */
export function createStickyWindow(sessionId: string): BrowserWindow {
  const win = new BrowserWindow({
    width: 340,
    height: 430,
    minWidth: 260,
    minHeight: 300,
    frame: false,
    resizable: true,
    backgroundColor: "#f3f2f9",
    webPreferences: {
      preload: path.join(dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.setAlwaysOnTop(true, "floating");
  if (process.platform === "darwin") {
    win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  }
  const devUrl = process.env.VITE_DEV_SERVER_URL;
  if (devUrl) {
    const url = new URL(devUrl);
    url.searchParams.set("session", sessionId);
    url.searchParams.set("sticky", "1");
    void win.loadURL(url.toString());
  } else {
    void win.loadFile(path.join(dirname, "..", "dist", "index.html"), {
      query: { session: sessionId, sticky: "1" },
    });
  }
  return win;
}
