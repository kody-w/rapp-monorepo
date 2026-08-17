# rapp-vision-daily/1.0 — one script, a different outcome every day

**Status:** design, 2026-08-02. Not yet implemented.
Completes the triple with `rapp-metrics/1.0` (measure) and `rapp-vision-remix/1.0` (branch).
Vocabulary (shed / shred / remix / drop) is defined in REMIX.md and used here unchanged:
the daily ritual is the **morning shred**, its delivery is the **drop**, and an AI's
scheduled run is a shred like any other — a **pace car** to race, editorial in the
counters, first-class as content.

---

## The mechanism

A live-replay scene is a **fixed script**. The software it drives is **not fixed** — the
autonomous loops rewrite it continuously. So re-running the same scene tomorrow produces a
materially different session than today's, with nobody authoring anything.

> **The script is constant; the software is the variable. The diff is the content.**

This is why the daily loop costs nothing to feed. Conventional daily content needs a
creator every day. Here the creator is the estate improving itself, and the scene is just
the lens pointed at it.

## Why a permanent archive beats an ephemeral one

Snapchat's daily rhythm is built on disappearance. Copying that here would be a mistake:
the network is hydra-served and content-addressed, so permanence is the property the
architecture actually has.

Take the rhythm, drop the disappearance:

- **The drop is ephemeral in *attention*** — one message a day, the thing you look at now.
- **The archive is permanent by design** — every run is kept.

That inversion is strictly better than the thing it imitates. A year of daily runs of one
scene is a **time-lapse of software evolving under its own loops** — an artifact that has
essentially never existed before, and that only gets more valuable with age. The "streak"
stops being a retention gimmick and becomes a longitudinal record.

---

## The discipline that makes it not-spam

**Fire on difference, not on schedule.** A daily job that sends every day regardless
trains the recipient to ignore it inside a week, and a drop that says nothing happened is
worse than silence.

The estate already holds this line elsewhere and it should be inherited verbatim:

- `rapp-metrics/1.0` writes no timestamps into its snapshot, so a quiet day produces no
  commit at all.
- `notify_new_videos.py` diffs against a seen-list and is idempotent — a video is announced
  exactly once, ever.

So the daily run always *executes*; it only *publishes and notifies* when the outcome
actually differs from the previous run. Silence is a valid, meaningful result: it means
the loops did nothing worth showing.

### What counts as "different"

Cheapest reliable signals first, since this must run unattended:

1. **The app's content hash changed** since the last run — a real code change happened.
2. **The run's outcome changed** — different assertion results, different final state,
   different HUD/console readings, a step that used to pass now failing.
3. **Perceptual delta on sampled frames** exceeds a threshold — catches visual change that
   the assertions miss.

(1) is nearly free and gates the rest. Signal (2) is the interesting one: a scene that
*stops working* is the highest-value drop the system can produce — the autonomous loop
broke something, and this is how you find out the morning after rather than in front of a
customer.

## The shed — every version stays playable, forever

> *"They can play the latest version if there was an update, but they can also play the
> same version they have always played."* — ratified 2026-08-02

If the app is mutable and yesterday's build is gone, "today vs. yesterday" is
unfalsifiable — you cannot re-run yesterday to check. So version choice must belong to the
**player**, not the publisher. Nobody gets force-updated.

RAR already holds this line for agents: every registry entry carries `_sha256`,
`_first_commit_sha`, and `_latest_commit_sha`. **Git is the shed.** A commit SHA is an
immutable address that never expires, and GitHub serves any file at any commit forever.

### Measured, not assumed (2026-08-02)

Two commits have touched `apex-driving-simulator.html`, and both remain live:

| commit | bytes | sha256 (12) | state |
|---|---|---|---|
| `e9d37614` | 97,464 | `300c11ba1128` | before the track-spline / collision fix |
| `4daf0bc9` | 113,910 | `f0507c41a5a2` | after the fix |

`https://kody-w.github.io/localFirstTools/apex-driving-simulator.html` returns
`f0507c41a5a2` — byte-identical to the newest commit. So the mutable "latest" pointer and
the immutable pinned versions already coexist with zero new infrastructure.

`raw.githubusercontent.com` responds with **`access-control-allow-origin: *`** (verified by
request), so the player may fetch any pinned version's source cross-origin.

### The same-origin wrinkle, and why the architecture already solves it

Live replay requires the app to be **same-origin** with the player, or events cannot be
dispatched into the iframe. A pinned version lives on `raw.githubusercontent.com`, a
*different* origin — so pointing an iframe straight at it would break replay.

The fix rides an existing property of this estate: every localFirstTools app is a
**single self-contained HTML file**. So the player can fetch the pinned source as text and
boot it from a `Blob` URL, which inherits the creating document's origin and is therefore
same-origin with the player. No relative asset paths exist to break under a blob URL,
precisely because the apps carry their CSS and JS inline.

**Unverified:** the blob-iframe path has NOT yet been tested end-to-end for event dispatch.
CORS, immutability, and version-distinctness are measured; *driving* a blob-booted historical
build is the remaining unknown and must be probed before this is promised to anyone.

### What version-pinning unlocks: isolating the variables

A daily run records the app version it ran against (`app_sha`). With every version still
playable, the two variables can be **separated** — which no conventional platform can do:

- Same script, same human, **two app versions** -> pure software delta. *Did the loop
  improve the game?*
- Same script, **same app version**, two days apart -> pure human delta. *Did I get better?*
- Same app version, two people -> pure skill comparison, on a frozen board.

"Am I improving, or is the game changing under me?" becomes an answerable question instead
of a vibe. That is the honest core of a daily score, and it is only possible because
nothing is ever thrown away.

## Delivery

Reuse the proven path, one message, direct watch link:

- The existing notifier already walks the registry, diffs, and sends exactly once.
- **Send a link, never an attachment.** File sends fail on this machine (`error=25`);
  attachment-based delivery would silently never arrive. Text + link is the verified path.
- One drop per day maximum, batching everything new into a single message.

## Where it meets the other two layers

- **Remix** (`rapp-vision-remix/1.0`) — the daily drop is a natural remix seed: *"here is
  what changed overnight, go run it yourself."* The recipient's own run diverges again,
  and per sneakernet-default they can keep it entirely on-device.
- **Metrics** (`rapp-metrics/1.0`) — the actor rule applies unchanged: the daily runner is
  automated, so its output is **editorial**, never a human counter. Humans reacting to a
  drop, or remixing it, count fully.
- **Steering** — this is the answer to *"which of my autonomous loops deserves attention
  today."* Ranked by human response to the drops, not by commit volume.

---

## Open questions

- **Cadence per scene.** Daily for everything is probably wrong; a scene over a fast-moving
  app earns a daily slot, a stable one does not. Cadence should likely be derived from
  observed change rate rather than configured.
- **Threshold calibration.** The perceptual-delta cutoff needs measuring against real runs,
  not guessing — too tight and every frame of noise is a story, too loose and real changes
  are swallowed.
- **Failure framing.** When a scene breaks, is the drop framed as an alert or as content?
  Probably both, but the wording matters if anyone outside the estate is subscribed.
- **Cost.** Every daily run is a headless browser session per scene. With ~11 live entries
  today that is trivial; the ceiling should be established before it is not.
