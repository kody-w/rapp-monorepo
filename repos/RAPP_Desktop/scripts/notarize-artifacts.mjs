import { notarize } from '@electron/notarize'
import { rm } from 'node:fs/promises'

import { notarizationOptions } from './macos-release.mjs'

export default async function notarizeArtifacts(context) {
  if (process.platform !== 'darwin') return []
  if (process.env.RAPP_DESKTOP_UNPACKED_SMOKE === '1') {
    if (context.artifactPaths.length === 0) return []
    await Promise.all(
      context.artifactPaths.map((artifact) => rm(artifact, { force: true })),
    )
    throw new Error(
      'RAPP_DESKTOP_UNPACKED_SMOKE is valid only for --dir builds; '
      + 'distributable artifacts were removed.',
    )
  }
  const dmgs = context.artifactPaths.filter((artifact) => artifact.endsWith('.dmg'))
  if (dmgs.length === 0) {
    throw new Error('macOS distribution did not produce a DMG to notarize.')
  }
  for (const dmg of dmgs) {
    await notarize(notarizationOptions(dmg))
  }
  return []
}
