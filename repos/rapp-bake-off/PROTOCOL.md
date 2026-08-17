# The bake-off protocol

A format for settling "we can already do that" with a measurement instead of a
meeting.

---

## 1. The situation this exists for

A capability gets built. Someone else's team says their champion already does
it. The argument happens in planning reviews, in strategy documents, in
corridors — everywhere except in front of a customer with a stopwatch running.

**A new thing loses that argument by default**, regardless of merit, because the
incumbent has relationships, a roadmap slide, and the benefit of the doubt. The
new thing gets killed before anyone measures it. Not defeated — *pre-empted*.

The protocol's whole purpose is to move the question from a room where the
incumbent wins by default into a room where the better system wins on numbers.

## 2. The one move

> **Never argue about capability in the abstract. Convert every claim into a
> scheduled, customer-owned, pre-registered side-by-side.**

The reply to "we already do that" is not a rebuttal. It is:

> "That's good news — if it's true, the customer gets what they need either way.
> Let's put them side by side on their scenario. Here's the protocol; it's
> public. Pick a date and I'll bring my half."

Nothing about this is adversarial, and that is what makes it work. You have
agreed with them, in public, and proposed the only thing that can prove either
of you right.

## 3. Why a confident competitor cannot refuse

Once the offer is on the table, the other team has three options:

| They can | Which reads to the customer as |
|---|---|
| Accept and win | their champion is genuinely better — a good outcome for everyone |
| Accept and lose | the measurement was fair; they now know what to fix |
| **Refuse** | **they believe they would lose** |

There is no fourth option, and the third is the reason the offer is made
publicly and politely. **The refusal is the result.** You never have to say so.

This only holds if the protocol is visibly fair. Every rule below exists to
remove a specific excuse for refusing, or a specific way of rigging the outcome.

## 4. The rules

### 4.1 The customer owns the scenario
The customer writes the tasks, in their own words, about their own work, using
their own data. Neither entrant sees the tasks before the day.

*Removes:* "you picked a task that suits you."

### 4.2 Metrics are pre-registered and sealed
Metrics, units, directions and weights are fixed and sealed **before anything is
measured**. The customer sets the weights — not either vendor.

```bash
bakeoff register scenario.json      # seals metrics + weights
bakeoff verify   scenario.json      # says plainly if they were edited after
```

*Removes:* "you chose the metrics once you saw the results." This is the single
most common way an evaluation is rigged, and the only one that is invisible
afterwards without a seal.

### 4.3 The customer holds the seal key
Not either vendor. A seal that the scorer can recompute proves nothing.

### 4.4 Each entrant is operated by its own team
Nobody demonstrates their competitor's product. An entrant operated by an
opponent has not been measured; it has been sabotaged, and everyone knows it.

*Removes:* "your people didn't know how to drive ours."

### 4.5 Identical hardware, identical time box
Same machine spec, same permissions posture, same clock. If the customer's
fleet has no local admin rights, **neither entrant gets local admin rights** —
that constraint is part of the scenario, not an unfair handicap.

### 4.6 The clock starts at a clean machine
Not at "once it's installed". Installation, authentication and reading the
documentation are part of time-to-value, because they are part of the
customer's experience.

*Removes:* the most common quiet advantage of an incumbent — being already
deployed.

### 4.7 The result is published in full, whoever wins
Committed **in writing, before the result is known**, including every metric on
which your own entrant lost.

*Removes:* "you'd only publish this if you won." It is also the clause that
makes the offer credible enough to be accepted.

### 4.8 No partial credit
A report that is 90% correct is incorrect. Booleans are booleans. This protects
the losing entrant as much as the winning one, because it stops "well, it nearly
worked" from doing the work of a result.

### 4.9 Ratios, not just ranks
"We came first" survives one round of argument. "9 minutes against 214, and the
artefact ran unchanged on the second machine" survives the meeting.

### 4.10 Losing is a legitimate outcome, and a useful one
A lost bake-off returns a prioritised, quantified defect list from a real
customer scenario. That is worth more than the meeting you would otherwise have
had. **A team that cannot afford to lose a bake-off cannot afford to run one,
and should fix that rather than avoid the format.**

## 5. Tone

Published material says **"champion"**, never anything pejorative. The neutrality
is not politeness for its own sake — it is what makes the card usable by the
customer inside their own organisation, and what makes a refusal look like a
refusal rather than a reasonable response to an attack.

Internally you may feel whatever you like. On the page, the numbers carry it.

## 6. What gets measured

Sixteen standard metrics in five dimensions, defined in
[`METRICS.md`](METRICS.md) with the exact procedure for each:

| Dimension | Question it answers |
|---|---|
| **velocity** | How fast does a real person get real value — and does the second capability cost more than the first? |
| **portability** | Does what you built survive moving? What does leaving cost? |
| **governance** | Can you say what ran? Can an administrator stop it? Is there a log? |
| **deployability** | Will the security team allow it on the network at all? |
| **trust** | Does it get the work right, and does it admit when it cannot? |

A bake-off may **add** metrics. Removing one after pre-registration is the
manoeuvre the seal exists to catch.

## 7. Running one

```bash
bakeoff template --out ./my-bakeoff       # blank scenario
# customer writes tasks and sets weights
bakeoff register  my-bakeoff/scenario.json
# ... run the bake-off, both teams present, one clock ...
# ... enter measurements into "results" ...
bakeoff verify    my-bakeoff/scenario.json
bakeoff score     my-bakeoff/scenario.json
bakeoff card      my-bakeoff/scenario.json --against champion-a \
                  --out my-bakeoff/RESULT-CARD.md
```

`score` refuses to run against an altered pre-registration. That refusal is a
feature; it is what the customer is relying on.

## 8. The standing offer

The default answer to any claim that something already does what RAPP does:

> **Bring it. Customer's scenario, customer's metrics, customer's weights,
> sealed before we start, published either way.**

Make the offer early, make it publicly, and make it in a tone that costs nothing
to accept. Then let the calendar do the work.
