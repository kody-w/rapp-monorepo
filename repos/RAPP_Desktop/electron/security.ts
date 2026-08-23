import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const SECURE_RENDERER_PREFERENCES = Object.freeze({
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: true,
  webSecurity: true,
})

export const EXPECTED_DEVELOPMENT_ORIGIN = 'http://127.0.0.1:5173'

export type RendererTarget =
  | { kind: 'development'; url: string; origin: string }
  | { kind: 'file'; path: string }

export interface RendererTargetOptions {
  isPackaged: boolean
  developmentUrl?: string
  rendererIndex: string
}

export interface ListenerProcess {
  pid: number
  ownerId: string
}

export type PeerVerification =
  | {
    kind: 'trusted'
    proof: 'https' | 'managed-process' | 'user-owned-process'
    pid?: number
  }
  | { kind: 'missing'; detail: string }
  | { kind: 'untrusted'; detail: string }

export type LauncherResult =
  | { kind: 'launched' }
  | { kind: 'not-found' }
  | { kind: 'failed'; error: string }

export class PeerIdentityError extends Error {
  readonly peerKind: 'missing' | 'untrusted'

  constructor(peer: Extract<PeerVerification, { kind: 'missing' | 'untrusted' }>) {
    super(peer.detail)
    this.name = 'PeerIdentityError'
    this.peerKind = peer.kind
  }
}

function isPathInside(root: string, target: string): boolean {
  const relative = path.relative(path.resolve(root), path.resolve(target))
  return relative === ''
    || (!relative.startsWith('..') && !path.isAbsolute(relative))
}

export function resolveRendererTarget(
  options: RendererTargetOptions,
): RendererTarget {
  if (options.isPackaged || !options.developmentUrl) {
    return { kind: 'file', path: options.rendererIndex }
  }

  let url: URL
  try {
    url = new URL(options.developmentUrl)
  } catch {
    throw new TypeError('The development renderer URL is invalid.')
  }
  if (
    url.origin !== EXPECTED_DEVELOPMENT_ORIGIN
    || url.username
    || url.password
    || url.pathname !== '/'
    || url.search
    || url.hash
  ) {
    throw new TypeError(
      `The development renderer must be ${EXPECTED_DEVELOPMENT_ORIGIN}.`,
    )
  }
  return {
    kind: 'development',
    url: `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
    origin: EXPECTED_DEVELOPMENT_ORIGIN,
  }
}

export function isTrustedRendererUrl(
  rawUrl: string,
  target: RendererTarget,
  rendererDirectory: string,
): boolean {
  try {
    const url = new URL(rawUrl)
    if (target.kind === 'development') {
      return target.origin === EXPECTED_DEVELOPMENT_ORIGIN
        && url.protocol === 'http:'
        && url.origin === EXPECTED_DEVELOPMENT_ORIGIN
    }
    return url.protocol === 'file:'
      && isPathInside(rendererDirectory, fileURLToPath(url))
  } catch {
    return false
  }
}

export function parseLsofListeners(output: string): ListenerProcess[] {
  const listeners: ListenerProcess[] = []
  let pid: number | undefined
  let ownerId = ''
  const flush = () => {
    if (pid !== undefined) listeners.push({ pid, ownerId })
  }
  for (const line of output.split(/\r?\n/)) {
    if (line.startsWith('p')) {
      flush()
      const parsed = Number(line.slice(1))
      pid = Number.isSafeInteger(parsed) && parsed > 0 ? parsed : undefined
      ownerId = ''
    } else if (line.startsWith('u') && pid !== undefined) {
      ownerId = line.slice(1).trim()
    }
  }
  flush()
  return listeners
}

export function assessLoopbackPeer(
  listeners: readonly ListenerProcess[],
  currentOwnerIds: readonly string[],
  managedPid?: number,
): PeerVerification {
  const unique = new Map<number, ListenerProcess>()
  for (const listener of listeners) unique.set(listener.pid, listener)
  if (unique.size === 0) {
    return {
      kind: 'missing',
      detail: 'No process is listening at the configured Brainstem endpoint.',
    }
  }
  if (unique.size !== 1) {
    return {
      kind: 'untrusted',
      detail: 'Multiple processes own the configured Brainstem endpoint.',
    }
  }

  const listener = [...unique.values()][0]
  if (managedPid !== undefined) {
    return listener.pid === managedPid
      ? { kind: 'trusted', proof: 'managed-process', pid: listener.pid }
      : {
        kind: 'untrusted',
        detail: 'The Brainstem endpoint is not owned by the bundled process.',
      }
  }

  const owners = new Set(
    currentOwnerIds.map((owner) => owner.trim().toLowerCase()).filter(Boolean),
  )
  if (!listener.ownerId || !owners.has(listener.ownerId.trim().toLowerCase())) {
    return {
      kind: 'untrusted',
      detail: 'The Brainstem endpoint is not owned by the current OS user.',
    }
  }
  return {
    kind: 'trusted',
    proof: 'user-owned-process',
    pid: listener.pid,
  }
}

export function useTrustedPeer<T>(
  peer: PeerVerification,
  sensitiveOperation: () => T,
): T {
  if (peer.kind !== 'trusted') throw new PeerIdentityError(peer)
  return sensitiveOperation()
}

export async function waitAfterLauncher(
  result: LauncherResult,
  waitForHealth: () => Promise<boolean>,
): Promise<boolean> {
  return result.kind === 'launched' ? waitForHealth() : false
}

export function requireRecord(
  value: unknown,
  label: string,
): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new TypeError(`${label} must be an object.`)
  }
  return value as Record<string, unknown>
}

export function requireString(
  value: unknown,
  label: string,
  maximumLength = 512,
): string {
  if (typeof value !== 'string') {
    throw new TypeError(`${label} must be a string.`)
  }
  const normalized = value.trim()
  if (!normalized || normalized.length > maximumLength || /[\0\r\n]/.test(normalized)) {
    throw new TypeError(`${label} is invalid.`)
  }
  return normalized
}

export function requireProjectName(value: unknown): string {
  const name = requireString(value, 'Project name', 64)
  if (
    name === '.'
    || name === '..'
    || !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(name)
  ) {
    throw new TypeError(
      'Project name may contain letters, numbers, dots, underscores, and hyphens.',
    )
  }
  return name
}

export function requireSafeRelativePath(
  value: unknown,
  label: string,
): string {
  const relative = requireString(value, label, 512).replaceAll('\\', '/')
  if (
    relative.startsWith('/')
    || relative.split('/').some((segment) => !segment || segment === '.' || segment === '..')
    || !/^[A-Za-z0-9@._/-]+$/.test(relative)
  ) {
    throw new TypeError(`${label} must be a safe relative path.`)
  }
  return relative
}

export function resolveInside(root: string, relative: string): string {
  const resolvedRoot = path.resolve(root)
  const resolved = path.resolve(resolvedRoot, relative)
  if (resolved !== resolvedRoot && !resolved.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new TypeError('Resolved path escapes its allowed directory.')
  }
  return resolved
}

export function requireGitHubRepository(value: unknown): string {
  const raw = requireString(value, 'Repository URL', 1024)
  let url: URL
  try {
    url = new URL(raw)
  } catch {
    throw new TypeError('Repository URL is invalid.')
  }
  const parts = url.pathname.split('/').filter(Boolean)
  if (
    url.protocol !== 'https:'
    || url.hostname !== 'github.com'
    || url.username
    || url.password
    || url.search
    || url.hash
    || parts.length !== 2
  ) {
    throw new TypeError('Only canonical HTTPS GitHub repository URLs are allowed.')
  }
  return url.toString()
}

export function requireExternalUrl(value: unknown): string {
  const raw = requireString(value, 'External URL', 2048)
  let url: URL
  try {
    url = new URL(raw)
  } catch {
    throw new TypeError('External URL is invalid.')
  }
  if (url.protocol !== 'https:' || url.username || url.password) {
    throw new TypeError('Only credential-free HTTPS links can be opened.')
  }
  return url.toString()
}
