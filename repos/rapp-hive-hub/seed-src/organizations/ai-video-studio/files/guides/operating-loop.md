# Operating loop

One front door, nine teams, one loop. The loop adapts a public creator's
method for editing short-form video with an AI coding agent and HyperFrames
(https://www.youtube.com/watch?v=z6zkeILNHL8) into an organization with
explicit handoffs and gates. This guide is the studio's own restatement.

## The loop

| # | Step | Team | Output |
|---|---|---|---|
| 1 | Brief | Showrunner | `BRIEF.md`: audience, platform, length, hook, source, kit, out of scope |
| 2 | Script lock | Explainer Lab | every factual line mapped to a verified claim; script sha256 recorded |
| 3 | Take | Explainer Lab | the recorded or synthesized source, with hash and capture notes |
| 4 | Transcript | Transcription Desk | `words.json`: word-level timestamps on the source timeline |
| 5 | Motion board | Motion Board Room | timestamped plan: hook, cuts, overlay beats with zone, effect, words, claim |
| 6 | Board approval | owner (presented by the Showrunner's Office) | approval record with the board's sha256; nothing is built before it |
| 7 | Captions | Captions Desk | short unpunctuated phrases, placed away from the face and overlays |
| 8 | Build | Motion Graphics Shop | HyperFrames project: cuts, overlays, captions; lint and check clean |
| 9 | Claim carryover | Explainer Lab | every on-screen technical statement mapped to a verified claim |
| 10 | QC | Quality Control | report plus a contact sheet reviewed against the board |
| 11 | Final approval | owner (presented by the Showrunner's Office) | approval record with the project commit |
| 12 | Release package | Release Desk | MP4, SRT, cover, post copy, provenance; never published by the org |
| 13 | Kit retro | Brand Studio | kit changes proposed from what QC found |

## Principles

- **Plan before building.** The motion board is written in plan mode and
  approved before any composition exists. Iteration after the build is short
  and specific ("move the panel up 40 px", "type at speaking pace").
- **Brand by name.** A kit (type, colour, zones, caption style, motion) is
  loaded by name, so no prompt re-describes the look.
- **Placement is deliberate.** Never cover the face, stay clear of the frame
  edges, use empty space. One overlay per zone at a time; captions move when
  an overlay needs their zone. Each overlay is tied to the spoken words that
  trigger it.
- **Captions are short.** One to four words, no punctuation, the spoken word
  highlighted.
- **Effects start from a reference.** A screenshot or sketch of the target
  look goes with every effect request.
- **Voice first.** The owner dictates every request to their own AI, which
  confirms the plan in two lines and does the work. The Showrunner's Office
  is a stage behind that AI, not a separate bot.
- **Facts are pinned.** Technical statements come from a pinned corpus and a
  claim ledger; a derived cut may simplify wording, never add facts.
- **Owner authority.** Uploading, publishing, spending and sharing media
  outside the studio belong to the owner, never to the org.

## Project layout (one folder per production)

```
productions/<slug>/
  BRIEF.md  motion-board.md  approvals/
  raw/                 source media (not in git)
  transcript/          words.json, transcript.txt, meta.json
  brand/               tokens.json, design.md for this production
  compositions/        overlays/*.html, captions.html
  index.html           root HyperFrames composition (1080x1920)
  renders/ snapshots/  outputs (not in git)
```

## Tools you need

Node 18 or newer, ffmpeg and ffprobe, and the HyperFrames CLI
(`npx hyperframes`, pin one version for the whole studio). Optional: an
ElevenLabs API key for transcription, kept in the production's `.env`.
