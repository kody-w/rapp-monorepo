/**
 * The single source of truth for IPC channel names and the shapes crossing the
 * preload bridge. electron/preload.cjs hand-duplicates the channel strings
 * (CommonJS isolated world) — keep them in sync.
 */

export const IPC = {
  health: "mirror:health",
  chat: "mirror:chat",
  tts: "mirror:tts",
  voiceStatus: "mirror:voice-status",
  transcribe: "mirror:transcribe",
  askMedia: "mirror:ask-media",
  forgeDistill: "forge:distill",
  forgeExport: "forge:export",
  forgeDeploy: "forge:deploy",
  forgeReveal: "forge:reveal",
  sessionsList: "sessions:list",
  sessionsCreate: "sessions:create",
  sessionsUpdate: "sessions:update",
  sessionsDelete: "sessions:delete",
  sessionsChanged: "sessions:changed",
  popout: "mirror:popout",
  openExternal: "mirror:open-external",
  surgeonCreate: "surgeon:create",
  surgeonSend: "surgeon:send",
  surgeonCancel: "surgeon:cancel",
  surgeonClose: "surgeon:close",
  surgeonList: "surgeon:list",
  voiceInstall: "voice:install",
  sttInstall: "stt:install",
  voiceInstallProgress: "voice:install-progress",
  brainLogin: "brain:login",
  brainLoginPoll: "brain:login-poll",
  licenseGet: "license:get",
  licenseActivate: "license:activate",
  /** main -> renderer push channel for live Brain Surgeon events. */
  surgeonEvent: "surgeon:event",
  rehearseStart: "rehearse:start",
  rehearseDecide: "rehearse:decide",
  rehearseStatus: "rehearse:status",
  /** main -> renderer push channel for live rehearsal progress. */
  rehearsalEvent: "rehearse:event",
  engineGet: "mirror:engine-get",
  engineRetry: "mirror:engine-retry",
  brainstemSetUrl: "mirror:brainstem-set-url",
  /** main -> renderer push channel for engine provisioning state. */
  engineState: "mirror:engine-state",
} as const;

/**
 * Live engine (global brainstem) provisioning state, pushed to every window.
 * "unavailable" means the grail installer itself can't provision right now
 * (URL unreachable or serving a refusal tombstone) — distinct from "failed"
 * (the installer ran and broke), because the user's remedy differs.
 */
export interface EngineStateView {
  phase: "checking" | "installing" | "ready" | "failed" | "unavailable";
  /** The brainstem URL the mirror is targeting right now. */
  url: string;
  /** Human-readable reason for failed/unavailable; progress note otherwise. */
  detail?: string;
}

/* ── The Rehearsal: virtual-twin dry-runs (see electron/rehearsal.ts) ── */

/** One entity in the rehearsal's virtual world. */
export interface WorldEntity {
  id: string;
  kind: string;
  name: string;
  state: string;
  detail: string;
}

export interface RehearsalWorld {
  entities: WorldEntity[];
}

/** One concrete data change a simulated step made, engine-validated. */
export interface WorldChange {
  entity: string;
  field: "state" | "detail" | "name";
  before: string;
  after: string;
}

export interface RehearsalStepRecord {
  index: number;
  title: string;
  action: string;
  observation: string;
  status: "ok" | "blocked";
  note?: string;
  changes: WorldChange[];
  /** Model-proposed changes the engine refused (unknown entity, stale `before`). */
  invalid?: string[];
}

export type RehearsalRunState =
  | "seeding"
  | "running"
  | "judging"
  | "awaiting-confirmation"
  | "confirmed"
  | "rejected"
  | "stalled"
  | "error";

export interface RehearsalVerdict {
  complete: boolean;
  summary: string;
  gaps: string[];
}

export interface RehearsalDecision {
  status: "pending" | "confirmed" | "rejected";
  note?: string;
  /** How the human answered: "nod" | "portal" | "voice" | "cli" | "control". */
  method?: string;
  at?: number;
}

/** The persisted rehearsal artifact — always labeled a simulation. */
export interface RehearsalTranscript {
  version: "rehearsal/1";
  runId: string;
  specName: string;
  specHash: string;
  /** The exact spec this run rehearsed (what the hash covers). */
  spec: ForgeSpecView;
  simulated: true;
  engine: { model: string; app: string };
  startedAt: number;
  finishedAt?: number;
  state: RehearsalRunState;
  scenario: string;
  sampleInputs: Record<string, string | number | boolean>;
  world0: RehearsalWorld;
  steps: RehearsalStepRecord[];
  finalWorld: RehearsalWorld | null;
  verdict: RehearsalVerdict | null;
  decision: RehearsalDecision;
  error?: string;
}

export interface RehearsalResult {
  ok: boolean;
  transcript?: RehearsalTranscript;
  error?: string;
}

/** One live rehearsal event streamed to the stage. */
export type RehearsalEvent =
  | { kind: "state"; state: RehearsalRunState }
  | { kind: "seed"; scenario: string; world: RehearsalWorld; sampleInputs: Record<string, string | number | boolean> }
  | { kind: "step"; step: RehearsalStepRecord }
  | { kind: "verdict"; verdict: RehearsalVerdict };

/** One live Brain Surgeon event streamed to the panel. */
export interface SurgeonEventView {
  sessionId: string;
  kind: "status" | "tool" | "report" | "error" | "done";
  text: string;
}

export interface SurgeonSessionView {
  id: string;
  title: string;
  busy: boolean;
}

/** GET /health on the brainstem (the fields the mirror shows). */
export interface BrainstemHealth {
  ok: boolean;
  status?: string;
  version?: string;
  model?: string;
  agents?: string[];
  quarantined?: string[];
  error?: string;
}

/** One conversation turn, in the brainstem's /chat history shape. */
export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

/** POST /chat result (response field is named `response` — rapp-chat). */
export interface ChatResult {
  ok: boolean;
  response?: string;
  agentLogs?: string;
  model?: string;
  error?: string;
}

/** Combined output-voice + input-voice availability for the DO panel. */
export interface VoiceStatus {
  /** VibeVoice service state. */
  vibevoice: "ready" | "loading" | "error" | "off";
  speaker?: string;
  device?: string;
  /** whisper.cpp server reachable (voice input). */
  whisper: boolean;
}

export interface TranscribeResult {
  ok: boolean;
  text?: string;
  error?: string;
}

/**
 * One concurrent conversation (the vBrainstem side-chat pattern). Sessions are
 * stored by the main process (userData/sessions.json) and shared by every
 * window — the big mirror and any popped-out sticky mirrors. Inactive sessions
 * are frozen: nothing runs for them until a window focuses them again.
 */
export interface MirrorSession {
  id: string;
  /** Short label shown in the rail / sticky titlebar (first words of the first ask). */
  title: string;
  createdAt: number;
  updatedAt: number;
  history: ChatTurn[];
  /** The assistant's last display line (rail snippet + sticky resume). */
  lastSaid: string;
}

/** Partial update; id is required, the rest merges over the stored session. */
export interface SessionPatch {
  id: string;
  title?: string;
  history?: ChatTurn[];
  lastSaid?: string;
}

/** A distilled, render-ready automation (see electron/forge.ts). */
export interface ForgeSpecView {
  name: string;
  className: string;
  title: string;
  description: string;
  intent: string;
  steps: { title: string; detail: string }[];
  parameters: { name: string; description: string; type: string; required: boolean }[];
}

export interface ForgeDistillResult {
  ok: boolean;
  spec?: ForgeSpecView;
  error?: string;
}

export interface ForgeExportResult {
  ok: boolean;
  dir?: string;
  agentPath?: string;
  skillPath?: string;
  solutionPath?: string;
  error?: string;
}

export interface ForgeDeployResult {
  ok: boolean;
  path?: string;
  live?: boolean;
  quarantined?: boolean;
  /** Refused by the rehearsal gate — rehearse (or force) first. */
  needsRehearsal?: boolean;
  /** The gate was overridden for this deploy; recorded, never the default. */
  forced?: boolean;
  error?: string;
}

/** A capability an arriving agent can reach for. */
export interface ArrivalFinding {
  severity: "critical" | "warn";
  id: string;
  detail: string;
  line: number;
  evidence: string;
}

/** What the mirror learned about an agent someone handed you. */
export interface ArrivedAgentView {
  ok: boolean;
  origin: "file" | "card";
  card?: {
    ok: boolean;
    verdict: "safe" | "review" | "dangerous" | "invalid";
    className: string;
    name: string;
    description: string;
    parameters: { name: string; description: string }[];
    steps: string[];
    findings: ArrivalFinding[];
    lineCount: number;
    error?: string;
  };
  summary?: string;
  spec?: ForgeSpecView;
  pendingPath?: string;
  dangerous?: boolean;
  /** The card's `rapp://` link, computed in the main process. */
  shareUrl?: string;
  error?: string;
}

export interface AcceptArrivalResult {
  ok: boolean;
  installed?: boolean;
  path?: string;
  verified?: boolean;
  needsRehearsal?: boolean;
  refused?: boolean;
  error?: string;
}

/** Shape exposed on `window.mirror` by the preload bridge. */
export interface MirrorApi {
  /** Optional trusted JPEG frame endpoint for headless/remote camera input. */
  cameraFrameUrl: string;
  /** Optional preferred microphone label substring (wireless mic friendly). */
  preferredMicLabel: string;
  /** Start camera gesture tracking automatically when the mirror mounts. */
  headlessGestures: boolean;
  /** Start always-listening narration automatically (local Whisper only). */
  headlessMic: boolean;
  health(): Promise<BrainstemHealth>;
  chat(userInput: string, history: ChatTurn[], sessionId: string): Promise<ChatResult>;
  /** VibeVoice synthesis; null when the service isn't ready (use system voice). */
  tts(text: string): Promise<ArrayBuffer | null>;
  voiceStatus(): Promise<VoiceStatus>;
  /** 16-kHz mono WAV bytes -> text via the local whisper.cpp server. */
  transcribe(wav: ArrayBuffer): Promise<TranscribeResult>;
  /** Trigger the macOS permission prompt for "camera" | "microphone". */
  askMedia(kind: "camera" | "microphone"): Promise<boolean>;
  /** Distill the observed work into a portable automation spec. */
  forgeDistill(history: ChatTurn[], screenContext: string[], sessionId: string): Promise<ForgeDistillResult>;
  /** Render + write agent.py, SKILL.md, and the Copilot Studio solution zip. */
  forgeExport(spec: ForgeSpecView): Promise<ForgeExportResult>;
  /** Drop the agent.py into the live global brainstem and verify it's live.
   *  Rehearsal-gated; `force` overrides (recorded, never the default). */
  forgeDeploy(spec: ForgeSpecView, force?: boolean): Promise<ForgeDeployResult>;
  /** Reveal an exported artifact in the OS file manager. */
  forgeReveal(path: string): Promise<void>;
  /** All sessions, newest-updated first. */
  listSessions(): Promise<MirrorSession[]>;
  /** Create (and persist) a fresh session; returns it. */
  createSession(): Promise<MirrorSession>;
  /** Merge a patch into a stored session (bumps updatedAt, broadcasts). */
  updateSession(patch: SessionPatch): Promise<MirrorSession | null>;
  deleteSession(id: string): Promise<void>;
  /** Subscribe to store changes from any window; returns unsubscribe. */
  onSessionsChanged(cb: (sessions: MirrorSession[]) => void): () => void;
  /** Pop a session out into its own always-on-top sticky mirror window. */
  popout(sessionId: string): Promise<void>;
  /** Open an http(s) URL in the user's default browser (ticket actions). */
  openExternal(url: string): Promise<void>;
  /** Brain Surgeon: GitHub Copilot agent-mode sessions operating on the brainstem. */
  surgeonCreate(): Promise<{ ok: boolean; id?: string; error?: string }>;
  surgeonSend(id: string, text: string): Promise<{ ok: boolean; error?: string }>;
  surgeonCancel(id: string): Promise<void>;
  surgeonClose(id: string): Promise<void>;
  surgeonList(): Promise<SurgeonSessionView[]>;
  onSurgeonEvent(cb: (ev: SurgeonEventView) => void): () => void;
  /** An agent arrived by AirDrop or a scanned card — inspection only. */
  onAgentArrived(cb: (received: ArrivedAgentView) => void): () => void;
  /** The only door: accept an arrival into the brainstem. */
  acceptArrival(
    spec: ForgeSpecView,
    opts?: { acceptDangerous?: boolean; force?: boolean },
  ): Promise<AcceptArrivalResult>;
  /** One-click VibeVoice install (clone + venv + deps); progress via onVoiceInstallProgress. */
  voiceInstall(): Promise<{ ok: boolean; error?: string }>;
  /** One-click whisper.cpp install (brew + model) — gives the mirror hearing. */
  sttInstall(): Promise<{ ok: boolean; error?: string }>;
  onVoiceInstallProgress(cb: (line: string) => void): () => void;
  /** Fresh-brainstem GitHub device-code login (clickable, no terminal). */
  brainLogin(): Promise<{ ok: boolean; userCode?: string; url?: string; error?: string }>;
  brainLoginPoll(): Promise<{ ok: boolean; status: string }>;
  /** Offline license: state + key activation (Ed25519-verified, no network). */
  licenseGet(): Promise<{ status: "licensed" | "trial" | "expired"; email?: string; plan?: string; trialDaysLeft?: number }>;
  licenseActivate(key: string): Promise<{ status: "licensed" | "trial" | "expired"; email?: string; plan?: string; trialDaysLeft?: number }>;
  /** Run the virtual-twin rehearsal for a spec (progress via onRehearsalEvent). */
  rehearseStart(spec: ForgeSpecView, sessionId: string): Promise<RehearsalResult>;
  /** Countersign (or reject) a rehearsal that reached awaiting-confirmation. */
  rehearseDecide(specName: string, verdict: "confirmed" | "rejected", note?: string, method?: string): Promise<RehearsalResult>;
  rehearseStatus(specName: string): Promise<RehearsalResult>;
  onRehearsalEvent(cb: (ev: RehearsalEvent) => void): () => void;
  /** Current engine provisioning state (for windows that mount mid-install). */
  engineGet(): Promise<EngineStateView>;
  /** Re-run engine provisioning (health check -> install if needed). */
  engineRetry(): Promise<EngineStateView>;
  /** Point the mirror at a brainstem URL (persisted; "" clears). */
  brainstemSetUrl(url: string): Promise<{ ok: boolean; error?: string }>;
  /** Subscribe to engine provisioning state pushes; returns unsubscribe. */
  onEngineState(cb: (state: EngineStateView) => void): () => void;
}

/** A parsed rapp-vui response envelope. */
export interface Envelope {
  /** Full display text (clean — no delimiters). */
  text: string;
  /** The single spoken line, when the model supplied one. */
  spoken: string | null;
  /** HOLO projection: a prompt plus 2–6 options. */
  holo: { prompt?: string; options: { label: string; value?: string }[] } | null;
}

/**
 * Split a raw brainstem `response` into display text, spoken line, and next
 * options, per the rapp-vui protocol — marker order is tolerated:
 *   text |||VOICE||| spoken |||OPTIONS||| a | b | c
 *   text |||VOICE||| spoken |||HOLO||| {"prompt": "...", "options": [...]}
 * `|||OPTIONS|||` is the every-turn quick form (three predicted next requests,
 * pipe-separated, exactly like VOICE is one line); `|||HOLO|||` remains the
 * rich JSON form. Both land in `holo.options` for the UI. Malformed sections
 * degrade to clean text.
 */
export function parseEnvelope(raw: string): Envelope {
  const src = raw ?? "";
  const MARKERS = ["|||VOICE|||", "|||HOLO|||", "|||OPTIONS|||"] as const;
  const found = MARKERS
    .map((m) => ({ m, idx: src.indexOf(m) }))
    .filter((f) => f.idx >= 0)
    .sort((a, b) => a.idx - b.idx);

  const text = (found.length ? src.slice(0, found[0].idx) : src).trim();
  let spoken: string | null = null;
  let holo: Envelope["holo"] = null;

  const clean = (label: string) => label.trim().replace(/^[-•\d.\s]+/, "").slice(0, 80);

  for (let i = 0; i < found.length; i++) {
    const section = src.slice(found[i].idx + found[i].m.length, found[i + 1]?.idx ?? src.length).trim();
    if (found[i].m === "|||VOICE|||") {
      spoken = section || null;
    } else if (found[i].m === "|||HOLO|||") {
      try {
        const parsed = JSON.parse(section);
        if (parsed && Array.isArray(parsed.options)) {
          const options = parsed.options
            .filter((o: unknown): o is { label: string; value?: string } =>
              Boolean(o && typeof (o as { label?: unknown }).label === "string"))
            .slice(0, 6);
          holo = { prompt: typeof parsed.prompt === "string" ? parsed.prompt : undefined, options };
        }
      } catch {
        /* malformed HOLO payload — surface the clean text only */
      }
    } else if (!holo) {
      // |||OPTIONS||| quick form: pipe-separated labels, deduped, max 6
      const seen = new Set<string>();
      const options = section
        .split("|")
        .map(clean)
        .filter((l) => l && !seen.has(l.toLowerCase()) && seen.add(l.toLowerCase()))
        .slice(0, 6)
        .map((label) => ({ label }));
      if (options.length) holo = { options };
    }
  }

  return { text, spoken, holo };
}
