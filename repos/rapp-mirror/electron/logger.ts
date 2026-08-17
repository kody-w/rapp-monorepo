/** Tiny namespaced logger for the main process (skill-recorder idiom).
 *
 *  Every line also lands in the local evidence ledger, so a failure that
 *  scrolled past in a terminal — or happened in a packaged app with no
 *  terminal at all — is still answerable from the machine afterwards. */
import { record } from "./diagnostics.ts";

const say = (args: unknown[]) =>
  args
    .map((a) =>
      typeof a === "string" ? a : a instanceof Error ? a.message : JSON.stringify(a),
    )
    .join(" ");

export function createLogger(name: string) {
  const prefix = `[${name}]`;
  const tee = (level: "info" | "warn" | "error", args: unknown[]) => {
    try {
      record({ component: name, level, message: say(args) });
    } catch {
      // The ledger is evidence, not a dependency: never break a log call.
    }
  };
  return {
    info: (...args: unknown[]) => {
      console.log(prefix, ...args);
      tee("info", args);
    },
    warn: (...args: unknown[]) => {
      console.warn(prefix, ...args);
      tee("warn", args);
    },
    error: (...args: unknown[]) => {
      console.error(prefix, ...args);
      tee("error", args);
    },
  };
}
