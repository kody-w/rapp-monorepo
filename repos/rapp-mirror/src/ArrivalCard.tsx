import { useCallback, useEffect, useState } from "react";

import type { AgentCard } from "../common/agentcard.ts";
import type { ArrivedAgentView } from "../common/ipc.ts";
import { AgentTradingCard } from "./AgentTradingCard.tsx";
import "./ArrivalCard.css";

/**
 * Someone handed you an agent.
 *
 * This is the consent moment, and it is deliberately unhurried: the card,
 * what the sender says it does, and — plainly — everything it can actually
 * reach for. Nothing has been installed to get here; the agent is sitting in
 * the inbox. Accepting is a separate act, and a dangerous card makes you say
 * so twice.
 */
export function ArrivalCard() {
  const [arrival, setArrival] = useState<ArrivedAgentView | null>(null);
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<string | null>(null);

  useEffect(() => window.mirror.onAgentArrived?.(setArrival), []);

  const dismiss = useCallback(() => {
    setArrival(null);
    setOutcome(null);
  }, []);

  const accept = useCallback(
    async (acceptDangerous: boolean) => {
      if (!arrival?.spec) {
        setOutcome(
          "This arrived as a file rather than a card, so there is no recipe to rebuild — inspect it in the inbox and deploy it yourself.",
        );
        return;
      }
      setBusy(true);
      try {
        const result = await window.mirror.acceptArrival(arrival.spec, { acceptDangerous });
        if (result.ok) {
          setOutcome(`Installed and verified — ${arrival.card?.className} is live.`);
        } else if (result.needsRehearsal) {
          setOutcome(
            "The rehearsal gate refused it: nothing deploys until the twin has run it and you have said it is fully done.",
          );
        } else {
          setOutcome(result.error ?? "It could not be installed.");
        }
      } finally {
        setBusy(false);
      }
    },
    [arrival],
  );

  if (!arrival) return null;

  if (!arrival.ok || !arrival.card?.ok) {
    return (
      <div className="arrival-scrim" onClick={dismiss}>
        <div className="arrival" onClick={(e) => e.stopPropagation()}>
          <h2>That is not an agent</h2>
          <p className="arrival-error">{arrival.error ?? arrival.card?.error}</p>
          <button className="arrival-btn" onClick={dismiss}>
            Close
          </button>
        </div>
      </div>
    );
  }

  const card = arrival.card as AgentCard;
  // Computed in the main process: `agentshare` needs node:zlib, which would
  // take the whole renderer down if it were imported here.
  const shareUrl = arrival.shareUrl;
  const critical = card.findings.filter((f) => f.severity === "critical");
  const warnings = card.findings.filter((f) => f.severity === "warn");

  return (
    <div className="arrival-scrim" onClick={dismiss}>
      <div className="arrival" onClick={(e) => e.stopPropagation()}>
        <header className="arrival-head">
          <span className="arrival-kicker">
            {arrival.origin === "card" ? "A card was scanned" : "An agent was AirDropped"}
          </span>
          <h2>{card.name}</h2>
          <p className="arrival-desc">{card.description || "It came with no description."}</p>
        </header>

        <div className="arrival-body">
          <AgentTradingCard card={card} shareUrl={shareUrl} />

          <div className="arrival-detail">
            {card.steps.length > 0 && (
              <section>
                <h3>What it says it does</h3>
                <ol className="arrival-steps">
                  {card.steps.slice(0, 6).map((step) => (
                    <li key={step}>{step.replace(/^\s*\d+[.)]\s*/, "")}</li>
                  ))}
                </ol>
              </section>
            )}

            <section>
              <h3>What it can reach for</h3>
              {card.findings.length === 0 ? (
                <p className="arrival-clean">
                  Nothing. No shell, no network, no file writes, no credentials.
                </p>
              ) : (
                <ul className="arrival-findings">
                  {[...critical, ...warnings].map((finding) => (
                    <li key={finding.id} className={`finding-${finding.severity}`}>
                      <span className="finding-dot" aria-hidden />
                      <span>
                        {finding.detail}
                        <code>line {finding.line}</code>
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {arrival.origin === "card" && (
              <p className="arrival-note">
                This arrived as a recipe, not as code — your own Forge wrote the Python, so nothing
                of the sender's ran to get here.
              </p>
            )}

            {outcome && <p className="arrival-outcome">{outcome}</p>}

            <div className="arrival-actions">
              <button className="arrival-btn ghost" onClick={dismiss} disabled={busy}>
                Not now
              </button>
              {arrival.dangerous ? (
                <button className="arrival-btn danger" onClick={() => void accept(true)} disabled={busy}>
                  {busy ? "Installing…" : "I trust the sender — install anyway"}
                </button>
              ) : (
                <button className="arrival-btn" onClick={() => void accept(false)} disabled={busy}>
                  {busy ? "Installing…" : "Accept into my brainstem"}
                </button>
              )}
            </div>
            <p className="arrival-parked">
              Until then it sits in <code>{arrival.pendingPath}</code> and runs nowhere.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
