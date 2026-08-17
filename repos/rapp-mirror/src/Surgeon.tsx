import { useCallback, useEffect, useRef, useState } from "react";

import type { SurgeonEventView } from "../common/ipc.ts";
import { renderMd } from "./md.tsx";

/**
 * The Brain Surgeon: GitHub Copilot in agent mode, operating on the live
 * brainstem — in the vbrainstem HERD grammar. Two modes:
 *
 *  - **Dock** — the narrow right panel: the herd stacked as status cards.
 *  - **Herd** — wide grid of FULL chat panes (multiple agents, one brainstem),
 *    each with its own composer, READY/WORKING/DONE chip, and ✕. "+ New chat"
 *    spawns an empty pane whose suggestions message that pane only.
 *
 * Portals dragged from the mirror land here as brainstem chat panes and join
 * the same herd. Closed, the whole thing slides off-screen right; an edge tab
 * reshows it.
 */

interface Msg {
  who: "user" | "surgeon" | "tool" | "error";
  text: string;
}

interface Op {
  id: string;
  title: string;
  busy: boolean;
  error: boolean;
  expanded: boolean;
  msgs: Msg[];
}

const SUGGESTIONS = [
  "Build an agent for MY real use case — interview me",
  "Build the Daily Closeout agent — totals by category, then export closeout.xlsx",
  "Build the Artifact Loan agent (Gallery Systems EmbARK) — synthetic records, test it live",
  "Build the Food Truck Fleet agent (Dynamics 365 Field Service) — check truck FT-004",
];

/** A portal dragged onto the board: a plain brainstem chat pane in the herd. */
export interface BoardChat {
  id: string;
  label: string;
  expanded: boolean;
  busy: boolean;
  msgs: { u: string; a: string }[];
}

interface SurgeonProps {
  open: boolean;
  onToggle: () => void;
  /** Herd layout signal: wide mode + how many panes — the dock width follows
   *  the herd's size (one pane never needs the whole screen). */
  onLayoutChange(wide: boolean, cards: number): void;
  /** True while a portal is being dragged over the drop zone. */
  dropReady: boolean;
  chats: BoardChat[];
  onChatSend(id: string, text: string): void;
  onChatClose(id: string): void;
}

export default function Surgeon({ open, onToggle, onLayoutChange, dropReady, chats, onChatSend, onChatClose }: SurgeonProps) {
  const [ops, setOps] = useState<Op[]>([]);
  const [wide, setWide] = useState(false);
  const [err, setErr] = useState("");
  const composerRef = useRef<HTMLTextAreaElement>(null);
  const opsRef = useRef(ops);
  opsRef.current = ops;

  useEffect(() => {
    return window.mirror.onSurgeonEvent((ev: SurgeonEventView) => {
      setOps((prev) =>
        prev.map((op) => {
          if (op.id !== ev.sessionId) return op;
          if (ev.kind === "tool") return { ...op, msgs: [...op.msgs, { who: "tool", text: ev.text }] };
          if (ev.kind === "report") return { ...op, msgs: [...op.msgs, { who: "surgeon", text: ev.text }], busy: false };
          if (ev.kind === "error") return { ...op, msgs: [...op.msgs, { who: "error", text: ev.text }], busy: false, error: true };
          if (ev.kind === "done") return { ...op, busy: false };
          return op;
        }),
      );
    });
  }, []);

  const toggleHerd = useCallback(() => setWide((w) => !w), []);

  /** "+ New chat": an empty pane in the herd, ready for its first instruction. */
  const newChat = useCallback(async (): Promise<string | null> => {
    setErr("");
    const r = await window.mirror.surgeonCreate();
    if (!r.ok || !r.id) {
      setErr(r.error || "could not start Copilot");
      return null;
    }
    setOps((prev) => [
      { id: r.id!, title: "New chat", busy: false, error: false, expanded: true, msgs: [] },
      ...prev,
    ]);
    return r.id;
  }, []);

  /** Send into a specific operation pane. */
  const sendToOp = useCallback(async (id: string, text: string) => {
    const t = text.trim();
    if (!t) return;
    setOps((prev) =>
      prev.map((o) =>
        o.id === id
          ? { ...o, title: o.title === "New chat" ? t.slice(0, 44) : o.title, busy: true, msgs: [...o.msgs, { who: "user", text: t }] }
          : o,
      ),
    );
    const res = await window.mirror.surgeonSend(id, t);
    if (!res.ok && res.error) setErr(res.error);
  }, []);

  /** The dock-mode bottom composer: spawn a new operation with its first task. */
  const operate = useCallback(
    async (text: string) => {
      const t = text.trim();
      if (!t) return;
      const id = await newChat();
      if (id) void sendToOp(id, t);
    },
    [newChat, sendToOp],
  );

  const closeOp = useCallback((id: string) => {
    setOps((prev) => prev.filter((o) => o.id !== id));
    void window.mirror.surgeonClose(id);
  }, []);

  const opState = (op: Op) =>
    op.busy ? "working" : op.error ? "error" : op.msgs.length ? "done" : "ready";

  const cardCount = ops.length + chats.length;

  useEffect(() => {
    onLayoutChange(wide, cardCount);
  }, [wide, cardCount, onLayoutChange]);

  const renderOpMsgs = (op: Op) => (
    <>
      {op.msgs.map((m, i) =>
        m.who === "tool" ? (
          <div key={i} className="toolline">▸ {m.text}</div>
        ) : (
          <div key={i} className={`msg ${m.who}`}>
            {m.who === "user" ? m.text : renderMd(m.text)}
          </div>
        ),
      )}
      {op.busy && <div className="toolline pulse">◌ operating…</div>}
    </>
  );

  const miniHero = (opId: string) => (
    <div className="minihero">
      <div className="cloud">🧠</div>
      <h2>GitHub Copilot, in your brainstem</h2>
      <p>The real Copilot agent loop — describe an agent and it writes the file into your workspace, <b>hot-loads it, and tests it live</b>.</p>
      <div className="chips">
        <span>▶ run python</span>
        <span>📄 read/write files</span>
        <span>🧠 test the brainstem</span>
      </div>
      <div className="suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s} onClick={() => void sendToOp(opId, s)}>{s}</button>
        ))}
      </div>
    </div>
  );

  return (
    <>
      <aside id="surgeon" className={`${open ? "open" : ""}${wide ? " wide" : ""}${dropReady ? " dropready" : ""}`}>
        <header>
          <span className="brand">🧠</span>
          <div className="who">
            <b>GitHub Copilot{wide ? " · Herd" : ""}</b>
            <span>{wide ? "multiple agents, one brainstem" : "Brain Surgeon · agent mode"}</span>
          </div>
          <button className="badge action" onClick={() => void newChat()}>+ New chat</button>
          <button className="badge action" onClick={toggleHerd}>{wide ? "Dock ▸" : "⊞ Herd"}</button>
          <button className="x" title="Hide (the tab brings it back)" onClick={onToggle}>✕</button>
        </header>

        <div className={`body${wide ? " herdgrid" : ""}`}>
          {cardCount === 0 && (
            <div className="hero">
              <div className="cloud">🧠</div>
              <h1>GitHub Copilot, in your brainstem</h1>
              <p>
                The real Copilot agent loop — describe an agent and it writes the file into your
                workspace, <b>hot-loads it, and tests it live</b>. Every chat joins the herd:
                multiple agents, one brainstem. Drag a portal from the mirror here to keep it as
                its own conversation.
              </p>
              <div className="chips">
                <span>▶ run python</span>
                <span>📄 read/write files</span>
                <span>🧠 test the brainstem</span>
              </div>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} onClick={() => void operate(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}

          {chats.map((c) => (
            <section key={c.id} className="pane chat">
              <div className="phead">
                <span className={`glyph${c.busy ? " pulse" : ""}`}>{c.busy ? "◌" : "💬"}</span>
                <span className="ptitle">{c.label}</span>
                <span className={`pstate ${c.busy ? "working" : "done"}`}>{c.busy ? "WORKING" : "READY"}</span>
                <button className="pclose" title="Dismiss" onClick={() => onChatClose(c.id)}>✕</button>
              </div>
              <div className="pbody">
                {c.msgs.map((m, i) => (
                  <div key={i}>
                    <div className="msg user">{m.u}</div>
                    <div className="msg surgeon">{renderMd(m.a)}</div>
                  </div>
                ))}
              </div>
              <div className="pfoot">
                <input
                  type="text"
                  placeholder="Message this chat…"
                  disabled={c.busy}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      const v = e.currentTarget.value;
                      e.currentTarget.value = "";
                      onChatSend(c.id, v);
                    }
                  }}
                />
              </div>
            </section>
          ))}

          {ops.map((op) => (
            <section key={op.id} className={`pane op${op.busy ? " busy" : ""}`}>
              <div className="phead">
                <span className={`glyph${op.busy ? " pulse" : ""}`}>{op.busy ? "◌" : op.error ? "⚠" : "🛠"}</span>
                <span className="ptitle">{op.title}</span>
                <span className={`pstate ${opState(op)}`}>{opState(op).toUpperCase()}</span>
                <button className="pclose" title="Close this operation" onClick={() => closeOp(op.id)}>✕</button>
              </div>
              <div className="pbody">{op.msgs.length === 0 && !op.busy ? miniHero(op.id) : renderOpMsgs(op)}</div>
              <div className="pfoot">
                <input
                  type="text"
                  placeholder="Message this Copilot…"
                  disabled={op.busy}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      const v = e.currentTarget.value;
                      e.currentTarget.value = "";
                      void sendToOp(op.id, v);
                    }
                  }}
                />
              </div>
            </section>
          ))}
          {err && <div className="msg error">{err}</div>}
        </div>

        {!wide && (
          <footer>
            <textarea
              ref={composerRef}
              rows={2}
              placeholder="Describe what to build — each build joins the herd…"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  const v = e.currentTarget.value;
                  e.currentTarget.value = "";
                  void operate(v);
                }
              }}
            />
            <div className="row">
              <span className="hint">🛠 Agent · writes into the live brainstem</span>
              <button
                className="build"
                onClick={() => {
                  const v = composerRef.current?.value ?? "";
                  if (composerRef.current) composerRef.current.value = "";
                  void operate(v);
                }}
              >
                Build
              </button>
            </div>
            <div className="fine">runs on your GitHub Copilot account · ⌘↵ to send</div>
          </footer>
        )}
      </aside>
      {!open && (
        <button
          id="surgeontab"
          className={dropReady ? "dropready" : ""}
          title="Brain Surgeon — Copilot agent mode"
          onClick={onToggle}
        >
          🧠<span>Brain&nbsp;Surgeon</span>
        </button>
      )}
    </>
  );
}
