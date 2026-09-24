# Craftsmanship rubric

The standard includes the "screws no one will see": the invisible work must
be as dependable as the visible result. Inspect actual behavior, not effort
or personality. Be specific and respectful.

Score each dimension `not-observed`, `0` (broken/unsafe), `1` (material gaps),
`2` (acceptance met), or `3` (acceptance met with a demonstrated refinement).
Supply exact candidate bindings, a concrete locus, method, and evidence for
every observed score. A high average cannot cancel a blocker or a missing gate.

| Dimension | Inspect | Evidence to request |
| --- | --- | --- |
| Conversation | Clear intent, concise output, unknown-command refusal, no invented progress | Real chat journeys, separate from parser fixtures |
| Interaction | Empty, loading, failure, completion, and cancellation states where applicable | Keyboard and assistive-technology observations on the actual host |
| Recovery | Duplicate requests, interrupted work, preservation of user data, recovery instructions | Repeatable fault and recovery checks |
| Quiet engineering | Determinism, bounded inputs, stable errors, no dead paths, meaningful assertions | Source loci, unit and negative cases, reproducibility hashes |
| Installation | Necessary dependencies only, explicit effects, repeat use, uninstall/reinstall boundaries | Authorized clean-environment procedure and observed results |
| Integrity | Claims, inventories, record checking, evidence freshness, role separation | Exact subject and independent findings; no fixture-as-live claim |
| Public safety | Minimal distribution, nested scanning, licenses, no private artifacts | Filename/content/archive scan and complete license review |
| Speed and simplicity | Necessary steps, latency and size budgets, absence of unnecessary services | Measured samples, environment, method, declared limitations |
| Support | Useful refusal, simple reproduction, minimum requested data | Help review and synthetic reproduction; no fictitious service level |

## Punch list

Use `templates/punch-list.json`. Each item records:

- stable ID and first-seen candidate binding;
- a relative `path:line` or an authorized internal evidence reference;
- observed behavior and expected acceptance;
- severity: `blocker`, `major`, `minor`, or `screw`;
- accountable team, verification method, disposition, and evidence references.

`blocker`: unsafe, unauthorized, unusable, or misleading essential behavior.
`major`: a required journey or acceptance criterion fails.
`minor`: nonessential roughness with a viable documented workaround.
`screw`: small unseen refinement, never a euphemism for a serious failure.

Preserve every prior item in successor reviews. `resolved` requires evidence
on the current candidate. `deferred` requires a reason and owner; blocker and
major items cannot be deferred through shipment. Do not invent findings to
justify iteration or close a finding because its file moved.

End the review with one focus and `ship`, `iterate`, or `stop`. `ship` is only
a recommendation pending independent verification, separate external decision,
public-safety gates, and owner merge. Praise must cite a demonstrated behavior.
