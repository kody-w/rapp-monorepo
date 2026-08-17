import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { resetSecretCache } from "./brainstem.ts";
import { runDoctor, type DoctorCheck } from "./doctor.ts";

function listen(handler: http.RequestListener): Promise<{ server: http.Server; url: string }> {
  const server = http.createServer(handler);
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({ server, url: `http://127.0.0.1:${(server.address() as { port: number }).port}` }),
    ),
  );
}

async function fakeBrainstem(health: Record<string, unknown>): Promise<{ server: http.Server; url: string }> {
  return listen((_req, res) => {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(health));
  });
}

async function fakeInstaller(body = "#!/usr/bin/env bash\necho ok\n", status = 200): Promise<{ server: http.Server; url: string }> {
  return listen((_req, res) => {
    res.writeHead(status, { "Content-Type": "text/plain" });
    res.end(body);
  });
}

async function fakeVoice(): Promise<{ server: http.Server; url: string }> {
  return listen((req, res) => {
    if (req.url === "/health") {
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ status: "ready", speaker: "test", device: "cpu" }));
      return;
    }
    res.end("ok");
  });
}

async function withDoctorEnv<T>(
  opts: {
    brainstemHealth?: Record<string, unknown>;
    brainstemUrl?: string;
    installerBody?: string;
    installerStatus?: number;
    agentsDir?: string;
    exportsDir?: string;
    rehearsalsDir?: string;
  },
  body: () => Promise<T>,
): Promise<T> {
  const servers: http.Server[] = [];
  const brainstem = opts.brainstemUrl
    ? null
    : await fakeBrainstem(opts.brainstemHealth || { status: "ok", version: "0.6.16", model: "fake", agents: ["A"], quarantined: [] });
  if (brainstem) servers.push(brainstem.server);
  const installer = await fakeInstaller(opts.installerBody, opts.installerStatus);
  servers.push(installer.server);
  const voice = await fakeVoice();
  servers.push(voice.server);
  const agentsDir = opts.agentsDir || mkdtempSync(path.join(os.tmpdir(), "doctor-agents-"));
  const exportsDir = opts.exportsDir || mkdtempSync(path.join(os.tmpdir(), "doctor-exports-"));
  const rehearsalsDir = opts.rehearsalsDir || mkdtempSync(path.join(os.tmpdir(), "doctor-rehearsals-"));
  const secretFile = path.join(mkdtempSync(path.join(os.tmpdir(), "doctor-secret-")), ".brainstem_secret");
  writeFileSync(secretFile, "test-secret\n");

  const prev = {
    brainstem: process.env.RAPP_BRAINSTEM_URL,
    installer: process.env.RAPP_INSTALLER_URL,
    agents: process.env.RAPP_BRAINSTEM_AGENTS,
    exports: process.env.RAPP_MIRROR_EXPORTS,
    rehearsals: process.env.MIRROR_REHEARSALS_DIR,
    secret: process.env.BRAINSTEM_SECRET_FILE,
    voice: process.env.RAPP_VOICE_URL,
    whisper: process.env.WHISPER_URL,
  };
  process.env.RAPP_BRAINSTEM_URL = opts.brainstemUrl || brainstem!.url;
  process.env.RAPP_INSTALLER_URL = installer.url;
  process.env.RAPP_BRAINSTEM_AGENTS = agentsDir;
  process.env.RAPP_MIRROR_EXPORTS = exportsDir;
  process.env.MIRROR_REHEARSALS_DIR = rehearsalsDir;
  process.env.BRAINSTEM_SECRET_FILE = secretFile;
  process.env.RAPP_VOICE_URL = voice.url;
  process.env.WHISPER_URL = voice.url;
  resetSecretCache();
  try {
    return await body();
  } finally {
    for (const server of servers) server.close();
    if (prev.brainstem === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prev.brainstem;
    if (prev.installer === undefined) delete process.env.RAPP_INSTALLER_URL; else process.env.RAPP_INSTALLER_URL = prev.installer;
    if (prev.agents === undefined) delete process.env.RAPP_BRAINSTEM_AGENTS; else process.env.RAPP_BRAINSTEM_AGENTS = prev.agents;
    if (prev.exports === undefined) delete process.env.RAPP_MIRROR_EXPORTS; else process.env.RAPP_MIRROR_EXPORTS = prev.exports;
    if (prev.rehearsals === undefined) delete process.env.MIRROR_REHEARSALS_DIR; else process.env.MIRROR_REHEARSALS_DIR = prev.rehearsals;
    if (prev.secret === undefined) delete process.env.BRAINSTEM_SECRET_FILE; else process.env.BRAINSTEM_SECRET_FILE = prev.secret;
    if (prev.voice === undefined) delete process.env.RAPP_VOICE_URL; else process.env.RAPP_VOICE_URL = prev.voice;
    if (prev.whisper === undefined) delete process.env.WHISPER_URL; else process.env.WHISPER_URL = prev.whisper;
    resetSecretCache();
  }
}

const byId = (checks: DoctorCheck[], id: string): DoctorCheck => checks.find((c) => c.id === id)!;

test("doctor reports a tombstoned installer body as unavailable, not ok", async () => {
  await withDoctorEnv({ installerBody: 'printf "%s\\n" "410 Gone: installer refuses to fetch"; exit 78\n' }, async () => {
    const report = await runDoctor();
    const installer = byId(report.checks, "installer");
    assert.equal(installer.status, "unavailable");
    assert.match(installer.detail, /410 Gone|refuses to fetch/);
    assert.equal(report.ok, false);
  });
});

test("doctor reports a healthy fake brainstem with its version", async () => {
  await withDoctorEnv({ brainstemHealth: { status: "ok", version: "0.6.16", model: "gpt-test", agents: ["A", "B"], quarantined: [] } }, async () => {
    const report = await runDoctor();
    const engine = byId(report.checks, "engine");
    assert.equal(engine.status, "ok");
    assert.match(engine.detail, /0\.6\.16/);
    assert.match(engine.detail, /2 agents/);
  });
});

test("doctor reports an unreachable brainstem as unavailable with a next action", async () => {
  await withDoctorEnv({ brainstemUrl: "http://127.0.0.1:9" }, async () => {
    const report = await runDoctor();
    const engine = byId(report.checks, "engine");
    assert.equal(engine.status, "unavailable");
    assert.ok(engine.nextAction);
  });
});

test("doctor reports a missing agents dir as unavailable", async () => {
  const missing = path.join(os.tmpdir(), "doctor-missing-agents-" + Date.now());
  await withDoctorEnv({ agentsDir: missing }, async () => {
    const report = await runDoctor();
    const agents = byId(report.checks, "agentsDir");
    assert.equal(agents.status, "unavailable");
    assert.match(agents.detail, /ENOENT|no such file/i);
  });
});

test("doctor ok is false with any unavailable check and true with only ok/degraded checks", async () => {
  await withDoctorEnv({ installerStatus: 500 }, async () => {
    assert.equal((await runDoctor()).ok, false);
  });
  await withDoctorEnv({}, async () => {
    const report = await runDoctor();
    assert.equal(report.ok, true);
    assert.ok(report.checks.every((c) => c.status !== "unavailable"));
  });
});

test("doctor turns a throwing check into an unavailable check instead of crashing", async () => {
  const exportsFile = path.join(mkdtempSync(path.join(os.tmpdir(), "doctor-throw-")), "not-a-dir");
  writeFileSync(exportsFile, "I am a file, not a directory");
  await withDoctorEnv({ exportsDir: exportsFile }, async () => {
    const report = await runDoctor();
    const exports = byId(report.checks, "exports");
    assert.equal(exports.status, "unavailable");
    assert.match(exports.detail, /check failed|EEXIST|ENOTDIR/i);
  });
});
