#!/usr/bin/env node
// Render every card style to a static HTML gallery, so the art can be looked
// at (and screenshotted by an agent) without booting the whole app.
import { readFileSync, writeFileSync } from "node:fs";
import { inspectAgentSource } from "../common/agentcard.ts";
import { mintCard } from "../common/cardart.ts";
import { ART_STYLES } from "../common/cardstyles.ts";
import { encodeShareUrl } from "../common/agentshare.ts";
import { encodeQr, qrPath } from "../common/qr.ts";

const spec = {
  name: "weekly-billing", className: "WeeklyBilling",
  title: "Weekly Unbilled Summary", description: "Tally unbilled time and email each client.",
  intent: "Automate the weekly billing review.",
  steps: [
    { title: "Fetch entries", detail: "Retrieve unbilled time grouped by client." },
    { title: "Total per client", detail: "Sum billable hours and dollar value for each client." },
    { title: "Send summaries", detail: "Email each client their outstanding total." },
    { title: "Log the run", detail: "Record what was sent and to whom." },
    { title: "Report back", detail: "Summarise the week for the operator." },
  ],
  parameters: [{ name: "run_date", description: "Period end", type: "string", required: false }],
};

const agentSource = `
class WeeklyBilling(BasicAgent):
    def __init__(self):
        self.name = "WeeklyBilling"
        self.metadata = {"description": "Tally unbilled time and email each client."}
    def perform(self, **kwargs):
        steps = ["1. Fetch entries: Retrieve unbilled time grouped by client.", "2. Total per client: Sum hours and value.", "3. Send summaries: Email each client.", "4. Log the run: Record what was sent.", "5. Report back: Summarise the week."]
        return steps
`;

const cursedSource = agentSource.replace("def perform", "import subprocess\n    def perform");

const shape = (s) => {
  const o = s.opacity !== undefined ? ` opacity="${s.opacity}"` : "";
  const st = s.stroke ? ` stroke="${s.stroke}" stroke-width="${s.width ?? 1}" stroke-linecap="round" stroke-linejoin="round"` : "";
  const f = ` fill="${s.fill ?? "none"}"`;
  switch (s.kind) {
    case "path": return `<path d="${s.d}"${f}${st}${o}/>`;
    case "circle": return `<circle cx="${s.cx}" cy="${s.cy}" r="${s.r}"${f}${st}${o}/>`;
    case "rect": return `<rect x="${s.x}" y="${s.y}" width="${s.w}" height="${s.h}" rx="${s.radius ?? 0}"${f}${st}${o}/>`;
    case "line": return `<line x1="${s.x1}" y1="${s.y1}" x2="${s.x2}" y2="${s.y2}" stroke="${s.stroke}" stroke-width="${s.width ?? 1}"${o}/>`;
    case "text": return `<text x="${s.x}" y="${s.y}" fill="${s.fill}" font-size="${s.size}" font-family="${s.family ?? "inherit"}"${o} style="white-space:pre">${s.text.replace(/[<>&]/g, c => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]))}</text>`;
  }
};

const url = encodeShareUrl(spec).url;
const qr = encodeQr(url);

function renderCard(card, styleId, label) {
  const face = mintCard(card, styleId);
  const art = face.art;
  return `
  <figure class="slot">
    <div class="tcg holo-${art.holo} rarity-${face.rarity}" style="--from:${art.palette.from};--to:${art.palette.to};--accent:${art.palette.accent};--ink:${art.palette.ink};--gx:34%;--gy:28%;--rx:0deg;--ry:0deg">
      <div class="tcg-inner"><div class="tcg-face tcg-front">
        <div class="tcg-foil" style="opacity:1"></div>
        <header class="tcg-head"><span class="tcg-title">${face.title}</span><span class="tcg-trust"><b>${face.trust}</b> TRUST</span></header>
        <div class="tcg-window">
          <svg class="card-art" viewBox="${art.viewBox}" preserveAspectRatio="xMidYMid slice">
            <defs><linearGradient id="bg-${styleId ?? face.style.id}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="${art.palette.from}"/><stop offset="100%" stop-color="${art.palette.to}"/>
            </linearGradient></defs>
            <rect width="100" height="100" fill="url(#bg-${styleId ?? face.style.id})"/>
            ${art.shapes.map(shape).join("")}
          </svg>
          <div class="tcg-texture texture-${art.texture}"></div>
          <div class="tcg-window-gloss"></div>
        </div>
        <div class="tcg-body">
          <div class="tcg-typeline"><span class="tcg-element">${face.element}</span><span class="tcg-rarity">${face.rarity}</span></div>
          ${face.moves.map(m => `<div class="tcg-move"><span class="tcg-cost">${"●".repeat(m.cost)}</span><span class="tcg-move-name">${m.name}</span><span class="tcg-power">${m.power}</span><p class="tcg-move-text">${m.text}</p></div>`).join("")}
        </div>
        <footer class="tcg-foot"><span class="tcg-flavor">${face.flavor}</span><span class="tcg-credit">${face.style.name} · ${face.style.medium} · ${face.style.artist}</span><span class="tcg-dex">${face.dex}</span></footer>
      </div></div>
    </div>
    <figcaption>${label ?? face.style.name}</figcaption>
  </figure>`;
}

const card = inspectAgentSource(agentSource);
const cursed = inspectAgentSource(cursedSource);

const back = `
  <figure class="slot">
    <div class="tcg" style="--from:#e8f6ff;--to:#b9e2ff;--accent:#3aa6ff;--ink:#0b2a3f">
      <div class="tcg-inner"><div class="tcg-face tcg-back" style="transform:none">
        <span class="tcg-back-mark">RAPP</span>
        <svg class="tcg-qr" viewBox="-2 -2 ${qr.size + 4} ${qr.size + 4}">
          <rect x="-2" y="-2" width="${qr.size + 4}" height="${qr.size + 4}" fill="#fff" rx="1"/>
          <path d="${qrPath(qr)}" fill="#0b0b10" shape-rendering="crispEdges"/>
        </svg>
        <p class="tcg-back-hint">Point a phone at this to receive <b>Weekly Unbilled Summary</b>.<br/>It carries the recipe, never the code — their mirror builds it themselves.</p>
        <span class="tcg-back-dex">${mintCard(card).dex}</span>
      </div></div>
    </div>
    <figcaption>the back — scan to trade</figcaption>
  </figure>`;

const css = readFileSync(new URL("../src/AgentTradingCard.css", import.meta.url), "utf8");
writeFileSync(new URL("../.card-preview.html", import.meta.url), `<!doctype html><meta charset="utf-8">
<title>RAPP agent cards</title>
<style>
 body{margin:0;padding:36px;background:#0f1117;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;color:#e8ecf5}
 h1{font-size:19px;font-weight:650;margin:0 0 4px}
 p.sub{margin:0 0 28px;opacity:.6;font-size:12.5px}
 .grid{display:flex;flex-wrap:wrap;gap:30px}
 .slot{margin:0}
 figcaption{margin-top:9px;font-size:11px;opacity:.65;text-align:center;width:300px}
 ${css}
</style>
<h1>One frame. Ten artists.</h1>
<p class="sub">Identity is invariant — same silhouette, same stats, same dex number. Only the medium changes.</p>
<div class="grid">
${ART_STYLES.map(s => renderCard(card, s.id)).join("")}
${renderCard(cursed, undefined, "a cursed agent — it runs shell commands")}
${back}
</div>`);
console.log("wrote .card-preview.html  |  share url", url.length, "chars, QR v" + qr.version);
