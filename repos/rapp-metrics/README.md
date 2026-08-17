<!-- (c) 2026 Kody Wildfeuer · part of the RAPP ecosystem (RAPP) -->

# rapp-metrics

**Real usage numbers for surfaces that have no backend.**

`rapp-metrics/1.0` · normative spec: [SPEC.md](SPEC.md) · builds on `rapp-static-api/1.0`

---

## The founding tenet

Read this first. It is [§1 of the spec](SPEC.md), it is the law everything else is derived from, and it is the
part an implementation is most likely to get wrong.

> ### THE ACTOR DETERMINES THE LANE — NEVER THE SUBJECT.
>
> **Who PERFORMED an action decides which counter it feeds. Not who authored the thing being acted upon.**

Two halves. **Both mandatory.**

**Half one — an automated actor MUST NEVER contribute to a human counter.** Agent reviews and agent-generated
*actions* can provide value, but they are completely separate from human engagement, always. Machine output
lives in a distinct **editorial** lane: attributed to a reviewer id and rubric version, visibly
machine-authored, never summed into endorsements, tallies or conversation counts. *Why:* every count must mean
**people, not clicks**. GitHub dedupes reactions per user, and that dedup is the entire source of this
pattern's trustworthiness. **One bot upvote makes every number the protocol publishes a lie.**

**Half two — a HUMAN acting at the bot layer IS fair game and MUST count.** *"a human can interact at the bot
layer... then its fair game... this is where we draw the simple lines of engagement."* If a human upvotes an
agent-**generated** video, **that is 200 real people if 200 people did it** — it counts, fully, as human
engagement. If a human reacts to or replies to a **machine review**, that counts too.

**The opposite error is just as disqualifying.** Quarantining by *subject* instead of by *actor* would make
agent-generated content unmeasurable and gut the value of the content machine. Agent-authored content is a
first-class citizen that earns real human numbers. **Only agent-authored ACTIONS are quarantined.**

And the consequence worth building rather than discarding: human reactions to a machine review are the
community **rating the reviewer**. Sustained negative human signal on an agent's reviews means the rubric is
wrong. The protocol requires that loop to be collected and published — `reviewer_feedback`, keyed by
`reviewer_id`, in the human document, summed into nothing else.

| Actor | Acted on | Lane | Counter |
|---|---|---|---|
| human | top post | **human** | `endorsements` |
| human | tally / poll comment | **human** | `tallies.*` / `signals.*` |
| human | **machine-written review** | **human** | `reviewer_feedback.<reviewer_id>` |
| human | anything on a **machine-authored subject** | **human** | the same counters, full weight |
| **bot / app / CI token** | any reaction | **forbidden** | **none** |
| **bot** | provisioning a comment | machinery | excluded from `conversation` |
| **bot** | writing a review | **editorial** | the editorial document only |

---

## What it is

Every RAPP surface is static and hydra-served — no server, no database, no session, no auth. And every one of
them still needs to answer *"is anyone actually using this?"* with a number somebody can defend in a meeting.

**rapp-metrics says: GitHub is the backend you already have.**

- GitHub **Discussions** give you a permanent public thread per subject — identity, spam control, and a URL
  that CI can both read from and write to.
- GitHub **reactions** are per-user-deduped by the platform. One reaction per person per emoji means every
  count is a count of **people**, not clicks, *by construction*.
- A **scheduled workflow** folds those counters into one byte-stable JSON file and commits it **only when a
  number actually moved**.
- Any static page reads that file with a plain `GET`.

No server. No auth to hold. No PII to lose. And because the snapshot carries no timestamps, **the git history
of the file is the time series.**

---

## The 60-second version

```
subject provider        one function you write:  enumerate() -> [{subject_id, title, url}]
        │
        ▼
GitHub Discussions      one thread per subject, title == subject_id, maintainer-only category
        │               top post       = endorsement       ("I vouch for this")
        │               tally comment  = acquisition       ("I installed / watched this")
        │               poll comment   = experience        (8 reactions = 8 independent counters)
        │               review comment = reviewer_feedback (a machine wrote it; people rate it)
        ▼
collector (cron)        seed → provision → fetch → snapshot → commit iff bytes changed
        │               it NEVER reacts. it is a bot.
        ▼
state/metrics.json      rapp-metrics/1.0 · human lane · sorted keys · no timestamps · CORS-open
state/editorial.json    rapp-metrics-editorial/1.0 · machine reviews, walled off
        │
        ▼
any static page         plain GET. missing file → render nothing. never a zero, never a crash.
```

Writes go **from the browser, with the viewer's own GitHub token, on an explicit click**. There is no server in
this protocol and you must not add one — a proxy would also destroy the actor attribution §1 depends on, since
every write would arrive as the proxy.

---

## Adopting it: you implement one function

Everything else in the protocol is generic. An adopter supplies a **subject provider** and a **profile
declaration**.

```python
def enumerate() -> list[Subject]:
    """Total, deterministic, all-or-nothing. Every subject, or raise."""

Subject = {
  "subject_id": str,        # canonical + permanent + globally unique. this is the join key
  "title":      str,        # display only. may change freely
  "url":        str,        # canonical public URL of the subject
  "digest":     str | None, # sha256, if the subject has bytes
}
```

Five rules that will bite you if you skip them ([§5](SPEC.md)):

1. **Total or raise.** A partial enumeration is a *deletion* of the subjects that did not answer.
2. **Deterministic.** Unstable ordering churns the snapshot and destroys the git-history-as-time-series
   property.
3. **Never reads metrics state.** The provider answers *"what exists"*, never *"what is popular"*.
4. **Never filters or flags by authorship.** A machine-generated subject is enumerated exactly like a
   human-authored one (§1.3).
5. **If the natural id is only locally unique, qualify it.** This is the mistake that is easiest to make and
   hardest to undo — see below.

### Reference provider A — RAR, `subject = agent`

The filesystem is the source of truth; `registry.json` is the built projection every metric joins to.
`subject_id` is the agent's `@publisher/slug` name (279 entries at the time of reading), pattern
`^@[A-Za-z0-9][A-Za-z0-9_-]*/[a-z0-9_]+$`. It is already permanent and machine-enforced:
`state/published_paths.json` is an append-only ledger and `scripts/check_url_stability.py` is the **first** job
in CI, blocking any merge that renames or moves a published agent.

A large share of those agents are machine-written. Nothing in the provider or the counters branches on that —
which is half two satisfied by construction.

### Reference provider B — rapp-vision, `subject = video`

`channels.json` → `channel.json` → `videos[]` (8 channels declared today). And here is the trap, verified in
the shipped player:

> **A video's `id` is unique only inside its own `channel.json`.** The player already treats it as a global
> primary key — `const byId = id => VIDEOS.find(v => v.id === id)` (`index.html:266`) resolves a bare id
> across every channel and **first match silently wins**. `fetchChannel()` rewrites thumbnails, sources and
> live-scene app paths but never namespaces or dedupes `v.id`. And `template/channel.json` ships
> `"id": "my-first-video"` to every new publisher who follows the README.

So the `subject_id` **must** be `<channel.id>/<video.id>` — e.g. `rock-tumbler/rock-tumbler-showcase` — using
the channel id declared **inside** `channel.json`, not the registry entry id (user-added channels get a
throwaway `"custom-" + Date.now()`).

Every entry on that network is a **live replay** — an application performed by a machine. Under §1.3 that
changes nothing: the audience is people, so the counts are people.

---

## The parts most people get wrong

The plumbing is easy. [§9 of the spec](SPEC.md) is 36 invariants; seven of them are §1 restated as tests, and
the other twenty-nine serve one further rule:

> **Never publish a number whose failure mode looks like an honest zero.**

The greatest hits:

| Invariant | Why it exists |
|---|---|
| **People, not clicks** | Let the platform dedup. A count you deduped yourself is a count you have to defend. |
| **No automated actor in a human counter** | The collector creates threads, provisions surfaces, writes editorial, splices report cards. It never reacts. Best form: ship no reaction-writing code in the collector at all. |
| **A human at the bot layer always counts** | Reactions on machine-provisioned surfaces, replies to machine comments, endorsements of machine-authored subjects — all ordinary human signal at full weight. Discarding them is the opposite error, and it is just as disqualifying. |
| **Negatives never subtract** | 👎 becomes a named channel (`did_not_work`, `too_long`, `disagree`), not a penalty. A score that can go down is a brigading target and stops being publishable. Withdrawing your own 👍 *is* the downvote. |
| **One object, one metric** | Top post = endorsement. Tally = acquisition. Poll = experience. Review = reviewer feedback. Conflate them and you get one number that means four things and defends none of them. |
| **Machinery is not conversation** | Subtract the machine-written comments — *computed from what is present*, never a constant — or every subject shows "2 comments" on day zero and your own robots are your engagement number. Human **replies** to those comments still count. |
| **Non-fatal collection** | Missing token, 404, GraphQL error → warn, leave the snapshot alone, exit 0. Some signal is unrecoverable: GitHub's traffic API is a 14-day rolling window. |
| **Never clobber non-empty with empty** | One bad fetch must not erase counts you cannot recompute. |
| **"Never wired" ≠ zero** | Render an em-dash, not `0`. *"No release has been cut yet"* and *"nobody downloaded this"* are different claims, and the second one ends up on a slide. |
| **No timestamps in the snapshot** | Identical counts → identical bytes → no commit on a quiet day → the git log becomes a readable record of when each number actually moved. There is a live counter-example in RAR: `metrics.json` carries `generated_at`, so its no-op guard can never fire and it commits daily regardless. |
| **The metric never blocks the thing measured** | Tracking is a silent no-op when signed out; every client failure is swallowed. A metric must never block a download. |

The worst bug on record in the reference implementation is the reason for one more:

> A join key was written two ways — underscore-normalized as a map key, dashed inside each record. Lookup
> resolved nothing for most of the registry, so **every report card read "not yet scored" while real scores
> existed.** It failed silently and looked exactly like "no data yet" — the worst way for a metric to break.
> Hence: **one named normalizer, in shipped code, called by both sides, never re-derived inside a test.**
> (And: a test that re-implements the logic it checks *cannot fail* and is worse than no test, because the
> docs citing it become false assurance. Verify each new test by reintroducing the bug and confirming it goes
> red.)

---

## The marker comment, and why it exists

GitHub Discussions has a real poll type. It is unusable here, for one concrete reason:

> `createDiscussion` accepts only `repositoryId`, `title`, `body`, `categoryId`. **A poll can only be created
> by hand in the web UI.**

A signal surface that needs a human to click through a web form once per subject is not a pattern — it is a
chore that will not survive the catalog growing. But a **comment** *is* API-creatable, and every comment
carries **all eight reaction contents as independent, per-user-deduped counters**. So one comment behaves as
an eight-option poll, provisioned automatically for every subject the moment it enters the subject set.

Note the tenet at work: the comment is written by a **machine**, the reactions are left by **people**. The
actor on each reaction is human, so every one of those counters is a human counter.

The protocol defaults for a poll surface (a profile may rebind them, but no two channels may share a reaction):

| 👍 | 👎 | 😕 | ❤️ | 🚀 | 👀 | 🎉 | 😄 |
|---|---|---|---|---|---|---|---|
| `worked` | `did_not_work` | `stuck` | `regular_use` | `shipped` | `want_to_try` | `saved_time` | *reserved, unmapped* |

😄 is deliberately left meaning nothing: *"there is no honest question it answers, and an option that means
nothing pollutes every other count."*

---

## The editorial lane — a consequence, not a primitive

The editorial lane is not a category of content. It is what half one **requires you to do with machine-authored
actions**: keep them out of the human counters by putting them somewhere structurally separate. It says nothing
about machine-authored *subjects*, which are counted like everything else.

- Editorial output lives in a **separate document** (`rapp-metrics-editorial/1.0`), never inside the metrics
  document's `subjects` map. So a consumer doing `Object.values(snapshot.subjects).reduce(...)` is
  *structurally incapable* of picking up machine scores. Conflation becomes an explicit act, not an accident.
- Every review is **attributed** to a reviewer id from a published roster and **pinned** to the sha256 of what
  it read, under a **`rubric_version`** that bumps whenever the rubric changes.
- Every render site **labels the review as machine-authored** — and never dims, asterisks or footnotes the
  *subject's* counts for being machine-made.
- **No bot, service account, app installation, or CI token may ever add a reaction to any surface.** The
  collector's token creates threads, provisions surfaces, writes editorial comments, and splices report cards.
  That is all it may do.
- **The humans who react to a machine review are counted** — in `reviewer_feedback`, keyed by `reviewer_id`,
  never merged into the subject's numbers. Five 👎 on a review means five people think the *reviewer* is wrong.

Drop the fourth rule and every number becomes a lie. Drop the fifth and you have thrown away real human
engagement because a machine wrote the thing it was about.

---

## Privacy

Public by design, aggregate by construction. It is a review surface, not telemetry.

- **No usernames in the snapshot** — not one, even though the API hands reactor identities to the collector.
- **No events**, no sessions, no devices, no fingerprints. Only standing counters.
- **Reading the snapshot transmits nothing** about the reader. It is a `GET` of a public file.
- **But the act is not anonymous, and you must say so.** Reacting associates a person's GitHub identity with
  that subject publicly *on GitHub*. The counts are anonymous; the click is not. Claiming otherwise would be
  false. Un-reacting removes them at the next collection, with no residue.
- `reviewer_feedback` names the **reviewer** (a machine), never the people who reacted to it.

---

## Status — read this before citing anything here

**RAR** (`subject = agent`) is running and substantially conformant. Four known gaps, all listed in
[§14](SPEC.md): its snapshot publishes no reaction map, counting rules or `lanes` block; its `metrics.json`
carries a `generated_at` that defeats the no-op commit guard; its `track` subcommand would react with a CI
token if it were ever wired into a workflow (it is not today); and it has no `review` surface, so half two's
feedback loop is unimplemented.

**rapp-vision** (`subject = video`) had a collector — `scripts/rapp_metrics.py`, tests, `docs/METRICS.md`, a
workflow and an empty snapshot — present in the scratch clone **while this spec was being written, authored by
a parallel session**. Treat §14's description of it as a read at a point in time. As read: it is conformant by
construction on half one (the module contains **no `addReaction` mutation at all**), and it has one half-two
gap — it treats its editorial comment purely as machinery and never reads the human reactions on it, which is
exactly the quarantine-by-subject error. Its snapshot is also profile-native (`rapp-vision-metrics/1.0`, a
`videos` map), which §8.6 maps to the canonical field names.

**Nothing in this spec was exercised against a live GitHub API.** Every behavioural claim is grounded in source
or committed state files read in scratch clones; I ran no collector, no workflow, and no test suite. Behaviour
at volume is proven by construction and by hermetic tests, not by load — RAR's live snapshot has 272 subjects
of which **5** carry any nonzero value, with a maximum of 1 endorsement and 1 acquisition, and rapp-vision's
snapshot is empty. The invariants are load-bearing precisely *because* the numbers are still small: they are
what make the numbers worth publishing when they are not.

---

## Files

| File | What |
|---|---|
| [`SPEC.md`](SPEC.md) | The normative spec. **§1 is the founding tenet**, §5 is the provider interface, §7 is the signal surfaces, §8 is the snapshot schema, §9 is the 36 invariants, §10 is the editorial lane, **§13 is the 62-item conformance checklist** (items 1–11 test both halves of §1), §14 is the honest status of both implementations. |
| `README.md` | This page. |

Registers into `kody-w/rapp-spine/registry.json` as `rapp-metrics/1.0`, layer `distribution` — the block is in
[§16](SPEC.md).
