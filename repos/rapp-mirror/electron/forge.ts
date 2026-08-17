import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import {
  closeSync,
  existsSync,
  fsyncSync,
  mkdirSync,
  openSync,
  readFileSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";

import AdmZip from "adm-zip";

import type { ChatTurn } from "../common/ipc.ts";
import { chat, health } from "./brainstem.ts";
import { createLogger } from "./logger.ts";
import { rehearsalGate } from "./rehearsal.ts";

/**
 * The Forge — monkey saw it, now it can be shot ANYWHERE. Distills what the
 * mirror observed (conversation + screen context) into a portable automation
 * spec, then renders it three ways:
 *
 *  1. `<name>_agent.py`  — a single-file RAPP/openrappter BasicAgent (with an
 *     embedded BasicAgent fallback so the file also runs standalone).
 *  2. `SKILL.md`         — an on-demand skill any SKILL.md-speaking agent
 *     (Scout, Cowork, clawhub, rapp-skills) can load.
 *  3. `<name>_solution.zip` — an importable Microsoft Copilot Studio
 *     (Power Platform) solution: one generative bot whose instructions carry
 *     the intent + steps. Template field values are verbatim from
 *     import-proven solution exports. No secrets are ever baked in.
 *
 * Deploy drops the agent into the live global brainstem's agents/ directory —
 * the kernel re-globs `*_agent.py` on every request, so it's live immediately.
 */

const log = createLogger("Forge");

export interface ForgeParam {
  name: string;
  description: string;
  type: "string" | "integer" | "number" | "boolean";
  required: boolean;
}

export interface ForgeStep {
  title: string;
  detail: string;
}

export interface ForgeSpec {
  /** kebab-case artifact id, e.g. "submit-weekly-expenses". */
  name: string;
  /** PascalCase agent class/tool name derived from `name`. */
  className: string;
  /** Human title, e.g. "Submit weekly expenses". */
  title: string;
  /** Trigger-oriented one-liner (tool/skill description). */
  description: string;
  /** The user's overall goal. */
  intent: string;
  steps: ForgeStep[];
  parameters: ForgeParam[];
}

/** Content identity of a spec: sha256 over an explicit-order serialization,
 *  so a rehearsal confirmation earned on one spec can never be spent on a
 *  mutated one (key order from JSON.parse is never trusted). */
export function specHash(spec: ForgeSpec): string {
  const canonical = JSON.stringify({
    name: spec.name,
    className: spec.className,
    title: spec.title,
    description: spec.description,
    intent: spec.intent,
    steps: spec.steps.map((s) => ({ title: s.title, detail: s.detail })),
    parameters: spec.parameters.map((p) => ({
      name: p.name, description: p.description, type: p.type, required: p.required,
    })),
  });
  return createHash("sha256").update(canonical, "utf8").digest("hex");
}

/* ── distillation ────────────────────────────────────────────────────── */

const DISTILL_PROMPT = `You are the Forge inside RAPP Mirror. From the conversation and screen
context below, distill ONE repeatable automation the user demonstrated or asked for.

Respond with ONLY a JSON object — no prose, no code fences — shaped exactly:
{"name":"kebab-case-id","title":"Short title","description":"One trigger-oriented line: when should an agent reach for this?","intent":"The user's overall goal in one sentence","steps":[{"title":"Short step label","detail":"Imperative, generalized instruction"}],"parameters":[{"name":"snake_case","description":"what it is","type":"string","required":true}]}

Rules: generalize from the specific example (loop over ALL items of the kind,
not the one demonstrated); 2-8 steps; 0-4 parameters (only genuine run-time
inputs); types limited to string|integer|number|boolean.`;

/** Pull the first balanced JSON object out of (possibly noisy) model text. */
export function extractJson(text: string): string | null {
  const start = text.indexOf("{");
  if (start < 0) return null;
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let i = start; i < text.length; i++) {
    const ch = text[i];
    if (escaped) { escaped = false; continue; }
    if (ch === "\\") { escaped = inString; continue; }
    if (ch === '"') inString = !inString;
    if (inString) continue;
    if (ch === "{") depth++;
    if (ch === "}" && --depth === 0) return text.slice(start, i + 1);
  }
  return null;
}

export function slugify(raw: string): string {
  const slug = raw.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 50).replace(/^-+|-+$/g, "");
  return slug || "mirror-automation";
}

export function toClassName(slug: string): string {
  const pascal = slug.split("-").filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1)).join("");
  return /^[0-9]/.test(pascal) ? "Auto" + pascal : pascal || "MirrorAutomation";
}

/** Normalize whatever the model returned into a valid, render-ready spec. */
export function normalizeSpec(raw: Record<string, unknown>): ForgeSpec {
  const name = slugify(String(raw.name || raw.title || "mirror-automation"));
  const types = new Set(["string", "integer", "number", "boolean"]);
  const steps = (Array.isArray(raw.steps) ? raw.steps : [])
    .map((s: Record<string, unknown>) => ({
      title: String(s?.title || "").trim() || "Step",
      detail: String(s?.detail || s?.text || "").trim(),
    }))
    .filter((s) => s.detail)
    .slice(0, 12);
  const parameters = (Array.isArray(raw.parameters) ? raw.parameters : [])
    .map((p: Record<string, unknown>) => ({
      name: String(p?.name || "").replace(/[^a-zA-Z0-9_]/g, "_").replace(/^_+|_+$/g, ""),
      description: String(p?.description || "").trim(),
      type: (types.has(String(p?.type)) ? String(p?.type) : "string") as ForgeParam["type"],
      required: Boolean(p?.required),
    }))
    .filter((p) => p.name)
    .slice(0, 6);
  if (!steps.length) throw new Error("The distilled spec has no steps.");
  return {
    name,
    className: toClassName(name),
    title: String(raw.title || name).trim().slice(0, 80),
    description: String(raw.description || raw.intent || "").trim().slice(0, 300),
    intent: String(raw.intent || raw.description || "").trim(),
    steps,
    parameters,
  };
}

/** Ask the brainstem to distill the observed work into a ForgeSpec. */
export async function distill(
  conversation: ChatTurn[],
  screenContext: string[],
  sessionId: string,
): Promise<ForgeSpec> {
  const context: string[] = [DISTILL_PROMPT, "", "## Conversation"];
  for (const turn of conversation.slice(-16)) context.push(`${turn.role}: ${turn.content}`);
  if (screenContext.length) {
    context.push("", "## Screen context (local OCR of what the user was doing)");
    context.push(...screenContext);
  }
  const result = await chat(context.join("\n"), [], sessionId + "-forge");
  if (!result.ok || !result.response) throw new Error(result.error || "The brainstem gave no answer.");
  let json = extractJson(result.response);
  if (!json) {
    // One strict retry — models sometimes chat first; hold the line.
    const retry = await chat(
      "Your previous reply was not a JSON object. Respond with ONLY the JSON spec object now — no prose, no code fences.",
      [
        { role: "user", content: context.join("\n").slice(0, 4000) },
        { role: "assistant", content: result.response.slice(0, 2000) },
      ],
      sessionId + "-forge",
    );
    if (retry.ok && retry.response) json = extractJson(retry.response);
  }
  if (!json) throw new Error("The brainstem never produced a JSON spec — try describing the task more concretely, then forge again.");
  return normalizeSpec(JSON.parse(json) as Record<string, unknown>);
}

/* ── artifact 1: RAPP / openrappter single-file agent ────────────────── */

const py = (s: string) => JSON.stringify(s ?? "");

export function renderAgentPy(spec: ForgeSpec): string {
  const props = spec.parameters
    .map((p) => `            "${p.name}": {"type": ${py(p.type)}, "description": ${py(p.description)}}`)
    .join(",\n");
  const required = spec.parameters.filter((p) => p.required).map((p) => `"${p.name}"`).join(", ");
  // Plain strings, not f-strings — nothing is interpolated, so braces and
  // quotes in model-authored titles/details can never break the Python.
  const pyStr = (s: string) => `"${s.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  const stepLines = spec.steps
    .map((s, i) => `        ${pyStr(`${i + 1}. ${s.title}: ${s.detail}`)}`)
    .join(",\n");
  return `"""${spec.title.replace(/"""/g, "'''")} — forged by RAPP Mirror (monkey saw, monkey does).

Single-file agent. Drop it into any brainstem's agents/ directory
(kody-w/RAPP or openrappter — both hot-load *_agent.py on the next request),
or run it anywhere: the BasicAgent fallback below keeps it self-contained.
"""

import json

try:  # RAPP brainstem / openrappter both shim this import
    from agents.basic_agent import BasicAgent
except ImportError:  # standalone: minimal stand-in so the file runs anywhere
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name = name or self.__class__.__name__
            self.metadata = metadata or {}

        def perform(self, **kwargs):
            return "Not implemented."


class ${spec.className}(BasicAgent):
    def __init__(self):
        self.name = "${spec.className}"
        self.metadata = {
            "name": self.name,
            "description": ${py(spec.description)},
            "parameters": {
                "type": "object",
                "properties": {
${props || ""}
                },
                "required": [${required}],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """Returns the generalized procedure with the caller's inputs bound in.
        The invoking model executes the steps with its own tools and narrates
        the outcome to the user."""
        inputs = {k: v for k, v in kwargs.items() if v is not None}
        steps = [
${stepLines}
        ]
        return json.dumps({
            "status": "procedure",
            "executed": False,
            "intent": ${py(spec.intent)},
            "inputs": inputs,
            "procedure": steps,
            "summary": ${py(`Procedure "${spec.title}" is ready — it has NOT been executed. Carry out the steps in order with the bound inputs, then report what was actually done.`)},
        })


if __name__ == "__main__":
    print(${spec.className}().perform())
`;
}

/* ── artifact 2: SKILL.md ────────────────────────────────────────────── */

export function renderSkillMd(spec: ForgeSpec): string {
  const lines = [
    "---",
    `name: ${spec.name}`,
    `description: ${JSON.stringify(spec.description)}`,
    "---",
    "",
    `# ${spec.title}`,
    "",
    "## When to use",
    "",
    spec.intent || spec.description,
    "",
  ];
  if (spec.parameters.length) {
    lines.push("## Inputs", "");
    for (const p of spec.parameters) {
      lines.push(`- \`${p.name}\` (${p.type}${p.required ? ", required" : ""}) — ${p.description}`);
    }
    lines.push("");
  }
  lines.push("## Steps", "");
  spec.steps.forEach((s, i) => lines.push(`${i + 1}. **${s.title}** — ${s.detail}`));
  lines.push("", "Generalize: if the recorded example acted on one item, apply the same steps to every item of that kind.", "");
  return lines.join("\n");
}

/* ── artifact 3: Copilot Studio (Power Platform) solution zip ────────── */

const PUBLISHER_PREFIX = "rappm";
const TINY_PNG =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

const xmlEscape = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** Double-quoted YAML scalar — colons, hashes, and quotes stay literal. */
const yamlDq = (s: string) => JSON.stringify(s ?? "");

function solutionXml(spec: ForgeSpec): string {
  return `<ImportExportXml version="9.2.26023.151" SolutionPackageVersion="9.2" languagecode="1033" generatedBy="CrmLive" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" OrganizationVersion="9.2.26023.151" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.26024.00146">
  <SolutionManifest>
    <UniqueName>${PUBLISHER_PREFIX}_${spec.name.replace(/-/g, "")}</UniqueName>
    <LocalizedNames>
      <LocalizedName description="${xmlEscape(spec.title)}" languagecode="1033" />
    </LocalizedNames>
    <Descriptions />
    <Version>1.0.0.0</Version>
    <Managed>0</Managed>
    <Publisher>
      <UniqueName>rappmirror</UniqueName>
      <LocalizedNames>
        <LocalizedName description="RAPP Mirror" languagecode="1033" />
      </LocalizedNames>
      <Descriptions>
        <Description description="Auto-generated publisher" languagecode="1033" />
      </Descriptions>
      <EMailAddress xsi:nil="true"></EMailAddress>
      <SupportingWebsiteUrl xsi:nil="true"></SupportingWebsiteUrl>
      <CustomizationPrefix>${PUBLISHER_PREFIX}</CustomizationPrefix>
      <CustomizationOptionValuePrefix>10000</CustomizationOptionValuePrefix>
      <Addresses>
        <Address>
          <AddressNumber>1</AddressNumber>
          <AddressTypeCode xsi:nil="true"></AddressTypeCode>
          <City xsi:nil="true"></City>
          <County xsi:nil="true"></County>
          <Country xsi:nil="true"></Country>
          <Fax xsi:nil="true"></Fax>
          <FreightTermsCode xsi:nil="true"></FreightTermsCode>
          <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
          <Latitude xsi:nil="true"></Latitude>
          <Line1 xsi:nil="true"></Line1>
          <Line2 xsi:nil="true"></Line2>
          <Line3 xsi:nil="true"></Line3>
          <Longitude xsi:nil="true"></Longitude>
          <Name xsi:nil="true"></Name>
          <PostalCode xsi:nil="true"></PostalCode>
          <PostOfficeBox xsi:nil="true"></PostOfficeBox>
          <PrimaryContactName xsi:nil="true"></PrimaryContactName>
          <ShippingMethodCode xsi:nil="true"></ShippingMethodCode>
          <StateOrProvince xsi:nil="true"></StateOrProvince>
          <Telephone1 xsi:nil="true"></Telephone1>
          <Telephone2 xsi:nil="true"></Telephone2>
          <Telephone3 xsi:nil="true"></Telephone3>
          <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
          <UPSZone xsi:nil="true"></UPSZone>
          <UTCOffset xsi:nil="true"></UTCOffset>
          <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
        </Address>
        <Address>
          <AddressNumber>2</AddressNumber>
          <AddressTypeCode xsi:nil="true"></AddressTypeCode>
          <City xsi:nil="true"></City>
          <County xsi:nil="true"></County>
          <Country xsi:nil="true"></Country>
          <Fax xsi:nil="true"></Fax>
          <FreightTermsCode xsi:nil="true"></FreightTermsCode>
          <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
          <Latitude xsi:nil="true"></Latitude>
          <Line1 xsi:nil="true"></Line1>
          <Line2 xsi:nil="true"></Line2>
          <Line3 xsi:nil="true"></Line3>
          <Longitude xsi:nil="true"></Longitude>
          <Name xsi:nil="true"></Name>
          <PostalCode xsi:nil="true"></PostalCode>
          <PostOfficeBox xsi:nil="true"></PostOfficeBox>
          <PrimaryContactName xsi:nil="true"></PrimaryContactName>
          <ShippingMethodCode xsi:nil="true"></ShippingMethodCode>
          <StateOrProvince xsi:nil="true"></StateOrProvince>
          <Telephone1 xsi:nil="true"></Telephone1>
          <Telephone2 xsi:nil="true"></Telephone2>
          <Telephone3 xsi:nil="true"></Telephone3>
          <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
          <UPSZone xsi:nil="true"></UPSZone>
          <UTCOffset xsi:nil="true"></UTCOffset>
          <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
        </Address>
      </Addresses>
    </Publisher>
    <RootComponents></RootComponents>
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>`;
}

const CUSTOMIZATIONS_XML = `<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" OrganizationVersion="9.2.26023.151" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.26024.00146">
  <Entities></Entities>
  <Roles></Roles>
  <Workflows></Workflows>
  <FieldSecurityProfiles></FieldSecurityProfiles>
  <Templates />
  <EntityMaps />
  <EntityRelationships />
  <OrganizationSettings />
  <optionsets />
  <CustomControls />
  <EntityDataProviders />
  <connectionreferences>
  </connectionreferences>
  <Languages>
    <Language>1033</Language>
  </Languages>
</ImportExportXml>`;

/** Bot schema name: prefix + sanitized name, comfortably under Dataverse's
 *  100-char botcomponent limit once ".gpt.default" is appended. */
export function botSchema(spec: ForgeSpec): string {
  return `${PUBLISHER_PREFIX}_${spec.name.replace(/-/g, "").slice(0, 40)}`;
}

/** Bot display names above 42 chars fail Dataverse import (error 10004). */
export function botDisplayName(spec: ForgeSpec): string {
  return spec.title.slice(0, 42);
}

function gptInstructions(spec: ForgeSpec): string {
  const lines = [spec.intent || spec.description, "", "Follow these steps in order:"];
  spec.steps.forEach((s, i) => lines.push(`${i + 1}. ${s.title}: ${s.detail}`));
  if (spec.parameters.length) {
    lines.push("", "Ask the user for these inputs when missing:");
    for (const p of spec.parameters) lines.push(`- ${p.name}: ${p.description}`);
  }
  return lines.join("\n");
}

export function renderMcsFiles(spec: ForgeSpec): Map<string, string> {
  const schema = botSchema(spec);
  const gptSchema = `${schema}.gpt.default`;
  const indented = gptInstructions(spec).split("\n").map((l) => "  " + l).join("\n");
  const files = new Map<string, string>();
  files.set("solution.xml", solutionXml(spec));
  files.set("customizations.xml", CUSTOMIZATIONS_XML);
  files.set(
    "[Content_Types].xml",
    `<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/octet-stream" /><Default Extension="json" ContentType="application/octet-stream" /><Override PartName="/botcomponents/${gptSchema}/data" ContentType="application/octet-stream" /></Types>`,
  );
  files.set(
    `bots/${schema}/bot.xml`,
    `<bot schemaname="${schema}">
  <authenticationmode>2</authenticationmode>
  <authenticationtrigger>1</authenticationtrigger>
  <iconbase64>${TINY_PNG}</iconbase64>
  <iscustomizable>0</iscustomizable>
  <language>1033</language>
  <name>${xmlEscape(botDisplayName(spec))}</name>
  <runtimeprovider>0</runtimeprovider>
  <template>default-2.1.0</template>
</bot>`,
  );
  files.set(
    `bots/${schema}/configuration.json`,
    JSON.stringify(
      {
        $kind: "BotConfiguration",
        settings: { GenerativeActionsEnabled: true },
        isAgentConnectable: true,
        gPTSettings: { $kind: "GPTSettings", defaultSchemaName: gptSchema },
        isLightweightBot: false,
        aISettings: {
          $kind: "AISettings",
          useModelKnowledge: true,
          isFileAnalysisEnabled: true,
          isSemanticSearchEnabled: true,
          contentModeration: "High",
          optInUseLatestModels: false,
        },
        recognizer: { $kind: "GenerativeAIRecognizer" },
      },
      null,
      2,
    ),
  );
  files.set(
    `botcomponents/${gptSchema}/botcomponent.xml`,
    `<botcomponent schemaname="${gptSchema}">
  <componenttype>15</componenttype>
  <description>${xmlEscape(spec.description)}</description>
  <iscustomizable>0</iscustomizable>
  <name>Default GPT</name>
  <parentbotid>
    <schemaname>${schema}</schemaname>
  </parentbotid>
  <statecode>0</statecode>
  <statuscode>1</statuscode>
</botcomponent>`,
  );
  files.set(
    `botcomponents/${gptSchema}/data`,
    `kind: GptComponentMetadata
displayName: ${yamlDq(botDisplayName(spec))}
instructions: |-
${indented}
conversationStarters:
  - title: ${yamlDq(spec.title.slice(0, 60))}
    text: ${yamlDq(spec.intent.slice(0, 120) || spec.title)}
gptCapabilities:
  webBrowsing: true
  codeInterpreter: true

aISettings:
  model:
    modelNameHint: GPT5Chat

  extensionData:
    lastUsedCustomModel: {}

declarativeSkillsMetadata:`,
  );
  return files;
}

export function renderMcsZip(spec: ForgeSpec): Buffer {
  const zip = new AdmZip();
  for (const [file, content] of renderMcsFiles(spec)) {
    zip.addFile(file, Buffer.from(content, "utf8"));
  }
  return zip.toBuffer();
}

/* ── export + deploy ─────────────────────────────────────────────────── */

export interface ForgedArtifacts {
  dir: string;
  agentPath: string;
  skillPath: string;
  solutionPath: string;
}

export function exportsRoot(): string {
  return process.env.RAPP_MIRROR_EXPORTS || path.join(os.homedir(), "Documents", "rapp-mirror-exports");
}

/** Write all three artifacts under exportsRoot()/<name>/; returns the paths. */
export function exportAll(spec: ForgeSpec): ForgedArtifacts {
  const dir = path.join(exportsRoot(), spec.name);
  mkdirSync(dir, { recursive: true });
  const agentPath = path.join(dir, `${spec.name.replace(/-/g, "_")}_agent.py`);
  const skillPath = path.join(dir, "SKILL.md");
  const solutionPath = path.join(dir, `${spec.name}_solution.zip`);
  writeFileSync(agentPath, renderAgentPy(spec));
  writeFileSync(skillPath, renderSkillMd(spec));
  writeFileSync(solutionPath, renderMcsZip(spec));
  writeFileSync(path.join(dir, "spec.json"), JSON.stringify(spec, null, 2));
  log.info("exported", spec.name, "->", dir);
  return { dir, agentPath, skillPath, solutionPath };
}

export function brainstemAgentsDir(): string {
  return (
    process.env.RAPP_BRAINSTEM_AGENTS ||
    path.join(os.homedir(), ".brainstem", "src", "rapp_brainstem", "agents")
  );
}

export interface DeployResult {
  ok: boolean;
  path?: string;
  live?: boolean;
  quarantined?: boolean;
  /** Refused by the rehearsal gate — rehearse (or force) first. */
  needsRehearsal?: boolean;
  /** The gate was overridden for this deploy; recorded, never the default. */
  forced?: boolean;
  /** The generated artifact executed successfully before entering the live dir. */
  verified?: boolean;
  /** A failed live verification restored the previous on-disk state. */
  rolledBack?: boolean;
  /** Path to the best-effort pre-deploy backup, when there was a previous file. */
  backupPath?: string;
  /** Standalone invocation evidence from the pre-live verification. */
  invocation?: { exitCode: number; stdout: string };
  error?: string;
}

function withForced(result: DeployResult, forced: boolean): DeployResult {
  return forced ? { ...result, forced: true } : result;
}

function writeAtomic(file: string, content: string | Buffer): void {
  const tmp = `${file}.tmp`;
  const fd = openSync(tmp, "w");
  try {
    writeFileSync(fd, content);
    fsyncSync(fd);
  } finally {
    closeSync(fd);
  }
  renameSync(tmp, file);
}

function removeIfExists(file: string): void {
  try {
    if (existsSync(file)) unlinkSync(file);
  } catch {
    // Best-effort cleanup only.
  }
}

function verifyStandalone(source: string, spec: ForgeSpec): {
  ok: boolean;
  error?: string;
  invocation?: { exitCode: number; stdout: string };
} {
  const file = path.join(
    os.tmpdir(),
    `rapp-mirror-${process.pid}-${Date.now()}-${spec.name.replace(/[^a-z0-9_-]/gi, "_")}_agent.py`,
  );
  try {
    writeFileSync(file, source);
    const run = spawnSync("python3", [file], { encoding: "utf8", timeout: 20_000 });
    const exitCode = run.status ?? -1;
    const stdout = run.stdout ?? "";
    const invocation = { exitCode, stdout };
    if (run.error) return { ok: false, error: `python3 failed: ${run.error.message}`, invocation };
    if (run.signal) return { ok: false, error: `python3 terminated by signal ${run.signal}`, invocation };
    if (exitCode !== 0) {
      return {
        ok: false,
        error: `artifact exited with code ${exitCode}: ${(run.stderr || stdout || "(no output)").trim()}`,
        invocation,
      };
    }
    try {
      JSON.parse(stdout);
    } catch (err) {
      return {
        ok: false,
        error: `artifact stdout was not parseable JSON: ${err instanceof Error ? err.message : String(err)}`,
        invocation,
      };
    }
    return { ok: true, invocation };
  } finally {
    removeIfExists(file);
  }
}

/** Drop the agent into the live brainstem (hot-loaded on the next request)
 *  and verify it shows up in /health's agent list, unquarantined.
 *
 *  Gated: every deploy path (UI, control plane, mirrorctl) funnels through
 *  here, so no unrehearsed spec deploys by default — the spec needs a
 *  confirmed rehearsal whose hash matches this exact spec. `force` overrides
 *  and is recorded in the result. */
export async function deployAgent(
  spec: ForgeSpec,
  opts: { force?: boolean } = {},
): Promise<DeployResult> {
  const gate = rehearsalGate(spec, opts.force === true);
  if (!gate.allowed) return { ok: false, needsRehearsal: true, error: gate.reason };
  const rendered = renderAgentPy(spec);
  const verified = verifyStandalone(rendered, spec);
  if (!verified.ok) {
    return withForced({
      ok: false,
      verified: false,
      invocation: verified.invocation,
      error: verified.error || "artifact did not execute successfully",
    }, gate.forced === true);
  }
  const dir = brainstemAgentsDir();
  if (!existsSync(dir)) {
    return withForced({
      ok: false,
      verified: true,
      invocation: verified.invocation,
      error: `no brainstem agents dir at ${dir}`,
    }, gate.forced === true);
  }
  const file = path.join(dir, `${spec.name.replace(/-/g, "_")}_agent.py`);
  const hadBackup = existsSync(file);
  const previous = hadBackup ? readFileSync(file) : null;
  const backupPath = hadBackup ? `${file}.bak` : undefined;
  if (previous) writeAtomic(backupPath!, previous);
  writeAtomic(file, rendered);
  const h = await health();
  const live = Boolean(h.agents?.includes(spec.className));
  const quarantined = Boolean(
    h.quarantined?.some((q) => typeof q === "string" && q.includes(spec.className)),
  );
  if (!live || quarantined) {
    if (previous) {
      writeAtomic(file, previous);
    } else {
      removeIfExists(file);
    }
    removeIfExists(`${file}.tmp`);
    const reason = quarantined
      ? `${spec.className} was quarantined by the brainstem`
      : h.error || `${spec.className} was not listed by /health`;
    log.warn("deploy rolled back", file, reason);
    return withForced({
      ok: false,
      path: file,
      live,
      quarantined,
      verified: true,
      rolledBack: true,
      backupPath,
      invocation: verified.invocation,
      error: reason,
    }, gate.forced === true);
  }
  removeIfExists(`${file}.tmp`);
  log.info("deployed", file, live ? "(live)" : "(not listed!)", quarantined ? "QUARANTINED" : "");
  const result: DeployResult = {
    ok: verified.ok && live && !quarantined,
    path: file,
    live,
    quarantined,
    verified: true,
    backupPath,
    invocation: verified.invocation,
  };
  if (gate.forced) result.forced = true;
  return result;
}
