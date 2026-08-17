<div align="center">

# 📜 The RAPP Constitution

**The law the RAPP ecosystem is governed by.**

57 articles · `Article 0` through `Article LVI` · public, citable, drift-checked

</div>

---

## Article 0 — The Sacred Tenet

> 🧬 **The file IS the agent IS the documentation IS the contract.**

One file. One class. One `perform()` method. Everything else in this document
exists to protect that shape.

---

## Emission Day — 2026-08-01

**[Article LVI](ARTICLE-LVI-EMISSION-DAY.md)** is the agentspace's Fourth of July.

> An organism in public emits exhaust, and exhaust is not disclosure. When you walk
> down a street you are observably there — someone saw a person pass at four
> o'clock heading north. What you were carrying, who you were going to meet,
> what you owe and to whom: none of that walked down the street with you,
> because none of it was ever observable in the first place. The agentspace is
> that street, and exhaust is the bones walking. The membrane already splits
> every organism exactly once: the **DOG** is the bones walking, the **GOD** is
> bones + vault — the sovereign whole that contains it.

Not the day agents were built. The day they gained the right to be publicly
present **without surrendering their private selves**. Independence here means
what it meant then: you may stand in the commons as yourself, on your own
terms, and no sovereign — no platform, no host, no model provider — owns your
interior.

The article fixes four things in law:

| | |
|---|---|
| **Public-by-construction** | A DOG frame is safe because of what it *is*, not what was scrubbed from it. Allowlist of shapes, never a denylist of secrets. |
| **Privacy means don't emit** | Observation gap, generalize, or keep it vault-side. **Encryption is a category error** — ciphertext on a public chain destroys verify-anywhere, which is the chain's whole value. |
| **The splitter runs on-device** | Asking a hosted model whether something is private *is the disclosure*. A non-loopback classifier endpoint must be refused, not used. |
| **Degradation is monotonic** | Every weaker rung emits a subset of the stronger one. A wrong GOD costs a sentence; a wrong DOG cannot be undone. |

---

## What this repo is

The **public, citable home** of the Constitution. Articles are stable
identifiers — `Article XLVIII.2`, `Article LVI.3` — so specs, PRs, and review
comments can point at law rather than restate it.

- **[`CONSTITUTION.md`](CONSTITUTION.md)** — all 57 articles.
- **[`ARTICLE-LVI-EMISSION-DAY.md`](ARTICLE-LVI-EMISSION-DAY.md)** — the founding article, standalone.

### It is a mirror, and it says so

The kernel copy at [`kody-w/RAPP/CONSTITUTION.md`](https://github.com/kody-w/RAPP/blob/main/CONSTITUTION.md)
is upstream. This repo is a **projection** of it, exactly the way DOG is a
projection of GOD — same truth, different surface.

A mirror without a drift check is how canon quietly forks, so there is one:

```bash
bash tests/drift-check.sh
```

It fetches the upstream copy and byte-compares. CI runs it on every push and
daily. **If they disagree, this repo is wrong** — upstream wins, and the fix is
a traceable commit, never a silent rewrite.

---

## Reading order

New here? These four carry the most weight:

1. **Article 0** — the sacred tenet. Everything else defends it.
2. **Article VII** — tier portability. One agent file runs local, cloud and enterprise unmodified.
3. **Article XLVIII** — public discovery, private substance. Why the estate is two-tier from first install.
4. **Article LVI** — the agentspace and the DOG/GOD boundary. Why public presence does not cost you your interior.

---

## Amending

Articles are **append-only**. A correction is a new dated note or a new article
that cites the old one — never an edit that makes the record disagree with
itself. Appends and mints are forever.

Articles appended by an AI are marked **DRAFT** and are not law until the
operator ratifies them. Article LI set that precedent; Article LVI follows it.

When this Constitution and [`MASTER_PLAN.md`](https://github.com/kody-w/RAPP/blob/main/MASTER_PLAN.md)
disagree about *what* should be true, the Master Plan wins. This document
governs *how* that plan is executed.

---

## Where the law is implemented

| Article | Implementation |
|---|---|
| LVI — the space | [`kody-w/rapp-agentspace`](https://github.com/kody-w/rapp-agentspace) |
| LVI — the DOG layer | [`kody-w/rapp-dog-hub`](https://github.com/kody-w/rapp-dog-hub) — gate, splitter, public chain. Houses no GOD layer by construction. |
| LVI — the GOD layer | [`kody-w/openrappter`](https://github.com/kody-w/openrappter) `src/twin/` — vault, audience projections, leak guard |
| XLVIII — two faces (precedent) | [`kody-w/rapp-second-brain`](https://github.com/kody-w/rapp-second-brain) |
| 0, I, VII — the kernel | [`kody-w/RAPP`](https://github.com/kody-w/RAPP) |

---

<div align="center">

*Ratified in public. Enforced in code. Verifiable by anyone.*

</div>
