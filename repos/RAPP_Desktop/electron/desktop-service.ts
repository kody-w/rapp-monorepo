import { spawn, type ChildProcess } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import {
  access,
  mkdir,
  readdir,
  rename,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

import type {
  CatalogAgent,
  CatalogImplementation,
  CatalogSkill,
  HubManifest,
  InstallResult,
  ProjectInfo,
  StoreManifest,
} from '../src/desktop-api.js'
import {
  requireGitHubRepository,
  requireProjectName,
  requireRecord,
  requireSafeRelativePath,
  requireString,
  resolveInside,
} from './security.js'

const STORE_MANIFEST =
  'https://raw.githubusercontent.com/kody-w/RAPP_Store/main/index.json'
const HUB_MANIFEST =
  'https://raw.githubusercontent.com/kody-w/RAPP_Hub/main/manifest.json'
const MAX_MANIFEST_BYTES = 2 * 1024 * 1024
const MAX_PACKAGE_BYTES = 5 * 1024 * 1024
const DEFAULT_AVAILABILITY_CACHE_TTL_MS = 5 * 60_000
const MAX_AVAILABILITY_CACHE_TTL_MS = 15 * 60_000

type FetchImplementation = typeof fetch
type CommandResult = { code: number; stderr: string }
type CommandRunner = (
  command: string,
  args: string[],
  timeoutMs?: number,
) => Promise<CommandResult>

interface InstallableSkill extends CatalogSkill {
  downloadUrl: string
  sha256: string
}

interface StoreCatalog {
  manifest: StoreManifest
  installableSkills: InstallableSkill[]
}

export interface DesktopServiceOptions {
  fetch?: FetchImplementation
  rappHome?: string
  runCommand?: CommandRunner
  availabilityCacheTtlMs?: number
  now?: () => number
}

function optionalString(value: unknown, label: string): string | undefined {
  return value === undefined || value === null || value === ''
    ? undefined
    : requireString(value, label)
}

function stringArray(value: unknown): string[] | undefined {
  if (value === undefined || value === null) return undefined
  if (!Array.isArray(value)) throw new TypeError('Features must be an array.')
  return value.map((entry, index) => requireString(entry, `Feature ${index + 1}`, 128))
}

function requireSha256(value: unknown, label: string): string {
  const digest = requireString(value, label, 64).toLowerCase()
  if (!/^[0-9a-f]{64}$/.test(digest)) {
    throw new TypeError(`${label} must be a SHA-256 digest.`)
  }
  return digest
}

function requireRawGitHubUrl(value: unknown, label: string): string {
  const raw = requireString(value, label, 2048)
  let url: URL
  try {
    url = new URL(raw)
  } catch {
    throw new TypeError(`${label} is invalid.`)
  }
  if (
    url.protocol !== 'https:'
    || url.hostname !== 'raw.githubusercontent.com'
    || url.username
    || url.password
    || url.search
    || url.hash
    || url.pathname.split('/').filter(Boolean).length < 4
  ) {
    throw new TypeError(`${label} must be a canonical raw GitHub URL.`)
  }
  return url.toString()
}

function parseAgent(value: unknown): CatalogAgent {
  const record = requireRecord(value, 'Rapplication')
  return {
    id: requireString(record.id, 'Rapplication id', 256),
    name: requireString(record.name, 'Rapplication name', 256),
    description: requireString(
      record.summary ?? record.tagline,
      'Rapplication summary',
      4096,
    ),
    version: requireString(record.version, 'Rapplication version', 64),
    filename: requireSafeRelativePath(
      record.singleton_filename,
      'Singleton filename',
    ),
    downloadUrl: requireRawGitHubUrl(
      record.singleton_url,
      'Singleton URL',
    ),
    sha256: requireSha256(record.singleton_sha256, 'Singleton SHA-256'),
    features: stringArray(record.tags),
  }
}

function parseSkillProjection(record: Record<string, unknown>): InstallableSkill {
  const downloadUrl = requireRawGitHubUrl(record.skill_url, 'Skill URL')
  const url = new URL(downloadUrl)
  const parts = url.pathname.split('/').filter(Boolean)
  if (parts.at(-1) !== 'SKILL.md' || parts.length < 5) {
    throw new TypeError('Skill URL must identify a SKILL.md in a GitHub repository.')
  }
  return {
    id: requireSafeRelativePath(record.id, 'Skill id'),
    name: requireString(record.name, 'Skill name', 256),
    description: requireString(
      record.summary ?? record.tagline,
      'Skill description',
      4096,
    ),
    version: requireString(record.version, 'Skill version', 64),
    icon: optionalString(record.icon, 'Skill icon'),
    path: requireSafeRelativePath(parts.slice(3, -1).join('/'), 'Skill path'),
    features: stringArray(record.tags),
    downloadUrl,
    sha256: requireSha256(record.skill_sha256, 'Skill SHA-256'),
  }
}

function parseImplementation(value: unknown): CatalogImplementation {
  const record = requireRecord(value, 'Implementation')
  return {
    id: requireProjectName(record.id),
    name: requireString(record.name, 'Implementation name', 256),
    description: requireString(record.description, 'Implementation description', 4096),
    version: requireString(record.version, 'Implementation version', 64),
    icon: optionalString(record.icon, 'Implementation icon'),
    repo: requireGitHubRepository(record.repo),
    path: requireSafeRelativePath(record.path, 'Implementation path'),
    branch: requireGitRef(record.branch ?? 'main'),
    features: stringArray(record.features),
  }
}

function requireGitRef(value: unknown): string {
  const ref = requireString(value, 'Git branch', 256)
  if (
    ref.startsWith('-')
    || ref.startsWith('/')
    || ref.endsWith('/')
    || ref.includes('..')
    || ref.includes('@{')
    || ref.includes('\\')
    || !/^[A-Za-z0-9._/-]+$/.test(ref)
  ) {
    throw new TypeError('Git branch is invalid.')
  }
  return ref
}

function publicRapplications(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    throw new Error('Store catalog does not satisfy rapp-store/1.0.')
  }
  const visible: Record<string, unknown>[] = []
  value.forEach((entry, index) => {
    const record = requireRecord(entry, `Rapplication ${index + 1}`)
    const access = optionalString(record.access, 'Rapplication access')
    if (access === 'private') return
    if (access !== undefined && access !== 'public') {
      throw new TypeError('Rapplication access must be public or private.')
    }
    visible.push(record)
  })
  return visible
}

function parseStoreCatalog(value: unknown): StoreCatalog {
  const record = requireRecord(value, 'Store manifest')
  if (record.schema !== 'rapp-store/1.0') {
    throw new Error('Store catalog does not satisfy rapp-store/1.0.')
  }
  const rapplications = publicRapplications(record.rapplications)
  const installableSkills = rapplications
    .filter((entry) => entry.skill_url !== undefined && entry.skill_url !== null)
    .map(parseSkillProjection)
  return {
    manifest: {
      agents: rapplications.map(parseAgent),
      skills: installableSkills.map((skill) => ({
        id: skill.id,
        name: skill.name,
        description: skill.description,
        version: skill.version,
        icon: skill.icon,
        path: skill.path,
        features: skill.features,
      })),
    },
    installableSkills,
  }
}

export function parseStoreManifestDocument(value: unknown): StoreManifest {
  return parseStoreCatalog(value).manifest
}

export function parseHubManifestDocument(value: unknown): HubManifest {
  const record = requireRecord(value, 'Hub manifest')
  if (!Array.isArray(record.implementations)) {
    throw new Error('Hub manifest is missing implementations.')
  }
  return { implementations: record.implementations.map(parseImplementation) }
}

async function fetchBytes(
  url: string,
  maximumBytes: number,
  fetchImplementation: FetchImplementation,
  accept = 'application/json, text/plain;q=0.9',
): Promise<Buffer> {
  const response = await fetchImplementation(url, {
    headers: { Accept: accept },
    redirect: 'error',
    signal: AbortSignal.timeout(15_000),
  })
  if (!response.ok) {
    throw new Error(`Request failed with HTTP ${response.status}.`)
  }
  const contentLength = Number(response.headers.get('content-length') ?? '0')
  if (contentLength > maximumBytes) {
    throw new Error('Remote content exceeds the allowed size.')
  }
  const content = Buffer.from(await response.arrayBuffer())
  if (content.byteLength > maximumBytes) {
    throw new Error('Remote content exceeds the allowed size.')
  }
  return content
}

async function fetchText(
  url: string,
  maximumBytes: number,
  fetchImplementation: FetchImplementation,
): Promise<string> {
  return (await fetchBytes(url, maximumBytes, fetchImplementation)).toString('utf8')
}

async function fetchJson(
  url: string,
  fetchImplementation: FetchImplementation,
): Promise<unknown> {
  const text = await fetchText(url, MAX_MANIFEST_BYTES, fetchImplementation)
  try {
    return JSON.parse(text)
  } catch {
    throw new Error('Remote manifest is not valid JSON.')
  }
}

function boundedAvailabilityCacheTtl(value: number | undefined): number {
  if (value === undefined) return DEFAULT_AVAILABILITY_CACHE_TTL_MS
  if (!Number.isFinite(value) || value <= 0) {
    throw new TypeError('Availability cache TTL must be a positive finite number.')
  }
  return Math.min(Math.floor(value), MAX_AVAILABILITY_CACHE_TTL_MS)
}

function implementationAvailabilityUrl(
  implementation: CatalogImplementation,
): string {
  const repository = new URL(implementation.repo)
  const [owner, name] = repository.pathname.split('/').filter(Boolean)
  const selectedPath = implementation.path
    .split('/')
    .map((segment) => encodeURIComponent(segment))
    .join('/')
  return (
    `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(name)}`
    + `/contents/${selectedPath}?ref=${encodeURIComponent(implementation.branch)}`
  )
}

async function implementationDirectoryIsPublic(
  availabilityUrl: string,
  fetchImplementation: FetchImplementation,
): Promise<boolean> {
  const response = await fetchImplementation(availabilityUrl, {
    headers: { Accept: 'application/vnd.github+json' },
    redirect: 'error',
    signal: AbortSignal.timeout(15_000),
  })
  if (response.status === 404) return false
  if (!response.ok) {
    throw new Error(`Request failed with HTTP ${response.status}.`)
  }
  const contentLength = Number(response.headers.get('content-length') ?? '0')
  if (contentLength > MAX_MANIFEST_BYTES) {
    throw new Error('Remote content exceeds the allowed size.')
  }
  const content = Buffer.from(await response.arrayBuffer())
  if (content.byteLength > MAX_MANIFEST_BYTES) {
    throw new Error('Remote content exceeds the allowed size.')
  }
  try {
    return Array.isArray(JSON.parse(content.toString('utf8')))
  } catch {
    throw new Error('GitHub availability response is not valid JSON.')
  }
}

async function pathExists(target: string): Promise<boolean> {
  try {
    await access(target)
    return true
  } catch {
    return false
  }
}

async function atomicWrite(
  target: string,
  content: string | Uint8Array,
): Promise<void> {
  const temporary = `${target}.${process.pid}.${randomUUID()}.tmp`
  await writeFile(temporary, content, { flag: 'wx', mode: 0o600 })
  try {
    await rename(temporary, target)
  } finally {
    await rm(temporary, { force: true })
  }
}

async function terminateProcessTree(child: ChildProcess): Promise<void> {
  if (child.pid === undefined) return
  if (process.platform !== 'win32') {
    try {
      process.kill(-child.pid, 'SIGKILL')
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ESRCH') throw error
    }
    return
  }

  await new Promise<void>((resolve) => {
    const terminator = spawn(
      'taskkill',
      ['/pid', String(child.pid), '/T', '/F'],
      { shell: false, windowsHide: true, stdio: 'ignore' },
    )
    terminator.once('error', () => {
      child.kill('SIGKILL')
      resolve()
    })
    terminator.once('close', () => resolve())
  })
}

export async function runCommand(
  command: string,
  args: string[],
  timeoutMs = 120_000,
): Promise<CommandResult> {
  const child = spawn(command, args, {
    detached: process.platform !== 'win32',
    shell: false,
    windowsHide: true,
    stdio: ['ignore', 'ignore', 'pipe'],
  })
  let stderr = ''
  child.stderr?.on('data', (chunk: Buffer) => {
    stderr = `${stderr}${chunk.toString()}`.slice(-16_384)
  })

  const completion = new Promise<CommandResult>((resolve, reject) => {
    child.once('error', reject)
    child.once('close', (code) => {
      resolve({ code: code ?? -1, stderr: stderr.trim() })
    })
  })

  let timer: NodeJS.Timeout | undefined
  const timeout = new Promise<'timeout'>((resolve) => {
    timer = setTimeout(() => resolve('timeout'), timeoutMs)
  })

  try {
    const outcome = await Promise.race([
      completion.then((result) => ({ kind: 'complete' as const, result })),
      timeout.then(() => ({ kind: 'timeout' as const })),
    ])
    if (outcome.kind === 'complete') return outcome.result

    await terminateProcessTree(child)
    await completion.catch(() => undefined)
    throw new Error(`${command} timed out.`)
  } finally {
    if (timer !== undefined) clearTimeout(timer)
  }
}

export class DesktopService {
  readonly rappHome: string
  readonly agentsDirectory: string
  readonly skillsDirectory: string
  readonly projectsDirectory: string
  readonly stagingDirectory: string
  private readonly fetchImplementation: FetchImplementation
  private readonly commandRunner: CommandRunner
  private readonly availabilityCacheTtlMs: number
  private readonly now: () => number
  private readonly availabilityCache = new Map<
    string,
    { available: boolean; expiresAt: number }
  >()
  private readonly availabilityRequests = new Map<string, Promise<boolean>>()

  constructor(options: DesktopServiceOptions = {}) {
    this.rappHome = options.rappHome ?? path.join(os.homedir(), '.rapp')
    this.agentsDirectory = path.join(this.rappHome, 'agents')
    this.skillsDirectory = path.join(this.rappHome, 'skills')
    this.projectsDirectory = path.join(this.rappHome, 'projects')
    this.stagingDirectory = path.join(this.rappHome, '.staging')
    this.fetchImplementation = options.fetch ?? fetch
    this.commandRunner = options.runCommand ?? runCommand
    this.availabilityCacheTtlMs = boundedAvailabilityCacheTtl(
      options.availabilityCacheTtlMs,
    )
    this.now = options.now ?? Date.now
  }

  private implementationIsAvailable(
    implementation: CatalogImplementation,
  ): Promise<boolean> {
    const key = implementationAvailabilityUrl(implementation)
    const cached = this.availabilityCache.get(key)
    if (cached && cached.expiresAt > this.now()) {
      return Promise.resolve(cached.available)
    }
    if (cached) this.availabilityCache.delete(key)

    const pending = this.availabilityRequests.get(key)
    if (pending) return pending

    const request = implementationDirectoryIsPublic(
      key,
      this.fetchImplementation,
    ).then((available) => {
      this.availabilityCache.set(key, {
        available,
        expiresAt: this.now() + this.availabilityCacheTtlMs,
      })
      return available
    }).finally(() => {
      if (this.availabilityRequests.get(key) === request) {
        this.availabilityRequests.delete(key)
      }
    })
    this.availabilityRequests.set(key, request)
    return request
  }

  async initialize(): Promise<void> {
    await Promise.all([
      mkdir(this.agentsDirectory, { recursive: true, mode: 0o700 }),
      mkdir(this.skillsDirectory, { recursive: true, mode: 0o700 }),
      mkdir(this.projectsDirectory, { recursive: true, mode: 0o700 }),
      mkdir(this.stagingDirectory, { recursive: true, mode: 0o700 }),
      mkdir(path.join(this.rappHome, 'contexts'), { recursive: true, mode: 0o700 }),
      mkdir(path.join(this.rappHome, 'memory'), { recursive: true, mode: 0o700 }),
    ])
  }

  async storeManifest(): Promise<StoreManifest> {
    return parseStoreManifestDocument(
      await fetchJson(STORE_MANIFEST, this.fetchImplementation),
    )
  }

  async hubManifest(): Promise<HubManifest> {
    const manifest = parseHubManifestDocument(
      await fetchJson(HUB_MANIFEST, this.fetchImplementation),
    )
    const availability = await Promise.all(manifest.implementations.map(
      (implementation) => this.implementationIsAvailable(implementation),
    ))
    return {
      implementations: manifest.implementations.filter(
        (_implementation, index) => availability[index],
      ),
    }
  }

  async installAgent(value: unknown): Promise<InstallResult> {
    const agentId = requireString(value, 'Rapplication id', 256)
    const manifest = await this.storeManifest()
    const agent = manifest.agents.find((candidate) => candidate.id === agentId)
    if (!agent) throw new Error(`Rapplication ${agentId} is not in the current Store catalog.`)
    if (path.basename(agent.filename) !== agent.filename) {
      throw new TypeError('Agent filename cannot contain directories.')
    }
    const content = await fetchBytes(
      agent.downloadUrl,
      MAX_PACKAGE_BYTES,
      this.fetchImplementation,
    )
    const digest = createHash('sha256').update(content).digest('hex')
    if (digest !== agent.sha256) {
      throw new Error(`Integrity check failed for ${agent.name}.`)
    }
    const target = resolveInside(this.agentsDirectory, agent.filename)
    await atomicWrite(target, content)
    return { success: true, message: `Installed ${agent.name}`, path: target }
  }

  async installSkill(value: unknown): Promise<InstallResult> {
    const input = typeof value === 'string'
      ? value
      : requireRecord(value, 'Skill').id
    const skillId = requireSafeRelativePath(input, 'Skill id')
    const catalog = parseStoreCatalog(
      await fetchJson(STORE_MANIFEST, this.fetchImplementation),
    )
    const skill = catalog.installableSkills.find((candidate) => candidate.id === skillId)
    if (!skill) throw new Error(`Skill ${skillId} is not in the current Store catalog.`)
    const content = await fetchBytes(
      skill.downloadUrl,
      MAX_PACKAGE_BYTES,
      this.fetchImplementation,
    )
    const digest = createHash('sha256').update(content).digest('hex')
    if (digest !== skill.sha256) {
      throw new Error(`Integrity check failed for ${skill.name}.`)
    }
    const directory = resolveInside(this.skillsDirectory, skill.id)
    await mkdir(directory, { recursive: true, mode: 0o700 })
    const target = resolveInside(directory, 'SKILL.md')
    await atomicWrite(target, content)
    return { success: true, message: `Installed ${skill.name}`, path: directory }
  }

  async listProjects(): Promise<ProjectInfo[]> {
    await this.initialize()
    const entries = await readdir(this.projectsDirectory, { withFileTypes: true })
    const projects = await Promise.all(entries
      .filter((entry) => entry.isDirectory())
      .map(async (entry) => {
        const projectPath = resolveInside(this.projectsDirectory, entry.name)
        const projectStat = await stat(projectPath)
        return {
          name: entry.name,
          path: projectPath,
          created: projectStat.birthtime.toISOString(),
        }
      }))
    return projects.sort((left, right) => left.name.localeCompare(right.name))
  }

  async createProject(value: unknown): Promise<InstallResult> {
    const name = requireProjectName(value)
    const target = resolveInside(this.projectsDirectory, name)
    if (await pathExists(target)) {
      return { success: false, message: 'Already exists' }
    }
    const staging = resolveInside(
      this.stagingDirectory,
      `project-${name}-${randomUUID()}`,
    )
    try {
      await mkdir(staging, { recursive: false, mode: 0o700 })
      await mkdir(path.join(staging, 'agents'), { mode: 0o700 })
      await atomicWrite(
        path.join(staging, 'rapp.json'),
        `${JSON.stringify({
          name,
          version: '1.0.0',
          dependencies: { rapp_store: { agents: [], skills: [] } },
        }, null, 2)}\n`,
      )
      await atomicWrite(
        path.join(staging, 'main.py'),
        "#!/usr/bin/env python3\nprint('Hello from RAPP!')\n",
      )
      await rename(staging, target)
    } catch (error) {
      await rm(staging, { recursive: true, force: true })
      if (
        error
        && typeof error === 'object'
        && 'code' in error
        && (error.code === 'EEXIST' || error.code === 'ENOTEMPTY')
      ) {
        return { success: false, message: 'Already exists' }
      }
      throw error
    }

    return { success: true, message: `Created ${name}`, path: target }
  }

  async cloneImplementation(value: unknown): Promise<InstallResult> {
    const input = typeof value === 'string'
      ? value
      : requireRecord(value, 'Implementation').id
    const implementationId = requireProjectName(input)
    const manifest = await this.hubManifest()
    const implementation = manifest.implementations.find(
      (candidate) => candidate.id === implementationId,
    )
    if (!implementation) {
      throw new Error(
        `Implementation ${implementationId} is not currently available in the Hub.`,
      )
    }
    const target = resolveInside(this.projectsDirectory, implementation.id)
    if (await pathExists(target)) {
      return { success: false, message: 'Already exists' }
    }
    const staging = resolveInside(
      this.stagingDirectory,
      `clone-${implementation.id}-${randomUUID()}`,
    )
    try {
      const clone = await this.commandRunner('git', [
        'clone',
        '--depth',
        '1',
        '--filter=blob:none',
        '--sparse',
        '--branch',
        implementation.branch,
        '--',
        implementation.repo,
        staging,
      ])
      if (clone.code !== 0) {
        return {
          success: false,
          message: clone.stderr || `git exited with code ${clone.code}`,
        }
      }
      const sparse = await this.commandRunner('git', [
        '-C',
        staging,
        'sparse-checkout',
        'set',
        '--no-cone',
        '--',
        implementation.path,
      ])
      if (sparse.code !== 0) {
        return {
          success: false,
          message: sparse.stderr || `git exited with code ${sparse.code}`,
        }
      }
      const selected = resolveInside(staging, implementation.path)
      if (!(await pathExists(selected))) {
        return { success: false, message: 'Implementation path was not found.' }
      }
      await rename(selected, target)
      return { success: true, message: `Cloned ${implementation.name}`, path: target }
    } catch (error) {
      if (
        error
        && typeof error === 'object'
        && 'code' in error
        && (error.code === 'EEXIST' || error.code === 'ENOTEMPTY')
      ) {
        return { success: false, message: 'Already exists' }
      }
      throw error
    } finally {
      await rm(staging, { recursive: true, force: true })
    }
  }

  projectPath(value: unknown): string {
    const requested = requireString(value, 'Project path', 4096)
    const relative = path.relative(this.projectsDirectory, path.resolve(requested))
    if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
      throw new TypeError('Only a project inside the RAPP projects directory can be opened.')
    }
    return resolveInside(this.projectsDirectory, relative)
  }
}
