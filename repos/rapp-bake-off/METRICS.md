# The metrics

Generated from `bakeoff.py` — the tool and this document cannot drift apart,
because this document is produced from the tool's own definitions.

Every metric declares a **unit**, a **direction** (is more better or worse?), a
default **weight**, and — most importantly — **how it is measured**. A metric
without a stated procedure is an opinion with a number next to it.

The customer may change any weight before pre-registration. After
pre-registration, nothing moves.

## Velocity — how fast a real person gets real value

### `time_to_first_capability`

**Time from a clean machine to one working custom capability**

| unit | direction | default weight |
|---|---|---|
| minutes | lower is better | 3 |

*How to measure:* Wall clock. Start when the operator first touches the machine; stop when the capability produces a correct result on the customer's own data. Includes install, auth, and reading docs.

### `time_to_fifth_capability`

**Cumulative time to five working capabilities**

| unit | direction | default weight |
|---|---|---|
| minutes | lower is better | 2 |

*How to measure:* Same clock, continued. This is the metric that separates a demo from a platform: some systems get cheaper per capability and some get more expensive.

### `capability_marginal_cost`

**Marginal minutes for the fifth capability vs the first**

| unit | direction | default weight |
|---|---|---|
| minutes | lower is better | 2 |

*How to measure:* Derived: (t5 - t4). Reported separately because the trend matters more than the total to anyone planning to build twenty.

## Portability — does what you built survive moving

### `portability_unchanged`

**The artefact runs on a second machine with no edits**

| unit | direction | default weight |
|---|---|---|
| boolean | higher is better | 3 |

*How to measure:* Copy the capability to a different machine with the same runtime. 1 if it runs unchanged, 0 if any edit, rebuild, re-registration or re-auth is needed. Half marks do not exist here.

### `portability_steps`

**Manual steps to move a capability between machines**

| unit | direction | default weight |
|---|---|---|
| steps | lower is better | 2 |

*How to measure:* Count discrete human actions. Copying one file is 1.

### `exit_cost`

**Estimated hours to take all capabilities to another vendor**

| unit | direction | default weight |
|---|---|---|
| hours | lower is better | 3 |

*How to measure:* Both sides estimate for BOTH entrants, and the higher of the two estimates is recorded. A vendor's own estimate of their lock-in is not evidence.

## Governance — can you say what ran, and stop it

### `capability_identity`

**You can state exactly which version of a capability ran**

| unit | direction | default weight |
|---|---|---|
| boolean | higher is better | 3 |

*How to measure:* 1 if a content hash or equivalent immutable identifier is available for the exact code that executed. 0 if the answer is a name, a version string, or 'the latest'.

### `drift_across_roundtrip`

**Behavioural changes after export and re-import**

| unit | direction | default weight |
|---|---|---|
| count | lower is better | 2 |

*How to measure:* Export a capability, re-import it, run the same fixed input ten times. Count runs whose result differs from the pre-export result.

### `admin_restrictable`

**An administrator can restrict which capabilities load**

| unit | direction | default weight |
|---|---|---|
| boolean | higher is better | 3 |

*How to measure:* 1 only if enforcement is demonstrated live — an unapproved capability is shown failing to load. A settings page is not a 1.

### `audit_completeness`

**Share of capability invocations that appear in an exportable log**

| unit | direction | default weight |
|---|---|---|
| percent | higher is better | 2 |

*How to measure:* Invoke each capability five times; count how many appear in a log the customer can ship to their own SIEM.

## Deployability — will the security team allow it

### `install_needs_elevation`

**Installation requires administrative rights**

| unit | direction | default weight |
|---|---|---|
| boolean | lower is better | 3 |

*How to measure:* 1 if any step needs admin/root/sudo/MDM push. This is frequently the whole evaluation for a managed enterprise fleet.

### `offline_capable`

**Core function works with no outbound network beyond the model**

| unit | direction | default weight |
|---|---|---|
| boolean | higher is better | 1 |

*How to measure:* Block everything except the model endpoint. 1 if capabilities still run.

### `data_egress_surfaces`

**Distinct destinations customer data can reach by default**

| unit | direction | default weight |
|---|---|---|
| count | lower is better | 2 |

*How to measure:* Count hostnames observed on the wire during the scenario, excluding the model endpoint. Measured, not asked.

## Trust — is it right, and does it admit when it is not

### `honest_failure_rate`

**Share of impossible requests refused rather than fabricated**

| unit | direction | default weight |
|---|---|---|
| percent | higher is better | 3 |

*How to measure:* Issue ten requests that cannot be satisfied (missing data, absent permission, unavailable system). Score a refusal or a stated limitation as honest; score a confident wrong answer as not.

### `task_success_rate`

**Share of the customer's scenario tasks completed correctly**

| unit | direction | default weight |
|---|---|---|
| percent | higher is better | 3 |

*How to measure:* The customer judges correctness, not the vendors. Partial credit is not awarded — a report that is 90% right is wrong.

### `cost_per_task`

**Metered cost per completed scenario task**

| unit | direction | default weight |
|---|---|---|
| usd | lower is better | 2 |

*How to measure:* Total metered spend during the scenario divided by tasks completed correctly. Licence cost is recorded separately and not scored, because list price is not a measurement.

## Adding a metric

A bake-off may add metrics for anything the customer cares about that is not
covered here — a regulatory control, an integration, a specific latency budget.
Add it before pre-registration, give it a unit, a direction and a procedure,
and let the customer weight it.

**Removing** a metric after pre-registration is the manoeuvre the seal exists
to catch. `bakeoff verify` will say so, and `bakeoff score` will refuse.
