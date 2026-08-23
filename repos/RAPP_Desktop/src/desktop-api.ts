export interface CatalogAgent {
  id: string
  name: string
  description: string
  version: string
  icon?: string
  filename: string
  downloadUrl: string
  sha256: string
  features?: string[]
}

export interface CatalogSkill {
  id: string
  name: string
  description: string
  version: string
  icon?: string
  path: string
  features?: string[]
}

export interface CatalogImplementation {
  id: string
  name: string
  description: string
  version: string
  icon?: string
  repo: string
  path: string
  branch: string
  features?: string[]
}

export interface StoreManifest {
  agents: CatalogAgent[]
  skills: CatalogSkill[]
}

export interface HubManifest {
  implementations: CatalogImplementation[]
}

export interface ProjectInfo {
  name: string
  path: string
  created: string
}

export interface InstallResult {
  success: boolean
  message: string
  path?: string
}

export type BrainstemPhase =
  | 'checking'
  | 'starting'
  | 'ready'
  | 'authentication-required'
  | 'authentication-failed'
  | 'stopped'
  | 'error'

export interface BrainstemStatus {
  running: boolean
  port: number
  endpoint: string
  managed: boolean
  phase: BrainstemPhase
  detail?: string
  version?: string
  model?: string
  agentCount?: number
  authenticated?: boolean
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface BrainstemChatRequest {
  userInput: string
  sessionId?: string
  conversationHistory?: ChatTurn[]
}

export interface BrainstemChatResponse {
  response: string
  agentLogs: string[]
  agentsUsed: string[]
  sessionId: string
  contextId: string
}

export interface BrainstemLogin {
  userCode: string
  verificationUrl: string
}

export interface DesktopAppInfo {
  version: string
  platform:
    | 'aix'
    | 'android'
    | 'darwin'
    | 'freebsd'
    | 'haiku'
    | 'linux'
    | 'openbsd'
    | 'sunos'
    | 'win32'
    | 'cygwin'
    | 'netbsd'
}

export interface RappDesktopApi {
  catalog: {
    store(): Promise<StoreManifest>
    hub(): Promise<HubManifest>
    installAgent(agentId: string): Promise<InstallResult>
    installSkill(skill: CatalogSkill): Promise<InstallResult>
  }
  projects: {
    list(): Promise<ProjectInfo[]>
    create(name: string): Promise<InstallResult>
    clone(implementation: CatalogImplementation): Promise<InstallResult>
    reveal(path: string): Promise<void>
  }
  brainstem: {
    status(): Promise<BrainstemStatus>
    start(): Promise<BrainstemStatus>
    stop(): Promise<BrainstemStatus>
    chat(request: BrainstemChatRequest): Promise<BrainstemChatResponse>
    login(): Promise<BrainstemLogin>
    pollLogin(): Promise<BrainstemStatus>
    onStatus(listener: (status: BrainstemStatus) => void): () => void
  }
  shell: {
    openExternal(url: string): Promise<void>
  }
  app: {
    info(): Promise<DesktopAppInfo>
  }
}
