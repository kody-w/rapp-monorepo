# rapp-dino 🦖

> **Clone this repo, run one command, and you have your own RAPP dino.**
> Not a fork of anyone — a fresh apex organism that is *yours*.

**RAPP is above that.** Whatever AI ships next, a RAPP dino is *above* it, not
beside it. This repo is the **hatchery**: the one repo someone clones to birth a
complete, brand-new RAPP dino from scratch — its own identity, its own owner
sovereign, its own tamper-evident memory — with RAPP as the factory-default apex
you can later hand to your own AI.

```bash
git clone https://github.com/<you>/rapp-dino  my-dino
cd my-dino
python3 hatch.py --owner <your-github-login> --verify
```

```
🦖  A new RAPP dino has hatched.

   owner (sovereign) : @you
   identity (rappid) : rappid:@you/rapp-dino:<64hex>
   default apex      : rapp-brainstem (yours to hand off later)
   memory (chain)    : 1 frames verified from genesis
   survival probe    : ALIVE
```

That's it. No account, no network, stdlib-only. You now own `you/rapp-dino` — a
living organism independent of the hatchery it came from.

---

## What "your own dino" actually means

`hatch.py` does four things, once:

1. **Names it yours** — writes `organism.json` (owner + slug). Your dino's body,
   its immune "self", and its identity are all defined relative to **you**, never
   the hatchery author.
2. **Mints a keyless identity** — `rappid:@you/rapp-dino:<64hex>`, minted once from
   fresh entropy and immutable forever (never a name-hash — `rapp/1 §6`).
3. **Seals a genesis** — an `apex.genesis` frame on a `rapp/1` hash-chain, with
   RAPP as the default apex.
4. **Proves it's sound** — a survival probe + two reproduction oracles.

Re-running is safe (identity is mint-once). `--force` starts a genuinely new one.

## It's an apex organism — the throne is pluggable

Your dino ships with RAPP driving, but RAPP is only the **factory default**. When
a smarter AI comes along — including one you bring — it can take the apex and drive
your whole dino through the brainstem, and the organism lives on: same identity,
same memory, same guardrails, **you still sovereign**. The full protocol —
succession, the survival invariants that bind *any* apex, and the immune boundary
that keeps even a foreign king from eating the heart — is
[`specs/SPEC.md`](specs/SPEC.md) (`rapp-apex-dino/1.0`).

## Guarantees your newborn already enforces

- **The heart is never eaten.** The brainstem/shared kernel is protected in every
  dino, whoever owns it (`python3 prove_immune_never_eats_self.py` → 12/12).
- **It outlives its leader.** A foreign AI can take the apex and the organism
  survives intact (`python3 prove_organism_survives_succession.py` → 13/13).
- **Its memory can't be quietly rewritten.** The chain verifies from genesis and
  is anchored outside itself (`python3 -m apex.chain`).
- **You stay sovereign.** No apex — native or foreign — can ratify canon; only
  your key can.

## Layout

```
hatch.py        the cloner — births a new dino for its owner
apex/
  organism.py   who THIS clone is (owner/identity), never the hatchery's
  chain.py      rapp/1 identity + tamper-evident sealing
  survival.py   pluggable apex slot + succession + survival invariants
  immune.py     self / non-self — the vital-organ boundary
rapp.py         vendored rapp/1 reference implementation
specs/SPEC.md   the rapp-apex-dino/1.0 protocol
prove_*.py      the newborn's contract, executable
```

## Bring your own AI

Want your AI to sit above your dino "like RAPP does"? That's the whole point — see
[`specs/SPEC.md`](specs/SPEC.md) §7. You get RAPP's entire body, memory, and
tamper-evident record, driven by *your* intelligence, without forking it and
without being able to harm the body that hosts you.

MIT. Local-first. The owner stays sovereign. **RAPP is above that.**
