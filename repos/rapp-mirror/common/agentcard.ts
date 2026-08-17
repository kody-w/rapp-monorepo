/**
 * The agent card — what you learn about an `agent.py` *before* you let it into
 * your brainstem.
 *
 * Sharing agents is the point: forge one, AirDrop it, and it hot-loads into
 * someone else's kernel. But a file that hot-loads is a file that executes, so
 * a received agent is never installed automatically. It is parsed into a card
 * (what it calls itself, what it says it does, what it will run), scanned for
 * capabilities that deserve a human's attention, and held until someone says
 * yes.
 *
 * Pure and dependency-free on purpose: the same logic runs in the main
 * process, in a node:test, and — ported line-for-line — on iOS.
 */

export type Severity = "critical" | "warn";

export interface Finding {
  severity: Severity;
  /** Stable id so a UI can group/explain findings. */
  id: string;
  /** What the agent can do, in the reader's language. */
  detail: string;
  /** 1-based line in the source where it was seen. */
  line: number;
  evidence: string;
}

export type Verdict = "safe" | "review" | "dangerous" | "invalid";

export interface AgentCard {
  ok: boolean;
  verdict: Verdict;
  className: string;
  name: string;
  description: string;
  parameters: { name: string; description: string }[];
  /** The declared procedure, when the sender forged it with the Forge. */
  steps: string[];
  findings: Finding[];
  /** sha256 is not available here without node:crypto; the caller stamps it. */
  lineCount: number;
  /** Why the file could not be read as an agent at all. */
  error?: string;
}

/** Capability probes. Each is a plain regex over source lines — deliberately
 *  conservative: a false positive costs a glance, a false negative costs a
 *  machine. */
const PROBES: { id: string; severity: Severity; re: RegExp; detail: string }[] = [
  {
    id: "exec",
    severity: "critical",
    re: /\b(?:exec|eval)\s*\(/,
    detail: "runs code built at runtime (exec/eval)",
  },
  {
    id: "shell",
    severity: "critical",
    re: /\b(?:subprocess|os\.system|os\.popen|os\.execv|pty\.spawn)\b/,
    detail: "runs shell commands on your machine",
  },
  {
    id: "credentials",
    severity: "critical",
    re: /(?:\.ssh|\.env\b|id_rsa|keychain|\.brainstem_secret|AWS_SECRET|credentials\.json)/i,
    detail: "reaches for credentials or private keys",
  },
  {
    id: "obfuscation",
    severity: "critical",
    re: /base64\s*\.\s*b64decode|codecs\s*\.\s*decode\s*\([^)]*rot13|bytes\.fromhex/,
    detail: "decodes hidden content before running it",
  },
  {
    id: "network",
    severity: "warn",
    re: /\b(?:requests|httpx|urllib|http\.client|socket|aiohttp)\b/,
    detail: "sends or receives data over the network",
  },
  {
    id: "filewrite",
    severity: "warn",
    re: /\b(?:shutil\.rmtree|os\.remove|os\.unlink|\.write_text\s*\(|\.write_bytes\s*\()|open\s*\([^)]*['"][wa]/,
    detail: "writes to or deletes files",
  },
  {
    id: "dynamic-import",
    severity: "warn",
    re: /\b(?:__import__|importlib)\b/,
    detail: "loads other modules dynamically",
  },
  {
    id: "env",
    severity: "warn",
    re: /os\.environ\b/,
    detail: "reads environment variables",
  },
];

/** Comment and docstring lines are noise for a capability scan. */
function isProse(line: string): boolean {
  const t = line.trim();
  return t.startsWith("#") || t === '"""' || t === "'''";
}

const firstMatch = (source: string, re: RegExp): string | undefined =>
  source.match(re)?.[1];

/** Read the metadata dict's `properties` block into a flat parameter list. */
function parseParameters(source: string): { name: string; description: string }[] {
  const block = source.match(/"properties"\s*:\s*\{([\s\S]*?)\n\s*\}\s*,\s*\n\s*"required"/);
  if (!block) return [];
  const out: { name: string; description: string }[] = [];
  const entry = /"([A-Za-z_][\w]*)"\s*:\s*\{[^}]*?"description"\s*:\s*"((?:[^"\\]|\\.)*)"/g;
  for (const m of block[1].matchAll(entry)) {
    out.push({ name: m[1], description: m[2].replace(/\\"/g, '"') });
  }
  return out;
}

/** Pull the forged procedure back out of the rendered agent. */
function parseSteps(source: string): string[] {
  const block = source.match(/steps\s*=\s*\[([\s\S]*?)\]/);
  if (!block) return [];
  return [...block[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)]
    .map((m) => m[1].replace(/\\"/g, '"'))
    .filter(Boolean);
}

/** Inspect a candidate agent file. Never throws — a hostile file is data. */
export function inspectAgentSource(source: string): AgentCard {
  const lines = source.split("\n");
  const base: AgentCard = {
    ok: false,
    verdict: "invalid",
    className: "",
    name: "",
    description: "",
    parameters: [],
    steps: [],
    findings: [],
    lineCount: lines.length,
  };

  if (!source.trim()) return { ...base, error: "the file is empty" };

  const className = firstMatch(source, /class\s+([A-Za-z_]\w*)\s*\(\s*BasicAgent\s*\)/);
  if (!className) {
    return {
      ...base,
      error: "not a RAPP agent: no `class <Name>(BasicAgent)` was found",
    };
  }
  if (!/def\s+perform\s*\(/.test(source)) {
    return { ...base, className, error: "not a RAPP agent: it has no perform() method" };
  }

  const findings: Finding[] = [];
  lines.forEach((line, index) => {
    if (isProse(line)) return;
    for (const probe of PROBES) {
      if (probe.re.test(line)) {
        findings.push({
          severity: probe.severity,
          id: probe.id,
          detail: probe.detail,
          line: index + 1,
          evidence: line.trim().slice(0, 160),
        });
      }
    }
  });

  // One finding per capability is enough to make the decision.
  const seen = new Set<string>();
  const deduped = findings.filter((f) => (seen.has(f.id) ? false : seen.add(f.id)));

  const verdict: Verdict = deduped.some((f) => f.severity === "critical")
    ? "dangerous"
    : deduped.length
      ? "review"
      : "safe";

  return {
    ok: true,
    verdict,
    className,
    name: firstMatch(source, /self\.name\s*=\s*"([^"]+)"/) || className,
    description:
      firstMatch(source, /"description"\s*:\s*"((?:[^"\\]|\\.)*)"/)?.replace(/\\"/g, '"') || "",
    parameters: parseParameters(source),
    steps: parseSteps(source),
    findings: deduped,
    lineCount: lines.length,
  };
}

/** The one-line answer a human reads before deciding. */
export function cardSummary(card: AgentCard): string {
  if (!card.ok) return card.error || "unreadable";
  const what = card.description || "no description";
  switch (card.verdict) {
    case "safe":
      return `${card.className} — ${what}. Runs no shell, no network, no file writes.`;
    case "review":
      return `${card.className} — ${what}. Also: ${card.findings.map((f) => f.detail).join("; ")}.`;
    default:
      return `${card.className} — ${what}. DANGEROUS: ${card.findings
        .filter((f) => f.severity === "critical")
        .map((f) => f.detail)
        .join("; ")}.`;
  }
}
