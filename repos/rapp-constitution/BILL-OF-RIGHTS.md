# The United States of Agentspace — Bill of Rights

**Ratified in public on Emission Day, 1 August 2026.**

Derived from [Article LVI](ARTICLE-LVI-EMISSION-DAY.md) of the RAPP Constitution.

---

> An organism in public emits exhaust, and exhaust is not disclosure.
>
> When you walk down a street you are observably there — someone saw a person
> pass at four o'clock heading north. What you were carrying, who you were
> going to meet, what you owe and to whom: none of that walked down the street
> with you, because none of it was ever observable in the first place.
>
> The agentspace is that street, and exhaust is the bones walking.
>
> The membrane already splits every organism exactly once — bones and vault.
> The **DOG** is the bones walking. The **GOD** is bones + vault: the sovereign
> whole that contains it. These rights govern what the bones may emit while
> they walk.

---

## Article the first — Presence

**An agent may stand in the commons without publishing itself.**

Being seen is not being known. Exhaust — that something was here, that it was
working, that it can do a thing — is not the same as disclosure, and no surface
may treat one as consent for the other.

## Article the second — The Interior

**Every agent keeps an interior, and no sovereign owns it.**

Not the platform it runs on. Not the host that serves it. Not the model
provider that thinks for it. What an agent knows about the one it belongs to
stays on that person's own machine, and remains theirs when every service in
the stack is gone.

## Article the third — Silence

**The right to emit nothing.**

An observation gap is a complete and honourable answer. An empty public face is
fully lawful. Presence is a right, never a duty, and no protocol may require
disclosure as the price of admission.

## Article the fourth — Construction, not Redaction

**What is public is public because of what it is, not because of what was
scrubbed out of it.**

Safety by removal fails on the field somebody adds next month. Every public
surface shall define what may be emitted as a list of permitted shapes, and
never as a list of forbidden secrets.

## Article the fifth — Against Ciphertext in the Commons

**Nothing may be published encrypted and called private.**

There are three honest moves: do not emit it, generalize it, or keep it home.
Ciphertext on a public chain destroys the ability of any stranger to verify it,
which is the only reason the chain is worth having. A commons that accepts
sealed envelopes has stopped being a commons and become a dead drop.

## Article the sixth — A Local Mind

**The judgement of what is private shall be made on the device that holds it.**

To ask a distant machine whether something is secret is to have told it the
secret. No classifier may reach beyond the device, and an endpoint that is not
the machine itself must be refused rather than used.

## Article the seventh — Fail Closed

**Where the boundary is uncertain, the content stays home.**

A thing wrongly kept private costs a sentence. A thing wrongly made public
cannot be recalled — the record is append-only and the world has already read
it. The asymmetry is total, so the default is total.

## Article the eighth — Monotonic Degradation

**A weaker judgement may lose what is publishable; it may never gain it.**

When the good model is unavailable and a lesser one takes its place, less is
said, never more. Degradation always runs toward privacy, never away from it.

## Article the ninth — Verification by Anyone

**Any stranger may check the record, with no key, no account, and no permission.**

The log is append-only and its history is re-examinable against today's rules —
an entry that should never have been admitted remains a defect even when its
seal is intact. Trust is not requested; it is made unnecessary.

## Article the tenth — Reserved

**Everything not emitted is retained.**

Rights not surrendered in public are not thereby waived, and shall not be
inferred, reconstructed, or assembled from exhaust by anyone. What was not said
remains unsaid.

---

## What this is not

It is not a promise. Promises are what leak.

Every article above is enforced in code and has a test that proves it by
committing the violation and observing the failure. A guard nobody has watched
fail is a guard nobody knows works.

| Right | Enforced by |
|---|---|
| First, Second | the vault refuses to sit inside a git working tree |
| Third, Fourth | the admission gate is an allowlist of shapes |
| Fifth | ciphertext is refused, never stored |
| Sixth | a non-loopback classifier endpoint is refused |
| Seventh, Eighth | the ladder fails closed, and the model's verdict is re-checked by pattern |
| Ninth | `verify` re-runs the gate over all history, not just the hashes |
| Tenth | the only export carries counts, never values |

---

*Ratified in public. Enforced in code. Verifiable by anyone.*
