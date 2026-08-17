#!/usr/bin/env node
// Stage all vision/OCR runtime assets locally under public/ (gitignored):
//  - MediaPipe tasks-vision wasm  -> public/vision/wasm/
//  - Face + gesture .task models  -> public/vision/models/  (storage.googleapis.com)
//  - Tesseract.js runtime         -> public/vendor/
// Runs on postinstall; safe to re-run (skips what already exists). The app
// never depends on jsdelivr at runtime — some networks break it.
import { copyFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const pub = (...p) => path.join(root, "public", ...p);
const nm = (...p) => path.join(root, "node_modules", ...p);

mkdirSync(pub("vision", "wasm"), { recursive: true });
mkdirSync(pub("vision", "models"), { recursive: true });
mkdirSync(pub("vendor"), { recursive: true });

const copies = [
  ...["vision_wasm_internal.js", "vision_wasm_internal.wasm", "vision_wasm_nosimd_internal.js", "vision_wasm_nosimd_internal.wasm"]
    .map((f) => [nm("@mediapipe", "tasks-vision", "wasm", f), pub("vision", "wasm", f)]),
  [nm("tesseract.js", "dist", "tesseract.min.js"), pub("vendor", "tesseract.min.js")],
  [nm("tesseract.js", "dist", "worker.min.js"), pub("vendor", "worker.min.js")],
  [nm("tesseract.js-core", "tesseract-core-simd-lstm.wasm.js"), pub("vendor", "tesseract-core-simd-lstm.wasm.js")],
];
for (const [src, dst] of copies) {
  if (!existsSync(src)) {
    console.error("missing package asset:", src);
    process.exitCode = 1;
    continue;
  }
  copyFileSync(src, dst);
}

const MODELS = [
  ["face_landmarker.task", "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"],
  ["gesture_recognizer.task", "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"],
];
for (const [name, url] of MODELS) {
  const dst = pub("vision", "models", name);
  if (existsSync(dst)) continue;
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    writeFileSync(dst, Buffer.from(await r.arrayBuffer()));
    console.log("downloaded", name);
  } catch (err) {
    console.warn(`could not download ${name} (${err.message}) — hands-free needs it; re-run npm install online`);
  }
}
console.log("vision assets staged in public/");
