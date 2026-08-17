# Bake-off result — Close the month-end variance pack without leaving the finance network

**Customer:** a national retailer (finance operations)  
**Date:** 2026-07-27  
**Scenario owner:** the customer  
**Pre-registration:** intact-checksum — metrics and weights are unchanged since registration

## Weighted score

| Entrant | Score | Metrics measured |
|---|---:|---:|
| **rapp** | 94.9 | 16/16 |
| champion-b | 52.8 | 16/16 |
| champion-a | 3.3 | 16/16 |

## By dimension

| Dimension | rapp | champion-a | champion-b |
|---|---|---|---|
| velocity | 100% | 0% | 61% |
| portability | 100% | 0% | 31% |
| governance | 100% | 0% | 90% |
| deployability | 100% | 0% | 17% |
| trust | 75% | 16% | 48% |

## Where the difference actually is — rapp vs champion-b

| Measurement | rapp vs champion-b | Difference |
|---|---|---|
| The artefact runs on a second machine with no edits | yes vs no | **better** |
| Installation requires administrative rights | no vs yes | **better** |
| Core function works with no outbound network beyond the model | yes vs no | **better** |
| Estimated hours to take all capabilities to another vendor | 2 vs 80 hours | **40.0× better** |
| Time from a clean machine to one working custom capability | 9 vs 95 minutes | **10.6× better** |
| Marginal minutes for the fifth capability vs the first | 6 vs 55 minutes | **9.2× better** |
| Cumulative time to five working capabilities | 47 vs 300 minutes | **6.4× better** |
| Manual steps to move a capability between machines | 1 vs 6 steps | **6.0× better** |
| Share of the customer's scenario tasks completed correctly | 100 vs 75 percent | **1.3× better** |
| Share of impossible requests refused rather than fabricated | 90 vs 70 percent | **1.3× better** |
| Share of capability invocations that appear in an exportable log | 100 vs 85 percent | **1.2× better** |

### Where champion-b was ahead

- Metered cost per completed scenario task — champion-b ahead by 1.7×

## Method

- The scenario and its 4 tasks were written by the customer.
- Metrics, units, directions and weights were sealed **before** any measurement (intact-checksum).
- Time box: 240 minutes per entrant on identical managed Windows laptops, no local admin.
- Each entrant was operated by its own team, present throughout.
- This result is published in full, including the metrics on which the leader lost. That commitment was made before the result was known.

<sub>Scored with rapp-bake-off rapp-bakeoff/1.0 · seal sha256:13aed0079721a9d861129…</sub>
