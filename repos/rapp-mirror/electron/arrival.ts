import type { ReceivedAgent } from "./agentshare.ts";
import { createLogger } from "./logger.ts";
import { mirrorWindow } from "./window.ts";

/**
 * Announcing an arrival.
 *
 * Every way an agent can arrive — AirDrop (`open-file`), a scanned card
 * (`open-url`), a second instance, or the control plane — surfaces the same
 * consent card in the same place. One door, one moment, one decision, so an
 * autonomous driver and a human see identical behaviour.
 */

const log = createLogger("Arrival");

export function announceArrival(received: ReceivedAgent): void {
  if (received.ok) {
    log.info("agent arrived:", received.summary ?? received.card?.className ?? "");
  } else {
    log.warn("agent refused:", received.error ?? "unreadable");
  }

  const window = mirrorWindow();
  if (!window) return;
  window.webContents.send("mirror:agent-arrived", received);
  if (window.isMinimized()) window.restore();
  window.focus();
}
