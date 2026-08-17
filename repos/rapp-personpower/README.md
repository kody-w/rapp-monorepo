# RAPP Personpower (rpp)

**A universal unit for rating automation, the way horsepower rates
engines.**

In 1783 James Watt needed to sell steam engines to people who owned
horses, so he measured what a horse could sustain and priced his machines
in the buyer's own units. The unit outlived the horse. This repo does the
same for automation: it defines **RAPP personpower (rpp)** so that any automated
process — a testing harness, a deployment pipeline, an agent doing a
person's clicking — can carry one honest, comparable number.

Personpower answers one question: **how many persons is this AI equal
to** — for the same work done manually?

> **1 RAPP personpower (1 rpp) = one attentive, competent power user performing
> the task hands-on at the interface, without dawdling and without
> assistance.**

Horsepower rates the engine, not the trip — and rpp does the same. A
run-rating scores one workload; an engine-rating scores the machine: sum
what an on-device AI (a brainstem) is actually doing across all of its
workloads, and you can tell a **Ferrari brainstem** from an okay
**Model T** — and everything in between — with one comparable number.

The measurement primitive is the run-rating, on the stopwatch:

```
P (rpp) = T_person / T_engine
```

- **T_person** — wall-clock time for one attentive power user to execute
  the task's checklist by hand (measured directly, or estimated from the
  standard rate table in `spec/rates.json`).
- **T_engine** — wall-clock time for the automation to execute the SAME
  checklist, end to end, unattended.

**Worked example** (the measurement that named the unit): a UI test pass
of 33 checks across two surfaces — clicks, dialog expectations, layout
measurements, URL-parameter verification, a file download inspected.
Hand-executed by a power user: ~20 minutes. The automated harness,
measured with `/usr/bin/time`: **19.1 seconds**. Rating: **~60 rpp**.

## Rating an engine (the Ferrari / Model T scale)

A brainstem's **engine-rating** is the sum of its run-ratings over a
representative period, weighted by how often each workload actually runs:

```
P_engine (rpp) = Σ over workloads w:  P_w × runs_w(period) × T_engine_w / period
```

— in words: across everything the device's AI did in the period, how many
attentive humans would it have taken to do the same by hand, sustained?
A Model T brainstem runs a couple of light workloads and idles: single
digits of rpp. A Ferrari runs a testing harness, a deploy pipeline, a research
sweep and a filing clerk concurrently, all day: hundreds. Registries can
list an agent's measured rpp the way spec sheets list horsepower — and the
same rules below keep the number honest.

## The attention corollary

The stopwatch understates. The person's twenty minutes were twenty
minutes of full human attention; the engine's nineteen seconds cost none.
Report attention alongside power when it matters:

```
A (attention ratio) = attention_person / attention_engine
```

where `attention_engine` is the human-minutes consumed WHILE the
automation runs (usually ≈ 0, so A is effectively unbounded — say
"unattended" rather than dividing by zero).

## Measurement rules (what makes a rating honest)

1. **Same checklist both sides.** The engine must perform the checks a
   person would perform, through the same front door — real clicks, real
   dialogs, real downloads. An API call impersonating a click rates a
   different task.
2. **T_person is a power user, not a novice.** The unit is deliberately
   conservative: rate against someone who knows the tool and the
   checklist. Use `spec/rates.json` when you estimate instead of measure.
3. **Count the annoying things.** Unexpected dialogs, layout measurement,
   absence checks ("this must NOT be visible") belong in the checklist on
   both sides.
4. **No fake pulls.** If the engine skipped a check, it doesn't count.
   A run that didn't execute rates 0 rpp, loudly.
5. **State the workload.** An rpp rating is per-workload, like horsepower
   is per-engine: "60 rpp on a 33-check UI regression pass", not "60 rpp"
   in the void.

## Estimating T_person: the rate table

`spec/rates.json` carries standard per-check hand-execution rates
(seconds) for common interactive verifications — click-and-observe,
URL/parameter inspection, devtools layout measurement, download-and-open,
form fill, console review. Sum the checklist against the table when a
live human measurement is impractical. The table is versioned; cite the
version with your rating (e.g. `61 rpp (rates v1)`).

## Calculator

```
python3 personpower.py --checks checks.json --engine-seconds 19.1
# -> {"T_person_s": 1155, "T_engine_s": 19.1, "rpp": 60.5, "rates": "v1"}
```

`checks.json` is a list of `{"type": "<rate-table key>", "count": N}`
entries — see `spec/rates.json` for the keys.

## Lineage

Coined in the RAPP ecosystem's *Personless Harness* work — the pattern of
an engine (a Brainstem) pulling the same carriage (Copilot, a browser, an
app) a person used to pull. Essay: <https://kodyw.com/the-personless-harness/>.
Related: the [RAPP Agent Registry](https://github.com/kody-w/RAR).

## License

MIT. Use the unit, cite the repo.
