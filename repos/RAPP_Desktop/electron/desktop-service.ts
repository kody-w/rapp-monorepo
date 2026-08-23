import { spawn } from 'node:child_process'
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
const STORE_RAW_ROOT =
  'https://raw.githubusercontent.com/kody-w/RAPP_Store/main/'
const MAX_MANIFEST_BYTES = 2 * 1024 * 1024
const MAX_PACKAGE_BYTES = 5 * 1024 * 1024

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

function parseSkill(value: unknown): CatalogSkill {
  const record = requireRecord(value, 'Skill')
  return {
    id: requireSafeRelativePath(record.id, 'Skill id'),
    name: requireString(record.name, 'Skill name', 256),
    description: requireString(record.description, 'Skill description', 4096),
    version: requireString(record.version, 'Skill version', 64),
    icon: optionalString(record.icon, 'Skill icon'),
    path: requireSafeRelativePath(record.path, 'Skill path'),
    features: stringArray(record.features),
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

async function fetchText(url: string, maximumBytes: number): Promise<string> {
  const response = await fetch(url, {
    headers: { Accept: 'application/json, text/plain;q=0.9' },
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
  const text = await response.text()
  if (Buffer.byteLength(text) > maximumBytes) {
    throw new Error('Remote content exceeds the allowed size.')
  }
  return text
}

async function fetchJson(url: string): Promise<unknown> {
  const text = await fetchText(url, MAX_MANIFEST_BYTES)
  try {
    return JSON.parse(text)
  } catch {
    throw new Error('Remote manifest is not valid JSON.')
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

async function atomicWrite(target: string, content: string): Promise<void> {
  const temporary = `${target}.${process.pid}.${randomUUID()}.tmp`
  await writeFile(temporary, content, { encoding: 'utf8', flag: 'wx', mode: 0o600 })
  try {
    await rename(temporary, target)
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error
    await rm(target, { force: true })
    await rename(temporary, target)
  }
}

async function run(
  command: string,
  args: string[],
  timeoutMs = 120_000,
): Promise<{ code: number; stderr: string }> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      shell: false,
      windowsHide: true,
      stdio: ['ignore', 'ignore', 'pipe'],
    })
    let stderr = ''
    child.stderr?.on('data', (chunk: Buffer) => {
      stderr = `${stderr}${chunk.toString()}`.slice(-16_384)
    })
    let timedOut = false
    const timer = setTimeout(() => {
      timedOut = true
      child.kill('SIGKILL')
    }, timeoutMs)
    child.once('error', (error) => {
      clearTimeout(timer)
      reject(error)
    })
    child.once('exit', (code) => {
      clearTimeout(timer)
      if (timedOut) {
        reject(new Error(`${command} timed out.`))
      } else {
        resolve({ code: code ?? -1, stderr: stderr.trim() })
      }
    })
  })
}

export class DesktopService {
  readonly rappHome = path.join(os.homedir(), '.rapp')
  readonly agentsDirectory = path.join(this.rappHome, 'agents')
  readonly skillsDirectory = path.join(this.rappHome, 'skills')
  readonly projectsDirectory = path.join(this.rappHome, 'projects')
  readonly stagingDirectory = path.join(this.rappHome, '.staging')

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
    const record = requireRecord(await fetchJson(STORE_MANIFEST), 'Store manifest')
    if (record.schema !== 'rapp-store/1.0' || !Array.isArray(record.rapplications)) {
      throw new Error('Store catalog does not satisfy rapp-store/1.0.')
    }
    return {
      agents: record.rapplications.map(parseAgent),
      skills: [],
    }
  }

  async hubManifest(): Promise<HubManifest> {
    const record = requireRecord(await fetchJson(HUB_MANIFEST), 'Hub manifest')
    if (!Array.isArray(record.implementations)) {
      throw new Error('Hub manifest is missing implementations.')
    }
    return { implementations: record.implementations.map(parseImplementation) }
  }

  async installAgent(value: unknown): Promise<InstallResult> {
    const agentId = requireString(value, 'Rapplication id', 256)
    const manifest = await this.storeManifest()
    const agent = manifest.agents.find((candidate) => candidate.id === agentId)
    if (!agent) throw new Error(`Rapplication ${agentId} is not in the current Store catalog.`)
    if (path.basename(agent.filename) !== agent.filename) {
      throw new TypeError('Agent filename cannot contain directories.')
    }
    const content = await fetchText(agent.downloadUrl, MAX_PACKAGE_BYTES)
    const digest = createHash('sha256').update(content).digest('hex')
    if (digest !== agent.sha256) {
      throw new Error(`Integrity check failed for ${agent.name}.`)
    }
    const target = resolveInside(this.agentsDirectory, agent.filename)
    await atomicWrite(target, content)
    return { success: true, message: `Installed ${agent.name}`, path: target }
  }

  async installSkill(value: unknown): Promise<InstallResult> {
    const skill = parseSkill(value)
    const source = new URL(`${skill.path}/SKILL.md`, STORE_RAW_ROOT)
    const content = await fetchText(source.toString(), MAX_PACKAGE_BYTES)
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
    const implementation = parseImplementation(value)
    const target = resolveInside(this.projectsDirectory, implementation.id)
    if (await pathExists(target)) {
      return { success: false, message: 'Already exists' }
    }
    const staging = resolveInside(
      this.stagingDirectory,
      `clone-${implementation.id}-${randomUUID()}`,
    )
    try {
      const clone = await run('git', [
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
      const sparse = await run('git', [
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
