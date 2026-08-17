# RNR — RAR Nightly Review

A [RAPP Vision](https://kody-w.github.io/rapp-vision/) channel.

> What landed on the front page of the agentic web, and what broke getting there.

**Channel:** <https://kody-w.github.io/rappvision-rnr/>
**Add to any player:** `https://kody-w.github.io/rappvision-rnr/rappvision/channel.json`

---

## What this is

RNR reviews [RAR](https://kody-w.github.io/RAR/) — the RAPP Agent Registry — the way a
nightly news show reviews a beat. Each episode is a silent, typographic debrief: what
shipped, what turned out to be broken, what is verified live right now, and the one
decision still waiting on a human.

The format is deliberate. Episodes are unnarrated because they are meant to be scannable
muted, and every number on screen is pulled from the live registry at record time rather
than written from memory. When an episode says 279 agents, `registry.json` said 279 while
it was rendering.

The standing rule is that a segment is allowed to report bad news about its own subject.
Episode one is about a health check that had been dead for 82 days while reporting green.
Episode two is about a static API that served a stale catalog while every workflow passed.
A review channel that only carries wins is an ad.

## What's here

| Path | What it is |
|---|---|
| `rappvision/channel.json` | The only file you edit. `rapp-vision-channel/1.0`. |
| `rappvision/media/` | `.mp4` + `.webm` per episode |
| `rappvision/thumbs/` | poster image per episode |
| `build.py` | regenerates everything below from `channel.json` |
| `index.html` | channel landing page |
| `v/<id>.html` | per-episode **share page** |
| `e/<id>.html` | bare embed (iframes, Twitter player cards) |
| `feed.xml` | RSS 2.0 with `<enclosure>` |

`index.html`, `v/`, `e/` and `feed.xml` are **generated**. Don't hand-edit them — the next
build overwrites your change. `python3 build.py --check` fails if any of them is stale, so
the drift is caught rather than discovered later.

## Add an episode

```bash
cp episode.mp4  rappvision/media/my-episode.mp4
cp episode.webm rappvision/media/my-episode.webm     # optional, but ~3x smaller
cp poster.jpg   rappvision/thumbs/my-episode.jpg
# add one entry to the "videos" array in rappvision/channel.json
python3 build.py
```

## Why the share pages exist

RAPP Vision's player routes with a hash (`#/watch/<id>`). Hash fragments are never sent to
a server, so **every** episode link unfurls identically on X, LinkedIn, Slack and Discord —
the generic player, no title, no thumbnail.

So each episode also gets a real URL at `v/<id>.html` carrying per-episode Open Graph tags,
a Twitter player card pointing at `e/<id>.html`, JSON-LD `VideoObject`, chapter deep links
(`v/<id>.html#t=55` starts 55 seconds in) and a working `<video>` — so a shared link is
watchable on its own, with no app shell and no round-trip to a registry.

## Paths are relative on purpose

Every `src` in `channel.json` resolves **against that file's own URL**, per the
`rapp-vision-channel/1.0` spec. Mirror this repo, rename it, serve it from anywhere — the
media still resolves. The generated pages need absolute URLs (Open Graph requires them),
so `build.py` holds a single `SITE` constant. That's the one line to change in a fork.

## Licence

Code in this repo (`build.py`, page templates): MIT.
Episode content: © the author, all rights reserved.
