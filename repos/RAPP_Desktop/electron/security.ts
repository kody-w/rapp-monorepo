import path from 'node:path'

export const SECURE_RENDERER_PREFERENCES = Object.freeze({
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: true,
  webSecurity: true,
})

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
