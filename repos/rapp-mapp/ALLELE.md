# rapp-allele/1.0 — heritable variation for organisms

> **Draft.** Vocabulary follows the Lexicon: an **organism** is a planted being
> (word 3), its identity is a **rappid** (word 4). An **allele** is a variant
> form of a heritable trait — the genetics word, for the being that already has
> a biology.

## The one-line version

> **Alleles are to this ecosystem what pets are to Adopt Me.**

That is the whole product framing. Adopt Me is not really a game about a house;
it is a game about the pet you got, how rare it turned out, and the fact that
everyone can see it. The pet is the unit of attachment, the unit of identity,
and the unit of conversation.

The allele is that unit here. Not the organism — an organism is a being, and
beings are not inventory. Not the repo, not the twin, not the frame. **The
allele is the thing you got, the thing you show, and the thing you did not
choose.**

Everything below is downstream of taking that seriously.

## The pattern being borrowed

Adopt Me works because a pet is **yours specifically**: it hatched a certain
way, it is a certain rarity, four of a kind fuse into something else, and every
trade is priced by scarcity everyone can see. Rarity creates attachment;
attachment creates a culture.

## The tension that makes a naive copy fail

Adopt Me's rarity is **server-authoritative**. A server rolls the dice, records
the result, and is trusted because it is the only writer.

RAPP has no server. It is local-first and content-addressed, so anyone can
write anything into their own files. A rarity tier stored as a *field* —
`{"rarity": "legendary"}` — is worth nothing: I can type that. Any design where
rareness is **asserted** is a design where rareness is **free**, and a currency
that is free to mint is not a currency.

## The move: rarity is a property of the identity, not a claim about it

A rappid's 64-hex tail is minted exactly once, per RAPP/1 §6.2, from UUIDv4
octets or a public key — and then it is immutable. It cannot be re-rolled
(§6.2 forbids re-minting; the one exception is an owner-authorized re-anchor).

So: **derive the allele from the tail.** Nobody assigns it, nobody can fake it,
and anyone can verify it offline with a hash function and no network.

```
allele(trait, rappid) = first bits of H("rapp/1:allele:" + trait, rappid_tail)
```

Domain-separated per §5, so the allele space cannot collide with the particle,
wave, egg or rappid spaces.

This inverts the Adopt Me trust model and keeps the mechanic:

| | Adopt Me | rapp-allele |
|---|---|---|
| who decides rarity | the server | the hash |
| can the owner fake it | no (server) | no (mint-once) |
| can anyone verify | no (trust the server) | yes, offline, no keys |
| what makes it scarce | drop tables | the cost of minting until you get one |

Rarity becomes **honest work**: to get a rare allele you mint identities until
one lands, exactly like a vanity address. The scarcity is real because the
electricity was real.

## The allele is the collectible

The trait is the *slot*; the **allele is the thing you have**. You do not collect
organisms — an organism is a being, and beings are not inventory. You collect
the alleles your organisms turned out to carry.

That reading is what makes the whole design hold together:

- an allele is **had, never traded** — it is a property of an identity, and
  identity is mint-once (§6.2), so it cannot be detached and sold
- two organisms may carry the **same allele**, and that is a real relation
  between them — a kinship you can verify without either one disclosing anything
- a collection is a **set of alleles across your planted organisms**, which grows
  by planting, not by buying
- rarity is a fact about the allele, not a rank of its owner

So the sentence is *"I have a mythic glow"*, not *"my organism is mythic"*. The
organism is not the prize. The allele is.

## Traits

Each trait reads a different slice of the tail, so they are independent:

| trait | what it colours | slice |
|---|---|---|
| `coat` | how the organism presents | bits 0–7 |
| `tempo` | how eagerly it acts | bits 8–15 |
| `voice` | its register | bits 16–23 |
| `glow` | the rare cosmetic | bits 24–39 |

Tiers are cumulative-probability bands, so the distribution is fixed by the
spec rather than by whoever is running the code:

| tier | band (exclusive) | odds | measured over 20k mints |
|---|---|---:|---:|
| common | `< 0xC000` | 3 in 4 | 73.9% |
| uncommon | `0xC000 – 0xEFFF` | ~1 in 5 | 19.4% |
| rare | `0xF000 – 0xFEFF` | ~1 in 17 | 6.3% |
| ultra | `0xFF00 – 0xFFFE` | ~1 in 257 | 0.4% |
| mythic | `== 0xFFFF` | 1 in 65,536 | 0 |

The bands are exclusive, so the odds are the band widths — not cumulative
thresholds. An earlier draft of this table quoted cumulative odds against
exclusive bands and disagreed with its own reference implementation; the
measured column exists so that can never silently drift again.

## Inheritance

An organism planted from another (Art. `parent_rappid` provenance) is a **new
mint** — its tail is fresh, so its alleles are fresh. Lineage is recorded, not
inherited numerically. This is deliberate: heritable-by-copy would let one lucky
mint be cloned into infinite rare children, and the scarcity would evaporate in
a day.

What *is* inherited is **descent** — the chain of who planted whom, already
carried by `_migrated_from` / `parent_rappid`. A common organism with a mythic
ancestor is a real and interesting thing to be.

## Fusion (the Neon mechanic), stated honestly

Adopt Me fuses four identical pets into a Neon. The RAPP analogue is an
**attestation**, not a new organism: four organisms whose owners co-sign a
statement that they share a trait. It needs §10 signatures and estate-owner
authority, so it is **specified but not implemented here** — claiming it works
before signing exists would be the same false-authority defect that retired
`rapp-frame-net`.

## What this must never become

- **Not a token.** No transfer, no balance, no price. An allele is a property of
  an identity, and identity is not transferable (§6.2 mint-once).
- **Not a gate.** An allele never affects what an organism may *do*. Capability
  comes from the mandate (Art. LVI), never from cosmetics. A mythic coat buys
  you nothing but a mythic coat.
- **Not private.** Alleles are computed from the public tail, so they are pure
  DOG — bones-side by construction, nothing to leak.

## Verifying one

```python
import hashlib
def allele(trait, tail, bits=16):
    h = hashlib.sha256(f"rapp/1:allele:{trait}\n{tail}".encode()).hexdigest()
    return int(h[:bits // 4], 16)
```

Same input, same answer, on any machine, forever. That is the whole design.
