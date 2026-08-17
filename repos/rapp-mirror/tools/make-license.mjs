#!/usr/bin/env node
// Mint a RAPP Mirror license key after a sale:
//   node tools/make-license.mjs kody@example.com pro
// Signs with the PRIVATE key at ~/.rapp-mirror/license-signing.private.pem
// (or LICENSE_SIGNING_KEY env path) — that file must never enter any repo.
import { createPrivateKey, sign } from "node:crypto";
import { readFileSync } from "node:fs";
import os from "node:os";

const [email, plan = "pro"] = process.argv.slice(2);
if (!email) {
  console.error("usage: node tools/make-license.mjs <email> [plan]");
  process.exit(2);
}
const keyPath = process.env.LICENSE_SIGNING_KEY || `${os.homedir()}/.rapp-mirror/license-signing.private.pem`;
const privateKey = createPrivateKey(readFileSync(keyPath, "utf8"));
const payload = Buffer.from(JSON.stringify({ email, plan, issued: new Date().toISOString().slice(0, 10) }));
const sig = sign(null, payload, privateKey);
console.log(`RAPPM1.${payload.toString("base64url")}.${sig.toString("base64url")}`);
