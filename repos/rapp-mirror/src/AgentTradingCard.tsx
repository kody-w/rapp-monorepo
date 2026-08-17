import { useCallback, useRef, useState } from "react";

import "./AgentTradingCard.css";

import type { AgentCard } from "../common/agentcard.ts";
import { mintCard } from "../common/cardart.ts";
import type { ArtWork, Shape } from "../common/cardstyles.ts";
import { encodeQr, qrPath } from "../common/qr.ts";

/**
 * The card.
 *
 * One iconic frame, any medium: the silhouette, the stat positions and the
 * foil behaviour never move, while the art inside comes from whichever artist
 * the agent's fingerprint drew. Flip it and the back carries a QR of the
 * agent's *spec* — show it to a friend's camera and they receive the agent.
 *
 * The tilt is real: pointer position drives an actual 3D transform and moves
 * the foil sweep against it, so the holo behaves like foil rather than a
 * static gradient.
 */

interface Props {
  card: AgentCard;
  /** The `rapp://agent?…` link this card trades. Omit to hide the back. */
  shareUrl?: string;
  styleId?: string;
  onFlip?: (showingBack: boolean) => void;
}

/** Draw one scene-graph primitive. The same data draws on iOS and in Wallet. */
function drawShape(shape: Shape, index: number) {
  const common = { key: index, opacity: shape.kind === "text" ? shape.opacity : shape.opacity };
  switch (shape.kind) {
    case "path":
      return (
        <path
          {...common}
          d={shape.d}
          fill={shape.fill ?? "none"}
          stroke={shape.stroke ?? "none"}
          strokeWidth={shape.width ?? 1}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      );
    case "circle":
      return (
        <circle
          {...common}
          cx={shape.cx}
          cy={shape.cy}
          r={shape.r}
          fill={shape.fill ?? "none"}
          stroke={shape.stroke ?? "none"}
          strokeWidth={shape.width ?? 1}
        />
      );
    case "rect":
      return (
        <rect
          {...common}
          x={shape.x}
          y={shape.y}
          width={shape.w}
          height={shape.h}
          rx={shape.radius ?? 0}
          fill={shape.fill ?? "none"}
          stroke={shape.stroke ?? "none"}
          strokeWidth={shape.width ?? 1}
        />
      );
    case "line":
      return (
        <line
          {...common}
          x1={shape.x1}
          y1={shape.y1}
          x2={shape.x2}
          y2={shape.y2}
          stroke={shape.stroke}
          strokeWidth={shape.width ?? 1}
        />
      );
    case "text":
      return (
        <text
          {...common}
          x={shape.x}
          y={shape.y}
          fill={shape.fill}
          fontSize={shape.size}
          fontFamily={shape.family ?? "inherit"}
          style={{ whiteSpace: "pre" }}
        >
          {shape.text}
        </text>
      );
  }
}

function Art({ art }: { art: ArtWork }) {
  return (
    <svg className="card-art" viewBox={art.viewBox} preserveAspectRatio="xMidYMid slice" aria-hidden>
      <defs>
        <linearGradient id="card-bg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={art.palette.from} />
          <stop offset="100%" stopColor={art.palette.to} />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="100" height="100" fill="url(#card-bg)" />
      {art.shapes.map(drawShape)}
    </svg>
  );
}

export function AgentTradingCard({ card, shareUrl, styleId, onFlip }: Props) {
  const face = mintCard(card, styleId);
  const [flipped, setFlipped] = useState(false);
  const [tilt, setTilt] = useState({ x: 0, y: 0, gx: 50, gy: 50 });
  const ref = useRef<HTMLDivElement | null>(null);

  const onMove = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    const box = ref.current?.getBoundingClientRect();
    if (!box) return;
    const px = (event.clientX - box.left) / box.width;
    const py = (event.clientY - box.top) / box.height;
    setTilt({
      // Deliberately shallow: the foil should move more than the card does.
      x: (0.5 - py) * 16,
      y: (px - 0.5) * 16,
      gx: px * 100,
      gy: py * 100,
    });
  }, []);

  const rest = useCallback(() => setTilt({ x: 0, y: 0, gx: 50, gy: 50 }), []);

  const flip = useCallback(() => {
    setFlipped((was) => {
      onFlip?.(!was);
      return !was;
    });
  }, [onFlip]);

  const qr = shareUrl ? encodeQr(shareUrl) : null;

  return (
    <div
      ref={ref}
      className={`tcg ${flipped ? "is-flipped" : ""} holo-${face.art.holo} rarity-${face.rarity}`}
      style={
        {
          "--from": face.palette.from,
          "--to": face.palette.to,
          "--accent": face.palette.accent,
          "--ink": face.palette.ink,
          "--gx": `${tilt.gx}%`,
          "--gy": `${tilt.gy}%`,
          "--rx": `${tilt.x}deg`,
          "--ry": `${tilt.y}deg`,
        } as React.CSSProperties
      }
      onPointerMove={onMove}
      onPointerLeave={rest}
      onClick={flip}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && flip()}
      aria-label={`${face.title} — ${face.rarity} ${face.element} card. Click to ${flipped ? "see the front" : "see the sharing code"}.`}
    >
      <div className="tcg-inner">
        {/* ── front ── */}
        <div className="tcg-face tcg-front">
          <div className="tcg-foil" />

          <header className="tcg-head">
            <span className="tcg-title">{face.title}</span>
            <span className="tcg-trust">
              <b>{face.trust}</b> TRUST
            </span>
          </header>

          {/* The aperture: art is framed here, never behind the text. */}
          <div className="tcg-window">
            <Art art={face.art} />
            <div className={`tcg-texture texture-${face.art.texture}`} />
            <div className="tcg-window-gloss" />
          </div>

          <div className="tcg-body">
            <div className="tcg-typeline">
              <span className={`tcg-element el-${face.element}`}>{face.element}</span>
              <span className="tcg-rarity">{face.rarity}</span>
            </div>
            {face.moves.map((move) => (
              <div className="tcg-move" key={move.name}>
                <span className="tcg-cost" aria-label={`${move.cost} energy`}>
                  {"●".repeat(move.cost)}
                </span>
                <span className="tcg-move-name">{move.name}</span>
                <span className="tcg-power">{move.power}</span>
                <p className="tcg-move-text">{move.text}</p>
              </div>
            ))}
          </div>

          <footer className="tcg-foot">
            <span className="tcg-flavor">{face.flavor}</span>
            <span className="tcg-credit">
              {face.style.name} · {face.style.medium} · {face.style.artist}
            </span>
            <span className="tcg-dex">{face.dex}</span>
          </footer>
        </div>

        {/* ── back ── */}
        <div className="tcg-face tcg-back">
          <div className="tcg-foil" />
          <span className="tcg-back-mark">RAPP</span>
          {qr ? (
            <>
              <svg className="tcg-qr" viewBox={`-2 -2 ${qr.size + 4} ${qr.size + 4}`} role="img" aria-label="Scan to receive this agent">
                <rect x={-2} y={-2} width={qr.size + 4} height={qr.size + 4} fill="#fff" rx={1} />
                <path d={qrPath(qr)} fill="#0b0b10" shapeRendering="crispEdges" />
              </svg>
              <p className="tcg-back-hint">
                Point a phone at this to receive <b>{face.title}</b>.
                <br />
                It carries the recipe, never the code — their mirror builds it themselves.
              </p>
            </>
          ) : (
            <p className="tcg-back-hint">This agent is too detailed to trade by code — AirDrop the file instead.</p>
          )}
          <span className="tcg-back-dex">{face.dex}</span>
        </div>
      </div>
    </div>
  );
}
