import { strict as assert } from 'node:assert'
import { spawn } from 'node:child_process'
import path from 'node:path'
import { test } from 'node:test'
import { pathToFileURL } from 'node:url'

import {
  assessLoopbackPeer,
  EXPECTED_DEVELOPMENT_ORIGIN,
  isTrustedRendererUrl,
  parseLsofListeners,
  resolveRendererTarget,
  SECURE_RENDERER_PREFERENCES,
  useTrustedPeer,
  waitAfterLauncher,
} from '../electron/security.ts'
import {
  BrainstemManager,
  waitForProcessExit,
  windowsListenerScript,
} from '../electron/brainstem.ts'
import { ChatRequestLifecycle } from '../src/desktop-api.ts'

const rendererDirectory = path.resolve('dist')
const rendererIndex = path.join(rendererDirectory, 'index.html')

test('packaged renderer ignores every development URL override', () => {
  for (const developmentUrl of [
    `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
    'http://127.0.0.1:9000/',
    'https://attacker.example/',
  ]) {
    assert.deepEqual(resolveRendererTarget({
      isPackaged: true,
      developmentUrl,
      rendererIndex,
    }), {
      kind: 'file',
      path: rendererIndex,
    })
  }
})

test('development renderer accepts only the configured loopback origin', () => {
  assert.deepEqual(resolveRendererTarget({
    isPackaged: false,
    developmentUrl: `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
    rendererIndex,
  }), {
    kind: 'development',
    url: `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
    origin: EXPECTED_DEVELOPMENT_ORIGIN,
  })

  for (const developmentUrl of [
    'https://127.0.0.1:5173/',
    'http://localhost:5173/',
    'http://127.0.0.1:5174/',
    'http://127.0.0.1:5173/other',
    'http://attacker.example:5173/',
  ]) {
    assert.throws(
      () => resolveRendererTarget({
        isPackaged: false,
        developmentUrl,
        rendererIndex,
      }),
      /development renderer/,
    )
  }
})

test('trusted sender policy rejects remote and escaped renderers', () => {
  const packagedTarget = resolveRendererTarget({
    isPackaged: true,
    developmentUrl: 'https://attacker.example/',
    rendererIndex,
  })
  assert.equal(
    isTrustedRendererUrl(
      pathToFileURL(rendererIndex).toString(),
      packagedTarget,
      rendererDirectory,
    ),
    true,
  )
  assert.equal(
    isTrustedRendererUrl(
      pathToFileURL(path.resolve('outside.html')).toString(),
      packagedTarget,
      rendererDirectory,
    ),
    false,
  )
  assert.equal(
    isTrustedRendererUrl(
      'https://attacker.example/',
      packagedTarget,
      rendererDirectory,
    ),
    false,
  )

  const developmentTarget = resolveRendererTarget({
    isPackaged: false,
    developmentUrl: `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
    rendererIndex,
  })
  assert.equal(
    isTrustedRendererUrl(
      `${EXPECTED_DEVELOPMENT_ORIGIN}/`,
      developmentTarget,
      rendererDirectory,
    ),
    true,
  )
  assert.equal(
    isTrustedRendererUrl(
      'http://127.0.0.1:5174/',
      developmentTarget,
      rendererDirectory,
    ),
    false,
  )
  assert.equal(
    isTrustedRendererUrl(
      'https://attacker.example/',
      {
        kind: 'development',
        url: 'https://attacker.example/',
        origin: 'https://attacker.example',
      },
      rendererDirectory,
    ),
    false,
  )
})

test('renderer hardening preferences are executable policy values', () => {
  assert.deepEqual(SECURE_RENDERER_PREFERENCES, {
    contextIsolation: true,
    nodeIntegration: false,
    sandbox: true,
    webSecurity: true,
  })
  assert.equal(Object.isFrozen(SECURE_RENDERER_PREFERENCES), true)
})

test('local peer proof requires the managed process or current OS user', () => {
  const listeners = parseLsofListeners('p321\nu501\nf4\n')
  assert.deepEqual(listeners, [{ pid: 321, ownerId: '501' }])
  assert.deepEqual(assessLoopbackPeer(listeners, ['501']), {
    kind: 'trusted',
    proof: 'user-owned-process',
    pid: 321,
  })

  test('Windows listener proof script separates every PowerShell statement', () => {
    const script = windowsListenerScript(7071)
    assert.match(script, /;\s+\$processIds =/)
    assert.match(script, /;\s+foreach \(/)
    assert.match(script, /;\s+if \(\$process\)/)
    assert.doesNotMatch(script, /\)\s+\$processIds =/)
    assert.doesNotMatch(script, /SilentlyContinue\s+if \(/)
    assert.doesNotMatch(script, /;\s+-[A-Za-z]/)
  })
  assert.equal(assessLoopbackPeer(listeners, ['502']).kind, 'untrusted')
  assert.equal(assessLoopbackPeer(listeners, ['501'], 999).kind, 'untrusted')
  assert.deepEqual(assessLoopbackPeer(listeners, ['502'], 321), {
    kind: 'trusted',
    proof: 'managed-process',
    pid: 321,
  })
  assert.equal(
    assessLoopbackPeer(
      [...listeners, { pid: 654, ownerId: '501' }],
      ['501'],
    ).kind,
    'untrusted',
  )
})

test('unverified peers cannot trigger secret or chat materialization', () => {
  let sensitiveOperationCalled = false
  assert.throws(
    () => useTrustedPeer(
      { kind: 'untrusted', detail: 'wrong owner' },
      () => {
        sensitiveOperationCalled = true
        return 'long-lived-secret'
      },
    ),
    /wrong owner/,
  )
  assert.equal(sensitiveOperationCalled, false)

  const value = useTrustedPeer(
    { kind: 'trusted', proof: 'https' },
    () => {
      sensitiveOperationCalled = true
      return 'encrypted-chat'
    },
  )
  assert.equal(value, 'encrypted-chat')
  assert.equal(sensitiveOperationCalled, true)
})

test('Brainstem manager never fetches or loads secrets for an unverified peer', async () => {
  let fetches = 0
  let credentialReads = 0
  const manager = new BrainstemManager({
    baseUrl: 'http://127.0.0.1:47991',
    legacyScriptPath: path.resolve('missing-brainstem.py'),
    onStatus: () => {},
    verifyPeer: async () => ({
      kind: 'untrusted',
      detail: 'listener belongs to another user',
    }),
    credentialHeaders: () => {
      credentialReads += 1
      return { 'X-Long-Lived-Secret': 'must-not-leak' }
    },
    fetch: async () => {
      fetches += 1
      throw new Error('fetch must not run')
    },
  })

  await assert.rejects(
    manager.chat({
      requestId: 'untrusted-chat',
      userInput: 'private chat',
    }),
    /another user/,
  )
  assert.equal(credentialReads, 0)
  assert.equal(fetches, 0)
})

test('Brainstem cancellation aborts chat and waits for server acknowledgement', async () => {
  let markFetchStarted
  const fetchStarted = new Promise((resolve) => {
    markFetchStarted = resolve
  })
  let acknowledgeCancel
  const cancelAcknowledgement = new Promise((resolve) => {
    acknowledgeCancel = resolve
  })
  let markCancelStarted
  const cancelStarted = new Promise((resolve) => {
    markCancelStarted = resolve
  })
  let chatBody
  let cancelBody
  const manager = new BrainstemManager({
    baseUrl: 'http://127.0.0.1:47992',
    legacyScriptPath: path.resolve('missing-brainstem.py'),
    onStatus: () => {},
    verifyPeer: async () => ({
      kind: 'trusted',
      proof: 'user-owned-process',
      pid: 123,
    }),
    credentialHeaders: () => ({ 'X-Test-Secret': 'test-only' }),
    fetch: async (url, init) => {
      if (new URL(url).pathname === '/cancel') {
        cancelBody = JSON.parse(init?.body)
        markCancelStarted()
        await cancelAcknowledgement
        return new Response(JSON.stringify({
          status: 'cancelled',
          cancelled: true,
          worker_ended: true,
        }), {
          headers: { 'Content-Type': 'application/json' },
        })
      }
      chatBody = JSON.parse(init?.body)
      const signal = init?.signal
      markFetchStarted()
      return new Promise((_resolve, reject) => {
        if (signal?.aborted) {
          reject(signal.reason)
          return
        }
        signal?.addEventListener(
          'abort',
          () => reject(signal.reason),
          { once: true },
        )
      })
    },
  })

  const pending = manager.chat({
    requestId: 'cancel-me',
    userInput: 'slow chat',
  })
  const chatRejected = assert.rejects(pending, /cancelled/)
  await fetchStarted
  const cancellation = manager.cancelChat('cancel-me')
  await cancelStarted

  let cancellationSettled = false
  void cancellation.finally(() => {
    cancellationSettled = true
  })
  await new Promise((resolve) => setTimeout(resolve, 0))
  assert.equal(cancellationSettled, false)
  assert.equal(chatBody.request_id, 'cancel-me')
  assert.deepEqual(cancelBody, { request_id: 'cancel-me' })

  acknowledgeCancel()
  await cancellation
  await chatRejected
  assert.equal(cancellationSettled, true)
})

test('external Brainstems may explicitly report cancellation unsupported', async () => {
  let markFetchStarted
  const fetchStarted = new Promise((resolve) => {
    markFetchStarted = resolve
  })
  const manager = new BrainstemManager({
    baseUrl: 'https://brainstem.example',
    legacyScriptPath: path.resolve('missing-brainstem.py'),
    onStatus: () => {},
    verifyPeer: async () => ({ kind: 'trusted', proof: 'https' }),
    credentialHeaders: () => ({ Authorization: 'test-only' }),
    fetch: async (url, init) => {
      if (new URL(url).pathname === '/cancel') {
        return new Response('', { status: 404 })
      }
      markFetchStarted()
      return new Promise((_resolve, reject) => {
        init?.signal?.addEventListener(
          'abort',
          () => reject(init.signal.reason),
          { once: true },
        )
      })
    },
  })

  const pending = manager.chat({
    requestId: 'external-cancel',
    userInput: 'slow chat',
  })
  const chatRejected = assert.rejects(pending, /cancelled/)
  await fetchStarted
  await manager.cancelChat('external-cancel')
  await chatRejected
})

test('bundled Brainstem cannot silently omit cancellation support', async () => {
  let markFetchStarted
  const fetchStarted = new Promise((resolve) => {
    markFetchStarted = resolve
  })
  const manager = new BrainstemManager({
    baseUrl: 'http://127.0.0.1:47993',
    legacyScriptPath: path.resolve('missing-brainstem.py'),
    onStatus: () => {},
    verifyPeer: async () => ({
      kind: 'trusted',
      proof: 'managed-process',
      pid: 321,
    }),
    credentialHeaders: () => ({ 'X-Test-Secret': 'test-only' }),
    fetch: async (url, init) => {
      if (new URL(url).pathname === '/cancel') {
        return new Response('', { status: 404 })
      }
      markFetchStarted()
      return new Promise((_resolve, reject) => {
        init?.signal?.addEventListener(
          'abort',
          () => reject(init.signal.reason),
          { once: true },
        )
      })
    },
  })
  manager.ownedProcess = { pid: 321 }

  const pending = manager.chat({
    requestId: 'bundled-cancel',
    userInput: 'slow chat',
  })
  const chatRejected = assert.rejects(pending, /cancelled/)
  await fetchStarted
  await assert.rejects(
    manager.cancelChat('bundled-cancel'),
    /does not support request cancellation/,
  )
  await chatRejected
})

test('launcher wait is skipped unless a launcher actually succeeded', async () => {
  let waits = 0
  const wait = async () => {
    waits += 1
    return true
  }

  assert.equal(await waitAfterLauncher({ kind: 'not-found' }, wait), false)
  assert.equal(
    await waitAfterLauncher({ kind: 'failed', error: 'exit code 1' }, wait),
    false,
  )
  assert.equal(waits, 0)
  assert.equal(await waitAfterLauncher({ kind: 'launched' }, wait), true)
  assert.equal(waits, 1)
})

test('process exit waiting times out, then observes confirmed teardown', async () => {
  const child = spawn(
    process.execPath,
    ['-e', 'setTimeout(() => process.exit(0), 100)'],
    { stdio: 'ignore' },
  )
  assert.equal(await waitForProcessExit(child, 5), false)
  assert.equal(await waitForProcessExit(child, 2_000), true)
  assert.equal(child.exitCode, 0)
})

test('clearing chat invalidates stale completion and session updates', () => {
  const lifecycle = new ChatRequestLifecycle()
  const stale = lifecycle.begin('request-1')
  assert.equal(lifecycle.accepts(stale), true)
  assert.equal(lifecycle.clear(), 'request-1')
  assert.equal(lifecycle.accepts(stale), false)
  assert.equal(lifecycle.finish(stale), false)

  const current = lifecycle.begin('request-2')
  assert.equal(lifecycle.accepts(current), true)
  assert.equal(lifecycle.accepts(stale), false)
  assert.equal(lifecycle.finish(current), true)
  assert.equal(lifecycle.accepts(current), false)
})
