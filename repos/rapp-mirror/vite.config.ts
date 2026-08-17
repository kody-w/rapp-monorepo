import { copyFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import electron from "vite-plugin-electron";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

/** The preload is CommonJS on purpose (isolated world); ship it verbatim. */
function copyPreload(): void {
  const out = path.join(rootDir, "dist-electron");
  mkdirSync(out, { recursive: true });
  copyFileSync(path.join(rootDir, "electron", "preload.cjs"), path.join(out, "preload.cjs"));
}

export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        entry: "electron/main.ts",
        onstart(args) {
          copyPreload();
          const env = { ...process.env };
          delete env.ELECTRON_RUN_AS_NODE;
          void args.startup([".", "--no-sandbox", "--remote-debugging-port=9333"], { env });
        },
        vite: {
          build: {
            outDir: "dist-electron",
            rolldownOptions: { external: ["electron"] },
          },
          plugins: [{ name: "copy-preload", closeBundle: copyPreload }],
        },
      },
    ]),
  ],
});
