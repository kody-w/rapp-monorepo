import { createPublicKey, verify as edVerify } from "node:crypto";

/** Pure, Electron-free license verification (unit-testable anywhere). Keys:
 *  `RAPPM1.<base64url payload>.<base64url ed25519 signature>` where payload is
 *  {"email","plan","issued"}, minted by tools/make-license.mjs. */

export const PUBLIC_KEY_PEM = `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEACQAKB+e7lQngDwrRy2WLqmYPTlc+IfDz0ZIqOrmXCPI=
-----END PUBLIC KEY-----`;

export function verifyKey(key: string): { ok: boolean; email?: string; plan?: string } {
  try {
    const [magic, payloadB64, sigB64] = key.trim().split(".");
    if (magic !== "RAPPM1" || !payloadB64 || !sigB64) return { ok: false };
    const payload = Buffer.from(payloadB64, "base64url");
    const sig = Buffer.from(sigB64, "base64url");
    const ok = edVerify(null, payload, createPublicKey(PUBLIC_KEY_PEM), sig);
    if (!ok) return { ok: false };
    const data = JSON.parse(payload.toString("utf8")) as { email?: string; plan?: string };
    return { ok: true, email: data.email, plan: data.plan };
  } catch {
    return { ok: false };
  }
}
