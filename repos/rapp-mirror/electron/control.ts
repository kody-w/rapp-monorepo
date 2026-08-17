import http from "node:http";

import { parseEnvelope, type ChatTurn } from "../common/ipc.ts";
import { chat, health } from "./brainstem.ts";
import { acceptAgent, receiveAgentCard, receiveAgentFile, shareAgent } from "./agentshare.ts";
import { announceArrival } from "./arrival.ts";
import { diagnosticsSnapshot, eventsSince } from "./diagnostics.ts";
import { runDoctor } from "./doctor.ts";
import { deployAgent, distill, exportAll, normalizeSpec } from "./forge.ts";
import { trustedLocalRequest } from "./guard.ts";
import { createLogger } from "./logger.ts";
import { decideRehearsal, loadRehearsal, rehearse, revise } from "./rehearsal.ts";
import { tts, voiceStatus } from "./voice.ts";

/**
 * The autonomy surface: a loopback-only HTTP control plane so a CLI (or any
 * local agent — Claude, scripts, cron) can drive the mirror headlessly:
 *
 *   GET  /status                          engine + voice health
 *   GET  /doctor                          honest subsystem verdicts
 *   GET  /diagnostics                     durable evidence snapshot
 *   GET  /events?since=<seq>              evidence events newer than a cursor
 *   POST /share  {spec}                   file to AirDrop + link for the card
 *   POST /receive {file} | {url}          inspect an arriving agent (installs nothing)
 *   POST /accept {spec, acceptDangerous?, force?}  the only door into the brainstem
 *   POST /chat   {text, sessionId?, history?}   -> chat result + parsed envelope
 *   POST /tts    {text}                   -> audio/wav (pipe to afplay)
 *   POST /forge  {history?, screenContext?, sessionId?} -> distilled spec
 *   POST /forge/export {spec}             -> artifact paths
 *   POST /forge/deploy {spec, force?}     -> live-deploy result (rehearsal-gated)
 *   POST /rehearse {spec, sessionId?}     -> full virtual-twin dry-run (may take minutes)
 *   POST /rehearse/confirm {name, note?}  -> countersign "fully done"
 *   POST /rehearse/reject  {name, note?}  -> reject + revised spec (objection folded in)
 *   GET  /rehearse/status?name=<spec>     -> latest transcript for a spec
 *
 * `bin/mirrorctl.mjs` wraps all of it. Binds 127.0.0.1 only; the UI-level
 * twin of this is the renderer's `window.mirrorDebug` console API reachable
 * over the Chrome remote-debugging port (9333 in dev).
 */

const log = createLogger("Control");

export function controlPort(): number {
  return Number.parseInt(process.env.MIRROR_CONTROL_PORT || "8474", 10);
}

const readBody = (req: http.IncomingMessage): Promise<string> =>
  new Promise((resolve) => {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => resolve(body));
  });

let server: http.Server | null = null;

export function startControlServer(): void {
  server = http.createServer(async (req, res) => {
    const json = (code: number, value: unknown) => {
      const body = JSON.stringify(value, null, 1);
      res.writeHead(code, { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) });
      res.end(body);
    };
    try {
      const url = req.url || "/";
      if (req.method === "GET" && url.startsWith("/status")) {
        return json(200, { engine: await health(), voice: await voiceStatus() });
      }
      if (req.method === "GET" && url.startsWith("/doctor")) {
        const report = await runDoctor();
        return json(report.ok ? 200 : 503, report);
      }
      if (req.method === "GET" && url.startsWith("/diagnostics")) {
        return json(200, diagnosticsSnapshot());
      }
      if (req.method === "GET" && url.startsWith("/events")) {
        const since = Number.parseInt(new URL(url, "http://127.0.0.1").searchParams.get("since") || "0", 10);
        const snapshot = diagnosticsSnapshot();
        return json(200, { ok: true, cursor: snapshot.seq, events: eventsSince(Number.isFinite(since) ? since : 0) });
      }
      if (req.method === "POST" && !trustedLocalRequest(req)) {
        return json(403, { error: "control plane accepts local JSON clients only" });
      }
      const body = req.method === "POST" ? JSON.parse((await readBody(req)) || "{}") : {};
      if (req.method === "POST" && url.startsWith("/chat")) {
        const result = await chat(
          String(body.text ?? ""),
          (Array.isArray(body.history) ? body.history : []) as ChatTurn[],
          String(body.sessionId ?? "mirrorctl"),
        );
        return json(result.ok ? 200 : 502, {
          ...result,
          envelope: result.ok ? parseEnvelope(result.response ?? "") : undefined,
        });
      }
      if (req.method === "POST" && url.startsWith("/tts")) {
        const wav = await tts(String(body.text ?? ""));
        if (!wav) return json(503, { error: "VibeVoice not ready — system voice lives in the app only" });
        const buf = Buffer.from(wav);
        res.writeHead(200, { "Content-Type": "audio/wav", "Content-Length": buf.length });
        return res.end(buf);
      }
      if (req.method === "POST" && url.startsWith("/share")) {
        return json(200, shareAgent(body.spec ?? body));
      }
      if (req.method === "POST" && url.startsWith("/receive")) {
        // Inspect only. Nothing here writes into the brainstem.
        const received = body.url
          ? receiveAgentCard(String(body.url))
          : receiveAgentFile(String(body.file ?? ""));
        // Same consent card as an AirDrop, so a driver and a human see one door.
        announceArrival(received);
        return json(received.ok ? 200 : 400, received);
      }
      if (req.method === "POST" && url.startsWith("/accept")) {
        const result = await acceptAgent(body.spec ?? body, {
          acceptDangerous: body.acceptDangerous === true,
          force: body.force === true,
        });
        return json(result.ok ? 200 : result.refused ? 403 : 409, result);
      }
      if (req.method === "POST" && url.startsWith("/forge/export")) {
        return json(200, { ok: true, ...exportAll(normalizeSpec(body.spec ?? body)) });
      }
      if (req.method === "POST" && url.startsWith("/forge/deploy")) {
        return json(200, await deployAgent(normalizeSpec(body.spec ?? body), { force: body.force === true }));
      }
      if (req.method === "GET" && url.startsWith("/rehearse/status")) {
        const name = new URL(url, "http://127.0.0.1").searchParams.get("name") || "";
        const t = loadRehearsal(name);
        return t ? json(200, { ok: true, transcript: t }) : json(404, { ok: false, error: `"${name}" has never been rehearsed` });
      }
      if (req.method === "POST" && url.startsWith("/rehearse/confirm")) {
        const r = decideRehearsal(String(body.name ?? ""), "confirmed", body.note ? String(body.note) : undefined, "control");
        return json(r.ok ? 200 : 409, r);
      }
      if (req.method === "POST" && url.startsWith("/rehearse/reject")) {
        const r = decideRehearsal(String(body.name ?? ""), "rejected", body.note ? String(body.note) : undefined, "control");
        if (!r.ok || !r.transcript) return json(409, r);
        // Fold the objection back in: hand back a revised spec that must
        // itself be rehearsed (its hash differs, so the gate stays closed).
        try {
          const revised = await revise(body.spec ?? r.transcript.spec, String(body.note ?? ""), String(body.sessionId ?? "mirrorctl"));
          return json(200, { ...r, revised });
        } catch {
          return json(200, r); // rejection stands even when revision fails
        }
      }
      if (req.method === "POST" && url.startsWith("/rehearse")) {
        const t = await rehearse(body.spec ?? body, String(body.sessionId ?? "mirrorctl"));
        return json(200, { ok: t.state === "awaiting-confirmation", transcript: t });
      }
      if (req.method === "POST" && url.startsWith("/forge")) {
        const spec = await distill(
          (Array.isArray(body.history) ? body.history : []) as ChatTurn[],
          Array.isArray(body.screenContext) ? body.screenContext : [],
          String(body.sessionId ?? "mirrorctl"),
        );
        return json(200, { ok: true, spec });
      }
      return json(404, { error: "unknown route" });
    } catch (err) {
      return json(500, { error: err instanceof Error ? err.message : String(err) });
    }
  });
  server.listen(controlPort(), "127.0.0.1", () =>
    log.info(`control plane on http://127.0.0.1:${controlPort()}`),
  );
}

export function stopControlServer(): void {
  server?.close();
  server = null;
}
