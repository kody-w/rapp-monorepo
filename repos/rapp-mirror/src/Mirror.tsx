import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  parseEnvelope,
  type BrainstemHealth,
  type ChatTurn,
  type EngineStateView,
  type ForgeDeployResult,
  type ForgeExportResult,
  type ForgeSpecView,
  type VoiceStatus,
} from "../common/ipc.ts";
import { startNarration, startRecording, type NarrationSession, type Recording } from "./audio.ts";
import { renderMd } from "./md.tsx";
import { ArrivalCard } from "./ArrivalCard.tsx";
import Rehearsal, { emptyRehearsal, type RehearsalView } from "./Rehearsal.tsx";
import Surgeon from "./Surgeon.tsx";
import { startScreenWatch, type ScreenWatch } from "./screenwatch.ts";
import {
  DEFAULT_GESTURE_COMMANDS,
  parseGestureMapping,
  validGestureMap,
  type CommandGesture,
  type GestureCommand,
  type GestureCommandMap,
} from "../common/gestures.ts";
import {
  startVision,
  type HandGesture,
  type VisionSession,
} from "./vision.ts";

/**
 * The mirror, in the rapp-vui design language: a living central orb you hold
 * to talk, and portals — the AI's injected options — orbiting it, selectable
 * hands-free by head-pointing + dwell, nod, or gesture. Monkey SEE flows in
 * (voice, camera, screen); monkey DO flows out (spoken VibeVoice answers,
 * portals, forged automations). `window.mirrorDebug` exposes every action for
 * DevTools / CDP / mirrorctl autonomy.
 */

type Phase = "idle" | "listening" | "thinking" | "speaking";

const FORGE_INTENT = /\b(make|turn|forge|convert)\b.*\b(automation|agent|skill)\b/i;
const REFLECT_INTENT = /^(?:reflect on|keep (?:working on|doing)|loop on)\s+(.+)/i;
const DWELL_MS = 3000;
const PINCH_HOLD_MS = 3000;
const REFLECT_DELAY_MS = 15000;
const REFLECT_MAX_TURNS = 12;
const REFLECT_MAX_ACTIVE = 3;
const GESTURE_STORAGE_KEY = "rapp-mirror.gesture-commands.v1";
const GESTURE_APPROVAL_MS = 15_000;

function loadGestureCommands(): GestureCommandMap {
  try {
    const parsed: unknown = JSON.parse(
      localStorage.getItem(GESTURE_STORAGE_KEY) || "null",
    );
    if (validGestureMap(parsed)) return parsed;
  } catch {
    // Fall through to the bounded defaults.
  }
  return structuredClone(DEFAULT_GESTURE_COMMANDS);
}

/** rapp-vui response protocol, requested per turn: VOICE is the only thing
 *  spoken aloud, and EVERY turn ends with three predicted next options that
 *  become the user's orbs — the mind-reading loop. */
const ENVELOPE_HINT =
  "\n\n[mirror voice protocol] End EVERY reply with these blocks, in order:\n" +
  "|||VOICE||| one short natural spoken line (under 25 words, no markdown, no URLs) — it is read aloud by text-to-speech.\n" +
  "|||OPTIONS||| exactly THREE short likely NEXT requests from the user's perspective, separated by | " +
  "(e.g. |||OPTIONS|||Show me more like this | Make this an automation | What changed today). " +
  "Predict what THIS user most wants next — use everything you remember about their preferences and habits; " +
  "these become tappable orbs, so make at least one of them the thing they'd have typed anyway. " +
  'For rich choices you may use |||HOLO|||{"prompt":"...","options":[{"label":"...","value":"..."}]} instead of OPTIONS.';
const STARTERS = [
  { label: "What can you do" },
  { label: "Show me a task" },
  { label: "What is RAPP" },
];
/** Portal colors — in café mode these become the ONLY words the mirror hears. */
const PORTAL_COLORS = [
  { name: "green", css: "#34d399" },
  { name: "blue", css: "#3b82f6" },
  { name: "purple", css: "#a855f7" },
  { name: "orange", css: "#fb923c" },
  { name: "pink", css: "#f472b6" },
  { name: "teal", css: "#2dd4bf" },
];

let sessionId =
  localStorage.getItem("mirror.session") || `mirror-${Math.random().toString(36).slice(2, 10)}`;
localStorage.setItem("mirror.session", sessionId);

interface Exchange {
  u: string;
  a: string;
}

/** A portal dragged out of the orbit: a persistent chip with its own
 *  background /chat session (the vbrainstem herd grammar — 2+ chips
 *  auto-organize into the herd rail). */
interface DetachedChat {
  id: string;
  label: string;
  session: string;
  expanded: boolean;
  busy: boolean;
  msgs: Exchange[];
}

/** A reflection: a sticky standing task that loops with the brainstem in the
 *  background (the vbrainstem Coordinator-twin pattern) so the user doesn't
 *  have to keep driving each turn. */
interface Reflection {
  id: string;
  goal: string;
  status: "running" | "paused" | "done";
  turns: number;
  note: string;
}

export default function Mirror() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [asleep, setAsleep] = useState(false);
  const [muted, setMuted] = useState(false);
  const [prompt, setPrompt] = useState("Where to?");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [health, setHealth] = useState<BrainstemHealth | null>(null);
  const [voice, setVoice] = useState<VoiceStatus | null>(null);
  const [toast, setToast] = useState("");
  const [portals, setPortals] = useState<{ label: string; value?: string }[]>(STARTERS);
  const [turn, setTurn] = useState(0);
  const [hot, setHot] = useState(-1);
  const [dwell, setDwell] = useState(0);
  const [camOn, setCamOn] = useState(false);
  const [camState, setCamState] = useState("");
  const [scrOn, setScrOn] = useState(false);
  const [scrState, setScrState] = useState("off");
  const [seenParts, setSeenParts] = useState("");
  const [context, setContext] = useState("");
  const [agentLog, setAgentLog] = useState("");
  const [showStatus, setShowStatus] = useState(false);
  const [gestureCommands, setGestureCommands] =
    useState<GestureCommandMap>(loadGestureCommands);
  const gestureCommandsRef = useRef(gestureCommands);
  gestureCommandsRef.current = gestureCommands;
  const pendingGestureRef = useRef<{
    gesture: CommandGesture;
    command: GestureCommand;
    expiresAt: number;
  } | null>(null);
  const [chatOpen, setChatOpen] = useState(true);
  const [surgeonOpen, setSurgeonOpen] = useState(false);
  const [surgeonWide, setSurgeonWide] = useState(false);
  const [surgeonCards, setSurgeonCards] = useState(0);
  const onSurgeonLayout = useCallback((wide: boolean, cards: number) => {
    setSurgeonWide(wide);
    setSurgeonCards(cards);
  }, []);
  /** The dock's width follows the herd: one pane never needs the whole screen. */
  const herdActive = surgeonWide && surgeonCards >= 2;
  const dockWnum = !surgeonOpen
    ? 0
    : !herdActive
      ? Math.min(500, window.innerWidth * 0.44)
      : surgeonCards === 2
        ? Math.min(840, window.innerWidth - 560)
        : Math.min(1180, window.innerWidth - 560);
  const ldockWnum = chatOpen ? Math.min(420, window.innerWidth * 0.3) : 0;
  /** Narrow stage = the phone layout: vertical flow, option pills, no orbit. */
  const narrowMid = window.innerWidth - dockWnum - ldockWnum < 880;
  const wasNarrow = useRef(narrowMid);
  useEffect(() => {
    if (narrowMid && !wasNarrow.current) setChatOpen(false); // phone: mirror first
    wasNarrow.current = narrowMid;
  }, [narrowMid]);
  const dockCss = !surgeonOpen
    ? "0px"
    : !herdActive
      ? "min(500px, 44vw)"
      : surgeonCards === 2
        ? "min(840px, calc(100vw - 560px))"
        : "min(1180px, calc(100vw - 560px))";
  /* draggable previews (webcam / screen): grab and place anywhere; persists */
  const loadPos = (key: string): { x: number; y: number } | null => {
    try {
      const v = localStorage.getItem(key);
      return v ? (JSON.parse(v) as { x: number; y: number }) : null;
    } catch {
      return null;
    }
  };
  const [camPos, setCamPos] = useState<{ x: number; y: number } | null>(() => loadPos("mirror.campos"));
  const [scrPos, setScrPos] = useState<{ x: number; y: number } | null>(() => loadPos("mirror.scrpos"));
  const dragPreview = useCallback(
    (key: string, set: (p: { x: number; y: number }) => void) =>
      (e: React.PointerEvent<HTMLVideoElement>) => {
        const el = e.currentTarget;
        const host = el.parentElement!;
        const start = el.getBoundingClientRect();
        const hostBox = host.getBoundingClientRect();
        const dx = e.clientX - start.left;
        const dy = e.clientY - start.top;
        el.setPointerCapture(e.pointerId);
        let last = { x: start.left - hostBox.left, y: start.top - hostBox.top };
        const move = (ev: PointerEvent) => {
          last = {
            x: Math.max(4, Math.min(hostBox.width - start.width - 4, ev.clientX - hostBox.left - dx)),
            y: Math.max(4, Math.min(hostBox.height - start.height - 4, ev.clientY - hostBox.top - dy)),
          };
          set(last);
        };
        const up = () => {
          localStorage.setItem(key, JSON.stringify(last));
          removeEventListener("pointermove", move);
          removeEventListener("pointerup", up);
        };
        addEventListener("pointermove", move);
        addEventListener("pointerup", up);
      },
    [],
  );
  const posStyle = (p: { x: number; y: number } | null) =>
    p ? { left: p.x, top: p.y, right: "auto", bottom: "auto" } : undefined;

  const [license, setLicense] = useState<{ status: string; email?: string; plan?: string; trialDaysLeft?: number } | null>(null);
  useEffect(() => {
    void window.mirror.licenseGet().then(setLicense);
  }, []);
  const [forge, setForge] = useState<{
    phase: "hidden" | "distilling" | "ready" | "busy" | "error";
    spec?: ForgeSpecView;
    artifacts?: ForgeExportResult;
    deploy?: ForgeDeployResult;
    error?: string;
  }>({ phase: "hidden" });

  const [narrating, setNarrating] = useState(false);
  const [speechLive, setSpeechLive] = useState(false);

  const historyRef = useRef<ChatTurn[]>([]);
  const screenCtxRef = useRef<string[]>([]);
  const visionRef = useRef<VisionSession | null>(null);
  const screenRef = useRef<ScreenWatch | null>(null);
  const recordingRef = useRef<Recording | null>(null);
  const narrationRef = useRef<NarrationSession | null>(null);
  const routeTranscriptRef = useRef<(text: string) => void>(() => undefined);
  const phaseRef = useRef<Phase>("idle");
  /** Gaze-dwell on the orb calls this (set once toggleNarrate exists). */
  const toggleNarrateRef = useRef<() => void>(() => undefined);
  /** Live audio levels feeding the voice wave: {v: 0..1, t: performance.now()}. */
  const micLevelRef = useRef({ v: 0, t: 0 });
  const aiLevelRef = useRef({ v: 0, t: 0 });
  const playbackCtxRef = useRef<AudioContext | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const camVideoRef = useRef<HTMLVideoElement>(null);
  const scrVideoRef = useRef<HTMLVideoElement>(null);
  const composerRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mutedRef = useRef(muted);
  mutedRef.current = muted;
  phaseRef.current = phase;
  const portalsRef = useRef(portals);
  portalsRef.current = portals;
  const hotRef = useRef(hot);
  hotRef.current = hot;
  const dwellRef = useRef<{ idx: number; since: number }>({ idx: -1, since: 0 });

  const alive = exchanges.length > 0 || phase !== "idle" || camOn;

  const notify = useCallback((m: string) => {
    setToast(m);
    setTimeout(() => setToast(""), 4200);
  }, []);

  const [voiceInstallLine, setVoiceInstallLine] = useState("");
  const [voiceInstalling, setVoiceInstalling] = useState(false);
  useEffect(() => window.mirror.onVoiceInstallProgress(setVoiceInstallLine), []);
  const installVibeVoice = useCallback(async () => {
    setVoiceInstalling(true);
    notify("Installing VibeVoice — a few GB, one time. The mirror keeps working meanwhile.");
    const r = await window.mirror.voiceInstall();
    setVoiceInstalling(false);
    notify(r.ok ? "VibeVoice installed — the voice switches over as soon as the model loads." : `VibeVoice install failed: ${r.error}`);
    setVoice(await window.mirror.voiceStatus());
  }, [notify]);

  const [sttInstalling, setSttInstalling] = useState(false);
  const installHearing = useCallback(async () => {
    setSttInstalling(true);
    notify("Installing hearing — whisper.cpp plus a ~466 MB model, one time.");
    const r = await window.mirror.sttInstall();
    setSttInstalling(false);
    notify(r.ok ? "Hearing installed — tap the orb and just talk." : `Hearing install failed: ${r.error}`);
    setVoice(await window.mirror.voiceStatus());
  }, [notify]);

  /* fresh brainstem: clickable GitHub device-code login (no terminal) */
  const [brainLogin, setBrainLogin] = useState<{ code: string; url: string } | null>(null);
  const connectBrainstem = useCallback(async () => {
    const r = await window.mirror.brainLogin();
    if (!r.ok || !r.userCode) {
      notify(`Couldn't start GitHub login: ${r.error ?? "unknown"}`);
      return;
    }
    setBrainLogin({ code: r.userCode, url: r.url || "https://github.com/login/device" });
    void window.mirror.openExternal(r.url || "https://github.com/login/device");
    const poll = async () => {
      const p = await window.mirror.brainLoginPoll();
      if (p.ok) {
        setBrainLogin(null);
        setHealth(await window.mirror.health());
        notify("Your brainstem is connected to GitHub Copilot.");
        return;
      }
      setTimeout(() => void poll(), 4000);
    };
    void poll();
  }, [notify]);


  /* ── status polling ────────────────────────────────────────────────── */
  useEffect(() => {
    const poll = async () => {
      setHealth(await window.mirror.health());
      setVoice(await window.mirror.voiceStatus());
    };
    void poll();
    const t = setInterval(() => void poll(), 12000);
    return () => clearInterval(t);
  }, []);

  /* ── engine provisioning state (never an eternal "connecting…") ────── */
  const [engine, setEngine] = useState<EngineStateView | null>(null);
  useEffect(() => {
    void window.mirror.engineGet().then(setEngine);
    return window.mirror.onEngineState(setEngine);
  }, []);
  const retryEngine = useCallback(() => {
    setEngine((e) => (e ? { ...e, phase: "checking", detail: undefined } : e));
    void window.mirror.engineRetry().then(setEngine);
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [exchanges]);

  /* ── voice OUT ─────────────────────────────────────────────────────── */
  const hush = useCallback(() => {
    audioRef.current?.pause();
    audioRef.current = null;
    setPhase((p) => (p === "speaking" ? "idle" : p));
  }, []);

  const gestureTone = useCallback(
    (kind: "detected" | "approved" | "rejected") => {
      try {
        const audio = new AudioContext();
        const oscillator = audio.createOscillator();
        const gain = audio.createGain();
        oscillator.type = "sine";
        oscillator.frequency.value =
          kind === "approved" ? 880 : kind === "rejected" ? 220 : 660;
        gain.gain.setValueAtTime(0.0001, audio.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.16, audio.currentTime + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + 0.16);
        oscillator.connect(gain).connect(audio.destination);
        oscillator.start();
        oscillator.stop(audio.currentTime + 0.18);
        oscillator.onended = () => void audio.close();
      } catch {
        // Spoken confirmation still provides feedback if WebAudio is unavailable.
      }
    },
    [],
  );

  const speak = useCallback(
    async (text: string) => {
      if (!text || mutedRef.current) return;
      const line = text.length > 600 ? text.slice(0, 600) + "…" : text;
      // The mirror's voice IS VibeVoice — without it, captions only.
      const wav = await window.mirror.tts(line).catch(() => null);
      if (!wav) return;
      hush();
      setPhase("speaking");
      await new Promise<void>((res) => {
        const audio = new Audio(URL.createObjectURL(new Blob([wav], { type: "audio/wav" })));
        audioRef.current = audio;
        // feed the AI side of the voice wave with the REAL playback signal
        let meter: ReturnType<typeof setInterval> | null = null;
        try {
          const actx = (playbackCtxRef.current ??= new AudioContext());
          void actx.resume().catch(() => undefined);
          const src = actx.createMediaElementSource(audio);
          const an = actx.createAnalyser();
          an.fftSize = 512;
          src.connect(an);
          an.connect(actx.destination);
          const buf = new Float32Array(an.fftSize);
          meter = setInterval(() => {
            an.getFloatTimeDomainData(buf);
            let sum = 0;
            for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
            aiLevelRef.current = { v: Math.min(1, Math.sqrt(sum / buf.length) * 3.2), t: performance.now() };
          }, 50);
        } catch {
          /* metering is decoration — playback continues without it */
        }
        const done = () => {
          if (meter) clearInterval(meter);
          res();
        };
        audio.onended = done;
        audio.onerror = done;
        void audio.play().catch(done);
      });
      setPhase((p) => (p === "speaking" ? "idle" : p));
    },
    [hush],
  );

  /* ── detached chats: drag a portal out → persistent AI chip (herd) ──── */
  const [detached, setDetached] = useState<DetachedChat[]>([]);
  const detachedRef = useRef(detached);
  detachedRef.current = detached;

  const chipAsk = useCallback(async (chipId: string, text: string) => {
    const chip = detachedRef.current.find((c) => c.id === chipId);
    if (!chip || !text.trim()) return;
    setDetached((ds) => ds.map((c) => (c.id === chipId ? { ...c, busy: true, msgs: [...c.msgs, { u: text, a: "…" }] } : c)));
    const prior: ChatTurn[] = chip.msgs.flatMap((m) => [
      { role: "user" as const, content: m.u },
      { role: "assistant" as const, content: m.a },
    ]);
    const r = await window.mirror.chat(text, prior.slice(-8), chip.session);
    const answer = r.ok ? parseEnvelope(r.response ?? "").text : `(no answer — ${r.error})`;
    setDetached((ds) =>
      ds.map((c) => (c.id === chipId ? { ...c, busy: false, msgs: [...c.msgs.slice(0, -1), { u: text, a: answer }] } : c)),
    );
  }, []);

  /** Drop a portal onto the Brain Surgeon board: it becomes a brainstem chat
   *  card living IN the dock (that's the point of the drag). */
  const detachPortal = useCallback(
    (i: number) => {
      const o = portalsRef.current[i];
      if (!o) return;
      const id = Math.random().toString(36).slice(2, 8);
      setPortals((ps) => ps.filter((_, j) => j !== i));
      setHot(-1);
      setSurgeonOpen(true);
      setDetached((ds) => [
        { id, label: o.label, session: `chip-${id}`, expanded: false, busy: false, msgs: [] },
        ...ds,
      ]);
      void chipAsk(id, o.value || o.label);
    },
    [chipAsk],
  );

  /* drag-out: a ghost chip follows the pointer; dropping it over the Brain
     Surgeon (the dock, or the right edge when closed) lands it on the board */
  const [ghost, setGhost] = useState<{ label: string; x: number; y: number; ready: boolean } | null>(null);
  const dragRef = useRef<{ idx: number; x: number; y: number; live: boolean } | null>(null);
  const onPortalPointerDown = useCallback((i: number, e: React.PointerEvent) => {
    dragRef.current = { idx: i, x: e.clientX, y: e.clientY, live: false };
  }, []);
  useEffect(() => {
    const dropZoneX = () =>
      surgeonOpen ? window.innerWidth - Math.min(500, window.innerWidth * 0.44) : window.innerWidth - 150;
    const move = (e: PointerEvent) => {
      const d = dragRef.current;
      if (!d) return;
      if (!d.live && Math.hypot(e.clientX - d.x, e.clientY - d.y) > 60) d.live = true;
      if (d.live) {
        const o = portalsRef.current[d.idx];
        setGhost(o ? { label: o.label, x: e.clientX, y: e.clientY, ready: e.clientX > dropZoneX() } : null);
      }
    };
    const up = (e: PointerEvent) => {
      const d = dragRef.current;
      dragRef.current = null;
      setGhost(null);
      if (d?.live && e.clientX > dropZoneX()) detachPortal(d.idx);
    };
    addEventListener("pointermove", move);
    addEventListener("pointerup", up);
    return () => {
      removeEventListener("pointermove", move);
      removeEventListener("pointerup", up);
    };
  }, [detachPortal, surgeonOpen]);

  /* ── reflections: sticky loops with the brainstem ──────────────────── */
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const reflectionsRef = useRef(reflections);
  reflectionsRef.current = reflections;

  const reflect = useCallback(
    (goal: string) => {
      const active = reflectionsRef.current.filter((r) => r.status === "running").length;
      if (active >= REFLECT_MAX_ACTIVE) {
        notify(`Max ${REFLECT_MAX_ACTIVE} reflections at once — dismiss one first.`);
        return;
      }
      const id = Math.random().toString(36).slice(2, 8);
      setReflections((rs) => [...rs, { id, goal, status: "running", turns: 0, note: "starting…" }]);
      const session = `reflect-${id}`;
      const history: ChatTurn[] = [];
      const turnOnce = async () => {
        const current = reflectionsRef.current.find((r) => r.id === id);
        if (!current || current.status !== "running") {
          if (current?.status === "paused") setTimeout(() => void turnOnce(), REFLECT_DELAY_MS);
          return;
        }
        if (current.turns >= REFLECT_MAX_TURNS) {
          setReflections((rs) => rs.map((r) => (r.id === id ? { ...r, status: "done", note: r.note + " (turn limit)" } : r)));
          return;
        }
        const r = await window.mirror.chat(
          `[reflection loop — turn ${current.turns + 1}] Standing task: ${goal}\n` +
            "Work this task one step further RIGHT NOW using your agents/tools. Reply with a one-or-two sentence progress note. " +
            "When the task is genuinely complete, start your reply with DONE:",
          history.slice(-8),
          session,
        );
        const note = r.ok ? (r.response ?? "").trim() : `error: ${r.error}`;
        if (r.ok) {
          history.push({ role: "user", content: `continue: ${goal}` }, { role: "assistant", content: note });
        }
        const done = /^DONE:/i.test(note);
        setReflections((rs) =>
          rs.map((x) =>
            x.id === id
              ? { ...x, turns: x.turns + 1, note: note.replace(/^DONE:\s*/i, "").slice(0, 200), status: done ? "done" : x.status }
              : x,
          ),
        );
        if (done) {
          void speak(`A reflection finished: ${goal.slice(0, 60)}`);
          return;
        }
        setTimeout(() => void turnOnce(), REFLECT_DELAY_MS);
      };
      void turnOnce();
    },
    [notify, speak],
  );

  /* ── the rehearsal: the twin runs the job virtually before deploy ──── */
  const [rehearsal, setRehearsal] = useState<RehearsalView>(emptyRehearsal);
  /** True only while the one question is on stage: "fully done?" */
  const rehearsalAwaitRef = useRef(false);
  const rehearsalSpecRef = useRef<ForgeSpecView | null>(null);
  const finishRehearsalRef = useRef<(v: "confirmed" | "rejected", m: string) => void>(() => undefined);

  useEffect(
    () =>
      window.mirror.onRehearsalEvent((ev) => {
        setRehearsal((r) => {
          if (ev.kind === "state") return { ...r, state: ev.state };
          if (ev.kind === "seed")
            return { ...r, scenario: ev.scenario, world: ev.world, sampleInputs: ev.sampleInputs };
          if (ev.kind === "step")
            return {
              ...r,
              steps: [...r.steps.filter((s) => s.index !== ev.step.index), ev.step].sort((a, b) => a.index - b.index),
            };
          return { ...r, verdict: ev.verdict };
        });
        // The orb narrates the twin's run as it happens.
        if (ev.kind === "seed") void speak(ev.scenario);
        else if (ev.kind === "step") void speak(ev.step.observation || ev.step.action);
      }),
    [speak],
  );

  const startRehearsal = useCallback(
    async (spec: ForgeSpecView) => {
      rehearsalSpecRef.current = spec;
      rehearsalAwaitRef.current = false;
      setRehearsal({ ...emptyRehearsal, open: true, running: true, state: "seeding", totalSteps: spec.steps.length });
      const r = await window.mirror.rehearseStart(spec, sessionId);
      setRehearsal((prev) => ({
        ...prev,
        running: false,
        state: r.transcript?.state ?? "error",
        scenario: r.transcript?.scenario || prev.scenario,
        world: r.transcript?.finalWorld ?? prev.world,
        steps: r.transcript?.steps ?? prev.steps,
        verdict: r.transcript?.verdict ?? prev.verdict,
        transcript: r.transcript ?? null,
        error: r.error || r.transcript?.error || "",
      }));
      if (r.ok && r.transcript) {
        rehearsalAwaitRef.current = true;
        setPortals([
          { label: "Fully done", value: "__rehearsal:confirm" },
          { label: "Not right", value: "__rehearsal:reject" },
        ]);
        setHot(-1);
        setPrompt("Did it complete the job?");
        const v = r.transcript.verdict;
        void speak(
          (v?.complete
            ? `In rehearsal the whole job finished. ${v.summary} `
            : `The rehearsal finished with gaps. ${v?.summary ?? ""} `) +
            "Did this complete the job — fully done?",
        );
      } else {
        void speak("The rehearsal could not finish — check the panel.");
      }
    },
    [speak],
  );

  const finishRehearsal = useCallback(
    async (verdict: "confirmed" | "rejected", method: string) => {
      const spec = rehearsalSpecRef.current;
      rehearsalAwaitRef.current = false;
      setPortals([]);
      setHot(-1);
      if (!spec) return;
      const r = await window.mirror.rehearseDecide(spec.name, verdict, undefined, method);
      setRehearsal((prev) => ({
        ...prev,
        state: r.transcript?.state ?? prev.state,
        transcript: r.transcript ?? prev.transcript,
      }));
      if (!r.ok) {
        notify(r.error || "Could not record the rehearsal verdict.");
        return;
      }
      if (verdict === "confirmed") {
        const deploy = await window.mirror.forgeDeploy(spec);
        setForge((f) => ({ ...f, phase: "ready", deploy }));
        setHealth(await window.mirror.health());
        if (deploy.ok) setRehearsal(emptyRehearsal);
        void speak(
          deploy.ok
            ? "Deployed. The agent is live in the brainstem right now — rehearsed and confirmed."
            : "Deploy hit a snag — check the panel.",
        );
      } else {
        void speak("Okay — tell me what went wrong, then forge it again and I'll fold that in.");
      }
    },
    [notify, speak],
  );
  finishRehearsalRef.current = (v, m) => void finishRehearsal(v, m);

  /* ── the forge ─────────────────────────────────────────────────────── */
  const runForge = useCallback(async () => {
    if (!historyRef.current.length && !screenCtxRef.current.length) {
      setForge({
        phase: "error",
        error:
          "Nothing to forge yet. Show the mirror a task first — talk it through, or turn on “see screen” and walk through it once — then forge.",
      });
      return;
    }
    setForge({ phase: "distilling" });
    const r = await window.mirror.forgeDistill(historyRef.current, screenCtxRef.current, sessionId);
    if (!r.ok || !r.spec) {
      setForge({ phase: "error", error: r.error || "Nothing to forge yet — show or tell me a task first." });
      void speak("I couldn't distill an automation from what I've seen yet.");
      return;
    }
    setForge({ phase: "ready", spec: r.spec });
    void speak(`I forged ${r.spec.title}. Export it anywhere, or deploy it straight into the brainstem.`);
  }, [speak]);

  const forgeExport = useCallback(async () => {
    if (!forge.spec) return;
    setForge((f) => ({ ...f, phase: "busy" }));
    const artifacts = await window.mirror.forgeExport(forge.spec);
    setForge((f) => ({ ...f, phase: "ready", artifacts }));
    if (artifacts.ok) void speak("Exported: an agent file, a skill file, and a Copilot Studio solution.");
  }, [forge.spec, speak]);

  const forgeDeploy = useCallback(async () => {
    if (!forge.spec) return;
    setForge((f) => ({ ...f, phase: "busy" }));
    const deploy = await window.mirror.forgeDeploy(forge.spec);
    if (deploy.needsRehearsal) {
      // The gate spoke: no unrehearsed spec goes live. Rehearse instead.
      setForge((f) => ({ ...f, phase: "ready" }));
      void speak("Before this goes live, let me rehearse it — the twin runs the whole job virtually first.");
      void startRehearsal(forge.spec);
      return;
    }
    setForge((f) => ({ ...f, phase: "ready", deploy }));
    setHealth(await window.mirror.health());
    void speak(deploy.ok ? "Deployed. The agent is live in the brainstem right now." : "Deploy hit a snag — check the panel.");
  }, [forge.spec, speak, startRehearsal]);

  /* ── chat ──────────────────────────────────────────────────────────── */
  const chat = useCallback(
    async (input: string): Promise<string | null> => {
      const text = input.trim();
      if (!text) return null;
      // While "fully done?" is on stage, every input channel — portal pick,
      // nod (picks the hot portal), voice, typing — routes to the verdict.
      if (rehearsalAwaitRef.current) {
        if (text === "__rehearsal:confirm" || /\b(fully done|deploy it)\b/i.test(text)) {
          void finishRehearsal("confirmed", text.startsWith("__") ? "portal" : "voice");
          return "rehearsal-confirmed";
        }
        if (text === "__rehearsal:reject" || /\b(not right|not done|reject)\b/i.test(text)) {
          void finishRehearsal("rejected", text.startsWith("__") ? "portal" : "voice");
          return "rehearsal-rejected";
        }
      }
      if (FORGE_INTENT.test(text)) {
        void runForge();
        return "forging";
      }
      const reflectMatch = REFLECT_INTENT.exec(text);
      if (reflectMatch) {
        reflect(reflectMatch[1]);
        setExchanges((x) => [...x, { u: text, a: `Reflecting on it — I'll keep looping with the brainstem in the background. Watch the sticky.` }]);
        return "reflecting";
      }
      setPhase("thinking");
      setPortals([]);
      setHot(-1);
      setExchanges((x) => [...x, { u: text, a: "…" }]);
      let userInput = text;
      if (screenCtxRef.current.length) {
        userInput += "\n\n[What the mirror currently sees on my screen]\n" + screenCtxRef.current.join("\n---\n");
      }
      userInput += ENVELOPE_HINT;
      const r = await window.mirror.chat(userInput, historyRef.current.slice(-12), sessionId);
      if (!r.ok) {
        setPhase("idle");
        setExchanges((x) => [...x.slice(0, -1), { u: text, a: `(no answer — ${r.error ?? "brainstem unreachable"})` }]);
        return null;
      }
      const env = parseEnvelope(r.response ?? "");
      historyRef.current = [...historyRef.current, { role: "user", content: text }, { role: "assistant", content: env.text }];
      setExchanges((x) => [...x.slice(0, -1), { u: text, a: env.text || "…" }]);
      if (r.agentLogs) setAgentLog(r.agentLogs.slice(0, 220));
      if (env.holo?.options.length) {
        setPortals(env.holo.options);
        setTurn((t) => t + 1);
        setHot(-1);
        setPrompt(env.holo.prompt || "See more?");
      } else {
        setPrompt("See more?");
      }
      setPhase("idle");
      // VOICE-only speech: the |||VOICE||| line is what gets spoken — the raw
      // text stays visual (transcript). No VOICE line, no speech.
      if (env.spoken) void speak(env.spoken);
      return env.text;
    },
    [finishRehearsal, reflect, runForge, speak],
  );

  const pickPortal = useCallback(
    (i: number) => {
      const o = portalsRef.current[i];
      if (!o) return;
      setPortals([]);
      setHot(-1);
      setDwell(0);
      dwellRef.current = { idx: -1, since: 0 };
      void chat(o.value || o.label);
    },
    [chat],
  );

  const newConversation = useCallback(() => {
    hush();
    historyRef.current = [];
    screenCtxRef.current = [];
    sessionId = `mirror-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem("mirror.session", sessionId);
    setExchanges([]);
    setPortals(STARTERS);
    setTurn(0);
    setHot(-1);
    setPrompt("New conversation.");
    setAgentLog("");
    setContext("");
    setForge({ phase: "hidden" });
    setRehearsal(emptyRehearsal);
    rehearsalAwaitRef.current = false;
    rehearsalSpecRef.current = null;
  }, [hush]);

  /* ── voice IN (push-to-talk) ───────────────────────────────────────── */
  const talkStart = useCallback(async () => {
    if (asleep || recordingRef.current) return;
    hush();
    try {
      recordingRef.current = await startRecording();
      setPhase("listening");
    } catch (err) {
      notify(err instanceof Error ? err.message : String(err));
    }
  }, [asleep, hush, notify]);

  const talkStop = useCallback(async () => {
    const rec = recordingRef.current;
    if (!rec) return;
    recordingRef.current = null;
    setPhase("thinking");
    try {
      const wav = await rec.stop();
      const t = await window.mirror.transcribe(wav);
      if (!t.ok) {
        setPhase("idle");
        notify(`Voice input needs a local whisper server (brew install whisper-cpp): ${t.error}`);
        return;
      }
      if (!t.text) {
        setPhase("idle");
        return;
      }
      routeTranscriptRef.current(t.text);
    } catch (err) {
      setPhase("idle");
      notify(err instanceof Error ? err.message : String(err));
    }
  }, [notify]);

  /* café mode: the mirror hears COLORS only — quick confirms in loud rooms,
     everything that isn't a color never registers at all */
  const [cafeMode, setCafeMode] = useState(false);
  const cafeRef = useRef(cafeMode);
  cafeRef.current = cafeMode;

  /** Route a heard transcript. In café mode only option colors count. */
  const routeTranscript = useCallback(
    (text: string) => {
      if (!text || text.length < 2) return;
      const lower = text.toLowerCase();
      if (cafeRef.current) {
        const n = portalsRef.current.length;
        const heardColor = PORTAL_COLORS.findIndex((c, i) => i < n && lower.includes(c.name));
        if (heardColor >= 0) pickPortal(heardColor);
        return; // anything that isn't a color was never heard
      }
      const mapping = parseGestureMapping(text);
      if (mapping) {
        setGestureCommands((current) => {
          const next = {
            ...current,
            [mapping.gesture]: mapping.command,
          };
          localStorage.setItem(GESTURE_STORAGE_KEY, JSON.stringify(next));
          return next;
        });
        notify(
          `${mapping.gesture.replace(/_/g, " ")} now means: ${mapping.command.label}`,
        );
        void speak(
          `Gesture saved. I will ask for a thumbs up before ${mapping.command.label}.`,
        );
        return;
      }
      const idx = portalsRef.current.findIndex((o) => lower.includes(o.label.toLowerCase()));
      if (idx >= 0) return pickPortal(idx);
      void chat(text);
    },
    [chat, notify, pickPortal, speak],
  );
  routeTranscriptRef.current = routeTranscript;

  /* narrate mode — the orb: tap once, then just talk */
  const routeUtterance = useCallback(
    async (wav: ArrayBuffer) => {
      if (phaseRef.current === "thinking" && !cafeRef.current) return; // don't pile questions up
      if (phaseRef.current === "speaking" && !cafeRef.current) hush(); // barge-in
      const t = await window.mirror.transcribe(wav);
      routeTranscript((t.ok && t.text) || "");
    },
    [hush, routeTranscript],
  );

  const toggleNarrate = useCallback(async () => {
    if (narrationRef.current) {
      narrationRef.current.stop();
      narrationRef.current = null;
      setNarrating(false);
      setSpeechLive(false);
      setPhase((p) => (p === "listening" ? "idle" : p));
      return;
    }
    if (!voice?.whisper) {
      notify("To let the mirror hear: brew install whisper-cpp, then run whisper-server on :8765.");
    }
    try {
      narrationRef.current = await startNarration({
        onSegment: (wav) => void routeUtterance(wav),
        onLevel: (level) => {
          micLevelRef.current = { v: level, t: performance.now() };
        },
        onSpeech: (active) => {
          setSpeechLive(active);
          if (active && phaseRef.current === "speaking") hush();
          setPhase((p) => (active && p === "idle" ? "listening" : !active && p === "listening" ? "idle" : p));
        },
      });
      setNarrating(true);
    } catch (err) {
      notify(err instanceof Error ? err.message : String(err));
    }
  }, [hush, notify, routeUtterance, voice?.whisper]);
  toggleNarrateRef.current = () => void toggleNarrate();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.code === "Space" && document.activeElement !== composerRef.current && !e.repeat) {
        e.preventDefault();
        void talkStart();
      }
    };
    const up = (e: KeyboardEvent) => {
      if (e.code === "Space" && document.activeElement !== composerRef.current) {
        e.preventDefault();
        void talkStop();
      }
    };
    addEventListener("keydown", down);
    addEventListener("keyup", up);
    return () => {
      removeEventListener("keydown", down);
      removeEventListener("keyup", up);
    };
  }, [talkStart, talkStop]);

  /* ── portal geometry: collision-aware placement ────────────────────── */
  // Every fixed HUD element is a forbidden rectangle; each card tries its
  // orbit slot at several radii and falls back to a clean right-lane stack.
  // Nothing ever overlaps the heading, monkeys, transcript, herd, stickies,
  // controls, the orb — or the Brain Surgeon dock's stolen width.
  const [layoutTick, setLayoutTick] = useState(0);
  useEffect(() => {
    const onResize = () => setLayoutTick((t) => t + 1);
    addEventListener("resize", onResize);
    return () => removeEventListener("resize", onResize);
  }, []);

  const positions = useMemo(() => {
    const n = portals.length;
    if (!n) return [];
    if (narrowMid) return portals.map(() => ({ x: 0, y: 0, angle: 0 })); // phone flow — no orbit
    const dockW = !surgeonOpen
      ? 0
      : !(surgeonWide && surgeonCards >= 2)
        ? Math.min(500, window.innerWidth * 0.44)
        : surgeonCards === 2
          ? Math.min(840, window.innerWidth - 560)
          : Math.min(1180, window.innerWidth - 560);
    const ldockW = chatOpen ? Math.min(420, window.innerWidth * 0.3) : 0;
    const W = window.innerWidth - dockW - ldockW; // usable space (matches the CSS shift)
    const H = window.innerHeight;
    const CARD = 196;
    const half = CARD / 2 + 12;
    interface Rect { l: number; t: number; r: number; b: number }
    const zones: Rect[] = [
      { l: 0, t: 0, r: W, b: 212 }, // heading + monkeys band
      { l: 0, t: H - 150, r: W, b: H }, // voice wave + toast band
      { l: W - 160, t: H - 420, r: W, b: H }, // side controls + previews
      { l: W - 140, t: 0, r: W, b: 116 }, // + button
    ];
    if (reflections.length) zones.push({ l: W - 300, t: 90, r: W, b: H * 0.62 }); // stickies
    const cx = W / 2;
    const cy = H * 0.48;
    zones.push({ l: cx - 255, t: cy - 255, r: cx + 255, b: cy + 255 }); // the orb
    const collides = (x: number, y: number, extra: Rect[]) => {
      const c = { l: x - half, t: y - half, r: x + half, b: y + half };
      if (c.l < 8 || c.t < 8 || c.r > W - 8 || c.b > H - 8) return true;
      return [...zones, ...extra].some((z) => c.l < z.r && c.r > z.l && c.t < z.b && c.b > z.t);
    };
    const SLOTS: Record<number, number[]> = {
      1: [0],
      2: [180, 0],
      3: [-50, 180, 50],
      4: [-135, -45, 135, 45],
      5: [-135, -45, 180, 0, 135],
      6: [-135, -45, 180, 0, 135, 45],
    };
    const slots = SLOTS[Math.min(n, 6)];
    const flip = turn % 2 === 1 ? -1 : 1;
    const baseR = Math.min(W * 0.34, H * 0.42, 470);
    const placed: Rect[] = [];
    return portals.map((_, i) => {
      const a = ((slots[i % slots.length] * Math.PI) / 180);
      let px = cx;
      let py = cy;
      let ok = false;
      for (const rf of [1, 0.85, 1.18, 0.72, 1.35]) {
        const x = cx + Math.cos(a) * baseR * rf * flip;
        const y = cy + Math.sin(a) * baseR * rf * 0.82;
        if (!collides(x, y, placed)) {
          px = x;
          py = y;
          ok = true;
          break;
        }
      }
      if (!ok) {
        // lane scan: two right lanes, then a left lane — first free pocket wins
        for (const laneX of [W - 172 - half, W - 320 - half, 340 + half]) {
          for (let y = 220 + half; y < H - 110 - half; y += 44) {
            if (!collides(laneX, y, placed)) {
              px = laneX;
              py = y;
              ok = true;
              break;
            }
          }
          if (ok) break;
        }
      }
      if (!ok) {
        // absolute last resort: a top-right pocket — NEVER the orb
        px = Math.min(W - 8 - half, W - 250);
        py = 240 + placed.length * 60;
      }
      placed.push({ l: px - half, t: py - half, r: px + half, b: py + half });
      return { x: px - cx, y: py - cy, angle: a };
    }).reduce<{ x: number; y: number; angle: number }[]>((acc, p) => {
      // belt-and-suspenders: no two cards may overlap, whatever path placed
      // them — walk down (then a column left) until clear of ALL priors.
      let { x, y } = p;
      const GAP = CARD + 26;
      for (let guard = 0; guard < 16; guard++) {
        const clash = acc.find((q) => Math.abs(x - q.x) < GAP && Math.abs(y - q.y) < GAP);
        if (!clash) break;
        y = clash.y + GAP;
        if (y > H / 2 - 130) {
          y = -(H / 2) + 250;
          x -= GAP;
        }
      }
      acc.push({ ...p, x, y });
      return acc;
    }, []);
  }, [portals, turn, narrowMid, surgeonOpen, surgeonWide, surgeonCards, chatOpen, cafeMode, detached.length, reflections.length, layoutTick]);

  /* ── the visible cursor (rapp-vui): gaze-driven and/or fingertip-driven ─
     A ring you can SEE. Hovering a portal highlights it; gaze dwell fills the
     ring and selects; a pinch clicks whatever the hand cursor is over. */
  const [cursor, setCursor] = useState<{ x: number; y: number; kind: "gaze" | "hand"; pinching: boolean; progress: number } | null>(null);
  const pinchHold = useRef<{ idx: number; since: number }>({ idx: -1, since: 0 });
  /** After a gaze-dwell fires on the orb, the gaze must leave it to re-arm. */
  const orbLatch = useRef(false);
  const [gestureFlash, setGestureFlash] = useState("");
  const gestureTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handLive = useRef(false);

  const flashGesture = useCallback((label: string) => {
    setGestureFlash(label);
    if (gestureTimer.current) clearTimeout(gestureTimer.current);
    gestureTimer.current = setTimeout(() => setGestureFlash(""), 1500);
  }, []);

  const portalAt = useCallback((px: number, py: number): number => {
    const el = document.elementFromPoint(px, py)?.closest?.(".portal");
    const idx = el ? Number.parseInt((el as HTMLElement).dataset.idx ?? "-1", 10) : -1;
    return Number.isNaN(idx) ? -1 : idx;
  }, []);

  const moveCursor = useCallback(
    (px: number, py: number, kind: "gaze" | "hand", pinching: boolean, pinchDown: boolean) => {
      const x = Math.max(8, Math.min(window.innerWidth - 8, px));
      const y = Math.max(8, Math.min(window.innerHeight - 8, py));
      const idx = portalAt(x, y);
      if (idx >= 0) setHot(idx);
      if (kind === "hand") {
        // Pinch-HOLD over an option: a visible circle fills for 3s, then selects.
        // Releasing the pinch early cancels. Instant pinch-click still works on
        // ordinary buttons (orb, chips, controls).
        let progress = 0;
        const now = performance.now();
        if (pinching && idx >= 0) {
          if (pinchHold.current.idx !== idx) pinchHold.current = { idx, since: now };
          progress = Math.min(1, (now - pinchHold.current.since) / PINCH_HOLD_MS);
          setDwell(progress);
          if (progress >= 1) {
            pinchHold.current = { idx: -1, since: 0 };
            setCursor({ x, y, kind, pinching, progress: 0 });
            pickPortal(idx);
            return;
          }
        } else {
          if (pinchHold.current.idx !== -1) {
            pinchHold.current = { idx: -1, since: 0 };
            setDwell(0);
          }
          if (pinchDown && idx < 0) {
            (document.elementFromPoint(x, y) as HTMLElement | null)?.click?.();
          }
        }
        setCursor({ x, y, kind, pinching, progress });
        return;
      }
      // gaze: hold the cursor over an option — or the ORB — for 3s; the same
      // circle fills on the cursor before it acts. Looking at the orb equals
      // clicking it: it toggles narrate (re-arms after the gaze leaves).
      const now = performance.now();
      const overOrb = idx < 0 && Boolean(document.elementFromPoint(x, y)?.closest?.("#core"));
      const target = idx >= 0 ? idx : overOrb ? -2 : -1;
      if (!overOrb) orbLatch.current = false;
      if (target === -1 || (target === -2 && orbLatch.current)) {
        dwellRef.current = { idx: -1, since: 0 };
        setDwell(0);
        setCursor({ x, y, kind, pinching, progress: 0 });
        return;
      }
      if (dwellRef.current.idx !== target) {
        dwellRef.current = { idx: target, since: now };
        setDwell(0);
        setCursor({ x, y, kind, pinching, progress: 0 });
        return;
      }
      const progress = Math.min(1, (now - dwellRef.current.since) / DWELL_MS);
      if (target >= 0) setDwell(progress);
      setCursor({ x, y, kind, pinching, progress });
      if (progress >= 1) {
        dwellRef.current = { idx: -1, since: 0 };
        if (target >= 0) {
          pickPortal(target);
        } else {
          orbLatch.current = true;
          toggleNarrateRef.current();
        }
      }
    },
    [pickPortal, portalAt],
  );

  const onPose = useCallback(
    (dx: number, dy: number) => {
      if (handLive.current) return; // the fingertip owns the cursor while a hand is up
      const px = window.innerWidth / 2 + dx * window.innerWidth * 2.4;
      const py = window.innerHeight * 0.46 + dy * window.innerHeight * 3.0;
      moveCursor(px, py, "gaze", false, false);
    },
    [moveCursor],
  );
  const onPoseRef = useRef(onPose);
  onPoseRef.current = onPose;

  const onHandPoint = useCallback(
    (x: number | null, y: number | null, pinching: boolean, pinchDown: boolean) => {
      if (x === null || y === null) {
        if (handLive.current) {
          handLive.current = false;
          setCursor((c) => (c?.kind === "hand" ? null : c));
        }
        return;
      }
      handLive.current = true;
      moveCursor(x * window.innerWidth, y * window.innerHeight, "hand", pinching, pinchDown);
    },
    [moveCursor],
  );
  const onHandPointRef = useRef(onHandPoint);
  onHandPointRef.current = onHandPoint;

  /* ── hands-free (camera) ───────────────────────────────────────────── */
  const toggleScreen = useCallback(async () => {
    if (screenRef.current) {
      screenRef.current.stop();
      screenRef.current = null;
      setScrOn(false);
      setScrState("off");
      return;
    }
    try {
      setScrState("starting…");
      screenRef.current = await startScreenWatch(scrVideoRef.current!, {
        onStatus: setScrState,
        onText: (snippet) => {
          screenCtxRef.current = [...screenCtxRef.current.slice(-2), snippet];
          setContext(snippet);
        },
        onEnded: () => {
          screenRef.current = null;
          setScrOn(false);
          setScrState("off");
        },
      });
      setScrOn(true);
    } catch (err) {
      setScrState("unavailable");
      notify(err instanceof Error ? err.message : String(err));
    }
  }, [notify]);

  const [eyesOn, setEyesOn] = useState(false);
  const [handsOn, setHandsOn] = useState(false);
  const modesRef = useRef({ eyes: false, hands: false });

  const setVisionModes = useCallback(async (eyes: boolean, hands: boolean) => {
    modesRef.current = { eyes, hands };
    setEyesOn(eyes);
    setHandsOn(hands);
    if (!eyes && !hands) {
      if (visionRef.current) {
        visionRef.current.stop();
        visionRef.current = null;
      }
      setCamOn(false);
      setCamState("");
      setSeenParts("");
      setHot(-1);
      setDwell(0);
      return;
    }
    if (visionRef.current) {
      visionRef.current.setModes({ eyes, hands });
      return;
    }
    await startCamera({ eyes, hands });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleCamera = useCallback(async () => {
    const on = modesRef.current.eyes || modesRef.current.hands;
    await setVisionModes(!on, !on);
  }, [setVisionModes]);

  const rejectPendingGesture = useCallback(() => {
    if (!pendingGestureRef.current) return;
    pendingGestureRef.current = null;
    gestureTone("rejected");
    notify("Pending gesture command cancelled.");
    void speak("Cancelled.");
  }, [gestureTone, notify, speak]);

  const stageGestureCommand = useCallback(
    (gesture: CommandGesture) => {
      const command = gestureCommandsRef.current[gesture];
      pendingGestureRef.current = {
        gesture,
        command,
        expiresAt: Date.now() + GESTURE_APPROVAL_MS,
      };
      gestureTone("detected");
      notify(`${command.label} detected — thumbs up to approve.`);
      void speak(
        `${command.label} detected. Thumbs up to approve, or thumbs down to cancel.`,
      );
    },
    [gestureTone, notify, speak],
  );

  const approvePendingGesture = useCallback(() => {
    const pending = pendingGestureRef.current;
    if (!pending) return false;
    pendingGestureRef.current = null;
    if (Date.now() > pending.expiresAt) {
      gestureTone("rejected");
      notify("Gesture approval expired.");
      void speak("That gesture expired. Show it again.");
      return true;
    }
    if (rehearsalAwaitRef.current) {
      gestureTone("rejected");
      notify("Custom gestures cannot approve a deployment rehearsal.");
      void speak(
        "Use the highlighted confirmation portal or an explicit spoken confirmation for deployment.",
      );
      return true;
    }
    gestureTone("approved");
    notify(`${pending.command.label} approved.`);
    void speak(`Approved. ${pending.command.label}.`);
    if (pending.command.prompt === "@local:toggle-screen") {
      void toggleScreen();
    } else {
      void chat(pending.command.prompt);
    }
    return true;
  }, [chat, gestureTone, notify, speak, toggleScreen]);

  const startCamera = useCallback(async (modes: { eyes: boolean; hands: boolean }) => {
    try {
      setCamState("starting…");
      visionRef.current = await startVision(camVideoRef.current!, {
        onStatus: setCamState,
        onSeen: (parts) => setSeenParts(parts.join(" · ")),
        onPose: (dx, dy) => onPoseRef.current(dx, dy),
        onHead: (g) => {
          if (g === "nod" && hotRef.current >= 0) pickPortal(hotRef.current);
          if (g === "shake") {
            if (rehearsalAwaitRef.current) {
              finishRehearsalRef.current("rejected", "shake");
            } else if (portalsRef.current.length) {
              setPortals([]);
              setHot(-1);
            } else hush();
          }
        },
        onHandPoint: (x, y, pinching, pinchDown) => onHandPointRef.current(x, y, pinching, pinchDown),
        onHand: (g) => {
          flashGesture(
            g === "Open_Palm" ? "✋ open palm" :
            g === "Thumb_Up" ? "👍 approve" :
            g === "Thumb_Down" ? "👎 cancel" :
            g === "Closed_Fist" ? "✊ hush" :
            g === "Victory" ? "✌️ command" :
            g === "ILoveYou" ? "🤟 command" : "☝️ next",
          );
          if (g === "Open_Palm") void (recordingRef.current ? talkStop() : talkStart());
          if (g === "Thumb_Up") {
            if (!approvePendingGesture() && hotRef.current >= 0) {
              pickPortal(hotRef.current);
            }
          }
          if (g === "Thumb_Down") {
            if (pendingGestureRef.current) rejectPendingGesture();
            else if (portalsRef.current.length) {
              setPortals([]);
              setHot(-1);
            }
          }
          if (g === "Closed_Fist") {
            rejectPendingGesture();
            hush();
          }
          if (g === "Victory") stageGestureCommand("Victory");
          if (g === "ILoveYou") stageGestureCommand("ILoveYou");
          if (g === "Pointing_Up") {
            if (portalsRef.current.length) {
              setHot((h) => (h + 1) % portalsRef.current.length);
            } else {
              stageGestureCommand("Pointing_Up");
            }
          }
        },
        onBlinkHold: () =>
          setAsleep((s) => {
            const next = !s;
            notify(next ? "Going quiet — long-blink again to wake me." : "Awake.");
            return next;
          }),
        onFatal: (m) => {
          visionRef.current = null;
          modesRef.current = { eyes: false, hands: false };
          setEyesOn(false);
          setHandsOn(false);
          setCamOn(false);
          setCamState("failed");
          notify(m);
        },
      }, modes);
      setCamOn(true);
    } catch (err) {
      modesRef.current = { eyes: false, hands: false };
      setEyesOn(false);
      setHandsOn(false);
      setCamState("unavailable");
      notify(err instanceof Error ? err.message : String(err));
    }
  }, [
    approvePendingGesture,
    hush,
    notify,
    pickPortal,
    rejectPendingGesture,
    stageGestureCommand,
    talkStart,
    talkStop,
  ]);

  const headlessGesturesStarted = useRef(false);
  const headlessMicStarted = useRef(false);
  useEffect(() => {
    if (
      window.mirror.headlessGestures &&
      !headlessGesturesStarted.current
    ) {
      headlessGesturesStarted.current = true;
      void setVisionModes(true, true);
    }
    if (
      window.mirror.headlessMic &&
      !headlessMicStarted.current &&
      !narrationRef.current
    ) {
      headlessMicStarted.current = true;
      void toggleNarrate();
    }
  }, [setVisionModes, toggleNarrate]);

  /* ── autonomy surface (DevTools / CDP / mirrorctl's UI twin) ───────── */
  useEffect(() => {
    window.mirrorDebug = {
      chat,
      speak,
      hush,
      forge: runForge,
      forgeExport,
      forgeDeploy,
      rehearse: (spec?: ForgeSpecView) => {
        const s = spec ?? forge.spec;
        if (s) void startRehearsal(s);
      },
      rehearseConfirm: () => void finishRehearsal("confirmed", "debug"),
      rehearseReject: () => void finishRehearsal("rejected", "debug"),
      rehearsalState: () => rehearsal,
      toggleCamera,
      toggleScreen,
      toggleNarrate,
      talkStart,
      talkStop,
      newConversation,
      reflect,
      reflections: () => reflectionsRef.current,
      detachPortal,
      detached: () => detachedRef.current,
      openSurgeon: () => setSurgeonOpen(true),
      setCafe: setCafeMode,
      /** Test seam: route a transcript as if whisper heard it. */
      hearText: routeTranscript,
      gestureCommands: () => gestureCommandsRef.current,
      pendingGesture: () => pendingGestureRef.current,
      stageGesture: (gesture: CommandGesture) => stageGestureCommand(gesture),
      approveGesture: approvePendingGesture,
      rejectGesture: rejectPendingGesture,
      setMuted,
      pickPortal,
      health: () => window.mirror.health(),
      state: () => ({
        phase,
        asleep,
        muted,
        camOn,
        scrOn,
        prompt,
        portals: portalsRef.current,
        exchanges: exchanges.length,
        screenContext: screenCtxRef.current,
      }),
    };
  }, [asleep, camOn, chat, exchanges.length, finishRehearsal, forge.spec, forgeDeploy, forgeExport, hush, muted, newConversation, phase, pickPortal, prompt, rehearsal, runForge, scrOn, speak, startRehearsal, talkStart, talkStop, toggleCamera, toggleScreen]);

  /* ── render ────────────────────────────────────────────────────────── */
  const brainOk = Boolean(health?.ok && health.status === "ok");
  const coreLabel =
    phase === "thinking"
      ? "thinking…"
      : phase === "speaking"
        ? "speaking"
        : narrating
          ? speechLive
            ? "listening…"
            : "narrating — just talk"
          : "tap to narrate";

  return (
    <div
      className={`${phase !== "idle" ? phase : ""}${surgeonOpen && herdActive ? " herdmode" : ""}${narrowMid ? " narrowmid" : ""}`}
      style={{ "--dock": dockCss, "--ldock": chatOpen ? "min(420px, 30vw)" : "0px" } as React.CSSProperties}
    >
      <div id="dragbar" />
      <div id="prompt">{prompt}</div>

      <div id="monkeys">
        <button
          className={`monkey${eyesOn ? " on" : ""}`}
          title={eyesOn ? "Eye interaction on — head-pointing highlights a portal, dwell selects, nod = yes, shake = no, long blink = sleep. Click to cover its eyes." : "Click for EYE interaction — look toward a portal to highlight it, dwell to select, nod to confirm. macOS asks for camera access once. Works alone or together with hands."}
          onClick={() => void setVisionModes(!eyesOn, handsOn)}
        >
          <span className="face">{eyesOn ? "🐵" : "🙈"}</span>
          <span className="cap">eyes</span>
          <span className="sub">{eyesOn ? camState || "tracking gaze" : "covered"}</span>
        </button>
        <button
          className={`monkey${handsOn ? " on" : ""}`}
          title={handsOn ? "Hand interaction on — ☝️ cycles the options, 👍 confirms, ✋ talk, ✊ hush, ✌️ screen. Click to stop." : "Click for HAND interaction — point up to cycle options, thumb-up to select, open palm to talk. Works alone or together with eyes."}
          onClick={() => void setVisionModes(eyesOn, !handsOn)}
        >
          <span className="face">{handsOn ? "✋" : "🤚"}</span>
          <span className="cap">hands</span>
          <span className="sub">{handsOn ? seenParts || "watching hands" : "covered"}</span>
        </button>
        <button
          className={`monkey${scrOn ? " on" : ""}`}
          title={scrOn ? "The mirror is reading your screen (local OCR). Click to stop." : "Click so the mirror can SEE YOUR SCREEN — read locally, folded into the conversation."}
          onClick={() => void toggleScreen()}
        >
          <span className="face">{scrOn ? "🖥️" : "🙈"}</span>
          <span className="cap">see screen</span>
          <span className="sub">{scrOn ? scrState : "screen covered"}</span>
        </button>
        <button
          className={`monkey${narrating ? " on" : ""}`}
          title={
            !voice?.whisper
              ? "The mirror can't HEAR yet — click to install hearing (whisper.cpp + a local model, one time)."
              : narrating
                ? "Narrating — the mirror hears everything you say. Click to cover its ears."
                : "Click so the mirror can HEAR — open-mic narration, transcribed locally."
          }
          onClick={() => {
            if (!voice?.whisper) {
              void installHearing();
              return;
            }
            void toggleNarrate();
          }}
        >
          <span className="face">{narrating ? "🐵" : "🙉"}</span>
          <span className="cap">hear</span>
          <span className="sub">{!voice?.whisper ? (sttInstalling ? "installing…" : "install hearing") : narrating ? (speechLive ? "hearing you…" : "narrating") : "ears covered"}</span>
        </button>
        <button
          className={`monkey${cafeMode ? " on" : ""}`}
          title={cafeMode ? "Café mode ON — the mirror hears option COLORS only; all other speech never registers. Click for full listening." : "Click for CAFÉ mode — in loud rooms the mirror hears only the option colors (say “green”, “blue”…) and drops everything else."}
          onClick={() => {
            setCafeMode((c) => {
              const next = !c;
              if (next && !narrationRef.current) toggleNarrateRef.current(); // café = mic always on
              if (!next && narrationRef.current) toggleNarrateRef.current();
              notify(next
                ? "Café mode: mic is ON, but it only hears the option COLORS — everything else is dropped."
                : "Café mode off — mic closed; tap the orb to narrate.");
              return next;
            });
          }}
        >
          <span className="face">☕</span>
          <span className="cap">café</span>
          <span className="sub">{cafeMode ? "listening · colors only" : "off"}</span>
        </button>
        <button
          className={`monkey${!muted && voice?.vibevoice === "ready" ? " on" : ""}`}
          title={
            voice?.vibevoice === "off"
              ? "The mirror has no voice yet — click to install VibeVoice (its real voice; a few GB, one time)."
              : muted
                ? "Mouth covered (muted). Click so the mirror can SPEAK."
                : "The mirror speaks with VibeVoice. Click to cover its mouth."
          }
          onClick={() => {
            if (voice?.vibevoice === "off") {
              void installVibeVoice();
              return;
            }
            setMuted((m) => !m);
            hush();
          }}
        >
          <span className="face">{voice?.vibevoice === "off" ? "🙊" : muted ? "🙊" : "🐵"}</span>
          <span className="cap">speak</span>
          <span className="sub">{voice?.vibevoice === "off" ? (voiceInstalling ? "installing…" : "install VibeVoice") : muted ? "mouth covered" : voice?.vibevoice === "ready" ? `VibeVoice · ${voice.speaker}` : "VibeVoice loading…"}</span>
        </button>
      </div>

      <div id="topctl">
        <button className="sqbtn" title="New conversation" onClick={newConversation}>
          <PlusIcon />
        </button>
      </div>

      <div id="orbstage">
        <Particles active={alive} turns={exchanges.length} />
        <svg id="blob" viewBox="0 0 100 100" style={{ opacity: alive ? 1 : 0 }}>
          <defs>
            <linearGradient id="bg1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="var(--orb-a)" />
              <stop offset="100%" stopColor="var(--orb-b)" />
            </linearGradient>
          </defs>
          <path d={blobPath(exchanges.length)} fill="url(#bg1)" opacity="0.92" />
        </svg>
        <Wireframe active={alive} turns={exchanges.length} />
        <div
          id="core"
          className={narrating ? "narrating" : ""}
          title="Tap to narrate — the mirror listens until you tap again (hold space for push-to-talk)"
          onClick={() => void toggleNarrate()}
        >
          <div>
            <MicIcon />
            <div className="label">{coreLabel}</div>
          </div>
        </div>
      </div>

      <div id="portals">
        {portals.map((o, i) => {
          const p = positions[i];
          if (!p) return null;
          return (
            <button
              key={`${turn}-${i}`}
              className={`portal${i === hot ? " hot" : ""}`}
              data-idx={i}
              onPointerDown={(e) => onPortalPointerDown(i, e)}
              title="Click to choose — or drag it out of the circle to keep it as its own chat"
              style={
                narrowMid
                  ? ({ "--dwell": i === hot ? dwell : 0 } as React.CSSProperties)
                  : ({
                      left: `calc(50% + ${p.x}px)`,
                      top: `calc(48% + ${p.y}px)`,
                      "--dwell": i === hot ? dwell : 0,
                    } as React.CSSProperties)
              }
              onClick={() => pickPortal(i)}
            >
              {cafeMode ? (
                <span className="colorpill" style={{ background: PORTAL_COLORS[i % PORTAL_COLORS.length].css }}>
                  {PORTAL_COLORS[i % PORTAL_COLORS.length].name}
                </span>
              ) : (
                <span className="dash" style={{ background: PORTAL_COLORS[i % PORTAL_COLORS.length].css }} />
              )}
              {o.label}
              <span className="dwell" />
            </button>
          );
        })}
      </div>

      {/* the LEFT dock: all text I/O lives here — the middle stays a
          keyboard-less, mobile-portable surface */}
      <aside id="leftdock" className={chatOpen ? "open" : ""}>
        <header>
          <span className="brand avatar">🧠</span>
          <div className="who">
            <b>Your Brainstem</b>
            <span>{health?.ok
              ? `online · v${health.version} · ${health.model}`
              : engine?.phase === "installing" ? "planting your brainstem…"
              : engine?.phase === "unavailable" || engine?.phase === "failed" ? "no engine — open status ⓘ"
              : "connecting…"}</span>
          </div>
          <button className="x" title="Hide (the tab brings it back)" onClick={() => setChatOpen(false)}>✕</button>
        </header>
        <div className="scroll" ref={scrollRef}>
          {exchanges.length === 0 && (
            <div className="a dim">
              Welcome. The form at the center is your brainstem — alive, and reshaped by every
              turn. Choose a portal, tap the center and speak, or share your screen and say
              “make this an automation.”
            </div>
          )}
          {exchanges.map((x, i) => (
            <div key={i}>
              <div className="u">{x.u}</div>
              <div className="a">{renderMd(x.a)}</div>
            </div>
          ))}
        </div>
        <input
          ref={composerRef}
          type="text"
          placeholder="…or type to the mirror"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const v = e.currentTarget.value.trim();
              if (v) {
                e.currentTarget.value = "";
                void chat(v);
              }
            }
          }}
        />
      </aside>
      {!chatOpen && (
        <button id="lefttab" title="Conversation" onClick={() => setChatOpen(true)}>
          🪞<span>Conversation</span>
        </button>
      )}

      <div id="sidectl">
        <button className="sqbtn" title="Forge an automation from what the mirror has seen" onClick={() => void runForge()}>
          <HammerIcon />
        </button>
        <button className={`sqbtn${showStatus ? " on" : ""}`} title="Status" onClick={() => setShowStatus((s) => !s)}>
          <InfoIcon />
        </button>
      </div>

      {showStatus && (
        <div id="status">
          <h3>Monkey see · Monkey do</h3>
          <div className="row"><span className={`dot${brainOk ? " on" : " bad"}`} /><span className="lbl">brainstem</span><span className="val">{brainOk
            ? `v${health?.version} · ${health?.model}`
            : engine?.phase === "installing" ? "installing…"
            : engine?.phase === "unavailable" ? "installer unavailable"
            : engine?.phase === "failed" ? "install failed"
            : health?.error || health?.status || "connecting…"}</span></div>
          {(engine?.phase === "failed" || engine?.phase === "unavailable") && !brainOk && (
            <>
              {engine.detail && (
                <div className="row"><span className="lbl">engine</span><span className="val wrap">{engine.detail}</span></div>
              )}
              <button
                style={{ width: "100%", marginTop: 4, border: "1px solid rgba(109,114,243,0.45)", background: "rgba(109,114,243,0.08)", color: "var(--orb-b)", borderRadius: 8, padding: "8px 10px", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
                onClick={retryEngine}
              >
                ↻ Retry engine setup
              </button>
            </>
          )}
          {engine?.phase === "installing" && voiceInstallLine.startsWith("brainstem:") && (
            <div className="row"><span className="lbl">install</span><span className="val wrap">{voiceInstallLine}</span></div>
          )}
          {!brainOk && (
            <input
              type="text"
              defaultValue={engine?.url ?? ""}
              placeholder="brainstem URL — e.g. http://127.0.0.1:7071"
              title="Already run a brainstem somewhere (this Mac or another machine)? Point the mirror at it and press Enter."
              style={{ width: "100%", marginTop: 4, border: "1px solid rgba(109,114,243,0.3)", background: "transparent", color: "inherit", borderRadius: 8, padding: "7px 10px", fontSize: "0.78rem" }}
              onKeyDown={(e) => {
                if (e.key !== "Enter") return;
                const v = e.currentTarget.value.trim();
                void window.mirror.brainstemSetUrl(v).then((r) => {
                  notify(r.ok
                    ? (v ? `Looking for your brainstem at ${v}…` : "Brainstem URL reset to the default.")
                    : `Couldn't set the URL: ${r.error}`);
                });
              }}
            />
          )}
          <div className="row"><span className={`dot${voice?.vibevoice === "ready" ? " on" : voice?.vibevoice === "loading" ? " warn" : ""}`} /><span className="lbl">voice out</span><span className="val">{voice?.vibevoice === "ready" ? `VibeVoice · ${voice.speaker} (${voice.device})` : voice?.vibevoice === "loading" ? "VibeVoice loading…" : "no voice — install VibeVoice"}</span></div>
          {voice?.vibevoice === "off" && (
            <button
              disabled={voiceInstalling}
              style={{ width: "100%", marginTop: 4, border: "1px solid rgba(109,114,243,0.45)", background: voiceInstalling ? "transparent" : "rgba(109,114,243,0.08)", color: "var(--orb-b)", borderRadius: 8, padding: "8px 10px", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
              onClick={() => void installVibeVoice()}
            >
              {voiceInstalling ? "installing…" : "⬇ Install VibeVoice — give the mirror a real voice"}
            </button>
          )}
          {voiceInstalling && voiceInstallLine && (
            <div className="row"><span className="lbl">install</span><span className="val wrap">{voiceInstallLine}</span></div>
          )}
          <div className="row"><span className={`dot${voice?.whisper ? " on" : ""}`} /><span className="lbl">voice in</span><span className="val">{voice?.whisper ? "whisper.cpp — tap the orb to narrate" : "no whisper server"}</span></div>
          <div className="row"><span className={`dot${camOn ? " on" : ""}`} /><span className="lbl">camera</span><span className="val">{camOn ? `${camState}${seenParts ? " · " + seenParts : ""}` : "off — camera frames never leave this app"}</span></div>
          <div className="row"><span className={`dot${scrOn ? " on" : ""}`} /><span className="lbl">screen</span><span className="val">{scrState}</span></div>
          {context && <div className="row"><span className="lbl">sees</span><span className="val wrap">{context}</span></div>}
          <div className="row"><span className="lbl">agents</span><span className="val">{health?.agents?.slice(0, 5).join(", ") || "—"}{(health?.agents?.length ?? 0) > 5 ? "…" : ""}</span></div>
          {health?.status === "unauthenticated" && (
            <button
              style={{ width: "100%", marginTop: 4, border: "1px solid rgba(109,114,243,0.45)", background: "rgba(109,114,243,0.08)", color: "var(--orb-b)", borderRadius: 8, padding: "8px 10px", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
              onClick={() => void connectBrainstem()}
            >
              {brainLogin ? `enter code ${brainLogin.code} on GitHub…` : "🔑 Connect GitHub Copilot — one click, no terminal"}
            </button>
          )}
          {agentLog && <div className="row"><span className="lbl">did</span><span className="val wrap">{agentLog}</span></div>}
          <div className="row">
            <span className={`dot${license?.status === "licensed" ? " on" : license?.status === "expired" ? " bad" : " warn"}`} />
            <span className="lbl">license</span>
            <span className="val">
              {license?.status === "licensed"
                ? `licensed · ${license.email}`
                : license?.status === "expired"
                  ? "trial expired — enter a key"
                  : `trial · ${license?.trialDaysLeft ?? 14} days left`}
            </span>
          </div>
          {license?.status !== "licensed" && (
            <input
              type="text"
              placeholder="paste license key…"
              style={{ width: "100%", marginTop: 6, border: "1px solid rgba(26,34,48,0.12)", borderRadius: 8, padding: "7px 10px", fontSize: "0.78rem", outline: "none", background: "transparent", color: "var(--ink)" }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  const v = e.currentTarget.value.trim();
                  if (v) void window.mirror.licenseActivate(v).then((st) => {
                    setLicense(st);
                    notify(st.status === "licensed" ? `Licensed to ${st.email} — thank you.` : "That key didn't verify.");
                  });
                  e.currentTarget.value = "";
                }
              }}
            />
          )}
        </div>
      )}

      <Rehearsal
        view={rehearsal}
        onConfirm={() => void finishRehearsal("confirmed", "click")}
        onReject={() => void finishRehearsal("rejected", "click")}
        onClose={() => setRehearsal(emptyRehearsal)}
      />

      {/* Someone handed you an agent: shows the card, installs nothing. */}
      <ArrivalCard />

      {forge.phase !== "hidden" && (
        <section id="forge">
          <h2>The Forge — shot anywhere</h2>
          {forge.phase === "distilling" && <div>Distilling what the mirror has seen…</div>}
          {forge.phase === "error" && (
            <>
              <div className="err">{forge.error}</div>
              <button onClick={() => setForge({ phase: "hidden" })}>close</button>
            </>
          )}
          {forge.spec && (
            <>
              <div className="spec-title">{forge.spec.title}</div>
              <div className="spec-desc">{forge.spec.description}</div>
              <ol>
                {forge.spec.steps.map((s, i) => (
                  <li key={i}><b>{s.title}</b> — {s.detail}</li>
                ))}
              </ol>
              <div>
                <button className="primary" disabled={forge.phase === "busy"} onClick={() => void forgeDeploy()}>⚡ Deploy to brainstem</button>
                <button disabled={forge.phase === "busy"} onClick={() => void forgeExport()}>⇩ Export agent.py + SKILL.md + Copilot Studio .zip</button>
                <button onClick={() => setForge({ phase: "hidden" })}>Close</button>
              </div>
              {forge.artifacts?.ok && (
                <div className="paths">
                  <span className="ok">exported ✓</span>{" "}
                  <a href="#" onClick={(e) => { e.preventDefault(); void window.mirror.forgeReveal(forge.artifacts!.agentPath!); }}>reveal in Finder</a>
                  <br />{forge.artifacts.agentPath}<br />{forge.artifacts.skillPath}<br />{forge.artifacts.solutionPath}
                </div>
              )}
              {forge.deploy && (
                <div className="paths">
                  {forge.deploy.ok
                    ? <span className="ok">live in the brainstem ✓ — {forge.deploy.path}</span>
                    : <span className="err">deploy: {forge.deploy.error || (forge.deploy.quarantined ? "quarantined by the kernel" : "not listed yet")}</span>}
                </div>
              )}
            </>
          )}
        </section>
      )}

      {reflections.length > 0 && (
        <div id="stickies">
          {reflections.map((r) => (
            <div key={r.id} className={`sticky ${r.status}`}>
              <div className="goal">{r.goal}</div>
              <div className="note">{r.note}</div>
              <div className="meta">
                <span>{r.status === "done" ? "✓ done" : r.status === "paused" ? "paused" : `looping · turn ${r.turns}`}</span>
                <span className="acts">
                  {r.status !== "done" && (
                    <button onClick={() => setReflections((rs) => rs.map((x) => x.id === r.id ? { ...x, status: x.status === "paused" ? "running" : "paused" } : x))}>
                      {r.status === "paused" ? "▶" : "⏸"}
                    </button>
                  )}
                  <button onClick={() => setReflections((rs) => rs.filter((x) => x.id !== r.id))}>✕</button>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <video
        id="camview"
        className="preview"
        ref={camVideoRef}
        autoPlay
        muted
        playsInline
        title="Drag me anywhere"
        onPointerDown={dragPreview("mirror.campos", setCamPos)}
        style={{ display: camOn ? "block" : "none", ...posStyle(camPos) }}
      />
      <video
        id="screenview"
        className="preview"
        ref={scrVideoRef}
        autoPlay
        muted
        playsInline
        title="Drag me anywhere"
        onPointerDown={dragPreview("mirror.scrpos", setScrPos)}
        style={{ display: scrOn ? "block" : "none", ...posStyle(scrPos) }}
      />

      <VoiceWave micRef={micLevelRef} aiRef={aiLevelRef} />

      {cursor && (
        <div
          id="cursor"
          className={`${cursor.kind}${cursor.pinching ? " pinch" : ""}`}
          style={{ left: cursor.x, top: cursor.y, "--p": cursor.progress } as React.CSSProperties}
        />
      )}
      {gestureFlash && cursor && (
        <div id="gflash" style={{ left: cursor.x, top: cursor.y }}>{gestureFlash}</div>
      )}

      {ghost && (
        <div id="ghostchip" className={ghost.ready ? "ready" : ""} style={{ left: ghost.x, top: ghost.y }}>
          💬 {ghost.label}
          <span className="hint">{ghost.ready ? "release → board" : "drag to the Brain Surgeon →"}</span>
        </div>
      )}

      <Surgeon
        open={surgeonOpen}
        onToggle={() => setSurgeonOpen((s) => !s)}
        onLayoutChange={onSurgeonLayout}
        dropReady={Boolean(ghost?.ready)}
        chats={detached}
        onChatSend={(id, text) => void chipAsk(id, text)}
        onChatClose={(id) => setDetached((ds) => ds.filter((x) => x.id !== id))}
      />

      <div id="toast" className={toast ? "show" : ""}>{toast}</div>
    </div>
  );
}

/* ── voice wave: who the room hears, over time ───────────────────────── */

/** Podcast-style scrolling wave. Every 50ms slot keeps BOTH amplitudes —
 *  blue = your microphone, purple = the AI's voice — drawn layered so
 *  simultaneous speech (barge-in) is visible as both colors at once. */
function VoiceWave({
  micRef,
  aiRef,
}: {
  micRef: React.MutableRefObject<{ v: number; t: number }>;
  aiRef: React.MutableRefObject<{ v: number; t: number }>;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current!;
    const W = 560;
    const H = 64;
    canvas.width = W * 2;
    canvas.height = H * 2;
    const ctx = canvas.getContext("2d")!;
    ctx.scale(2, 2);
    const SLOTS = 128;
    const buf: { mic: number; ai: number }[] = Array.from({ length: SLOTS }, () => ({ mic: 0, ai: 0 }));
    const FRESH_MS = 170;
    const tick = setInterval(() => {
      const now = performance.now();
      buf.shift();
      buf.push({
        mic: now - micRef.current.t < FRESH_MS ? micRef.current.v : 0,
        ai: now - aiRef.current.t < FRESH_MS ? aiRef.current.v : 0,
      });
    }, 50);
    let raf = 0;
    const bw = W / SLOTS;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < SLOTS; i++) {
        const { mic, ai } = buf[i];
        const x = i * bw;
        if (ai > 0.015) {
          const h = Math.max(4, ai * (H - 8));
          ctx.fillStyle = "rgba(139, 142, 249, 0.85)"; // the AI — purple
          ctx.fillRect(x, (H - h) / 2, bw - 1.2, h);
        }
        if (mic > 0.015) {
          const h = Math.max(4, mic * (H - 8));
          ctx.fillStyle = "rgba(59, 130, 246, 0.9)"; // you — blue
          ctx.fillRect(x + bw * 0.22, (H - h) / 2, bw * 0.56, h);
        }
        if (ai <= 0.015 && mic <= 0.015) {
          ctx.fillStyle = "rgba(138, 147, 163, 0.35)"; // idle baseline
          ctx.fillRect(x, H / 2 - 1, bw - 1.2, 2);
        }
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => {
      clearInterval(tick);
      cancelAnimationFrame(raf);
    };
  }, [micRef, aiRef]);
  return (
    <div id="voicewave" title="Who the room hears — blue is your microphone, purple is the AI's voice">
      <canvas ref={canvasRef} style={{ width: 560, height: 64 }} />
      <div className="legend">
        <span className="you">● you</span>
        <span className="ai">● the mirror</span>
      </div>
    </div>
  );
}

/* ── orb dressing ────────────────────────────────────────────────────── */

/** The form at the center is alive — every turn reshapes it. The blob gains
 *  vertices and irregularity with each conversation turn (rapp-vui grammar). */
function blobPath(turns: number): string {
  const n = Math.min(10 + turns * 2, 30);
  let seed = 13 + turns * 31;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const jitter = 3 + Math.min(turns * 1.2, 9);
  const pts: string[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    const r = 47 - jitter / 2 + rnd() * jitter;
    pts.push(`${(50 + Math.cos(a) * r).toFixed(1)} ${(50 + Math.sin(a) * r).toFixed(1)}`);
  }
  return `M${pts.join(" L")} Z`;
}

function Particles({ active, turns }: { active: boolean; turns: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current!;
    canvas.width = 640;
    canvas.height = 640;
    const ctx = canvas.getContext("2d")!;
    const dots = Array.from({ length: Math.min(90 + turns * 18, 320) }, () => ({
      a: Math.random() * Math.PI * 2,
      r: 170 + Math.random() * 145,
      s: 0.0004 + Math.random() * 0.0012,
      size: 1.5 + Math.random() * 2.2,
      alpha: 0.25 + Math.random() * 0.55,
      wobble: Math.random() * Math.PI * 2,
    }));
    let raf = 0;
    const draw = (t: number) => {
      ctx.clearRect(0, 0, 640, 640);
      if (active) {
        for (const d of dots) {
          const a = d.a + t * d.s;
          const r = d.r + Math.sin(t / 900 + d.wobble) * 14;
          ctx.globalAlpha = d.alpha * (0.7 + 0.3 * Math.sin(t / 700 + d.wobble));
          ctx.fillStyle = "#f472b6";
          ctx.fillRect(320 + Math.cos(a) * r, 320 + Math.sin(a) * r * 0.92, d.size, d.size);
        }
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [active, turns]);
  return <canvas id="particles" ref={ref} />;
}

function Wireframe({ active, turns }: { active: boolean; turns: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current!;
    const SIZE = 640;
    canvas.width = SIZE;
    canvas.height = SIZE;
    const ctx = canvas.getContext("2d")!;

    // A true 3D lat/lon sphere with diagonal struts (the geodesic cradle from
    // the rapp-vui POC), tilted toward the viewer and slowly turning — and,
    // like the VUI, it grows denser with every conversation turn.
    const LAT = Math.min(5 + Math.floor(turns / 2) * 2, 13);
    const LON = Math.min(14 + turns * 2, 32);
    const R = 172;
    const verts: [number, number, number][] = [];
    for (let la = 0; la <= LAT; la++) {
      const phi = (la / LAT) * Math.PI; // 0 top -> PI bottom
      for (let lo = 0; lo < LON; lo++) {
        const theta = (lo / LON) * Math.PI * 2;
        verts.push([
          R * Math.sin(phi) * Math.cos(theta),
          R * Math.cos(phi),
          R * Math.sin(phi) * Math.sin(theta),
        ]);
      }
    }
    const at = (la: number, lo: number) => la * LON + ((lo % LON) + LON) % LON;
    const edges: [number, number][] = [];
    for (let la = 0; la < LAT; la++) {
      for (let lo = 0; lo < LON; lo++) {
        edges.push([at(la, lo), at(la, lo + 1)]); // ring
        edges.push([at(la, lo), at(la + 1, lo)]); // meridian
        edges.push([at(la, lo), at(la + 1, lo + 1)]); // diagonal -> triangles
      }
    }

    const TILT = 0.42;
    const cosT = Math.cos(TILT);
    const sinT = Math.sin(TILT);
    let raf = 0;
    const draw = (t: number) => {
      ctx.clearRect(0, 0, SIZE, SIZE);
      const rot = t * 0.00022;
      const cosR = Math.cos(rot);
      const sinR = Math.sin(rot);
      const cx = SIZE / 2;
      const cy = SIZE / 2 + 4;
      const proj = verts.map(([x, y, z]) => {
        const rx = x * cosR + z * sinR; // spin around Y
        const rz = z * cosR - x * sinR;
        const ry = y * cosT - rz * sinT; // tilt toward the viewer
        const rz2 = y * sinT + rz * cosT;
        return [cx + rx, cy - ry, rz2] as const;
      });
      ctx.lineWidth = 1;
      for (const [a, b] of edges) {
        const [ax, ay, az] = proj[a];
        const [bx, by, bz] = proj[b];
        // the cradle: only the lower band of the sphere, depth-faded
        const bandA = (ay - cy) / R;
        const bandB = (by - cy) / R;
        if (bandA < 0.28 && bandB < 0.28) continue; // keep the lower hemisphere
        const depth = (az + bz) / (2 * R); // -1 back .. 1 front
        const alpha = 0.1 + 0.32 * (depth + 1) * 0.5;
        ctx.strokeStyle = active
          ? `rgba(255, 255, 255, ${alpha + 0.1})`
          : `rgba(110, 145, 245, ${alpha})`;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.stroke();
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [active, turns]);
  return <canvas id="wire" ref={ref} />;
}

/* ── icons ───────────────────────────────────────────────────────────── */

const MicIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <rect x="9" y="3" width="6" height="11" rx="3" />
    <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
  </svg>
);
const EyeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
    <circle cx="12" cy="12" r="2.6" />
  </svg>
);
const SpeakerIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 5 6.5 9H3v6h3.5L11 19V5Z" />
    <path d="M15.5 8.5a5 5 0 0 1 0 7M18.4 6a9 9 0 0 1 0 12" />
  </svg>
);
const SpeakerOffIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 5 6.5 9H3v6h3.5L11 19V5Z" />
    <path d="m16 9 5 5m0-5-5 5" />
  </svg>
);
const PlusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <path d="M12 5v14M5 12h14" />
  </svg>
);
const MonitorIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <rect x="3" y="4" width="18" height="13" rx="2" />
    <path d="M9 21h6m-3-4v4" />
  </svg>
);
const HammerIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="m14 4 6 6-2.5 2.5L11.5 6.5 14 4ZM11.5 6.5 4 14l6 6 7.5-7.5" />
  </svg>
);
const InfoIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8h.01M12 11v5" />
  </svg>
);
