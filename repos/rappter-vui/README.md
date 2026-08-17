# rappter-vui — the fauna player + openrappter Voice UI

A single self-contained page that renders a **rappter** (a live creature from
[rapp·go](https://kody-w.github.io/rapp-static-apis/rapp-go/)'s canonical
`lib/fauna.js`, so it's the same species system everywhere) and lets you talk to
your on-device **openrappter** agent by voice and hand gesture.

**Live:** https://kody-w.github.io/rappter-vui/

## What it does
- **HOLO creature** — a green legged `strider` rappter, rendered live via rapp·go fauna. Reacts while it listens/speaks.
- **🥚 .egg export** — export the creature as a rapp·go `.egg` (byte-verified against rapp·go's `receiveEgg`: `id === genomeId(genome)`), with one-click *open in rapp·go*.
- **Voice** — speech-to-text + text-to-speech via the Web Speech API (universal); on-device HD upgrade slot (Whisper + Kokoro on WebGPU).
- **Gestures** — MediaPipe Tasks hand-gesture control (👍 send · ✋ stop · ✊ listen · ✌️ clear).
- **Brain** — drives openrappter over its gateway (`ws://127.0.0.1:18790`) using the RAPP **sense** protocol (`|||VOICE|||`, `|||HOLO|||`).

## Running it
The creature, egg export, gestures and voice all run **fully client-side** — the
Pages demo above works standalone. To have it **drive your openrappter agent**,
run it from `http://localhost` (a browser blocks an `https://` page from opening
the local `ws://` gateway — mixed content):

```bash
# with openrappter running locally:
python3 -m http.server 8790     # then open http://localhost:8790
# — or — openrappter serves it itself at http://127.0.0.1:18790/vui
```

Welded from three donors, kept intact: rapp·go fauna · MediaPipe Tasks · the RAPP Sense spec.
