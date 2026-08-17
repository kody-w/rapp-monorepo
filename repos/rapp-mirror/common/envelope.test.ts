import assert from "node:assert/strict";
import test from "node:test";

import { parseEnvelope } from "./ipc.ts";

test("plain text passes through untouched", () => {
  const e = parseEnvelope("Hello there.");
  assert.deepEqual(e, { text: "Hello there.", spoken: null, holo: null });
});

test("voice line is split out and trimmed", () => {
  const e = parseEnvelope("Full answer here.|||VOICE||| The short spoken line. ");
  assert.equal(e.text, "Full answer here.");
  assert.equal(e.spoken, "The short spoken line.");
  assert.equal(e.holo, null);
});

test("full envelope: text + voice + holo options", () => {
  const raw =
    'Here are your choices.|||VOICE|||Pick one.|||HOLO|||{"prompt":"Which?","options":[{"label":"Alpha","value":"a"},{"label":"Beta"}]}';
  const e = parseEnvelope(raw);
  assert.equal(e.text, "Here are your choices.");
  assert.equal(e.spoken, "Pick one.");
  assert.equal(e.holo?.prompt, "Which?");
  assert.deepEqual(e.holo?.options.map((o) => o.label), ["Alpha", "Beta"]);
});

test("malformed HOLO json degrades to clean text", () => {
  const e = parseEnvelope("Answer.|||HOLO|||{not json");
  assert.equal(e.text, "Answer.");
  assert.equal(e.holo, null);
});

test("holo options are capped at six and label-validated", () => {
  const options = JSON.stringify({
    options: [1, { label: "A" }, { nope: true }, ...Array.from({ length: 8 }, (_, i) => ({ label: `L${i}` }))],
  });
  const e = parseEnvelope(`x|||HOLO|||${options}`);
  assert.equal(e.holo?.options.length, 6);
  assert.equal(e.holo?.options[0].label, "A");
});

test("empty voice section becomes null", () => {
  const e = parseEnvelope("Text.|||VOICE|||   ");
  assert.equal(e.spoken, null);
  assert.equal(e.text, "Text.");
});

test("OPTIONS quick form: three pipe-separated next requests become options", () => {
  const e = parseEnvelope(
    "Here's the digest.|||VOICE|||Digest ready.|||OPTIONS|||Show me more like this | Make this an automation | What changed today",
  );
  assert.equal(e.text, "Here's the digest.");
  assert.equal(e.spoken, "Digest ready.");
  assert.deepEqual(e.holo?.options.map((o) => o.label), [
    "Show me more like this",
    "Make this an automation",
    "What changed today",
  ]);
});

test("OPTIONS tolerates list bullets, dupes, and blanks; caps at six", () => {
  const e = parseEnvelope("x|||OPTIONS|||1. Alpha | - Beta |  | alpha | c | d | e | f | g");
  assert.deepEqual(e.holo?.options.map((o) => o.label), ["Alpha", "Beta", "c", "d", "e", "f"]);
});

test("marker order is tolerated: OPTIONS before VOICE still parses both", () => {
  const e = parseEnvelope("Answer.|||OPTIONS|||a | b | c|||VOICE|||Spoken line.");
  assert.equal(e.text, "Answer.");
  assert.equal(e.spoken, "Spoken line.");
  assert.equal(e.holo?.options.length, 3);
});

test("HOLO wins over OPTIONS when both are present", () => {
  const e = parseEnvelope(
    'x|||HOLO|||{"options":[{"label":"Rich","value":"r"}]}|||OPTIONS|||quick a | quick b',
  );
  assert.deepEqual(e.holo?.options.map((o) => o.label), ["Rich"]);
});
