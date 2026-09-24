#!/usr/bin/env node
// transcribe.mjs — word-timed transcript for a clip, in the studio's words.json contract (studio-words/1).
//
//   node transcribe.mjs <media> [--out transcript] [--engine auto|scribe|local] [--model <id>] [--language en]
//                       [--window 0.3-48.7] [--speakers 1] [--keyterms "WebSocket,RFC 6455"]
//                       [--terms "WebSocket,Sec-WebSocket-Key"] [--known <script.md|words.json>]
//
// Engines
//   scribe  ElevenLabs Speech to Text (POST /v1/speech-to-text, model scribe_v2, word timestamps, diarization).
//           Needs ELEVENLABS_API_KEY in the environment or in ./.env. The key is never printed or written.
//   local   HyperFrames 0.8.41 `transcribe` (Whisper small.en or Parakeet), fully offline once models are cached.
//   auto    scribe when a key is configured, otherwise local.
// Fixes
//   --terms  canonical spellings; any 1-3 recognized words that match a term ignoring case, spaces and hyphens
//            are replaced by it ("web socket" -> "WebSocket").
//   --known  the words are known (teleprompter read verbatim, synthesized narration): known words win, the
//            recognized words only supply timing. Prints how well the two agreed. Add --timing known when the
//            known file is itself a trusted word alignment (e.g. synthesized narration): its times are kept and
//            the recognition only verifies the audio says those words.
// Output (times on the SOURCE clip timeline): <out>/words.json, <out>/transcript.txt, <out>/meta.json
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { basename, extname, join, relative, resolve } from "node:path";

const HF_VERSION = "0.8.41";
const args = process.argv.slice(2);
const flag = (name, fallback = null) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : fallback;
};
const media = args.find((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
if (!media || !existsSync(media)) {
  console.error("usage: node transcribe.mjs <media> [--out transcript] [--engine auto|scribe|local] [--window a-b] [--known file] [--terms list]");
  process.exit(2);
}
const outDir = resolve(flag("out", "transcript"));
const language = flag("language");
const speakers = flag("speakers");
const [winFrom, winTo] = (flag("window") ?? "").split("-").map(Number);
const hasWindow = Number.isFinite(winFrom) && Number.isFinite(winTo) && winTo > winFrom;

function apiKey() {
  if (process.env.ELEVENLABS_API_KEY) return process.env.ELEVENLABS_API_KEY;
  if (!existsSync(".env")) return null;
  const line = readFileSync(".env", "utf8").split(/\r?\n/).find((l) => /^\s*ELEVENLABS_API_KEY\s*=/.test(l));
  const value = line?.split("=").slice(1).join("=").trim().replace(/^["']|["']$/g, "");
  return value || null;
}
const key = apiKey();
let engine = flag("engine", "auto");
if (engine === "auto") engine = key ? "scribe" : "local";
if (engine === "scribe" && !key) {
  console.error("✗ scribe needs ELEVENLABS_API_KEY (environment or ./.env). Use --engine local to stay offline.");
  process.exit(2);
}

// 16 kHz mono PCM of the clip (or of the window): small uploads, identical input for both engines.
const scratch = mkdtempSync(join(tmpdir(), "studio-transcribe-"));
const wav = join(scratch, "audio.wav");
const cut = hasWindow ? ["-ss", String(winFrom), "-t", String(winTo - winFrom)] : [];
const ff = spawnSync("ffmpeg", ["-v", "error", "-y", ...cut, "-i", media, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav]);
if (ff.status !== 0) {
  console.error(`✗ ffmpeg could not extract audio: ${String(ff.stderr).trim()}`);
  process.exit(1);
}
const offset = hasWindow ? winFrom : 0;

async function scribe() {
  const model = flag("model", "scribe_v2");
  const form = new FormData();
  form.append("model_id", model);
  form.append("file", new Blob([readFileSync(wav)], { type: "audio/wav" }), "audio.wav");
  form.append("file_format", "pcm_s16le_16");
  form.append("timestamps_granularity", "word");
  form.append("tag_audio_events", "false");
  form.append("diarize", speakers === "1" ? "false" : "true");
  if (speakers) form.append("num_speakers", speakers);
  if (language) form.append("language_code", language);
  for (const term of (flag("keyterms") ?? "").split(",").map((t) => t.trim()).filter(Boolean)) form.append("keyterms", term);
  const res = await fetch("https://api.elevenlabs.io/v1/speech-to-text", { method: "POST", headers: { "xi-api-key": key }, body: form });
  if (!res.ok) throw new Error(`ElevenLabs returned ${res.status}: ${(await res.text()).slice(0, 300)}`);
  const body = await res.json();
  const words = (body.words ?? []).filter((w) => w.type === "word").map((w) => ({ text: w.text, start: w.start, end: w.end, speaker: w.speaker_id ?? "S1" }));
  return { words, model, language: body.language_code ?? language ?? null };
}

function hyperframesBin() {
  const spec = `hyperframes@${HF_VERSION}`;
  const dir = process.env.HYPERFRAMES_CLI_DIR ||
    join(process.env.npm_config_cache || join(homedir(), ".npm"), "_npx", createHash("sha512").update(spec).digest("hex").slice(0, 16), "node_modules/hyperframes");
  if (!existsSync(join(dir, "bin/hyperframes.mjs"))) spawnSync("npx", ["--yes", spec, "--version"], { stdio: "ignore" });
  return join(dir, "bin/hyperframes.mjs");
}

function local() {
  const model = flag("model", "small.en");
  const env = { ...process.env, HYPERFRAMES_NO_UPDATE_CHECK: "1", HYPERFRAMES_NO_TELEMETRY: "1", DO_NOT_TRACK: "1" };
  const argv = [hyperframesBin(), "transcribe", wav, "-d", scratch, "--json", "--model", model, ...(language ? ["--language", language] : [])];
  const run = spawnSync(process.execPath, argv, { env, encoding: "utf8" });
  const summary = JSON.parse(run.stdout || "{}");
  if (run.status !== 0 || !summary.ok) throw new Error(`hyperframes transcribe failed: ${(run.stderr || run.stdout).slice(0, 300)}`);
  const words = JSON.parse(readFileSync(summary.transcriptPath, "utf8")).map((w) => ({ text: w.text, start: w.start, end: w.end, speaker: "S1" }));
  return { words, model: `${summary.engine}:${summary.model ?? model}`, language };
}

const norm = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "");

function applyTerms(words, terms) {
  const canon = new Map(terms.map((t) => [norm(t), t]));
  const out = [];
  for (let i = 0; i < words.length; ) {
    let taken = 0;
    for (let n = 3; n >= 1 && !taken; n--) {
      if (i + n > words.length) continue;
      const run = words.slice(i, i + n);
      const trail = run[n - 1].text.match(/[^\p{L}\p{N}]+$/u)?.[0] ?? "";
      const hit = canon.get(norm(run.map((w) => w.text).join("")));
      if (hit) {
        out.push({ ...run[0], text: hit + trail, end: run[n - 1].end });
        taken = n;
      }
    }
    if (!taken) out.push(words[i]);
    i += taken || 1;
  }
  return out;
}

function knownTokens(file) {
  const raw = readFileSync(file, "utf8");
  if (extname(file) === ".json") {
    const data = JSON.parse(raw);
    return (data.words ?? data).map((w) => ({ text: w.text, speaker: w.speaker ?? null, start: w.start ?? null, end: w.end ?? null }));
  }
  return raw.replace(/^#.*$/gm, " ").split(/\s+/).filter(Boolean).map((text) => ({ text, speaker: null, start: null, end: null }));
}

// Known words win; recognized words supply timing. Alignment on normalized forms allows 1:1, 1:2 and 2:1 matches.
function alignKnown(recognized, known) {
  const R = recognized.map((w) => norm(w.text)), K = known.map((w) => norm(w.text));
  const n = R.length, m = K.length, INF = 1e9;
  const cost = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(INF));
  const back = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(null));
  cost[0][0] = 0;
  for (let i = 0; i <= n; i++) {
    for (let j = 0; j <= m; j++) {
      const c = cost[i][j];
      if (c >= INF) continue;
      const step = (di, dj, add, kind) => {
        if (i + di <= n && j + dj <= m && c + add < cost[i + di][j + dj]) {
          cost[i + di][j + dj] = c + add;
          back[i + di][j + dj] = [i, j, kind];
        }
      };
      if (i < n && j < m) step(1, 1, R[i] === K[j] ? 0 : 1, R[i] === K[j] ? "same" : "fix");
      if (i < n && j + 1 < m && R[i] === K[j] + K[j + 1]) step(1, 2, 0, "split");
      if (i + 1 < n && j < m && R[i] + R[i + 1] === K[j]) step(2, 1, 0, "merge");
      step(1, 0, 1, "extra");
      step(0, 1, 1, "missing");
    }
  }
  const pairs = [];
  for (let i = n, j = m; i || j; ) {
    const [pi, pj, kind] = back[i][j];
    pairs.push({ r: [pi, i], k: [pj, j], kind });
    [i, j] = [pi, pj];
  }
  pairs.reverse();
  const out = [], stats = { same: 0, fix: 0, split: 0, merge: 0, extra: 0, missing: 0 };
  for (const p of pairs) {
    stats[p.kind] += 1;
    if (p.kind === "extra") continue;
    const rs = recognized.slice(p.r[0], p.r[1]), ks = known.slice(p.k[0], p.k[1]);
    if (!rs.length) {
      ks.forEach((k) => out.push({ text: k.text, start: null, end: null, speaker: k.speaker ?? "S1" }));
      continue;
    }
    const start = rs[0].start, end = rs[rs.length - 1].end, chars = ks.reduce((s, k) => s + k.text.length, 0);
    let t = start;
    for (const k of ks) {
      const span = ((end - start) * k.text.length) / chars;
      out.push({ text: k.text, start: +t.toFixed(3), end: +(t + span).toFixed(3), speaker: k.speaker ?? rs[0].speaker });
      t += span;
    }
  }
  for (let i = 0; i < out.length; i++) {
    if (out[i].start !== null) continue;
    const prev = out.slice(0, i).reverse().find((w) => w.end !== null)?.end ?? 0;
    const next = out.slice(i + 1).find((w) => w.start !== null)?.start ?? prev;
    Object.assign(out[i], { start: prev, end: Math.max(prev, next) });
  }
  const agreement = known.length ? (stats.same + stats.split + stats.merge) / known.length : 1;
  return { words: out, stats: { ...stats, agreement: +agreement.toFixed(3) } };
}

try {
  const result = engine === "scribe" ? await scribe() : local();
  let words = result.words.map((w) => ({ ...w, start: +(w.start + offset).toFixed(3), end: +(w.end + offset).toFixed(3) }));
  const terms = (flag("terms") ?? "").split(",").map((t) => t.trim()).filter(Boolean);
  if (terms.length) words = applyTerms(words, terms);
  let alignment = null;
  if (flag("known")) {
    const known = knownTokens(flag("known"));
    ({ words, stats: alignment } = alignKnown(words, known));
    if (flag("timing") === "known") {
      if (!known.every((k) => Number.isFinite(k.start) && Number.isFinite(k.end))) throw new Error("--timing known needs a words.json whose every word has start and end");
      words = known.map((k) => ({ text: k.text, start: k.start, end: k.end, speaker: k.speaker ?? "S1" }));
    }
  }
  for (let i = 1; i < words.length; i++) if (words[i].start < words[i - 1].start) words[i].start = words[i - 1].start;
  mkdirSync(outDir, { recursive: true });
  const source = relative(process.cwd(), resolve(media)) || basename(media);
  writeFileSync(join(outDir, "words.json"), `${JSON.stringify({ schema: "studio-words/1", engine, model: result.model, source,
    window: hasWindow ? [winFrom, winTo] : null, language: result.language, words }, null, 1)}\n`);
  const lines = [];
  for (const w of words) {
    const last = lines[lines.length - 1];
    if (last && last.speaker === w.speaker && w.start - last.end < 0.6) Object.assign(last, { text: `${last.text} ${w.text}`, end: w.end });
    else lines.push({ speaker: w.speaker, start: w.start, end: w.end, text: w.text });
  }
  const stamp = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${(s % 60).toFixed(2).padStart(5, "0")}`;
  writeFileSync(join(outDir, "transcript.txt"), lines.map((l) => `[${stamp(l.start)}] ${l.speaker}: ${l.text}`).join("\n") + "\n");
  const mediaSha = createHash("sha256").update(readFileSync(media)).digest("hex");
  writeFileSync(join(outDir, "meta.json"), `${JSON.stringify({ schema: "studio-transcript-meta/1", engine, model: result.model,
    media: source, media_sha256: mediaSha, window: hasWindow ? [winFrom, winTo] : null, words: words.length, terms, alignment,
    settings: { language, speakers, keyterms: flag("keyterms") } }, null, 1)}\n`);
  console.log(`✓ ${words.length} words via ${engine} (${result.model})${alignment ? `; known-script agreement ${(alignment.agreement * 100).toFixed(1)}%` : ""} -> ${relative(process.cwd(), outDir) || "."}/words.json`);
} catch (error) {
  console.error(`✗ ${error.message}`);
  process.exitCode = 1;
} finally {
  rmSync(scratch, { recursive: true, force: true });
}
