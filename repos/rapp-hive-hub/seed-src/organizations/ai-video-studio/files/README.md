# The AI Video Studio: pilot case starter

Everything a new studio needs to run its first production: a 40-second
vertical short that explains how a WebSocket connection starts. The script,
the claim ledger and the reference timings are original studio material; the
facts are pinned to the public text of RFC 6455.

| File | What it is |
|---|---|
| `case/pilot.json` | deliverable spec, source options, must-show beats, gates |
| `source/script.md` | the two-voice narration to record (or synthesize) |
| `source/reference-words.json` | real word timings of a synthesized reference read, for pacing only |
| `source/claims.json` | every line's claims, with RFC 6455 line anchors and snippets |
| `source/corpus.json` | where to fetch RFC 6455 and the sha256 its bytes must match |
| `brand/house-kit.md`, `brand/tokens.json` | the house look: type, colour, zones, captions, motion |
| `board/motion-board-template.md` | the motion board format (plan before building) |
| `refs/*.svg` | reference images for the typing window and the server-answer panel |
| `guides/operating-loop.md` | how the nine teams run a production, step by step |
| `guides/prompts.md` | the studio's prompt library, from brief to iteration |
| `guides/effects.md` | effect catalogue with HyperFrames implementation notes |
| `guides/transcription.md` | the words.json contract and how to produce it |
| `project/*.html` | starter HyperFrames overlay compositions (hook card, typing window, UI panel) |
| `tools/caption-phraser.mjs` | words.json + kit -> caption phrases, SRT, and a trace check |
| `tools/transcribe.mjs` | word-timed transcript via ElevenLabs Scribe or local Whisper |
| `tools/check-kit.mjs` | validates a brand kit's tokens, fonts and zones |
| `quality/review-checklist.csv` | the QC rows the cut must pass |
| `ops/release-checklist.md` | what the release package contains |

The task board orders the work. Claim a ready task, meet its acceptance
criteria, attach the artifact and the evidence. Reference files show the
intended look and pacing; they are not completed deliverables.

The tools are inert until your own AI or operator reviews and runs them on a
machine with Node 18+, ffmpeg and the HyperFrames CLI.
