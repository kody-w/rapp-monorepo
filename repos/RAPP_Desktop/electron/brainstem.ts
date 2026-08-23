import {
  execFile,
  spawn,
  type ChildProcess,
} from 'node:child_process'
import {
  existsSync,
  lstatSync,
  readFileSync,
} from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import type {
  BrainstemChatRequest,
  BrainstemChatResponse,
  BrainstemLogin,
  BrainstemStatus,
  ChatTurn,
} from '../src/desktop-api.js'
import {
  assessLoopbackPeer,
  parseLsofListeners,
  PeerIdentityError,
  requireRecord,
  requireString,
  type LauncherResult,
  type ListenerProcess,
  type PeerVerification,
  useTrustedPeer,
  waitAfterLauncher,
} from './security.js'

const HEALTH_TIMEOUT_MS = 5_000
const CHAT_TIMEOUT_MS = 120_000
const CANCEL_TIMEOUT_MS = 10_000
const START_TIMEOUT_MS = 45_000

export interface BrainstemManagerOptions {
  legacyScriptPath: string
  onStatus(status: BrainstemStatus): void
  baseUrl?: string
  fetch?: typeof fetch
  verifyPeer?(
    port: number,
    managedPid?: number,
  ): Promise<PeerVerification>
  credentialHeaders?(): Record<string, string>
}

interface CommandResult {
  executed: boolean
  succeeded: boolean
  output: string
}

function normalizeBaseUrl(raw: string): string {
  const url = new URL(raw)
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
    throw new TypeError('RAPP_BRAINSTEM_URL must be an HTTP(S) URL without credentials.')
  }
  if (url.protocol === 'http:' && !isLoopback(url.hostname)) {
    throw new TypeError('Remote Brainstem URLs must use HTTPS.')
  }
  return url.toString().replace(/\/$/, '')
}

function isLoopback(hostname: string): boolean {
  return ['127.0.0.1', 'localhost', '::1', '[::1]'].includes(hostname)
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

function runCommand(command: string, args: readonly string[]): Promise<CommandResult> {
  return new Promise((resolve) => {
    execFile(
      command,
      [...args],
      { encoding: 'utf8', windowsHide: true },
      (error, stdout) => {
        const code = error && 'code' in error ? error.code : undefined
        resolve({
          executed: code !== 'ENOENT',
          succeeded: error === null,
          output: typeof stdout === 'string' ? stdout : '',
        })
      },
    )
  })
}

export function windowsListenerScript(port: number): string {
  return [
    `$connections = @(Get-NetTCPConnection -State Listen -LocalPort ${port} -ErrorAction SilentlyContinue)`,
    '$processIds = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)',
    'foreach ($processId in $processIds) {',
    '$process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue',
    'if ($process) {',
    '$owner = Invoke-CimMethod -InputObject $process -MethodName GetOwner',
    'Write-Output ("{0}|{1}\\{2}" -f $processId,$owner.Domain,$owner.User)',
    '}',
    '}',
  ].join('; ')
}

function readPrivateSecret(secretPath: string): string {
  let stats
  try {
    stats = lstatSync(secretPath)
  } catch (error) {
    if (
      error
      && typeof error === 'object'
      && 'code' in error
      && error.code === 'ENOENT'
    ) {
      return ''
    }
    throw error
  }
  if (!stats.isFile() || stats.isSymbolicLink()) {
    throw new Error(`Brainstem secret is not a private regular file: ${secretPath}`)
  }
  if (
    process.platform !== 'win32'
    && (
      (typeof process.getuid === 'function' && stats.uid !== process.getuid())
      || (stats.mode & 0o077) !== 0
    )
  ) {
    throw new Error(`Brainstem secret file permissions are unsafe: ${secretPath}`)
  }
  return readFileSync(secretPath, 'utf8').trim()
}

function parseWindowsListeners(output: string): ListenerProcess[] {
  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .flatMap((line) => {
      const separator = line.indexOf('|')
      const pid = Number(line.slice(0, separator))
      const ownerId = line.slice(separator + 1).trim()
      return separator > 0 && Number.isSafeInteger(pid) && pid > 0
        ? [{ pid, ownerId }]
        : []
    })
}

async function inspectLoopbackPeer(
  port: number,
  managedPid?: number,
): Promise<PeerVerification> {
  if (process.platform === 'win32') {
    const script = windowsListenerScript(port)
    const result = await runCommand(
      process.env.SystemRoot
        ? path.join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
        : 'powershell.exe',
      ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
    )
    if (!result.executed || !result.succeeded) {
      return {
        kind: 'untrusted',
        detail: 'Cannot verify ownership of the local Brainstem endpoint.',
      }
    }
    const username = process.env.USERNAME ?? ''
    const domain = process.env.USERDOMAIN ?? ''
    return assessLoopbackPeer(
      parseWindowsListeners(result.output),
      [`${domain}\\${username}`, username],
      managedPid,
    )
  }

  const candidates = [
    '/usr/sbin/lsof',
    '/usr/bin/lsof',
    'lsof',
  ]
  let executed = false
  let output = ''
  for (const candidate of candidates) {
    if (path.isAbsolute(candidate) && !existsSync(candidate)) continue
    const result = await runCommand(candidate, [
      '-nP',
      '-a',
      `-iTCP:${port}`,
      '-sTCP:LISTEN',
      '-Fpu',
    ])
    if (!result.executed) continue
    executed = true
    output = result.output
    break
  }
  if (!executed && process.platform === 'linux') {
    const result = await runCommand('ss', [
      '-ltnpH',
      `sport = :${port}`,
    ])
    if (result.executed) {
      executed = true
      output = result.output
      const listeners: ListenerProcess[] = []
      for (const [index, line] of output.split(/\r?\n/).entries()) {
        const processIds = [...line.matchAll(/pid=(\d+)/g)]
        if (processIds.length === 0 && line.trim()) {
          listeners.push({ pid: -(index + 1), ownerId: '' })
        } else {
          for (const match of processIds) {
            listeners.push({
              pid: Number(match[1]),
              ownerId: String(process.getuid?.() ?? ''),
            })
          }
        }
      }
      return assessLoopbackPeer(
        listeners,
        [String(process.getuid?.() ?? ''), os.userInfo().username],
        managedPid,
      )
    }
  }
  if (!executed || typeof process.getuid !== 'function') {
    return {
      kind: 'untrusted',
      detail: 'Cannot verify ownership of the local Brainstem endpoint.',
    }
  }
  return assessLoopbackPeer(
    parseLsofListeners(output),
    [String(process.getuid()), os.userInfo().username],
    managedPid,
  )
}

function parseHistory(value: unknown): ChatTurn[] {
  if (value === undefined || value === null) return []
  if (!Array.isArray(value) || value.length > 200) {
    throw new TypeError('Conversation history must contain at most 200 turns.')
  }
  return value.map((turn, index) => {
    const record = requireRecord(turn, `Conversation turn ${index + 1}`)
    if (record.role !== 'user' && record.role !== 'assistant') {
      throw new TypeError(`Conversation turn ${index + 1} has an invalid role.`)
    }
    return {
      role: record.role,
      content: requireString(
        record.content,
        `Conversation turn ${index + 1} content`,
        100_000,
      ),
    }
  })
}

function parseChatRequest(value: unknown): BrainstemChatRequest {
  const record = requireRecord(value, 'Chat request')
  return {
    userInput: requireString(record.userInput, 'Chat message', 100_000),
    requestId: record.requestId
      ? requireString(record.requestId, 'Chat request id', 128)
      : undefined,
    sessionId: record.sessionId
      ? requireString(record.sessionId, 'Session id', 512)
      : undefined,
    conversationHistory: parseHistory(record.conversationHistory),
  }
}

function normalizeLogs(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .filter((entry): entry is string => typeof entry === 'string')
      .map((entry) => entry.trim())
      .filter(Boolean)
  }
  return typeof value === 'string' && value.trim() ? [value.trim()] : []
}

async function waitForExit(
  child: ChildProcess,
  timeoutMs: number,
): Promise<number | null> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill('SIGKILL')
      reject(new Error('Brainstem launcher timed out.'))
    }, timeoutMs)
    child.once('error', (error) => {
      clearTimeout(timer)
      reject(error)
    })
    child.once('exit', (code) => {
      clearTimeout(timer)
      resolve(code)
    })
  })
}

export async function waitForProcessExit(
  child: ChildProcess,
  timeoutMs: number,
): Promise<boolean> {
  if (child.exitCode !== null || child.signalCode !== null) return true
  return new Promise((resolve) => {
    const finish = () => {
      clearTimeout(timer)
      child.off('exit', finish)
      resolve(true)
    }
    const timer = setTimeout(() => {
      child.off('exit', finish)
      resolve(false)
    }, timeoutMs)
    child.once('exit', finish)
  })
}

export class BrainstemManager {
  private readonly baseUrl: string
  private readonly fetchImpl: typeof fetch
  private readonly options: BrainstemManagerOptions
  private readonly chatRequests = new Map<string, AbortController>()
  private ownedProcess: ChildProcess | null = null
  private starting: Promise<BrainstemStatus> | null = null
  private lastStatus: BrainstemStatus

  constructor(options: BrainstemManagerOptions) {
    this.options = options
    this.baseUrl = normalizeBaseUrl(
      options.baseUrl
        ?? process.env.RAPP_BRAINSTEM_URL
        ?? 'http://127.0.0.1:7071',
    )
    this.fetchImpl = options.fetch ?? fetch
    this.lastStatus = this.makeStatus({
      running: false,
      phase: 'checking',
      managed: false,
    })
  }

  currentStatus(): BrainstemStatus {
    return this.lastStatus
  }

  private makeStatus(
    fields: Pick<BrainstemStatus, 'running' | 'phase' | 'managed'>
      & Partial<BrainstemStatus>,
  ): BrainstemStatus {
    const url = new URL(this.baseUrl)
    return {
      running: fields.running,
      port: Number(url.port || (url.protocol === 'https:' ? 443 : 80)),
      endpoint: `${this.baseUrl}/chat`,
      managed: fields.managed,
      phase: fields.phase,
      detail: fields.detail,
      version: fields.version,
      model: fields.model,
      agentCount: fields.agentCount,
      authenticated: fields.authenticated,
    }
  }

  private emit(status: BrainstemStatus): BrainstemStatus {
    this.lastStatus = status
    this.options.onStatus(status)
    return status
  }

  private peerVerification(): Promise<PeerVerification> {
    const url = new URL(this.baseUrl)
    if (url.protocol === 'https:') {
      return Promise.resolve({ kind: 'trusted', proof: 'https' })
    }
    return (this.options.verifyPeer ?? inspectLoopbackPeer)(
      Number(url.port || 80),
      this.ownedProcess?.pid,
    )
  }

  private credentialHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    }
    if (this.options.credentialHeaders) {
      return {
        ...headers,
        ...this.options.credentialHeaders(),
      }
    }
    const loopback = isLoopback(new URL(this.baseUrl).hostname)
    const explicitSecret = process.env.RAPP_BRAINSTEM_SECRET
    const explicitSecretFile = process.env.BRAINSTEM_SECRET_FILE
    const secretPath = explicitSecretFile
      ?? (loopback
        ? path.join(
          os.homedir(),
          '.brainstem',
          'src',
          'rapp_brainstem',
          '.brainstem_secret',
        )
        : undefined)
    const secret = explicitSecret
      ?? (secretPath ? readPrivateSecret(secretPath) : '')
    if (secret) headers['X-Brainstem-Secret'] = secret
    if (loopback) {
      const desktopSecretPath = path.join(
        os.homedir(),
        '.rapp',
        'desktop_secret',
      )
      const desktopSecret = readPrivateSecret(desktopSecretPath)
      if (desktopSecret) {
        headers['X-RAPP-Desktop-Secret'] = desktopSecret
      }
    }
    return headers
  }

  private async authenticatedHeaders(
    signal?: AbortSignal,
  ): Promise<Record<string, string>> {
    signal?.throwIfAborted()
    const peer = await this.peerVerification()
    signal?.throwIfAborted()
    return useTrustedPeer(peer, () => this.credentialHeaders())
  }

  async status(): Promise<BrainstemStatus> {
    try {
      const headers = await this.authenticatedHeaders()
      const response = await this.fetchImpl(`${this.baseUrl}/health`, {
        headers,
        signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
      })
      const data = requireRecord(await response.json(), 'Brainstem health response')
      if (response.ok && data.status === 'unauthenticated') {
        const agents = Array.isArray(data.agents) ? data.agents : []
        return this.emit(this.makeStatus({
          running: true,
          phase: 'authentication-required',
          managed: this.ownedProcess !== null,
          authenticated: false,
          version: typeof data.version === 'string' ? data.version : undefined,
          model: typeof data.model === 'string' ? data.model : undefined,
          agentCount: agents.length,
          detail: data.auth_error === 'invalid_credentials'
            ? 'GitHub credentials need to be renewed.'
            : 'Sign in with GitHub to activate the Brainstem.',
        }))
      }
      if (!response.ok || data.status !== 'ok') {
        return this.emit(this.makeStatus({
          running: false,
          phase: 'error',
          managed: this.ownedProcess !== null,
          detail: typeof data.error === 'string'
            ? data.error
            : `Health check returned HTTP ${response.status}.`,
        }))
      }
      const agents = Array.isArray(data.agents) ? data.agents : []
      return this.emit(this.makeStatus({
        running: true,
        phase: 'ready',
        managed: this.ownedProcess !== null,
        version: typeof data.version === 'string' ? data.version : undefined,
        model: typeof data.model === 'string' ? data.model : undefined,
        agentCount: agents.length,
        authenticated: true,
      }))
    } catch (error) {
      return this.emit(this.makeStatus({
        running: error instanceof PeerIdentityError
          && error.peerKind === 'untrusted',
        phase: error instanceof PeerIdentityError
          && error.peerKind === 'untrusted'
          ? 'error'
          : 'stopped',
        managed: this.ownedProcess !== null,
        detail: message(error),
      }))
    }
  }

  start(): Promise<BrainstemStatus> {
    if (this.starting) return this.starting
    this.starting = this.startOnce()
      .catch((error) => {
        this.emit(this.makeStatus({
          running: false,
          phase: 'error',
          managed: this.ownedProcess !== null,
          detail: message(error),
        }))
        throw error
      })
      .finally(() => {
        this.starting = null
      })
    return this.starting
  }

  private async startOnce(): Promise<BrainstemStatus> {
    this.emit(this.makeStatus({
      running: false,
      phase: 'starting',
      managed: this.ownedProcess !== null,
    }))
    const current = await this.status()
    if (current.running) return current

    const target = new URL(this.baseUrl)
    if (!isLoopback(target.hostname)) {
      throw new Error('A remote Brainstem must be started by its host.')
    }

    const launcherResult = await this.tryGlobalLauncher()
    if (
      await waitAfterLauncher(
        launcherResult,
        () => this.waitForHealth(START_TIMEOUT_MS),
      )
    ) {
      return this.status()
    }

    await this.startLegacyFallback()
    if (!(await this.waitForHealth(START_TIMEOUT_MS))) {
      await this.stopOwnedProcess()
      const detail = launcherResult.kind === 'failed'
        ? `Global launcher failed (${launcherResult.error}); bundled fallback did not become healthy.`
        : 'Bundled Brainstem did not become healthy.'
      return this.emit(this.makeStatus({
        running: false,
        phase: 'error',
        managed: false,
        detail,
      }))
    }
    return this.status()
  }

  private launcherCandidates(): string[] {
    const candidates = [
      process.env.RAPP_BRAINSTEM_LAUNCHER,
      path.join(
        os.homedir(),
        '.copilot',
        'bin',
        process.platform === 'win32' ? 'brainstem.cmd' : 'brainstem',
      ),
      path.join(
        os.homedir(),
        '.brainstem',
        'src',
        'rapp_brainstem',
        'installer',
        process.platform === 'win32' ? 'brainstem.cmd' : 'brainstem',
      ),
    ]
    return candidates.filter((candidate): candidate is string =>
      Boolean(candidate && existsSync(candidate)))
  }

  private async tryGlobalLauncher(): Promise<LauncherResult> {
    const launcher = this.launcherCandidates()[0]
    if (!launcher) return { kind: 'not-found' }
    try {
      const child = process.platform === 'win32'
        ? spawn(
          process.env.ComSpec ?? 'cmd.exe',
          ['/d', '/s', '/c', launcher, 'start'],
          { windowsHide: true, stdio: 'ignore' },
        )
        : spawn(launcher, ['start'], {
          windowsHide: true,
          stdio: 'ignore',
        })
      const code = await waitForExit(child, 120_000)
      return code === 0
        ? { kind: 'launched' }
        : { kind: 'failed', error: `exit code ${code}` }
    } catch (error) {
      return { kind: 'failed', error: message(error) }
    }
  }

  private pythonCandidates(): string[] {
    return process.platform === 'win32'
      ? [
        path.join(os.homedir(), '.rapp', 'venv', 'Scripts', 'python.exe'),
        'python',
      ]
      : [
        path.join(os.homedir(), '.rapp', 'venv', 'bin', 'python'),
        'python3',
        'python',
      ]
  }

  private async startLegacyFallback(): Promise<void> {
    if (!existsSync(this.options.legacyScriptPath)) {
      throw new Error('No global or bundled Brainstem installation is available.')
    }
    let lastError = 'Python is unavailable.'
    for (const python of this.pythonCandidates()) {
      if (path.isAbsolute(python) && !existsSync(python)) continue
      try {
        const child = spawn(
          python,
          [
            this.options.legacyScriptPath,
            '--port',
            String(new URL(this.baseUrl).port || '7071'),
          ],
          {
            detached: process.platform !== 'win32',
            env: { ...process.env, PYTHONUNBUFFERED: '1' },
            stdio: 'ignore',
            windowsHide: true,
          },
        )
        await new Promise<void>((resolve, reject) => {
          child.once('spawn', resolve)
          child.once('error', reject)
        })
        this.ownedProcess = child
        child.once('exit', () => {
          if (this.ownedProcess === child) {
            this.ownedProcess = null
            void this.status()
          }
        })
        return
      } catch (error) {
        lastError = message(error)
      }
    }
    throw new Error(`Unable to start the bundled Brainstem: ${lastError}`)
  }

  private async waitForHealth(timeoutMs: number): Promise<boolean> {
    const deadline = Date.now() + timeoutMs
    while (Date.now() < deadline) {
      try {
        const headers = await this.authenticatedHeaders()
        const response = await this.fetchImpl(`${this.baseUrl}/health`, {
          headers,
          signal: AbortSignal.timeout(2_000),
        })
        if (response.ok) return true
      } catch {
        // A bounded health loop reports one final error at its caller.
      }
      await new Promise((resolve) => setTimeout(resolve, 750))
    }
    return false
  }

  async stop(): Promise<BrainstemStatus> {
    if (!this.ownedProcess) {
      const current = await this.status()
      if (current.running) {
        return this.emit({
          ...current,
          detail: 'This global Brainstem is shared and remains running.',
        })
      }
      return current
    }
    await this.stopOwnedProcess()
    return this.emit(this.makeStatus({
      running: false,
      phase: 'stopped',
      managed: false,
    }))
  }

  private async stopOwnedProcess(): Promise<void> {
    const child = this.ownedProcess
    if (!child?.pid) return
    if (process.platform === 'win32') {
      const killer = spawn(
        'taskkill.exe',
        ['/pid', String(child.pid), '/t'],
        { windowsHide: true, stdio: 'ignore' },
      )
      await waitForExit(killer, 10_000).catch(() => undefined)
    } else {
      try {
        process.kill(-child.pid, 'SIGTERM')
      } catch {
        child.kill('SIGTERM')
      }
    }
    if (!(await waitForProcessExit(child, 5_000))) {
      if (process.platform === 'win32') {
        const killer = spawn(
          'taskkill.exe',
          ['/pid', String(child.pid), '/t', '/f'],
          { windowsHide: true, stdio: 'ignore' },
        )
        await waitForExit(killer, 10_000).catch(() => undefined)
      } else {
        try {
          process.kill(-child.pid, 'SIGKILL')
        } catch {
          child.kill('SIGKILL')
        }
      }
      if (!(await waitForProcessExit(child, 5_000))) {
        throw new Error('Bundled Brainstem did not stop.')
      }
    }
    if (this.ownedProcess === child) this.ownedProcess = null
  }

  async chat(value: unknown): Promise<BrainstemChatResponse> {
    const request = parseChatRequest(value)
    const requestId = request.requestId
      ?? `internal-${Date.now()}-${Math.random().toString(16).slice(2)}`
    if (this.chatRequests.has(requestId)) {
      throw new Error('A chat request with this id is already active.')
    }
    const controller = new AbortController()
    this.chatRequests.set(requestId, controller)
    try {
      return await this.performChat(request, requestId, controller.signal)
    } finally {
      if (this.chatRequests.get(requestId) === controller) {
        this.chatRequests.delete(requestId)
      }
    }
  }

  private async performChat(
    request: BrainstemChatRequest,
    requestId: string,
    signal: AbortSignal,
  ): Promise<BrainstemChatResponse> {
    const body = {
      request_id: requestId,
      user_input: request.userInput,
      session_id: request.sessionId ?? '',
      conversation_history: request.conversationHistory ?? [],
    }
    let response = await this.post('/chat', body, signal)
    if (response.status === 404) {
      response = await this.post('/api/rapp', {
        ...body,
        user_guid: 'desktop',
        session_guid: request.sessionId ?? '',
        context_guid: 'default',
      }, signal)
    }
    const data = requireRecord(await response.json(), 'Brainstem chat response')
    if (!response.ok || data.error) {
      throw new Error(
        typeof data.error === 'string'
          ? data.error
          : `Brainstem returned HTTP ${response.status}.`,
      )
    }
    return {
      response: typeof data.response === 'string' ? data.response : '',
      agentLogs: normalizeLogs(data.agent_logs),
      agentsUsed: normalizeLogs(data.agents_used),
      sessionId: typeof data.session_id === 'string'
        ? data.session_id
        : typeof data.session_guid === 'string'
          ? data.session_guid
          : request.sessionId ?? '',
      contextId: typeof data.context_guid === 'string'
        ? data.context_guid
        : 'default',
    }
  }

  async cancelChat(value: unknown): Promise<void> {
    const requestId = requireString(value, 'Chat request id', 128)
    const controller = this.chatRequests.get(requestId)
    if (!controller) return
    controller.abort(
      new Error('Chat request was cancelled.'),
    )
    const managed = this.ownedProcess !== null
    const response = await this.post(
      '/cancel',
      { request_id: requestId },
      undefined,
      CANCEL_TIMEOUT_MS,
    )
    if ([404, 405, 501].includes(response.status)) {
      if (!managed) return
      throw new Error(
        'The bundled Brainstem does not support request cancellation.',
      )
    }
    const data = requireRecord(
      await response.json(),
      'Brainstem cancellation response',
    )
    if (!response.ok) {
      throw new Error(
        typeof data.error === 'string'
          ? data.error
          : `Brainstem cancellation returned HTTP ${response.status}.`,
      )
    }
    const acknowledged = data.cancelled === true
      || data.status === 'not_found'
    if (!acknowledged || (managed && data.worker_ended !== true)) {
      throw new Error('Brainstem did not acknowledge request cancellation.')
    }
  }

  private async post(
    pathname: string,
    body: object,
    signal?: AbortSignal,
    timeoutMs = CHAT_TIMEOUT_MS,
  ): Promise<Response> {
    const requestSignal = signal
      ? AbortSignal.any([signal, AbortSignal.timeout(timeoutMs)])
      : AbortSignal.timeout(timeoutMs)
    const headers = await this.authenticatedHeaders(requestSignal)
    requestSignal.throwIfAborted()
    return this.fetchImpl(`${this.baseUrl}${pathname}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: requestSignal,
    })
  }

  async login(): Promise<BrainstemLogin> {
    const response = await this.post('/login', {})
    const data = requireRecord(await response.json(), 'Brainstem login response')
    if (!response.ok || data.error) {
      throw new Error(
        typeof data.error === 'string'
          ? data.error
          : `Brainstem login returned HTTP ${response.status}.`,
      )
    }
    return {
      userCode: requireString(data.user_code, 'GitHub device code', 64),
      verificationUrl: requireString(
        data.verification_uri,
        'GitHub verification URL',
        2048,
      ),
    }
  }

  async pollLogin(): Promise<BrainstemStatus> {
    const response = await this.post('/login/poll', {})
    const data = requireRecord(
      await response.json(),
      'Brainstem login poll response',
    )
    if (!response.ok) {
      throw new Error(
        typeof data.error === 'string'
          ? data.error
          : `Brainstem login poll returned HTTP ${response.status}.`,
      )
    }
    if (
      data.status === 'expired'
      || data.status === 'error'
      || typeof data.error === 'string'
    ) {
      return this.emit(this.makeStatus({
        running: true,
        phase: 'authentication-failed',
        managed: this.ownedProcess !== null,
        authenticated: false,
        detail: typeof data.error === 'string'
          ? data.error
          : `GitHub authorization ${String(data.status)}.`,
      }))
    }
    if (data.status === 'ok' || data.status === 'success') {
      return this.status()
    }
    return this.emit(this.makeStatus({
      running: true,
      phase: 'authentication-required',
      managed: this.ownedProcess !== null,
      authenticated: false,
      detail: 'Waiting for GitHub authorization.',
    }))
  }

  async dispose(): Promise<void> {
    const activeRequestIds = [...this.chatRequests.keys()]
    await Promise.allSettled(
      activeRequestIds.map((requestId) => this.cancelChat(requestId)),
    )
    this.chatRequests.clear()
    await this.stopOwnedProcess()
  }
}
