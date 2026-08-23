import { strict as assert } from 'node:assert'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'

const read = (relative) =>
  readFileSync(new URL(`../${relative}`, import.meta.url), 'utf8')

const desktopPackage = JSON.parse(read('package.json'))
const main = read('electron/main.ts')
const preload = read('electron/preload.cjs')
const renderer = read('src/App.tsx')
const index = read('index.html')
const brainstem = read('electron/brainstem.ts')
const desktopService = read('electron/desktop-service.ts')
const fallbackServer = read('rapp_os/core/local_server.py')

test('Electron is the only native desktop shell', () => {
  assert.equal(desktopPackage.main, 'dist-electron/main.js')
  assert.ok(desktopPackage.devDependencies.electron)
  assert.ok(desktopPackage.devDependencies['electron-builder'])
  assert.equal(desktopPackage.dependencies?.['@tauri-apps/api'], undefined)
  assert.equal(desktopPackage.devDependencies?.['@tauri-apps/cli'], undefined)
})

test('main process applies renderer security and permission policy', () => {
  assert.match(main, /SECURE_RENDERER_PREFERENCES/)
  assert.match(main, /setPermissionRequestHandler/)
  assert.match(main, /callback\(false\)/)
})

test('preload exposes capabilities instead of a generic invoke primitive', () => {
  assert.match(preload, /contextBridge\.exposeInMainWorld\('rappDesktop', api\)/)
  assert.match(preload, /catalog:\s*Object\.freeze/)
  assert.match(preload, /projects:\s*Object\.freeze/)
  assert.match(preload, /brainstem:\s*Object\.freeze/)
  assert.doesNotMatch(preload, /invoke:\s*\(/)
  assert.doesNotMatch(renderer, /@tauri-apps|ipcRenderer|require\s*\(/)
  assert.match(renderer, /window\.rappDesktop/)
})

test('main process wires the resident companion shell', () => {
  assert.match(main, /requestSingleInstanceLock/)
  assert.match(main, /new Tray/)
  assert.match(main, /event\.preventDefault\(\)[\s\S]*window\.hide\(\)/)
  assert.match(main, /Launch at Login/)
  assert.match(main, /setWindowOpenHandler/)
  assert.match(main, /will-navigate/)
  assert.match(main, /window-all-closed[\s\S]*resident companion/)
  assert.match(main, /RAPP_DESKTOP_SMOKE/)
  assert.match(main, /RAPP_DESKTOP_SMOKE_OK/)
})

test('packaged renderer carries a restrictive content security policy', () => {
  assert.match(index, /Content-Security-Policy/)
  assert.match(index, /__RAPP_CSP__/)
  assert.match(read('vite.config.ts'), /connect-src 'none'/)
})

test('Brainstem authentication UI stays behind narrow main-process IPC', () => {
  assert.match(brainstem, /authentication-required/)
  assert.match(brainstem, /Remote Brainstem URLs must use HTTPS/)
  assert.match(brainstem, /async login\(\)/)
  assert.match(brainstem, /async pollLogin\(\)/)
  assert.match(main, /shell\.openExternal\(requireExternalUrl\(login\.verificationUrl\)\)/)
  assert.match(renderer, /Sign in with GitHub/)
})

test('bundled fallback requires a per-install capability secret', () => {
  assert.match(fallbackServer, /X-RAPP-Desktop-Secret/)
  assert.match(fallbackServer, /hmac\.compare_digest/)
  assert.match(fallbackServer, /Browser access is disabled/)
  assert.match(fallbackServer, /Content-Type must be application\/json/)
})

test('Store installs use the current catalog and verify artifact integrity', () => {
  assert.match(desktopService, /RAPP_Store\/main\/index\.json/)
  assert.match(desktopService, /rapp-store\/1\.0/)
  assert.match(desktopService, /singleton_sha256/)
  assert.match(desktopService, /createHash\('sha256'\)/)
  assert.match(desktopService, /Integrity check failed/)
})

test('Hub clones only the selected implementation through atomic staging', () => {
  assert.match(desktopService, /Implementation path/)
  assert.match(desktopService, /branch: requireGitRef/)
  assert.match(desktopService, /sparse-checkout/)
  assert.match(desktopService, /stagingDirectory/)
  assert.match(desktopService, /finally\s*\{[\s\S]*rm\(staging/)
})

test('terminal authentication failures stop polling and expose retry', () => {
  assert.match(brainstem, /authentication-failed/)
  assert.match(renderer, /status\.phase === 'authentication-failed'/)
  assert.match(renderer, /Retry GitHub sign-in/)
})

test('login-item UI is limited to platforms Electron supports', () => {
  assert.match(main, /process\.platform === 'darwin'[\s\S]*process\.platform === 'win32'/)
  assert.match(main, /visible: supportsLoginItem/)
})
