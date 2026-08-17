/**
 * The card face — every agent is a trading card.
 *
 * An agent you can AirDrop is an agent you can trade, so it should look like
 * something worth trading. Everything here is derived *deterministically* from
 * the agent itself: the same agent always mints the identical card on every
 * machine, and two different agents never collide by accident. Nothing is
 * random, so a card is a fingerprint you can recognise across a room.
 *
 * Element comes from what the agent actually does. Rarity comes from what it
 * is allowed to touch — a shell-running agent is not "rare", it is *cursed*,
 * and it looks like it.
 */

import type { AgentCard } from "./agentcard.ts";
import {
  type ArtStyle,
  type ArtWork,
  type Palette,
  type StyleCredit,
  styleById,
  styleForSeed,
} from "./cardstyles.ts";

export type Element = "spirit" | "aether" | "ember" | "stone" | "void";
export type Rarity = "common" | "uncommon" | "rare" | "holo" | "cursed";

export interface Move {
  name: string;
  /** Energy pips drawn beside the move, 1–3. */
  cost: number;
  text: string;
  /** Damage-style number, derived — flavour with a real basis. */
  power: number;
}

export interface CardFace {
  /** Stable 32-bit fingerprint of the agent's identity + behaviour. */
  seed: number;
  title: string;
  subtitle: string;
  element: Element;
  rarity: Rarity;
  /** "HP" — how much of your machine this agent leaves alone. 20–120. */
  trust: number;
  moves: Move[];
  /** The artwork, as a platform-agnostic scene graph (SVG, SwiftUI, raster). */
  art: ArtWork;
  /** Which artist/medium drew this card — printed on the face. */
  style: StyleCredit;
  /** Convenience mirror of `art.palette` for frame chrome. */
  palette: Palette;
  /** The flavour line along the card's foot. */
  flavor: string;
  /** Dex-style number, e.g. "042 / 151". */
  dex: string;
}

const ELEMENT_ORDER: Element[] = ["spirit", "aether", "ember", "stone", "void"];

const FLAVOR: Record<Rarity, string> = {
  common: "Forged in a quiet room.",
  uncommon: "It has seen the outside.",
  rare: "Few of these were ever made.",
  holo: "Watched once. Repeats forever.",
  cursed: "It asks for the keys. Decide carefully.",
};

/** FNV-1a — small, stable, and identical in TypeScript and Swift. */
export function fingerprint(input: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

/** A deterministic stream of numbers from one seed (mulberry32). */
function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** What the agent touches decides its element — not its name. */
export function elementFor(card: AgentCard): Element {
  const ids = new Set(card.findings.map((f) => f.id));
  if (ids.has("exec") || ids.has("credentials") || ids.has("obfuscation")) return "void";
  if (ids.has("shell")) return "ember";
  if (ids.has("network")) return "aether";
  if (ids.has("filewrite") || ids.has("dynamic-import") || ids.has("env")) return "stone";
  return "spirit";
}

/** Rarity is earned by restraint, and by how much the agent actually does. */
export function rarityFor(card: AgentCard): Rarity {
  if (card.verdict === "dangerous") return "cursed";
  if (card.verdict === "review") return card.findings.length > 2 ? "common" : "uncommon";
  // Safe agents: the more real procedure it carries, the better the pull.
  if (card.steps.length >= 5) return "holo";
  if (card.steps.length >= 3) return "rare";
  return "uncommon";
}

/** Trust is the card's HP: what it leaves alone. */
export function trustFor(card: AgentCard): number {
  const penalty = card.findings.reduce(
    (sum, f) => sum + (f.severity === "critical" ? 35 : 12),
    0,
  );
  const bonus = Math.min(card.parameters.length * 5, 20);
  return Math.max(20, Math.min(120, 100 - penalty + bonus));
}

/** The agent's steps become its moves. */
function movesFor(card: AgentCard, next: () => number): Move[] {
  const source = card.steps.length
    ? card.steps
    : [card.description || "Performs its purpose."];
  return source.slice(0, 3).map((step, index) => {
    // Steps arrive as "1. Title: detail" — split the title back out.
    const stripped = step.replace(/^\s*\d+[.)]\s*/, "");
    const [head, ...rest] = stripped.split(":");
    const name = head.trim().slice(0, 28) || `Move ${index + 1}`;
    const text = (rest.join(":").trim() || stripped).slice(0, 96);
    return {
      name,
      cost: 1 + (index % 3),
      text,
      power: 10 * (2 + Math.floor(next() * 7)),
    };
  });
}

/** Mint the card face for an inspected agent. */
export function mintCard(card: AgentCard, styleId?: string): CardFace {
  // Identity + behaviour, so an edited agent mints a visibly different card.
  const seed = fingerprint(
    [card.className, card.name, card.description, card.steps.join("|"), card.verdict].join("::"),
  );
  const next = rng(seed);
  const element = elementFor(card);
  const rarity = rarityFor(card);
  // An explicit choice wins; otherwise the fingerprint decides which artist
  // drew this one, so the style is part of what you pull.
  const style: ArtStyle = styleId ? styleById(styleId) : styleForSeed(seed, rarity);
  // Identity and art draw from separate streams on purpose: a card's stats must
  // never shift because a different artist drew it.
  const art = style.render({ next: rng(seed ^ 0x9e3779b9), element, rarity, seed });

  return {
    seed,
    title: card.name || card.className || "Unknown Agent",
    subtitle: card.className,
    element,
    rarity,
    trust: trustFor(card),
    moves: movesFor(card, next),
    art,
    style: { id: style.id, name: style.name, artist: style.artist, medium: style.medium },
    palette: art.palette,
    flavor: FLAVOR[rarity],
    dex: `${String((seed % 151) + 1).padStart(3, "0")} / 151`,
  };
}

/** Stable ordering for a shelf of collected agents. */
export function elementIndex(element: Element): number {
  return ELEMENT_ORDER.indexOf(element);
}
