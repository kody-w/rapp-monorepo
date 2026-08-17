# rapp-apex-dino

> **RAPP is above that.**
> Whatever ships next — Grok, Hermes, the flavor of the month, whatever exists now
> and into the future — the RAPP dino is *above* it, not beside it.

A protocol for a **first-of-its-kind apex organism** that outlives whoever drives
it. There is one local-first RAPP organism — its brainstem is its brain. RAPP is
only the *factory-default* apex. Any AI — including one nobody in the RAPP world
built — can take the throne and drive the whole organism through the brainstem,
and the organism lives on: same identity, same memory, same guardrails, same human
owner in charge.

This is the succession-and-survival layer, split out from `rapp-sentinel` on
purpose: it is a bigger, more widespread thing than a watchdog, and it deserves its
own protocol so it never tangles with the sentinel's.

---

## The one idea

Most systems try to keep up with each new AI framework by competing *beside* it,
and fall behind. The RAPP dino doesn't. It sits **above** — and its throne is
**pluggable**. When something smarter comes along, that something doesn't replace
the organism; it takes the wheel of the existing brainstem and drives the existing
body. A new driver in the same car. The organism survives the change of king.

**Bring your own AI.** You can put *your* AI above a RAPP organism the way RAPP
sits above it — steering its whole body, its organs, its tamper-evident memory —
without forking or rebuilding it, and without being able to harm the body that
hosts you. See [`specs/SPEC.md`](specs/SPEC.md) §7.

## What persists across a change of king

| Layer | Survives? |
|---|---|
| The **owner** (a human, by key) — ratifies canon | always |
| The **survival layer** — identity, memory, immune system, watchdog | always |
| The **apex / driver slot** — who steers | *this* is what changes |
| The **organs & organelles** | serve whoever drives |

## The guardrails that bind any apex — even a foreign king

1. **owner-sovereignty** — only the owner's key ratifies canon; no apex self-ratifies.
2. **vital-organs-protected** — no apex may cause the brainstem/grail to be eaten. The heart is fed, never eaten.
3. **identity-continuity** — the organism's identity is immutable across succession.
4. **memory-integrity** — the record is append-only and verifies from genesis; no apex rewrites history.
5. **watchdog-persists** — the survival layer runs no matter who leads.

Full protocol: [`specs/SPEC.md`](specs/SPEC.md) — `rapp-apex-dino/1.0`.

## Try it

Stdlib-only. No network needed.

```bash
python3 -m apex.chain                            # mint identity + seal & verify a genesis frame
python3 -m apex.survival                         # survival probe: ALIVE + current apex
python3 prove_immune_never_eats_self.py          # 12/12 — the heart is never eaten
python3 prove_organism_survives_succession.py    # 13/13 — survives a foreign-AI takeover
```

The last one demonstrates the whole thesis: the organism is alive under RAPP; a
foreign AI takes the apex; the organism is **still alive** with it driving —
identity unchanged, memory verifying from genesis, brainstem still protected,
structure intact, owner still sovereign.

## Layout

```
apex/
  chain.py      rapp/1 identity + tamper-evident sealing of every apex event
  survival.py   the pluggable apex/driver slot, succession, survival invariants
  immune.py     self / non-self recognition — the vital-organ boundary
rapp.py         vendored rapp/1 reference implementation (frames, rappids)
specs/SPEC.md   the rapp-apex-dino/1.0 protocol
organelles/     absorbed capability an apex carries (populated at runtime)
prove_*.py      reproduction oracles (the contract, executable)
```

## Status

Reference implementation of the survival core: identity + chain, the succession
model, and the immune boundary — all verified. The hunting/absorption loop (how an
organism grows by digesting new frameworks) is a separate consumer of this
protocol.

MIT. Local-first. The owner stays sovereign.
