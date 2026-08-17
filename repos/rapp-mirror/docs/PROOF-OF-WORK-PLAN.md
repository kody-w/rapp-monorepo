# Proof of Work — the mirror must prove what it did

**The majority verdict of eight strategists.** Eight independent analyses, each
forced down a different lens (cold-start funnel, adversarial reliability, job
completion, distribution, threat model, self-debuggability, differentiation,
code entropy), named eight different primary problems. Their *solutions*
converged on one thing.

| Capability the solution requires | Strategists |
| --- | ---: |
| E2E harness that drives the **real running app** (mirrorctl + CDP + fake brainstem) | **6 / 8** |
| Structured honest results — never claim success unproven | **5 / 8** |
| A `doctor` an agent can read | **4 / 8** |
| Durable local diagnostics/event ledger | **4 / 8** |
| Verify a deploy by *invoking* it, not by trusting `/health` | **3 / 8** |
| Atomic deploy + rollback | **2 / 8** |
| — split Mirror.tsx / notarized release / control-plane auth token / automation library | 1 each |

The single-vote items are the minority *and* the most expensive; they are
deferred. The majority is one coherent spine:

> **The mirror claims success it has not earned — at install, at deploy, and
> inside the forged automation itself — and nobody, human or agent, can prove
> otherwise from the machine alone.**

Three places it happens today, all confirmed by running the real app:

1. **The forged automation.** `perform()` returns `"status": "success"` with a
   list of steps it did not take. Deployed, invoked live, it answers
   *"success"* for work nobody did.
2. **The deploy.** `writeFileSync(file, renderAgentPy(spec))` writes straight
   into the live hot-load path — no temp file, no backup, no rollback — then
   calls the deploy `ok` if `/health` merely *lists the class name*.
3. **The install.** The default installer URL answers `410 Gone`; the app has
   no single command that says so.

And underneath all three: `createLogger` is `console.log`, so when any of it
goes wrong there is no durable evidence anywhere on the machine.

## The build

| # | Change | Files |
| --- | --- | --- |
| 1 | **Diagnostics ledger** — monotonic seq, in-memory ring, redacted JSONL on disk, rotation | `electron/diagnostics.ts` |
| 2 | **Every log line becomes evidence** — `createLogger` tees into the ledger | `electron/logger.ts` |
| 3 | **`doctor`** — one honest verdict per subsystem with a `nextAction`, and explicit tombstone detection for the withdrawn installer | `electron/doctor.ts` |
| 4 | **Atomic, reversible deploy** — tmp + fsync + rename, backup, rollback on failed health or quarantine | `electron/forge.ts` |
| 5 | **Verified deploy** — actually execute the artifact and require parseable JSON out of it before reporting success | `electron/forge.ts` |
| 6 | **Honest artifact** — the generated agent reports `status: "procedure"`, `executed: false` | `electron/forge.ts` |
| 7 | **Agent-readable surfaces** — `GET /doctor /diagnostics /events?since=` | `electron/control.ts` |
| 8 | **`mirrorctl doctor \| events \| diagnostics`** | `bin/mirrorctl.mjs` |
| 9 | **E2E over the real app** — fake brainstem + CDP driver + a test that boots the app and drives it through its own tooling | `test/e2e/**` |

## The rule this encodes

Nothing in the mirror may report success it has not verified. Where it cannot
verify, it says so — with the reason and the next action.

## Verification

`npm test` (unit, fast) · `npm run test:e2e` (boots the real app, drives it
through mirrorctl **and** `window.mirrorDebug`, asserts real outcomes) ·
`npm run typecheck` · `npm run build`.
