import { mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

import { createLogger } from "./logger.ts";

/**
 * Tiny main-process settings store — <dir>/settings.json — for the handful of
 * user preferences that must outlive a run (today: the brainstem URL override
 * set from the status panel). Same shape as sessionstore: loaded lazily once,
 * cached, persisted synchronously (tmp + rename) on every mutation.
 *
 * Env override (also used by tests): `MIRROR_SETTINGS_DIR`. When set the store
 * never touches Electron, so plain-node unit tests can exercise it.
 */

const log = createLogger("Settings");

interface MirrorSettings {
  /** User-set brainstem URL ("" = unset; env RAPP_BRAINSTEM_URL still wins). */
  brainstemUrl?: string;
}

function storeDir(): string {
  const envDir = process.env.MIRROR_SETTINGS_DIR;
  if (envDir) return envDir;
  // Lazy on purpose: only the running app reaches this branch, so importing
  // "electron" here never happens under plain node.
  const { app } = createRequire(import.meta.url)("electron") as typeof import("electron");
  return app.getPath("userData");
}

function storeFile(): string {
  return path.join(storeDir(), "settings.json");
}

let cache: MirrorSettings | null = null;

function store(): MirrorSettings {
  if (cache !== null) return cache;
  try {
    const parsed: unknown = JSON.parse(readFileSync(storeFile(), "utf8"));
    cache = parsed && typeof parsed === "object" ? (parsed as MirrorSettings) : {};
  } catch {
    cache = {};
  }
  return cache;
}

function persist(): void {
  try {
    const file = storeFile();
    mkdirSync(path.dirname(file), { recursive: true });
    const tmp = `${file}.tmp`;
    writeFileSync(tmp, JSON.stringify(store(), null, 2));
    renameSync(tmp, file);
  } catch (err) {
    log.error("failed to persist settings:", err instanceof Error ? err.message : String(err));
  }
}

/** The saved brainstem URL override ("" when none). */
export function getBrainstemUrlOverride(): string {
  return (store().brainstemUrl ?? "").trim();
}

/** Save (or clear, with "") the brainstem URL override. */
export function setBrainstemUrlOverride(url: string): void {
  const trimmed = url.trim();
  if (trimmed) store().brainstemUrl = trimmed;
  else delete store().brainstemUrl;
  persist();
}

/** Test seam: forget the cached settings so env overrides take effect. */
export function resetSettingsCacheForTests(): void {
  cache = null;
}
