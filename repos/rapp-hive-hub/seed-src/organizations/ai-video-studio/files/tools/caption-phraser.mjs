#!/usr/bin/env node
// caption-phraser.mjs — words.json (studio-words/1) + a brand kit's tokens.json -> caption phrases on the output
// timeline, an SRT file, or a trace check of an existing captions.json. Node 18+, no dependencies.
//
//   node tools/caption-phraser.mjs <words.json> <tokens.json> [--cuts 0.3-16.39,20.8-48.7] [--out captions.json] [--srt captions.srt]
//   node tools/caption-phraser.mjs <words.json> <tokens.json> [--cuts ...] --verify captions.json
//
// Phrases follow tokens.captions: at most max_words words, sentence punctuation removed when punctuation is false
// (characters inside a token such as HTTP/1.1 or Sec-WebSocket-Key stay), and a hard break at every sentence end,
// speaker change, pause of 0.35 s or more, and cut. Inside a run, a small dynamic program picks the breaks (see
// split()). Cuts map source times onto the output timeline: the output
// is the cuts played back to back, and words outside every cut are dropped.
import { readFileSync, writeFileSync } from "node:fs";

const argv = process.argv.slice(2);
const opt = (name) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 ? argv[i + 1] : null;
};
const [wordsPath, tokensPath] = argv.filter((a, i) => !a.startsWith("--") && !(i > 0 && argv[i - 1].startsWith("--")));
if (!wordsPath || !tokensPath) {
  console.error("usage: node caption-phraser.mjs <words.json> <tokens.json> [--cuts a-b,c-d] [--out captions.json] [--srt file] [--verify captions.json]");
  process.exit(2);
}
const words = JSON.parse(readFileSync(wordsPath, "utf8")).words;
const kit = JSON.parse(readFileSync(tokensPath, "utf8"));
const maxWords = kit.captions?.max_words ?? 4;
const keepPunctuation = kit.captions?.punctuation === true;
const cuts = (opt("cuts") ?? "")
  .split(",")
  .filter(Boolean)
  .map((c) => c.split("-").map(Number))
  .map(([from, to]) => ({ from, to }));
if (!cuts.length) cuts.push({ from: 0, to: Infinity });
const PAUSE = 0.35;
const EDGE = /^[\s.,;:!?"'“”‘’()[\]{}…—–-]+|[\s.,;:!?"'“”‘’()[\]{}…—–-]+$/gu;
const round = (t) => Math.round(t * 1000) / 1000;
const norm = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "");

function onOutput(list) {
  const out = [];
  let offset = 0;
  cuts.forEach((cut, index) => {
    for (const w of list) {
      if (w.start < cut.from || w.start >= cut.to) continue;
      out.push({ ...w, cut: index, start: round(offset + w.start - cut.from), end: round(offset + Math.min(w.end, cut.to) - cut.from) });
    }
    offset += cut.to - cut.from;
  });
  return out;
}

// A run between hard breaks is split by a small dynamic program: fewest phrases first, then prefer breaking after a
// comma, avoid breaking after an article, preposition or number, and avoid one-word phrases.
const ARTICLES = new Set(["a", "an", "the"]);
const GLUE = new Set(["of", "to", "in", "on", "for", "with", "by", "as", "at", "from", "and", "or", "but", "that", "which", "its", "their", "your", "our", "my", "is", "are", "was", "were"]);
function split(run) {
  const breakCost = (j) => {
    const before = run[j - 1].text;
    if (/[,;:]["”’)]*$/u.test(before)) return -7;
    const word = norm(before);
    if (ARTICLES.has(word)) return 8;
    if (GLUE.has(word) || /^\d+$/.test(word)) return 4;
    return 0;
  };
  const best = [{ cost: 0, from: -1 }];
  for (let i = 1; i <= run.length; i++) {
    best[i] = { cost: Infinity, from: -1 };
    for (let k = 1; k <= maxWords && k <= i; k++) {
      const j = i - k;
      const cost = best[j].cost + 6 + (k === 1 ? 5 : 0) + (j > 0 ? breakCost(j) : 0);
      if (cost < best[i].cost) best[i] = { cost, from: j };
    }
  }
  const chunks = [];
  for (let i = run.length; i > 0; i = best[i].from) chunks.unshift(run.slice(best[i].from, i));
  return chunks;
}

function phrases(list) {
  const runs = [];
  list.forEach((w, i) => {
    const prev = list[i - 1];
    const hard = !prev || prev.cut !== w.cut || (prev.speaker ?? "") !== (w.speaker ?? "") || w.start - prev.end >= PAUSE || /[.?!]["”’)]*$/u.test(prev.text);
    if (hard) runs.push([]);
    runs[runs.length - 1].push(w);
  });
  const result = [];
  for (const run of runs) {
    for (const chunk of split(run)) {
      const shown = chunk.map((w) => ({ text: keepPunctuation ? w.text : w.text.replace(EDGE, ""), start: w.start, end: w.end })).filter((w) => w.text);
      if (shown.length) result.push({ start: shown[0].start, end: shown[shown.length - 1].end, speaker: chunk[0].speaker ?? null, text: shown.map((w) => w.text).join(" "), words: shown });
    }
  }
  result.forEach((ph, i) => {
    ph.id = `c${String(i + 1).padStart(3, "0")}`;
    const next = result[i + 1];
    ph.end = round(next ? Math.min(ph.end + 0.2, next.start) : ph.end + 0.2);
  });
  return result;
}

function srt(list) {
  const stamp = (t) => {
    const ms = Math.round(t * 1000);
    const pad = (n, w = 2) => String(n).padStart(w, "0");
    return `${pad(Math.floor(ms / 3600000))}:${pad(Math.floor(ms / 60000) % 60)}:${pad(Math.floor(ms / 1000) % 60)},${pad(ms % 1000, 3)}`;
  };
  return list.map((p, i) => `${i + 1}\n${stamp(p.start)} --> ${stamp(p.end)}\n${p.text}\n`).join("\n");
}

const spoken = onOutput(words);
if (opt("verify")) {
  const captions = JSON.parse(readFileSync(opt("verify"), "utf8")).phrases;
  const fails = [];
  const shown = captions.flatMap((p) => p.text.split(/\s+/).filter(Boolean));
  const expected = spoken.map((w) => norm(w.text)).filter(Boolean);
  const got = shown.map(norm).filter(Boolean);
  const firstDiff = expected.findIndex((w, i) => got[i] !== w);
  if (firstDiff >= 0 || got.length !== expected.length) {
    const at = firstDiff >= 0 ? firstDiff : Math.min(got.length, expected.length);
    fails.push(`caption-trace: word ${at + 1} is "${shown[at] ?? "(none)"}", transcript says "${spoken[at]?.text ?? "(none)"}"`);
  }
  for (const p of captions) {
    const count = p.text.split(/\s+/).filter(Boolean).length;
    if (count > maxWords) fails.push(`caption-style: ${p.id ?? p.text} has ${count} words (max ${maxWords})`);
    if (!keepPunctuation && /(^|\s)[.,;:!?"“”]|[.,;:!?"“”](\s|$)/u.test(p.text)) fails.push(`caption-style: ${p.id ?? p.text} carries punctuation: "${p.text}"`);
  }
  if (fails.length) {
    fails.forEach((f) => console.error(`✗ ${f}`));
    process.exit(1);
  }
  console.log(`✓ ${captions.length} phrases trace to ${expected.length} spoken words in order; style ok (max ${maxWords} words, punctuation ${keepPunctuation ? "kept" : "removed"})`);
  process.exit(0);
}

const list = phrases(spoken);
const doc = { schema: "studio-captions/1", words: wordsPath, kit: kit.name ?? null, max_words: maxWords, punctuation: keepPunctuation,
  cuts: cuts.map((c) => [c.from, Number.isFinite(c.to) ? c.to : null]), duration: round(cuts.reduce((s, c) => s + (Number.isFinite(c.to) ? c.to - c.from : 0), 0)) || null, phrases: list };
const out = opt("out") ?? "captions.json";
writeFileSync(out, `${JSON.stringify(doc, null, 1)}\n`);
if (opt("srt")) writeFileSync(opt("srt"), srt(list));
const sizes = list.map((p) => p.words.length);
console.log(`✓ ${list.length} phrases from ${spoken.length} words -> ${out}${opt("srt") ? ` and ${opt("srt")}` : ""} (words per phrase ${Math.min(...sizes)}-${Math.max(...sizes)})`);
