import assert from "node:assert/strict";
import { test } from "node:test";

import { decodeShareUrl, encodeShareUrl, MAX_PAYLOAD_CHARS } from "./agentshare.ts";
import { elementFor, fingerprint, mintCard, rarityFor, trustFor } from "./cardart.ts";
import { ART_STYLES, credits, styleById, styleForSeed } from "./cardstyles.ts";
import { inspectAgentSource } from "./agentcard.ts";
import type { ForgeSpecView } from "./ipc.ts";

const spec: ForgeSpecView = {
  name: "weekly-billing",
  className: "WeeklyBilling",
  title: "Weekly Unbilled Summary",
  description: "Tally unbilled time and email each client.",
  intent: "Automate the weekly billing review.",
  steps: [
    { title: "Fetch entries", detail: "Retrieve unbilled time grouped by client." },
    { title: "Total per client", detail: "Sum hours and dollar value." },
    { title: "Send summaries", detail: "Email each client their outstanding total." },
  ],
  parameters: [
    { name: "run_date", description: "Billing period end date", type: "string", required: false },
  ],
};

/* ── the share codec ─────────────────────────────────────────────────── */

test("a spec round-trips through the share link unchanged", () => {
  const encoded = encodeShareUrl(spec);
  assert.equal(encoded.ok, true);
  const decoded = decodeShareUrl(encoded.url!);
  assert.equal(decoded.ok, true);
  assert.deepEqual(decoded.spec, spec);
});

test("the link uses the rapp scheme so a phone camera can open it", () => {
  const { url } = encodeShareUrl(spec);
  assert.match(url!, /^rapp:\/\/agent\?v=1&n=weekly-billing&d=/);
});

test("a real spec compresses small enough to scan", () => {
  const { size } = encodeShareUrl(spec);
  assert.ok(size! < MAX_PAYLOAD_CHARS, `payload was ${size} characters`);
});

test("an agent too detailed for a QR is refused with a way forward", () => {
  const huge: ForgeSpecView = {
    ...spec,
    steps: Array.from({ length: 400 }, (_, i) => ({
      title: `Step ${i}`,
      detail: `A uniquely worded instruction number ${i} ${Math.random().toString(36)}`,
    })),
  };
  const encoded = encodeShareUrl(huge);
  assert.equal(encoded.ok, false);
  assert.match(encoded.error!, /AirDrop the file instead/);
});

test("a link from a stranger's newer mirror is refused clearly", () => {
  const { url } = encodeShareUrl(spec);
  const bumped = url!.replace("v=1", "v=9");
  const decoded = decodeShareUrl(bumped);
  assert.equal(decoded.ok, false);
  assert.match(decoded.error!, /newer mirror/);
});

test("a damaged or hostile link never throws, it just fails", () => {
  for (const bad of ["", "https://example.com", "rapp://agent?v=1&d=!!!!", "rapp://agent?v=1"]) {
    const decoded = decodeShareUrl(bad);
    assert.equal(decoded.ok, false);
    assert.ok(decoded.error);
  }
});

test("a card that names an invalid class is rejected before anything renders it", () => {
  const evil = encodeShareUrl({ ...spec, className: "../../etc/passwd" });
  const decoded = decodeShareUrl(evil.url!);
  assert.equal(decoded.ok, false);
  assert.match(decoded.error!, /invalid agent class/);
});

test("the shared payload carries no rendered Python at all", () => {
  const { url } = encodeShareUrl(spec);
  const decoded = decodeShareUrl(url!);
  assert.equal(decoded.ok, true);
  assert.ok(!JSON.stringify(decoded.spec).includes("import "));
  assert.ok(!JSON.stringify(decoded.spec).includes("def perform"));
});

/* ── the card face ───────────────────────────────────────────────────── */

const safeAgent = `
class WeeklyBilling(BasicAgent):
    def __init__(self):
        self.name = "WeeklyBilling"
        self.metadata = {"description": "Tally unbilled time."}
    def perform(self, **kwargs):
        steps = ["1. Fetch entries", "2. Total per client", "3. Send summaries", "4. Log it", "5. Report"]
        return steps
`;

test("the same agent always mints the identical card", () => {
  const card = inspectAgentSource(safeAgent);
  assert.deepEqual(mintCard(card), mintCard(card));
});

test("two different agents mint visibly different cards", () => {
  const a = mintCard(inspectAgentSource(safeAgent));
  const b = mintCard(inspectAgentSource(safeAgent.replace(/WeeklyBilling/g, "DailyCloseout")));
  assert.notEqual(a.seed, b.seed);
  assert.notDeepEqual(a.art.shapes, b.art.shapes);
});

test("editing an agent's behaviour re-mints its card", () => {
  const before = mintCard(inspectAgentSource(safeAgent));
  const after = mintCard(inspectAgentSource(safeAgent.replace("Send summaries", "Wire funds")));
  assert.notEqual(before.seed, after.seed);
});

test("a shell-running agent is cursed and void, never rare", () => {
  const card = inspectAgentSource(safeAgent.replace("def perform", "import subprocess\n    def perform"));
  assert.equal(rarityFor(card), "cursed");
  assert.equal(elementFor(card), "ember");
  assert.match(mintCard(card).flavor, /Decide carefully/);
});

test("a networked agent reads as aether", () => {
  const card = inspectAgentSource(safeAgent.replace("def perform", "import requests\n    def perform"));
  assert.equal(elementFor(card), "aether");
});

test("a restrained agent with real procedure earns a holo", () => {
  assert.equal(rarityFor(inspectAgentSource(safeAgent)), "holo");
});

test("trust falls as an agent reaches for more of your machine", () => {
  const safe = trustFor(inspectAgentSource(safeAgent));
  const shell = trustFor(inspectAgentSource(safeAgent.replace("def perform", "import subprocess\n    def perform")));
  assert.ok(shell < safe, `${shell} should be below ${safe}`);
  assert.ok(shell >= 20 && safe <= 120);
});

test("moves are drawn from the agent's own steps", () => {
  const face = mintCard(inspectAgentSource(safeAgent));
  assert.equal(face.moves.length, 3);
  assert.equal(face.moves[0].name, "Fetch entries");
  assert.ok(face.moves.every((m) => m.cost >= 1 && m.cost <= 3 && m.power > 0));
});

test("the artwork is a drawable scene graph, not platform code", () => {
  const face = mintCard(inspectAgentSource(safeAgent));
  assert.equal(face.art.viewBox, "0 0 100 100");
  assert.ok(face.art.shapes.length > 0);
  assert.ok(face.art.shapes.every((s) => typeof s.kind === "string"));
});

test("the dex number is stable and inside the set", () => {
  const face = mintCard(inspectAgentSource(safeAgent));
  assert.match(face.dex, /^\d{3} \/ 151$/);
  assert.ok(Number.parseInt(face.dex, 10) >= 1);
});

test("the fingerprint is a stable 32-bit value across runs", () => {
  assert.equal(fingerprint("WeeklyBilling"), fingerprint("WeeklyBilling"));
  assert.ok(fingerprint("a") !== fingerprint("b"));
  assert.ok(fingerprint("anything") <= 0xffffffff);
});

/* ── the art system: iconic frame, versatile medium ──────────────────── */

test("every shipped style renders a non-empty, well-formed artwork", () => {
  for (const style of ART_STYLES) {
    let n = 0;
    const next = () => ((n = (n * 1103515245 + 12345) % 2147483648), n / 2147483648);
    const art = style.render({ next, element: "aether", rarity: "holo", seed: 12345 });
    assert.equal(art.viewBox, "0 0 100 100", `${style.id} moved the art window`);
    assert.ok(art.shapes.length > 0, `${style.id} drew nothing`);
    for (const shape of art.shapes) {
      assert.ok(
        ["path", "circle", "rect", "line", "text"].includes(shape.kind),
        `${style.id} emitted an unknown shape ${shape.kind}`,
      );
      for (const [key, value] of Object.entries(shape)) {
        assert.ok(
          typeof value !== "number" || Number.isFinite(value),
          `${style.id} emitted a non-finite ${key}`,
        );
      }
    }
    for (const key of ["from", "to", "accent", "ink"] as const) {
      assert.ok(art.palette[key], `${style.id} left ${key} unset`);
    }
  }
});

test("the set spans real, distinct mediums so artists are featured", () => {
  const mediums = new Set(ART_STYLES.map((s) => s.medium));
  assert.equal(mediums.size, ART_STYLES.length, "two styles claim the same medium");
  assert.ok(ART_STYLES.length >= 8, "the set is too small to feel like a set");
  assert.ok(credits().every((c) => c.artist && c.name && c.medium));
});

test("the frame stays iconic: identity never changes with the style", () => {
  const card = inspectAgentSource(safeAgent);
  const faces = ART_STYLES.map((s) => mintCard(card, s.id));
  for (const face of faces) {
    assert.equal(face.seed, faces[0].seed);
    assert.equal(face.trust, faces[0].trust);
    assert.equal(face.rarity, faces[0].rarity);
    assert.equal(face.element, faces[0].element);
    assert.equal(face.dex, faces[0].dex);
    assert.deepEqual(face.moves, faces[0].moves);
  }
});

test("but the art itself genuinely differs between styles", () => {
  const card = inspectAgentSource(safeAgent);
  const drawings = ART_STYLES.map((s) => JSON.stringify(mintCard(card, s.id).art.shapes));
  assert.equal(new Set(drawings).size, ART_STYLES.length, "two styles drew the same picture");
});

test("a card credits the artist who drew it", () => {
  const face = mintCard(inspectAgentSource(safeAgent), "woodblock");
  assert.equal(face.style.id, "woodblock");
  assert.equal(face.style.medium, "ukiyo-e woodblock");
  assert.ok(face.style.artist.length > 0);
});

test("an unknown style falls back to the house style rather than failing", () => {
  const face = mintCard(inspectAgentSource(safeAgent), "not-a-real-style");
  assert.equal(face.style.id, "prism");
});

test("style choice is deterministic per agent, so a card is always itself", () => {
  const card = inspectAgentSource(safeAgent);
  assert.equal(mintCard(card).style.id, mintCard(card).style.id);
  assert.equal(styleForSeed(42, "holo").id, styleForSeed(42, "holo").id);
});

test("a cursed agent is never dressed up in a pretty style", () => {
  const cursed = inspectAgentSource(safeAgent.replace("def perform", "import subprocess\n    def perform"));
  const face = mintCard(cursed);
  assert.equal(face.rarity, "cursed");
  assert.equal(face.style.id, styleById("vapor").id);
  assert.equal(face.art.holo, "shattered");
});
