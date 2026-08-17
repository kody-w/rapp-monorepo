import type {
  RehearsalRunState,
  RehearsalStepRecord,
  RehearsalTranscript,
  RehearsalVerdict,
  RehearsalWorld,
} from "../common/ipc.ts";

/**
 * The Rehearsal stage — the virtual twin performing the automation while the
 * user watches. Presentational only: Mirror.tsx owns the run (IPC + events),
 * the portals, and the nod/shake grammar; this renders what the twin did and
 * hosts the one question that matters: "did this complete the job?"
 * Always badged VIRTUAL — a rehearsal is a simulation, never an execution.
 */

export interface RehearsalView {
  open: boolean;
  running: boolean;
  state: RehearsalRunState | null;
  scenario: string;
  world: RehearsalWorld | null;
  sampleInputs: Record<string, string | number | boolean>;
  steps: RehearsalStepRecord[];
  totalSteps: number;
  verdict: RehearsalVerdict | null;
  transcript: RehearsalTranscript | null;
  error: string;
}

export const emptyRehearsal: RehearsalView = {
  open: false,
  running: false,
  state: null,
  scenario: "",
  world: null,
  sampleInputs: {},
  steps: [],
  totalSteps: 0,
  verdict: null,
  transcript: null,
  error: "",
};

const phaseLine = (v: RehearsalView): string => {
  if (v.state === "seeding") return "Dreaming up the world…";
  if (v.state === "running") return `Rehearsing step ${Math.min(v.steps.length + 1, v.totalSteps)} of ${v.totalSteps}…`;
  if (v.state === "judging") return "Judging the outcome…";
  return "";
};

export default function Rehearsal({
  view,
  onConfirm,
  onReject,
  onClose,
}: {
  view: RehearsalView;
  onConfirm: () => void;
  onReject: () => void;
  onClose: () => void;
}) {
  if (!view.open) return null;
  const awaiting = view.state === "awaiting-confirmation";
  const failed = view.state === "stalled" || view.state === "error";
  return (
    <section id="rehearsal">
      <h2>
        The Rehearsal — the twin runs it first <span className="virtual">VIRTUAL</span>
      </h2>

      {view.scenario && <div className="scenario">{view.scenario}</div>}

      {view.world && view.world.entities.length > 0 && (
        <div className="world">
          {view.world.entities.map((e) => (
            <span key={e.id} className="entity" title={e.detail}>
              <b>{e.name}</b>
              {e.state ? ` — ${e.state}` : ""}
            </span>
          ))}
        </div>
      )}

      {view.steps.length > 0 && (
        <ol className="runsteps">
          {view.steps.map((s) => (
            <li key={s.index} className={s.status}>
              <b>{s.title}</b> — {s.action} {s.status === "blocked" ? "🚫" : "✓"}
              {s.note && <span className="note"> ({s.note})</span>}
              {s.changes.map((c, i) => (
                <div key={i} className="change">
                  {c.entity}.{c.field}: “{c.before}” → “{c.after}”
                </div>
              ))}
              {s.observation && <div className="obs">{s.observation}</div>}
            </li>
          ))}
        </ol>
      )}

      {view.running && <div className="phase">{phaseLine(view)}</div>}

      {failed && (
        <div className="err">
          The rehearsal {view.state === "error" ? "hit an engine error" : "stalled"} — {view.error || "the twin lost the thread"}.
          A failed run can never be confirmed; fix the spec or the engine and rehearse again.
        </div>
      )}

      {view.verdict && (
        <div className={`verdict ${view.verdict.complete ? "complete" : "incomplete"}`}>
          {view.verdict.complete ? "✅" : "⚠️"} {view.verdict.summary}
          {view.verdict.gaps.map((g, i) => (
            <div key={i} className="gap">gap: {g}</div>
          ))}
        </div>
      )}

      {awaiting && (
        <>
          <div className="question">Did this complete the job — fully done?</div>
          <div>
            <button className="primary" onClick={onConfirm}>👍 Fully done — deploy it</button>
            <button onClick={onReject}>✋ Not right yet</button>
          </div>
          <div className="hint">nod or say “fully done” · shake or say “not right”</div>
        </>
      )}

      {view.state === "confirmed" && <div className="ok">Confirmed — deploying to the brainstem…</div>}
      {view.state === "rejected" && (
        <div className="phase">
          Rejected. Tell the mirror what was wrong, then say “make this an automation” to forge the fix.
        </div>
      )}

      {!awaiting && !view.running && <button onClick={onClose}>Close</button>}
    </section>
  );
}
