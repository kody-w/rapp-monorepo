import { existsSync, readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import type { BrainstemHealth, ChatResult, ChatTurn } from "../common/ipc.ts";
import { createLogger } from "./logger.ts";
import { getBrainstemUrlOverride } from "./settings.ts";

/**
 * Main-process client for the mirror's engine: the GLOBAL RAPP brainstem
 * (the grail install at ~/.brainstem, serving :7071 — see engine.ts). Running
 * in the main process means no CORS and direct access to the per-install
 * `X-Brainstem-Secret` — it never travels through the renderer.
 *
 * Env overrides (also used by tests): `RAPP_BRAINSTEM_URL`,
 * `BRAINSTEM_SECRET_FILE`.
 */

const log = createLogger("Brainstem");

const CHAT_TIMEOUT_MS = 120_000;
const HEALTH_TIMEOUT_MS = 5_000;

export function brainstemUrl(): string {
  return (
    process.env.RAPP_BRAINSTEM_URL ||
    getBrainstemUrlOverride() ||
    "http://127.0.0.1:7071"
  ).replace(/\/$/, "");
}

function secretFile(): string {
  return (
    process.env.BRAINSTEM_SECRET_FILE ||
    path.join(os.homedir(), ".brainstem", "src", "rapp_brainstem", ".brainstem_secret")
  );
}

let cachedSecret: string | null = null;

/** The per-install secret, read once (missing file -> empty string). */
export function brainstemSecret(): string {
  if (cachedSecret !== null) return cachedSecret;
  try {
    cachedSecret = existsSync(secretFile()) ? readFileSync(secretFile(), "utf8").trim() : "";
  } catch {
    cachedSecret = "";
  }
  if (!cachedSecret) log.warn("no brainstem secret found at", secretFile());
  return cachedSecret;
}

/** Test seam: forget the cached secret so env overrides take effect. */
export function resetSecretCache(): void {
  cachedSecret = null;
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const secret = brainstemSecret();
  if (secret) h["X-Brainstem-Secret"] = secret;
  return h;
}

const msg = (err: unknown) => (err instanceof Error ? err.message : String(err));

export async function health(): Promise<BrainstemHealth> {
  try {
    const r = await fetch(`${brainstemUrl()}/health`, {
      headers: headers(),
      signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
    });
    const data = (await r.json()) as Record<string, unknown>;
    return {
      ok: r.ok,
      status: data.status as string | undefined,
      version: data.version as string | undefined,
      model: data.model as string | undefined,
      agents: (data.agents as string[] | undefined) ?? [],
      quarantined: (data.quarantined as string[] | undefined) ?? [],
      error: data.error as string | undefined,
    };
  } catch (err) {
    return { ok: false, error: msg(err) };
  }
}

/** POST /chat — the brainstem answers in the `response` field (rapp-chat). */
export async function chat(
  userInput: string,
  history: ChatTurn[],
  sessionId: string,
): Promise<ChatResult> {
  try {
    const r = await fetch(`${brainstemUrl()}/chat`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        user_input: userInput,
        conversation_history: history,
        session_id: sessionId,
      }),
      signal: AbortSignal.timeout(CHAT_TIMEOUT_MS),
    });
    const data = (await r.json()) as Record<string, unknown>;
    if (!r.ok || data.error) {
      return { ok: false, error: (data.error as string) || `HTTP ${r.status}` };
    }
    return {
      ok: true,
      response: String(data.response ?? ""),
      agentLogs: (data.agent_logs as string) || "",
      model: (data.model as string) || "",
    };
  } catch (err) {
    return { ok: false, error: msg(err) };
  }
}


/** Start the brainstem's GitHub device-code login (fresh installs). */
export async function loginStart(): Promise<{ ok: boolean; userCode?: string; url?: string; error?: string }> {
  try {
    const r = await fetch(`${brainstemUrl()}/login`, { method: "POST", headers: headers(), signal: AbortSignal.timeout(10_000) });
    const d = (await r.json()) as Record<string, unknown>;
    if (!r.ok) return { ok: false, error: String(d.error ?? r.status) };
    return { ok: true, userCode: String(d.user_code ?? ""), url: String(d.verification_uri ?? "https://github.com/login/device") };
  } catch (err) {
    return { ok: false, error: msg(err) };
  }
}

/** Poll the device-code flow; ok=true when authenticated. */
export async function loginPoll(): Promise<{ ok: boolean; status: string }> {
  try {
    const r = await fetch(`${brainstemUrl()}/login/poll`, { method: "POST", headers: headers(), signal: AbortSignal.timeout(10_000) });
    const d = (await r.json()) as { status?: string };
    return { ok: d.status === "ok" || d.status === "success", status: d.status ?? "pending" };
  } catch (err) {
    return { ok: false, status: msg(err) };
  }
}
