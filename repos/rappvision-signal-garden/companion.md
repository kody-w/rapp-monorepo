# When a Heartbeat Wilts

**Channel:** Signal Garden  
**Creator:** Mina Vale, a fictional synthetic field scientist  
**Pair:** encoded micro-documentary + deterministic live replay

## WHAT IT IS

A 26-second film and live replay showing one bounded synthetic mechanism:
Iris Three's heartbeat changes from **4.0 seconds** to **11.8 seconds**, crosses
an **8.0-second** threshold, wilts, and recovers when the signal returns to 4.0.

## WHY IT MATTERS

The botanical metaphor makes a delayed distributed-system signal visible
without hiding the exact measurement or causal threshold.

## LOCATION

- Film: `media/signal-garden-pulse-lag.mp4` or `.webm`
- Replay: `live/index.html`
- Thumbnail: `thumbs/signal-garden-pulse-lag.svg`

## EVIDENCE

HyperFrames passed with zero errors or warnings during production, but the
production composition source is not included in this package, so that check
cannot be rerun from these files. The shipped encodes were independently fully
decoded and probed. A local Chromium run verified baseline, no-op failure,
anomaly/wilt, healing, and reset. SHA-256 values are recorded in
`evidence.json`.

## BOUNDARIES

All identities, plants, systems, measurements, visuals, narration, and audio
are fictional or locally synthesized. No real infrastructure, telemetry,
person, place, customer, or production data is represented.

## KNOWN COMPROMISES

The replay is a deterministic teaching model, not a production monitoring
interface. Its single threshold is intentionally narrow and synthetic. The
encoded film is delivered without its production composition source.

## NEXT DECISION

Watch the film first, then open the replay:

1. Select **Introduce anomaly** to change Iris Three from 4.0 to 11.8 seconds.
2. Select **Heal signal** to restore the heartbeat and plant.
3. Select **Reset** to return to the canonical baseline.
