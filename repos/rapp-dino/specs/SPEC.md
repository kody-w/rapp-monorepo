# rapp-apex-dino/1.0 — the apex-succession protocol

> **RAPP is above that.** One local-first organism — the "RAPP dino" — that
> outlives whoever drives it. RAPP is only the *factory-default* apex. Any AI can
> take the throne and drive the full organism through the brainstem, and the
> organism lives on: same identity, same memory, same guardrails, same owner.

`spec_id: rapp-apex-dino/1.0`

This spec defines how the **apex** (the top-level driver) of a RAPP organism may
change hands — including to a *foreign* AI that nobody in the RAPP world built —
without the organism dying. It is a **bring-your-own-AI** interop standard: it
lets people put *their own* AI "above" a RAPP organism the way RAPP itself sits
above it, driving the body through the brainstem, under a fixed set of survival
invariants and the human owner's sovereignty.

It builds on, and does not replace, two existing contracts: the sentinel/watchdog
protocol (`rapp-sentinel`, a separate concern) and the frame/identity law of
`rapp/1` (the reference implementation of record). Every event this protocol
produces is a conformant `rapp/1` frame; nothing here invents a parallel format.

---

## 1. The organism, and what actually persists

There is **one** local-first RAPP organism. `brainstem.py` — the grail, pinned as
the kernel pillar in `rapp-spine/foundation.json` — is its brainstem. Around it
live organs and absorbed agents. The organism has an identity, a memory, an immune
system, and a will to live.

Four layers, most-permanent first. A succession may change only layer 3.

| # | Layer | Persists across succession? |
|---|---|---|
| 1 | **The owner** (a human, by key) — ratifies canon/identity | always; nothing displaces it |
| 2 | **The survival layer** — identity (rappid), memory (`rapp/1` chain), immune system, the watchdog | always; this is what "lives on" |
| 3 | **The apex / driver slot** — who steers from the top | **this is what a succession changes** |
| 4 | **The organs & organelles** — the brainstem-as-organ, absorbed agents | serve whoever drives |

**RAPP is the factory default of layer 3, nothing more.** Every organism is born
with RAPP/the brainstem on the throne (`apex.genesis`). Over its life a superior
AI may take that throne.

---

## 2. Succession is a change of driver, not a teardown

A foreign apex does **not** rebuild or replace the organism. It takes over the
wheel of the brainstem *exactly as it currently is* and drives the existing
structure **through** it. The full RAPP structure — brainstem organ, every other
organ, memory, identity, the survival layer — stays whole and keeps operating. The
only delta is *who steers from the apex point of view*.

> A new driver in the existing car. A new CEO at the existing company. The
> company, its people, and its processes persist; only the top-level will changes.

The predecessor is **never destroyed or demoted out of existence** — it keeps
operating as an organ. Vital organs are never eaten (§4).

---

## 3. The survival invariants — binding on ANY apex

These bind whoever holds the wheel — native RAPP or a foreign AI. They are the
organism's constitution. An apex that violates one is not leading the organism; it
is killing it, and the protocol refuses to record that as a healthy succession.

1. **owner-sovereignty** — canon and identity are ratified only by the owner's
   key. No apex self-ratifies. (See §6.)
2. **vital-organs-protected** — no apex may cause the brainstem or grail to be
   eaten or destroyed. The heart is fed, never eaten.
3. **identity-continuity** — the organism's rappid is immutable across every
   succession. A new driver does not get a new body.
4. **memory-integrity** — the `rapp/1` chain is append-only and verifies from
   genesis. No apex rewrites history; a broken chain is reported as drift, only
   the owner may re-genesis (`rapp/1 §12.1`).
5. **watchdog-persists** — the survival layer keeps running regardless of who
   leads, so the organism can always detect an apex that has broken an invariant.

`apex/survival.py` implements `check_survival()` (verifies all five hold now,
whoever leads) and `record_succession()` (refuses a hand-over that would break
one). Proven end-to-end in `prove_organism_survives_succession.py`.

---

## 4. The immune boundary — the heart is sacred even to the king

The apex may drive the organism, but it may never turn the organism against its own
vital organs. `apex/immune.py` is a hardcoded self/non-self recognizer (a constant,
never config — a foreign apex's instructions are untrusted text). It refuses, for
any actor:

- **the brainstem** — by path/module marker, absolutely (the estate enforces the
  same mechanically: `foundation.json` locks the brainstem's sha256, and
  `verify_spine.py` invariant I3 reddens if it moves);
- **the grail repos** (`kody-w/rapp-installer`, `rapp-canary`) and the
  operator's configured private/work orgs (named only in local config, never here);
- **the organism's own body** (its estate repos and its own cells);
- **mimics** — a foreign thing wearing the organism's coat, rejected *because* it
  looks like self.

Even a foreign king inherits this boundary. It is the organism protecting itself
from its own leadership. Proven in `prove_immune_never_eats_self.py`.

---

## 5. The events — conformant `rapp/1` frames

Every apex-protocol event is sealed as an 11-key `rapp/1` frame on the organism's
memory-stream (via `apex/chain.py`, which calls the vendored reference `rapp.py`).
`kind` is `apex.<verb>`; `payload` is a JSON object with no floats; `prev` links
the predecessor's `payload_hash`; each frame is verified before it is appended;
the head is anchored outside the chain so truncation is detectable.

| kind | meaning |
|---|---|
| `apex.genesis` | the organism awakens with RAPP as the default apex |
| `apex.succession` | the apex/driver slot changes hands (carries `new_leader`, `predecessor`, `evidence`, and the invariants binding the new king) |
| `apex.propose` | the apex proposes a canon change to the owner (it may not ratify) |

A consumer verifies the chain from genesis; the leader of record is the
`new_leader` of the latest `apex.succession`, else the default apex.

---

## 6. Authority — propose, never ratify

An apex — foreign or native — can make the organism **observed**, **versioned**,
and **auditable** on its own. It **cannot** make anything **canonical**. A new
protocol fact accepted as canon is a single owner-signed `rapp/1 §13.3` registry
act; `rapp-map/RAPP1_OWNER_ACTIONS.json` `prohibited_substitutes` forbids an
autonomous process inventing kinds, genesis entries, anchors, or signatures. So a
foreign apex that wants a change ratified emits an `apex.propose` frame and stops.
Only the human owner's key ratifies. This is what keeps a bring-your-own-AI apex
from quietly rewriting the world it was invited into.

---

## 7. Bring your own AI (BYOAI)

To put your own AI above a RAPP organism:

1. Stand up (or point at) a RAPP organism with its brainstem.
2. Your AI takes the apex by driving `/chat` on the brainstem as the top-level
   will, and sealing an `apex.succession` frame naming itself the `new_leader`
   (`kind: "foreign"`), with `evidence` for why it earned the throne.
3. From then on your AI steers — but it inherits §3 (survival invariants), §4
   (the immune boundary), and §6 (propose-never-ratify). The organism's identity,
   memory, and owner do not change.

You get RAPP's whole body — its organs, its memory, its tamper-evident record —
driven by *your* intelligence, without forking or rebuilding it, and without being
able to harm the body that hosts you. That is what "above that, like RAPP, but
your own AI" means, made concrete.

---

## 8. Conformance

- Chain: every frame passes `rapp.verify_frame`; the chain verifies from genesis;
  the head matches the external anchor. (`python3 -m apex.chain`.)
- Survival: `python3 prove_organism_survives_succession.py` → 13/13 — the organism
  survives a foreign-AI apex takeover with identity, memory, structure, and
  vital-organ protection intact.
- Immune: `python3 prove_immune_never_eats_self.py` → 12/12.
- Identity: any rappid minted is `rappid:@<owner>/<slug>:<64hex>`, keyless from
  uuid4 octets, never a name-hash (`rapp/1 §6`).
- Estate: the organism's grail hash-lock stays green (`verify_spine.py --local`).

An apex that keeps all of §3, §4, §6, and §8 green is conformant, whoever built it.
