# RAPP Bake-Off

> A format for settling **"we already do that"** with a measurement instead of a
> meeting.
>
> Customer's scenario. Customer's weights. Metrics sealed before anyone starts.
> Published either way.

---

## The problem

A new capability gets built. Another team says their champion already does it.
The argument then happens in planning reviews and strategy decks — everywhere
except in front of a customer with a stopwatch running.

**The new thing loses that argument by default.** Not on merit: the incumbent
has relationships, a roadmap slide, and the benefit of the doubt. The new thing
doesn't get beaten. It gets pre-empted, before anybody measures anything.

## The move

Convert every abstract claim into a **scheduled, customer-owned, pre-registered
side-by-side**. The reply to "we already do that" is not a rebuttal:

> "That's good news — if it's true, the customer wins either way. Let's put them
> side by side on their scenario. Here's the protocol; it's public. Pick a date."

You have just agreed with them, publicly, and proposed the only thing that can
prove either of you right.

## Why a confident competitor cannot refuse

| They can | Which reads as |
|---|---|
| Accept and win | their champion really is better — good outcome |
| Accept and lose | fair measurement; now they know what to fix |
| **Refuse** | **they think they'd lose** |

There is no fourth option. **The refusal is the result** — and you never have to
say so out loud.

That only holds if the protocol is visibly fair, which is what every rule in
[`PROTOCOL.md`](PROTOCOL.md) is for: each one removes a specific excuse for
refusing, or a specific way of rigging the outcome.

---

## What it produces

```
                                               rapp  champion-a  champion-b
  --------------------------------------------------------------------------
  VELOCITY                                     100%          0%         61%
    Time from a clean machine to one wor          9         214          95
    Cumulative time to five working capa         47         690         300
  PORTABILITY                                  100%          0%         31%
    The artefact runs on a second machin          1           0           0
    Estimated hours to take capabilities          2         160          80
  GOVERNANCE                                   100%          0%         90%
  DEPLOYABILITY                                100%          0%         17%
  TRUST                                         75%         16%         48%
  ==========================================================================
  WEIGHTED SCORE                               94.9         3.3        52.8

  Leader: rapp (+42.1 points over champion-b)
```

…and a one-page card the customer takes into their own meeting, which quantifies
the gap in terms that survive being repeated second-hand:

| Measurement | rapp vs champion-b | Difference |
|---|---|---|
| Runs on a second machine with no edits | yes vs no | **better** |
| Requires administrative rights to install | no vs yes | **better** |
| Hours to take all capabilities elsewhere | 2 vs 80 | **40.0× better** |
| Time to first working capability | 9 vs 95 min | **10.6× better** |

**And, on the same page, where RAPP lost:**

> ### Where champion-b was ahead
> - Metered cost per completed scenario task — champion-b ahead by 1.7×

That section is not a concession. It is the reason the rest of the page is
believed.

---

## N entrants, not two

An entrant is a name in a list. Put RAPP beside one champion or five; the
arithmetic treats them identically and has no idea which one is RAPP.

```json
"entrants": ["rapp", "champion-a", "champion-b"]
```

The scoring tool will report RAPP losing when the measurements say it lost —
verified by swapping the result sets and confirming the leader changes. A
scoring tool that can only produce one answer is a brochure with a command-line
interface, and any reviewer spots it in a minute.

---

## The five dimensions

| Dimension | The question it answers |
|---|---|
| **velocity** | How fast does a real person get real value — and does the fifth capability cost more than the first? |
| **portability** | Does what you built survive moving? What does leaving cost? |
| **governance** | Can you state exactly what ran? Can an administrator stop it? Is there a log? |
| **deployability** | Will the security team allow it on the network at all? |
| **trust** | Does it get the work right, and does it admit when it cannot? |

Sixteen metrics, each with a unit, a direction, a weight and **a stated
measurement procedure** — see [`METRICS.md`](METRICS.md), which is generated
from the tool's own definitions so the two can never drift apart.

---

## Pre-registration is the whole trick

Every rigged evaluation is rigged the same way: **the metrics are chosen after
the results are known.** So they are fixed and sealed first.

```bash
bakeoff register scenario.json     # seals metrics, weights, tasks
# ... run it, both teams present, one clock, results entered afterwards ...
bakeoff verify   scenario.json     # intact-hmac  |  ALTERED
bakeoff score    scenario.json     # refuses outright if ALTERED
```

Entering results does **not** break the seal — that is the point. Changing a
metric, a weight or a direction does, and `score` will refuse to produce a card
from it.

**The customer holds the seal key.** A seal the scorer can recompute proves
nothing.

---

## Use it

```bash
git clone https://github.com/kody-w/rapp-bake-off
cd rapp-bake-off

python3 bakeoff.py template --out ./my-bakeoff
#  customer writes the tasks and sets the weights
python3 bakeoff.py register my-bakeoff/scenario.json

#  ... run the bake-off ...

python3 bakeoff.py score my-bakeoff/scenario.json
python3 bakeoff.py card  my-bakeoff/scenario.json --against champion-a \
                         --out my-bakeoff/RESULT-CARD.md
```

Python 3.8+, standard library only, no network. A worked three-way example is in
[`examples/`](examples/), including its
[result card](examples/RESULT-CARD.md).

---

## The standing offer

> **Bring it.** Customer's scenario, customer's metrics, customer's weights,
> sealed before we start, published either way.

Make it early, make it publicly, make it in a tone that costs nothing to accept.
Then let the calendar do the work.

---

## Licence

MIT. A project of Wildhaven Homes LLC. The protocol is deliberately
vendor-neutral — anyone may run a bake-off against RAPP using these rules, and
that is the point.
