import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { verifyKey } from "./license-verify.ts";

test("garbage keys are rejected", () => {
  assert.equal(verifyKey("").ok, false);
  assert.equal(verifyKey("not-a-key").ok, false);
  assert.equal(verifyKey("RAPPM1.YWJj.ZGVm").ok, false); // bad signature
  assert.equal(verifyKey("WRONG1.YWJj.ZGVm").ok, false); // bad magic
});

test("a tampered payload fails verification", () => {
  const fake = Buffer.from(JSON.stringify({ email: "x@y.z", plan: "pro" })).toString("base64url");
  assert.equal(verifyKey(`RAPPM1.${fake}.${Buffer.alloc(64).toString("base64url")}`).ok, false);
});

test("a freshly minted key verifies (skipped when no signing key on this machine)", (t) => {
  const keyPath = path.join(os.homedir(), ".rapp-mirror", "license-signing.private.pem");
  if (!existsSync(keyPath)) return t.skip("no local signing key");
  const minted = execFileSync("node", ["tools/make-license.mjs", "test@rapp.dev", "pro"], {
    cwd: path.join(import.meta.dirname, ".."),
    encoding: "utf8",
  }).trim();
  const v = verifyKey(minted);
  assert.equal(v.ok, true);
  assert.equal(v.email, "test@rapp.dev");
  assert.equal(v.plan, "pro");
});
