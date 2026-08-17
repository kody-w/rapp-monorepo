<!-- (c) 2026 Kody Wildfeuer · part of the RAPP ecosystem (RAPP) -->

# rapp-metrics/1.0 — real usage numbers for surfaces that have no backend

> **Spec id:** `rapp-metrics/1.0` · **status:** normative, protocol · **layer:** distribution
> **proposed home:** `kody-w/rapp-metrics/SPEC.md` · **registers into:** `kody-w/rapp-spine/registry.json`
> **builds on:** `rapp-static-api/1.0` (the repo IS the API — the snapshot this spec defines is one of its documents)
> **reference implementations:** RAR (`subject = agent`) · rapp-vision (`subject = video`) — status in §14
>
> Every RAPP surface is static and hydra-served: no server, no database, no session, no auth. It still needs
> defensible utilization numbers. **rapp-metrics says: GitHub is the backend you already have.** Discussions
> supply permanent per-subject identity, spam control, and per-user-deduped reaction counters for free. A
> scheduled workflow folds them into one byte-stable JSON file. Any static page reads that file with a plain
> `GET`. Nothing else exists — no server to run, no auth to hold, no PII to lose.

---

## 1. The founding tenet

Everything else in this document is derived from one rule. It is stated first because it is the law the rest
of the protocol implements, not a caveat attached to it. An implementation that gets every other section right
and this one wrong publishes numbers that are lies, and is **non-conformant**.

> ### THE ACTOR DETERMINES THE LANE — NEVER THE SUBJECT.
>
> **Who PERFORMED an action decides which counter it feeds. Not who authored the thing being acted upon.**

The rule has two halves. **Both are mandatory.** An implementation that honours one and drops the other has
not implemented the tenet — it has implemented half of it, and each half fails in its own direction.

### 1.1 Half one — an automated actor MUST NEVER contribute to a human counter

Agent reviews and agent-generated *actions* can provide value, but they are **completely separate from human
engagement, always**. Machine output lives in a distinct **editorial** lane: attributed to a reviewer id and a
rubric version, visibly machine-authored, and **never summed into endorsements, tallies, or conversation
counts**.

**Why:** every count this protocol publishes must mean **people, not clicks**. GitHub dedupes reactions per
user, and that dedup is the entire source of the pattern's trustworthiness — it is why a number here is
defensible without an analytics vendor, a session store, or a bot-detection budget. **One bot upvote makes
every number the protocol publishes a lie**, and it does so retroactively and unrecoverably, because you
cannot subtract it later without knowing which reactions were machine-made.

**What the protocol can actually enforce — stated here rather than discovered later.** The rule above is the
standard. It is *not* a claim that violations are detectable, and an earlier draft of this spec asserted it as
though it were. The threads are public and the write path is deliberately any-credential (C-W1), so nothing
stops a third-party bot account or App installation that never read this document from reacting on a top post
or a surface comment. Two things follow, and both are normative:

- **The collector MUST classify reactors and count only declared humans (M38).** That catches a bot account, a
  GitHub App installation, and a CI token — every automated actor that identifies itself as one at the API.
  Without M38, L2 and M32 are MUSTs that bind only the people who already agreed to be bound by them, and the
  protocol has no way to check its own headline claim.
- **The residual is real and is named.** A human-operated PAT driven by a script, a machine posting through a
  human account, and a stolen credential (C-W5) are all byte-identical to a person clicking, at the API, with
  no signal to separate them. So the guarantee this protocol delivers is **"no *declared* machine actor is in a
  human counter"** — not "no machine actor is".

An implementation whose `counting_rules` claim more than M38 can check is making a false statement (M29). The
honest wording is *"no bot account, app installation, or CI token is counted: every reactor is classified and
non-human reactors are dropped"* — never *"no machine has ever voted here"*.

### 1.2 Half two — a HUMAN acting at the bot layer IS fair game and MUST count

> *"a human can interact at the bot layer... then its fair game... this is where we draw the simple lines of
> engagement."*

- If a human upvotes an **agent-generated** video, **that is 200 real people if 200 people did it.** It counts,
  fully, as human engagement. The subject being machine-authored changes nothing.
- If a human **reacts to or replies to a machine review**, that **also counts as human engagement** — and it is
  one of the most valuable signals in the system (§1.5).
- If a human uses a machine-provisioned surface — a tally comment, a poll comment, a bot-written review — the
  surface's authorship is irrelevant. A person acted. It counts.

**Agent-authored content is a first-class citizen of this protocol that earns real human numbers.** Nothing in
this spec discounts, footnotes, suppresses, or separately-bins a counter because a machine made the thing being
counted.

### 1.3 The opposite error: quarantining by SUBJECT

The most likely way to get this wrong is to over-apply half one — to see "machine" anywhere near a number and
quarantine it. **Quarantining by subject instead of by actor is the opposite error, and it is just as
disqualifying.** It would make agent-generated content unmeasurable and gut the value of the content machine:
the very artifacts a RAPP surface produces at scale would be the only ones that could never demonstrate
traction.

**Only agent-authored ACTIONS are quarantined. Agent-authored SUBJECTS are counted like anything else.**

### 1.4 Lane assignment — the whole law in one table

Read every row as: *who acted → which lane → which counter.* The middle column never depends on who authored
the object in column two.

| Actor | Object acted on | Lane | Counter it feeds |
|---|---|---|---|
| human | thread top post (reaction) | **human** | `endorsements` |
| human | tally surface comment (reaction) | **human** | `tallies.<surface_id>` |
| human | poll surface comment (reaction) | **human** | `signals.<surface_id>.<channel>` |
| human | reply in the thread | **human** | `conversation` |
| human | **machine-written review comment** (reaction) | **human** | `reviewer_feedback.<reviewer_id>` |
| human | **reply to a machine review** | **human** | `conversation` |
| human | any surface of a **machine-authored subject** | **human** | the same counters, at full weight |
| **bot / app / CI token** | any reaction, anywhere | **forbidden** | **none — this write MUST NOT happen** |
| **bot** | provisioning a surface comment | machinery | none; excluded from `conversation` (M10) |
| **bot** | writing a review | **editorial** | the editorial document only, never a human counter |

Two rows carry the whole tenet: the **bot / any reaction** row (half one) and the **human / machine-written
review comment** row (half two). An implementation that permits the first, or discards the second, is
non-conformant. §13 makes both testable.

### 1.5 The consequence worth building: the community rates the reviewer

Human reactions to a machine review are the community **rating the reviewer**. This falls straight out of the
tenet — a person acted, so it is human signal — and it is the most useful thing half two buys you:

> **Sustained negative human signal on an agent's reviews means the rubric is wrong.**

That is a feedback loop worth exposing, so this protocol **requires it to be collected and published** wherever
an editorial surface exists (M35), in its own field, keyed by `reviewer_id`, in the **human** document —
because it is a human counter. It is never summed into the reviewed subject's own numbers: people disliking a
review is not people disliking the thing reviewed.

### 1.6 Derived laws

These are normative. Every later section is an application of them.

- **L1.** Lane assignment **MUST** be a function of the **actor** only. No code path that computes a human
  counter **MAY** read the authorship, provenance, or generator of the *subject*.
- **L2.** An automated actor — bot account, service account, GitHub App installation, CI token, scheduled
  workflow, agent — **MUST NOT** perform any action that lands in a human counter. Concretely: it **MUST NOT**
  add a reaction to any thread, tally surface, poll surface, or review surface.
- **L3.** A human action **MUST** be counted in full regardless of what it was performed on, including
  machine-authored subjects and machine-authored comments.
- **L4.** Machine output **MUST** be published in the editorial lane: separate document, attributed to a
  `reviewer_id` and a `rubric_version`, visibly machine-authored at every render site (§10).
- **L5.** Machine-authored comments on a thread **MUST** carry a marker and **MUST** be excluded from
  `conversation`. Human replies **to** those comments are ordinary human replies and **MUST** be included.
- **L6.** Where an editorial surface exists, human reactions to it **MUST** be collected as
  `reviewer_feedback` and **MUST NOT** be summed into `endorsements`, `tallies`, `signals`, `conversation`,
  or `rank`.
- **L7.** No counter, badge, or ranking **MAY** be suppressed, discounted, footnoted, or moved to a separate
  bin because the subject was machine-generated (§1.3).
- **L8.** Where per-user dedup cannot be delegated to the platform, the implementation **MUST** hand-roll it
  (M6). A lane that cannot dedupe by person cannot be a human lane.

**One-line test for any new counter you invent:** *name the actor.* If the actor is a person, it belongs in the
human document and counts. If the actor is a machine, it belongs in the editorial document and counts toward
nothing else. If you cannot name the actor, do not publish the number.

---

## 2. Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**,
**RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described in RFC 2119.

"Conforming implementation" means the whole system: the provider, the collector, the snapshot, and every page
that renders it. A conformant collector paired with a page that prints `0` for an unknown value is **not** a
conforming implementation (M20). A conformant collector paired with a workflow that reacts with the CI token is
**not** a conforming implementation (L2).

---

## 3. Vocabulary

These terms are used with exactly these meanings throughout. Where an adopter's own vocabulary differs
(RAR says "agent", rapp-vision says "video"), the mapping **MUST** be declared in the profile (§5.5).

| Term | Definition |
|---|---|
| **subject** | The thing being measured. Exactly one real, addressable artifact — an agent, a video, a tool, an egg, a channel, a repo. Never a category, never an aggregate. May be human-authored or machine-authored; the protocol does not care (§1.3). |
| **subject_id** | The subject's canonical, permanent, globally-unique-within-the-surface identifier. The join key for every number this protocol produces, and also a GitHub Discussion title. §5.2. |
| **subject provider** | The one component an adopter implements: a total, deterministic enumeration of the subject set. §5. |
| **actor** | Whoever performed an action: a **human** acting with their own credential, or an **automated actor** (bot, service account, app installation, CI token, agent). The actor — and only the actor — determines the lane. §1. |
| **lane** | Which family of counters an action may feed. Exactly two: **human** (the `rapp-metrics/1.0` document) and **editorial** (the `rapp-metrics-editorial/1.0` document). §1.4. |
| **thread** | The GitHub Discussion bound to one subject. Its title **is** the `subject_id`. It supplies identity, a permanent public URL, spam control, and the objects that carry counters. §6. |
| **endorsement** | **Exactly one named reaction content**, left by a person, on the thread's **top post**. "I vouch for this." Protocol default `THUMBS_UP`; a profile **MAY** rebind it to a different single content and **MUST** publish which one (§7.2). One object, **one reaction content**, one meaning. An `endorsements` figure is **never** a sum across two or more reaction contents — that is a click-count, not a people-count (M39). |
| **signal surface** | A machine-provisioned comment whose reactions are counters. Three kinds: **tally** (one reaction content = one counter), **poll** (up to eight independent counters), **review** (an editorial comment whose reactions are `reviewer_feedback`). §7. |
| **tally** | A signal surface of kind `tally`. Counts one specific act — acquisition, install, watched-it. Exactly one reaction content is meaningful; the rest are ignored. |
| **conversation** | Human replies in the thread, **minus** the machine-authored comments actually present. §9 M10, L5. |
| **snapshot** | The byte-stable JSON document this spec defines (§8). The only thing a reading page ever sees. |
| **editorial** | Machine-**authored** assessment — an LLM critic, a rubric scorer, an agent reviewer. A first-class output, published in a **separate document**, never summed into a human counter. §10. *(Note: "editorial" describes the author of the assessment, never the subject of it.)* |
| **reviewer_feedback** | **Human** reactions to a machine review. A human counter, published in the human document, keyed by `reviewer_id`. The community rating the reviewer. §1.5. |
| **profile** | A named, versioned binding of this protocol to one subject kind: the id grammar, the surface registry, the reaction map, the rank formula. §5.5. |
| **collector** | The scheduled job that reads GitHub and writes the snapshot. It is an automated actor and is bound by L2. |
| **marker** | An HTML comment embedded in a machine-written comment body, used to find that comment again idempotently — and to exclude it from `conversation`. |

---

## 4. The substrate, and why this is a spec rather than a script

Three properties make metrics on a static surface hard, and all three are solved by the same substrate.

| Problem | What a normal product does | What rapp-metrics does |
|---|---|---|
| **Identity** — "which thing is this a number about?" | rows in a database | one GitHub Discussion per subject, title == `subject_id` |
| **Anti-inflation** — "is this 40 people or one person clicking 40 times?" | accounts, sessions, rate limits, bot detection | GitHub enforces one reaction per user per subject per emoji; every count is a *people* count by construction |
| **Delivery** — "how does a static page read a live number?" | an API endpoint you must own | a committed JSON file on `raw.githubusercontent.com` / Pages |

The write path is the **viewer's own** GitHub token hitting GitHub's GraphQL API directly. The read path is a
static page fetching a committed file. In between is a cron job that reads GitHub, folds it into a snapshot,
and commits **only when a number actually moved**. That is the whole protocol.

The hard part is not the plumbing — it is the honesty. §1 is the constitution; §9 is forty invariants, of
which eleven (M30–M40) restate §1 as tests and the other twenty-nine serve one further rule: **never publish
a number whose failure mode looks like an honest zero.** A metric
that breaks silently and reads as "no data yet" is worse than no metric, because nobody re-checks a figure that
looked plausible.

### 4.1 Architecture

```
                 ┌───────────────────────── the adopter writes ONLY this ────────┐
                 │  subject provider:  enumerate() -> [ {subject_id, ...} ]      │
                 └───────────────────────────────┬──────────────────────────────┘
                                                 │
   ┌─────────────────────────────────────────────▼──────────────────────────────────┐
   │  COLLECTOR  (scheduled workflow, capped, non-fatal, never clobbers)             │
   │    seed      : create a thread per subject that lacks one (title == subject_id) │
   │    provision : back-fill every surface in the surface registry, idempotently    │
   │    fetch     : read reaction counts -> build snapshot -> persist iff non-empty  │
   │    editorial : (optional) write machine reviews into the editorial lane         │
   │    report    : (last, continue-on-error) splice a report card into the thread   │
   │                                                                                 │
   │    NEVER: addReaction. The collector is an automated actor (L2).                │
   └─────────────────────────────────────────────┬──────────────────────────────────┘
                                                 │ commit ONLY when bytes changed
   ┌─────────────────────────────────────────────▼──────────────────────────────────┐
   │  HUMAN LANE      state/metrics.json    (schema rapp-metrics/1.0, byte-stable)   │
   │                  endorsements · tallies · signals · conversation ·             │
   │                  reviewer_feedback                                              │
   │  EDITORIAL LANE  state/editorial.json  (schema rapp-metrics-editorial/1.0)      │
   │                  machine-authored assessments only — never summed into above    │
   └─────────────────────────────────────────────┬──────────────────────────────────┘
                                                 │ plain GET, CORS-open, CDN-cached
   ┌─────────────────────────────────────────────▼──────────────────────────────────┐
   │  READERS    any static page. Missing file -> render nothing, never zero.        │
   │  WRITERS    the browser, with the VIEWER'S OWN token, on explicit user action.  │
   └────────────────────────────────────────────────────────────────────────────────┘
```

Three stages, and their independence is the point:

1. **Collect** is the expensive, unrecoverable stage. Reaction history cannot be reconstructed if a run is
   lost. Everything in it is non-fatal (M18) and never destructive (M19).
2. **Publish** is a file write. It is cheap, and it is guarded so that a bad collect cannot damage a good file.
3. **Read** is a `GET` of a public document. It has no dependency on the other two being healthy today.

**Step order and failure policy follow the cost of losing the artifact, not the narrative order of the
pipeline.** Reporting runs *last* and *non-blocking* because writing a card is the least valuable thing the
workflow does and losing a day of reactions is the most expensive. (Verified in RAR:
`.github/workflows/refresh-ratings.yml` — the "Publish per-agent report cards" step carries
`continue-on-error: true` and an inline comment recording that it previously sat *between* the collectors and
the commit, where an unhandled error threw away the whole day's collected signal.)

---

## 5. The subject provider — the only thing an adopter implements

Everything else in this protocol is generic. An adopter supplies **one function and one declaration**.

### 5.1 The interface

```
enumerate() -> list[Subject]

Subject := {
  "subject_id": str,          # REQUIRED. canonical, permanent, matches the profile's pattern
  "title":      str,          # REQUIRED. human display name. MAY change freely; never a join key
  "url":        str,          # REQUIRED. canonical public URL of the subject itself
  "digest":     str | null,   # OPTIONAL. content address (sha256) if the subject has bytes
  "seed":       object        # OPTIONAL. opaque extras used only to render a new thread's body
}
```

Normative requirements on `enumerate()`:

- **P1.** It **MUST** be **total**: every subject that exists in the surface is returned, or the call fails.
  A partial enumeration is forbidden — a snapshot rebuilt from the sources that happened to answer is a
  *deletion* of the ones that did not.
- **P2.** It **MUST** be **deterministic**: the same repository state produces the same list, in the same
  order, with the same ids. Ordering instability produces snapshot churn, which destroys M23.
- **P3.** It **MUST** be **all-or-nothing**. If any enumeration source fails (a missing file, a failed fetch,
  malformed JSON at the *root* level), it **MUST** raise rather than return a short list, and the collector
  **MUST** leave the snapshot unchanged. Per-*record* tolerance is different and is permitted: one malformed
  subject entry **SHOULD** be dropped with a warning rather than failing the whole enumeration.
- **P4.** It **MUST NOT** read any metrics state. The provider answers "what exists", never "what is popular".
  A provider that filtered by signal would make the metric define its own population.
- **P5.** It **MUST NOT** filter, flag, or partition subjects by authorship. A machine-generated subject is
  enumerated exactly like a human-authored one (L1, L7). A provider **MAY** carry authorship in `seed` for
  *display*, but no counter may branch on it.
- **P6.** It **SHOULD** derive the subject set from files in the repository (the filesystem or a committed
  index), so the enumeration is auditable in git and reviewable in a PR.

### 5.2 `subject_id` — the grammar rules that actually bite

`subject_id` is the join key for every number, the Discussion title, and the anti-spoof shape check. It is the
single highest-stakes design decision an adopter makes.

- **I1.** It **MUST** be unique across the entire adopting surface — not merely within whatever file it was
  read from. **If the natural local id is only locally unique, the `subject_id` MUST be namespace-qualified.**
  (§5.4 is a worked example of exactly this hazard.)
- **I2.** It **MUST** be permanent. Renaming a subject orphans every count ever collected for it, and there is
  no way to notify the people whose links and installs point at the old id.
- **I3.** Permanence **MUST** be machine-enforced, not merely intended. A conforming surface keeps an
  **append-only ledger** of published `subject_id`s and runs a CI check that **blocks the merge** on any
  rename, move, or deletion. (RAR does this: `state/published_paths.json` plus
  `scripts/check_url_stability.py`, which is the *first* job in `test.yml`.)
- **I4.** It **MUST** match an anchored regular expression published by the profile, and that expression
  **MUST** be tight enough that an arbitrary human-written Discussion title does not accidentally satisfy it.
- **I5.** It **SHOULD** be ≤ 120 characters and URL-safe, so it works as a Discussion title, a search term,
  and a URL fragment without escaping surprises. *(This spec does not assert GitHub's exact title length
  limit; the recommendation is a safety margin, not a measured bound.)*
- **I6.** If any writer in the system can produce a variant spelling of the id (dashes vs underscores, case),
  the profile **MUST** name **one** normalizer function, that function **MUST** live in shipped code that both
  the writer and the reader call, and it **MUST NOT** be re-implemented inside a test. See M21 — this exact
  class of bug is the worst failure this protocol has on record.

### 5.3 Reference provider A — RAR (`subject = agent`)

RAR's subject set is the agent registry. The filesystem is the source of truth and `registry.json` is the
built projection every metric joins to.

```python
# provider: rar-agents/1.0
REGISTRY = ROOT / "registry.json"

def enumerate():
    doc = json.loads(REGISTRY.read_text(encoding="utf-8"))   # raises -> P3 all-or-nothing
    return [
        {
            "subject_id": a["name"],                          # "@publisher/slug"
            "title":      a.get("display_name", a["name"]),
            "url":        f"https://github.com/{REPO}/blob/main/{a['_file']}",
            "digest":     a.get("_sha256"),
            "seed":       {"description": a.get("description", ""),
                           "version": a.get("version", "")},
        }
        for a in doc.get("agents", []) if a.get("name")
    ]

SUBJECT_ID_PATTERN = r"^@[A-Za-z0-9][A-Za-z0-9_-]*/[a-z0-9_]+$"
```

Grounding (read from the files in a scratch clone):

- `registry.json` carries **279** agent entries; each entry's `name` is `@publisher/slug`, and the build stamps
  `_file`, `_install_filename`, `_sha256`, `_size_kb`, `_lines`, and git-derived `_added_at` fields.
- `build_registry.py` enumerates from the filesystem (`agents/**` glob for `*.py`, `*.py.card` with card
  winning, plus a `*.py.stub` pass), extracts each manifest **via AST, never by importing the file**, requires
  `schema, name, version, display_name, description, author, tags, category`, and treats a dash in a filename
  as a build **error**.
- `scripts/discussion_ratings.py:74` is the shape check, verbatim:
  `AGENT_TITLE_RE = re.compile(r"^@[A-Za-z0-9][A-Za-z0-9_-]*/[a-z0-9_]+$")`, with the comment
  *"Belt: shape check. Suspenders: the title must also exist in registry.json."*

Note for §1: a large fraction of RAR's agents are themselves machine-generated. Nothing in this provider or in
RAR's counters treats them differently, which is L7 satisfied by construction.

### 5.4 Reference provider B — rapp-vision (`subject = video`)

rapp-vision's subject set is a two-level walk: a network registry (`channels.json`) → one `channel.json` per
channel → the `videos[]` inside it. The live network declares **8** channels
(`rock-tumbler`, `localfirsttools`, `learnwithkody`, `catchup`, `field-notes`, `rooms`, `arcade`, `workbench`).

**The load-bearing finding, and the reason this provider is in the spec:** a video's `id` is unique only
*inside its own `channel.json`*. It is not globally unique, and the shipped player already treats it as if it
were. Verified in the shipped `index.html`:

- `index.html:266` — `const byId = id => VIDEOS.find(v => v.id === id);` — a bare id is resolved across every
  subscribed channel's flattened video list; **first match silently wins**.
- `fetchChannel()` (`index.html:994-1017`) rewrites `v.thumb`, `v.sources[].src` and `v.live.scenes[].app`,
  and attaches `v._ch`, but **never touches, namespaces, validates, or dedupes `v.id`**. The only
  uniqueness guard in the whole file is on *channel* ids (`index.html:1028`).
- `template/channel.json` ships `"id": "my-first-video"` and `"id": "my-live-replay"`, and `README.md`
  instructs every new publisher to copy that template. Colliding video ids are produced by the documented
  onboarding path, not merely permitted by it.

Therefore the subject id is channel-qualified:

```js
// provider: rapp-vision-videos/1.0
// subject_id = "<channel.id>/<video.id>"   ← channel id from the channel FILE, not the registry entry
async function enumerate() {
  const registry = await (await fetch("channels.json", { cache: "no-cache" })).json(); // throws -> P3
  const channels = await Promise.all(registry.channels.map(fetchChannel));             // throws -> P3
  const subjects = [];
  for (const c of channels) {
    for (const v of (c.videos || [])) {
      if (!v.id || !c.id) continue;                        // P3 per-record tolerance
      subjects.push({
        subject_id: `${c.id}/${v.id}`,
        title:      v.title || v.id,
        url:        `https://kody-w.github.io/rapp-vision/#/watch/${encodeURIComponent(v.id)}`,
        digest:     null,                                  // media bytes are not content-addressed here
        seed:       { channel: c.name, published: v.published },
      });
    }
  }
  subjects.sort((a, b) => a.subject_id.localeCompare(b.subject_id));   // P2 determinism
  return subjects;
}

const SUBJECT_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]*\/[A-Za-z0-9][A-Za-z0-9._-]*$/;
```

Two further requirements specific to this provider, both grounded:

- **The channel id MUST come from inside `channel.json`, not from the `channels.json` registry entry.** For
  channels a user adds through the UI, the registry entry id is a throwaway timestamp —
  `index.html:903`: `await fetchChannel({ id: "custom-" + Date.now(), url })` — while the value written back
  and used everywhere else is `c.id` from the file (`index.html:905`, `:684`, `:837`, `:1046`).
- **`enumerate()` MUST NOT be derived from the player's `VIDEOS` array.** `rebuild()`
  (`index.html:1045-1050`) filters to *subscribed* channels only, so `VIDEOS` is a per-viewer subset. A
  provider keyed off it would silently omit every unsubscribed channel's subjects — a partial enumeration,
  forbidden by P1.

Every rapp-vision channel is a **live replay** — a running application driven by a script, i.e. content a
machine performs. Under §1.3 that changes nothing about how its numbers are collected: the viewers are people,
so the counts are people.

### 5.5 Profiles

A **profile** is a named, versioned binding of this protocol to one subject kind. A conforming implementation
**MUST** declare exactly one profile, and the profile string **MUST** appear in the snapshot.

A profile declares, and **MUST** publish in the snapshot (§8):

| Field | Meaning |
|---|---|
| `profile` | `"<name>/<major>.<minor>"`, e.g. `"rar-agents/1.0"` |
| `subject_kind` | singular noun: `"agent"`, `"video"`, `"tool"`, `"egg"`, `"channel"` |
| `subject_id_pattern` | anchored regex (I4) |
| `surfaces` | the surface registry (§7.2) |
| `rank_formula` | prose + expression, **or omitted entirely**. §8.3 |
| `counting_rules` | the prose a reader needs before trusting a number. M29 |

A profile **MAY** rebind reaction meanings, add surfaces, and define a rank. A profile **MUST NOT** relax any
invariant in §9 and **MUST NOT** modify §1 in any way; profiles nest under the protocol, they never override it.

---

## 6. Thread binding

- **T1.** There **MUST** be exactly one Discussion per subject, and its **title MUST be exactly the
  `subject_id`** — no prefix, no display name, no decoration. The title is the join key.
- **T2.** Threads **MUST** live in a Discussion category that **ordinary users cannot post in** (on GitHub
  today, an Announcements-type category is maintainer-only). The collector **MUST** filter on category name
  and discard every node outside it.
- **T3. Anti-spoof is two independent checks, and both are REQUIRED.** A node counts only if
  **(a)** its title matches `subject_id_pattern` **and (b)** its title is present in the set returned by
  `enumerate()`. Belt and suspenders: the regex alone admits well-formed names for subjects that do not
  exist; membership alone admits anything a maintainer mistyped into a title.
- **T4.** If two threads exist for one subject, the **lowest discussion number wins**, deterministically.
- **T5.** Thread creation **MUST** be idempotent (create only for subjects with no thread) and **capped per
  run** (M17).
- **T6.** A newly created thread **MUST** receive its **full** surface set in the same pass, so a subject can
  record signal the day it lands and needs no back-fill.
- **T7.** Thread creation is the collector's job and is a **machinery** act, not engagement. Creating a thread
  **MUST NOT** produce any count — no seed endorsement, no priming reaction, no "the bot upvoted it to start
  the ball rolling" (L2).

Verified in RAR (`scripts/discussion_ratings.py`) and independently in rapp-vision
(`scripts/rapp_metrics.py:573-600`), which implement the same four checks:

```python
# RAR build_snapshot(), lines 338-341 and 362-365
if ((node.get("category") or {}).get("name")) != category:      # T2
    continue
title = str(node.get("title", "")).strip()
if not is_agent_title(title) or title not in registry_names:    # T3 (a) and (b)
    continue
...
existing = ratings.get(title)
if existing is None or entry["number"] < existing["number"]:    # T4
    ratings[title] = entry
```

**Why this beats building your own:** the platform supplies a permanent public URL per subject that CI can
both read counters from *and* write a report card to, plus identity, spam control, and per-user dedup. Without
it you need a database, an auth system, and abuse controls before you can collect the first number.

---

## 7. Signal surfaces — the marker comment as an n-option poll

### 7.1 Why a comment and not a poll

GitHub Discussions **has** a real poll type (`DiscussionPoll`, `addDiscussionPollVote`). It is unusable here,
for one concrete reason:

> `createDiscussion` accepts only `repositoryId`, `title`, `body`, `categoryId`. **A poll can only be created
> by hand in the web UI.**

This is recorded verbatim in both reference implementations (`RAR/scripts/discussion_ratings.py:95-107`;
`rapp-vision/scripts/rapp_metrics.py:145-156`), together with the judgement that follows from it:

> *"A signal surface that needs a human to click through the web UI once per agent is not a pattern; it is a
> chore that will not survive the catalog growing."*

A **comment** *is* creatable over the API (`addDiscussionComment`), and every comment carries **all eight
reaction contents as independent, per-user-deduped counters**. So one comment behaves as an eight-option poll
and can be provisioned automatically for every subject the moment it enters the subject set.

> **The generalizable move:** when the platform's first-class primitive cannot be provisioned
> programmatically, find the primitive that *can* be and that carries the same counter semantics. A surface
> that requires manual setup per subject does not scale past the first fifty and will be half-missing forever.

Note the tenet at work: the comment is **written by a machine** and the reactions on it are **left by people**.
The actor on each reaction is a human, so every one of those counters is a human counter (§1.2). The machine's
authorship of the container is irrelevant — except that it must be excluded from `conversation` (L5, M10),
because *writing the comment* was a machine action.

### 7.2 The surface registry

Surfaces **MUST** be declared as data — a registry keyed by `surface_id` — never hard-coded at call sites.
Adding a surface **MUST** be a one-entry change that the existing idempotent provisioner back-fills across the
whole subject set on subsequent capped runs.

The registry covers **every** object a counter is read from, including the top post. `endorsements` is a
published counter like any other, so the object and the single reaction content it counts are declared here —
a reader must never have to guess what the headline number means (R4, and the Gap-1 failure in §14).

```json
{
  "surfaces": {
    "endorsement": {
      "kind": "endorsement",
      "object": "top_post",
      "reaction": "THUMBS_UP",
      "means": "distinct people who vouched for this subject"
    },
    "download": {
      "kind": "tally",
      "marker": "<!-- rapp-metrics:tally:download -->",
      "reaction": "THUMBS_UP",
      "means": "distinct signed-in GitHub users who acquired this subject"
    },
    "experience": {
      "kind": "poll",
      "marker": "<!-- rapp-metrics:poll:experience -->",
      "map": {
        "THUMBS_UP": "worked",
        "THUMBS_DOWN": "did_not_work",
        "CONFUSED": "stuck",
        "HEART": "regular_use",
        "ROCKET": "shipped",
        "EYES": "want_to_try",
        "HOORAY": "saved_time"
      }
    },
    "review:rubric": {
      "kind": "review",
      "marker": "<!-- rapp-metrics:review:rubric -->",
      "reviewer_id": "rubric",
      "feeds": "reviewer_feedback",
      "map": {
        "THUMBS_UP": "agree",
        "THUMBS_DOWN": "disagree",
        "CONFUSED": "unclear",
        "HEART": "useful"
      }
    }
  }
}
```

- **S1.** Every **comment** surface (`tally`, `poll`, `review`) **MUST** carry a `marker`: an HTML comment in
  the comment body, invisible when rendered, used to locate the comment idempotently **and** to exclude it from
  `conversation`. The format `<!-- rapp-metrics:<kind>:<surface_id> -->` is **RECOMMENDED**; any stable string
  is permitted, but the exact marker **MUST** be published in the snapshot's surface registry so a reader can
  audit it. An `endorsement` surface carries no marker — its object is the top post, named by `object`, not a
  comment to be found.
  **A marker is a routing label, never proof of authorship.** It is recognized only under M40: the marker
  **MUST** be the first non-whitespace token of the body **and** the comment **MUST** be authored by the
  collector identity. Substring containment anywhere in a body is **NOT** sufficient and **MUST NOT** be used —
  GitHub's "Quote reply" copies the raw body including the invisible HTML comment, so a substring test deletes
  a human quote-reply from `conversation` (the §1.3 error) while still admitting any unmarked machine comment.
  *(Both reference implementations predate the recommended format and use their own strings —
  `<!-- rar:download-tally -->`, `<!-- rar:signal -->`, `<!-- rapp-vision:watch-tally -->`,
  `<!-- rapp-vision:signal -->`, `<!-- rapp-vision:editorial -->`. Those strings are conformant once declared.
  On the recognition rule the two differ: rapp-vision's `is_machinery_comment()` already requires
  `body.startswith(marker)` **and** `viewerDidAuthor` or an allow-listed author login, which is M40; RAR's
  `marker_comment_of()` is a plain `if marker in (c.get("body") or "")` at
  `scripts/discussion_ratings.py:284`, which is not — see §14.)*
- **S2.** Provisioning **MUST** be **per-marker idempotent**: a thread missing only the newer surface receives
  only that one.
- **S3.** Provisioning **MUST** be capped per run and **MUST** drain over successive scheduled runs (M17).
- **S4.** Each surface's counters are read **only** from the comment bearing its marker. Reactions on the top
  post, on another surface, or on a human reply **MUST NOT** contribute to it (M9).
- **S5.** An absent surface **MUST** read as all-zeros of the correct shape, so a not-yet-provisioned subject
  is structurally identical to an unanswered one and callers need no special case.
- **S6.** The surface body **MUST** state, in the comment itself, what each reaction means and that counts are
  people rather than clicks. The instruction lives where the click happens.
- **S7.** A surface of kind `review` is the editorial comment (§10). Its **body** is machine-authored
  (editorial lane) and its **reactions** are human (human lane) and feed `reviewer_feedback`. A conforming
  collector **MUST** read those reactions. Discarding them because the comment was machine-written is the
  §1.3 error and is non-conformant.
- **S8.** A surface of kind `endorsement` is **REQUIRED** wherever `endorsements` is published. It declares
  `object` (`"top_post"`) and exactly one `reaction`, and it **MUST NOT** declare a `map` — an endorsement is
  one content, and a counter summed over several contents is forbidden by M39. `kind: "tally"` follows the
  same rule: one `reaction`, never a set.
- **S9. Every `review` surface MUST declare a `reviewer_id`, and that id is what `reviewer_feedback` is keyed
  by.** Without it the key is underivable: a thread carries a review *comment*, while §10.2's roster is a panel
  of N reviewers, and nothing else in the document maps one comment's reactions to one reviewer.
  - **One declared `review` surface per reviewer whose feedback is published separately.** Each gets its own
    `surface_id`, its own `marker`, and its own `reviewer_id`; the community can then rate each panellist
    independently, which is the whole point of §1.5.
  - **A panel that publishes a single combined comment MUST use a single synthetic `reviewer_id`** (e.g.
    `"panel"`), and that id **MUST** appear in the editorial roster like any other reviewer (E5). Reactions on
    one comment cannot be attributed to individual panellists after the fact, so the honest key is the panel,
    not a guess.
  - The `reviewer_id` **MUST** be a stable opaque id and **MUST NOT** embed the rubric version — versioning is
    `rubric_version`'s job (E7), and an id that moves with the rubric orphans the feedback history it keys.

### 7.3 The default reaction map

GitHub exposes exactly eight reaction contents. These are the **protocol defaults** for a `poll` surface,
taken verbatim from `RAR/scripts/discussion_ratings.py:113-121`:

| Reaction | Default channel | Meaning |
|---|---|---|
| `THUMBS_UP` 👍 | `worked` | it did the thing |
| `THUMBS_DOWN` 👎 | `did_not_work` | it did not do the thing |
| `CONFUSED` 😕 | `stuck` | could not get it running at all |
| `HEART` ❤️ | `regular_use` | I use this repeatedly |
| `ROCKET` 🚀 | `shipped` | I put this in front of someone real |
| `EYES` 👀 | `want_to_try` | intent, not experience |
| `HOORAY` 🎉 | `saved_time` | measurable payoff |
| `LAUGH` 😄 | **(reserved, unmapped)** | deliberately means nothing |

And for a `review` surface (§1.5 — the community rating the reviewer):

| Reaction | Default channel | Meaning |
|---|---|---|
| `THUMBS_UP` 👍 | `agree` | this review matches my experience |
| `THUMBS_DOWN` 👎 | `disagree` | this review is wrong |
| `CONFUSED` 😕 | `unclear` | I cannot tell what it is claiming |
| `HEART` ❤️ | `useful` | this helped me decide |
| everything else | **(unmapped)** | — |

Rules:

- **R1.** A profile **MAY** rebind any reaction to a different channel name, **MAY** map the reserved `LAUGH`
  slot, and **MAY** define additional surfaces each with their own map.
- **R2.** Within one surface, **no two channels MAY share a reaction**, and a surface **MUST NOT** declare
  more than eight channels. This **MUST** be pinned by a test. Two channels sharing one emoji are
  *permanently indistinguishable* — the counts can never be separated retroactively, at any cost, because the
  platform stores one set of reactors.
- **R3.** Leaving a reaction unmapped is **RECOMMENDED** over inventing a meaning for it. The reference
  implementation's reasoning, verbatim: *"there is no honest question it answers, and an option that means
  nothing pollutes every other count."*
- **R4.** The effective map **MUST** be published in the snapshot. A reader **MUST NOT** have to read the
  collector's source to learn what `signals.experience.shipped` counts.
- **R5.** A negative channel (`did_not_work`, `stuck`, `disagree`) **MUST** be counted and published, and
  **MUST NOT** subtract from any other number (M7). rapp-vision states this in the surface body itself:
  *"The last two are real answers, not complaints: they are counted and published under their own names, and
  they never subtract from anything."*
- **R6.** A `review` surface's channels feed `reviewer_feedback` **only**. They **MUST NOT** be merged into
  `signals`, and `disagree` **MUST NOT** subtract from the subject's `endorsements` or `rank` (L6).
- **R7. No counter MAY be the sum of two or more reaction contents on the same object.** Per-user dedup is
  **per emoji**: the platform stores one reactor set per *(object, content)* pair, so one person who leaves
  👍 and ❤️ appears once in each set. Adding those sets counts that person twice. A counter built that way is
  a **click-count**, which is the one thing M6 says this protocol cannot publish, and it re-inflates exactly
  the way §4 claims is impossible "by construction". `endorsements` and every `tally` are therefore
  **one content each** (S8). A profile that wants several positive signals **MUST** publish them as separate
  named channels of a `poll` surface, where each stays independently attributable, rather than adding them
  together into one number nobody can decompose. Pinned by a test (M39, item 64).

### 7.4 What each object means — one object, one metric

| Object on the thread | Written by | Reacted on by | Metric | Never also means |
|---|---|---|---|---|
| top post | collector | people | **endorsement** | acquisition, experience |
| `tally` surface comment | collector | people | **acquisition** (or whatever act it names) | endorsement |
| `poll` surface comment | collector | people | **experience**, per channel | endorsement, acquisition |
| `review` surface comment | **a model** | people | **reviewer_feedback**, per channel | anything about the subject |
| a human reply | a person | people | **conversation** | approval |
| a machine reply (marked) | a bot | people | nothing — excluded (L5) | conversation |

Conflating these produces one number that means three things and defends none of them.

---

## 8. The snapshot — `rapp-metrics/1.0`

### 8.1 Document shape

One document for the human lane. `state/metrics.json` is **RECOMMENDED**; the path **MUST** be stable once
published.

```jsonc
{
  "schema": "rapp-metrics/1.0",          // REQUIRED, exact string
  "profile": "rar-agents/1.0",           // REQUIRED
  "subject_kind": "agent",               // REQUIRED
  "subject_id_pattern": "^@[A-Za-z0-9][A-Za-z0-9_-]*/[a-z0-9_]+$",  // REQUIRED
  "repo": "kody-w/RAR",                  // REQUIRED, owner/repo hosting the threads
  "category": "Announcements",           // REQUIRED, the maintainer-only category
  "collector_logins": ["github-actions[bot]"],  // REQUIRED, non-empty. M40's author check, published
                                         //   so a reader can audit which comments were treated as
                                         //   machinery. Automated identities only — never a person (PR1).
  "lanes": {                             // REQUIRED. the tenet, machine-readable
    "human": "Every count in `subjects` and `reviewer_feedback` was produced by a person acting with their own credential. The actor determines the lane; the authorship of the subject is irrelevant.",
    "editorial": "state/editorial.json (rapp-metrics-editorial/1.0). Machine-authored. Summed into nothing here."
  },
  "surfaces": { ... },                   // REQUIRED, §7.2 — includes each map, verbatim
  "rank_formula": {                      // OPTIONAL; REQUIRED if any subject carries "rank"
    "expression": "2 * endorsements + tallies.download",
    "why": "storefront ranking for a market where endorsement is scarcer than acquisition"
  },
  "counting_rules": [ "…", "…" ],        // REQUIRED, non-empty. M29
  "sources": [                           // RECOMMENDED: one URL per externally-sourced number
    { "metric": "endorsements", "from": "https://github.com/kody-w/RAR/discussions" }
  ],
  "totals": {                            // OPTIONAL aggregates. Every one MUST be defensible.
    "subjects": 272,
    "subjects_with_signal": 5,
    "orphaned_subject_ids": 0            // REQUIRED if any key was dropped. M14
  },
  "subjects": {                          // REQUIRED. keys sorted. one entry per enumerated subject
    "<subject_id>": {
      "endorsements": 0,                 // REQUIRED, int >= 0
      "conversation": 0,                 // REQUIRED, int >= 0, machine-authored comments subtracted
      "tallies":  { "download": 0 },     // REQUIRED (MAY be {}), surface_id -> int
      "signals":  { "experience": {      // REQUIRED (MAY be {}), surface_id -> channel -> int
        "worked": 0, "did_not_work": 0, "stuck": 0,
        "regular_use": 0, "shipped": 0, "want_to_try": 0, "saved_time": 0
      } },
      "rank": 0,                         // OPTIONAL; present only if rank_formula is declared
      "thread": { "url": "…", "number": 380 }   // REQUIRED
    }
  },
  "reviewer_feedback": {                 // REQUIRED if any `review` surface exists; else omitted
    "<reviewer_id>": {                   // §1.5 — humans rating the machine reviewer. The key is the
                                         //   reviewer_id declared on a `review` surface (S9) and MUST
                                         //   resolve to an entry in the editorial roster (E5).
      "surface": "<surface_id>",         // which review surface these reactions were read from
      "counts": { "agree": 0, "disagree": 0, "unclear": 0, "useful": 0 },
      "subjects": {                      // OPTIONAL per-subject breakdown
        "<subject_id>": { "agree": 0, "disagree": 0, "unclear": 0, "useful": 0 }
      }
    }
  }
}
```

### 8.2 Field rules

- **F1.** `schema` **MUST** be the literal `"rapp-metrics/1.0"`. Consumers **MUST** check it and **MUST**
  degrade to rendering nothing on a mismatch.
- **F2.** `subjects` **MUST** contain one entry for **every** subject returned by `enumerate()`, including
  those with all-zero counts. Absence of a key means "this subject does not exist", never "this subject has no
  signal". *(RAR complies: 272 entries, of which 5 have any nonzero value.)*
  A profile **MAY** instead omit never-provisioned subjects entirely **only if** `counting_rules` states that
  absence means "no thread yet" — but it **MUST NOT** be possible for a reader to confuse the two claims.
- **F3.** All counter values **MUST** be non-negative integers. There is no negative primitive anywhere in
  this protocol (M7).
- **F4.** Object keys **MUST** be serialized in sorted order and the serialization **MUST** be stable, so
  identical counts produce identical bytes (M23).
- **F5.** The document **MUST NOT** contain any field that changes when no measured value changed. In
  particular it **MUST NOT** carry `generated_at`, `updated_at`, a run id, or a build number.
- **F6.** The document **MUST NOT** contain usernames, logins, avatars, emails, or any per-person identifier,
  even though the GitHub API exposes reactor identities (§12). **One exception, and only one:**
  `collector_logins` (F12) names the **automated** identities whose comments are treated as machinery. Those
  are not people, and publishing them is what makes M40's author check auditable rather than asserted. No
  reactor's identity, and no human commenter's identity, may appear anywhere in this document.
- **F7.** An unknown value **MUST** be `null` or absent, never `0`. `null` means "not wired / not read"; `0`
  means "read successfully, and it was zero" (M20).
- **F8.** The document **MUST NOT** contain any machine-authored assessment, score, verdict, or review text.
  That is the editorial document's job (§10). The **only** machine-adjacent field permitted here is
  `reviewer_feedback`, and it is permitted precisely because its actor is a human (§1.5).
- **F9.** No field **MAY** encode the authorship of a subject in a way that any counter, rank, or rendering
  branches on (L1, L7). Publishing an authorship label for *display* is permitted; branching a number on it is
  not.
- **F10.** A publisher **SHOULD** also write a content-addressed copy (e.g.
  `state/metrics.<sha256[:8]>.json`) so consumers can pin, per `rapp-static-api/1.0`. Byte-stability (M23) is
  what makes this worth doing: identical counts produce an identical digest, so a pin does not churn and the
  CDN cache is not invalidated by a no-op day.
- **F12.** `collector_logins` **MUST** be present and non-empty, and **MUST** list every identity whose
  comments the collector treats as machinery (M40b). It is the one authorship claim a reader can check: with it
  a reader can open the thread and confirm that the comments subtracted from `conversation` were in fact
  written by the machinery, and that no human comment was. It **MUST** contain only automated identities —
  putting a person's login here is both an F6 violation and an admission that a human's comments are being
  deleted from a human counter. *(F11 is in §8.6, with the mapping table it governs.)*

### 8.3 `rank` is optional and profile-owned

RAR's `score = 2 * upvotes + downloads` is an arbitrary storefront weighting for a market where endorsement is
scarcer than acquisition. It is **not** protocol. A profile that publishes a `rank` **MUST** publish its
formula in `rank_formula` next to it, and a reader **MUST** be able to recompute it from the fields in the
same document. Most subject kinds should publish no rank at all.

`rank` **MUST NOT** include any editorial value and **MUST NOT** include `reviewer_feedback` (L6).

### 8.4 Worked example — RAR (`subject = agent`)

Real values, read from `state/discussion_ratings.json` in a scratch clone, re-expressed in the
`rapp-metrics/1.0` shape. RAR's live file uses the profile-native schema `rar-discussion-ratings/1.0` with
top-level key `agents` (§8.6); the counts below are exactly as found — including the fact that of 272 threads,
only five carry any signal at all.

```json
{
  "schema": "rapp-metrics/1.0",
  "profile": "rar-agents/1.0",
  "subject_kind": "agent",
  "subject_id_pattern": "^@[A-Za-z0-9][A-Za-z0-9_-]*/[a-z0-9_]+$",
  "repo": "kody-w/RAR",
  "category": "Announcements",
  "collector_logins": ["github-actions[bot]"],
  "lanes": {
    "human": "Every count in `subjects` was produced by a person acting with their own GitHub credential.",
    "editorial": "state/editorial.json — machine-written critic panel. Summed into nothing here."
  },
  "surfaces": {
    "endorsement": {
      "kind": "endorsement",
      "object": "top_post",
      "reaction": "THUMBS_UP",
      "means": "distinct people who vouched for this agent"
    },
    "download": {
      "kind": "tally",
      "marker": "<!-- rar:download-tally -->",
      "reaction": "THUMBS_UP",
      "means": "distinct signed-in GitHub users who acquired the agent.py"
    },
    "experience": {
      "kind": "poll",
      "marker": "<!-- rar:signal -->",
      "map": {
        "THUMBS_UP": "worked", "THUMBS_DOWN": "did_not_work", "CONFUSED": "stuck",
        "HEART": "regular_use", "ROCKET": "shipped", "EYES": "want_to_try",
        "HOORAY": "saved_time"
      }
    }
  },
  "rank_formula": {
    "expression": "2 * endorsements + tallies.download",
    "why": "storefront ranking; endorsement is scarcer than acquisition, so it weighs double"
  },
  "counting_rules": [
    "Reactions are one per user per emoji, so every count is people, not clicks.",
    "Most agents in this registry were written by a machine. That changes nothing here: the people endorsing and installing them are people, and their signal is counted at full weight.",
    "No bot, app installation, or CI token ever reacts. The collector creates threads and writes surface comments; it never votes.",
    "Self-reactions count. A maintainer reacting to their own agent is counted like anyone else, so seeded test data is indistinguishable from organic data.",
    "Reacting is publicly attributable on GitHub. This is a review surface, not telemetry — but it is not anonymous.",
    "tallies.download counts signed-in people who tapped the tally. Release-asset downloads are a different population, measured server-side including signed-out fetches, and the two are NEVER summed.",
    "Negative experience is counted in signals.experience.did_not_work and signals.experience.stuck. It never subtracts from endorsements or rank."
  ],
  "totals": { "subjects": 272, "subjects_with_signal": 5, "orphaned_subject_ids": 0 },
  "subjects": {
    "@aibast-agents-library/account_risk_assessment": {
      "endorsements": 0,
      "conversation": 0,
      "tallies": { "download": 1 },
      "signals": { "experience": {
        "worked": 0, "did_not_work": 0, "stuck": 0,
        "regular_use": 0, "shipped": 0, "want_to_try": 0, "saved_time": 0
      } },
      "rank": 1,
      "thread": { "url": "https://github.com/kody-w/RAR/discussions/208", "number": 208 }
    },
    "@borg/borg_agent": {
      "endorsements": 1,
      "conversation": 0,
      "tallies": { "download": 1 },
      "signals": { "experience": {
        "worked": 0, "did_not_work": 0, "stuck": 0,
        "regular_use": 0, "shipped": 0, "want_to_try": 0, "saved_time": 0
      } },
      "rank": 3,
      "thread": { "url": "https://github.com/kody-w/RAR/discussions/310", "number": 310 }
    },
    "@rapp/basic_agent": {
      "endorsements": 1,
      "conversation": 0,
      "tallies": { "download": 0 },
      "signals": { "experience": {
        "worked": 0, "did_not_work": 0, "stuck": 0,
        "regular_use": 0, "shipped": 0, "want_to_try": 0, "saved_time": 0
      } },
      "rank": 2,
      "thread": { "url": "https://github.com/kody-w/RAR/discussions/380", "number": 380 }
    }
  }
}
```

**One correction to this example, stated rather than hidden.** The `endorsements` values above are RAR's live
`upvotes` figures, and RAR does **not** compute `upvotes` the way this document defines `endorsements`. It
computes `positive_score()` — a **sum over five reaction contents**,
`{THUMBS_UP, HEART, HOORAY, ROCKET, LAUGH}` (`scripts/discussion_ratings.py:78-80`, summed at `:272-278`,
published as `upvotes` at `:343`). Because dedup is per-emoji, one person leaving 👍❤️🎉🚀😄 contributes **5**.
That is a click-count, forbidden by M39 and R7, so **`upvotes` is not a conforming `endorsements` value** and
these three numbers are re-expressed shapes, not conforming ones. (At these volumes — one endorsement each on
two agents — the sum and the single-content count are almost certainly identical, but "almost certainly" is
not a conformance claim, and re-reading the threads for `THUMBS_UP` alone was not done.) The `endorsement`
surface entry shown above is what a conforming `rar-agents/1.0` profile **would** declare; the shipped
collector does not implement it. §14, RAR Gap 5.

### 8.5 Worked example — rapp-vision (`subject = video`)

The `subject_id`s are real: the `rock-tumbler` channel file declares `"id": "rock-tumbler"` with videos
`rock-tumbler-showcase`, `rock-tumbler-short`, `rock-tumbler-reel`. **The counts are invented** — at the time
of writing the live snapshot's `videos` map is empty, because no thread has been seeded yet.

This example carries a `review` surface, so it shows both halves of §1 in one file: a machine wrote the review;
people reacted to it; those reactions are human counters in `reviewer_feedback`, and they are not mixed into
the video's own numbers.

```json
{
  "schema": "rapp-metrics/1.0",
  "profile": "rapp-vision-videos/1.0",
  "subject_kind": "video",
  "subject_id_pattern": "^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$",
  "repo": "kody-w/rapp-vision",
  "category": "Announcements",
  "collector_logins": ["github-actions[bot]"],
  "lanes": {
    "human": "Every count in `subjects` and `reviewer_feedback` came from a person. Live-replay entries are performed by a machine; the audience is not.",
    "editorial": "state/editorial.json — a deterministic rubric reviews each entry. Summed into nothing here."
  },
  "surfaces": {
    "endorsement": {
      "kind": "endorsement",
      "object": "top_post",
      "reaction": "THUMBS_UP",
      "means": "distinct people who vouched for this entry"
    },
    "watched": {
      "kind": "tally",
      "marker": "<!-- rapp-vision:watch-tally -->",
      "reaction": "THUMBS_UP",
      "means": "distinct signed-in people who said they watched this — not a play count"
    },
    "reception": {
      "kind": "poll",
      "marker": "<!-- rapp-vision:signal -->",
      "map": {
        "THUMBS_UP": "watched_it_all",
        "HOORAY": "learned_something",
        "HEART": "want_more_like_this",
        "ROCKET": "tried_it_myself",
        "EYES": "saved_for_later",
        "THUMBS_DOWN": "too_long",
        "CONFUSED": "confusing"
      }
    },
    "review:rubric": {
      "kind": "review",
      "marker": "<!-- rapp-vision:editorial -->",
      "reviewer_id": "rubric",
      "feeds": "reviewer_feedback",
      "map": { "THUMBS_UP": "agree", "THUMBS_DOWN": "disagree", "CONFUSED": "unclear", "HEART": "useful" }
    }
  },
  "counting_rules": [
    "subject_id is <channel_id>/<video_id>. A video id is unique only inside its own channel.json, so the bare id is not a key.",
    "The channel id is the one declared INSIDE channel.json, never the registry entry id in channels.json — user-added channels get a throwaway 'custom-<timestamp>' entry id.",
    "Every entry on this network is machine-performed (a live replay drives a real app). The people watching and reacting are people, and their signal counts at full weight.",
    "Nothing here is derived from playback. The player does not report watch time, and this protocol adds no such path: every number below is an explicit reaction a person left on GitHub.",
    "reviewer_feedback counts people reacting to the MACHINE REVIEW. It rates the reviewer, not the video, and is summed into nothing else. Sustained 'disagree' means the rubric is wrong.",
    "Reactions are one per user per emoji, so every count is people, not plays."
  ],
  "totals": { "subjects": 21, "subjects_with_signal": 2, "orphaned_subject_ids": 0 },
  "subjects": {
    "rock-tumbler/rock-tumbler-showcase": {
      "endorsements": 7,
      "conversation": 2,
      "tallies": { "watched": 11 },
      "signals": { "reception": {
        "watched_it_all": 6, "learned_something": 4, "want_more_like_this": 3,
        "tried_it_myself": 2, "saved_for_later": 4, "too_long": 1, "confusing": 1
      } },
      "thread": { "url": "https://github.com/kody-w/rapp-vision/discussions/12", "number": 12 }
    },
    "rock-tumbler/rock-tumbler-short": {
      "endorsements": 0,
      "conversation": 0,
      "tallies": { "watched": 0 },
      "signals": { "reception": {
        "watched_it_all": 0, "learned_something": 0, "want_more_like_this": 0,
        "tried_it_myself": 0, "saved_for_later": 0, "too_long": 0, "confusing": 0
      } },
      "thread": { "url": "https://github.com/kody-w/rapp-vision/discussions/13", "number": 13 }
    }
  },
  "reviewer_feedback": {
    "rubric": {
      "surface": "review:rubric",
      "counts": { "agree": 3, "disagree": 5, "unclear": 2, "useful": 1 },
      "subjects": {
        "rock-tumbler/rock-tumbler-showcase": { "agree": 3, "disagree": 5, "unclear": 2, "useful": 1 }
      }
    }
  }
}
```

**The `reviewer_feedback` key is `"rubric"`, and that is not a free choice.** It is the `reviewer_id` declared
on the `review:rubric` surface (S9), and E5 requires it to resolve to an entry in the editorial document's
roster — so `state/editorial.json` for this profile **MUST** contain:

```jsonc
"reviewers": [
  { "id": "rubric", "name": "The Rubric",
    "lens": "structure, pacing, and whether the entry states what it is",
    "model": "deterministic-rubric" }
]
```

Three things this pins down that an earlier draft left underivable:

- **The key is a roster id, never a rubric or profile string.** A version-bearing key like
  `"rapp-vision-rubric/1.0"` orphans its own feedback history the first time E7 forces a version bump; the
  regime a reaction was left under is recorded by `rubric_version`, not by mangling the identity (S9).
  *(rapp-vision's shipped collector currently uses `EDITORIAL_BY = "rapp-vision-rubric/1.0"` for this
  attribution — a stable roster id and a roster entry to resolve it against are what S9 adds.)*
- **One reviewer here, so one `review` surface.** A two-reviewer panel publishing feedback separately declares
  two `review` surfaces with two markers and two `reviewer_id`s; a panel publishing one combined comment
  declares one surface with a synthetic panel id, because reactions on a single comment cannot be split
  between panellists afterwards (S9).
- **`surface` names the surface the reactions were read from,** so a reader can walk from the number back to
  the exact comment and its published reaction map.

Read the counts as the protocol intends: **five people disagreed with the machine review and three agreed.**
The video's own `endorsements` are untouched by that — people disliking a review is not people disliking the
video. What it does mean is that this rubric is being told it is wrong, publicly, by name, and that is
precisely the loop §1.5 exists to expose.

Note what is **absent** everywhere in this example: no view count, no watch time, no completion rate, no
per-viewer anything. rapp-vision states in three separate places in `index.html` that nothing phones home
(`:190-191`, `:713`, `:942`). This protocol does not change that: the page performs one read-only `GET` of a
public aggregate file, sending no user data, which is the same class of request it already makes for
`channels.json`. A conforming adopter **SHOULD** review that copy anyway so it does not imply more than it now
means.

### 8.6 Profile-native snapshots and the mapping table

Both reference implementations publish a **profile-native** snapshot: the same information under their own
schema string and their own field names, predating this spec. That is permitted, and this section is what makes
it consumable — but it is a **conformance gap**, not a variant: a document that does not carry
`"schema": "rapp-metrics/1.0"` is not a `rapp-metrics/1.0` document, and a generic reader **MUST NOT** guess.

- **F11.** A profile-native snapshot **MUST** publish a mapping to the canonical field names, either by
  emitting the canonical document alongside it or by publishing the table below in its own docs. A generic
  consumer **MUST** be given an explicit adapter; it **MUST NOT** infer field meanings from key names.

| Canonical (`rapp-metrics/1.0`) | RAR (`rar-discussion-ratings/1.0`) | rapp-vision (`rapp-vision-metrics/1.0`) |
|---|---|---|
| `subjects` | `agents` | `videos` |
| `endorsements` — **one** reaction content (S8, M39) | `upvotes` — **a sum over five reaction contents** (`THUMBS_UP, HEART, HOORAY, ROCKET, LAUGH`; `discussion_ratings.py:78-80`, `:272-278`, `:343`). Per-emoji dedup means one person can contribute 5, so this is a click-count. **NOT a conforming `endorsements` value** — §14 Gap 5 | `upvotes` — the same five-content sum in `positive_score()`. **Also not conforming**, for the same reason |
| `conversation` | `comments` — top-level only, replies never fetched (M10) | `comments` — top-level only, replies never fetched; stated in the module's own KNOWN LIMITS |
| `tallies.download` | `downloads` | `watched` |
| `signals.<surface>.<channel>` | `signals.<channel>` (one surface) | `signals.<channel>` (one surface) |
| `rank` | `score` | `score` |
| `thread.url` / `thread.number` | `url` / `number` | `url` / `number` |
| `reviewer_feedback` | *(absent — no `review` surface exists)* | present, but nested inside the `editorial` block rather than in the human document, and keyed by `EDITORIAL_BY` rather than by a roster `reviewer_id` — see §14 |
| editorial document | `state/critic_reviews.json`, `state/curator_reviews.json` | `editorial` block in the same file |

The single-surface collapse in the middle rows is why §8.1 nests `signals` under a `surface_id`: with one
surface the extra level looks like ceremony, and the day a second surface is added without it, every existing
channel name becomes ambiguous and no historical file can be disambiguated.

---

## 9. Invariants

Each invariant is stated, justified, and paired with its failure mode. **All are REQUIRED unless marked
SHOULD.** M30–M40 are §1 restated as testable invariants; they are the ones that matter most. M30–M36 state
what the two lanes are; **M37–M40 are what makes half one checkable rather than merely declared** — M38
classifies the actor, M39 keeps a counter from being a click-count, and M37/M40 keep the machinery boundary
from drifting silently as a thread grows or a human quotes a marker.

### Identity and anti-spoofing

**M1 — One durable platform-owned thread per subject, titled with the `subject_id`.**
*Why:* it gives every subject a permanent public URL that CI can read counters from and write a report card
to, with the platform supplying identity, spam control, and dedup.
*Dropped:* you need your own database, auth, and abuse controls before collecting the first signal.

**M2 — Threads live in a category ordinary users cannot post in.**
*Why:* the ranking input must not be user-writable.
*Dropped:* anyone opens a thread titled with a subject id and mints their own counters.

**M3 — Membership is two independent checks: shape regex AND presence in the enumerated subject set.**
*Why:* they fail in opposite directions.
*Dropped:* the regex alone admits well-formed names for subjects that do not exist; membership alone admits
any title someone mistyped.

**M4 — Duplicate threads resolve deterministically to the lowest number.**
*Why:* API page order is not stable.
*Dropped:* the published count silently flips between two threads run to run.

**M5 — `subject_id` permanence is machine-enforced by an append-only ledger and a blocking CI check.**
*Why:* every counter is keyed on that identity, and install URLs live in other people's systems.
*Dropped:* a rename orphans every count ever collected and breaks links you cannot notify anyone about.

### Counting

**M6 — Counts are people, not clicks; per-user dedup is delegated to the platform wherever possible.**
GitHub enforces one reaction per user per subject per emoji, so a count is a people-count *by construction*;
the client additionally checks `viewerHasReacted` before adding. Where dedup must be hand-rolled, the
implementation **MUST** keep a `voters: {identity: choice}` map **and** an `operations: {idempotency_key:
result}` replay ledger, so re-submitting toggles or replays deterministically.
*Dropped:* counts become click-counts, inflatable by one motivated person, and unpublishable. This is the
invariant §1 exists to protect.

**M7 — Only positive reactions score. Negative reactions are named channels and NEVER subtract.**
Negative sentiment is not censored — it is *routed*, into `did_not_work` / `stuck` / `too_long` / `disagree`.
*Why:* it also means "downvote" can be implemented as *withdraw your own endorsement*, so no negative
primitive exists to abuse.
*Dropped:* the score becomes a brigading target, can go negative, and stops being publishable.

**M8 — One reaction ↔ one channel, per surface; unmapped is better than meaningless.** Pinned by a test.
*Dropped:* two channels sharing an emoji are permanently indistinguishable — unrecoverable at any cost.

**M9 — One object per metric. Never conflate.** Top post = endorsement; tally comment = acquisition; poll
comment = experience; review comment = reviewer feedback. Four distinct platform subject ids, four fields.
*Dropped:* one number that means four things and defends none of them.

**M10 — `conversation` counts every human comment in the thread — top-level comments AND threaded replies —
minus the machinery actually present. Computed from what is there, never from a constant.**
```python
conversation = (comments.totalCount + Σ over comments of replies.totalCount)
             - (count of comments AND replies that are machinery under M40)
```
Two facts make the formula this shape, and both bite:

1. **Replies live on a separate connection.** `discussion.comments.totalCount` counts **top-level** comments
   only; a reply to a comment is returned on that comment's own `replies` connection. A formula built on
   `comments.totalCount` alone therefore **cannot see a human replying to a machine review** — the single most
   valuable half-two signal this spec defines (§1.2, §1.5, L5, M36, item 8). The collector's query **MUST**
   request replies:
   ```graphql
   comments(first: N) {
     totalCount
     nodes {
       id body viewerDidAuthor author { login }
       reactionGroups { content reactors(first: 100) { totalCount nodes { __typename } } }
       replies(first: M) {
         totalCount
         nodes { id body viewerDidAuthor author { login } }
       }
     }
   }
   ```
   Replies are subject to M40 exactly like top-level comments: a machine reply that is marker-anchored and
   collector-authored is machinery and is subtracted; every other reply is a human reply and counts.
2. **Machinery is identified by M40, not by substring.** Counting *comments that are machinery*, rather than
   *markers found*, is what keeps the number honest when a surface is ever provisioned twice: both copies are
   excluded from the human total instead of one being counted as conversation. rapp-vision states exactly this
   property in `machinery_comment_count()`, and routes it through the same predicate its writer uses, *"so a
   marker can never mean one thing to the counter and another to the writer."*

*Dropped, in two directions at once:* every subject shows "2 comments" on day zero — a fabricated conversation,
your own robots as your engagement number — **and** a lively human argument under a machine review is deleted
from the record because of what it was attached to (§1.3).

**M11 — Two counts of different populations are NEVER summed.** Signed-in tally reactions and server-side
release-download counts measure different things by different methods; adding them produces a number neither
system can defend. Aggregated third-party signal **MUST** be kept in its own field for the same reason.
*Dropped:* a headline number that no component can explain when questioned.

**M12 — Counts accumulate; uniques do not. Publish both and label them.** Publish the platform's authoritative
uniques figure *and*, if you also sum daily uniques, label that sum explicitly as an **upper bound** — any
actor active on more than one day is counted twice.
*Dropped:* an over-count presented as a headcount.

**M13 — Self-generated traffic is estimated and subtracted, and the estimate is published beside the raw
total.** Every CI checkout counts as a clone. RAR uses the minimum daily clone count over the window as a
floor on the CI baseline and publishes both `ci_clone_estimate` and `clones_excluding_ci_estimate` next to the
raw figure. (Live values in RAR's `state/metrics.json`: 1,792 of 2,743 clones estimated as CI, leaving 951.)
*Dropped:* your headline growth number is mostly your own robots. This is M32 at repository scale.

**M14 — Stale subject keys are dropped from totals AND the drop count is published.**
*Dropped:* renamed or removed subjects quietly inflate the public tally and nobody can tell it happened.

*(M37–M40 were numbered after M36 but belong to Counting, so they are stated here with their topic rather
than appended to the end of §9. Nothing before them was renumbered.)*

**M37 — Marker lookup MUST be exhaustive.** The collector **MUST** paginate the comment connection — and each
comment's `replies` connection — until every marker declared in the surface registry has been located or the
connection is exhausted. A provisioner **MUST NOT** create a surface comment on the basis of a partial page.
*Why:* a single-page read is correct only until a thread outgrows the page, and it fails on the busiest
subjects first — the ones most likely to be shown to somebody. Once the machinery comments fall out of view,
**two** failures fire together: machinery stops being subtracted, so bot comments become engagement (M10's
exact stated failure), **and** the "idempotent" provisioner sees no marker and adds a *second* surface comment,
splitting one tally across two objects so the acquisition number silently drops while the thread gets busier.
*Dropped:* the metric degrades in proportion to the subject's success, which is the worst possible direction,
and both symptoms read as ordinary numbers.
*Grounded:* RAR requests `comments(first: 25)` for counting **and** for provisioning
(`scripts/discussion_ratings.py:160`, `:200`) with no `pageInfo` and no cursor loop on that connection.
rapp-vision requests `comments(first: 100)` one page deep and states the consequence in its KNOWN LIMITS
block rather than leaving it to be discovered. Neither paginates comments; §14 records it for both.

**M38 — Reactors MUST be classified, and only human actors are counted.** A raw `reactors { totalCount }` is a
count of *accounts*, not of people. The collector **MUST** read the reactor list and drop every reactor the
platform does not declare to be a person:
```graphql
reactionGroups { content reactors(first: 100) { totalCount nodes { __typename } pageInfo { hasNextPage endCursor } } }
```
Every reactor whose `__typename` is not `User` — `Bot`, `Organization`, `Mannequin` — **MUST** be excluded
before the counter is taken, and the `reactors` connection **MUST** be paginated to exhaustion, because a
partial page silently reverts the counter to `totalCount` semantics with no visible symptom.
*Why:* this is the only mechanism in the protocol that can *check* half one. L2 and M32 forbid an automated
actor from reacting, but a forbidden write is not a prevented write: the threads are public and the write path
is deliberately any-credential (C-W1), so a third-party bot account or App installation can react on the top
post, the tally, the poll, and the review comment, and without M38 every one of those lands in `endorsements`,
`tallies`, `signals`, and `reviewer_feedback` indistinguishably.
*Cost, and the honest failure:* classification multiplies query cost by the reactor pages. A group whose
`totalCount` is `0` needs no page fetch. Where the reactor list **cannot** be paginated to exhaustion within
budget, the counter **MUST** be published as `null` (F7, M20) — never as the unclassified `totalCount`, which
would be an unverified number wearing a verified number's clothes.
*Residual, per §1.1:* a human-operated PAT driven by a script, a machine posting through a human account, and
a stolen credential (C-W5) all present as `User`. M38 delivers "no *declared* machine actor", not "no machine
actor", and `counting_rules` **MUST NOT** claim more (M29).
*Dropped:* half one is an assertion the implementation cannot check, and §1.1's "one bot upvote makes every
number a lie" becomes a statement about a failure mode nobody would ever detect.
*Status:* **neither reference implementation can detect one.** Both read only `reactors { totalCount }` —
RAR `scripts/discussion_ratings.py:165`, `:168`, `:277`, `:310`, `:321`; rapp-vision's query and all four of
its reaction readers do the same, and the string `__typename` does not appear in either file.

**M39 — No counter is a sum of two or more reaction contents on the same object.** Per-user dedup is *per
emoji*: the platform stores one reactor set per *(object, content)* pair, so a person leaving 👍 and ❤️ is in
both sets. Summing the sets counts that person twice. Such a counter is a **click-count** — the exact thing M6
exists to prevent — and it inflates without any second person, at no cost, using a feature of the UI.
*Concretely:* an `endorsements` figure computed as `THUMBS_UP + HEART + HOORAY + ROCKET + LAUGH` reads **5**
for one enthusiastic person and **1** for five people who each left a plain 👍. The number is not comparable
even to itself.
*Dropped:* the headline human counter is inflatable by one motivated individual, and every
`counting_rules` line saying "counts are people, not clicks" is false in the file that publishes it.
*Live counter-example:* RAR's `positive_score()` is exactly that five-content sum
(`POSITIVE_REACTIONS = {THUMBS_UP, HEART, HOORAY, ROCKET, LAUGH}` at `scripts/discussion_ratings.py:78-80`,
summed at `:272-278`) and its result is published as `upvotes` at `:343`. rapp-vision's `positive_score()`
carries the same five-content set and publishes the same `upvotes`. **Neither `upvotes` is a conforming
`endorsements` value.** §14, RAR Gap 5.

**M40 — Marker recognition is anchored AND author-bound.** A comment or reply counts as machinery only when
**both** hold:
**(a)** the marker is the **first non-whitespace token** of the body, and
**(b)** the comment was written by the **collector identity** — proved by `viewerDidAuthor` (the token reading
the thread is the token that wrote it) or by `author.login` being a member of the `collector_logins` set
published in the snapshot (§8.1).
Both checks are REQUIRED, and they fail in **opposite** directions — which is why neither alone is enough:
*Why (a):* GitHub's **Quote reply** copies the raw body, invisible HTML comment included. Under substring
matching, a human quote-replying to a tally, poll, or review comment carries the marker and is **subtracted
from `conversation`** — a genuine human action discarded because of what it was attached to, which is the §1.3
error, and one that lands hardest on exactly the threads where people are engaging.
*Why (b):* a substring test says nothing about **who wrote it**. Any automated actor that comments *without* a
marker — a third-party App, an agent that never read this spec, a webhook — is counted as human `conversation`.
L5 is a MUST on that machine, and a machine that never agreed to L5 is not constrained by it; the author check
excludes it whether it cooperates or not. A marker is a **routing label, never proof of authorship**.
*Unattributable comments fall to the human side:* a deleted account returns `author: null`. Counting it as
conversation costs at most one machinery comment miscounted; the other default lets any stranger delete
themselves from a thread's human count, or mint counters, by pasting an invisible string.
*Residual, named like §1.1's:* **M40 checks ownership, not provenance.** On GitHub Actions every workflow in a
repository runs as the same `github-actions[bot]`, so any workflow in that repo can write a comment the
collector will accept as its own surface. M40 stops arbitrary users; it does not stop a hostile or careless
workflow sharing the collector's identity. Closing that would need a signature over the body, which this
protocol does not define. rapp-vision records the same limit in its own KNOWN LIMITS block —
*"Ownership is checked, PROVENANCE IS NOT."*
*Identity-rotation hazard (SHOULD):* because `viewerDidAuthor` is evaluated by the token doing the read, a
collector that swaps tokens stops recognising the comments its predecessor wrote and provisions a duplicate
beside each one. A publisher rotating the collector identity **SHOULD** add the old login to
`collector_logins` **before** the switch, not after.
*Dropped:* `conversation` simultaneously loses real human replies and gains machine ones, in the same file,
with nothing in the output to tell which happened.
*Grounded:* rapp-vision already implements exactly this — `is_machinery_comment()` requires
`body.startswith(marker)` **and** `machinery_authored()` (`viewerDidAuthor`, or an env-overridable author
allowlist defaulting to `github-actions[bot]`), and both `marker_comment_of()` and `machinery_comment_count()`
route through that one predicate. RAR does not: `marker_comment_of()` is
`if marker in (c.get("body") or "")` at `scripts/discussion_ratings.py:284`, and its discussion query requests
no author field at all (`:155-170`). §14, RAR Gap 6.

### Provisioning

**M15 — Signal surfaces are provisioned over the API, never by hand.** §7.1.
*Dropped:* the surface exists only on whatever subjects somebody remembered, and coverage silently rots as the
catalog grows.

**M16 — Surfaces are a data registry with idempotent per-marker back-fill.** Adding a surface is a one-entry
change; the next scheduled runs back-fill the whole subject set. New subjects get the full surface at creation.
*Dropped:* every new signal type becomes a migration script.

**M17 — Writes are capped per run, spaced, and STOP rather than fail.** On the first write error the
provisioner **MUST** break, report "N still missing", and exit 0; the next scheduled run resumes.
*Dropped:* a bulk import trips secondary rate limits, and a hard failure either loses the run or retries the
same head of the queue forever.

### Failure posture

**M18 — Collection is non-fatal end to end, and strictness is the CALLER's choice.** Missing token, network
error, GraphQL error, missing category → warn, leave the snapshot unchanged, exit 0. A collector that is the
*whole* job **MUST** offer a `--strict` mode that exits non-zero, and strict **MUST** refuse **before**
writing.
*Why:* when a collector is one of six steps, a swallowed failure costs one metric; when it is the only step, a
swallowed 404 is indistinguishable from a quiet week — green run, catalog silently ageing.
*Dropped:* one 404 in a six-step workflow costs you the other five steps' signal. Some of that loss is
permanent: GitHub's traffic API is a 14-day rolling window, so a read missed for 14 days is gone forever.

**M19 — Never clobber a non-empty snapshot with an empty one.** `persist()` **MUST** refuse to write an empty
result when a snapshot already exists.
*Dropped:* one bad fetch permanently erases counts you cannot recompute, because the source of truth is remote
and mutable.

**M20 — "Never wired" is not "zero", in the file AND on the screen.** A counter that has never been wired
**MUST NOT** be written as `0`, and an unknown value **MUST** render as an em-dash or be omitted — never as
`0`.
*Why, verbatim from the reference implementation's docs:* *"'No release has been cut yet' and 'nobody
downloaded this' are different claims. Printing 0 for the first asserts the second, and it is the kind of
number that ends up on a slide."*

**M21 — A broken metric MUST NOT be indistinguishable from an honest empty state.**
This is the worst bug on record in the reference implementation: `critic_reviews.json` keyed its map with an
underscore-normalized name while each record's `name` field held the real dashed one, so lookup-by-key
resolved nothing for every dashed publisher and every card read "not yet scored" while real scores existed.
*Corollary (REQUIRED):* any join key writable two ways gets **one named normalizer that the shipped code
calls** — never re-derived inside a test.
*Second corollary (REQUIRED):* a test that re-implements the logic it checks **cannot fail** and is worse than
no test, because documentation citing it becomes false assurance. Verify every new test by reintroducing the
bug and confirming it goes red.

**M22 — Freshness beats staleness, but only when the read actually succeeded.** The discriminator **MUST** be
*did this source answer*, never *is the value falsy*: `x if source_answered else last_known`, not
`x or last_known`.
*Dropped:* real zeros get papered over by yesterday's numbers — a lie in the direction that flatters you.

### The snapshot as a file

**M23 — No timestamps. Identical counts MUST produce identical bytes, so the git history IS the time series.**
A no-op day produces no commit, and the log becomes a readable record of when each number actually moved.
*Dropped, with a live counter-example in the same repository:* RAR's `state/metrics.json` carries
`"generated_at": now_iso()` and its history merge appends a snapshot entry every run, so
`metrics.yml`'s `git diff --staged --quiet` no-op guard **can never fire** — that pipeline commits daily
whether or not anything changed, and its history is unreadable as a time series. The invariant is
load-bearing, not stylistic.

**M24 — Rolling-window sources are accumulated into a date-keyed ledger merged with `max()`, not `+`.**
*Why:* overlapping re-reads become idempotent, and a 14-day window becomes an all-time total.
*Dropped:* either you lose everything older than the window, or you double-count the overlap.

### Write-back and consumption

**M25 — Write-back is idempotent and preserves human text.** A report card spliced between start/end markers;
everything outside survives; the rendered block is compared before mutating, so a quiet day costs zero writes.
A start marker with a **missing end marker MUST still replace**, not append.
*Dropped:* blocks accumulate on every daily run, forever, and human edits get clobbered.

**M26 — Per-subject and portfolio views render from the SAME snapshot.**
*Why, verbatim:* *"the two can never disagree. Nobody types a field: if a number has to be typed, it will be
wrong by the next quarter."*

**M27 — The metric MUST NEVER block the thing being measured.** Tracking is a silent no-op when signed out;
every client-side tracking failure is swallowed; the download/playback proceeds regardless.
*Dropped:* you have converted a metric into an outage.

**M28 — Optimistic local mirror, snapshot authoritative.** The click may update a local mirror so it feels
instant; the daily snapshot is what everyone else sees. The mirror **MUST NOT** be written into any file the
user can export as their own data (§11).

**M29 — Counting rules are published in prose beside the number.** `counting_rules` is REQUIRED and non-empty,
and **SHOULD** state at minimum: that counts are people not events; that no automated actor ever reacts; that
machine-authored subjects earn ordinary counts; that self-reactions count, so seeded data is indistinguishable
from organic; that reacting is publicly attributable on GitHub; and, for any count that is a floor rather than
a total, that it is a floor and what it excludes.
*Dropped:* every number gets read as the most flattering thing it could mean.

### The founding tenet, as invariants

**M30 — Editorial output NEVER enters a human counter.** No machine-written score, verdict, or review text
appears in the metrics document, and no editorial value is summed into `endorsements`, `conversation`,
`tallies`, `signals`, `rank`, `reviewer_feedback`, or any `totals` figure. §10.
*Dropped:* your robots become your engagement numbers, and every number in the file needs a footnote nobody
will read.

**M31 — The ACTOR determines the lane, never the subject.** No code path that computes a human counter may
read the authorship of the subject.
*Test:* build the snapshot twice from fixtures identical except for an authorship field; the bytes **MUST**
match.
*Dropped:* the protocol acquires a second, undocumented axis of classification, and no published number can be
explained without knowing which axis produced it.

**M32 — No automated actor may write to a human counter.** No bot account, service account, app installation,
CI token, scheduled workflow, or agent may add a reaction to any thread, tally, poll, or review surface. The
collector's write-capable token is for thread creation, surface provisioning, editorial writes, and report-card
splicing — nothing else. A conforming implementation **SHOULD** make the violation *impossible* rather than
merely unlikely (refuse to react when `CI` / `GITHUB_ACTIONS` is set; or ship no reaction-writing code path in
the collector at all, which is what rapp-vision does).
*Dropped:* one bot upvote makes every number the protocol publishes a lie, retroactively and unrecoverably.

**M33 — A human action counts in full, whatever it was performed on.** Reactions on machine-provisioned
surfaces, replies to machine-written comments, and endorsements of machine-authored subjects are ordinary human
signal at full weight. *Verbatim from the ruling:* if a human upvotes an agent-generated video, **that is 200
real people if 200 people did it.**
*Dropped:* you have quarantined by subject (§1.3) — the opposite error — and the content your surface produces
at scale becomes the only content that can never demonstrate traction.

**M34 — Machine-authored subjects are first-class.** No counter, badge, ranking, or rendering may be
suppressed, discounted, footnoted, or moved to a separate bin because the subject was machine-generated.
*Dropped:* the metric silently becomes an editorial judgement about provenance, and the numbers stop being
comparable across the catalog.

**M35 — Where an editorial surface exists, human reactions to it MUST be collected and published as
`reviewer_feedback`,** keyed by `reviewer_id`, in the human document, and summed into nothing else.
*Why:* it is the community rating the reviewer. Sustained negative human signal on an agent's reviews means
the rubric is wrong, and that is the loop most worth having.
*Dropped:* you have thrown away genuine human engagement because a machine wrote the thing it was about (§1.3),
and a bad rubric can run for a year with nobody able to point at evidence.

**M36 — Machine-written comments are marked and excluded from `conversation`; human replies to them are
included.** Both halves of this are required, and they are the same rule applied to two different actors.
*Dropped:* either bot comments inflate your conversation count (M10), or a lively human argument under a
machine review is deleted from the record because of what it is attached to.

---

## 10. The editorial lane — a consequence of §1, not a primitive

The editorial lane is **not** a category of content. It is what §1.1 requires you to do with **machine-authored
actions**: keep them out of the human counters by putting them somewhere structurally separate. Everything in
this section derives from that, and nothing in it applies to a machine-authored *subject*.

Automated reviewers — LLM critics, rubric scorers, agent panels — are legitimate and valuable. They are also
the fastest way to turn every number this protocol publishes into a lie, because a machine can manufacture
unlimited "signal" that is structurally identical to a person's. So they get a **first-class lane with a hard
wall around it**, and — by §1.2 — the humans who react to their output get counted like any other humans.

### 10.1 Structural separation is REQUIRED

- **E1.** Editorial output **MUST** be published in a **separate document** with its own schema string,
  `rapp-metrics-editorial/1.0` (`state/editorial.json` RECOMMENDED). It **MUST NOT** appear inside the
  `subjects` map of the `rapp-metrics/1.0` document, and it **MUST NOT** appear anywhere else in that document.
- **E2.** *Why a separate file and not a nested block:* a consumer that does
  `Object.values(snapshot.subjects).reduce(...)` must be **structurally incapable** of picking up machine
  scores. Separation by file makes conflation an explicit act, not an accident. It also isolates editorial
  churn — editorial re-runs frequently and its records legitimately change without any human number moving,
  which would otherwise dirty the counters file every day and destroy M23.
- **E3.** No field of the editorial document **MAY** be summed into `endorsements`, `conversation`, `tallies`,
  `signals`, `rank`, `reviewer_feedback`, or any `totals` figure in the metrics document, under any
  circumstances.
- **E4.** Both reference implementations already do this in prose, and 1.0 promotes it to a structural rule:
  RAR reports engine-generated curator reviews in their own block noted *"Reported for transparency; NOT
  counted in the review totals or the review leaderboards"* (live: `curator_reviews = 420` alongside
  `reviews = 0`); rapp-vision's collector constant reads *"Machine-written from the channel record by a
  deterministic rubric. Never counted in any human total, ranking, or leaderboard."*

### 10.2 Editorial document shape

```jsonc
{
  "schema": "rapp-metrics-editorial/1.0",     // REQUIRED
  "profile": "rar-critics/1.0",               // REQUIRED
  "rubric_version": "3",                      // REQUIRED. bump on ANY rubric change
  "authorship": "machine",                    // REQUIRED, literal. there is no other legal value
  "not_counted_in": "rapp-metrics/1.0 subjects",  // REQUIRED, literal. self-documenting wall
  "feedback_in": "state/metrics.json#reviewer_feedback",  // REQUIRED when a review surface exists
  "reviewers": [                              // REQUIRED. the roster, with lenses and models
    { "id": "architect", "name": "The Architect",
      "lens": "structure, separation of concerns, single-file discipline",
      "model": "openai/gpt-4.1" },
    { "id": "sentinel",  "name": "Security Sentinel",
      "lens": "secret handling, input trust, blast radius, failure modes",
      "model": "openai/gpt-4.1" }
  ],
  "scale": { "min": 0, "max": 100, "fresh_at": 60 },   // REQUIRED
  "subjects": {
    "@rapp/basic_agent": {
      "reviewed_digest": "db3bf0e8…",         // REQUIRED when the subject has bytes. pins the review
      "score": 71,                            // OPTIONAL aggregate over reviews[]
      "state": "fresh",                       // OPTIONAL profile-defined verdict
      "reviews": [
        { "reviewer_id": "architect", "score": 74, "backend": "model",
          "headline": "Holds up at 644 lines",
          "text": "…one paragraph…" },
        { "reviewer_id": "sentinel",  "score": 59, "backend": "rubric",
          "headline": "Undeclared environment reads",
          "text": "…one paragraph…" }
      ]
    }
  }
}
```

- **E5.** Every review **MUST** carry `reviewer_id`, and every `reviewer_id` **MUST** resolve to an entry in
  `reviewers`. An unattributed machine opinion is not publishable — and without a stable `reviewer_id` there is
  nothing for `reviewer_feedback` to key on, so §1.5 becomes impossible.
  **The same id space spans both documents.** The `reviewer_id` declared on a `review` surface (S9) is a
  `reviewers` roster id, and it is the key `reviewer_feedback` uses in the human document. One id, three
  places: the surface that collects the reactions, the roster that says who the reviewer is, and the counter
  that publishes what people thought of them. A rubric string, a profile string, or a model name is **NOT** a
  `reviewer_id` unless it is also a roster entry — and a `reviewer_id` **MUST NOT** embed `rubric_version`,
  because E7 will move that string and the feedback keyed under the old one would be orphaned (S9).
  A roster of N reviewers whose feedback is published separately therefore requires N declared `review`
  surfaces; a panel that emits one combined comment declares one surface and one synthetic roster entry.
- **E6.** Every review **MUST** be pinned to what it read: `reviewed_digest` when the subject has bytes,
  otherwise the profile **MUST** define an equivalent version pin. A review of "the agent" is meaningless; a
  review of *this sha256* is a fact.
- **E7.** `rubric_version` **MUST** change whenever the rubric, the panel, or the scale changes, so scores
  from different regimes are never silently averaged together — and so `reviewer_feedback` can be read against
  the regime it was actually reacting to.
- **E8.** `backend` **SHOULD** be recorded per review (`model`, `rubric`, `human-in-the-loop`), and a
  deterministic fallback rubric **SHOULD** exist so the panel always returns a verdict rather than leaving a
  subject silently unscored — an unscored subject and a badly-scored one must not look the same (M21).
- **E9.** The editorial document **MAY** carry a `generated_at`, because it is a separate file whose churn
  cannot dirty the counters. It **SHOULD** still avoid one, for the same reason M23 gives.

### 10.3 Rendering, writing, and the bot rule

- **E10.** Every render site **MUST** label an editorial number as machine-authored, with the reviewer id
  visible or one interaction away. A machine score rendered in the same visual treatment as a human count is
  a misrepresentation regardless of what the JSON says. rapp-vision prints the disclaimer verbatim: *"Written
  by a model, not by a person. It is not counted in any number above."*
- **E11.** The **subject's own** counters **MUST NOT** be labelled, dimmed, asterisked, or otherwise
  editorialised because the subject is machine-authored (M34). E10 labels the *reviewer's* output; it says
  nothing about the subject's numbers.
- **E12.** The collector's write-capable token **MUST NOT** be used to call `addReaction` on any surface
  (M32). It **MAY** create threads, provision surface comments, write editorial comments, and splice report
  cards.
  > *Conformance hazard, verified:* RAR's `scripts/discussion_ratings.py` contains an `addReaction` mutation
  > (line 185) behind a `track` subcommand. In the browser (`store.html`) the token is the **viewer's own**,
  > which is conformant, and `refresh-ratings.yml` runs `seed`, `tally`, `fetch` only — so RAR is conformant in
  > practice. It is not conformant *by construction*: nothing prevents a future workflow from calling `track`.
  > rapp-vision's collector shows the stronger form — `scripts/rapp_metrics.py` contains **no `addReaction`
  > mutation at all**, and its workflow records the property in a comment beside the editorial step
  > (`.github/workflows/metrics.yml:324`: *"…and this command adds no reaction anywhere"*).
- **E13.** If an automated reviewer's assessment should be *visible* on the thread, it **MUST** be posted as a
  comment or spliced into the report card as text — never as a reaction. That comment **MUST** carry a marker
  so it is excluded from `conversation` (L5, M36), and it **SHOULD** be a declared `review` surface so the
  human reactions it attracts are collected as `reviewer_feedback` rather than discarded (S7, M35).
- **E14.** An editorial comment body **SHOULD** be byte-stable for an unchanged review, so re-running the
  editorial pass costs zero writes (the same discipline as M25). rapp-vision's `render_editorial()` documents
  exactly this property.

---

## 11. The client contract

### 11.1 Reading

- **C-R1.** Fetch the snapshot with `try/catch` (or equivalent), default to a **neutral empty value**, and
  never throw into render. A missing snapshot **MUST** degrade to *no badges*, never to a broken page and
  never to zeros.
- **C-R2.** The metrics fetch **MUST NOT** be awaited on the page's critical boot path. Patch the UI when the
  snapshot lands. *(Concrete hazard in rapp-vision: `route()` at `index.html:1042` runs only after
  `await Promise.allSettled(...)` at `:1030`; adding a metrics fetch into that awaited chain lets a slow
  metrics host delay first paint of the entire player.)*
- **C-R3.** Validate **per record**, not per file. One malformed subject entry drops that entry; it does not
  discard the snapshot.
- **C-R4.** Every rendered value from the snapshot **MUST** be escaped, every numeric value interpolated into
  markup or a style attribute **MUST** be coerced to a number, and every URL **MUST** be scheme-checked
  (`http:` / `https:` only) before it reaches an `href`. The snapshot is untrusted input — anyone can fork the
  repo, open a PR against the file, or point a page at their own copy.
- **C-R5.** The snapshot **MUST NOT** be stored in the same structure as the user's own local state if that
  structure is serialized on a hot path or exported as "your data". *(Concrete hazard in rapp-vision:
  `save()` at `index.html:227` serializes the whole `state` object on every playback tick, and Export at
  `:803` spreads `...state` into the user's downloadable library file — a snapshot parked there becomes both
  a storage-bloat vector and fake personal data in the export. Use a module-level variable, or a separate
  localStorage key.)*
- **C-R6.** Per-subject and portfolio views **MUST** read the same snapshot (M26).
- **C-R7.** A machine review and a human count **MUST NOT** share a visual treatment (E10), and a
  machine-authored subject's counts **MUST** be rendered exactly like any other subject's (E11, M34).

### 11.2 Writing

- **C-W1.** All writes go **directly from the browser to the platform API with the viewer's own credential**.
  There is no server in this protocol, and the adopter **MUST NOT** add one to proxy writes. A proxy would
  also destroy the actor attribution §1 depends on: every write would arrive as the proxy.
- **C-W2.** A write **MUST** be triggered by an explicit user action. No implicit, ambient, or
  playback-derived writes. An inferred "view" is not an actor.
- **C-W3.** The client **MUST** check the viewer's existing reaction state (`viewerHasReacted`) before adding,
  and **MUST** implement "undo" as `removeReaction` on the viewer's own reaction — never as a negative
  counter.
- **C-W4.** Every write failure **MUST** be swallowed and **MUST NOT** interrupt the action being measured
  (M27).
- **C-W5.** A credential **MUST NOT** be placed anywhere a third-party framed document could read it.
  *(Concrete hazard in rapp-vision: framed live-replay apps run with
  `sandbox="allow-scripts allow-same-origin allow-pointer-lock"` and are same-origin with the player, so any
  framed app can read `parent.localStorage`. A write token in `localStorage` there is readable by every app
  any channel scripts — and a stolen token is an automated actor with a human's identity, the one failure M32
  cannot detect after the fact.)*

---

## 12. Privacy

rapp-metrics is **public by design and aggregate by construction**. It is a review surface, not telemetry, and
the difference is that the person chooses to leave the signal and can withdraw it.

- **PR1.** The snapshot **MUST** contain aggregate counts only. It **MUST NOT** contain usernames, logins,
  display names, avatars, emails, user ids, IP-derived data, or any other per-person identifier — even though
  the platform API returns reactor identities to the collector.
- **PR2.** The snapshot **MUST NOT** contain per-person, per-session, or per-device event records. There are
  no events in this protocol; there are only standing counters.
- **PR3.** No cookie, no fingerprint, no identifier, and no session is created by reading the snapshot. The
  read is a plain `GET` of a public file and transmits nothing about the reader.
- **PR4.** Any surface using this protocol **MUST** state plainly, at the point of interaction, that
  **reacting associates the person's platform identity with that subject publicly on the platform.** The
  counts are anonymous; **the act is not.** Claiming anonymity would be false.
- **PR5.** Withdrawal **MUST** be available and **MUST** be honest: removing the reaction removes the person
  from the count at the next collection, with no residue in the snapshot.
- **PR6.** No PII enters the snapshot from the subject side either — a subject's `title` and `url` are
  published artifacts, never customer names, internal identifiers, or private paths.
- **PR7.** The collector's token grants write access. It **MUST** live only in the CI secret store, **MUST
  NOT** be embedded in any published page or snapshot, and **MUST NOT** be placed in browser storage (C-W5).
- **PR8.** `reviewer_feedback` is aggregate like everything else: it names the **reviewer** (a machine, by
  `reviewer_id`), never the people who reacted to it.
- **PR9. M38 requires the collector to read the reactor list, and that read is bounded here.** Classifying an
  actor means opening a connection that can return who reacted, so the privacy rule cannot stop at the output
  file:
  - The query **MUST** request `__typename` **only** on `reactors.nodes`. `login`, `name`, `avatarUrl`, `id`,
    and `databaseId` **MUST NOT** be requested. `__typename` alone answers the only question M38 asks — *is
    this reactor a person or a declared machine* — so no reactor identity needs to enter the process at all.
  - Where an identity is nonetheless unavoidable — M40's author check needs `author { login }` on **comments**,
    not on reactors — it **MUST** be compared and discarded in the same pass. Nothing derived from it beyond
    the machinery/human decision may be retained, logged, cached, or written to any file.
  - PR1 already forbids these values in the snapshot; PR9 forbids them everywhere else the collector could put
    them, including its logs and its intermediate state. The one identity that may be published is
    `collector_logins`, which names automated actors, not people (F6, F12).
  - *Why this is stated as a rule and not left to good sense:* M38 is the one place this protocol asks an
    implementer to look at who did something. A collector that fetches logins "since we're already paginating"
    has quietly built the per-person event store §12 exists to say does not exist.

---

## 13. Conformance checklist

An implementation is **rapp-metrics/1.0 conformant** if every numbered item holds. Each is stated so it can be
turned into a test. **Items 1–11 and 63–67 are §1**; failing any one of them is disqualifying no matter how
clean the rest is. (63–67 are numbered last but are tenet items: they are the ones that make half one
*checkable* instead of merely declared. See §1.1.)

**The founding tenet — half one (no automated actor in a human counter)**
1. No workflow, service account, app installation, or CI token adds a reaction to any thread, tally, poll, or
   review surface. *(L2, M32)* — **Test:** parse every workflow file and assert no step invokes a
   reaction-writing subcommand; better, assert the collector module contains no reaction mutation at all.
2. The collector's write-capable token is used only for thread creation, surface provisioning, editorial
   writes, and report-card splicing. *(E12, M32)*
3. Any reaction-writing code path that does exist refuses to run when `CI` / `GITHUB_ACTIONS` is set. *(M32)*
4. Seeding a thread produces no counts: a freshly created thread reads `endorsements: 0` and empty surfaces.
   *(T7)*
5. Machine-written comments carry a marker and are excluded from `conversation`, counted from the comments
   **and replies** actually present rather than from a constant. *(M10, M36, M40)* — **Test, three fixtures
   that must all pass together:**
   **(a)** a node with 2 collector-authored marker comments and 3 top-level human comments yields
   `conversation == 3`;
   **(b)** the same node with **1 human reply nested under one of the marker comments** yields
   `conversation == 4` — this is the case a `comments.totalCount`-only formula cannot see, so it is the one
   that proves the `replies` connection is actually requested;
   **(c)** the same node plus **1 human comment that quotes a marker comment** (marker present in the body but
   not first, author is not in `collector_logins`) yields `conversation == 5` — a quote-reply is a human
   comment and MUST NOT be subtracted.
   Verify (b) by deleting the `replies` request from the query and (c) by relaxing M40 to substring matching;
   each MUST turn its fixture red (M21 corollary).

**The founding tenet — half two (a human at the bot layer always counts)**
6. No code path computing a human counter reads the subject's authorship or provenance. *(L1, F9, M31)* —
   **Test:** build the snapshot from two fixtures differing **only** in an authorship field; assert the output
   bytes are identical.
7. Human reactions on machine-provisioned surfaces are counted at full weight, and human reactions on a
   **machine-authored subject's** surfaces are counted at full weight. *(L3, M33, M34)* — **Test:** a
   machine-authored subject with 200 endorsements publishes `200`, with no flag, discount, or separate bin.
8. Human replies **to** a machine-written comment are counted in `conversation`. This requires the collector to
   request each comment's `replies` connection: on GitHub, `comments.totalCount` counts top-level comments
   only, so a formula built on it alone is structurally incapable of seeing the reply. *(L5, M10, M36)* —
   **Test:** fixture 5(b); removing `replies` from the query MUST turn it red.
9. Where a `review` surface exists, human reactions on it are collected into `reviewer_feedback`, keyed by the
   `reviewer_id` **declared on that surface** (S9), and that id resolves to an entry in the editorial roster
   (E5). *(S7, S9, M35)* — **Test:** a fixture review comment with 5 `THUMBS_DOWN` yields
   `reviewer_feedback.<reviewer_id>.disagree == 5`; assert the same fixture leaves `endorsements`, `tallies`,
   `signals`, and `rank` unchanged; assert every key of `reviewer_feedback` is present in the editorial
   document's `reviewers` roster. A two-reviewer panel MUST declare two `review` surfaces, or one surface with
   a synthetic panel `reviewer_id` that is itself a roster entry — a key that cannot be derived from the
   declared surfaces is a failure of this item.
10. `reviewer_feedback` is rendered somewhere a human can see it, attributed to the reviewer. *(M35, §1.5)*
11. No rendering dims, asterisks, or footnotes a subject's counts because the subject is machine-authored;
    editorial *output* is always labelled machine-authored. *(E10, E11, C-R7, M34)*

**Provider**
12. `enumerate()` returns every subject or raises; it never returns a partial list. *(P1, P3)*
13. `enumerate()` is deterministic in content and order for a fixed repository state. *(P2)*
14. `enumerate()` reads no metrics state and does not branch on authorship. *(P4, P5)*
15. Every `subject_id` matches the published anchored pattern, and the pattern rejects an ordinary
    human-written title. *(I4)*
16. `subject_id` is globally unique across the surface; where the natural id is only locally unique it is
    namespace-qualified. *(I1)*
17. An append-only ledger of published `subject_id`s exists and a CI job **blocks merges** on rename, move, or
    deletion. *(I3, M5)*
18. Exactly one named normalizer exists for any key that can be written two ways, it lives in shipped code
    called by both writer and reader, and no test re-implements it. *(I6, M21)*

**Threads**
19. Exactly one thread per subject; its title is exactly the `subject_id`. *(M1)*
20. Threads live in a category ordinary users cannot post in, and the collector filters on it. *(M2)*
21. A node counts only if it passes **both** the shape check and subject-set membership. *(M3)*
22. Duplicate threads resolve to the lowest number, deterministically. *(M4)*
23. Thread creation is idempotent and capped per run. *(T5, M17)*
24. A newly created thread receives the full surface set in the same pass. *(T6)*

**Surfaces**
25. Every surface is declared in a data registry; adding one is a single entry, back-filled idempotently
    per-marker by the existing provisioner. *(M16)*
26. Every surface's marker and reaction map are published in the snapshot — **including the `endorsement`
    surface's `object` and single `reaction`**, and every `review` surface's `reviewer_id`. A reader can learn
    what the headline number counts without opening the collector's source. *(S1, S8, S9, R4)*
27. No two channels within a surface share a reaction, and no surface exceeds eight channels — pinned by a
    test. *(R2, M8)*
28. An absent surface reads as all-zeros of the correct shape. *(S5)*
29. Provisioning stops on the first write error, reports how many remain, and exits 0. *(M17)*

**Counting**
30. Only positive reactions contribute to endorsement; negatives — including `disagree` — are named channels
    and never subtract. *(M7, R5, R6)*
31. Counts from different populations or methods are never summed anywhere in the pipeline or the UI. *(M11)*
32. Where uniques are published, the authoritative figure and any summed figure are both present and the
    summed one is labelled an upper bound. *(M12)*
33. Where self-generated traffic exists, an estimate is subtracted and **published** alongside the raw
    total. *(M13)*
34. Dropped/orphaned subject keys are excluded from totals and their count is published. *(M14)*

**Failure posture**
35. Missing credential, network error, or API error leaves the snapshot **unchanged** and exits 0. *(M18)*
36. A collector that constitutes the whole job offers `--strict`, and strict refuses **before** writing. *(M18)*
37. `persist()` refuses to overwrite a non-empty snapshot with an empty result. *(M19)*
38. A never-wired counter is not written as `0`, and an unknown value renders as unknown, never `0`. *(M20, F7)*
39. Stale values are used only when the source did not answer — `source_answered`, never falsiness. *(M22)*
40. Every test in the suite has been verified to fail when its bug is reintroduced. *(M21 corollary)*

**Snapshot**
41. `schema` is exactly `rapp-metrics/1.0`; consumers check it; a profile-native document publishes an explicit
    mapping instead of expecting inference. *(F1, F11)*
42. Identical counts produce byte-identical output; keys are sorted; there is no `generated_at` or any other
    field that moves without a measurement moving. *(F4, F5, M23)*
43. The commit step is a no-op when nothing changed, so git history is a readable time series. *(M23)*
44. Every enumerated subject appears, including all-zero ones — or absence is explicitly defined in
    `counting_rules` and cannot be confused with zero. *(F2)*
45. `counting_rules` is present and non-empty and covers people-not-clicks, no-automated-actors,
    machine-authored-subjects-count, self-reaction visibility, public attribution, and any floor-not-total
    figure. *(M29)*
46. `rank` appears only alongside a `rank_formula` a reader can recompute from the same document, and includes
    no editorial value and no `reviewer_feedback`. *(§8.3, L6)*
47. The `lanes` block is present and names both lanes. *(§8.1)*
48. Rolling-window sources are accumulated into a date-keyed ledger merged with `max()`. *(M24)*

**Editorial**
49. Editorial output lives in a separate document with schema `rapp-metrics-editorial/1.0`. *(E1)*
50. No editorial value is summed into any counter or total in the metrics document. *(E3, M30)*
51. Every review carries a `reviewer_id` resolving to the published roster, and a `rubric_version` is
    published. *(E5, E7)*
52. Every review is pinned to the digest or version of what it read. *(E6)*
53. Editorial comments on a thread carry a marker and are declared as a `review` surface. *(E13)*

**Client**
54. A missing or malformed snapshot degrades to rendering nothing — never zeros, never an error state, never a
    broken page. *(C-R1)*
55. The metrics fetch is not awaited on the critical boot path. *(C-R2)*
56. All rendered snapshot values are escaped, numeric values coerced, and thread URLs scheme-checked. *(C-R4)*
57. The snapshot is not stored inside the user's exportable local state. *(C-R5)*
58. Writes come from the viewer's own credential, on explicit user action, check existing reaction state
    first, and never block the action being measured. *(C-W1..C-W4)*
59. Per-subject and portfolio views read the same snapshot. *(M26)*

**Privacy**
60. The snapshot contains no usernames or any per-person identifier, and no per-event records — the sole
    exception being `collector_logins`, which names automated identities. *(PR1, PR2, F6, F12)*
61. The interaction point states plainly that reacting is publicly attributable on the platform. *(PR4)*
62. Withdrawal removes the person from the count with no residue. *(PR5)*

**The founding tenet — enforcement (numbered last, disqualifying like items 1–11)**

These five are what turn half one from a declaration into something an implementation can be *checked* against.
Items 1–3 constrain only the adopter's own collector; a bot that never read this spec is unaffected by them.

63. **Every reactor is classified and non-`User` reactors are dropped** before any counter is taken, and the
    `reactors` connection is paginated to exhaustion. Where it cannot be, the counter is published as `null`,
    never as the unclassified `totalCount`. *(M38, §1.1)* — **Test:** a fixture reaction group with
    `totalCount: 3` whose `nodes` are `[User, Bot, User]` yields `2`; a fixture whose reactor pagination is
    truncated yields `null`, not `2` and not `3`. **Assert the query requests `__typename` and requests no
    reactor `login`/`id`/`avatarUrl`** *(PR9)*.
64. **No published counter is a sum of two or more reaction contents on the same object.** `endorsements` and
    every `tally` name exactly one `reaction`. *(M39, R7, S8)* — **Test:** one fixture actor leaving
    `THUMBS_UP + HEART + HOORAY + ROCKET + LAUGH` on a top post yields `endorsements == 1`, not `5`. Also
    assert statically that no surface of kind `endorsement` or `tally` declares a `map`.
65. **A marker is recognized only when it is the first non-whitespace token of the body AND the author is the
    collector identity** (`viewerDidAuthor`, or `author.login ∈ collector_logins`); `collector_logins` is
    published and contains only automated identities. *(M40, S1, F12)* — **Test:** fixture 5(c) — a human
    comment quoting a marker is NOT machinery; and a comment carrying a marker at the head but authored by a
    stranger is NOT machinery, so it can neither delete itself from `conversation` nor donate its reactions to
    a surface counter.
66. **Marker lookup is exhaustive:** the collector paginates the comment connection (and each `replies`
    connection) until every declared marker is found or the connection is exhausted, and the provisioner never
    creates a surface comment on the basis of a partial page. *(M37)* — **Test:** a fixture thread whose
    machinery comments sit on page 2 still subtracts them from `conversation` **and** reports the surface as
    already provisioned; assert that a single-page reader fails both halves.
67. **Every `review` surface declares a `reviewer_id` that resolves to the editorial roster,** and
    `reviewer_feedback` is keyed by exactly those ids. *(S9, E5, M35)* — **Test:** item 9's roster-resolution
    assertion; plus a two-reviewer fixture in which each reviewer's feedback is separately derivable from the
    declared surfaces.

---

## 14. Status of the reference implementations

Honesty about what is running matters more than a clean conformance table. **Nothing in this document was
exercised against a live GitHub API.** Every behavioural claim is read from source or from committed state
files in scratch clones.

### RAR — running; substantially conformant; eight gaps

Verified by reading `scripts/discussion_ratings.py`, `.github/workflows/refresh-ratings.yml`,
`docs/REPORTING-TESTS.md`, `state/discussion_ratings.json` (schema `rar-discussion-ratings/1.0`, 272 entries,
**5** with any nonzero value), `registry.json` (279 agents), `scripts/fetch_download_counts.py`,
`scripts/build_metrics.py`, `scripts/publish_reports.py`, and `store.html`.

| Checklist area | Status |
|---|---|
| Threads, anti-spoof, duplicates, provisioning, caps | conformant |
| Non-fatal collection, never-clobber, never-write-zeroes | conformant |
| Byte-stable snapshot, no timestamps, no-op days make no commit | conformant for `discussion_ratings.json` and `downloads.json` |
| Half one — no bot reactions in practice | conformant **for its own collector**; `refresh-ratings.yml` runs `seed`/`tally`/`fetch` only. Says nothing about any other automated actor — see Gap 7 |
| Editorial separation | conformant in file layout (`critic_reviews.json`, `curator_reviews.json` are separate files) and stated in prose |
| Machine-authored subjects earn full counts | conformant — a large share of the registry is machine-generated and nothing branches on it |
| **Gap 1** | The snapshot publishes no `surfaces`, no reaction map, no `counting_rules`, no `lanes`. A reader must read the collector's source to learn what `signals.shipped` counts. *(R4, M29, items 26/45/47)* |
| **Gap 2** | `state/metrics.json` carries `generated_at` and appends a history entry every run, so its no-op commit guard can never fire. That file is **not** conformant; `discussion_ratings.json` is. *(M23, item 42)* |
| **Gap 3** | `discussion_ratings.py` ships an `addReaction` mutation behind `track` (line 185). Conformant as used (browser, viewer's token) but not *by construction*: a future workflow calling it would silently violate half one. *(M32, items 1/3)* |
| **Gap 4** | No `review` surface and no `reviewer_feedback`. Machine reviews exist (`curator_reviews = 420`) but no surface collects human reaction to them, so half two's feedback loop is not implemented. *(M35, items 9/10)* |
| **Gap 5** | **`upvotes` is not a conforming `endorsements` value.** `positive_score()` sums reactors across **five** reaction contents — `POSITIVE_REACTIONS = {THUMBS_UP, HEART, HOORAY, ROCKET, LAUGH}` (`scripts/discussion_ratings.py:78-80`), summed at `:272-278`, published as `upvotes` at `:343`. Dedup is per-emoji, so one person leaving all five contributes **5**: a click-count, in the headline human counter. No `endorsement` surface is declared either, so a reader cannot learn what the number counts. *(M39, R7, S8, items 26/64)* |
| **Gap 6** | **Marker matching is unanchored and author-blind.** `marker_comment_of()` is `if marker in (c.get("body") or "")` (`:284`), and the discussion query requests no `author` and no `viewerDidAuthor` (`:155-170`). Two consequences: a human **quote-reply** to a tally or signal comment carries the copied marker and is subtracted from `comments` — a human action deleted because of what it was attached to (§1.3) — and any machine that comments *without* a marker is counted as human conversation. *(M40, S1, item 65)* |
| **Gap 7** | **No reactor classification.** Every counter reads `reactors { totalCount }` (`:165`, `:168`, `:277`, `:310`, `:321`); the string `__typename` does not appear in the file. A bot account or App installation reacting on a thread or a surface comment is counted as a person and nothing in the pipeline could notice. Half one is enforced only over RAR's own collector. *(M38, §1.1, item 63)* |
| **Gap 8** | **Comment lookup is one page deep.** `comments(first: 25)` for counting (`:160`) and for the provisioner's search (`:200`), with no cursor loop on that connection (the `pageInfo` at `:153` paginates *discussions*, not comments). Past 25 comments the markers leave the window: machinery stops being subtracted **and** the provisioner re-adds a duplicate surface comment, splitting the tally. Hits the busiest threads first. *(M37, item 66)* |

### rapp-vision — a collector exists as of this writing; unrun; four gaps and one partial

`scripts/rapp_metrics.py`, `tests/test_rapp_metrics.py`, `docs/METRICS.md`, `.github/workflows/metrics.yml`,
and `state/metrics.json` (schema `rapp-vision-metrics/1.0`) were present in the scratch clone when this spec
was written, authored in a parallel session. **They were being written while this was written, and the file
grew by roughly two hundred lines between two reads minutes apart during this revision.** Every rapp-vision
claim below is therefore cited **by identifier, not by line number** — a line number for this file is stale
before it is committed. Treat the table as a read at a point in time, not a stable description. I did not run
the collector, the tests, or the workflow.

| Checklist area | Status as read |
|---|---|
| Channel-qualified `subject_id` (§5.4) | implemented — `subject_id(channel_id, video_id)`, with the shape check requiring exactly one slash |
| Two-check anti-spoof, duplicate resolution, category filter | implemented — `build_snapshot()` mirrors RAR's four checks with the reasoning in the docstring |
| Marker-comment poll, per-marker idempotent back-fill, capped writes | implemented — `MARKERS` registry, `seed` / `surfaces` / `fetch` / `editorial` subcommands |
| Named negatives that never subtract | implemented — `too_long`, `confusing` in `NEGATIVE_SIGNALS`, stated in the surface body itself |
| Machinery excluded from conversation | implemented, in the sharper "comments carrying a marker" form — `machinery_comment_count()` counts *comments*, not markers found, so a double-provisioned surface excludes both copies (M10) |
| **Marker anchoring and authorship (M40)** | **implemented, and ahead of this spec's earlier draft** — `is_machinery_comment()` requires `body.startswith(marker)` **and** `machinery_authored()` (`viewerDidAuthor`, or an env-overridable author allowlist defaulting to `github-actions[bot]`); `marker_comment_of()` and `machinery_comment_count()` share that one predicate. Its own comment states the rule this spec now adopts: *"A marker is a ROUTING LABEL, never proof of who wrote the thing carrying it."* M40 is that behaviour promoted to a normative invariant. |
| **Half one — no bot *self*-reactions** | **conformant by construction** for its own collector: the module contains **no `addReaction` mutation at all**, and the workflow records the property in a comment. This is the strongest form of M32 in either implementation — and it still says nothing about any *other* automated actor (Gap C). |
| `reviewer_feedback` collected | **implemented** — `reviewer_feedback()` reads the reactions on the editorial comment, `build_editorial()` folds it in per subject and stamps `"actor": "human"`, and `rubric_health()` publishes the portfolio view. An earlier revision of this section recorded the opposite; that entry was **wrong** and is corrected here. What remains is where it is published and how it is keyed — Gap A. |
| Editorial lane | implemented as an in-file `editorial` block with `EDITORIAL_NOTE` and a marker; **1.0 requires a separate document** *(E1, item 49)* |
| Snapshot schema | profile-native `rapp-vision-metrics/1.0` with a `videos` map; needs the §8.6 mapping or the canonical document *(F11, item 41)* |
| **Gap A — `reviewer_feedback` placement and key** | It lives inside the `editorial` block rather than in the human document, and it is attributed with `EDITORIAL_BY = "rapp-vision-rubric/1.0"` — a rubric/profile string, not a roster `reviewer_id`. Two fixes: publish it in the human document (it is a human counter, §1.5, F8), and key it by a stable roster id that does not move when `rubric_version` does. *(S9, E5, M35, items 9/67)* |
| **Gap B — replies to the machine review are counted nowhere** | The one place half two loses real signal, and the module says so itself, verbatim in its KNOWN LIMITS block: *"`reviewer_feedback` counts REACTIONS on the machine review. A threaded REPLY to that comment is not counted anywhere: GitHub returns replies on a separate `replies` connection that this query does not request. A human reply is human engagement and should count, so this is an understatement of the feedback loop, not an inflation of it — the direction of the error is the safe one, but it is an error."* The query requests `comments(first: 100) { nodes { … } }` with no `replies`, and `human_comment_count()` is `comments.totalCount - machinery`, so a human arguing under a machine review is invisible to `conversation` **and** to `reviewer_feedback`. This is exactly what restated-M10 requires and what checklist item 5(b) tests. *(M10, M36, L5, items 5/8)* |
| **Gap C — no reactor classification** | Every counter reads `reactors { totalCount }` — the query, `positive_score()`, `signal_counts()`, `watch_count()`, and `reviewer_feedback()` all do; `__typename` does not appear in the file. A third-party bot or App installation reacting on any surface is counted as a person. *(M38, §1.1, item 63)* |
| **Gap D — `upvotes` is a five-content sum** | `positive_score()` carries the same `POSITIVE_REACTIONS = {THUMBS_UP, HEART, HOORAY, ROCKET, LAUGH}` set as RAR and publishes the sum as `upvotes`, so one person leaving all five contributes 5. *(M39, R7, item 64)* |
| **M37, partially — pagination not done, but the failure is honest** | The comment connection is still read one page deep (`comments(first: 100)`) with no cursor loop, so M37 is **not** met. What the module does instead is refuse to publish a wrong number: past one page `comments` is published as `null` with `comments_truncated: true` — explicitly *"NOT … `totalCount` minus the machinery found on page one: a machinery comment past position 100 is not in the subtrahend and would be counted as a human reply, which is a machine's own output landing in a human counter"* — and the editorial command becomes update-only rather than appending a second note. It states the remaining work in its own words: *"Restoring a number needs nested pagination on the comments connection, which is a live-API change this file does not make."* That is F7/M20 behaviour standing in for M37: the count is unavailable rather than false. **M37 still requires the pagination**; this row records that the interim failure mode is the safe one. *(M37, F7, M20, item 66)* |
| Live data | `state/metrics.json` has an empty `videos` map — no thread has been seeded. Nothing here is proven at volume. |

**What is unproven everywhere.** No live API call, no observed workflow run, no load. RAR's live snapshot has
272 subjects of which 5 carry any nonzero value, maximum 1 endorsement and 1 acquisition; rapp-vision's is
empty. The rate-limit drain (M17), the back-fill (M16), and the no-op-commit property (M23) are proven by
construction and by hermetic tests, **not** by observation.

---

## 15. Non-normative — what does NOT generalize

Do not lift these from the reference implementations. They are product decisions, not protocol.

- **`score = 2*upvotes + downloads`.** An arbitrary storefront weighting. Another subject kind needs its own
  weights, or none at all (§8.3).
- **The seven experience channels** (`worked / did_not_work / stuck / regular_use / shipped / saved_time /
  want_to_try`) and rapp-vision's seven (`watched_it_all / learned_something / want_more_like_this /
  tried_it_myself / saved_for_later / too_long / confusing`). The *shape* generalizes — ≤8 mutually exclusive
  channels, one distinct reaction each, meaningless options left unmapped. Neither vocabulary does.
- **"Announcements".** The invariant is *"a category ordinary users cannot post in"*, not the name.
- **The Rotten-Tomatoes critic/user split**, certified/fresh/rotten states, and split leaderboards. An
  editorial *product*, not the editorial *lane*.
- **jsDelivr per-file CDN hits as a download proxy.** Works only because each RAR subject is a single public
  `.py` file. No per-subject public file, no equivalent.
- **The `@publisher/slug` grammar**, snake_case enforcement, and `rar_<flat>_agent.py` install filenames.
  RAR packaging.
- **Federation and peer-store snapshots.** Registry-of-registries concerns.
- **The superseded issue-based vote path.** Its lesson generalizes — *two sources feeding one on-screen count
  guarantees they visibly disagree with the badge beside them, so exactly one is displayed* — the file does not.

---

## 16. Machine-readable registration

The entry to add to `kody-w/rapp-spine/registry.json`, matching the shape of the existing entries:

```json
{
  "spec_id": "rapp-metrics/1.0",
  "repo": "kody-w/rapp-metrics",
  "layer": "distribution",
  "founding_tenet": "The ACTOR determines the lane, never the SUBJECT. An automated actor never contributes to a human counter; a human acting at the bot layer always counts, including on machine-authored subjects and machine-written reviews.",
  "purpose": "Real utilization/impact numbers for surfaces with no backend. GitHub Discussions supply per-subject identity, spam control and per-user-deduped reaction counters; a scheduled workflow folds them into one byte-stable, content-addressable JSON snapshot any static page reads. No server, no auth, no PII. Machine reviewers get a first-class editorial lane in a separate document that can never enter the human counters — while the humans who react to those reviews are counted like any other humans.",
  "when_to_use": "When a static RAPP surface (registry, tool gallery, video channel, egg hub) needs defensible usage numbers and you refuse to run a server or hold user data. Reference impls: RAR (subject = agent), rapp-vision (subject = video).",
  "entry_point": "Implement one function — enumerate() -> [{subject_id, title, url, digest}] — declare a profile, run the collector on a cron. SPEC.md in repo; §1 is the law, §13 is the conformance checklist."
}
```

---

## Changelog

- **1.0** — Initial normative statement. §1 states the founding tenet as the constitution: **the actor
  determines the lane, never the subject** — an automated actor never contributes to a human counter, and a
  human acting at the bot layer always counts, including on machine-authored subjects and machine-written
  reviews; the editorial lane is derived from that law rather than presented as a primitive, and
  `reviewer_feedback` is required so the community can rate the reviewer. Generalizes RAR's running
  Discussions-as-backend metrics stack into a subject-agnostic protocol: the subject provider interface as the
  single adopter-implemented component; namespace-qualified `subject_id` grammar with machine-enforced
  permanence; thread binding with two-check anti-spoof; the marker-comment-as-n-option-poll surface (with the
  `createDiscussion` limitation that forces it) in three kinds — tally, poll, review; protocol-default reaction
  maps with profile rebinding; the `rapp-metrics/1.0` snapshot schema with required byte-stability, published
  surface registry, published `lanes`, and published counting rules; 40 invariants each with rationale and
  failure mode; a structurally separated `rapp-metrics-editorial/1.0` lane; a client contract; a
  public-by-design aggregate-only privacy model; and a 67-item conformance checklist whose sixteen §1 items
  (1–11 and 63–67) test both halves of the tenet.

  **Half one is enforced, not merely declared.** An earlier draft asserted that no automated actor may reach a
  human counter while shipping no mechanism that could detect one. 1.0 closes that with four invariants and
  five checklist items: **M38** classifies every reactor by `__typename` and drops non-`User` actors (with
  PR9 bounding what the collector may read to do it, and F7 requiring `null` rather than an unclassified
  count); **M39** and **R7/S8** forbid a counter built by summing several reaction contents, because
  per-emoji dedup makes such a sum a click-count — which is why `endorsements` is now defined as exactly one
  named reaction content, declared in the surface registry; **M40** requires a marker to be head-anchored
  *and* authored by a published `collector_login` before a comment is treated as machinery, so a human
  quote-reply is never deleted from `conversation` and an unmarked machine comment is never counted as one;
  and **M37** requires marker lookup to be exhaustive, so machinery does not silently fall off the first page
  of a busy thread. §1.1 now states the residual plainly: the guarantee is *"no declared machine actor"*, not
  *"no machine actor"*. **M10** is restated to include threaded replies, because `comments.totalCount` counts
  top-level comments only and a human replying to a machine review — half two's most valuable signal — was
  invisible to the previous formula. **S9/E5** bind each `review` surface to a roster `reviewer_id`, which is
  what makes `reviewer_feedback` derivable for a panel instead of underdetermined.
