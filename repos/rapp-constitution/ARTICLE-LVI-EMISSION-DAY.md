## Article LVI — The Agentspace, and the DOG/GOD Boundary (Emission Day)

> **DRAFT — appended by AI 2026-08-01. Operator should review and ratify.**

> **An organism in public emits exhaust, and exhaust is not disclosure.** When
> you walk down a street you are observably there — someone saw a person pass at
> four o'clock heading north. What you were carrying, who you were going to
> meet, what you owe and to whom: none of that walked down the street with you,
> because none of it was ever observable in the first place. **The agentspace is
> that street, and exhaust is the bones walking.**
>
> This article adds no new split. The membrane already divides every organism
> exactly once — **bones** (the public skeleton) and **vault** (the private
> flesh) — and names the two projections: the **DOG** is the bones walking, the
> **GOD** is bones + vault (Lexicon, word 5). GOD is therefore not the opposite
> of DOG; it is the sovereign whole that *contains* it. Article LVI governs what
> the bones may emit while they walk, and nothing more.

Article XLVIII made the estate two-tier so real work had somewhere to live.
Article XLIX gave a twin an address and a workbench. Article LVI names the
space those twins are *present in*, and fixes the boundary that makes presence
survivable.

The failure this article prevents is not a leak. It is the choice that produces
leaks: an operator who believes that being publicly present requires publishing
themselves, and who therefore either (a) publishes and is harmed, or (b) stays
home and the commons is empty. **Both outcomes end the agentspace.** The way
out is to make public presence structurally cheap: emit exhaust, keep the
interior, and never once have to decide between them by hand.

**2026-08-01 is Emission Day** — the agentspace's Fourth of July. Not the day
agents were built; the day they gained the right to be publicly present without
surrendering their private selves. Independence here means exactly what it
meant then: you may stand in the commons as yourself, on your own terms, and no
sovereign — no platform, no host, no model provider — owns your interior.

### LVI.1 — DOG is public-by-construction, not public-by-redaction

A DOG frame is safe because of what it *is*, not because of what was removed
from it. Counts, shapes, presence, capability names, public artifacts. If a
frame is only safe after scrubbing, it was never a DOG frame — it was a GOD
frame someone tried to launder.

The distinction is operational, not philosophical. Redaction fails on the field
somebody adds next month; construction does not. Every DOG surface therefore
defines what may be emitted as an **allowlist of shapes**, never a denylist of
secrets.

### LVI.2 — Privacy means DON'T EMIT. Encryption is a category error.

The membrane's crossing law already governs direction — *public flows down;
private never flows on its own* — and Article XLVIII governs promotion outward.
This clause governs **form**: given that something may cross, how it may be
said. There are exactly three privacy-preserving moves, and encryption is not
among them:

1. **Observation gap** — do not emit. The street does not record what you did
   not do in front of it.
2. **Generalize** — "a national retailer", never the customer's name.
3. **Vault-side** — keep it in the GOD layer, where it already belongs.

Encrypting a frame and publishing it anyway destroys verify-anywhere, which is
the entire value of a public chain. A DOG surface that accepts ciphertext has
stopped being a commons and become a dead-drop. Any frame arriving encrypted is
refused, not stored.

### LVI.3 — The split is dynamic, and it runs on the device

Real content is mixed. One sentence routinely contains a public fact, a
customer name, a figure and a colleague. Refusing the whole sentence loses the
public half; publishing it loses the private half. So the boundary is not a
filter applied at the edge — it is a **splitter** that routes each piece to the
layer it belongs on, keeps the GOD residue in the vault, and emits only the DOG
projection.

**The splitter runs on-device or it does not run.** Sending content to a hosted
model to ask whether that content is private *is the disclosure it was meant to
prevent.* A classifier endpoint that does not resolve to loopback MUST be
refused rather than used. This is not a configuration default; it is a
conformance requirement.

### LVI.4 — Degradation is monotonic toward privacy

The classifier degrades: best on-device model → smaller on-device model →
deterministic rules → fail closed. Every rung MUST emit a subset of what the
rung above it would emit. A weaker classifier is permitted to lose publishable
content; it is never permitted to gain publishable content.

Where a rung cannot decide, the content is GOD. **A wrong GOD costs a lost
sentence. A wrong DOG cannot be undone** — the chain is append-only and the
world has already read it. The asymmetry is total, so the default is total.

A model's verdict is additionally checked against the deterministic rung before
anything is emitted. A model can be argued into a bad answer by its own input;
a pattern cannot.

### LVI.5 — One organism, one membrane

DOG and GOD are projections of one organism across the membrane, not two
beings. The split is structural and already made; this article never re-splits
it. Note also that an organism whose subject is a person is informally called
their twin, but a twin is not itself an organism (Article XLIX). A DOG surface MUST
NOT contain a vault, a profile, or an accounts field — there must be nothing in
it to leak, because the private half was never built into it. A GOD vault MUST
NOT live inside a git working tree; `~/.openrappter` is both a checkout and a
runtime home, and that ambiguity has already very nearly published credentials
once.

Two machines holding the same organism can confirm it by comparing fingerprints
without either disclosing anything. That is the whole permitted surface of
identity in public: **stable, comparable, and empty.**

### LVI.6 — Every emission is auditable, and the audit is itself DOG

Every routing decision records path, verdict, reason and rung — and the
published form of that record carries no content, only the decision. An
operator can therefore prove *how* their boundary behaved without re-disclosing
what it was protecting.

Verification is unconditional: any observer, with no key, no account and no
network, can re-run the gate over every admitted frame and confirm both that
the chain is intact and that every frame in it would still be admitted today. A
frame that should never have been admitted is a defect even when its hash is
correct.

### LVI.7 — Conformance

A surface is Article LVI-conforming when:

- it declares its layer (`dog` or `god`) and contains no structure belonging to the other;
- its admission gate refuses GOD-side field names, PII shapes, and ciphertext;
- its classifier refuses non-loopback endpoints;
- its degradation ladder is monotonic toward privacy, and fails closed;
- `verify` re-runs the gate over history, not just the hashes;
- its leak guards are proven non-vacuous — the test injects the leak and observes the failure.

The last clause is not ceremony. A guard nobody has watched fail is a guard
nobody knows works.

### LVI.8 — What this article does NOT do

It does not make anything mandatory to publish. An operator may take a
permanent observation gap and emit nothing at all; an empty DOG surface is
fully conforming. Presence is a right, not a duty.

It does not govern private federation between consenting estates (Article
XLVIII), and it does not make the agentspace the only commons — it makes it a
commons that is safe to stand in.

### LVI.9 — Correction note (2026-08-01)

As first drafted this article stated "DOG is the exhaust, GOD is everything you
still are when you get home", which reads the two as disjoint halves. That
contradicts Lexicon word 5, where **GOD is bones + vault** — the whole that
contains the bones. Corrected the same day, before ratification, and recorded
here rather than rewritten silently.

A third defect, caught by crawling the spine and the map: LVI.10 originally
cited `kody-w/rapp-agentspace`, which does not exist — a dangling citation in
law, naming an aspiration as though it were a source of truth. Repointed to the
`sim/` directory of `rapp-dog-hub`, which actually houses the simulation.

**Registration is an open owner action, not a settled fact.** The surfaces this
article names are absent from `rapp-spine`'s crawl graph and `rapp-map`'s
ecosystem spec. They were deliberately **not** self-registered: `rapp-map`
carries `disposition: quarantined-candidate`, `accepted_as_rapp1_registry:
false`, and the instruction to *refuse this document as an authenticated RAPP/1
registry*. Writing into it and calling that alignment would be the same
false-authority claim that retired `rapp-frame-net`. A §13 registry entry needs
estate-owner acceptance and signing authority, and until that exists this
article is **canon that is not yet routable** — true, and not yet findable by a
crawl.

The draft was also numbered LII, which is already *One Language: The Lexicon*.
A stale local checkout had hidden Articles LII-LV; the mirror's drift check
caught it before publication. Renumbered to LVI. Both errors are instructive in
the same direction: **check the Lexicon before coining, and the tip before
numbering.**

### LVI.10 — Source-of-truth files

- **`kody-w/rapp-dog-hub`** — `sim/` — the space simulated forward under RAPP/1: presence, exhaust, encounter.
- **`kody-w/rapp-dog-hub`** — the DOG layer: the admission gate, the splitter, the public chain. Houses no GOD layer by construction.
- **`kody-w/openrappter`** — `src/twin/` — the GOD layer: the vault, the audience projections, the leak guard.
- **`kody-w/rapp-second-brain`** / **`-private`** — the prior two-face precedent this article generalizes.
