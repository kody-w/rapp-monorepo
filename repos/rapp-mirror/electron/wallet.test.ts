import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import path from "node:path";
import test from "node:test";

import AdmZip from "adm-zip";

import { decodeShareUrl, encodeShareUrl } from "../common/agentshare.ts";
import type { ForgeSpecView } from "../common/ipc.ts";
import { buildWalletPass } from "./wallet.ts";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const SPEC: ForgeSpecView = {
  name: "submit-weekly-expenses",
  className: "SubmitWeeklyExpenses",
  title: "Submit weekly expenses",
  description: "Files the week's expense report from receipts.",
  intent: "Submit every pending expense receipt as one weekly report.",
  steps: [
    { title: "Collect receipts", detail: "Gather all receipts for the week." },
    { title: "File report", detail: "Create and submit the expense report." },
  ],
  parameters: [
    { name: "week", description: "ISO week to file", type: "string", required: true },
    { name: "dry_run", description: "Preview without submitting", type: "boolean", required: false },
  ],
};

const SIGNING_ENV = [
  "RAPP_WALLET_CERT",
  "RAPP_WALLET_KEY",
  "RAPP_WALLET_WWDR",
  "RAPP_WALLET_KEY_PASSWORD",
] as const;

function setupWalletTest(t: { after: (fn: () => void) => void }): string {
  const root = mkdtempSync(path.join(process.cwd(), ".wallet-test-"));
  const previousExports = process.env.RAPP_MIRROR_EXPORTS;
  const previousSigning = new Map<string, string | undefined>(
    SIGNING_ENV.map((name) => [name, process.env[name]]),
  );
  process.env.RAPP_MIRROR_EXPORTS = root;
  for (const name of SIGNING_ENV) delete process.env[name];
  t.after(() => {
    if (previousExports === undefined) delete process.env.RAPP_MIRROR_EXPORTS;
    else process.env.RAPP_MIRROR_EXPORTS = previousExports;
    for (const [name, value] of previousSigning) {
      if (value === undefined) delete process.env[name];
      else process.env[name] = value;
    }
    rmSync(root, { recursive: true, force: true });
  });
  return root;
}

async function builtEntries(t: { after: (fn: () => void) => void }, spec: ForgeSpecView = SPEC) {
  setupWalletTest(t);
  const result = await buildWalletPass(spec);
  assert.equal(result.ok, true, result.error);
  assert.ok(result.path);
  assert.equal(existsSync(result.path), true);
  const zip = new AdmZip(readFileSync(result.path));
  const entries = new Map(zip.getEntries().map((entry) => [entry.entryName, entry.getData()]));
  return { result, entries };
}

function chunkTypes(png: Buffer): string[] {
  const types: string[] = [];
  let offset = PNG_MAGIC.length;
  while (offset + 12 <= png.length) {
    const length = png.readUInt32BE(offset);
    const type = png.subarray(offset + 4, offset + 8).toString("ascii");
    types.push(type);
    offset += 12 + length;
    if (type === "IEND") break;
  }
  return types;
}

test("wallet pass bundle is produced as a readable zip with required files", async (t) => {
  const { entries } = await builtEntries(t);
  for (const name of [
    "pass.json",
    "manifest.json",
    "icon.png",
    "icon@2x.png",
    "logo.png",
    "logo@2x.png",
  ]) {
    assert.ok(entries.has(name), `missing ${name}`);
  }
});

test("manifest lists every bundled payload file and each sha1 matches", async (t) => {
  const { entries } = await builtEntries(t);
  const manifest = JSON.parse(entries.get("manifest.json")!.toString("utf8")) as Record<string, string>;
  const expected = [...entries.keys()].filter((name) => name !== "manifest.json").sort();
  assert.deepEqual(Object.keys(manifest).sort(), expected);
  for (const name of expected) {
    assert.equal(createHash("sha1").update(entries.get(name)!).digest("hex"), manifest[name]);
  }
});

test("pass.json carries the exact encoded share URL as its QR barcode", async (t) => {
  const { entries } = await builtEntries(t);
  const pass = JSON.parse(entries.get("pass.json")!.toString("utf8"));
  assert.equal(pass.formatVersion, 1);
  assert.equal(pass.barcodes[0].message, encodeShareUrl(SPEC).url);
});

test("barcode message decodes back into the original forged spec", async (t) => {
  const { entries } = await builtEntries(t);
  const pass = JSON.parse(entries.get("pass.json")!.toString("utf8"));
  const decoded = decodeShareUrl(pass.barcodes[0].message);
  assert.equal(decoded.ok, true, decoded.error);
  assert.deepEqual(decoded.spec, SPEC);
});

test("serial number is stable for the same spec and differs for a changed spec", async (t) => {
  setupWalletTest(t);
  const first = await buildWalletPass(SPEC);
  const second = await buildWalletPass(SPEC);
  const changed = await buildWalletPass({ ...SPEC, title: "Submit monthly expenses" });
  assert.equal(first.ok, true, first.error);
  assert.equal(second.ok, true, second.error);
  assert.equal(changed.ok, true, changed.error);
  assert.equal(first.serialNumber, second.serialNumber);
  assert.notEqual(first.serialNumber, changed.serialNumber);
});

test("without certificate env the unsigned bundle is still produced with honest next action", async (t) => {
  setupWalletTest(t);
  const result = await buildWalletPass(SPEC);
  assert.equal(result.ok, true, result.error);
  assert.equal(result.signed, false);
  assert.equal(result.installable, false);
  assert.ok(result.path);
  assert.equal(existsSync(result.path), true);
  assert.match(result.nextAction ?? "", /Pass Type ID certificate/);
});

test("generated PNGs have PNG magic bytes and IHDR/IEND chunks", async (t) => {
  const { entries } = await builtEntries(t);
  for (const name of ["icon.png", "icon@2x.png", "logo.png", "logo@2x.png"]) {
    const png = entries.get(name)!;
    assert.deepEqual(png.subarray(0, PNG_MAGIC.length), PNG_MAGIC, `${name} magic`);
    const chunks = chunkTypes(png);
    assert.equal(chunks[0], "IHDR", `${name} first chunk`);
    assert.equal(chunks.at(-1), "IEND", `${name} final chunk`);
  }
});

test("pass colours are well-formed rgb strings", async (t) => {
  const { entries } = await builtEntries(t);
  const pass = JSON.parse(entries.get("pass.json")!.toString("utf8"));
  for (const key of ["foregroundColor", "backgroundColor", "labelColor"]) {
    assert.match(pass[key], /^rgb\((?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]), (?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]), (?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\)$/);
  }
});

test("oversized QR specs fail gracefully without an empty-barcode pass", async (t) => {
  const root = setupWalletTest(t);
  const noisy = Array.from({ length: 260 }, (_, i) =>
    createHash("sha256").update(`wallet-pass-too-large-${i}`).digest("hex"),
  ).join("");
  const result = await buildWalletPass({
    ...SPEC,
    name: "too-large-wallet-pass",
    steps: [{ title: "Carry too much", detail: noisy }],
  });
  assert.equal(result.ok, false);
  assert.equal(result.signed, false);
  assert.equal(result.installable, false);
  assert.match(`${result.error} ${result.nextAction}`, /QR|too detailed|Shorten/i);
  assert.equal(existsSync(path.join(root, "too-large-wallet-pass", "too-large-wallet-pass.pkpass")), false);
});
