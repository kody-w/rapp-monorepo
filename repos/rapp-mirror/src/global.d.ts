import type { MirrorApi } from "../common/ipc.ts";

declare global {
  interface Window {
    /** Preload bridge (electron/preload.cjs). */
    mirror: MirrorApi;
    /** Console/automation surface installed by Mirror.tsx — drive the whole
     *  app from DevTools or any CDP client on the remote-debugging port. */
    mirrorDebug?: Record<string, unknown>;
  }
}

export {};
