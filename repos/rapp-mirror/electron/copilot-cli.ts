import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";

const require = createRequire(import.meta.url);

/**
 * Locate a GitHub Copilot CLI binary for the Brain Surgeon's agent loop
 * (skill-recorder resolves a bundled per-platform package; the mirror checks,
 * in order: an explicit override, a bundled package, PATH, and the VS Code
 * Copilot Chat install every Copilot-enabled VS Code already carries).
 */
export function resolveCopilotCliPath(): string | null {
  if (process.env.COPILOT_CLI_PATH && existsSync(process.env.COPILOT_CLI_PATH)) {
    return process.env.COPILOT_CLI_PATH;
  }
  try {
    const pkg = `@github/copilot-${process.platform}-${process.arch}`;
    const dir = path.dirname(require.resolve(`${pkg}/package.json`));
    const bin = path.join(dir, process.platform === "win32" ? "copilot.exe" : "copilot");
    if (existsSync(bin)) return bin;
  } catch {
    /* not bundled */
  }
  for (const candidate of [
    "/opt/homebrew/bin/copilot",
    "/usr/local/bin/copilot",
    path.join(
      os.homedir(),
      "Library",
      "Application Support",
      "Code",
      "User",
      "globalStorage",
      "github.copilot-chat",
      "copilotCli",
      "copilot",
    ),
  ]) {
    if (existsSync(candidate)) return candidate;
  }
  return null;
}
