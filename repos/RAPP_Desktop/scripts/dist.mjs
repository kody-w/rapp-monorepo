import { rm } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import {
  requireNotarizationCredentials,
  runChecked,
  runCommand,
  verifyMacRelease,
} from './macos-release.mjs'

const projectDirectory = path.dirname(
  path.dirname(fileURLToPath(import.meta.url)),
)

export async function runDistribution({
  platform = process.platform,
  env = process.env,
  run = runCommand,
  cleanRelease,
  verifyRelease = verifyMacRelease,
  cwd = projectDirectory,
} = {}) {
  if (platform === 'darwin') {
    if (env.RAPP_DESKTOP_UNPACKED_SMOKE === '1') {
      throw new Error(
        'RAPP_DESKTOP_UNPACKED_SMOKE cannot be used for distribution.',
      )
    }
    requireNotarizationCredentials(env)
  }

  const releaseDirectory = path.join(cwd, 'release')
  if (cleanRelease) {
    await cleanRelease(releaseDirectory)
  } else {
    await rm(releaseDirectory, { recursive: true, force: true })
  }
  await runChecked(run, 'npm', ['run', 'build'], { cwd, env })
  await runChecked(run, 'electron-builder', ['--publish', 'never'], { cwd, env })

  if (platform === 'darwin') {
    await verifyRelease({ releaseDirectory, run })
  }
}

if (
  process.argv[1]
  && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  runDistribution().catch((error) => {
    console.error(`[dist] ${error instanceof Error ? error.message : String(error)}`)
    process.exitCode = 1
  })
}
