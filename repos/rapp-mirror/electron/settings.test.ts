import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { brainstemUrl } from "./brainstem.ts";
import {
  getBrainstemUrlOverride,
  resetSettingsCacheForTests,
  setBrainstemUrlOverride,
} from "./settings.ts";

function freshDir(): string {
  const dir = mkdtempSync(path.join(os.tmpdir(), "mirror-settings-"));
  process.env.MIRROR_SETTINGS_DIR = dir;
  resetSettingsCacheForTests();
  return dir;
}

test("override round-trips and persists to disk", () => {
  const dir = freshDir();
  assert.equal(getBrainstemUrlOverride(), "");
  setBrainstemUrlOverride("http://10.0.0.5:7071");
  assert.equal(getBrainstemUrlOverride(), "http://10.0.0.5:7071");
  // Survives a cache reset — i.e. it actually landed on disk.
  resetSettingsCacheForTests();
  assert.equal(getBrainstemUrlOverride(), "http://10.0.0.5:7071");
  assert.match(readFileSync(path.join(dir, "settings.json"), "utf8"), /10\.0\.0\.5/);
});

test("empty string clears the override", () => {
  freshDir();
  setBrainstemUrlOverride("http://10.0.0.5:7071");
  setBrainstemUrlOverride("");
  assert.equal(getBrainstemUrlOverride(), "");
  resetSettingsCacheForTests();
  assert.equal(getBrainstemUrlOverride(), "");
});

test("brainstemUrl precedence: env > saved override > default", () => {
  freshDir();
  const prev = process.env.RAPP_BRAINSTEM_URL;
  try {
    delete process.env.RAPP_BRAINSTEM_URL;
    assert.equal(brainstemUrl(), "http://127.0.0.1:7071");

    setBrainstemUrlOverride("http://10.0.0.5:9999/");
    assert.equal(brainstemUrl(), "http://10.0.0.5:9999", "override wins over default, trailing slash stripped");

    process.env.RAPP_BRAINSTEM_URL = "http://127.0.0.1:4444";
    assert.equal(brainstemUrl(), "http://127.0.0.1:4444", "env always wins");
  } finally {
    if (prev === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prev;
  }
});
