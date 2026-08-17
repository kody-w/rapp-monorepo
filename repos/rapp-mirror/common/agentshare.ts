import { deflateRawSync, inflateRawSync } from "node:zlib";

import type { ForgeSpecView } from "./ipc.ts";

/**
 * How an agent travels between people.
 *
 * A card's back carries a QR; a Wallet pass carries the same code; AirDrop
 * carries the file. In every case what moves is the **spec**, never the
 * rendered Python — the receiving mirror re-renders the agent locally with its
 * own trusted Forge. That is the whole security story of trading agents: a
 * scanned card cannot contain code, so it cannot contain an exploit.
 *
 * The wire form is deliberately tiny (single-letter keys, raw deflate,
 * base64url) so a real spec fits in a scannable QR.
 */

export const SHARE_SCHEME = "rapp";
export const SHARE_VERSION = 1;

/** QR capacity at version 40 / ECC-M is ~2331 bytes; stay well inside it. */
export const MAX_PAYLOAD_CHARS = 1800;

interface Packed {
  n: string;
  c: string;
  t: string;
  d: string;
  i: string;
  s: [string, string][];
  p: [string, string, string, 0 | 1][];
}

const base64url = (buf: Buffer): string =>
  buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

const unbase64url = (text: string): Buffer =>
  Buffer.from(text.replace(/-/g, "+").replace(/_/g, "/"), "base64");

function pack(spec: ForgeSpecView): Packed {
  return {
    n: spec.name,
    c: spec.className,
    t: spec.title,
    d: spec.description,
    i: spec.intent,
    s: (spec.steps ?? []).map((step) => [step.title, step.detail]),
    p: (spec.parameters ?? []).map((p) => [p.name, p.description, p.type, p.required ? 1 : 0]),
  };
}

function unpack(packed: Packed): ForgeSpecView {
  return {
    name: String(packed.n ?? ""),
    className: String(packed.c ?? ""),
    title: String(packed.t ?? ""),
    description: String(packed.d ?? ""),
    intent: String(packed.i ?? ""),
    steps: (packed.s ?? []).map(([title, detail]) => ({
      title: String(title ?? ""),
      detail: String(detail ?? ""),
    })),
    parameters: (packed.p ?? []).map(([name, description, type, required]) => ({
      name: String(name ?? ""),
      description: String(description ?? ""),
      type: String(type ?? "string"),
      required: required === 1,
    })),
  };
}

export interface EncodeResult {
  ok: boolean;
  url?: string;
  /** Payload length in characters, so a UI can show how close to the limit it is. */
  size?: number;
  error?: string;
}

/** Spec → a scannable, AirDroppable, Wallet-able link. */
export function encodeShareUrl(spec: ForgeSpecView): EncodeResult {
  try {
    const payload = base64url(deflateRawSync(Buffer.from(JSON.stringify(pack(spec)), "utf8"), { level: 9 }));
    if (payload.length > MAX_PAYLOAD_CHARS) {
      return {
        ok: false,
        size: payload.length,
        error: `this agent is too detailed to fit in a QR (${payload.length} of ${MAX_PAYLOAD_CHARS} characters) — AirDrop the file instead`,
      };
    }
    const name = encodeURIComponent(spec.name || spec.className || "agent");
    return {
      ok: true,
      size: payload.length,
      url: `${SHARE_SCHEME}://agent?v=${SHARE_VERSION}&n=${name}&d=${payload}`,
    };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) };
  }
}

export interface DecodeResult {
  ok: boolean;
  spec?: ForgeSpecView;
  error?: string;
}

/** A scanned or tapped link → the spec it carries. Never throws. */
export function decodeShareUrl(raw: string): DecodeResult {
  try {
    const text = (raw ?? "").trim();
    if (!text.startsWith(`${SHARE_SCHEME}://agent`)) {
      return { ok: false, error: "not a RAPP agent card" };
    }
    // `new URL` keeps custom-scheme query parsing consistent across platforms.
    const params = new URL(text.replace(`${SHARE_SCHEME}://`, "https://")).searchParams;
    const version = Number.parseInt(params.get("v") ?? "0", 10);
    if (version !== SHARE_VERSION) {
      return { ok: false, error: `this card was made by a newer mirror (format v${version})` };
    }
    const data = params.get("d");
    if (!data) return { ok: false, error: "the card carries no agent" };

    const json = inflateRawSync(unbase64url(data)).toString("utf8");
    const packed = JSON.parse(json) as Packed;
    if (!packed || typeof packed !== "object" || !packed.c) {
      return { ok: false, error: "the card's agent is unreadable" };
    }
    const spec = unpack(packed);
    if (!/^[A-Za-z_]\w*$/.test(spec.className)) {
      return { ok: false, error: "the card names an invalid agent class" };
    }
    return { ok: true, spec };
  } catch {
    return { ok: false, error: "the card is damaged or was not made by a mirror" };
  }
}
