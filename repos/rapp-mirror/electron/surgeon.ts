import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { approveAll, CopilotClient, RuntimeConnection, type CopilotSession, type Tool } from "@github/copilot-sdk";
import { BrowserWindow } from "electron";

import { brainstemUrl, chat, health } from "./brainstem.ts";
import { resolveCopilotCliPath } from "./copilot-cli.ts";
import { createLogger } from "./logger.ts";

/**
 * The Brain Surgeon: GitHub Copilot in agent mode, operating ON the brainstem.
 * Each session is a live Copilot CLI conversation (runs on the user's Copilot
 * account) whose tools write agent files into the brainstem's workspace,
 * hot-load them, run python, and test the result live over /chat. Multiple
 * sessions build in parallel on the same brainstem — the panel's tabs.
 *
 * Skill-recorder's AgentBuilder pattern, pointed at surgery.
 */

const log = createLogger("Surgeon");
const TURN_TIMEOUT_MS = 240_000;

export interface SurgeonEvent {
  sessionId: string;
  kind: "status" | "tool" | "report" | "error" | "done";
  text: string;
}

function broadcast(ev: SurgeonEvent): void {
  for (const win of BrowserWindow.getAllWindows()) {
    win.webContents.send("surgeon:event", ev);
  }
}

function agentsDir(): string {
  return (
    process.env.RAPP_BRAINSTEM_AGENTS ||
    path.join(os.homedir(), ".brainstem", "src", "rapp_brainstem", "agents")
  );
}

function venvPython(): string {
  const p = path.join(os.homedir(), ".brainstem", "venv", "bin", "python");
  return existsSync(p) ? p : "python3";
}

const SYSTEM = () => `You are the Brain Surgeon: GitHub Copilot operating directly on a live RAPP
brainstem (a local Flask agent server at ${brainstemUrl()} that hot-loads
single-file Python agents from ${agentsDir()} on every request — no restart
needed, ever).

The agent contract (one file = one class = one tool):

    import json
    from agents.basic_agent import BasicAgent

    class MyAgent(BasicAgent):
        def __init__(self):
            self.name = "MyAgent"   # tool-safe: ^[a-zA-Z0-9_-]+$
            self.metadata = {
                "name": self.name,
                "description": "When the model should call this.",
                "parameters": {"type": "object", "properties": {...}, "required": [...]},
            }
            super().__init__(name=self.name, metadata=self.metadata)

        def perform(self, **kwargs):
            return json.dumps({"status": "success", ...})

Rules of the operating theater:
- Filenames MUST end in _agent.py (snake_case). Write with write_agent_file.
- After writing, ALWAYS verify: check_health (the agent must appear, not
  quarantined), then test_brainstem with a realistic user request and read the
  agent_logs to confirm YOUR agent actually ran.
- Use run_python to prototype logic before committing it to a file.
- Prefer stdlib + requests; the brainstem auto-installs missing pip deps once.
- Interview the user briefly when their ask is vague — but bias to building.
- Finish EVERY turn by calling report with a concise, friendly summary of what
  you did and what's now live. The user sees only report messages and tool
  activity — never raw thoughts.`;

interface Live {
  id: string;
  copilot: CopilotSession;
  title: string;
  busy: boolean;
}

class Surgeon {
  private client: CopilotClient | null = null;
  private clientStart: Promise<CopilotClient> | null = null;
  private readonly live = new Map<string, Live>();
  private counter = 0;

  async ensureClient(): Promise<CopilotClient> {
    if (this.client) return this.client;
    if (this.clientStart) return this.clientStart;
    this.clientStart = (async () => {
      const cliPath = resolveCopilotCliPath();
      if (!cliPath) {
        throw new Error(
          "No GitHub Copilot CLI found — set COPILOT_CLI_PATH or install the Copilot CLI.",
        );
      }
      const client = new CopilotClient({ connection: RuntimeConnection.forStdio({ path: cliPath }) });
      await client.start();
      const auth = await client.getAuthStatus();
      if (!auth.isAuthenticated) {
        await client.stop().catch(() => undefined);
        throw new Error(`Copilot isn't signed in — run: "${cliPath}" login`);
      }
      log.info("Copilot ready", auth.login ? `as ${auth.login}` : "");
      this.client = client;
      return client;
    })();
    try {
      return await this.clientStart;
    } catch (err) {
      this.clientStart = null;
      throw err;
    }
  }

  list(): { id: string; title: string; busy: boolean }[] {
    return [...this.live.values()].map(({ id, title, busy }) => ({ id, title, busy }));
  }

  async create(): Promise<string> {
    const client = await this.ensureClient();
    const id = `op-${++this.counter}`;
    const tools = this.buildTools(id);
    const copilot = await client.createSession({
      systemMessage: { mode: "append", content: SYSTEM() },
      tools,
      onPermissionRequest: approveAll,
      workingDirectory: agentsDir(),
      enableHostGitOperations: false,
      infiniteSessions: { enabled: false },
      availableTools: tools.map((t) => t.name),
      ...(process.env.MIRROR_SURGEON_MODEL ? { model: process.env.MIRROR_SURGEON_MODEL } : {}),
    });
    this.live.set(id, { id, copilot, title: "New operation", busy: false });
    return id;
  }

  async send(id: string, text: string): Promise<{ ok: boolean; error?: string }> {
    const live = this.live.get(id);
    if (!live) return { ok: false, error: "unknown session" };
    if (live.busy) return { ok: false, error: "The surgeon is mid-operation — wait for the report." };
    live.busy = true;
    if (live.title === "New operation") live.title = text.slice(0, 40);
    broadcast({ sessionId: id, kind: "status", text: "operating…" });
    try {
      await live.copilot.sendAndWait(text, TURN_TIMEOUT_MS);
      broadcast({ sessionId: id, kind: "done", text: "" });
      return { ok: true };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      broadcast({ sessionId: id, kind: "error", text: msg });
      return { ok: false, error: msg };
    } finally {
      live.busy = false;
    }
  }

  async cancel(id: string): Promise<void> {
    await this.live.get(id)?.copilot.abort().catch(() => undefined);
  }

  async close(id: string): Promise<void> {
    const live = this.live.get(id);
    this.live.delete(id);
    await live?.copilot.disconnect().catch(() => undefined);
  }

  async dispose(): Promise<void> {
    for (const id of [...this.live.keys()]) await this.close(id);
    await this.client?.stop().catch(() => undefined);
    this.client = null;
    this.clientStart = null;
  }

  private buildTools(sessionId: string): Tool[] {
    const tool = (kind: SurgeonEvent["kind"], text: string) =>
      broadcast({ sessionId, kind, text });
    return [
      {
        name: "write_agent_file",
        description:
          "Write (or overwrite) a single-file agent into the brainstem's agents directory. Filename must end in _agent.py. The kernel hot-loads it on the next request.",
        parameters: {
          type: "object",
          properties: {
            filename: { type: "string", description: "snake_case file name ending in _agent.py" },
            content: { type: "string", description: "the complete Python source" },
          },
          required: ["filename", "content"],
          additionalProperties: false,
        },
        handler: (input: unknown) => {
          const raw = input as { filename: string; content: string };
          if (!/^[a-z0-9_]+_agent\.py$/.test(raw.filename)) {
            return { textResultForLlm: "rejected: filename must match ^[a-z0-9_]+_agent\\.py$", resultType: "failure" as const };
          }
          const file = path.join(agentsDir(), raw.filename);
          writeFileSync(file, raw.content);
          tool("tool", `wrote ${raw.filename} (${raw.content.length} chars)`);
          return `written to ${file} — hot-loads on the next brainstem request`;
        },
      },
      {
        name: "read_agent_file",
        description: "Read an existing agent file from the brainstem's agents directory.",
        parameters: {
          type: "object",
          properties: { filename: { type: "string" } },
          required: ["filename"],
          additionalProperties: false,
        },
        handler: (input: unknown) => {
          const raw = input as { filename: string };
          const file = path.join(agentsDir(), path.basename(raw.filename));
          if (!existsSync(file)) return { textResultForLlm: "no such file", resultType: "failure" as const };
          tool("tool", `read ${path.basename(file)}`);
          return readFileSync(file, "utf8").slice(0, 20000);
        },
      },
      {
        name: "run_python",
        description:
          "Run a short Python snippet in the brainstem's venv (30s timeout, scratch cwd). Use to prototype before writing the agent file.",
        parameters: {
          type: "object",
          properties: { code: { type: "string" } },
          required: ["code"],
          additionalProperties: false,
        },
        handler: async (input: unknown) => {
          const raw = input as { code: string };
          tool("tool", "running python…");
          const cwd = mkdtempSync(path.join(os.tmpdir(), "surgeon-"));
          return await new Promise<string>((resolve) => {
            const child = spawn(venvPython(), ["-c", raw.code], { cwd });
            let out = "";
            const cap = (c: Buffer) => (out.length < 6000 ? (out += c.toString()) : undefined);
            child.stdout.on("data", cap);
            child.stderr.on("data", cap);
            const timer = setTimeout(() => {
              child.kill();
              resolve(out + "\n[killed: 30s timeout]");
            }, 30_000);
            child.on("exit", (code) => {
              clearTimeout(timer);
              resolve(`exit ${code}\n${out}`.slice(0, 6000));
            });
          });
        },
      },
      {
        name: "check_health",
        description: "GET /health on the brainstem: loaded agents, quarantined list, version.",
        parameters: { type: "object", properties: {}, additionalProperties: false },
        handler: async () => {
          const h = await health();
          tool("tool", `health: ${h.agents?.length ?? 0} agents${h.quarantined?.length ? ` · QUARANTINED: ${h.quarantined.join(",")}` : ""}`);
          return JSON.stringify(h);
        },
      },
      {
        name: "test_brainstem",
        description:
          "Send a real user request through the brainstem's /chat and see the answer plus which agents ran (agent_logs). The definitive live test.",
        parameters: {
          type: "object",
          properties: { user_input: { type: "string" } },
          required: ["user_input"],
          additionalProperties: false,
        },
        handler: async (input: unknown) => {
          const raw = input as { user_input: string };
          tool("tool", `testing: "${raw.user_input.slice(0, 60)}"`);
          const r = await chat(raw.user_input, [], `surgeon-${sessionId}`);
          return JSON.stringify(r).slice(0, 8000);
        },
      },
      {
        name: "report",
        description:
          "Report to the user — REQUIRED at the end of every turn. A concise, friendly summary of what you did and what is now live.",
        parameters: {
          type: "object",
          properties: { message: { type: "string" } },
          required: ["message"],
          additionalProperties: false,
        },
        handler: (input: unknown) => {
          const raw = input as { message: string };
          tool("report", raw.message);
          return "reported — you may stop now";
        },
      },
    ];
  }
}

export const surgeon = new Surgeon();
