import { mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { createRequire } from "node:module";
import path from "node:path";

import type { MirrorSession, SessionPatch } from "../common/ipc.ts";
import { createLogger } from "./logger.ts";

/**
 * Main-process store for concurrent conversations (the vBrainstem side-chat
 * pattern). One JSON file — <dir>/sessions.json — shared by every window;
 * loaded lazily once, cached in memory, persisted synchronously (tmp + rename)
 * on every mutation so a crash never loses more than the in-flight write.
 *
 * Env override (also used by tests): `MIRROR_SESSIONS_DIR`. When it is set the
 * store never touches Electron, so plain-node unit tests can exercise it;
 * otherwise the dir is Electron's userData path, resolved lazily on first use.
 */

const log = createLogger("Sessions");

const UNTITLED = "New conversation";
const TITLE_MAX = 40;

/** Where sessions.json lives (env override first — keeps tests Electron-free). */
function storeDir(): string {
  const envDir = process.env.MIRROR_SESSIONS_DIR;
  if (envDir) return envDir;
  // Lazy on purpose: only the running app reaches this branch, so importing
  // "electron" here never happens under plain node.
  const { app } = createRequire(import.meta.url)("electron") as typeof import("electron");
  return app.getPath("userData");
}

function storeFile(): string {
  return path.join(storeDir(), "sessions.json");
}

let cache: MirrorSession[] | null = null;

/** Monotonic Date.now() so back-to-back mutations still order deterministically. */
let lastStamp = 0;
function stamp(): number {
  lastStamp = Math.max(Date.now(), lastStamp + 1);
  return lastStamp;
}

/** The in-memory store, loading sessions.json on first touch (corrupt or
 *  missing file -> empty store, never throw). */
function store(): MirrorSession[] {
  if (cache !== null) return cache;
  try {
    const parsed: unknown = JSON.parse(readFileSync(storeFile(), "utf8"));
    cache = Array.isArray(parsed) ? (parsed as MirrorSession[]) : [];
  } catch {
    cache = [];
  }
  return cache;
}

/** Write-through (atomic-ish: tmp file then rename). Persist failures are
 *  logged, not thrown — the in-memory store stays authoritative for the run. */
function persist(): void {
  try {
    const file = storeFile();
    mkdirSync(path.dirname(file), { recursive: true });
    const tmp = `${file}.tmp`;
    writeFileSync(tmp, JSON.stringify(store(), null, 2));
    renameSync(tmp, file);
  } catch (err) {
    log.error("failed to persist sessions:", err instanceof Error ? err.message : String(err));
  }
}

/** All sessions, newest updatedAt first. */
export function listSessions(): MirrorSession[] {
  return [...store()].sort((a, b) => b.updatedAt - a.updatedAt);
}

/** Create (and persist) a fresh, empty session; returns it. */
export function createSession(): MirrorSession {
  const now = stamp();
  const session: MirrorSession = {
    id: randomUUID(),
    title: UNTITLED,
    createdAt: now,
    updatedAt: now,
    history: [],
    lastSaid: "",
  };
  store().push(session);
  persist();
  return session;
}

/**
 * Merge a patch over a stored session (unknown id -> null). Bumps updatedAt.
 * Auto-title: a session still called "New conversation" whose history gained
 * its first user turn takes that turn's first ~40 chars as its title.
 */
export function updateSession(patch: SessionPatch): MirrorSession | null {
  const session = store().find((s) => s.id === patch.id);
  if (!session) return null;
  if (patch.title !== undefined) session.title = patch.title;
  if (patch.history !== undefined) session.history = patch.history;
  if (patch.lastSaid !== undefined) session.lastSaid = patch.lastSaid;
  if (session.title === UNTITLED) {
    const firstUser = session.history.find((t) => t.role === "user" && t.content.trim());
    if (firstUser) session.title = firstUser.content.trim().slice(0, TITLE_MAX).trim();
  }
  session.updatedAt = stamp();
  persist();
  return session;
}

/** Remove a session (unknown id is a no-op). */
export function deleteSession(id: string): void {
  const sessions = store();
  const idx = sessions.findIndex((s) => s.id === id);
  if (idx < 0) return;
  sessions.splice(idx, 1);
  persist();
}

/** Test seam: forget the cached store so env overrides take effect. */
export function resetStoreCacheForTests(): void {
  cache = null;
}
