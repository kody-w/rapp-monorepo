# rapp-vision-remix/1.0 — running a post is how the next post gets made

**Status:** design, ratified in conversation 2026-08-02. Not yet implemented.
Companion to `rapp-metrics/1.0`; extends `rapp-vision-channel/1.0`.

## The vocabulary (ratified)

Four words carry the whole system. **Pull it from the shed, shred it, send the shred.**

| word | meaning |
|---|---|
| **the shed** | where every version of every app lives forever. Git already is it: any commit SHA serves any file, permanently. Nobody is force-updated; playing yesterday's build is a URL, not a request. |
| **a shred** | one captured run of a scene — a performance, not a copy. Yours, a friend's, or an AI's; face and audio optional and off by default. |
| **a remix** | a shred *published back* to the network with `remix_of` lineage. Publishing is the opt-in; a sneakernet shred never has to become one. |
| **the drop** | the daily message when a scene's outcome actually changed. Silence means nothing changed, and silence is honest. |

The content layer is **actor-blind**: an AI's shred and a human's shred are the same
artifact shape, shared the same ways. Only the counters are actor-aware, per the
founding tenet of `rapp-metrics/1.0` — the actor determines the lane, never the subject.

---

## The idea

A recording can only be watched. A **live-replay scene can be run**, and running it
produces something that did not exist before: a new session, against the current app,
with a new person at the controls.

`rapp-remix` already names the fidelity ladder — video, scene, transcript — and observes
that replaying a transcript against a live engine *does not reproduce the recording,
and that is the point*. This spec adds the social consequence of that fact:

> **The output of running a post is itself a post.**

A viewer opens an episode, takes the wheel partway through, and what happens on screen is
genuinely new — the app has been updated by its own autonomous loop since the seed was
cut, and the human made different choices. Capture that, optionally with their camera and
voice over it, and it is a first-class artifact: a *remix*, attached by lineage to the post
it came from.

A remix carries a scene of its own. So a remix can be remixed. That is the loop, and it
has no natural end.

## Why this cannot be done on someone else's platform

Two properties make it possible, and RAPP Vision has both by accident of its architecture:

1. **The app is same-origin with the player.** GitHub Pages serves every one of a user's
   repos from one origin, so the player can dispatch real events into the app in an
   iframe. This is what makes live replay work at all.
2. **Capture is client-side.** `getUserMedia` + `MediaRecorder` are browser primitives.
   No upload pipeline, no transcode farm, no account.

A conventional video platform has neither: the "video" is an opaque decoded stream, and
there is nothing to seize control of.

---

## Ratified decisions

These were decided explicitly and are not defaults to be revisited casually.

### 1. The webcam is OFF by default

Camera and microphone are opt-in per recording, never remembered as an always-on
preference. The capture UI states in plain language, *before* the record button — not in a
footer — that a published video is mirrored across many heads and content-addressed, and
therefore effectively permanent. "You cannot unring this."

**Why:** the network is deliberately hydra-served and hard to kill. That is a feature for
a demo reel and a hazard for a stranger's face. The asymmetry of harm is the whole
argument: a missing webcam costs a slightly less personable video, a permanent one costs
someone their face on an unkillable mirror.

### 2. Remix happens on the CANONICAL player

Recording runs at `kody-w.github.io/rapp-vision`, where the player is same-origin with the
apps it drives. A self-hosted fork of the player on another user's Pages **cannot** drive
those apps — the origin differs and event dispatch into the iframe is blocked.

The rule: **remix on the canonical player; publish the artifact anywhere.**

This must be documented prominently, because the failure mode is silent — a forked player
looks fine until a scene simply does nothing.

### 3. Export is the default; publishing is opt-in

**The artifact is theirs before it is anyone else's.** When a capture finishes, the primary
action is `navigator.share()` with the video file — the native share sheet, so it goes to
iMessage, AirDrop, Photos, or wherever they like, and never touches a repo. Where the Web
Share API is unavailable or refuses files, fall back to a plain download.

Publishing to a channel is a secondary, deliberate action.

**Why:** this is the local-first position applied to social content — sneakernet first,
network second. It also resolves the permanence hazard structurally rather than by warning:
on the default path a face never enters a mirrored repo at all, because the default path
has no repo in it.

---

## Lineage

One field on the video entry, in `rapp-vision-channel/1.0`:

```json
{
  "id": "my-run-of-the-driving-sim",
  "remix_of": "arcade/arcade-take-over",
  "remix_kind": "live-run"
}
```

- `remix_of` — `"<channel-id>/<video-id>"`, the network-unique subject id already defined
  by `rapp-metrics/1.0`. (Video ids are unique only within a channel, so the qualifier is
  mandatory.)
- `remix_kind` — `live-run` (ran the scene), `commentary` (watched and reacted),
  `derivative` (used it as a starting point and diverged).

Rendering: the parent shows *"N remixes"* with a gallery; the child shows *"remix of →"*
linking home. The edge set across the network is the content graph.

**No permission handshake.** A remixer publishes to their own repo and adds their channel
to the network the same way every channel joins — by PR to `channels.json`, or locally
without asking anyone. The parent post never has to accept anything, and the network
registry remains the allowlist. This keeps hosting cost, moderation load, and the
publishing bottleneck at zero.

## What it means for metrics

Per the founding tenet of `rapp-metrics/1.0` — **the actor determines the lane, never the
subject** — a remix is a *human* action and therefore counts, fully, including when the
seed post was agent-generated.

A remix is the strongest engagement signal the protocol can observe: it costs real effort,
so it cannot be farmed the way a click can. Two consequences:

- `remixes` is a first-class counter alongside endorsements and conversation.
- A remix credits **both** the child and its parent. Reach is transitive; a seed that
  produced a hundred divergent sessions did more than one that produced a hundred views.

**"Most remixed" is the impact ranking** — the signal for deciding which autonomous loop's
output deserves attention, which is the steering problem this whole surface exists to solve.

---

## Open questions (not yet decided)

- **Audio bed.** Does the capture include the app's own audio alongside the mic, and how is
  ducking handled? Needs a real test with a noisy app (the 808, the DAW).
- **Length cap.** An unbounded `MediaRecorder` in a tab will happily eat all available
  memory. A cap plus a visible timer is probably right; the number needs measuring, not
  guessing.
- **Scene extraction from a live run.** A remix should carry a replayable scene of its own,
  which means recording the human's interactions as they drive — mechanically similar to
  the existing capture harness, but it must record *what the human did*, not a scripted
  cue list. This is the piece that makes the loop recurse, and it is the least proven.
- **Moderation posture at the network edge.** Anyone may publish anywhere; only listing in
  `channels.json` is gated. That is almost certainly correct, but it should be a stated
  policy rather than an emergent one.
