<!-- (c) 2026 Kody Wildfeuer · part of the RAPP ecosystem (RAPP) -->

# CANON — the constitutional landing of the actor-lane law

> **STATUS: PROPOSAL. THIS DOCUMENT IS NOT CANON AND AMENDS NOTHING.**
>
> Nothing here has been ratified. No constitution file was edited to produce it. This is
> drafted text for Kody to review, edit, and land himself under the amendment procedure of
> whichever document he chooses. Per the estate's standing rule, novel canon questions go to
> the operator, never improvised by an agent — so this file stops at the doorstep of the law
> and hands over the wording.
>
> **Home as spec text:** `kody-w/rapp-metrics/SPEC.md` §1 (landed 2026-08-02, this session)
> **Home if landed as kernel law:** `kody-w/RAPP/CONSTITUTION.md`, new Article LVII
> **Source ruling:** Kody, 2026-08-02 — *"a human can interact at the bot layer… then its
> fair game… this is where we draw the simple lines of engagement."*

---

## 0. The ruling in one line

> **The actor determines the lane — never the subject.**

Who *performed* an action decides which counter it feeds. Not who authored the thing being
acted upon.

This has two halves and both are mandatory. Drop the first and every number the estate
publishes is a lie. Drop the second and agent-authored content becomes unmeasurable, which
guts the entire value of a content machine.

---

## 1. The proposed amendment text

### 1.1 As kernel law — Article LVII

The text below is written to be pasted into `kody-w/RAPP/CONSTITUTION.md` immediately after
Article LVI, in that document's own voice and clause structure. It carries the same
AI-drafted banner Article LVI carries, because that is the convention the constitution
already established for a machine-proposed article awaiting operator ratification.

---

```markdown
## Article LVII — The Actor Determines The Lane (Every Count Means People)

> **DRAFT — proposed by AI 2026-08-02. Operator should review and ratify.**

> **Who performed an action decides which counter it feeds — never who authored
> the thing acted upon.** An automated actor may never contribute to a human
> counter. A human acting at the bot layer always does. Agent-authored *content*
> is a first-class citizen that earns real human numbers; only agent-authored
> *actions* are quarantined.

Every number this estate publishes about itself — endorsements, installs,
tallies, conversation counts, votes, rankings — is published on one claim:
**that it counts people, not clicks.** That claim is not a policy the estate
enforces by hand. It is a property it inherits, because the substrates the
estate counts on (GitHub reactions on a Discussion, one per account per emoji)
deduplicate per user at the platform. The estate did not build that property
and cannot rebuild it. It can only fail to protect it.

One bot reaction ends it. Not degrades it — ends it. A count that mixes one
machine action into a hundred human ones is no longer a count of people, and no
downstream disclaimer restores it, because a reader cannot tell which number was
contaminated. This article exists to make that failure structurally impossible
rather than merely discouraged.

### LVII.1 — An automated actor may never touch a human counter

A bot, service account, app installation, CI token, scheduled workflow, agent
`perform()`, or any credential not held by a person acting on their own behalf
**MUST NOT** perform an action that increments a human counter. On the GitHub
substrate the human lane is **reactions**, and it is closed to machines
absolutely.

On a human-counter surface an automation's write-capable token may create
threads, provision surfaces, post marked machine comments, and splice report
cards — that is the whole list. Elsewhere (committing snapshots, opening PRs,
publishing artifacts) an automation acts freely, because those actions touch no
counter.

### LVII.2 — A human acting at the bot layer is fair game and MUST count

A person is a person at every layer they touch. When a human upvotes an
agent-generated video, that is a human endorsement and it counts, fully. If two
hundred people do it, that is two hundred real people. When a human reacts to or
replies to a machine review, that is human engagement and it counts, fully.

No surface may discount a human action because the object of that action was
machine-made, and no surface may route a human action into a machine lane on the
grounds that it arrived through automation-adjacent plumbing.

### LVII.3 — Quarantine by actor, never by subject

Machine *output* is a first-class publication of this estate and is published,
attributed, and rendered as such: to a reviewer id from a declared roster, under
a versioned rubric, pinned to the digest of exactly what it read, and visibly
labelled machine-authored at every render site. It lives in its own **editorial**
lane — a separate document, so that a consumer summing the human counters is
*structurally incapable* of picking it up.

Machine output **MUST NOT** be summed into any human counter. Machine output
**MUST NOT** be suppressed, discounted, or excluded from measurement for being
machine-made. Quarantining by subject — treating agent-authored content as
unmeasurable — is the opposite error and is equally forbidden.

### LVII.4 — Human signal on a machine review rates the reviewer

Because a human reacting to a machine review counts (LVII.2), that signal is
real and it is *about the reviewer, not about the subject*. It **MUST** be
attributed to the reviewer and the rubric version, never folded into the
subject's own numbers.

Sustained negative human signal on an agent's reviews is the community telling
the estate its rubric is wrong. That is a feedback loop the estate builds and
exposes, not one it averages away.

### LVII.5 — Transition: the guard binds now, the rest is backfilled

This article lands on an estate that already publishes counters, so it binds at
two speeds, in the register Article XLVIII.1 established for a mandatory rule
that arrives after its subjects do.

**Immediately, with no grace period: LVII.1.** From ratification, no surface —
existing or new — may let a bot, service account, app installation, CI token, or
agent `perform()` touch a human counter, and no surface may rely on an opt-out
to stay clean. The guard fails closed. There is nothing here to phase, because
the harm it prevents is the one harm in this article that cannot be repaired
after the fact, and the change that prevents it is local to each surface.

**By backfill: everything else.** A surface that publishes human counters but
has not yet published an editorial document (LVII.3) or a reviewer-feedback
channel (LVII.4) is **`compliance: legacy`** — a declared, visible state, not a
violation. It is not an exemption: `compliance: legacy` is a public statement
that the surface owes work, and it is flagged exactly as XLVIII.1 flags a beacon
with no `private_estate_pointer`. A surface leaves the state by publishing both;
there is no further ceremony and no ratification step. A surface that has never
published a machine review owes neither document and is conformant without them.

**What this article requires:**
- Every published counter names its actor class, and every surface that accepts
  a human action authenticates that the actor is a person acting for themselves.
- Machine output is published in a separate document with its own schema string,
  a reviewer roster, a `rubric_version`, and a digest pin per review.
- Every render site labels a machine number as machine-authored, with the
  reviewer id visible or one interaction away.
- Human signal on machine output is collected and attributed to the reviewer.

**What this article forbids:**
- Any bot, CI token, app installation, or agent action on a human-lane surface.
  An opt-out environment variable is not a guard; the guard fails closed.
- Summing machine output into `endorsements`, tallies, conversation counts,
  rank, or any human total.
- Excluding agent-authored *content* from human measurement, or applying a
  discount to human actions because the subject was machine-made.
- One object carrying two metrics — a surface whose reactions cannot be read as
  a statement about exactly one thing is not a countable surface.

**Why this is constitutional and not a feature:**
Because the drift is one-directional and irreversible. Every future automation
in this estate will have a token, an errand, and a plausible reason to nudge a
number — a download tracker, a nightly sweep, a helpful agent "registering" an
install. Each one is individually reasonable, and the first one that lands
retroactively voids every number the estate ever published, including the
honest ones. There is no repair: you cannot un-mix a bot from a count, and you
cannot prove to a stranger that you didn't. A rule enforced per-surface will be
forgotten by the fourth surface. Constitutionalizing the actor-lane split makes
the property inheritable by every surface built after it, which is the only
form in which it survives.

This amendment satisfies Article XXVI: it preserves Article I (it adds no
responsibility to `brainstem.py` or `function_app.py` — it defines no route, no
slot, no in-core state) and it preserves Article XXV (it removes and renames no
wire field; it is purely additive).
```

---

### 1.2 As spec text — `rapp-metrics/1.0` §1

**Already landed while this was being drafted.** A parallel session restructured `SPEC.md`
during this run: the tenet is now **§1, The founding tenet** — ahead of §2 (Conformance
language) — and §10 is retitled *"The editorial lane — a consequence of §1, not a
primitive."* That is a better placement than the §0.1 I was going to propose, and it makes
the spec-tier half of §2.1 below already done.

The compressed rendering I drafted is kept here as a **cross-check against the landed text**,
not as a competing proposal. If the landed §1 says less than this, it is missing something; if
it says more, this is the floor:

```markdown
## 0.1 The founding tenet

> **The actor determines the lane — never the subject.**

Who *performed* an action decides which counter it feeds; not who authored the
thing acted upon.

- **No automated actor may contribute to a human counter.** Reactions are the
  human lane, and they are what make every count in this document mean people.
  A bot, service account, app installation, or CI token that adds one reaction
  makes every number this protocol publishes a lie. (Normative: the editorial lane's E11–E13.)
- **A human acting at the bot layer counts, fully.** A person upvoting an
  agent-generated subject is a person. A person reacting to a machine review is
  a person. Two hundred of them are two hundred people.
- **Machine output is quarantined by actor, never by subject.** Agent-authored
  content is a first-class subject that earns real human numbers. Only
  agent-authored *actions* are walled off, into the editorial lane. (The editorial lane's E1–E4.)
- **Human signal on a machine review rates the reviewer.** It is attributed to
  the reviewer id and `rubric_version`, never to the subject. Sustained negative
  human signal on an agent's reviews means the rubric is wrong, and the protocol
  exposes that rather than averaging it away.

Everything else in this spec is plumbing for that sentence.
```

---

### 1.3 Voice match — the clauses this was written against

I matched three structural habits of the documents I read, so the amendment does not read
as an import.

**(a) A one-blockquote statement of law, then the failure it prevents.** Article XLVII opens:

> "**The network has no registry.** A new estate becomes part of the federation the moment its
> operator publishes it per spec…"

and Article XLVIII opens:

> "**A public-only estate is a toy.**"

Article LVII opens the same way, with the law in bold inside the blockquote and the
consequence in the prose beneath it.

**(b) The `requires` / `forbids` / `why this is constitutional and not a feature` trio.**
Articles XLVII and XLVIII close every subsection with exactly those three labelled lists.
Article LVII closes with the same three, verbatim in label and order.

**(c) Plain-consequence enforcement prose, not legalese.** RAR's Article XXIII is the estate's
model for this register:

> "A published agent path is a public contract. It is not an implementation detail, it is not
> ours to tidy, and it is not subject to refactoring taste."

and

> "Absence of evidence of use is not evidence of absence of use."

LVII's "why" paragraph is written in that register — concrete failure, named mechanism, no
appeal to principle without a consequence attached.

**(d) The AI-draft banner.** Article LVI carries:

> "**DRAFT — appended by AI 2026-08-01. Operator should review and ratify.**"

Article LVII carries the identical banner with the 2026-08-02 date. That convention already
exists in the file; a machine-proposed article that omits it would be the anomaly.

---

## 2. Where it should land, and in what order

**Recommendation: both — but in a specific order, and they are not the same edit.**

### 2.1 Land it in `rapp-metrics/1.0` FIRST — DONE during this session

Reasons it belongs there first:

- It costs nothing to land. rapp-metrics is a Tier-3 spec under `rapp-canon/1.0` §2. Its
  amendment procedure is §5.3 — "a spec changes by publishing a new version" — and since
  rapp-metrics/1.0 has not shipped yet, this is not even an amendment; it is initial
  normative statement, and its own Changelog already says so.
- The normative machinery was already there. The editorial-lane rules E1–E4 are half one,
  E10–E13 are the enforcement, and E11 already read *"A conforming implementation MUST NOT
  let a bot, service account, app installation, or CI token add a reaction to any endorsement
  or signal surface."* What the tenet adds is the **generative sentence those rules were
  derived from** — plus half two, which the draft I first read stated nowhere. As it stood, it
  encoded the prohibition and omitted the permission, and a reader could have concluded that a
  human upvote on an agent-generated video was contaminated.
- It binds every adopter of the protocol on day one, without touching a foundation-locked
  file.

> **Status, same session:** this step is **done**, and done better than I was going to
> propose it. A parallel session landed the tenet as `SPEC.md` **§1 — The founding tenet**,
> ahead of the conformance language, and retitled the editorial section *"The editorial lane
> — a consequence of §1, not a primitive."* Section numbers shifted by one from my first
> read: provider §4→§5, invariants §8→§9, editorial §9→§10, checklist §12→§13, registration
> §15→§16. Cross-references elsewhere in this document use the **new** numbering.
>
> What remains from §2 is therefore only **§2.2** (the kernel article), **§2.3** (RAR's
> enforcement clause) and **§2.4** (the foundation re-lock).

### 2.2 Land it in the kernel constitution SECOND, as Article LVII

`kody-w/RAPP/CONSTITUTION.md`, appended after Article LVI. Reasons:

- **The law is not metrics-specific and a Tier-3 spec cannot reach the surfaces that need
  it.** `rapp-canon/1.0` §6 is explicit: a sub-constitution "may impose **stricter** rules on
  its domain than kernel canon; it may never grant a **permission** kernel canon withholds"
  — and, by the same logic, it cannot bind a domain it does not own. RAR's `rapp_sdk.py`
  install path is not a rapp-metrics implementation and never will be; nor is the
  localFirstTools gallery's vote system, nor rapp-commons' signed-event tallies, nor
  RAPP_Store install counts. Only kernel law reaches all of them.
- **It is genuinely constitutional in the estate's own sense of the word.** The kernel
  constitution's own test for that (used in Articles XLVII, XLVIII, LVI) is: *without this,
  what is the dominant drift?* Here the dominant drift is one plausible automation at a time
  until no published number is defensible, and the failure is unrepairable after the fact.
  That is the same shape of argument Article XLVII makes about central indexes.
- **It sits in article-space, not RAPP/1 wire-space.** The CONSTITUTION header scopes the
  RAPP/1 rev-5 authority boundary to "canonicalization, identity, frames, wire, eggs,
  registry, trust, and protocol evolution." I fetched `RAPP1_AUTHORITY.json` (schema
  `rapp-authority-pin/1.0`) and it is a structural pin on the wire spec's bytes — nothing in
  it concerns measurement or engagement. So Article LVII does not require a rev bump; it
  follows the Article LVI precedent of appending after the bounded 0–LIV history. **Confirm
  against `RAPP1_STATUS.md` before merging — I did not read that file.**
- **It can land before the work in §3.1 exists, because LVII.5 says so.** Without a transition
  clause, ratifying LVII second would make RAR — the estate's own reference implementation —
  unconstitutional the moment it merged, since LVII.4's reviewer channel is net-new work
  (§3.1 finding 4). LVII.5 puts every existing counter surface in `compliance: legacy` until
  it publishes an editorial document and a reviewer channel, while binding LVII.1's
  fail-closed bot guard immediately. So the only item that must ship *with* ratification is
  §2.3's guard; the rest is backfill.

### 2.3 Do NOT add it to RAR's constitution as a new Article

RAR's `CONSTITUTION.md` is a domain sub-constitution (Tier 3, `rapp-canon/1.0` §6). It should
**inherit** Article LVII, not restate it — a restated law is a second copy that can drift, and
the estate already runs four drift-detection legs precisely because copies drift. What RAR
should add instead is an **enforcement clause**, in the register its Article XXIII already
established for enforcement (append-only ledger + a CI job that is the *first* job so nothing
can merge around it):

> Amend RAR `CONSTITUTION.md` Article XI (Security & Trust) with a sub-section — not a new
> Article — reading approximately: *"No code in this repository may call `addReaction` with a
> token it did not obtain from a person acting on their own behalf. `scripts/` and any code
> reachable from CI MUST refuse to react when `CI` or `GITHUB_ACTIONS` is set. Enforced by a
> test in the blocking suite, not by convention."*

### 2.4 Prerequisite, not a side effect: re-lock the foundation

**This is a required, ordered step and it must be scheduled as work, not assumed.**

`kody-w/rapp-spine/foundation.json` has a `law[]` array that content-addresses the estate's
law files. Its entry for the kernel constitution is:

```json
{ "doc": "rapp-constitution (kernel)", "repo": "kody-w/RAPP",
  "raw_url": "https://raw.githubusercontent.com/kody-w/RAPP/main/CONSTITUTION.md",
  "sha256": "53cb10592cf44ea04e8f1fab443aaf09bab610f298203555e959e13f19330f11",
  "locked": true }
```

**That hash is already stale.** I fetched the live file at
`raw.githubusercontent.com/kody-w/RAPP/main/CONSTITUTION.md` on 2026-08-02 (4,295 lines) and
computed:

```
live sha256   e457568b989deea488ff44ce632ba0d2b5bde4dcc4866744120ba7e0af7acc90
locked sha256 53cb10592cf44ea04e8f1fab443aaf09bab610f298203555e959e13f19330f11
```

They do not match. The lock predates at least Article LVI (dated 2026-08-01 in the file
itself).

Why this blocks the amendment rather than merely accompanying it:

1. **A stale lock cannot distinguish a ratified change from an unratified one.** Appending
   Article LVII to a file whose lock is already broken produces a second divergence stacked
   on a first, and no drift detector can then say which edit was law and which was drift.
2. **`rapp-canon/1.0` §4 makes it a merge gate.** A change is canon only if it "leaves no
   spec stale" — a new primitive "incurs a **registration debt** that MUST be paid *in the
   same change-set*." Amending law while its own content-address lock is broken is exactly an
   unpaid registration debt, and `grail-scan` should flag it.
3. **`foundation.json` says its own hashes are the verification path**: *"Fetch over the
   hydra, verify sha256 against this."* A consumer doing that today already fails on the
   constitution. Landing LVII without re-locking hands that consumer a second reason to fail
   and no way to tell them apart.

**The ordered sequence:**

1. Confirm the current `main` CONSTITUTION.md (`e457568…`) is intended law — i.e. that
   Article LVI's DRAFT banner reflects Kody's decision, not an unreviewed append.
2. Re-lock: update `foundation.json.law[0].sha256` to the confirmed current hash. Commit
   that alone. This is the repair of an existing break and is independently worth doing
   whether or not Article LVII ever lands.
3. Merge Article LVII into CONSTITUTION.md.
4. Re-lock again to the post-amendment hash, in the same change-set as (3), paying the §4
   registration debt.
5. Snapshot the ratified version into `kody-w/rapp-god/versions/` per `rapp-canon/1.0` §7,
   which gives the law the same rollback points the kernel has.

### 2.5 A drifted pointer the amendment PR will trip over — flag for Kody

`rapp-spine/specs/CANON.md` §5.2 states: *"The Constitution is amended under **Article IX
(Amendments)**."*

The live kernel constitution's amendments article is **Article XXVI — Amendments**. RAR's is
**Article XXII — Amendments**. Neither is Article IX. (Kernel Article IX is "The Twin Offers,
The User Accepts.")

So the estate's meta-law currently cites a procedure by a number that resolves to the wrong
article in every constitution it governs. Whoever writes the Article LVII PR has to cite an
amendment procedure, and there is no consistent one to cite. **This is a novel canon question
and it is Kody's call**: either `rapp-canon/1.0` §5.2's pointer is corrected to Article XXVI,
or the kernel constitution's amendment article is renumbered — the first is almost certainly
right, but I am not guessing at canon. Recommend fixing it in the same sitting, before the
LVII PR, so the PR can cite a real procedure.

---

## 3. Blast radius — what has to change to conform

### 3.1 RAR — conformant in the live path, non-conformant in a reachable one

**Plainly: I checked, and RAR is not clean.** Nothing automated reacts on a human surface in
RAR *today*, but the code to do it exists on the documented install path, and the only thing
preventing it is that nobody has run it in an environment with a bot token.

**What is conformant (verified by reading the code):**

- `scripts/discussion_ratings.py` restricts the human lane deliberately, and says so at the
  top of the file: positive reactions only, *"Negative reactions (THUMBS_DOWN, CONFUSED) and
  neutral (EYES) never contribute, so a thumbs-down can't drag a score down"*, and
  *"one reaction per GitHub user, so the count is spam-proof and means 'unique installers'."*
- `.github/workflows/refresh-ratings.yml` runs `seed`, `tally`, `fetch`, `build_federation`,
  `crawl_sources`, `fetch_download_counts`, `publish_reports` — and **not** `track`. The
  bot's `GITHUB_TOKEN` creates discussions and comments; it never calls `addReaction`.
  Verified by reading the workflow and by grepping the repo: `addReaction` appears in exactly
  five places, and no workflow reaches any of them.
- The browser path is correct. `store.html` `trackDownload()` uses the signed-in viewer's own
  `ghToken`, no-ops when signed out, and checks `t.viewerInstalled` first so it cannot
  double-count. That is a human acting for themselves — conformant under LVII.2.
- The editorial wall substantially exists already. `scripts/critic_review.py` writes machine
  verdicts to `state/critic_reviews.json` with per-review `reviewer_id`-equivalent
  attribution, a `backend` field (`model` / `rubric`), and reviews *"pinned to the SHA-256 of
  the agent file they read."* `scripts/build_metrics.py::apply_critic` keeps `critic_score`
  and `user_score` as separate fields and never sums them. The docstring states the split
  outright: *"CRITIC SCORE % of AI critic reviews that came back fresh… USER SCORE % positive
  human signal."*

**What is non-conformant (the finding):**

1. **`rapp_sdk.py` reacts with whatever token is in the environment, on the documented
   install path.** `download_agent()` ends with `track_download(name)` (line 538, unguarded).
   `track_download()` (line 542) calls `_get_token()` (line 403), which is:

   ```python
   token = os.environ.get("GITHUB_TOKEN")
   if token:
       return token
   # else: subprocess `gh auth token`
   ```

   There is no check that the token belongs to a person. `python rapp_sdk.py install <agent>`
   is a shipped CLI subcommand (line 2013). Run it inside GitHub Actions — where
   `GITHUB_TOKEN` is present by default and is the `github-actions[bot]` identity — and the
   bot adds a 👍 to the download-tally comment. That reaction is counted as a *unique
   installer*, i.e. as a person, and feeds `score = 2*upvotes + downloads`.

   The only guard is `RAR_NO_TRACK=1` (line 551) — an **opt-out**. Under LVII this must
   fail closed: refuse to react when `CI` or `GITHUB_ACTIONS` is set, and ideally when the
   token's identity is not a `User`.

2. **`scripts/discussion_ratings.py track` is the same hazard in the collector.** `cmd_track`
   (line 588) fires `ADD_REACTION_MUTATION` (line 185) using module-level `TOKEN` (line 68,
   `GITHUB_TOKEN` or `GH_TOKEN`). It is reachable only via the CLI dispatch at line 636 and
   is called by no workflow — I grepped; there are no other callers anywhere in the repo. So
   it is latent, not live. But it is one YAML line away from live, and the correct fix is the
   same fail-closed guard.

3. **One object is carrying two metrics.** `scripts/publish_reports.py` splices a report card
   into the Discussion **top post** (`render()`, line 123), and that card includes the machine
   verdict — line 177: `f"**Critic score** {avg:.0f}/100 from {count} independent critics…"`.
   The top post is *also* the endorsement surface whose positive reactions are counted as
   `upvotes`. So a human 👍 on that post is now ambiguous between "I vouch for this agent" and
   "I agree with the critic panel," and it lands in the agent's counter either way. Under
   LVII.4 the reviewer-directed signal has to be a *separate object* attributed to the
   reviewer and `rubric_version` — which also gives the estate the feedback loop the tenet
   asks for and which RAR has no channel for today.

4. **No reviewer-rating channel exists at all.** Machine reviews live in a JSON file. There is
   nowhere a human can tell the estate a rubric is wrong. LVII.4 requires building that; it is
   net-new work, not a fix. Under LVII.5 that does not make RAR unconstitutional on merge day:
   RAR is `compliance: legacy` until the channel exists. Finding 1's fail-closed guard is the
   one item here with no grace period.

### 3.2 rapp-vision — implementation in flight, and it already encodes the tenet

Honest caveat on freshness: rapp-vision's own README still says it has no metrics
implementation, and rapp-metrics' README §Status repeats that (*"rapp-vision (subject = video)
has no implementation"*). **That is out of date as of my read.** A parallel session is writing
the implementation into this same scratch clone right now — `scripts/rapp_metrics.py` (59 KB),
`.github/workflows/metrics.yml`, `state/metrics.json` (`schema: rapp-vision-metrics/1.0`),
`tests/test_rapp_metrics.py`, and a metrics-reading block in `index.html` all exist and were
modified minutes before I read them. Treat every claim in this subsection as a snapshot of
work in progress, not a verified shipped state.

What I read there is conformant to both halves and states them in its own header comment
(`scripts/rapp_metrics.py`, lines 33–42): the machine review goes to an `editorial` block
attributed to a reviewer, and *"A human acting at the bot layer IS counted. A person reacting
to the [machine review]… quarantining by SUBJECT ('a robot wrote the comment, so ignore…')"*
is called out as the error to avoid. Line 839 records the same thing at the point of counting:
*"These are people acting at the bot layer, so they count as human."*

So rapp-vision does not need to change to conform — it needs the tenet it already implements
to be *cited* to a landed law rather than to a comment. That is precisely what §2 is for.

### 3.3 Surfaces I did not audit — name them, don't claim them

These publish or accept counts and are in the blast radius, but I did not read their code and
make no claim about their conformance. Under LVII.5 each of them is `compliance: legacy` on
merge day rather than silently in breach — with the single exception of LVII.1's bot guard,
which binds them immediately and is what the sweep below should look for first:

| Surface | Why it is in scope | Status |
|---|---|---|
| `kody-w/RAPP_Store`, `RAPP_Sense_Store` | install/adoption counts, peers of RAR under `rapp-stores/1.0` | **unaudited** |
| `rapp-commons-event/1.0` / `rappterbook` | signed append-only social events; tallies over them are counters | **unaudited** |
| `kody-w/rapp-god` | publishes ecosystem-wide figures | **unaudited** |
| localFirstTools gallery `index.html` | its `CLAUDE.md` documents a "Vote System… stored in localStorage" — a human counter with no per-identity dedup at all, which is a different failure from the one this article addresses but lands in the same audit | **read in `CLAUDE.md` only, code unaudited** |

A conformance sweep across these is the natural follow-on work item, and `rapp-metrics/1.0`
§13's 52-item conformance checklist is the instrument for it.

---

## 4. Rationale a stranger can follow

Suppose you publish "412 people found this useful."

You did not build the thing that makes that number trustworthy. GitHub did, by allowing each
account exactly one 👍 per object. Your count is a count of *people* not because you were
careful but because the platform made duplicate people impossible. That is the whole asset.

Now suppose one nightly job, holding a bot token, adds a 👍 while doing something reasonable —
registering a download, warming a cache, "tracking an install." Your number is now 413, and
412 of them are people. There is no repair. You cannot subtract the bot, because you did not
record who reacted (and if you did record it, you have built the surveillance system you were
avoiding). You cannot annotate it, because the reader has no way to know which of your numbers
were touched. And you cannot promise it won't recur, because the automation that did it was
behaving sensibly. **One bot action retroactively converts every honest number you have ever
published into a number you have to defend.** So the rule is not "minimize bot actions." The
rule is *never*, and it has to be law, because the cost is unbounded and the temptation
arrives one reasonable errand at a time.

That is half one, and most systems stop there — usually by going further than they should:
they decide machine-touched things are dirty and quarantine the *content*. That is the
opposite error, and it is expensive in a way that is easy to miss. If an agent makes a video
and two hundred people upvote it, those are two hundred people. Discounting them because a
machine made the video does not make your data cleaner; it makes your best-performing content
invisible and your content machine unmeasurable. The same holds one layer up: if a machine
writes a review and a human argues with it, the human is a human.

So the line is not drawn around the *subject*. It is drawn around the *actor*. Machines
publish — loudly, attributably, in their own lane, labelled, never summed into the human
totals. Machines do not *act* on human surfaces. Ever.

And the last piece falls out for free. Once you accept that a human reacting to a machine
review counts, you have accidentally built the thing every automated-review system needs and
almost none have: a channel where the community rates **the reviewer**. Sustained thumbs-down
on one critic's reviews is not noise to be averaged away — it is the estate being told its
rubric is wrong, by the only party qualified to say so. Half two is not a concession to
machine content. It is what makes machine content correctable.

---

## 5. What this document deliberately does not do

- **It does not edit any constitution.** `kody-w/RAPP/CONSTITUTION.md`, RAR's
  `CONSTITUTION.md`, and `rapp-spine/specs/CANON.md` were read only. No file outside
  `scratchpad/rapp-metrics/` was written.
- **It does not commit, push, or open a PR.** The orchestrator ships.
- **It does not renumber anything or resolve the Article IX pointer drift (§2.5).** That is a
  novel canon question and it goes to Kody.
- **It has not been exercised against a live GitHub API.** Every factual claim here is
  grounded in a file I read in a scratch clone or fetched read-only on 2026-08-02, and the
  two sha256 values in §2.4 are the only things I computed myself.

### Sources read for this draft

| Claim | Source |
|---|---|
| Kernel constitution voice, Articles XXV / XXVI / XLVII / XLVIII / LVI | `raw.githubusercontent.com/kody-w/RAPP/main/CONSTITUTION.md` (fetched 2026-08-02, 4,295 lines) |
| RAPP/1 authority scope | `raw.githubusercontent.com/kody-w/RAPP/main/RAPP1_AUTHORITY.json` |
| Law ladder, amendment tiers, sub-constitution nesting, grail merge gate | `rapp-spine/specs/CANON.md` §2, §4, §5, §6, §7 |
| Foundation lock + staleness | `rapp-spine/foundation.json` `law[0]`; live hash computed locally |
| RAR sub-constitution voice (Articles II, V, XI, XXII, XXIII) | `RAR/CONSTITUTION.md` |
| RAR reaction paths | `RAR/scripts/discussion_ratings.py`, `RAR/rapp_sdk.py`, `RAR/store.html`, `RAR/.github/workflows/refresh-ratings.yml` |
| RAR editorial separation | `RAR/scripts/critic_review.py`, `RAR/scripts/build_metrics.py`, `RAR/scripts/publish_reports.py` |
| rapp-metrics normative machinery | `rapp-metrics/SPEC.md` §1, §10, §16 (numbering as of 2026-08-02 21:49); `rapp-metrics/README.md` |
| rapp-vision in-flight implementation | `rapp-vision/scripts/rapp_metrics.py`, `state/metrics.json`, `.github/workflows/metrics.yml`, `index.html` |
