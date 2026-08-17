import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

import { app } from "electron";

/**
 * Offline license gate: keys are Ed25519-signed JSON payloads minted by
 * tools/make-license.mjs (the private key lives OUTSIDE the repo at
 * ~/.rapp-mirror/license-signing.private.pem). A key looks like
 * `RAPPM1.<base64url payload>.<base64url signature>` where payload is
 * {"email","plan","issued"}. Verification is fully offline against the
 * embedded public key. First run starts a 14-day trial.
 */

import { verifyKey } from "./license-verify.ts";

const TRIAL_DAYS = 14;

export { verifyKey };

export interface LicenseState {
  status: "licensed" | "trial" | "expired";
  email?: string;
  plan?: string;
  trialDaysLeft?: number;
}

const stateFile = () => path.join(app.getPath("userData"), "license.json");

interface Stored {
  key?: string;
  firstRun?: number;
}

function readStored(): Stored {
  try {
    if (existsSync(stateFile())) return JSON.parse(readFileSync(stateFile(), "utf8")) as Stored;
  } catch {
    /* corrupted store — treat as fresh */
  }
  return {};
}

function writeStored(s: Stored): void {
  writeFileSync(stateFile(), JSON.stringify(s, null, 2));
}

/** Accept and persist a license key; returns the resulting state. */
export function activate(key: string): LicenseState {
  const v = verifyKey(key);
  if (!v.ok) return licenseState(); // unchanged
  const stored = readStored();
  writeStored({ ...stored, key: key.trim() });
  return { status: "licensed", email: v.email, plan: v.plan };
}

export function licenseState(): LicenseState {
  const stored = readStored();
  if (stored.key) {
    const v = verifyKey(stored.key);
    if (v.ok) return { status: "licensed", email: v.email, plan: v.plan };
  }
  if (!stored.firstRun) {
    writeStored({ ...stored, firstRun: Date.now() });
    return { status: "trial", trialDaysLeft: TRIAL_DAYS };
  }
  const used = (Date.now() - stored.firstRun) / 86_400_000;
  const left = Math.ceil(TRIAL_DAYS - used);
  return left > 0 ? { status: "trial", trialDaysLeft: left } : { status: "expired" };
}
