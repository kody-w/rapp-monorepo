const { contextBridge, ipcRenderer } = require('electron')

const IPC = Object.freeze({
  appInfo: 'rapp:app-info',
  catalogStore: 'rapp:catalog-store',
  catalogHub: 'rapp:catalog-hub',
  catalogInstallAgent: 'rapp:catalog-install-agent',
  catalogInstallSkill: 'rapp:catalog-install-skill',
  projectsList: 'rapp:projects-list',
  projectsCreate: 'rapp:projects-create',
  projectsClone: 'rapp:projects-clone',
  projectsReveal: 'rapp:projects-reveal',
  brainstemStatus: 'rapp:brainstem-status',
  brainstemStart: 'rapp:brainstem-start',
  brainstemStop: 'rapp:brainstem-stop',
  brainstemChat: 'rapp:brainstem-chat',
  brainstemLogin: 'rapp:brainstem-login',
  brainstemLoginPoll: 'rapp:brainstem-login-poll',
  brainstemStatusChanged: 'rapp:brainstem-status-changed',
  shellOpenExternal: 'rapp:shell-open-external',
})

const api = Object.freeze({
  catalog: Object.freeze({
    store: () => ipcRenderer.invoke(IPC.catalogStore),
    hub: () => ipcRenderer.invoke(IPC.catalogHub),
    installAgent: (agentId) =>
      ipcRenderer.invoke(IPC.catalogInstallAgent, agentId),
    installSkill: (skill) => ipcRenderer.invoke(IPC.catalogInstallSkill, skill),
  }),
  projects: Object.freeze({
    list: () => ipcRenderer.invoke(IPC.projectsList),
    create: (name) => ipcRenderer.invoke(IPC.projectsCreate, name),
    clone: (implementation) =>
      ipcRenderer.invoke(IPC.projectsClone, implementation),
    reveal: (projectPath) =>
      ipcRenderer.invoke(IPC.projectsReveal, projectPath),
  }),
  brainstem: Object.freeze({
    status: () => ipcRenderer.invoke(IPC.brainstemStatus),
    start: () => ipcRenderer.invoke(IPC.brainstemStart),
    stop: () => ipcRenderer.invoke(IPC.brainstemStop),
    chat: (request) => ipcRenderer.invoke(IPC.brainstemChat, request),
    login: () => ipcRenderer.invoke(IPC.brainstemLogin),
    pollLogin: () => ipcRenderer.invoke(IPC.brainstemLoginPoll),
    onStatus: (listener) => {
      const handler = (_event, status) => listener(status)
      ipcRenderer.on(IPC.brainstemStatusChanged, handler)
      return () => ipcRenderer.removeListener(IPC.brainstemStatusChanged, handler)
    },
  }),
  shell: Object.freeze({
    openExternal: (url) => ipcRenderer.invoke(IPC.shellOpenExternal, url),
  }),
  app: Object.freeze({
    info: () => ipcRenderer.invoke(IPC.appInfo),
  }),
})

contextBridge.exposeInMainWorld('rappDesktop', api)
