/**
 * The art system — one iconic card, any medium.
 *
 * A card has to be recognisable across a room and still leave room for a
 * hundred different artists. So the two things are separated:
 *
 *   • **Identity** (common/cardart.ts) never changes: the silhouette, the stat
 *     positions, the element, the rarity, the moves, the dex number. That is
 *     what makes a card *iconic* — you know what you are holding before you
 *     read it.
 *   • **Style** (this file) changes completely: palette, linework, texture,
 *     foil behaviour, the art itself. That is what makes the set *versatile* —
 *     woodblock, risograph, ASCII, sumi ink, blueprint, stained glass.
 *
 * A style never draws pixels. It emits a small declarative scene graph, so the
 * exact same artwork renders as SVG in the desktop app, as `Path` in SwiftUI,
 * and as a flat raster on an Apple Wallet pass — with no per-platform art code
 * and no drift between them. Adding an artist means adding one function here.
 *
 * Everything is deterministic: an agent's art is a function of its fingerprint,
 * so the same agent is the same card on every machine, forever.
 */

export type TextureKind = "none" | "grain" | "halftone" | "scanlines" | "paper" | "weave";
export type HoloKind = "none" | "linear" | "prismatic" | "shattered" | "pearl";

export interface Palette {
  from: string;
  to: string;
  accent: string;
  ink: string;
  /** Optional second spot colour; styles that print in two inks use it. */
  spot?: string;
}

export type Shape =
  | { kind: "path"; d: string; fill?: string; stroke?: string; width?: number; opacity?: number }
  | { kind: "circle"; cx: number; cy: number; r: number; fill?: string; stroke?: string; width?: number; opacity?: number }
  | { kind: "rect"; x: number; y: number; w: number; h: number; fill?: string; stroke?: string; width?: number; opacity?: number; radius?: number }
  | { kind: "line"; x1: number; y1: number; x2: number; y2: number; stroke: string; width?: number; opacity?: number }
  | { kind: "text"; x: number; y: number; text: string; fill: string; size: number; family?: string; opacity?: number };

/** A finished piece of art, in a form any platform can draw. */
export interface ArtWork {
  /** Every style draws into the same window, so the frame never moves. */
  viewBox: string;
  palette: Palette;
  shapes: Shape[];
  texture: TextureKind;
  holo: HoloKind;
}

export interface StyleCredit {
  id: string;
  name: string;
  /** Who to credit on the card face. */
  artist: string;
  /** The real-world medium being evoked. */
  medium: string;
}

export interface ArtContext {
  /** Deterministic stream — call it for every random choice. */
  next: () => number;
  /** The agent's element, so art can respond to what the agent does. */
  element: string;
  rarity: string;
  seed: number;
}

export interface ArtStyle extends StyleCredit {
  render(ctx: ArtContext): ArtWork;
}

/** The art window every style paints inside. Fixed, so the frame is iconic. */
export const ART_VIEWBOX = "0 0 100 100";

/* ── shared helpers ──────────────────────────────────────────────────── */

const TAU = Math.PI * 2;

/** Pick one of a list, deterministically. */
const pick = <T,>(next: () => number, items: readonly T[]): T =>
  items[Math.floor(next() * items.length) % items.length];

const round = (n: number) => Math.round(n * 100) / 100;

/** Element hues, so a style stays true to what the agent does. */
const ELEMENT_HUE: Record<string, number> = {
  spirit: 200,
  aether: 265,
  ember: 22,
  stone: 40,
  void: 330,
};

const hsl = (h: number, s: number, l: number) => `hsl(${Math.round(h)} ${Math.round(s)}% ${Math.round(l)}%)`;

function elementPalette(element: string, next: () => number, opts?: { dark?: boolean }): Palette {
  const hue = ELEMENT_HUE[element] ?? 210;
  const drift = (next() - 0.5) * 24;
  if (opts?.dark) {
    return {
      from: hsl(hue + drift, 30, 12),
      to: hsl(hue + drift + 30, 40, 22),
      accent: hsl(hue + drift, 85, 62),
      ink: hsl(hue, 20, 95),
      spot: hsl(hue + 160, 70, 60),
    };
  }
  return {
    from: hsl(hue + drift, 70, 95),
    to: hsl(hue + drift + 20, 60, 80),
    accent: hsl(hue + drift, 75, 48),
    ink: hsl(hue, 45, 16),
    spot: hsl(hue + 150, 60, 55),
  };
}

/** A closed star-polygon — the shape language the original card used. */
function starPath(next: () => number, points: number, cx = 50, cy = 50, min = 18, span = 26): string {
  const segments: string[] = [];
  for (let i = 0; i < points; i++) {
    const angle = (i / points) * TAU - Math.PI / 2;
    const radius = min + next() * span;
    segments.push(
      `${i === 0 ? "M" : "L"}${round(cx + Math.cos(angle) * radius)},${round(cy + Math.sin(angle) * radius)}`,
    );
  }
  return segments.join(" ") + " Z";
}

/* ── the styles ──────────────────────────────────────────────────────── */

/** House style: crisp vector geometry, prismatic foil. The set's anchor. */
const prism: ArtStyle = {
  id: "prism",
  name: "Prism",
  artist: "RAPP Studio",
  medium: "vector geometry",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    const rings = 3 + Math.floor(next() * 3);
    for (let i = 0; i < rings; i++) {
      shapes.push({
        kind: "path",
        d: starPath(next, 5 + Math.floor(next() * 4), 50, 50, 10 + i * 6, 18),
        stroke: palette.accent,
        width: round(0.6 + next() * 1.2),
        opacity: round(0.35 + i * 0.18),
      });
    }
    shapes.push({ kind: "circle", cx: 50, cy: 50, r: round(6 + next() * 5), fill: palette.accent, opacity: 0.9 });
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "grain", holo: "prismatic" };
  },
};

/** Ukiyo-e: heavy contour, flat inks, visible paper. */
const woodblock: ArtStyle = {
  id: "woodblock",
  name: "Floating World",
  artist: "after Hokusai",
  medium: "ukiyo-e woodblock",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    // Stacked waves: a few thick, flat, overlapping arcs.
    for (let i = 0; i < 4; i++) {
      const y = 30 + i * 16;
      const lift = 8 + next() * 14;
      shapes.push({
        kind: "path",
        d: `M0,${round(y + lift)} C25,${round(y - lift)} 75,${round(y + lift * 1.4)} 100,${round(y - lift * 0.4)} L100,100 L0,100 Z`,
        fill: i % 2 === 0 ? palette.accent : palette.spot ?? palette.accent,
        opacity: round(0.28 + i * 0.16),
      });
    }
    shapes.push({ kind: "circle", cx: round(28 + next() * 44), cy: round(22 + next() * 10), r: round(9 + next() * 5), fill: palette.ink, opacity: 0.85 });
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "paper", holo: "none" };
  },
};

/** Risograph: two spot inks, halftone, deliberate misregistration. */
const riso: ArtStyle = {
  id: "riso",
  name: "Duplicator",
  artist: "Riso Collective",
  medium: "risograph screenprint",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    const offset = () => round((next() - 0.5) * 5);
    for (let layer = 0; layer < 2; layer++) {
      const ink = layer === 0 ? palette.accent : palette.spot ?? palette.ink;
      const dx = offset();
      const dy = offset();
      const sides = 3 + Math.floor(next() * 4);
      shapes.push({
        kind: "path",
        d: starPath(next, sides, 50 + dx, 50 + dy, 16, 24),
        fill: ink,
        opacity: 0.62,
      });
    }
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "halftone", holo: "none" };
  },
};

/** Pure type: the card is drawn out of characters. */
const ascii: ArtStyle = {
  id: "ascii",
  name: "Teletype",
  artist: "Terminal Anonymous",
  medium: "ASCII / monospace",
  render({ next, element }) {
    const palette = elementPalette(element, next, { dark: true });
    const glyphs = ["#", "@", "%", "*", "+", "=", "-", ".", ":", "░", "▒", "▓"];
    const shapes: Shape[] = [];
    const cols = 16;
    const rows = 16;
    for (let r = 0; r < rows; r++) {
      let line = "";
      for (let c = 0; c < cols; c++) {
        // Radial falloff: dense in the middle, sparse at the edges.
        const dx = (c - cols / 2) / (cols / 2);
        const dy = (r - rows / 2) / (rows / 2);
        const density = 1 - Math.min(1, Math.hypot(dx, dy));
        line += density > next() * 0.9 ? pick(next, glyphs) : " ";
      }
      shapes.push({
        kind: "text",
        x: 6,
        y: round(10 + r * 5.6),
        text: line,
        fill: r % 4 === 0 ? palette.accent : palette.ink,
        size: 5.4,
        family: "monospace",
        opacity: 0.9,
      });
    }
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "scanlines", holo: "linear" };
  },
};

/** Engraved naturalist plate: fine hatching, no fills. */
const botanical: ArtStyle = {
  id: "botanical",
  name: "Herbarium",
  artist: "Plate XIV",
  medium: "copperplate engraving",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    const stems = 3 + Math.floor(next() * 3);
    for (let s = 0; s < stems; s++) {
      const baseX = round(20 + (s / Math.max(1, stems - 1)) * 60);
      const sway = round((next() - 0.5) * 30);
      shapes.push({
        kind: "path",
        d: `M${baseX},96 C${baseX + sway},70 ${baseX - sway},44 ${round(baseX + sway / 2)},14`,
        stroke: palette.ink,
        width: 0.8,
        opacity: 0.9,
      });
      const leaves = 3 + Math.floor(next() * 4);
      for (let l = 0; l < leaves; l++) {
        const y = round(24 + l * (60 / leaves));
        const side = l % 2 === 0 ? 1 : -1;
        shapes.push({
          kind: "path",
          d: `M${baseX},${y} q${side * (7 + next() * 8)},-6 ${side * (13 + next() * 8)},2 q${-side * 7},7 ${-side * (13 + next() * 8)},-2 Z`,
          stroke: palette.accent,
          width: 0.5,
          opacity: 0.85,
        });
      }
    }
    // Hatched ground line.
    for (let i = 0; i < 14; i++) {
      const x = round(8 + i * 6);
      shapes.push({ kind: "line", x1: x, y1: 96, x2: round(x + 4), y2: round(90 + next() * 4), stroke: palette.ink, width: 0.4, opacity: 0.5 });
    }
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "paper", holo: "pearl" };
  },
};

/** Neon grid receding to a horizon. */
const vapor: ArtStyle = {
  id: "vapor",
  name: "Horizon",
  artist: "Night Drive",
  medium: "neon / CRT",
  render({ next, element }) {
    const palette = elementPalette(element, next, { dark: true });
    const shapes: Shape[] = [];
    const horizon = 54;
    shapes.push({ kind: "circle", cx: 50, cy: round(horizon - 10), r: round(14 + next() * 8), fill: palette.accent, opacity: 0.8 });
    for (let i = 0; i < 9; i++) {
      const t = (i + 1) / 10;
      const y = round(horizon + t * t * 46);
      shapes.push({ kind: "line", x1: 0, y1: y, x2: 100, y2: y, stroke: palette.spot ?? palette.accent, width: 0.5, opacity: round(0.9 - t * 0.5) });
    }
    for (let i = -6; i <= 6; i++) {
      shapes.push({ kind: "line", x1: 50, y1: horizon, x2: round(50 + i * 22), y2: 100, stroke: palette.spot ?? palette.accent, width: 0.4, opacity: 0.45 });
    }
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "scanlines", holo: "shattered" };
  },
};

/** Sumi-e: a few loaded brush strokes and a great deal of empty paper. */
const sumi: ArtStyle = {
  id: "sumi",
  name: "One Breath",
  artist: "Ink Studio",
  medium: "sumi-e brush",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    const strokes = 2 + Math.floor(next() * 3);
    for (let i = 0; i < strokes; i++) {
      const x0 = round(15 + next() * 25);
      const y0 = round(20 + next() * 30);
      const x1 = round(55 + next() * 30);
      const y1 = round(50 + next() * 35);
      shapes.push({
        kind: "path",
        d: `M${x0},${y0} C${round(x0 + 20)},${round(y0 + 25)} ${round(x1 - 25)},${round(y1 - 20)} ${x1},${y1}`,
        stroke: palette.ink,
        width: round(2 + next() * 5),
        opacity: round(0.55 + next() * 0.4),
      });
    }
    shapes.push({ kind: "circle", cx: round(70 + next() * 14), cy: round(16 + next() * 8), r: round(3 + next() * 2), fill: palette.accent, opacity: 0.9 });
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "paper", holo: "none" };
  },
};

/** Bauhaus: primary shapes, hard edges, nothing decorative. */
const bauhaus: ArtStyle = {
  id: "bauhaus",
  name: "Werkstatt",
  artist: "Weimar School",
  medium: "geometric abstraction",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const inks = [palette.accent, palette.spot ?? palette.ink, palette.ink];
    const shapes: Shape[] = [];
    const count = 4 + Math.floor(next() * 4);
    for (let i = 0; i < count; i++) {
      const form = pick(next, ["circle", "rect", "tri"] as const);
      const fill = pick(next, inks);
      const x = round(10 + next() * 60);
      const y = round(10 + next() * 60);
      const size = round(12 + next() * 26);
      if (form === "circle") {
        shapes.push({ kind: "circle", cx: round(x + size / 2), cy: round(y + size / 2), r: round(size / 2), fill, opacity: 0.85 });
      } else if (form === "rect") {
        shapes.push({ kind: "rect", x, y, w: size, h: round(size * (0.5 + next())), fill, opacity: 0.85 });
      } else {
        shapes.push({ kind: "path", d: `M${x},${round(y + size)} L${round(x + size / 2)},${y} L${round(x + size)},${round(y + size)} Z`, fill, opacity: 0.85 });
      }
    }
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "none", holo: "linear" };
  },
};

/** Leaded glass: irregular cells, dark cames, light behind. */
const stainedglass: ArtStyle = {
  id: "stainedglass",
  name: "Rosette",
  artist: "Guild of Glaziers",
  medium: "leaded stained glass",
  render({ next, element }) {
    const palette = elementPalette(element, next);
    const shapes: Shape[] = [];
    const wedges = 8 + Math.floor(next() * 5);
    for (let i = 0; i < wedges; i++) {
      const a0 = (i / wedges) * TAU;
      const a1 = ((i + 1) / wedges) * TAU;
      const rOuter = 40 + next() * 6;
      const rInner = 12 + next() * 8;
      const p = (a: number, r: number) => `${round(50 + Math.cos(a) * r)},${round(50 + Math.sin(a) * r)}`;
      shapes.push({
        kind: "path",
        d: `M${p(a0, rInner)} L${p(a0, rOuter)} L${p(a1, rOuter)} L${p(a1, rInner)} Z`,
        fill: i % 3 === 0 ? palette.accent : i % 3 === 1 ? palette.spot ?? palette.accent : palette.from,
        stroke: palette.ink,
        width: 1.2,
        opacity: 0.9,
      });
    }
    shapes.push({ kind: "circle", cx: 50, cy: 50, r: round(8 + next() * 4), fill: palette.ink, opacity: 0.9 });
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "weave", holo: "prismatic" };
  },
};

/** Drafting table: white lines on blue, dimensions and all. */
const blueprint: ArtStyle = {
  id: "blueprint",
  name: "Drafting Table",
  artist: "Sheet 3 of 7",
  medium: "cyanotype blueprint",
  render({ next, element }) {
    const palette: Palette = {
      from: "hsl(214 65% 26%)",
      to: "hsl(214 70% 16%)",
      accent: "hsl(200 30% 92%)",
      ink: "hsl(200 25% 88%)",
      spot: "hsl(38 90% 66%)",
    };
    const shapes: Shape[] = [];
    for (let i = 1; i < 10; i++) {
      const v = round(i * 10);
      shapes.push({ kind: "line", x1: v, y1: 0, x2: v, y2: 100, stroke: palette.accent, width: 0.25, opacity: 0.22 });
      shapes.push({ kind: "line", x1: 0, y1: v, x2: 100, y2: v, stroke: palette.accent, width: 0.25, opacity: 0.22 });
    }
    const w = round(30 + next() * 26);
    const h = round(24 + next() * 26);
    const x = round((100 - w) / 2);
    const y = round((100 - h) / 2);
    shapes.push({ kind: "rect", x, y, w, h, stroke: palette.ink, width: 1, opacity: 0.95 });
    shapes.push({ kind: "circle", cx: round(x + w / 2), cy: round(y + h / 2), r: round(Math.min(w, h) / 3), stroke: palette.spot ?? palette.ink, width: 0.8, opacity: 0.9 });
    shapes.push({ kind: "line", x1: x, y1: round(y + h + 6), x2: round(x + w), y2: round(y + h + 6), stroke: palette.spot ?? palette.ink, width: 0.5, opacity: 0.8 });
    shapes.push({ kind: "text", x, y: round(y + h + 12), text: `${w} × ${h}`, fill: palette.ink, size: 5, family: "monospace", opacity: 0.85 });
    return { viewBox: ART_VIEWBOX, palette, shapes, texture: "grain", holo: "none" };
  },
};

/* ── the registry ────────────────────────────────────────────────────── */

/** Every style in the set. Adding an artist is adding one entry here. */
export const ART_STYLES: readonly ArtStyle[] = [
  prism,
  woodblock,
  riso,
  ascii,
  botanical,
  vapor,
  sumi,
  bauhaus,
  stainedglass,
  blueprint,
];

export const DEFAULT_STYLE_ID = prism.id;

export function styleById(id: string | undefined): ArtStyle {
  return ART_STYLES.find((s) => s.id === id) ?? prism;
}

/** Which artist drew *your* card. Deterministic, so it is part of the pull —
 *  but a cursed agent always prints in the dark house style, because a warning
 *  should never be pretty by accident. */
export function styleForSeed(seed: number, rarity: string): ArtStyle {
  if (rarity === "cursed") return vapor;
  return ART_STYLES[seed % ART_STYLES.length];
}

export function credits(): StyleCredit[] {
  return ART_STYLES.map(({ id, name, artist, medium }) => ({ id, name, artist, medium }));
}
