import { spawn } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { mkdir, readdir, rm } from 'node:fs/promises'
import path from 'node:path'

function value(env, name) {
  const candidate = env[name]
  return typeof candidate === 'string' && candidate.trim()
    ? candidate.trim()
    : undefined
}

export function notarizationCredentials(env = process.env) {
  const keychainProfile = value(env, 'APPLE_KEYCHAIN_PROFILE')
  if (keychainProfile) {
    return {
      kind: 'keychain-profile',
      options: {
        keychainProfile,
        ...(value(env, 'APPLE_KEYCHAIN')
          ? { keychain: value(env, 'APPLE_KEYCHAIN') }
          : {}),
      },
    }
  }

  const appleApiKey = value(env, 'APPLE_API_KEY')
  const appleApiKeyId = value(env, 'APPLE_API_KEY_ID')
  const appleApiIssuer = value(env, 'APPLE_API_ISSUER')
  if (appleApiKey && appleApiKeyId && appleApiIssuer) {
    return {
      kind: 'app-store-connect-api-key',
      options: { appleApiKey, appleApiKeyId, appleApiIssuer },
    }
  }

  const appleId = value(env, 'APPLE_ID')
  const appleIdPassword = value(env, 'APPLE_APP_SPECIFIC_PASSWORD')
  const teamId = value(env, 'APPLE_TEAM_ID')
  if (appleId && appleIdPassword && teamId) {
    return {
      kind: 'apple-id',
      options: { appleId, appleIdPassword, teamId },
    }
  }

  return null
}

export function requireNotarizationCredentials(env = process.env) {
  const credentials = notarizationCredentials(env)
  if (credentials) return credentials
  throw new Error(
    'macOS distribution requires one complete notarization credential set: '
      + 'APPLE_KEYCHAIN_PROFILE; APPLE_API_KEY + APPLE_API_KEY_ID + '
      + 'APPLE_API_ISSUER; or APPLE_ID + APPLE_APP_SPECIFIC_PASSWORD + '
      + 'APPLE_TEAM_ID.',
  )
}

export function notarizationOptions(appPath, env = process.env) {
  return {
    appPath,
    ...requireNotarizationCredentials(env).options,
  }
}

export function windowsCommandLine(command, args) {
  const quote = (argument) => `"${String(argument).replaceAll('"', '""')}"`
  return `"${[command, ...args].map(quote).join(' ')}"`
}

export function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const platform = options.platform ?? process.platform
    const executable = platform === 'win32'
      ? options.env?.ComSpec ?? process.env.ComSpec ?? 'cmd.exe'
      : command
    const executableArgs = platform === 'win32'
      ? ['/d', '/s', '/c', windowsCommandLine(command, args)]
      : args
    const child = spawn(executable, executableArgs, {
      cwd: options.cwd,
      env: options.env,
      shell: false,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', (chunk) => {
      const text = chunk.toString()
      stdout += text
      if (!options.quiet) process.stdout.write(text)
    })
    child.stderr.on('data', (chunk) => {
      const text = chunk.toString()
      stderr += text
      if (!options.quiet) process.stderr.write(text)
    })
    child.once('error', reject)
    child.once('close', (code) => {
      resolve({ code: code ?? -1, stdout, stderr })
    })
  })
}

export async function runChecked(run, command, args, options = {}) {
  const result = await run(command, args, options)
  if (result?.code !== 0) {
    const detail = result?.stderr?.trim() || result?.stdout?.trim()
    throw new Error(
      `${command} ${args.join(' ')} failed with exit code ${result?.code ?? 'unknown'}`
        + (detail ? `: ${detail}` : '.'),
    )
  }
  return result
}

export function verificationSteps(target, kind) {
  if (kind === 'app') {
    return [
      {
        command: 'codesign',
        args: ['--display', '--verbose=4', target],
        requiresDeveloperId: true,
      },
      {
        command: 'codesign',
        args: ['--verify', '--deep', '--strict', '--verbose=2', target],
      },
      { command: 'xcrun', args: ['stapler', 'validate', target] },
      {
        command: 'spctl',
        args: ['--assess', '--type', 'execute', '--verbose=4', target],
      },
    ]
  }
  if (kind === 'dmg') {
    return [
      {
        command: 'codesign',
        args: ['--display', '--verbose=4', target],
        requiresDeveloperId: true,
      },
      {
        command: 'codesign',
        args: ['--verify', '--strict', '--verbose=2', target],
      },
      { command: 'xcrun', args: ['stapler', 'validate', target] },
      {
        command: 'spctl',
        args: [
          '--assess',
          '--type',
          'open',
          '--context',
          'context:primary-signature',
          '--verbose=4',
          target,
        ],
      },
    ]
  }
  throw new TypeError(`Unsupported macOS release target kind: ${kind}`)
}

export function requireDeveloperIdAuthority(output) {
  if (!/^Authority=Developer ID Application:/m.test(output)) {
    throw new Error('Release target is not signed by a Developer ID Application certificate.')
  }
}

export async function verifySignedNotarizedTarget(target, kind, run = runCommand) {
  for (const step of verificationSteps(target, kind)) {
    const result = await runChecked(run, step.command, step.args, { quiet: true })
    if (step.requiresDeveloperId) {
      requireDeveloperIdAuthority(`${result.stdout ?? ''}\n${result.stderr ?? ''}`)
    }
  }
}

async function walkReleaseDirectory(directory, targets) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.verify-')) continue
    const target = path.join(directory, entry.name)
    if (entry.isDirectory()) {
      if (entry.name.endsWith('.app')) {
        targets.apps.push(target)
      } else {
        await walkReleaseDirectory(target, targets)
      }
    } else if (entry.isFile() && entry.name.endsWith('.dmg')) {
      targets.dmgs.push(target)
    } else if (entry.isFile() && entry.name.endsWith('.zip')) {
      targets.zips.push(target)
    }
  }
}

export async function findMacReleaseTargets(releaseDirectory) {
  const targets = { apps: [], dmgs: [], zips: [] }
  await walkReleaseDirectory(releaseDirectory, targets)
  targets.apps.sort()
  targets.dmgs.sort()
  targets.zips.sort()
  return targets
}

export async function verifyMacRelease({
  releaseDirectory,
  run = runCommand,
  findTargets = findMacReleaseTargets,
}) {
  const targets = await findTargets(releaseDirectory)
  if (targets.apps.length === 0 || targets.dmgs.length === 0 || targets.zips.length === 0) {
    throw new Error('macOS distribution did not produce an app, DMG, and ZIP to verify.')
  }

  for (const app of targets.apps) {
    await verifySignedNotarizedTarget(app, 'app', run)
  }
  for (const dmg of targets.dmgs) {
    await verifySignedNotarizedTarget(dmg, 'dmg', run)
  }
  for (const zip of targets.zips) {
    const extractionDirectory = path.join(
      releaseDirectory,
      `.verify-${randomUUID()}`,
    )
    await mkdir(extractionDirectory, { recursive: false })
    try {
      await runChecked(
        run,
        'ditto',
        ['-x', '-k', zip, extractionDirectory],
        { quiet: true },
      )
      const extracted = await findTargets(extractionDirectory)
      if (extracted.apps.length === 0) {
        throw new Error(`${path.basename(zip)} does not contain a macOS app bundle.`)
      }
      for (const app of extracted.apps) {
        await verifySignedNotarizedTarget(app, 'app', run)
      }
    } finally {
      await rm(extractionDirectory, { recursive: true, force: true })
    }
  }
}
