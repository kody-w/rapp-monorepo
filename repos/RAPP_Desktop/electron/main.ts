import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  Menu,
  nativeImage,
  session,
  shell,
  Tray,
  type IpcMainInvokeEvent,
} from 'electron'

import type { BrainstemStatus } from '../src/desktop-api.js'
import { BrainstemManager } from './brainstem.js'
import { IPC } from './channels.js'
import { DesktopService } from './desktop-service.js'
import {
  isTrustedRendererUrl,
  requireExternalUrl,
  resolveRendererTarget,
  SECURE_RENDERER_PREFERENCES,
} from './security.js'

const sourceDirectory = path.dirname(fileURLToPath(import.meta.url))
const preloadPath = path.join(sourceDirectory, 'preload.cjs')
const rendererDirectory = path.join(app.getAppPath(), 'dist')
const rendererIndex = path.join(rendererDirectory, 'index.html')
const rendererTarget = resolveRendererTarget({
  isPackaged: app.isPackaged,
  developmentUrl: process.env.VITE_DEV_SERVER_URL,
  rendererIndex,
})
const desktopSmoke = process.env.RAPP_DESKTOP_SMOKE === '1'

let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null
let quitting = false
let shutdownComplete = false
let brainstem: BrainstemManager | null = null
let latestStatus: BrainstemStatus = {
  running: false,
  port: 7071,
  endpoint: 'http://127.0.0.1:7071/chat',
  managed: false,
  phase: 'checking',
}

function isTrustedRenderer(rawUrl: string): boolean {
  return isTrustedRendererUrl(rawUrl, rendererTarget, rendererDirectory)
}

function assertTrustedSender(event: IpcMainInvokeEvent): void {
  const senderUrl = event.senderFrame?.url
  if (!senderUrl || !isTrustedRenderer(senderUrl)) {
    throw new Error('Rejected IPC from an untrusted renderer.')
  }
}

type IpcHandler = (payload: unknown) => unknown | Promise<unknown>

function handle(channel: string, handler: IpcHandler): void {
  ipcMain.handle(channel, (event, payload) => {
    assertTrustedSender(event)
    return handler(payload)
  })
}

function registerIpc(service: DesktopService): void {
  handle(IPC.appInfo, () => ({
    version: app.getVersion(),
    platform: process.platform,
  }))
  handle(IPC.catalogStore, () => service.storeManifest())
  handle(IPC.catalogHub, () => service.hubManifest())
  handle(IPC.catalogInstallAgent, (payload) => service.installAgent(payload))
  handle(IPC.catalogInstallSkill, (payload) => service.installSkill(payload))
  handle(IPC.projectsList, () => service.listProjects())
  handle(IPC.projectsCreate, (payload) => service.createProject(payload))
  handle(IPC.projectsClone, (payload) => service.cloneImplementation(payload))
  handle(IPC.projectsReveal, async (payload) => {
    const error = await shell.openPath(service.projectPath(payload))
    if (error) throw new Error(error)
  })
  handle(IPC.brainstemStatus, () => brainstem!.status())
  handle(IPC.brainstemStart, () => brainstem!.start())
  handle(IPC.brainstemStop, () => brainstem!.stop())
  handle(IPC.brainstemChat, (payload) => brainstem!.chat(payload))
  handle(IPC.brainstemCancelChat, (payload) => brainstem!.cancelChat(payload))
  handle(IPC.brainstemLogin, async () => {
    const login = await brainstem!.login()
    await shell.openExternal(requireExternalUrl(login.verificationUrl))
    return login
  })
  handle(IPC.brainstemLoginPoll, () => brainstem!.pollLogin())
  handle(IPC.shellOpenExternal, async (payload) => {
    await shell.openExternal(requireExternalUrl(payload))
  })
}

function trayIcon(): Electron.NativeImage {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">
      <rect width="22" height="22" rx="6" fill="#10231f"/>
      <path d="M5 13c1.5-5 5-7 9-5 2 1 3 3 2 5-1 2-3 3-5 2l-1 3-2-1 1-3c-2 0-3 0-4-1z" fill="#58f5d2"/>
      <circle cx="13.8" cy="9.7" r="1" fill="#10231f"/>
    </svg>`
  const image = nativeImage.createFromDataURL(
    `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`,
  )
  if (process.platform === 'darwin') image.setTemplateImage(true)
  return image
}

function showWindow(): void {
  if (!mainWindow || mainWindow.isDestroyed()) {
    mainWindow = createWindow()
  }
  if (mainWindow.isMinimized()) mainWindow.restore()
  mainWindow.show()
  mainWindow.focus()
}

function refreshTray(): void {
  if (!tray) return
  const brainstemReady = latestStatus.phase === 'ready'
  const supportsLoginItem = process.platform === 'darwin'
    || process.platform === 'win32'
  const login = supportsLoginItem
    ? app.getLoginItemSettings().openAtLogin
    : false
  const statusLabel = brainstemReady
    ? `Brainstem ready on :${latestStatus.port}`
    : latestStatus.phase === 'starting'
      ? 'Brainstem is starting'
      : latestStatus.phase === 'error'
        ? 'Brainstem is unavailable'
      : 'Brainstem is offline'
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Open RAPP Desktop', click: showWindow },
    { label: statusLabel, enabled: false },
    {
      label: brainstemReady ? 'Check Brainstem' : 'Wake Brainstem',
      click: () => {
        const action = brainstemReady ? brainstem!.status() : brainstem!.start()
        void action.catch(showError)
      },
    },
    {
      label: 'Stop bundled Brainstem',
      visible: latestStatus.running && latestStatus.managed,
      click: () => void brainstem!.stop().catch(showError),
    },
    { type: 'separator' },
    {
      label: 'Launch at Login',
      type: 'checkbox',
      visible: supportsLoginItem,
      checked: login,
      click: (item) => {
        app.setLoginItemSettings({ openAtLogin: item.checked })
        refreshTray()
      },
    },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]))
}

function updateStatus(status: BrainstemStatus): void {
  latestStatus = status
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(IPC.brainstemStatusChanged, status)
  }
  refreshTray()
}

function createTray(): void {
  tray = new Tray(trayIcon())
  tray.setToolTip('RAPP Desktop')
  tray.on('click', showWindow)
  refreshTray()
}

function createWindow(): BrowserWindow {
  const window = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    backgroundColor: '#0a0a0f',
    title: 'RAPP Desktop',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      ...SECURE_RENDERER_PREFERENCES,
      preload: preloadPath,
      safeDialogs: true,
    },
  })

  window.webContents.setWindowOpenHandler(({ url }) => {
    try {
      void shell.openExternal(requireExternalUrl(url))
    } catch (error) {
      console.warn('Blocked external window:', error)
    }
    return { action: 'deny' }
  })
  window.webContents.on('will-navigate', (event, url) => {
    if (isTrustedRenderer(url)) return
    event.preventDefault()
    try {
      void shell.openExternal(requireExternalUrl(url))
    } catch (error) {
      console.warn('Blocked renderer navigation:', error)
    }
  })
  window.webContents.on('render-process-gone', (_event, details) => {
    if (!quitting) {
      void dialog.showMessageBox({
        type: 'error',
        title: 'RAPP Desktop needs to reload',
        message: `The companion surface stopped (${details.reason}).`,
        buttons: ['Reload'],
      }).then(() => window.reload())
    }
  })
  if (desktopSmoke) {
    window.webContents.once('did-finish-load', () => {
      console.log('RAPP_DESKTOP_SMOKE_OK')
      app.quit()
    })
  }
  window.once('ready-to-show', () => {
    if (!desktopSmoke && !process.argv.includes('--hidden')) window.show()
  })
  window.on('close', (event) => {
    if (!quitting) {
      event.preventDefault()
      window.hide()
    }
  })
  window.on('closed', () => {
    if (mainWindow === window) mainWindow = null
  })

  if (rendererTarget.kind === 'development') {
    void window.loadURL(rendererTarget.url)
  } else {
    void window.loadFile(rendererTarget.path)
  }
  return window
}

async function showError(error: unknown): Promise<void> {
  await dialog.showMessageBox({
    type: 'error',
    title: 'RAPP Desktop action failed',
    message: error instanceof Error ? error.message : String(error),
  })
}

async function bootstrap(): Promise<void> {
  app.setAppUserModelId('com.rapp.desktop')
  session.defaultSession.setPermissionRequestHandler(
    (_webContents, _permission, callback) => callback(false),
  )

  const service = new DesktopService()
  await service.initialize()
  const legacyScriptPath = app.isPackaged
    ? path.join(process.resourcesPath, 'rapp_os', 'rapp_os.py')
    : path.join(app.getAppPath(), 'rapp_os', 'rapp_os.py')
  brainstem = new BrainstemManager({
    legacyScriptPath,
    onStatus: updateStatus,
  })

  registerIpc(service)
  if (!desktopSmoke) createTray()
  mainWindow = createWindow()

  if (desktopSmoke) return
  void brainstem.start().catch(async (error) => {
    updateStatus({
      ...brainstem!.currentStatus(),
      running: false,
      phase: 'error',
      detail: error instanceof Error ? error.message : String(error),
    })
    await showError(error)
  })
}

if (!app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', showWindow)
  app.on('activate', showWindow)
  app.on('window-all-closed', () => {
    // RAPP remains available in the tray as a resident companion.
  })
  app.on('before-quit', (event) => {
    quitting = true
    if (shutdownComplete) return
    event.preventDefault()
    void (brainstem?.dispose() ?? Promise.resolve()).finally(() => {
      shutdownComplete = true
      app.quit()
    })
  })

  void app.whenReady().then(bootstrap).catch((error) => {
    dialog.showErrorBox(
      'RAPP Desktop could not start',
      error instanceof Error ? error.message : String(error),
    )
    shutdownComplete = true
    app.quit()
  })
}
