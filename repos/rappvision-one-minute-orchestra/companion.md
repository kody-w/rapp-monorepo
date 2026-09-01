TITLE: One Minute Orchestra — Proof in Four Voices  
OUTPUT: A paired 32-second square audiovisual performance and deterministic live step sequencer  
OWNER: Worker 08 / Asha Bell channel pilot  
STATUS: accepted

WHAT IT IS:

A music-led pilot for fictional composer Asha Bell. Four proof events become four visible and audible parts: Pulse observes, Prism verifies, Verdant applies, and Pearl seals.

WHY IT MATTERS:

It makes provenance legible without narration, then hands the same model to the viewer. The replay preserves a locked canonical source while allowing a clearly labeled, noncanonical remix.

LOCATION:

- Encoded performance: `media/one-minute-orchestra.mp4` and `media/one-minute-orchestra.webm`
- Live replay: `live/index.html`
- Thumbnail: `thumbs/one-minute-orchestra.svg`
- Production source: `index.html`, `audio/generate_score.py`, and `audio/provenance.json`

EVIDENCE:

Both encodes are square, contain stereo audio, and probe as H.264/AAC and VP9/Opus. `evidence.json` binds their SHA-256 hashes, records -18.0 LUFS integrated loudness, and cites passing composition and deterministic-reset checks.

BOUNDARIES:

Asha Bell is fictional/synthetic. The score is wholly original local synthesis with no samples, recordings, stock media, customer data, private URLs, or factual claims about real people. The remix is never called canonical.

KNOWN COMPROMISES:

The live replay uses browser Web Audio synthesis rather than replaying the rendered master, so timbre is intentionally close but not byte-identical. The performance is 32 seconds, within the requested 25–40 second pilot window.

NEXT DECISION:

The orchestrator decides whether this well passes the season-wide diversity and constitutional integration gates.
