#!/usr/bin/env node
// check-kit.mjs — validate a studio brand kit: node scripts/check-kit.mjs kits/<name>
// Checks tokens.json shape, hex colours, that every font file and licence exists, that zones sit inside the
// frame, that no word zone touches the face keep-out or the platform-safe areas, and that design.md exists.
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";

const dir = resolve(process.argv[2] ?? "");
const fail = [];
const need = (ok, msg) => ok || fail.push(msg);
let t;
try {
  t = JSON.parse(readFileSync(join(dir, "tokens.json"), "utf8"));
} catch (e) {
  console.error(`✗ ${dir}/tokens.json: ${e.message}`);
  process.exit(1);
}
need(t.schema === "studio-brand-kit/1", "schema must be studio-brand-kit/1");
need(existsSync(join(dir, "design.md")), "design.md is missing");
for (const k of ["ink", "paper", "signal", "pulse", "warn", "muted", "panel", "line"])
  need(/^#[0-9A-Fa-f]{6}$/.test(t.colors?.[k] ?? ""), `colors.${k} must be #RRGGBB`);
const fontFiles = Object.entries(t.fonts ?? {});
need(fontFiles.length >= 4, "fonts needs display, body, kicker and mono");
for (const [role, f] of fontFiles) need(f.file && existsSync(join(dir, f.file)), `fonts.${role}: missing file ${f.file}`);
const licences = existsSync(join(dir, "fonts")) ? readdirSync(join(dir, "fonts")).filter((n) => /ofl|licen[cs]e/i.test(n)) : [];
need(licences.length > 0, "fonts/ needs the licence text for every font family");
const { width: W = 1080, height: H = 1920 } = t.frame ?? {};
const box = (b) => ({ x: b[0], y: b[1], r: b[0] + b[2], b: b[1] + b[3] });
const hit = (a, c) => a.x < c.r && c.x < a.r && a.y < c.b && c.y < a.b;
const zones = t.zones ?? {};
need(Array.isArray(zones.face), "zones.face (the keep-out) is required");
const keepOut = [["face", box(zones.face ?? [0, 0, 0, 0])]];
if (t.platform_safe) {
  keepOut.push(["platform bottom", { x: 0, y: t.platform_safe.bottom_y, r: W, b: H }]);
  if (t.platform_safe.right_rail) keepOut.push(["platform right rail", box(t.platform_safe.right_rail)]);
}
for (const [name, b] of Object.entries(zones)) {
  const z = box(b);
  need(z.x >= 0 && z.y >= 0 && z.r <= W && z.b <= H, `zones.${name} leaves the ${W}x${H} frame`);
  if (name === "face") continue;
  for (const [k, ko] of keepOut) need(!hit(z, ko), `zones.${name} overlaps the ${k} keep-out`);
}
need((t.captions?.max_words ?? 0) >= 1 && t.captions.max_words <= 6, "captions.max_words must be 1-6");
need(t.captions?.punctuation === false || t.captions?.punctuation === true, "captions.punctuation must be true or false");
need(!t.logo || existsSync(join(dir, t.logo)), `logo ${t.logo} is missing`);
if (fail.length) {
  for (const f of fail) console.error(`✗ ${f}`);
  process.exit(1);
}
console.log(`✓ kit ${t.name}: ${fontFiles.length} fonts, ${Object.keys(zones).length} zones, platform-safe ${t.platform_safe ? "on" : "off"}`);
