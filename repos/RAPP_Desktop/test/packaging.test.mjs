import { strict as assert } from 'node:assert'
import { spawn } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import {
  chmod,
  mkdir,
  readFile,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import path from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

import { runDistribution } from '../scripts/dist.mjs'
import notarizeArtifacts from '../scripts/notarize-artifacts.mjs'
import {
  notarizationCredentials,
  runCommand,
  verificationSteps,
  verifySignedNotarizedTarget,
  windowsCommandLine,
} from '../scripts/macos-release.mjs'

const testDirectory = path.dirname(fileURLToPath(import.meta.url))
const projectDirectory = path.dirname(testDirectory)
const installer = path.join(projectDirectory, 'install', 'install.sh')

async function makeRuntime() {
  const runtime = path.join(testDirectory, `.runtime-${randomUUID()}`)
  await mkdir(runtime, { recursive: false })
  return runtime
}

async function writeExecutable(target, content) {
  await writeFile(target, `#!/bin/sh\nset -eu\n${content}\n`)
  await chmod(target, 0o700)
}

function execute(command, args, env) {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      cwd: projectDirectory,
      env,
      shell: false,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', (chunk) => {
      stdout += chunk
    })
    child.stderr.on('data', (chunk) => {
      stderr += chunk
    })
    child.on('close', (code) => resolve({ code, stdout, stderr }))
  })
}

async function assessmentEnvironment(runtime) {
  const bin = path.join(runtime, 'bin')
  const app = path.join(runtime, 'RAPP Desktop.app')
  const log = path.join(runtime, 'assessment.log')
  await mkdir(bin)
  await mkdir(app)
  await writeExecutable(
    path.join(bin, 'codesign'),
    `
printf 'codesign %s\\n' "$*" >> "$ASSESSMENT_LOG"
if [ "\${1:-}" = "--display" ]; then
  printf 'Authority=%s\\n' "$FAKE_AUTHORITY" >&2
fi
exit "\${FAKE_CODESIGN_EXIT:-0}"
`,
  )
  await writeExecutable(
    path.join(bin, 'xcrun'),
    `
printf 'xcrun %s\\n' "$*" >> "$ASSESSMENT_LOG"
exit "\${FAKE_STAPLER_EXIT:-0}"
`,
  )
  await writeExecutable(
    path.join(bin, 'spctl'),
    `
printf 'spctl %s\\n' "$*" >> "$ASSESSMENT_LOG"
exit "\${FAKE_SPCTL_EXIT:-0}"
`,
  )
  return {
    app,
    bin,
    env: {
      ...process.env,
      ASSESSMENT_LOG: log,
      FAKE_AUTHORITY: 'Developer ID Application: Example (TEAMID)',
      PATH: `${bin}:${process.env.PATH}`,
    },
    log,
  }
}

test('package and installers consistently require Node 22.12.0', async () => {
  const packageJson = JSON.parse(await readFile(path.join(projectDirectory, 'package.json')))
  const packageLock = JSON.parse(await readFile(path.join(projectDirectory, 'package-lock.json')))
  const shellInstaller = await readFile(installer, 'utf8')
  const powershellInstaller = await readFile(
    path.join(projectDirectory, 'install', 'install.ps1'),
    'utf8',
  )
  const readme = await readFile(path.join(projectDirectory, 'README.md'), 'utf8')

  assert.equal(packageJson.engines.node, '>=22.12.0')
  assert.equal(packageLock.packages[''].engines.node, '>=22.12.0')
  assert.match(shellInstaller, /major > 22 \|\| \(major === 22 && minor >= 12\)/)
  assert.match(
    powershellInstaller,
    /\(\$NodeMajor -eq 22\) -and \(\$NodeMinor -lt 12\)/,
  )
  assert.match(readme, /Node\.js 22\.12\.0 or newer/)
  assert.equal(packageJson.build.mac.forceCodeSigning, true)
  assert.equal(packageJson.build.mac.gatekeeperAssess, undefined)
  assert.equal(packageJson.build.mac.notarize, false)
  assert.equal(packageJson.build.dmg.sign, true)
  assert.equal(packageJson.build.afterSign, 'scripts/notarize-app.mjs')
  assert.equal(
    packageJson.build.afterAllArtifactBuild,
    'scripts/notarize-artifacts.mjs',
  )
  assert.equal(packageJson.scripts.dist, 'node scripts/dist.mjs')
  assert.ok(packageJson.devDependencies['@electron/notarize'])
})

test('macOS distribution rejects missing credentials before build', async () => {
  const commands = []
  let cleaned = false

  await assert.rejects(
    runDistribution({
      platform: 'darwin',
      env: {},
      run: async (command, args) => {
        commands.push([command, ...args])
        return { code: 0, stdout: '', stderr: '' }
      },
      cleanRelease: async () => {
        cleaned = true
      },
    }),
    /requires one complete notarization credential set/,
  )

  assert.deepEqual(commands, [])
  assert.equal(cleaned, false)
})

test('macOS distribution rejects the unpacked-smoke notarization bypass', async () => {
  const commands = []
  await assert.rejects(
    runDistribution({
      platform: 'darwin',
      env: {
        RAPP_DESKTOP_UNPACKED_SMOKE: '1',
        APPLE_KEYCHAIN_PROFILE: 'rapp-notary',
      },
      run: async (command, args) => {
        commands.push([command, ...args])
        return { code: 0, stdout: '', stderr: '' }
      },
      cleanRelease: async () => {},
    }),
    /cannot be used for distribution/,
  )
  assert.deepEqual(commands, [])
})

test('unpacked-smoke bypass removes and rejects distributable artifacts', async () => {
  const runtime = await makeRuntime()
  const artifact = path.join(runtime, 'RAPP Desktop.zip')
  await writeFile(artifact, 'not notarized')
  const previous = process.env.RAPP_DESKTOP_UNPACKED_SMOKE
  process.env.RAPP_DESKTOP_UNPACKED_SMOKE = '1'
  try {
    await assert.rejects(
      notarizeArtifacts({ artifactPaths: [artifact] }),
      /valid only for --dir builds/,
    )
    await assert.rejects(stat(artifact), { code: 'ENOENT' })
    assert.deepEqual(
      await notarizeArtifacts({ artifactPaths: [] }),
      [],
    )
  } finally {
    if (previous === undefined) {
      delete process.env.RAPP_DESKTOP_UNPACKED_SMOKE
    } else {
      process.env.RAPP_DESKTOP_UNPACKED_SMOKE = previous
    }
    await rm(runtime, { recursive: true, force: true })
  }
})

test('recognized notarization credential sets are complete and explicit', () => {
  assert.equal(
    notarizationCredentials({
      APPLE_KEYCHAIN_PROFILE: 'rapp-notary',
    }).kind,
    'keychain-profile',
  )
  assert.equal(
    notarizationCredentials({
      APPLE_API_KEY: 'AuthKey.p8',
      APPLE_API_KEY_ID: 'KEYID',
      APPLE_API_ISSUER: 'issuer',
    }).kind,
    'app-store-connect-api-key',
  )
  assert.equal(
    notarizationCredentials({
      APPLE_ID: 'release@example.com',
      APPLE_APP_SPECIFIC_PASSWORD: 'secret',
      APPLE_TEAM_ID: 'TEAMID',
    }).kind,
    'apple-id',
  )
  assert.equal(
    notarizationCredentials({
      APPLE_ID: 'release@example.com',
      APPLE_TEAM_ID: 'TEAMID',
    }),
    null,
  )
})

test('non-macOS distribution remains a build and electron-builder flow', async () => {
  const commands = []
  let verified = false
  await runDistribution({
    platform: 'linux',
    env: {},
    run: async (command, args) => {
      commands.push([command, ...args])
      return { code: 0, stdout: '', stderr: '' }
    },
    cleanRelease: async () => {},
    verifyRelease: async () => {
      verified = true
    },
  })

  test('Windows distribution routes cmd shims through a quoted command line', () => {
    assert.equal(
      windowsCommandLine('npm', ['run', 'build']),
      '""npm" "run" "build""',
    )
    assert.equal(
      windowsCommandLine('electron-builder', ['--publish', 'never']),
      '""electron-builder" "--publish" "never""',
    )
  })

  test('Windows command runner invokes ComSpec for npm cmd shims', async () => {
    const runtime = await makeRuntime()
    const fakeCmd = path.join(runtime, 'cmd.exe')
    const log = path.join(runtime, 'cmd-args.json')
    try {
      await writeExecutable(
        fakeCmd,
        `printf '%s\\n' "$@" > "${log}"`,
      )
      const result = await runCommand(
        'npm',
        ['run', 'build'],
        {
          platform: 'win32',
          env: { ...process.env, ComSpec: fakeCmd },
          quiet: true,
        },
      )
      assert.equal(result.code, 0)
      const args = await readFile(log, 'utf8')
      assert.match(args, /^\/d\n\/s\n\/c\n/)
      assert.match(args, /""npm" "run" "build""/)
    } finally {
      await rm(runtime, { recursive: true, force: true })
    }
  })

  assert.deepEqual(commands, [
    ['npm', 'run', 'build'],
    ['electron-builder', '--publish', 'never'],
  ])
  assert.equal(verified, false)
})

test('every macOS post-verification command failure rejects distribution', async () => {
  for (const kind of ['app', 'dmg']) {
    const target = kind === 'app' ? '/release/RAPP Desktop.app' : '/release/RAPP.dmg'
    const steps = verificationSteps(target, kind)
    for (let failureIndex = 0; failureIndex < steps.length; failureIndex += 1) {
      let callIndex = 0
      await assert.rejects(
        verifySignedNotarizedTarget(target, kind, async () => {
          const current = callIndex
          callIndex += 1
          if (current === failureIndex) {
            return { code: 7, stdout: '', stderr: 'controlled failure' }
          }
          return {
            code: 0,
            stdout: '',
            stderr: 'Authority=Developer ID Application: Example (TEAMID)',
          }
        }),
        /failed with exit code 7/,
        `${kind} verification step ${failureIndex + 1} must be fatal`,
      )
    }
  }
})

test('post-verification rejects a valid non-Developer-ID signature', async () => {
  await assert.rejects(
    verifySignedNotarizedTarget(
      '/release/RAPP Desktop.app',
      'app',
      async () => ({
        code: 0,
        stdout: '',
        stderr: 'Authority=Apple Development: Example (TEAMID)',
      }),
    ),
    /not signed by a Developer ID Application certificate/,
  )
})

test('macOS assessment requires Developer ID, notarization, and Gatekeeper', async () => {
  const runtime = await makeRuntime()
  try {
    const assessment = await assessmentEnvironment(runtime)
    const result = await execute(
      'bash',
      [installer, '--verify-macos-bundle', assessment.app],
      assessment.env,
    )

    assert.equal(result.code, 0, result.stderr)
    const log = await readFile(assessment.log, 'utf8')
    assert.match(log, /codesign --display --verbose=4/)
    assert.match(log, /codesign --verify --deep --strict --verbose=2/)
    assert.match(log, /xcrun stapler validate/)
    assert.match(log, /spctl --assess --type execute --verbose=4/)

    const rejected = await execute(
      'bash',
      [installer, '--verify-macos-bundle', assessment.app],
      { ...assessment.env, FAKE_SPCTL_EXIT: '1' },
    )
    assert.notEqual(rejected.code, 0)
    assert.match(rejected.stderr, /Gatekeeper rejected/)
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})

test('macOS source install does not copy or open a non-Developer-ID app', async () => {
  const runtime = await makeRuntime()
  const home = path.join(runtime, 'home')
  const bin = path.join(runtime, 'bin')
  const appRepository = path.join(home, '.rapp', 'app')
  const app = path.join(appRepository, 'release', 'mac', 'RAPP Desktop.app')
  const assessmentLog = path.join(runtime, 'assessment.log')
  const openMarker = path.join(runtime, 'opened')

  try {
    await mkdir(path.join(appRepository, '.git'), { recursive: true })
    await mkdir(app, { recursive: true })
    await mkdir(bin)
    await writeExecutable(path.join(bin, 'uname'), "printf 'Darwin\\n'")
    await writeExecutable(path.join(bin, 'git'), 'exit 0')
    await writeExecutable(path.join(bin, 'node'), 'exit 0')
    await writeExecutable(path.join(bin, 'npm'), 'exit 0')
    await writeExecutable(
      path.join(bin, 'python3'),
      `
if [ "\${1:-}" = "-m" ] && [ "\${2:-}" = "venv" ]; then
  mkdir -p "$3/bin"
  printf '#!/bin/sh\\nexit 0\\n' > "$3/bin/python"
  chmod +x "$3/bin/python"
fi
exit 0
`,
    )
    await writeExecutable(
      path.join(bin, 'codesign'),
      `
printf 'codesign %s\\n' "$*" >> "$ASSESSMENT_LOG"
if [ "\${1:-}" = "--display" ]; then
  printf 'Authority=Apple Development: Example (TEAMID)\\n' >&2
fi
exit 0
`,
    )
    await writeExecutable(
      path.join(bin, 'xcrun'),
      "printf 'xcrun %s\\n' \"$*\" >> \"$ASSESSMENT_LOG\"",
    )
    await writeExecutable(
      path.join(bin, 'spctl'),
      "printf 'spctl %s\\n' \"$*\" >> \"$ASSESSMENT_LOG\"",
    )
    await writeExecutable(
      path.join(bin, 'open'),
      `printf 'opened\\n' > "${openMarker}"`,
    )

    const result = await execute('bash', [installer], {
      ...process.env,
      ASSESSMENT_LOG: assessmentLog,
      HOME: home,
      PATH: `${bin}:${process.env.PATH}`,
    })

    assert.notEqual(result.code, 0)
    assert.match(result.stderr, /not signed with a Developer ID Application certificate/)
    await assert.rejects(
      stat(path.join(home, 'Applications', 'RAPP Desktop.app')),
      { code: 'ENOENT' },
    )
    await assert.rejects(stat(openMarker), { code: 'ENOENT' })
    const log = await readFile(assessmentLog, 'utf8')
    assert.match(log, /codesign --display --verbose=4/)
    assert.doesNotMatch(log, /xcrun|spctl/)
  } finally {
    await rm(runtime, { recursive: true, force: true })
  }
})
