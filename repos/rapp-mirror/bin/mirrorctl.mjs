#!/usr/bin/env node
// mirrorctl — drive the RAPP Mirror autonomously from any shell.
//
//   mirrorctl status
//   mirrorctl doctor                     # subsystem verdicts; exits 1 when unavailable
//   mirrorctl diagnostics                # evidence ledger snapshot
//   mirrorctl events [since]             # evidence events newer than a cursor
//   mirrorctl chat "what are my agents?"
//   mirrorctl forge                       # distill the app's idea of a spec from args
//   mirrorctl forge "conversation text"   # distill from ad-hoc text
//   mirrorctl export spec.json            # render agent.py + SKILL.md + MCS zip
//   mirrorctl rehearse spec.json          # virtual-twin dry-run (may take minutes)
//   mirrorctl rehearse-status <name>      # latest transcript for a spec name
//   mirrorctl rehearse-confirm <name>     # countersign "fully done"
//   mirrorctl rehearse-reject <name> "why"  # reject; prints a revised spec
//   mirrorctl deploy spec.json [--force]  # rehearsal-gated live deploy
//   mirrorctl say "hello"                 # VibeVoice wav to stdout (pipe to afplay -)
//
//   mirrorctl share spec.json             # a file to AirDrop + the card's rapp:// link
//   mirrorctl receive agent.py            # inspect an AirDropped agent (installs nothing)
//   mirrorctl receive "rapp://agent?..."  # inspect a scanned card (re-rendered locally)
//   mirrorctl accept spec.json [--accept-dangerous] [--force]   # the only door in
//
// Talks to the mirror app's loopback control plane (MIRROR_CONTROL_PORT, 8474).
// Deploy refuses an unrehearsed or unconfirmed spec by default — rehearse and
// confirm first, or pass --force (recorded, never the default).

import { readFileSync } from "node:fs";

const BASE = `http://127.0.0.1:${process.env.MIRROR_CONTROL_PORT || 8474}`;
const [cmd, ...rest] = process.argv.slice(2);

const post = async (path, body, raw = false) => {
  const r = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (raw) return Buffer.from(await r.arrayBuffer());
  return r.json();
};

const out = (v) => console.log(JSON.stringify(v, null, 1));

const getJson = async (path) => {
  const r = await fetch(BASE + path);
  return r.json();
};

const doctorSymbol = (status) => status === "ok" ? "✓" : status === "degraded" ? "!" : "✗";

try {
  switch (cmd) {
    case "status":
      out(await getJson("/status"));
      break;
    case "doctor": {
      const report = await getJson("/doctor");
      console.log(`RAPP Mirror ${report.app} doctor @ ${report.at}`);
      for (const check of report.checks || []) {
        console.log(`${doctorSymbol(check.status)} ${String(check.id).padEnd(11)} ${check.detail}`);
        if (check.nextAction) console.log(`  -> ${check.nextAction}`);
      }
      if (!report.ok) process.exit(1);
      break;
    }
    case "diagnostics":
      out(await getJson("/diagnostics"));
      break;
    case "events":
      out(await getJson(`/events?since=${encodeURIComponent(rest[0] || "0")}`));
      break;
    case "chat":
      out(await post("/chat", { text: rest.join(" ") }));
      break;
    case "forge":
      out(await post("/forge", rest.length
        ? { history: [{ role: "user", content: rest.join(" ") }] }
        : {}));
      break;
    case "export":
      out(await post("/forge/export", { spec: JSON.parse(readFileSync(rest[0], "utf8")) }));
      break;
    case "rehearse":
      console.error("rehearsing — the twin runs every step through the brainstem; this can take minutes…");
      out(await post("/rehearse", { spec: JSON.parse(readFileSync(rest[0], "utf8")) }));
      break;
    case "rehearse-status":
      out(await getJson(`/rehearse/status?name=${encodeURIComponent(rest[0] || "")}`));
      break;
    case "rehearse-confirm":
      out(await post("/rehearse/confirm", { name: rest[0], note: rest.slice(1).join(" ") || undefined }));
      break;
    case "rehearse-reject":
      out(await post("/rehearse/reject", { name: rest[0], note: rest.slice(1).join(" ") || undefined }));
      break;
    case "deploy": {
      const force = rest.includes("--force");
      const specFile = rest.find((a) => a !== "--force");
      const r = await post("/forge/deploy", { spec: JSON.parse(readFileSync(specFile, "utf8")), force });
      if (r.needsRehearsal) console.error("deploy refused: " + r.error + "\n  -> mirrorctl rehearse " + specFile + "  then  mirrorctl rehearse-confirm <name>  (or --force)");
      out(r);
      break;
    }
    case "share":
      out(await post("/share", { spec: JSON.parse(readFileSync(rest[0], "utf8")) }));
      break;
    case "receive": {
      const arg = rest[0] || "";
      const r = await post("/receive", arg.startsWith("rapp://") ? { url: arg } : { file: arg });
      if (r.ok) {
        console.error(`\n  ${r.summary}\n  parked at ${r.pendingPath}` +
          (r.dangerous ? "\n  ⚠ DANGEROUS — accept it explicitly only if you trust the sender\n" : "\n"));
      }
      out(r);
      break;
    }
    case "accept": {
      const dangerous = rest.includes("--accept-dangerous");
      const force = rest.includes("--force");
      const file = rest.find((a) => !a.startsWith("--"));
      const r = await post("/accept", {
        spec: JSON.parse(readFileSync(file, "utf8")),
        acceptDangerous: dangerous,
        force,
      });
      if (r.refused) console.error("refused: " + r.error + "\n  -> re-run with --accept-dangerous if you trust it");
      out(r);
      if (!r.ok) process.exitCode = 1;
      break;
    }
    case "say":
      process.stdout.write(await post("/tts", { text: rest.join(" ") }, true));
      break;
    default:
      console.error("usage: mirrorctl status|doctor|diagnostics|events|chat|forge|export|rehearse|rehearse-status|rehearse-confirm|rehearse-reject|deploy|say …");
      process.exit(2);
  }
} catch (err) {
  console.error("mirrorctl:", err.message, `(is the mirror app running? ${BASE})`);
  process.exit(1);
}
