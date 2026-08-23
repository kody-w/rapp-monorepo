import { copyFileSync, mkdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import electron from 'vite-plugin-electron'

const rootDir = path.dirname(fileURLToPath(import.meta.url))

function copyPreload(): void {
  const outputDirectory = path.join(rootDir, 'dist-electron')
  mkdirSync(outputDirectory, { recursive: true })
  copyFileSync(
    path.join(rootDir, 'electron', 'preload.cjs'),
    path.join(outputDirectory, 'preload.cjs'),
  )
}

export default defineConfig(({ command }) => ({
  base: './',
  plugins: [
    react(),
    {
      name: 'rapp-content-security-policy',
      transformIndexHtml(html) {
        const connectSource = command === 'serve'
          ? "connect-src 'self' ws://127.0.0.1:5173"
          : "connect-src 'none'"
        return html.replace(
          '__RAPP_CSP__',
          `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; ${connectSource}; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`,
        )
      },
    },
    electron([
      {
        entry: 'electron/main.ts',
        onstart(args) {
          copyPreload()
          const env = { ...process.env }
          delete env.ELECTRON_RUN_AS_NODE
          void args.startup(['.'], { env })
        },
        vite: {
          build: {
            outDir: 'dist-electron',
            rolldownOptions: { external: ['electron'] },
          },
          plugins: [{ name: 'copy-preload', closeBundle: copyPreload }],
        },
      },
    ]),
  ],
  clearScreen: false,
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
  },
  build: {
    target: 'chrome142',
    sourcemap: command === 'serve',
  },
}))
