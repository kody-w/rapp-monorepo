# Transcription

Captions, cuts and board timings all read one file, so it has to be right
before anyone plans on it.

## Contract: `transcript/words.json`

```json
{
  "schema": "studio-words/1",
  "engine": "scribe",
  "model": "scribe_v2",
  "source": "raw/take.mp4",
  "window": null,
  "language": "en",
  "words": [
    { "text": "How", "start": 0.56, "end": 0.68, "speaker": "S1" }
  ]
}
```

- Times are seconds on the **source** timeline. The build maps them through
  the cuts; never shift them to the output timeline by hand.
- Words keep their spoken spelling and punctuation; captions strip
  punctuation later.
- `transcript.txt` (speaker turns with timestamps) and `meta.json` (engine,
  model, settings, media sha256) sit beside it.

## Producing it: `tools/transcribe.mjs`

```bash
node tools/transcribe.mjs raw/take.mp4                         # Scribe if a key is set, else local Whisper
node tools/transcribe.mjs raw/take.mp4 --terms "WebSocket,Sec-WebSocket-Key,RFC 6455"
node tools/transcribe.mjs raw/take.mp4 --known source/script.md  # read verbatim: script words win
```

- **ElevenLabs Scribe** (default when `ELEVENLABS_API_KEY` is in the
  environment or the production's `.env`): word timestamps and speaker
  labels from `POST /v1/speech-to-text` with model `scribe_v2`. The key is
  read, never printed or written.
- **Local** (fallback): the HyperFrames CLI's `transcribe` command with
  Whisper `small.en` (or Parakeet when installed). Offline once the model is
  cached; one speaker label.
- `--terms` fixes names and product words (case, spaces and hyphens are
  ignored when matching, so "web socket" becomes "WebSocket").
- `--known` reconciles against the script: known words win, recognition gives
  timing, and the agreement figure is reported. Under 95 % means the take
  drifted from the script: keep the recognized words and flag it.

## Desk checklist

1. Transcribe the take; fix terms.
2. Reconcile with the script when one exists.
3. Read `transcript.txt` end to end; fix remaining text errors in
   `words.json` (never reorder words or move times backwards).
4. Compare pacing with `source/reference-words.json` if the board needs a
   target length; trims belong to the board, not the transcript.
5. Hand off the path, engine, model and agreement figure.

Never ask anyone to paste a key into chat. No key means local.
