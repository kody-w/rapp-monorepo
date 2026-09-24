# First-party release pipeline specification

This is an **inert stage/gate specification**, not an implemented release
engine. `data/pipeline-gates.json` is its structured companion. The forms are
unsigned working documents; no transition, signer, grant, or observation is
supplied. A trusted host implements and authenticates the gates through its
existing RAPP/1 and RAPP Work mechanisms, not a new protocol or envelope.

```text
idea → spec → build → internal-release → dogfood → feedback
                          ↑                         │
                          └────── iterate ←─────────┤
                                                    ↓
                                              ship-decision → promote
                                                                  │
                                             ready PR → owner-merged PR
```

Feedback can recommend shipment without an invented iteration if no changes
are needed. The synthetic task DAG includes an explicit iteration assessment.
If work is needed again, create successor tasks; never force an approval merely
because the finite starter board has reached its last task.

## Stage gates

| Stage | Owner | Required evidence before entry / exit |
| --- | --- | --- |
| idea | ceo-office | Owner-scoped goal, one useful outcome, risk and effect bounds. No execution grant inferred from prose. |
| spec | product | Acceptance journeys, exclusions, failure behavior, measured budgets, approval boundaries, design review. |
| build | engineering | Reproducible local tests, source and artifact inventories, support kit, dependency/license inventory, frozen complete subject. |
| internal-release | release | Exact candidate distributed to a specifically authorized internal channel, with installation/recovery instructions and a truthful signed/unsigned label. No public effect. |
| dogfood | quality | Actual use of that candidate through the intended chat host, including error and recovery journeys; runtime, suite, timings, and observations bound to hashes. |
| feedback | ceo-office | Support synthesis and a fresh craftsmanship review: ship/iterate/stop recommendation, one focus, evidence-linked punch list. |
| iterate | product | Bounded repair plan referencing the current review. Return to build with a changed subject; re-run release, dogfood, and review. |
| ship-decision | release | Independent verification by distinct identities; CEO recommendation; cleared blocking findings; current owner policy; separate external decision linked to exact review and verification. |
| promote | release | Same candidate/projection, nested privacy scan with zero findings, license review, full applicable local tests, current required CI, exact approved public diff and PR text, and owner-only merge route. |

`promote` has two distinguishable outcomes: **PR ready for owner review** and,
only after observing the external owner action, **owner-merged PR**. Creating
a PR is not shipping. A template, seed task, or CEO recommendation never
authorizes the owner action. There is no automatic merge or extra publish stage.

## Freeze the complete subject

At build bind the raw SHA-256 of the source inventory, candidate inventory,
dependency lock (including images if used), support inventory, qualification
suite, and intended public-projection inventory. Use an explicit empty lock
artifact when there are no external dependencies, not an omitted binding.
All paths in public inventories are safe relative paths.

The public-projection inventory describes the separately reviewed outgoing
distribution, never the private organization tree. Evidence records bind this
subject without including themselves in their own hash. Bind final PR text,
verification records, and CI separately at promotion to avoid circular hashes.

Any changed subject component invalidates carried release, live-use, review,
verification, and decision qualification. Version labels alone cannot preserve
acceptance. No-change iteration assessments may reference unchanged evidence
only when all exact bindings remain current. Retain prior failures and their
dispositions; a corrected harness requires a new observed run.

## Separation of duties and chronology

1. The founder-CEO chooses focus and issues only a recommendation.
2. The trusted host verifies role holders against current native authority.
   Labels, team placement, majority votes, and request text confer none.
3. At least one independent verifier must be distinct from every builder and
   the CEO. Duplicate identities do not increase the verifier count.
4. An external decider, neither a builder nor the CEO, issues a separate
   decision after the exact verification and review. Missing or failed
   verification cannot support an approve decision.
5. Blocker and major findings must be resolved with evidence. Minor findings
   or refinements may be deferred only with an explicit reason, owner, and
   follow-up. Reclassified findings require independent review; do not erase
   them or lower severity merely to get a green gate.
6. Revalidate the decision, current owner permission, exact outgoing bytes,
   licenses, PR text, and current PR head/checks immediately before promotion.
   Failed, missing, pending, or skipped required checks block this seed's gate.
7. Only the owner performs merge. Release records the actual merged head and
   resulting artifact after checking them; it cannot fill those fields early.

Refusal yields the failed gate, accountable team, exact missing evidence, and
one bounded next action. It must not perform the prohibited effect as a fallback.

## Honest protocol and qualification claims

Use the package's pinned RAPP/1 checker for real canonical records. Successful
structural checking means **structural validity only**. It does not establish
signature validity, issuer identity, registered genesis, current grants,
profile adoption, or authenticated acceptance. A production host must prove
these separately before authority-bearing effects; unproved authority blocks.

The reference unit suite is not an internal release or chat dogfood result.
An unsigned internal distribution may be used only under explicit owner
policy and may never be described as a signed Hive release. The seed includes
no keys, authority-bearing frames, activated identity, host adapter, or runtime.
