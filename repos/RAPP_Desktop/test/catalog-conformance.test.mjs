import { strict as assert } from 'node:assert'
import { createHash, randomUUID } from 'node:crypto'
import {
  mkdir,
  readFile,
  readdir,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import path from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

import {
  DesktopService,
  parseHubManifestDocument,
  parseStoreManifestDocument,
  runCommand,
} from '../electron/desktop-service.ts'

const testDirectory = path.dirname(fileURLToPath(import.meta.url))
const STORE_URL = 'https://raw.githubusercontent.com/kody-w/RAPP_Store/main/index.json'
const HUB_URL = 'https://raw.githubusercontent.com/kody-w/RAPP_Hub/main/manifest.json'
const SKILL_URL =
  'https://raw.githubusercontent.com/kody-w/RAPP_Store/main/apps/@rapp/catalog-test/skill/SKILL.md'

function digest(content) {
  return createHash('sha256').update(content).digest('hex')
}

function storeFixture(skillContent = '# Catalog test\n') {
  return {
    schema: 'rapp-store/1.0',
    rapplications: [
      {
        id: 'catalog_test',
        name: 'Catalog Test',
        summary: 'A public catalog projection.',
        version: '1.2.3',
        tags: ['catalog', 'test'],
        singleton_filename: 'catalog_test_agent.py',
        singleton_url:
          'https://raw.githubusercontent.com/kody-w/RAPP_Store/main/apps/@rapp/catalog-test/singleton/catalog_test_agent.py',
        singleton_sha256: 'a'.repeat(64),
        skill_url: SKILL_URL,
        skill_sha256: digest(skillContent),
      },
      {
        id: 'private_entry',
        access: 'private',
        private_repo: 'example/private',
        singleton_url:
          'https://raw.githubusercontent.com/example/private/main/private.py',
      },
    ],
  }
}

function implementation(id, pathValue = `implementations/${id}`) {
  return {
    id,
    name: id,
    description: `${id} implementation`,
    version: '1.0.0',
    repo: 'https://github.com/example/public-repo',
    branch: 'main',
    path: pathValue,
    features: ['test'],
  }
}

function hubFixture(...implementations) {
  return { implementations }
}

function jsonResponse(value, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}

async function makeRuntime() {
  const runtime = path.join(testDirectory, `.runtime-${randomUUID()}`)
  await mkdir(runtime, { recursive: false })
  return runtime
}

test('Store parser projects real skill fields and hides private entries', () => {
  const manifest = parseStoreManifestDocument(storeFixture())

  assert.deepEqual(manifest.agents.map((agent) => agent.id), ['catalog_test'])
  assert.equal(manifest.skills.length, 1)
  assert.deepEqual(
    Object.keys(manifest.skills[0]).sort(),
    ['description', 'features', 'icon', 'id', 'name', 'path', 'version'],
  )
  assert.deepEqual(manifest.skills[0], {
    id: 'catalog_test',
    name: 'Catalog Test',
    description: 'A public catalog projection.',
    version: '1.2.3',
    icon: undefined,
    path: 'apps/@rapp/catalog-test/skill',
    features: ['catalog', 'test'],
  })
  assert.equal(manifest.agents.some((agent) => agent.id === 'private_entry'), false)
})

test('skill install refetches by stable ID and verifies canonical bytes', async () => {
  const runtime = await makeRuntime()
  const skillContent = '# Canonical skill\n'
  const requests = []
  const fetchImplementation = async (input) => {
    const url = input.toString()
    requests.push(url)
    if (url === STORE_URL) return jsonResponse(storeFixture(skillContent))
    if (url === SKILL_URL) return new Response(skillContent)
    return new Response('not found', { status: 404 })
  }
  const service = new DesktopService({
    fetch: fetchImplementation,
    rappHome: path.join(runtime, '.rapp'),
  })

  try {
    await service.initialize()
    const result = await service.installSkill({
      id: 'catalog_test',
      name: 'Tampered renderer name',
      description: 'Tampered renderer description',
      version: '999',
      path: '../../tampered',
    })

    assert.equal(result.success, true)
    assert.deepEqual(requests, [STORE_URL, SKILL_URL])
    assert.equal(
      await readFile(path.join(service.skillsDirectory, 'catalog_test', 'SKILL.md'), 'utf8'),
      skillContent,
    )
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})

test('skill install rejects a SHA-256 mismatch without publishing bytes', async () => {
  const runtime = await makeRuntime()
  const fetchImplementation = async (input) => {
    const url = input.toString()
    if (url === STORE_URL) return jsonResponse(storeFixture('# Expected\n'))
    if (url === SKILL_URL) return new Response('# Different\n')
    return new Response('not found', { status: 404 })
  }
  const service = new DesktopService({
    fetch: fetchImplementation,
    rappHome: path.join(runtime, '.rapp'),
  })

  try {
    await service.initialize()
    await assert.rejects(
      service.installSkill({ id: 'catalog_test' }),
      /Integrity check failed for Catalog Test/,
    )
    await assert.rejects(
      stat(path.join(service.skillsDirectory, 'catalog_test', 'SKILL.md')),
      { code: 'ENOENT' },
    )
    await assert.rejects(service.installAgent('private_entry'), /not in the current Store catalog/)
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})

test('Hub filters definitive 404s and successful non-directories', async () => {
  const available = implementation('available')
  const missing = implementation('missing')
  const fileOnly = implementation('file-only')
  const requested = []
  const fetchImplementation = async (input, init) => {
    const url = input.toString()
    requested.push({ url, accept: new Headers(init?.headers).get('accept') })
    if (url === HUB_URL) return jsonResponse(hubFixture(available, missing, fileOnly))
    if (url.includes('/contents/implementations/available?ref=main')) {
      return jsonResponse([{ type: 'file', name: 'README.md' }])
    }
    if (url.includes('/contents/implementations/file-only?ref=main')) {
      return jsonResponse({ type: 'file', name: 'file-only' })
    }
    return new Response('not found', { status: 404 })
  }
  const service = new DesktopService({ fetch: fetchImplementation })

  assert.equal(parseHubManifestDocument(hubFixture(available)).implementations.length, 1)
  const manifest = await service.hubManifest()
  assert.deepEqual(manifest.implementations.map((entry) => entry.id), ['available'])
  assert.equal(
    requested.filter((request) => request.url.startsWith('https://api.github.com/')).length,
    3,
  )
  assert.ok(
    requested
      .filter((request) => request.url.startsWith('https://api.github.com/'))
      .every((request) => request.accept === 'application/vnd.github+json'),
  )
})

test('Hub propagates authorization, server, offline, and timeout failures', async () => {
  const available = implementation('available')
  const failures = [
    {
      name: 'authorization',
      response: () => new Response('forbidden', { status: 403 }),
      expected: /HTTP 403/,
    },
    {
      name: 'server',
      response: () => new Response('unavailable', { status: 503 }),
      expected: /HTTP 503/,
    },
    {
      name: 'offline',
      response: () => {
        throw new TypeError('fetch failed: offline')
      },
      expected: /offline/,
    },
    {
      name: 'timeout',
      response: () => {
        throw new DOMException('request timed out', 'TimeoutError')
      },
      expected: /timed out/,
    },
  ]

  for (const failure of failures) {
    let availabilityRequests = 0
    const service = new DesktopService({
      fetch: async (input) => {
        const url = input.toString()
        if (url === HUB_URL) return jsonResponse(hubFixture(available))
        availabilityRequests += 1
        return failure.response()
      },
    })

    await assert.rejects(
      service.hubManifest(),
      failure.expected,
      `${failure.name} failure must reject instead of emptying the Hub`,
    )
    await assert.rejects(service.hubManifest(), failure.expected)
    assert.equal(
      availabilityRequests,
      2,
      `${failure.name} failures must not be cached`,
    )
  }
})

test('Hub availability cache covers successful and 404 results before clone', async () => {
  const runtime = await makeRuntime()
  const available = implementation('available')
  const missing = implementation('missing')
  let now = 1_000
  let availabilityRequests = 0
  const service = new DesktopService({
    fetch: async (input) => {
      const url = input.toString()
      if (url === HUB_URL) return jsonResponse(hubFixture(available, missing))
      availabilityRequests += 1
      if (url.includes('/contents/implementations/available?ref=main')) {
        return jsonResponse([{ type: 'file', name: 'main.py' }])
      }
      return new Response('not found', { status: 404 })
    },
    rappHome: path.join(runtime, '.rapp'),
    availabilityCacheTtlMs: 100,
    now: () => now,
  })

  try {
    await service.initialize()
    assert.deepEqual(
      (await service.hubManifest()).implementations.map((entry) => entry.id),
      ['available'],
    )
    await service.hubManifest()
    await mkdir(path.join(service.projectsDirectory, available.id))
    assert.equal((await service.cloneImplementation(available.id)).success, false)
    assert.equal(availabilityRequests, 2)

    now += 101
    await service.hubManifest()
    assert.equal(availabilityRequests, 4)
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})

test('concurrent clones use canonical sparse staging and publish one target', async () => {
  const runtime = await makeRuntime()
  const canonical = implementation('available')
  const commands = []
  const fetchImplementation = async (input) => {
    const url = input.toString()
    if (url === HUB_URL) return jsonResponse(hubFixture(canonical))
    if (url.includes('/contents/implementations/available?ref=main')) {
      return jsonResponse([{ type: 'file', name: 'main.py' }])
    }
    return new Response('not found', { status: 404 })
  }
  const commandRunner = async (command, args) => {
    commands.push([command, ...args])
    if (args[0] === 'clone') {
      const staging = args.at(-1)
      await mkdir(path.join(staging, canonical.path), { recursive: true })
      await mkdir(path.join(staging, 'unselected'), { recursive: true })
      await writeFile(path.join(staging, canonical.path, 'main.py'), 'print("ok")\n')
      await writeFile(path.join(staging, 'unselected', 'must-not-publish'), 'no\n')
    }
    return { code: 0, stderr: '' }
  }
  const service = new DesktopService({
    fetch: fetchImplementation,
    rappHome: path.join(runtime, '.rapp'),
    runCommand: commandRunner,
  })

  try {
    await service.initialize()
    const rendererPayload = {
      ...canonical,
      repo: 'https://github.com/attacker/repository',
      path: 'attacker/path',
      branch: 'attacker',
    }
    const results = await Promise.all([
      service.cloneImplementation(rendererPayload),
      service.cloneImplementation(rendererPayload),
    ])

    assert.deepEqual(results.map((result) => result.success).sort(), [false, true])
    assert.equal(
      await readFile(path.join(service.projectsDirectory, 'available', 'main.py'), 'utf8'),
      'print("ok")\n',
    )
    await assert.rejects(
      stat(path.join(service.projectsDirectory, 'available', 'unselected')),
      { code: 'ENOENT' },
    )
    assert.deepEqual(await readdir(service.stagingDirectory), [])
    const cloneCommands = commands.filter((command) => command[1] === 'clone')
    assert.equal(cloneCommands.length, 2)
    assert.ok(cloneCommands.every((command) => command.includes(canonical.repo)))
    assert.ok(cloneCommands.every((command) => command.includes(canonical.branch)))
    assert.ok(commands.some((command) => command.includes(canonical.path)))
    assert.equal(commands.some((command) => command.includes('attacker/path')), false)
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})

test('timed out commands kill a spawned grandchild before rejecting', async () => {
  const runtime = await makeRuntime()
  const heartbeat = path.join(runtime, 'heartbeat')
  const pidFile = path.join(runtime, 'grandchild.pid')
  const grandchildCode = [
    "const fs = require('node:fs')",
    'const heartbeat = process.argv[1]',
    "fs.appendFileSync(heartbeat, 'x')",
    "setInterval(() => fs.appendFileSync(heartbeat, 'x'), 20)",
  ].join(';')
  const childCode = [
    "const fs = require('node:fs')",
    "const { spawn } = require('node:child_process')",
    'const grandchild = spawn(process.execPath, ["-e", process.argv[1], process.argv[2]], { stdio: "ignore" })',
    'fs.writeFileSync(process.argv[3], String(grandchild.pid))',
    'setInterval(() => {}, 1000)',
  ].join(';')

  try {
    await assert.rejects(
      runCommand(process.execPath, ['-e', childCode, grandchildCode, heartbeat, pidFile], 500),
      /timed out/,
    )
    const firstSize = (await stat(heartbeat)).size
    await new Promise((resolve) => setTimeout(resolve, 150))
    const settledSize = (await stat(heartbeat)).size
    assert.equal(settledSize, firstSize)
  } finally {
    try {
      const grandchildPid = Number(await readFile(pidFile, 'utf8'))
      if (Number.isInteger(grandchildPid)) process.kill(grandchildPid, 'SIGKILL')
    } catch {
      // The process tree is already gone or never started.
    }
    await rm(runtime, { recursive: true, force: true })
  }
})
