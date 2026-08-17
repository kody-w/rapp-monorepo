import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { type AgentCard, cardSummary, inspectAgentSource } from "../common/agentcard.ts";
import { decodeShareUrl, encodeShareUrl } from "../common/agentshare.ts";
import type { ForgeSpecView } from "../common/ipc.ts";
import { deployAgent, exportAll, normalizeSpec, renderAgentPy } from "./forge.ts";
import { createLogger } from "./logger.ts";

/**
 * Trading agents.
 *
 * An agent you can hand to someone is the thing that compounds: forge one,
 * AirDrop it or show its card's QR, and it hot-loads into their brainstem.
 *
 * But a file that hot-loads is a file that executes, so nothing here installs
 * anything on arrival. A received agent becomes a *card* — parsed, capability-
 * scanned, and held — and only an explicit human `accept` moves it into the
 * brainstem, through the same verified, atomic, rehearsal-gated deploy path
 * everything else uses.
 *
 * Two ways in, with different trust:
 *   • a `.py` file (AirDrop, Downloads, open-with) — real code, so it is
 *     scanned and shown before anything happens;
 *   • a `rapp://agent?…` link (a scanned card) — carries only the *spec*, and
 *     the code is re-rendered locally by our own Forge, so it cannot smuggle
 *     anything in at all.
 */

const log = createLogger("Share");

export function inboxDir(): string {
  return (
    process.env.RAPP_MIRROR_INBOX ||
    path.join(process.env.RAPP_MIRROR_HOME || path.join(os.homedir(), ".rapp-mirror"), "inbox")
  );
}

export interface ReceivedAgent {
  ok: boolean;
  /** How it arrived — decides how much we trust it. */
  origin: "file" | "card";
  card?: AgentCard;
  /** One line a human reads before deciding. */
  summary?: string;
  /** Present for card arrivals: the spec we would render locally. */
  spec?: ForgeSpecView;
  /** Where the pending agent is parked until someone accepts it. */
  pendingPath?: string;
  /** True when the mirror will refuse to install without an explicit override. */
  dangerous?: boolean;
  /** The card's link, computed here so the renderer never needs node:zlib. */
  shareUrl?: string;
  error?: string;
}

const safeName = (raw: string): string =>
  (raw || "agent").toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) ||
  "agent";

/** Park a received agent in the inbox. Never inside the brainstem. */
function park(name: string, source: string): string {
  const dir = inboxDir();
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${safeName(name)}_agent.py`);
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, source);
  renameSync(tmp, file);
  return file;
}

/** Someone AirDropped a file. Read it, scan it, show it — install nothing. */
export function receiveAgentFile(filePath: string): ReceivedAgent {
  try {
    if (!existsSync(filePath)) {
      return { ok: false, origin: "file", error: `no such file: ${filePath}` };
    }
    const source = readFileSync(filePath, "utf8");
    const card = inspectAgentSource(source);
    if (!card.ok) {
      return { ok: false, origin: "file", card, error: card.error };
    }
    const pendingPath = park(card.name || card.className, source);
    log.info("received", card.className, `(${card.verdict})`, "->", pendingPath);
    return {
      ok: true,
      origin: "file",
      card,
      summary: cardSummary(card),
      pendingPath,
      dangerous: card.verdict === "dangerous",
    };
  } catch (err) {
    return { ok: false, origin: "file", error: err instanceof Error ? err.message : String(err) };
  }
}

/** Someone scanned a card. The link carries a spec, so we render the code
 *  ourselves — a scanned card can never contain someone else's Python. */
export function receiveAgentCard(url: string): ReceivedAgent {
  const decoded = decodeShareUrl(url);
  if (!decoded.ok || !decoded.spec) {
    return { ok: false, origin: "card", error: decoded.error };
  }
  const spec = normalizeSpec({ ...decoded.spec });
  const source = renderAgentPy(spec);
  const card = inspectAgentSource(source);
  if (!card.ok) {
    return { ok: false, origin: "card", card, error: card.error };
  }
  const pendingPath = park(spec.name, source);
  log.info("scanned card", spec.className, `(${card.verdict})`, "->", pendingPath);
  return {
    ok: true,
    origin: "card",
    card,
    spec,
    summary: cardSummary(card),
    pendingPath,
    dangerous: card.verdict === "dangerous",
    shareUrl: encodeShareUrl(spec).url,
  };
}

export interface AcceptResult {
  ok: boolean;
  installed?: boolean;
  path?: string;
  verified?: boolean;
  needsRehearsal?: boolean;
  /** Set when a dangerous agent was refused without an explicit override. */
  refused?: boolean;
  error?: string;
}

/**
 * Accept a pending agent into the brainstem.
 *
 * This is the only door, and it is deliberately narrow: a dangerous card is
 * refused unless the caller explicitly says so, and everything else goes
 * through `deployAgent()`, which renders, executes the artifact to prove it
 * runs, writes atomically, verifies `/health`, and rolls back on failure.
 */
export async function acceptAgent(
  spec: ForgeSpecView,
  opts: { acceptDangerous?: boolean; force?: boolean } = {},
): Promise<AcceptResult> {
  const normalized = normalizeSpec({ ...spec });
  const card = inspectAgentSource(renderAgentPy(normalized));
  if (card.verdict === "dangerous" && opts.acceptDangerous !== true) {
    return {
      ok: false,
      refused: true,
      error: `refused: ${cardSummary(card)} — accept it explicitly if you trust the sender`,
    };
  }
  const result = await deployAgent(normalized, { force: opts.force === true });
  return {
    ok: result.ok,
    installed: result.ok,
    path: result.path,
    verified: result.verified,
    needsRehearsal: result.needsRehearsal,
    error: result.error,
  };
}

export interface ShareResult {
  ok: boolean;
  /** The file to AirDrop. */
  agentPath?: string;
  /** The link a card's QR carries. */
  url?: string;
  /** Set when the agent is too detailed to travel as a code. */
  urlError?: string;
  dir?: string;
  error?: string;
}

/** Prepare an agent to be handed to someone: a file to AirDrop and a link to
 *  put on the card's back. The link is best-effort — a very detailed agent
 *  simply travels as a file instead. */
export function shareAgent(spec: ForgeSpecView): ShareResult {
  try {
    const normalized = normalizeSpec({ ...spec });
    const exported = exportAll(normalized);
    const encoded = encodeShareUrl(normalized);
    return {
      ok: true,
      agentPath: exported.agentPath,
      dir: exported.dir,
      url: encoded.url,
      urlError: encoded.ok ? undefined : encoded.error,
    };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) };
  }
}
