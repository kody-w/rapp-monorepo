# 🎭 The Rehearsal — virtual-twin dry-runs for forged automations

**Status:** plan committed first, so the plan survives any session. Each phase
updates this doc in place; the log at the bottom says what is actually done.
Any capable model (or human) can resume from here — nothing below depends on
who executes it.

## The problem chosen, and why

RAPP Mirror already closes the *capture* loop: monkey sees your work, the
Forge distills it into a `ForgeSpec` (intent + steps + parameters), renders it
three ways (agent.py / SKILL.md / Copilot Studio zip), and can hot-deploy it
into the live brainstem.

What it cannot do is prove the automation **completes the job** before it runs
for real. Today the first execution of a forged automation *is* the test, on
live systems, in front of whoever is watching. That is the single biggest
barrier to trusting — and selling — autonomous automations.

Candidate problems ranked by direct impact of solving them:

| Candidate | Impact | Verdict |
| --- | --- | --- |
| **Virtual-twin rehearsal: simulate the whole business process virtually; end user confirms "fully done" before deploy** | Turns "trust me" into "watch it work" — the missing trust gate for every automation the Forge ever makes | **BUILD THIS** |
| More gestures / camera polish | Delight, no new capability | later |
| More Forge output formats | Breadth, but same unproven artifacts | later |
| Multi-brainstem federation | Real, but serves power users only | later |

## The feature in one paragraph

After the Forge distills a spec (or on any existing spec), the mirror can
**rehearse** it: the brainstem plays the *world* — every system, dataset, and
person the process touches — while the automation's steps execute against
that virtual world, step by step, narrated on the stage. The run produces a
verifiable transcript (inputs seen, actions taken, outcomes produced per
step). At the end the mirror asks the end user, in one screen: *"this is what
the automation will do — does this complete the job?"* Confirm → the spec is
stamped `rehearsed` and deploy proceeds. Reject → the objection is folded back
into the spec and the twin re-rehearses. **No spec deploys unrehearsed unless
the user explicitly overrides.**

## THE MAJORITY DESIGN (voted by 8 strategy-locked designers — this is what gets built)

Tally rules: ≥5/8 is in; conflicts broke on simplicity + fit with the
existing Forge pipeline. Unanimous (8/8): `electron/rehearsal.ts` engine +
`electron/rehearsal.test.ts`; reuse `chat()` + `extractJson` + one-strict-retry
with a `-rehearsal` session suffix; spec-hash-bound confirmation; `/rehearse`
+ confirm/reject control routes; gated deploy with recorded force-override;
orb-narrated steps with nod/shake portal confirmation; a machine verdict
before the human countersign.

**The flow** (per rehearsal run):

1. **SEED** — one strict-JSON brainstem call, built from the spec ONLY
   (never raw screen OCR — deliberate PII firewall, 6/8): invents
   `{scenario, world:{entities:[{id, kind, name, state, detail}]}, sampleInputs}`
   — the smallest believable business world plus sample values for the
   spec's parameters.
2. **STEP i (0..N-1)** — one strict-JSON call per ForgeStep: given the live
   world and only this step, return `{action, observation, changes:[{entity,
   field, before, after}], status: ok|blocked, note}`. The ENGINE applies
   changes (refusing unknown entities / mismatched `before` values) and
   computes the diff — concrete before→after data, never prose hand-waving
   (6/8). Malformed replies get one strict retry then land the run in
   `stalled` — fail-closed, never a crash.
3. **VERDICT** — one call judging the final world against the intent:
   `{complete, summary, gaps:[]}` (8/8 in some form).
4. **CONFIRM** — the stage shows the whole run, badged VIRTUAL; the orb asks
   "did this complete the job, fully done?" Nod / "fully done" portal →
   `confirmed`. Shake / objection → `rejected(note)` and the objection is
   fed back through a revision distill into spec v+1, which must itself be
   rehearsed (5/8).

**State machine** (legal transitions only; anything else refused):
`idle → seeding → running(i) → judging → awaiting-confirmation →
confirmed | rejected(note)`; `seeding|running|judging → stalled|error`
(terminal, count as NOT confirmed — a failed run can never be confirmed).

**Persistence** (6/8 + 5/8 hybrid): the gate's source of truth is a registry
dir (`MIRROR_REHEARSALS_DIR`, default `~/.rapp-mirror/rehearsals/<name>.json`,
tmp+rename writes) keyed by specHash; a human-shippable copy
(`rehearsal.json` + `rehearsal.md`) is written beside the other forge
artifacts in `exportsRoot()/<name>/`. Transcript carries
`version:"rehearsal/1"`, `simulated:true`, engine model + app version
(honest-simulation framing).

**The gate** (5/8 + blindspot): inside `deployAgent()` itself in `forge.ts` —
UI, control plane, and mirrorctl all funnel through it. Requires a
`confirmed` record whose `specHash` equals `specHash(normalizeSpec(spec))`.
`force` overrides, is recorded in the result and the transcript, and is
never the default anywhere.

**Files**: NEW `electron/rehearsal.ts`, `electron/rehearsal.test.ts`,
`src/Rehearsal.tsx` (stage overlay, 5/8). MOD `common/ipc.ts`,
`electron/preload.cjs`, `electron/ipc.ts` (+ `rehearsal:event` push channel,
surgeonEvent idiom), `electron/forge.ts` (gate), `electron/control.ts`
(`POST /rehearse`, `POST /rehearse/confirm`, `POST /rehearse/reject`,
`GET /rehearse/status`), `bin/mirrorctl.mjs` (`rehearse`,
`rehearse-confirm`, `rehearse-reject`, `rehearse-status`, `deploy --force`),
`src/Mirror.tsx` (deploy routes into rehearsal when unrehearsed),
`README.md`, `package.json` (test list).

**Amendment to blindspot item 5**: the majority (5/8) runs `/rehearse`
synchronously like `/forge`; step count is capped and the UI path streams
per-step events over IPC, so the long-blocking risk is CLI-only.
`GET /rehearse/status` (4/8) covers polling for long CLI runs.

**Minority ideas recorded, not built now**: gremlin adversarial scenario
suites (worst-case rehearsal); persona table-reads with per-actor sessions;
replay-vs-human episode diffing; compiled transition-table machines with
machineHash + zero-LLM deterministic replay; obligations checklists mapping
intent clauses to produced artifacts.

## The 8-strategy fan-out (decision protocol)

Eight design agents, each locked to ONE strategy — no two alike. Each returns
a structured proposal (architecture, files, state machine, confirmation UX,
control-plane surface, test cases, risks). The **majority design** is what
gets built: any element appearing in ≥5/8 proposals is in; conflicts resolved
by (1) simplicity, (2) fit with the existing Forge pipeline, (3) the
minority idea is recorded here, not built.

1. **State-machine purist** — model the process as a deterministic FSM; the twin executes transitions; simulation is table-driven, LLM only fills in world detail.
2. **Persona role-play** — the brainstem plays every actor (requester, approver, external system) as personas; the rehearsal is a scripted multi-party conversation.
3. **Test-harness lens** — every ForgeStep becomes an assertion; a rehearsal is a test run; "fully done" = green suite the user countersigns.
4. **Synthetic data plane** — generate a small virtual dataset (records, documents, inboxes) first; steps execute against that data; outcomes are diffs on the data.
5. **Replay lens** — replay what the mirror actually observed (conversation + screen OCR) as ground truth; the twin diffs the automation's behavior against the human's.
6. **Confirmation-UX-first** — design backward from the one screen where the user says "done"; build the minimum simulation that makes that screen trustworthy.
7. **Minimal-diff engineer** — smallest change that ships: extend the Forge pipeline and control plane in place; no new subsystem unless forced.
8. **Adversarial safety** — rehearse failure paths too: the twin injects edge cases (missing input, denial, ambiguity) and the user confirms behavior on nominal + worst case.

## Test cases (written before the code; the build is done when these pass)

1. Twin state machine: legal transitions only; a rejected rehearsal cannot be confirmed after the fact.
2. Simulation of an N-step spec produces exactly N step records, ordered, each with non-empty action + outcome.
3. Brainstem noise tolerance: non-JSON / malformed simulation replies degrade per-step, never crash the run (mirrors `extractJson` discipline).
4. Confirmation gate: deploy of an unrehearsed / rejected spec is refused by default; explicit override works and is recorded.
5. Rehearsal transcript round-trips to disk (`spec.rehearsal.json`) and back.
6. Control plane: `/rehearse` routes exist, are loopback-only, and return the documented shapes; unknown spec → clean error.
7. Rejection feedback loops into a revised spec (the objection text reaches the re-distill prompt).
8. Envelope: rehearsal narration renders as clean text (no leaked `|||` markers) in the step records.
9. `npm run typecheck`, `npm test`, `npm run build` all green.

## Execution steps

1. ✅ Worktree `virtual-twin`; plan committed + pushed (this doc).
2. 8-strategy fan-out → majority design → update this doc.
3. Blindspot pass (unknown unknowns end-to-end) → build-now items folded in, the rest logged below.
4. Implement majority design (engine → control plane → renderer → mirrorctl).
5. Tests until green (list above), plus typecheck + build.
6. Wow prompts (10) recorded below.
7. Merge to main, push to kody-w/rapp-mirror, verify live, hand over test instructions.

## Unknown-unknowns ledger (blindspot pass — grounded in the actual code)

**Build-now (folded into the implementation as hard requirements):**

1. **Bind confirmation to the spec's content hash** *(one-way door)*. A
   confirmation that isn't tied to exact spec bytes can be earned on spec A
   and spent on a mutated spec B. The `rehearsed` stamp must carry
   `specHash` (sha256 of the canonical spec JSON) and deploy must recompute
   and compare. Cheap now; a permanent trust hole later.
2. **Gate every deploy path at the choke point** *(silent killer of the
   feature's promise)*. Deploy runs three ways today — UI button
   (`ipc.ts forgeDeploy`), control plane (`POST /forge/deploy`), and
   `mirrorctl deploy`. A gate that lives only in the UI is theater. The gate
   belongs in `deployAgent()` itself; callers pass an explicit
   `allowUnrehearsed` override that is recorded.
3. **Harden the control plane before giving it more power** *(security)*.
   `control.ts` JSON-parses any body with no Content-Type or Origin check,
   and browsers may send cross-origin `no-cors` POSTs to 127.0.0.1 — a
   malicious web page could hit `/forge/deploy` and write a hot-loaded agent
   into the brainstem. Require `Content-Type: application/json` and reject
   requests bearing an `Origin` header before adding `/rehearse` routes.
4. **Honest-simulation framing** *(trust erosion)*. A rehearsal is a
   model-generated simulation, not an execution. The transcript must be
   labeled `simulated: true` and record engine model + app version; the
   confirm copy says what the automation *will attempt*, never that it was
   *verified*. Overclaiming here poisons the very trust the gate creates.
5. **Rehearsals take minutes — never block one HTTP request** *(erosion)*.
   Each step is a brainstem `/chat` round-trip (120s timeout each).
   `/rehearse` starts a run and returns a runId; progress is polled
   (`GET /rehearse/status`), matching the UI's streamed narration.

**Logged, not built now:**

- Rehearsal transcripts can carry business detail (screen-OCR text) —
  transcripts stay in the app's userData dir by default; only the stamp
  (`rehearsed`, `specHash`, verdict, timestamp) travels with exports.
- Version the artifact (`"rehearsal/1"`) — other RAPP surfaces will read it.
- No CI on this repo: tests exist but nothing runs them on push. Worth a
  minimal Actions workflow (typecheck + test) in a follow-up.
- `electron/main.ts` calls `ensureEngine()` twice concurrently — two grail
  installers could race on an unhealthy engine. One block should go.
- If the Rehearsal should ever be a paid tier, decide before it ships free
  in the public repo — un-shipping is a one-way door. (Kody's call.)

**Already covered (checked, solid):** loopback-only control plane binding;
brainstem secret never enters the renderer; graceful degradation ethos
throughout; model-noise tolerance (`extractJson` + strict-retry); node:test
suite pattern + typecheck; Developer ID packaging path; no telemetry.

## The 10 wow prompts

_(pending — generated last, against the finished feature)_

## Log

- Plan authored and pushed before any design or code, per the standing rule:
  the plan must outlive the session that wrote it.
- Blindspot pass folded in (ledger above); pre-fixes shipped separately:
  drive-by-proof control plane, `specHash`, single `ensureEngine`.
- 8-strategy fan-out ran (8/8 returned, 0 errors); majority tallied above.
- Majority design implemented: `electron/rehearsal.ts` (engine + registry +
  gate + revise), `electron/guard.ts`, `src/Rehearsal.tsx`, wiring across
  ipc/preload/control/mirrorctl/Mirror, README documented.
- Tests: 66/66 green (`npm test`), typecheck + production build green —
  including the full gate matrix (unrehearsed refused, confirmed deploys,
  mutated-spec hash mismatch refused, rejected stays closed, force recorded),
  fail-closed stall/error paths, envelope hygiene, and the revise loop.
