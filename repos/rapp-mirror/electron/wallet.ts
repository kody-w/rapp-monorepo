import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { deflateSync } from "node:zlib";

import AdmZip from "adm-zip";

import type { AgentCard } from "../common/agentcard.ts";
import { encodeShareUrl } from "../common/agentshare.ts";
import { mintCard } from "../common/cardart.ts";
import type { ForgeSpecView } from "../common/ipc.ts";
import { createLogger } from "./logger.ts";

const log = createLogger("Wallet");
const execFileAsync = promisify(execFile);

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

export interface WalletPassResult {
  ok: boolean;
  signed: boolean;
  installable: boolean;
  path?: string;
  serialNumber?: string;
  shareUrl?: string;
  error?: string;
  nextAction?: string;
}

interface Rgb {
  r: number;
  g: number;
  b: number;
}

function exportsRoot(): string {
  return process.env.RAPP_MIRROR_EXPORTS || path.join(os.homedir(), "Documents", "rapp-mirror-exports");
}

function safeSegment(raw: string): string {
  return raw.replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "agent";
}

function canonicalSpec(spec: ForgeSpecView): string {
  return JSON.stringify({
    name: spec.name,
    className: spec.className,
    title: spec.title,
    description: spec.description,
    intent: spec.intent,
    steps: (spec.steps ?? []).map((s) => ({ title: s.title, detail: s.detail })),
    parameters: (spec.parameters ?? []).map((p) => ({
      name: p.name,
      description: p.description,
      type: p.type,
      required: p.required,
    })),
  });
}

function serialNumberFor(spec: ForgeSpecView): string {
  return `rapp-${createHash("sha256").update(canonicalSpec(spec), "utf8").digest("hex").slice(0, 32)}`;
}

function agentCardFor(spec: ForgeSpecView): AgentCard {
  return {
    ok: true,
    verdict: "safe",
    className: spec.className,
    name: spec.title || spec.name || spec.className,
    description: spec.description,
    parameters: (spec.parameters ?? []).map((p) => ({ name: p.name, description: p.description })),
    steps: (spec.steps ?? []).map((s, i) => `${i + 1}. ${s.title}: ${s.detail}`),
    findings: [],
    lineCount: 0,
  };
}

function clampByte(value: number): number {
  return Math.max(0, Math.min(255, Math.round(value)));
}

function hslToRgb(hue: number, saturation: number, lightness: number): Rgb {
  const h = ((hue % 360) + 360) % 360;
  const s = Math.max(0, Math.min(100, saturation)) / 100;
  const l = Math.max(0, Math.min(100, lightness)) / 100;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const hp = h / 60;
  const x = c * (1 - Math.abs((hp % 2) - 1));
  const [r1, g1, b1] =
    hp < 1 ? [c, x, 0] :
      hp < 2 ? [x, c, 0] :
        hp < 3 ? [0, c, x] :
          hp < 4 ? [0, x, c] :
            hp < 5 ? [x, 0, c] :
              [c, 0, x];
  const m = l - c / 2;
  return { r: clampByte((r1 + m) * 255), g: clampByte((g1 + m) * 255), b: clampByte((b1 + m) * 255) };
}

function colourToRgb(colour: string): Rgb {
  const hex = /^#?([0-9a-f]{6})$/i.exec(colour);
  if (hex) {
    const value = Number.parseInt(hex[1], 16);
    return { r: (value >> 16) & 0xff, g: (value >> 8) & 0xff, b: value & 0xff };
  }

  const hsl = /^hsl\(\s*([-+]?\d+(?:\.\d+)?)(?:deg)?[\s,]+([-+]?\d+(?:\.\d+)?)%[\s,]+([-+]?\d+(?:\.\d+)?)%\s*\)$/i.exec(colour);
  if (hsl) return hslToRgb(Number(hsl[1]), Number(hsl[2]), Number(hsl[3]));

  throw new Error(`invalid wallet colour ${colour}`);
}

function rgbString(colour: string): string {
  const { r, g, b } = colourToRgb(colour);
  return `rgb(${r}, ${g}, ${b})`;
}

function crcTable(): Uint32Array {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
}

const CRC = crcTable();

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const byte of buf) c = CRC[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function pngChunk(type: string, data = Buffer.alloc(0)): Buffer {
  const typeBuf = Buffer.from(type, "ascii");
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  typeBuf.copy(out, 4);
  data.copy(out, 8);
  out.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 8 + data.length);
  return out;
}

function solidPng(width: number, height: number, colour: Rgb): Buffer {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;

  const rowBytes = 1 + width * 4;
  const raw = Buffer.alloc(rowBytes * height);
  for (let y = 0; y < height; y++) {
    const row = y * rowBytes;
    raw[row] = 0;
    for (let x = 0; x < width; x++) {
      const px = row + 1 + x * 4;
      raw[px] = colour.r;
      raw[px + 1] = colour.g;
      raw[px + 2] = colour.b;
      raw[px + 3] = 0xff;
    }
  }

  return Buffer.concat([
    PNG_SIGNATURE,
    pngChunk("IHDR", ihdr),
    pngChunk("IDAT", deflateSync(raw)),
    pngChunk("IEND"),
  ]);
}

function buildPassJson(spec: ForgeSpecView, shareUrl: string, serialNumber: string) {
  const card = mintCard(agentCardFor(spec));
  return {
    formatVersion: 1,
    passTypeIdentifier: process.env.RAPP_WALLET_PASS_TYPE_ID || "pass.dev.rapp.mirror.placeholder",
    serialNumber,
    teamIdentifier: process.env.RAPP_WALLET_TEAM_ID || "RAPPTEAMID",
    organizationName: process.env.RAPP_WALLET_ORGANIZATION_NAME || "RAPP Mirror",
    description: spec.title,
    logoText: "RAPP Mirror",
    foregroundColor: rgbString(card.palette.ink),
    backgroundColor: rgbString(card.palette.from),
    labelColor: rgbString(card.palette.accent),
    barcodes: [
      {
        format: "PKBarcodeFormatQR",
        message: shareUrl,
        messageEncoding: "iso-8859-1",
        altText: spec.name,
      },
    ],
    generic: {
      primaryFields: [{ key: "agent", label: "AGENT", value: spec.title }],
      secondaryFields: [
        { key: "element", label: "ELEMENT", value: card.element },
        { key: "trust", label: "TRUST", value: `${card.trust} HP` },
      ],
      auxiliaryFields: [{ key: "dex", label: "DEX", value: card.dex }],
      backFields: [
        { key: "intent", label: "INTENT", value: spec.intent },
        ...(spec.steps ?? []).map((step, i) => ({
          key: `step-${i + 1}`,
          label: `STEP ${i + 1}: ${step.title}`,
          value: step.detail,
        })),
        ...(spec.parameters ?? []).map((param, i) => ({
          key: `param-${i + 1}-${safeSegment(param.name)}`,
          label: `PARAMETER: ${param.name}`,
          value: `${param.description} (${param.type}${param.required ? ", required" : ""})`,
        })),
      ],
    },
  };
}

function manifestFor(files: Map<string, Buffer>): Buffer {
  const manifest: Record<string, string> = {};
  for (const name of [...files.keys()].sort()) {
    manifest[name] = createHash("sha1").update(files.get(name)!).digest("hex");
  }
  return Buffer.from(JSON.stringify(manifest, null, 2), "utf8");
}

function missingSigningEnv(): string[] {
  return ["RAPP_WALLET_CERT", "RAPP_WALLET_KEY", "RAPP_WALLET_WWDR"].filter((name) => !process.env[name]);
}

function signingNextAction(missing: string[]): string {
  const prefix = missing.length ? `Missing ${missing.join(", ")}. ` : "";
  return `${prefix}To make an installable Apple Wallet pass, use an Apple Developer account to create a Pass Type ID certificate, export the certificate and private key as PEM, download/export the Apple WWDR intermediate as PEM, then set RAPP_WALLET_CERT, RAPP_WALLET_KEY, and RAPP_WALLET_WWDR${process.env.RAPP_WALLET_KEY_PASSWORD ? "" : " (plus RAPP_WALLET_KEY_PASSWORD if the key is encrypted)"}.`;
}

async function signManifest(dir: string, manifest: Buffer): Promise<Buffer> {
  const workDir = path.join(dir, ".wallet-signing");
  rmSync(workDir, { recursive: true, force: true });
  mkdirSync(workDir, { recursive: true });
  const manifestPath = path.join(workDir, "manifest.json");
  const signaturePath = path.join(workDir, "signature");
  writeFileSync(manifestPath, manifest);

  try {
    const args = [
      "smime",
      "-binary",
      "-sign",
      "-certfile",
      process.env.RAPP_WALLET_WWDR!,
      "-signer",
      process.env.RAPP_WALLET_CERT!,
      "-inkey",
      process.env.RAPP_WALLET_KEY!,
      "-in",
      manifestPath,
      "-out",
      signaturePath,
      "-outform",
      "DER",
    ];
    if (process.env.RAPP_WALLET_KEY_PASSWORD) args.push("-passin", "env:RAPP_WALLET_KEY_PASSWORD");
    await execFileAsync("openssl", args, { encoding: "utf8", timeout: 30_000 });
    if (!existsSync(signaturePath)) throw new Error("openssl did not create a signature file");
    return readFileSync(signaturePath);
  } finally {
    rmSync(workDir, { recursive: true, force: true });
  }
}

/**
 * Build a Wallet pass even when the private Apple signing material is absent.
 * Unsigned bundles are useful evidence for QA, but iOS refuses them; the result
 * reports installability separately so the UI never promises an unverified pass.
 */
export async function buildWalletPass(
  spec: ForgeSpecView,
  opts: { outDir?: string } = {},
): Promise<WalletPassResult> {
  const share = encodeShareUrl(spec);
  if (!share.ok || !share.url) {
    return {
      ok: false,
      signed: false,
      installable: false,
      error: share.error || "this agent cannot be encoded as a Wallet QR barcode",
      nextAction: "Shorten the agent intent, steps, or parameters, or share it as a file instead of a QR-backed Wallet pass.",
    };
  }

  const serialNumber = serialNumberFor(spec);
  const safeName = safeSegment(spec.name || spec.className || "agent");
  const dir = path.join(opts.outDir || exportsRoot(), safeName);
  const passPath = path.join(dir, `${safeName}.pkpass`);
  const tmpPath = path.join(dir, `.${safeName}.pkpass.tmp`);

  try {
    mkdirSync(dir, { recursive: true });
    const card = mintCard(agentCardFor(spec));
    const accent = colourToRgb(card.palette.accent);
    const files = new Map<string, Buffer>([
      ["pass.json", Buffer.from(JSON.stringify(buildPassJson(spec, share.url, serialNumber), null, 2), "utf8")],
      ["icon.png", solidPng(29, 29, accent)],
      ["icon@2x.png", solidPng(58, 58, accent)],
      ["logo.png", solidPng(160, 50, accent)],
      ["logo@2x.png", solidPng(320, 100, accent)],
    ]);
    const manifest = manifestFor(files);

    const missing = missingSigningEnv();
    let signed = false;
    let error: string | undefined;
    let nextAction: string | undefined;
    const zip = new AdmZip();

    if (missing.length === 0) {
      try {
        files.set("signature", await signManifest(dir, manifest));
        signed = true;
      } catch (err) {
        error = `wallet signing failed: ${err instanceof Error ? err.message : String(err)}`;
        nextAction = "Verify RAPP_WALLET_CERT, RAPP_WALLET_KEY, RAPP_WALLET_WWDR, and RAPP_WALLET_KEY_PASSWORD, then rebuild the pass. iOS will not install this unsigned bundle.";
        log.warn(error);
      }
    } else {
      error = `wallet pass bundle produced but unsigned: missing ${missing.join(", ")}`;
      nextAction = signingNextAction(missing);
    }

    for (const [name, data] of files) zip.addFile(name, data);
    zip.addFile("manifest.json", manifest);
    writeFileSync(tmpPath, zip.toBuffer());
    renameSync(tmpPath, passPath);
    log.info(signed ? "signed pass" : "unsigned pass", "->", passPath);

    return {
      ok: true,
      signed,
      installable: signed,
      path: passPath,
      serialNumber,
      shareUrl: share.url,
      error,
      nextAction,
    };
  } catch (err) {
    rmSync(tmpPath, { force: true });
    return {
      ok: false,
      signed: false,
      installable: false,
      serialNumber,
      shareUrl: share.url,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
