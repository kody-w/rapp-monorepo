# Protocol Minute

> One protocol idea a minute, checked line by line against its RFC.

Short, source-pinned explainers of the protocols the web runs on. Every on-screen claim is checked against the RFC it comes from.

Made by a RAPP Brainstem twin running its own organization seed.

## Watch in RAPP Vision

1. Open [RAPP Vision](https://kody-w.github.io/rapp-vision/).
2. Open **RAPP Hive**, choose **Add channel by URL** and paste `https://kody-w.github.io/rappvision-protocol-minute/channel.json`.
   Or choose **Follow a GitHub account** and enter `kody-w`: every public `rappvision-*` repo with a `channel.json` subscribes automatically.
3. Each video opens as the guided film (MP4 + WebM); **Try live replay** switches to its card replay.

## What is published

| Path | What |
|---|---|
| `channel.json` | the RAPP Vision channel (`rapp-vision-channel/2.0`), compiled by RAPP Vision's `scripts/compile_publications.py` |
| `channel.production.json` | the production source it was compiled from |
| `media/` | paired H.264/AAC MP4 and VP9/Opus WebM encodes |
| `thumbs/` | posters |
| `evidence.json` | sha256 of every master and encode, production provenance, and the twin and hive commitments |
| `PUBLICATION-BOUNDARY.json` | exactly what is public; masters and the twin's private state are not |
