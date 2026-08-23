import { notarize } from '@electron/notarize'
import path from 'node:path'

import { notarizationOptions } from './macos-release.mjs'

export default async function notarizeApp(context) {
  if (process.platform !== 'darwin') return
  // `electron-builder --dir` is a local unpacked smoke artifact, never a
  // distributable. Release paths still flow through scripts/dist.mjs and
  // require notarization before producing DMG/ZIP artifacts.
  if (
    context.packager.info.options.dir === true
    || process.env.RAPP_DESKTOP_UNPACKED_SMOKE === '1'
  ) return
  const appPath = path.join(
    context.appOutDir,
    `${context.packager.appInfo.productFilename}.app`,
  )
  await notarize(notarizationOptions(appPath))
}
