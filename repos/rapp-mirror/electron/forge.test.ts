import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import AdmZip from "adm-zip";

import { resetSecretCache } from "./brainstem.ts";
import {
  botDisplayName,
  botSchema,
  deployAgent,
  exportAll,
  extractJson,
  normalizeSpec,
  renderAgentPy,
  renderMcsFiles,
  renderMcsZip,
  renderSkillMd,
  slugify,
  toClassName,
  type ForgeSpec,
} from "./forge.ts";

const SPEC: ForgeSpec = normalizeSpec({
  name: "Submit Weekly Expenses!",
  title: "Submit weekly expenses",
  description: "Files the week's expense report from receipts.",
  intent: "Submit every pending expense receipt as one weekly report.",
  steps: [
    { title: "Collect receipts", detail: "Gather all receipts for the week." },
    { title: "File report", detail: "Create and submit the expense report." },
  ],
  parameters: [
    { name: "week", description: "ISO week to file", type: "string", required: true },
    { name: "dry run?", description: "preview only", type: "boolean", required: false },
  ],
});

/** Compile-or-skip: py_compile the source; skip the test when python3 is absent. */
function pyCompile(t: { skip: (msg?: string) => void }, source: string): boolean {
  const dir = mkdtempSync(path.join(os.tmpdir(), "forge-compile-"));
  const file = path.join(dir, "agent.py");
  writeFileSync(file, source);
  const python = spawnSync("python3", ["-m", "py_compile", file], { encoding: "utf8" });
  if (python.error && (python.error as NodeJS.ErrnoException).code === "ENOENT") {
    t.skip("python3 is not available on this machine");
    return false;
  }
  assert.equal(python.status, 0, `py_compile failed:\n${python.stderr || python.stdout}`);
  return true;
}

/* ── extractJson ─────────────────────────────────────────────────────── */

test("extractJson pulls a plain object verbatim", () => {
  assert.equal(extractJson('{"a":1}'), '{"a":1}');
});

test("extractJson finds the first balanced object nested in prose", () => {
  const obj = '{"name":"x","inner":{"b":2},"list":[{"c":3}]}';
  const text = `Sure! Here is the spec:\n${obj}\nHope that helps.`;
  assert.equal(extractJson(text), obj);
  assert.deepEqual(JSON.parse(extractJson(text) as string), {
    name: "x",
    inner: { b: 2 },
    list: [{ c: 3 }],
  });
});

test("extractJson ignores braces and escaped quotes inside JSON strings", () => {
  assert.equal(extractJson('noise {"a": {"b": "}"}} trailing'), '{"a": {"b": "}"}}');
  const obj = '{"a":"has { and } inside","b":"escaped \\" quote and a { brace"}';
  const extracted = extractJson(`before ${obj} after }`);
  assert.equal(extracted, obj);
  const parsed = JSON.parse(extracted as string) as Record<string, string>;
  assert.equal(parsed.a, "has { and } inside");
  assert.equal(parsed.b, 'escaped " quote and a { brace');
});

test("extractJson returns null when there is no JSON", () => {
  assert.equal(extractJson("no json here"), null);
  assert.equal(extractJson('unbalanced {"a": 1'), null);
  assert.equal(extractJson(""), null);
});

/* ── slugify + toClassName ───────────────────────────────────────────── */

test("slugify turns spaces and symbols into kebab-case", () => {
  assert.equal(slugify("Submit Weekly Expenses!"), "submit-weekly-expenses");
  assert.equal(slugify("  --Hello__World--  "), "hello-world");
  assert.equal(slugify("A/B testing & CSVs"), "a-b-testing-csvs");
});

test("slugify falls back on degenerate input and clamps length", () => {
  assert.equal(slugify("!!!"), "mirror-automation");
  assert.equal(slugify(""), "mirror-automation");
  assert.ok(slugify("a".repeat(80)).length <= 50);
});

test("toClassName pascal-cases the slug and prefixes leading digits", () => {
  assert.equal(toClassName("submit-weekly-expenses"), "SubmitWeeklyExpenses");
  assert.equal(toClassName("9-lives"), "Auto9Lives");
  assert.equal(toClassName(""), "MirrorAutomation");
});

/* ── normalizeSpec ───────────────────────────────────────────────────── */

test("normalizeSpec slugifies, derives the class name, and sanitizes params", () => {
  assert.equal(SPEC.name, "submit-weekly-expenses");
  assert.equal(SPEC.className, "SubmitWeeklyExpenses");
  assert.equal(SPEC.parameters[1].name, "dry_run");
  assert.equal(SPEC.parameters[1].type, "boolean");
});

test("normalizeSpec clamps unknown types to string and coerces required", () => {
  const spec = normalizeSpec({
    name: "type-clamp",
    steps: [{ title: "Only", detail: "do it" }],
    parameters: [
      { name: "count", description: "how many", type: "integer", required: true },
      { name: "blob", description: "bad type", type: "object", required: "yes" },
    ],
  });
  assert.equal(spec.parameters[0].type, "integer");
  assert.equal(spec.parameters[1].type, "string"); // clamped from "object"
  assert.equal(spec.parameters[1].required, true);
});

test("normalizeSpec drops empty-detail steps and accepts the text alias", () => {
  const spec = normalizeSpec({
    name: "keep-some",
    steps: [
      { title: "Empty", detail: "   " },
      { title: "Kept", detail: "real work" },
      { title: "Alt field", text: "detail carried in text" },
    ],
  });
  assert.equal(spec.steps.length, 2);
  assert.equal(spec.steps[0].title, "Kept");
  assert.equal(spec.steps[1].detail, "detail carried in text");
});

test("normalizeSpec throws on zero surviving steps", () => {
  assert.throws(() => normalizeSpec({ name: "x", steps: [] }), /no steps/);
  assert.throws(
    () => normalizeSpec({ name: "all-empty", steps: [{ title: "x", detail: "" }] }),
    /no steps/,
  );
  assert.throws(() => normalizeSpec({ name: "missing" }), /no steps/);
});

/* ── renderAgentPy ───────────────────────────────────────────────────── */

test("renderAgentPy carries the class, metadata, params, and required list", () => {
  const py = renderAgentPy(SPEC);
  assert.match(py, /class SubmitWeeklyExpenses\(BasicAgent\)/);
  assert.ok(py.includes(JSON.stringify(SPEC.description)));
  for (const p of SPEC.parameters) assert.ok(py.includes(`"${p.name}"`), `missing param ${p.name}`);
  assert.match(py, /"required": \["week"\]/);
  assert.match(py, /def perform\(self, \*\*kwargs\)/);
  for (const s of SPEC.steps) assert.ok(py.includes(s.title), `missing step ${s.title}`);
});

test("renderAgentPy output compiles under python3 -m py_compile", (t) => {
  pyCompile(t, renderAgentPy(SPEC));
});

test("generated agent runs standalone (BasicAgent fallback) and returns JSON", (t) => {
  const dir = mkdtempSync(path.join(os.tmpdir(), "forge-run-"));
  const file = path.join(dir, "submit_weekly_expenses_agent.py");
  writeFileSync(file, renderAgentPy(SPEC));
  const run = spawnSync("python3", [file], { encoding: "utf8" });
  if (run.error && (run.error as NodeJS.ErrnoException).code === "ENOENT") {
    t.skip("python3 is not available on this machine");
    return;
  }
  assert.equal(run.status, 0, run.stderr);
  const out = JSON.parse(run.stdout);
  assert.equal(out.status, "procedure");
  assert.equal(out.executed, false);
  assert.match(out.summary, /NOT been executed/);
  assert.equal(out.procedure.length, 2);
});

/* ── renderSkillMd ───────────────────────────────────────────────────── */

test("renderSkillMd carries frontmatter, quoted description, inputs, ordered steps", () => {
  const md = renderSkillMd(SPEC);
  const lines = md.split("\n");
  assert.equal(lines[0], "---");
  assert.equal(lines[1], `name: ${SPEC.name}`);
  assert.equal(lines[2], `description: ${JSON.stringify(SPEC.description)}`);
  assert.equal(lines[3], "---");
  assert.match(md, /`week` \(string, required\)/);
  assert.match(md, /`dry_run` \(boolean\)/);
  SPEC.steps.forEach((s, i) => {
    assert.ok(md.includes(`${i + 1}. **${s.title}** — ${s.detail}`), `missing step ${i + 1}`);
  });
});

/* ── renderMcsFiles ──────────────────────────────────────────────────── */

test("renderMcsFiles emits the full import-critical file set", () => {
  const files = renderMcsFiles(SPEC);
  const schema = botSchema(SPEC);
  const expected = [
    "solution.xml",
    "customizations.xml",
    "[Content_Types].xml",
    `bots/${schema}/bot.xml`,
    `bots/${schema}/configuration.json`,
    `botcomponents/${schema}.gpt.default/botcomponent.xml`,
    `botcomponents/${schema}.gpt.default/data`,
  ];
  assert.deepEqual([...files.keys()].sort(), expected.slice().sort());
  assert.ok(schema.length + ".gpt.default".length <= 100);
  // every extensionless data part must be declared via Override in [Content_Types].xml
  const contentTypes = files.get("[Content_Types].xml")!;
  assert.ok(
    contentTypes.includes(`<Override PartName="/botcomponents/${schema}.gpt.default/data"`),
    "Content_Types must Override the data part path",
  );
});

test("bot display name stays under Dataverse's 42-char import limit", () => {
  assert.ok(botDisplayName(SPEC).length <= 42);
  const longTitle =
    "Consolidate and submit all weekly expense reports across every subsidiary team";
  const longSpec: ForgeSpec = { ...SPEC, title: longTitle };
  const display = botDisplayName(longSpec);
  assert.equal(display, longTitle.slice(0, 42));
  assert.ok(display.length <= 42);
  const botXml = renderMcsFiles(longSpec).get(`bots/${botSchema(longSpec)}/bot.xml`)!;
  const m = botXml.match(/<name>(.*?)<\/name>/);
  assert.ok(m, "bot.xml has a <name> element");
  assert.ok(m![1].length <= 42, `bot.xml name is ${m![1].length} chars`);
});

test("gpt data YAML carries the intent and steps; configuration.json is wired", () => {
  const files = renderMcsFiles(SPEC);
  const schema = botSchema(SPEC);
  const gpt = files.get(`botcomponents/${schema}.gpt.default/data`)!;
  assert.match(gpt, /kind: GptComponentMetadata/);
  assert.ok(gpt.includes(SPEC.intent), "data YAML must contain the intent");
  for (const s of SPEC.steps) assert.ok(gpt.includes(s.title), `data YAML missing step ${s.title}`);
  const config = JSON.parse(files.get(`bots/${schema}/configuration.json`)!) as {
    gPTSettings: { defaultSchemaName: string };
  };
  assert.equal(config.gPTSettings.defaultSchemaName, `${schema}.gpt.default`);
});

/* ── renderMcsZip ────────────────────────────────────────────────────── */

test("renderMcsZip round-trips through adm-zip with the same entry names", () => {
  const zip = new AdmZip(renderMcsZip(SPEC));
  assert.deepEqual(
    zip.getEntries().map((e) => e.entryName).sort(),
    [...renderMcsFiles(SPEC).keys()].sort(),
  );
  assert.ok(zip.readAsText("solution.xml").includes("<ImportExportXml"));
});

/* ── exportAll ───────────────────────────────────────────────────────── */

test("exportAll writes the four artifacts under RAPP_MIRROR_EXPORTS", () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), "forge-exports-"));
  const prev = process.env.RAPP_MIRROR_EXPORTS;
  process.env.RAPP_MIRROR_EXPORTS = tmp;
  try {
    const out = exportAll(SPEC);
    assert.equal(out.dir, path.join(tmp, SPEC.name));
    assert.equal(out.agentPath, path.join(out.dir, "submit_weekly_expenses_agent.py"));
    assert.equal(out.skillPath, path.join(out.dir, "SKILL.md"));
    assert.equal(out.solutionPath, path.join(out.dir, `${SPEC.name}_solution.zip`));
    assert.ok(existsSync(out.agentPath));
    assert.ok(existsSync(out.skillPath));
    assert.ok(existsSync(out.solutionPath));
    assert.ok(existsSync(path.join(out.dir, "spec.json")));
    assert.ok(readFileSync(out.agentPath, "utf8").includes(`class ${SPEC.className}(BasicAgent)`));
    assert.deepEqual(JSON.parse(readFileSync(path.join(out.dir, "spec.json"), "utf8")), SPEC);
  } finally {
    if (prev === undefined) delete process.env.RAPP_MIRROR_EXPORTS; else process.env.RAPP_MIRROR_EXPORTS = prev;
  }
});

/* ── deployAgent ─────────────────────────────────────────────────────── */

/** A fake brainstem whose /health reports the given agent list. */
function fakeHealthServer(
  agents: string[],
  quarantined: string[] = [],
): Promise<{ server: http.Server; url: string }> {
  const server = http.createServer((_req, res) => {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ status: "ok", agents, quarantined }));
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () =>
      resolve({ server, url: `http://127.0.0.1:${(server.address() as { port: number }).port}` }),
    ),
  );
}

async function withDeployEnv<T>(
  agents: string[],
  body: (agentsDir: string) => Promise<T>,
  quarantined: string[] = [],
): Promise<T> {
  const { server, url } = await fakeHealthServer(agents, quarantined);
  const agentsDir = mkdtempSync(path.join(os.tmpdir(), "forge-agents-"));
  // Empty rehearsal registry: deploys here exercise mechanics via force,
  // or the gate itself (rehearsal.test.ts owns the full gate matrix).
  const rehearsalsDir = mkdtempSync(path.join(os.tmpdir(), "forge-rehearsals-"));
  const secretFile = path.join(agentsDir, ".brainstem_secret");
  writeFileSync(secretFile, "test-secret\n");
  const prevUrl = process.env.RAPP_BRAINSTEM_URL;
  const prevAgents = process.env.RAPP_BRAINSTEM_AGENTS;
  const prevSecret = process.env.BRAINSTEM_SECRET_FILE;
  const prevRehearsals = process.env.MIRROR_REHEARSALS_DIR;
  process.env.RAPP_BRAINSTEM_URL = url;
  process.env.RAPP_BRAINSTEM_AGENTS = agentsDir;
  process.env.BRAINSTEM_SECRET_FILE = secretFile;
  process.env.MIRROR_REHEARSALS_DIR = rehearsalsDir;
  resetSecretCache();
  try {
    return await body(agentsDir);
  } finally {
    server.close();
    if (prevUrl === undefined) delete process.env.RAPP_BRAINSTEM_URL; else process.env.RAPP_BRAINSTEM_URL = prevUrl;
    if (prevAgents === undefined) delete process.env.RAPP_BRAINSTEM_AGENTS; else process.env.RAPP_BRAINSTEM_AGENTS = prevAgents;
    if (prevSecret === undefined) delete process.env.BRAINSTEM_SECRET_FILE; else process.env.BRAINSTEM_SECRET_FILE = prevSecret;
    if (prevRehearsals === undefined) delete process.env.MIRROR_REHEARSALS_DIR; else process.env.MIRROR_REHEARSALS_DIR = prevRehearsals;
    resetSecretCache();
  }
}

test("deployAgent is rehearsal-gated: an unrehearsed spec is refused by default", async () => {
  await withDeployEnv([SPEC.className], async () => {
    const res = await deployAgent(SPEC);
    assert.equal(res.ok, false);
    assert.equal(res.needsRehearsal, true);
    assert.match(res.error!, /rehears/i);
  });
});

test("deployAgent writes the agent file and verifies it live via /health", async () => {
  await withDeployEnv([SPEC.className], async (agentsDir) => {
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, true);
    assert.equal(res.verified, true);
    assert.equal(res.live, true);
    assert.equal(res.quarantined, false);
    assert.equal(res.forced, true); // the override is always recorded
    assert.equal(res.invocation?.exitCode, 0);
    assert.equal(res.path, path.join(agentsDir, "submit_weekly_expenses_agent.py"));
    assert.ok(existsSync(res.path!));
    assert.ok(readFileSync(res.path!, "utf8").includes(`class ${SPEC.className}(BasicAgent)`));
  });
});

test("deployAgent reports ok:false, live:false and rolls back when /health does not list it", async () => {
  await withDeployEnv([], async (agentsDir) => {
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, false);
    assert.equal(res.live, false);
    assert.equal(res.rolledBack, true);
    assert.equal(existsSync(path.join(agentsDir, "submit_weekly_expenses_agent.py")), false);
  });
});

test("deployAgent fails cleanly when the agents dir does not exist", async () => {
  const prev = process.env.RAPP_BRAINSTEM_AGENTS;
  process.env.RAPP_BRAINSTEM_AGENTS = path.join(os.tmpdir(), "forge-no-such-dir-" + Date.now());
  try {
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, false);
    assert.match(res.error!, /no brainstem agents dir/);
  } finally {
    if (prev === undefined) delete process.env.RAPP_BRAINSTEM_AGENTS; else process.env.RAPP_BRAINSTEM_AGENTS = prev;
  }
});

test("deployAgent refuses an artifact that fails to execute before writing live", async () => {
  await withDeployEnv(["Broken"], async (agentsDir) => {
    const broken: ForgeSpec = { ...SPEC, className: "Broken-Class" };
    const res = await deployAgent(broken, { force: true });
    assert.equal(res.ok, false);
    assert.equal(res.verified, false);
    assert.match(res.error!, /artifact exited|python3 failed/);
    assert.equal(existsSync(path.join(agentsDir, "submit_weekly_expenses_agent.py")), false);
  });
});

test("deployAgent leaves no live .tmp file behind after a successful deploy", async () => {
  await withDeployEnv([SPEC.className], async (agentsDir) => {
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, true);
    assert.equal(existsSync(path.join(agentsDir, "submit_weekly_expenses_agent.py.tmp")), false);
  });
});

test("deployAgent restores previous file bytes and reports rolledBack when health does not list the class", async () => {
  await withDeployEnv([], async (agentsDir) => {
    const file = path.join(agentsDir, "submit_weekly_expenses_agent.py");
    const previous = "previous bytes\n";
    writeFileSync(file, previous);
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, false);
    assert.equal(res.rolledBack, true);
    assert.equal(readFileSync(file, "utf8"), previous);
    assert.equal(res.backupPath, file + ".bak");
    assert.equal(readFileSync(res.backupPath!, "utf8"), previous);
  });
});

test("deployAgent removes the new file when health fails and there was no previous file", async () => {
  await withDeployEnv([], async (agentsDir) => {
    const file = path.join(agentsDir, "submit_weekly_expenses_agent.py");
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.ok, false);
    assert.equal(res.rolledBack, true);
    assert.equal(existsSync(file), false);
  });
});

test("deployAgent ok is false unless verified, live, and not quarantined", async () => {
  await withDeployEnv([SPEC.className], async () => {
    const res = await deployAgent(SPEC, { force: true });
    assert.equal(res.verified, true);
    assert.equal(res.live, true);
    assert.equal(res.quarantined, true);
    assert.equal(res.rolledBack, true);
    assert.equal(res.ok, false);
  }, [`${SPEC.className}: bad import`]);
});

/* ── hygiene ─────────────────────────────────────────────────────────── */

test("no secret-looking strings in any rendered artifact", () => {
  const all = [renderAgentPy(SPEC), renderSkillMd(SPEC), ...renderMcsFiles(SPEC).values()].join("\n");
  assert.doesNotMatch(all, /(api[_-]?key|client[_-]?secret|password|ghu_|gho_|x-functions-key)/i);
});
