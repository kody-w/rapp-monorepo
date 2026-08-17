import type http from "node:http";

/** Browsers can fire cross-origin no-cors POSTs at 127.0.0.1 — but they
 *  always attach an Origin header and can't send application/json. Real
 *  local clients (mirrorctl, scripts) do the opposite on both counts, so
 *  these two checks (+ a loopback Host, against DNS rebinding) shut the
 *  drive-by door without costing any legitimate caller anything. */
export function trustedLocalRequest(req: Pick<http.IncomingMessage, "headers">): boolean {
  if (req.headers.origin) return false;
  const host = String(req.headers.host || "").split(":")[0];
  if (host !== "127.0.0.1" && host !== "localhost" && host !== "[::1]") return false;
  return String(req.headers["content-type"] || "").split(";")[0].trim() === "application/json";
}
