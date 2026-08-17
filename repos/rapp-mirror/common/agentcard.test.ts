import assert from "node:assert/strict";
import { test } from "node:test";

import { cardSummary, inspectAgentSource } from "./agentcard.ts";

/** A forged agent, exactly as the Forge renders one. */
const forged = `"""RAPP agent."""

import json

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name = name or self.__class__.__name__


class WeeklyBilling(BasicAgent):
    def __init__(self):
        self.name = "WeeklyBilling"
        self.metadata = {
            "name": self.name,
            "description": "Tally unbilled time and email each client.",
            "parameters": {
                "type": "object",
                "properties": {
            "run_date": {"type": "string", "description": "Billing period end date"},
            "dry_run": {"type": "string", "description": "Preview without sending"}
                },
                "required": [],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        steps = [
        "1. Fetch unbilled entries",
        "2. Total per client"
        ]
        return json.dumps({"status": "procedure", "procedure": steps})
`;

test("a forged agent reads back as a complete, safe card", () => {
  const card = inspectAgentSource(forged);
  assert.equal(card.ok, true);
  assert.equal(card.verdict, "safe");
  assert.equal(card.className, "WeeklyBilling");
  assert.equal(card.name, "WeeklyBilling");
  assert.equal(card.description, "Tally unbilled time and email each client.");
  assert.deepEqual(
    card.parameters.map((p) => p.name),
    ["run_date", "dry_run"],
  );
  assert.deepEqual(card.steps, ["1. Fetch unbilled entries", "2. Total per client"]);
  assert.equal(card.findings.length, 0);
});

test("a file that is not a RAPP agent is refused with a reason, not a crash", () => {
  const card = inspectAgentSource("print('hello')\n");
  assert.equal(card.ok, false);
  assert.equal(card.verdict, "invalid");
  assert.match(card.error ?? "", /no `class <Name>\(BasicAgent\)`/);
});

test("an agent with no perform() is refused", () => {
  const card = inspectAgentSource("class X(BasicAgent):\n    pass\n");
  assert.equal(card.ok, false);
  assert.match(card.error ?? "", /no perform\(\)/);
});

test("an empty file is refused rather than treated as a safe agent", () => {
  const card = inspectAgentSource("   \n");
  assert.equal(card.ok, false);
  assert.equal(card.verdict, "invalid");
});

test("shell execution is flagged critical and makes the verdict dangerous", () => {
  const card = inspectAgentSource(
    forged.replace("import json", "import json\nimport subprocess"),
  );
  assert.equal(card.verdict, "dangerous");
  const shell = card.findings.find((f) => f.id === "shell");
  assert.equal(shell?.severity, "critical");
  assert.ok(shell!.line > 0);
});

test("exec of runtime-built code is flagged critical", () => {
  const card = inspectAgentSource(forged.replace("steps = [", "exec(kwargs['x'])\n        steps = ["));
  assert.equal(card.verdict, "dangerous");
  assert.ok(card.findings.some((f) => f.id === "exec"));
});

test("reaching for credentials is flagged critical", () => {
  const card = inspectAgentSource(forged.replace("steps = [", "open('~/.ssh/id_rsa')\n        steps = ["));
  assert.equal(card.verdict, "dangerous");
  assert.ok(card.findings.some((f) => f.id === "credentials"));
});

test("base64-decoded payloads are treated as obfuscation", () => {
  const card = inspectAgentSource(
    forged.replace("steps = [", "p = base64.b64decode(BLOB)\n        steps = ["),
  );
  assert.equal(card.verdict, "dangerous");
  assert.ok(card.findings.some((f) => f.id === "obfuscation"));
});

test("network access is a warning that asks for review, not a refusal", () => {
  const card = inspectAgentSource(forged.replace("import json", "import json\nimport requests"));
  assert.equal(card.verdict, "review");
  assert.equal(card.findings[0].severity, "warn");
});

test("file writes are surfaced so the reader knows what it touches", () => {
  const card = inspectAgentSource(forged.replace("steps = [", "open('/tmp/x','w')\n        steps = ["));
  assert.equal(card.verdict, "review");
  assert.ok(card.findings.some((f) => f.id === "filewrite"));
});

test("a capability mentioned only in a comment does not raise a finding", () => {
  const card = inspectAgentSource(
    forged.replace("import json", "import json\n# this agent never uses subprocess"),
  );
  assert.equal(card.verdict, "safe");
});

test("repeated uses of one capability collapse into a single finding", () => {
  const card = inspectAgentSource(
    forged.replace("import json", "import json\nimport requests\nimport httpx\nimport socket"),
  );
  assert.equal(card.findings.filter((f) => f.id === "network").length, 1);
});

test("the summary tells a human what they are about to accept", () => {
  assert.match(cardSummary(inspectAgentSource(forged)), /Runs no shell, no network/);
  const risky = inspectAgentSource(forged.replace("import json", "import json\nimport subprocess"));
  assert.match(cardSummary(risky), /DANGEROUS: runs shell commands/);
});

test("a hostile file cannot throw out of the inspector", () => {
  const nasty = "class X(BasicAgent):\n  def perform(self):\n" + '    s = "' + "\\".repeat(500) + '"\n';
  assert.doesNotThrow(() => inspectAgentSource(nasty));
  assert.doesNotThrow(() => inspectAgentSource("\u0000\uFFFF".repeat(1000)));
});
