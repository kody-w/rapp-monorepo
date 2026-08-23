import { useState, useEffect, useRef } from 'react'
import type {
  BrainstemChatResponse,
  BrainstemStatus,
  CatalogAgent as Agent,
  CatalogImplementation as Implementation,
  CatalogSkill as Skill,
  ProjectInfo as Project,
} from './desktop-api'
import { ChatRequestLifecycle } from './desktop-api'

type Page = 'home' | 'chat' | 'store' | 'hub' | 'projects' | 'settings'

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agentsUsed?: string[];
}

export default function App() {
  const [page, setPage] = useState<Page>('home')
  const [agents, setAgents] = useState<Agent[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [implementations, setImplementations] = useState<Implementation[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [catalogError, setCatalogError] = useState('')
  const [search, setSearch] = useState('')
  const [showNewProject, setShowNewProject] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')

  const [brainstemStatus, setBrainstemStatus] = useState<BrainstemStatus>({
    running: false,
    port: 7071,
    endpoint: 'http://127.0.0.1:7071/chat',
    managed: false,
    phase: 'checking',
  })
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [sessionGuid, setSessionGuid] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [loginCode, setLoginCode] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const chatLifecycleRef = useRef<ChatRequestLifecycle | null>(null)
  if (!chatLifecycleRef.current) {
    chatLifecycleRef.current = new ChatRequestLifecycle()
  }

  useEffect(() => {
    void loadProjects()
    void checkBrainstemStatus()
    return window.rappDesktop.brainstem.onStatus(setBrainstemStatus)
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  useEffect(() => {
    if (page === 'store') loadStore()
    if (page === 'hub') loadHub()
  }, [page])

  useEffect(() => {
    if (!loginCode) return
    let cancelled = false
    let timer = 0
    const poll = async () => {
      try {
        const status = await window.rappDesktop.brainstem.pollLogin()
        if (cancelled) return
        setBrainstemStatus(status)
        if (status.phase === 'ready') {
          setLoginCode('')
          return
        }
        if (status.phase === 'authentication-failed') {
          setLoginCode('')
          return
        }
      } catch (error) {
        if (!cancelled) {
          setBrainstemStatus(current => ({
            ...current,
            detail: String(error),
          }))
        }
      }
      if (!cancelled) timer = window.setTimeout(poll, 2500)
    }
    timer = window.setTimeout(poll, 1000)
    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [loginCode])

  async function loadStore() {
    setLoading(true)
    setCatalogError('')
    try {
      const manifest = await window.rappDesktop.catalog.store()
      setAgents(manifest.agents)
      setSkills(manifest.skills)
    } catch (e) {
      console.error(e)
      setCatalogError(e instanceof Error ? e.message : String(e))
    }
    setLoading(false)
  }

  async function loadHub() {
    setLoading(true)
    try {
      const manifest = await window.rappDesktop.catalog.hub()
      setImplementations(manifest.implementations)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  async function loadProjects() {
    try {
      const list = await window.rappDesktop.projects.list()
      setProjects(list)
    } catch (e) { console.error(e) }
  }

  async function installAgent(agent: Agent) {
    try {
      const result = await window.rappDesktop.catalog.installAgent(agent.id)
      alert(result.message)
    } catch (e) { alert(`Error: ${e}`) }
  }

  async function installSkill(skill: Skill) {
    try {
      const result = await window.rappDesktop.catalog.installSkill(skill)
      alert(result.message)
    } catch (e) { alert(`Error: ${e}`) }
  }

  async function cloneImpl(impl: Implementation) {
    try {
      const result = await window.rappDesktop.projects.clone(impl)
      alert(result.message)
      if (result.success) await loadProjects()
    } catch (e) { alert(`Error: ${e}`) }
  }

  async function createProject() {
    if (!newProjectName.trim()) return
    try {
      const result = await window.rappDesktop.projects.create(newProjectName)
      if (!result.success) {
        alert(result.message)
        return
      }
      setNewProjectName('')
      setShowNewProject(false)
      await loadProjects()
    } catch (e) { alert(`Error: ${e}`) }
  }

  async function openProject(path: string) {
    await window.rappDesktop.projects.reveal(path)
  }

  async function checkBrainstemStatus() {
    try {
      setBrainstemStatus(await window.rappDesktop.brainstem.status())
    } catch (e) {
      setBrainstemStatus(current => ({
        ...current,
        running: false,
        phase: 'error',
        detail: String(e),
      }))
    }
  }

  async function startBrainstem() {
    try {
      setBrainstemStatus(await window.rappDesktop.brainstem.start())
    } catch (e) {
      alert(`Error starting the Brainstem: ${e}`)
    }
  }

  async function stopBrainstem() {
    try {
      setBrainstemStatus(await window.rappDesktop.brainstem.stop())
    } catch (e) {
      alert(`Error stopping the Brainstem: ${e}`)
    }
  }

  async function startLogin() {
    try {
      const login = await window.rappDesktop.brainstem.login()
      setLoginCode(login.userCode)
    } catch (e) {
      alert(`Error starting GitHub sign-in: ${e}`)
    }
  }

  async function sendMessage() {
    if (!chatInput.trim() || chatLoading) return
    const requestId = crypto.randomUUID()
    const token = chatLifecycleRef.current!.begin(requestId)

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput.trim(),
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      const response: BrainstemChatResponse = await window.rappDesktop.brainstem.chat({
        userInput: userMessage.content,
        requestId,
        sessionId: sessionGuid || undefined,
        conversationHistory: chatMessages.map(m => ({
          role: m.role,
          content: m.content
        }))
      })

      if (!chatLifecycleRef.current!.accepts(token)) return
      if (response.sessionId) {
        setSessionGuid(response.sessionId)
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        agentsUsed: response.agentsUsed
      }

      setChatMessages(prev => [...prev, assistantMessage])
    } catch (e) {
      if (!chatLifecycleRef.current!.accepts(token)) return
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${e}. Make sure the RAPP Brainstem is running.`,
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      if (chatLifecycleRef.current!.finish(token)) {
        setChatLoading(false)
      }
    }
  }

  function clearChat() {
    const activeRequestId = chatLifecycleRef.current!.clear()
    setChatMessages([])
    setSessionGuid('')
    setChatLoading(false)
    if (activeRequestId) {
      void window.rappDesktop.brainstem.cancelChat(activeRequestId)
        .catch(error => console.error('Unable to cancel chat request:', error))
    }
  }

  const filteredAgents = agents.filter(a =>
    a.name.toLowerCase().includes(search.toLowerCase()) ||
    a.description.toLowerCase().includes(search.toLowerCase())
  )
  const filteredSkills = skills.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.description.toLowerCase().includes(search.toLowerCase())
  )
  const filteredImpls = implementations.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase()) ||
    i.description.toLowerCase().includes(search.toLowerCase())
  )
  const brainstemReady = brainstemStatus.phase === 'ready'
  const brainstemNeedsLogin = brainstemStatus.phase === 'authentication-required'
    || brainstemStatus.phase === 'authentication-failed'

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <h1>RAPP</h1>
        </div>
        <nav className="nav">
          <button className={`nav-item ${page === 'home' ? 'active' : ''}`} onClick={() => setPage('home')}>
            <span className="nav-icon">🏠</span> Home
          </button>
          <button className={`nav-item ${page === 'chat' ? 'active' : ''}`} onClick={() => setPage('chat')}>
            <span className="nav-icon">💬</span> Chat
            {brainstemStatus.running && <span className="status-dot online" />}
          </button>
          <button className={`nav-item ${page === 'store' ? 'active' : ''}`} onClick={() => setPage('store')}>
            <span className="nav-icon">📦</span> Store
          </button>
          <button className={`nav-item ${page === 'hub' ? 'active' : ''}`} onClick={() => setPage('hub')}>
            <span className="nav-icon">🌐</span> Hub
          </button>
          <button className={`nav-item ${page === 'projects' ? 'active' : ''}`} onClick={() => setPage('projects')}>
            <span className="nav-icon">📁</span> Projects
          </button>
          <button className={`nav-item ${page === 'settings' ? 'active' : ''}`} onClick={() => setPage('settings')}>
            <span className="nav-icon">⚙️</span> Settings
          </button>
        </nav>
      </aside>

      <main className="main">
        {page === 'home' && (
          <>
            <header className="header"><h2>Welcome to RAPP</h2></header>
            <div className="content">
              <div className="welcome">
                <div className="welcome-icon">🚀</div>
                <h2>Rapid AI Agent Production Pipeline</h2>
                <p>Your secure, local-first AI companion</p>
                <div className="quick-actions">
                  <div className="quick-action" onClick={() => setPage('chat')}>
                    <div className="quick-action-icon">💬</div>
                    <h4>Chat with RAPP</h4>
                    <p>Talk to your agents</p>
                  </div>
                  <div className="quick-action" onClick={() => setPage('store')}>
                    <div className="quick-action-icon">📦</div>
                    <h4>Browse Store</h4>
                    <p>Install agents & skills</p>
                  </div>
                  <div className="quick-action" onClick={() => setPage('hub')}>
                    <div className="quick-action-icon">🌐</div>
                    <h4>Explore Hub</h4>
                    <p>Find implementations</p>
                  </div>
                  <div className="quick-action" onClick={() => { setPage('projects'); setShowNewProject(true) }}>
                    <div className="quick-action-icon">✨</div>
                    <h4>New Project</h4>
                    <p>Start from scratch</p>
                  </div>
                </div>
              </div>
              <div className="stats-row" style={{ justifyContent: 'center', marginTop: '2rem' }}>
                <div className="stat-card">
                  <div className="stat-value">{projects.length}</div>
                  <div className="stat-label">Projects</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{agents.length || '—'}</div>
                  <div className="stat-label">Agents</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{skills.length || '—'}</div>
                  <div className="stat-label">Skills</div>
                </div>
              </div>
            </div>
          </>
        )}

        {page === 'chat' && (
          <>
            <header className="header">
              <h2>Chat with RAPP</h2>
              <div className="header-actions">
                <span className={`status-badge ${brainstemReady ? 'online' : 'offline'}`}>
                  {brainstemStatus.phase === 'authentication-required'
                    ? 'Sign-in Required'
                    : brainstemStatus.phase === 'authentication-failed'
                      ? 'Sign-in Failed'
                    : brainstemReady
                      ? 'Brainstem Ready'
                      : 'Brainstem Offline'}
                </span>
                {brainstemNeedsLogin ? (
                  <button className="btn btn-primary" onClick={startLogin}>
                    {brainstemStatus.phase === 'authentication-failed' ? 'Retry sign-in' : 'Sign in'}
                  </button>
                ) : brainstemStatus.running && brainstemStatus.managed ? (
                  <button className="btn btn-secondary" onClick={stopBrainstem}>Stop</button>
                ) : (
                  !brainstemStatus.running && (
                    <button className="btn btn-primary" onClick={startBrainstem}>Wake Brainstem</button>
                  )
                )}
                {loginCode && (
                  <span className="status-badge">GitHub code: {loginCode}</span>
                )}
                <button className="btn btn-secondary" onClick={clearChat}>Clear Chat</button>
              </div>
            </header>
            <div className="chat-container">
              <div className="chat-messages">
                {chatMessages.length === 0 ? (
                  <div className="chat-empty">
                    <div className="chat-empty-icon">💬</div>
                    <h3>Start a Conversation</h3>
                    <p>
                      {brainstemReady
                        ? 'Type a message below to chat with your RAPP agents'
                        : brainstemNeedsLogin
                          ? 'Sign in with GitHub above to activate the Brainstem'
                          : 'Wake the Brainstem above to begin'}
                    </p>
                  </div>
                ) : (
                  chatMessages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role}`}>
                      <div className="chat-message-header">
                        <span className="chat-avatar">{msg.role === 'user' ? '👤' : '🤖'}</span>
                        <span className="chat-sender">{msg.role === 'user' ? 'You' : 'RAPP'}</span>
                        <span className="chat-time">
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <div className="chat-message-content">{msg.content}</div>
                      {msg.agentsUsed && msg.agentsUsed.length > 0 && (
                        <div className="chat-agents-used">
                          Agents: {msg.agentsUsed.join(', ')}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {chatLoading && (
                  <div className="chat-message assistant">
                    <div className="chat-message-header">
                      <span className="chat-avatar">🤖</span>
                      <span className="chat-sender">RAPP</span>
                    </div>
                    <div className="chat-message-content typing">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              <div className="chat-input-container">
                <input
                  className="chat-input"
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder={brainstemReady ? "Type your message..." : "Activate the Brainstem to chat..."}
                  disabled={!brainstemReady || chatLoading}
                />
                <button
                  className="btn btn-primary chat-send"
                  onClick={sendMessage}
                  disabled={!brainstemReady || chatLoading || !chatInput.trim()}
                >
                  Send
                </button>
              </div>
            </div>
          </>
        )}

        {page === 'store' && (
          <>
            <header className="header">
              <h2>RAPP Store</h2>
              <div className="search-box">
                <span className="search-icon">🔍</span>
                <input placeholder="Search agents & skills..." value={search} onChange={e => setSearch(e.target.value)} />
              </div>
            </header>
            <div className="content">
              {catalogError && (
                <div className="error">Store unavailable: {catalogError}</div>
              )}
              {loading ? (
                <div className="loading"><div className="spinner" /> Loading...</div>
              ) : (
                <>
                  <h3 style={{ marginBottom: '1rem' }}>Agents ({filteredAgents.length})</h3>
                  <div className="card-grid">
                    {filteredAgents.map(agent => (
                      <div key={agent.id} className="card">
                        <div className="card-header">
                          <span className="card-icon">{agent.icon || '🤖'}</span>
                          <div>
                            <div className="card-title">{agent.name}</div>
                            <span className="card-badge badge-agent">Agent</span>
                          </div>
                        </div>
                        <p className="card-desc">{agent.description}</p>
                        <div className="card-tags">
                          {agent.features?.slice(0, 3).map((f, i) => <span key={i} className="tag">{f}</span>)}
                        </div>
                        <div className="card-actions">
                          <button className="btn btn-primary" onClick={() => installAgent(agent)}>Install</button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <h3 style={{ margin: '2rem 0 1rem' }}>Skills ({filteredSkills.length})</h3>
                  <div className="card-grid">
                    {filteredSkills.map(skill => (
                      <div key={skill.id} className="card">
                        <div className="card-header">
                          <span className="card-icon">{skill.icon || '✨'}</span>
                          <div>
                            <div className="card-title">{skill.name}</div>
                            <span className="card-badge badge-skill">Skill</span>
                          </div>
                        </div>
                        <p className="card-desc">{skill.description}</p>
                        <div className="card-tags">
                          {skill.features?.slice(0, 3).map((f, i) => <span key={i} className="tag">{f}</span>)}
                        </div>
                        <div className="card-actions">
                          <button className="btn btn-primary" onClick={() => installSkill(skill)}>Install</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </>
        )}

        {page === 'hub' && (
          <>
            <header className="header">
              <h2>RAPP Hub</h2>
              <div className="search-box">
                <span className="search-icon">🔍</span>
                <input placeholder="Search implementations..." value={search} onChange={e => setSearch(e.target.value)} />
              </div>
            </header>
            <div className="content">
              {loading ? (
                <div className="loading"><div className="spinner" /> Loading...</div>
              ) : (
                <div className="card-grid">
                  {filteredImpls.map(impl => (
                    <div key={impl.id} className="card">
                      <div className="card-header">
                        <span className="card-icon">{impl.icon || '🏠'}</span>
                        <div>
                          <div className="card-title">{impl.name}</div>
                          <span className="card-badge badge-impl">Implementation</span>
                        </div>
                      </div>
                      <p className="card-desc">{impl.description}</p>
                      <div className="card-tags">
                        {impl.features?.slice(0, 3).map((f, i) => <span key={i} className="tag">{f}</span>)}
                      </div>
                      <div className="card-actions">
                        <button className="btn btn-primary" onClick={() => cloneImpl(impl)}>Clone</button>
                        <a href={impl.repo} target="_blank" rel="noopener" className="btn btn-secondary">View</a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {page === 'projects' && (
          <>
            <header className="header">
              <h2>My Projects</h2>
              <button className="btn btn-primary" onClick={() => setShowNewProject(true)}>+ New Project</button>
            </header>
            <div className="content">
              {projects.length === 0 ? (
                <div className="welcome">
                  <div className="welcome-icon">📁</div>
                  <h2>No Projects Yet</h2>
                  <p>Create a new project or clone one from RAPP Hub</p>
                  <div className="quick-actions">
                    <div className="quick-action" onClick={() => setShowNewProject(true)}>
                      <div className="quick-action-icon">✨</div>
                      <h4>New Project</h4>
                    </div>
                    <div className="quick-action" onClick={() => setPage('hub')}>
                      <div className="quick-action-icon">🌐</div>
                      <h4>Browse Hub</h4>
                    </div>
                  </div>
                </div>
              ) : (
                projects.map(project => (
                  <div key={project.name} className="project-item">
                    <div className="project-info">
                      <h3>{project.name}</h3>
                      <p>{project.path}</p>
                    </div>
                    <div className="card-actions">
                      <button className="btn btn-secondary" onClick={() => openProject(project.path)}>Open</button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}

        {page === 'settings' && (
          <>
            <header className="header"><h2>Settings</h2></header>
            <div className="content">
              <div className="card" style={{ maxWidth: 500, marginBottom: '1rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>RAPP Brainstem</h3>
                <div className="settings-row">
                  <div>
                    <strong>Status:</strong>{' '}
                    <span className={`status-badge ${brainstemReady ? 'online' : 'offline'}`}>
                      {brainstemStatus.phase === 'authentication-required'
                        ? 'Sign-in Required'
                        : brainstemStatus.phase === 'authentication-failed'
                          ? 'Sign-in Failed'
                        : brainstemStatus.phase === 'error'
                          ? 'Unavailable'
                        : brainstemReady
                          ? 'Ready'
                          : 'Offline'}
                    </span>
                  </div>
                  {brainstemReady && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Endpoint: {brainstemStatus.endpoint}
                    </div>
                  )}
                  {brainstemStatus.detail && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      {brainstemStatus.detail}
                    </div>
                  )}
                </div>
                <div className="card-actions" style={{ marginTop: '1rem' }}>
                  {brainstemNeedsLogin ? (
                    <button className="btn btn-primary" onClick={startLogin}>
                      {brainstemStatus.phase === 'authentication-failed'
                        ? 'Retry GitHub sign-in'
                        : 'Sign in with GitHub'}
                    </button>
                  ) : brainstemStatus.running && brainstemStatus.managed ? (
                    <button className="btn btn-secondary" onClick={stopBrainstem}>Stop bundled Brainstem</button>
                  ) : (
                    !brainstemStatus.running && (
                      <button className="btn btn-primary" onClick={startBrainstem}>Wake Brainstem</button>
                    )
                  )}
                  {loginCode && (
                    <span className="status-badge">GitHub code: {loginCode}</span>
                  )}
                  <button className="btn btn-secondary" onClick={checkBrainstemStatus}>Refresh Status</button>
                </div>
              </div>

              <div className="card" style={{ maxWidth: 500 }}>
                <h3 style={{ marginBottom: '1rem' }}>RAPP Configuration</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                  Configure your RAPP installation and Azure deployment.
                </p>
                <a href="https://github.com/kody-w/rapp-installer" target="_blank" rel="noopener" className="btn btn-primary">
                  View Installer Docs
                </a>
              </div>
            </div>
          </>
        )}
      </main>

      {showNewProject && (
        <div className="modal-overlay" onClick={() => setShowNewProject(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>New Project</h3>
              <button className="modal-close" onClick={() => setShowNewProject(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="input-group">
                <label>Project Name</label>
                <input value={newProjectName} onChange={e => setNewProjectName(e.target.value)} placeholder="my-rapp-project" />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowNewProject(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={createProject}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
