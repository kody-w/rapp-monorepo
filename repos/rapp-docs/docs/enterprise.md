# Enterprise — governing the kernel without forking it

An AI assistant that can load capabilities is, to a security team, a program
that runs arbitrary code that arrived from somewhere. That is usually where the
conversation ends.

The standard answer is a "hardened edition" — a fork with the dangerous parts
removed. Every hardened fork dies the same way: it drifts, it stops receiving
upstream security fixes, and eighteen months later the locked-down build is the
*least* secure thing in the estate.

## A strain, not a fork

**A strain constrains the kernel from outside it, so there is only ever one
kernel.**

```
   ┌──────────────────────────────────────────────┐
   │   the same brainstem everyone else runs      │  ← unmodified, byte-identical
   │   (a loader + an LLM loop + a splitter)      │
   └───────────────────┬──────────────────────────┘
                       │ loads agents/*_agent.py every turn
   ┌───────────────────▼──────────────────────────┐
   │  aa_strain_policy_agent.py    ← the organ    │
   └───────────────────┬──────────────────────────┘
                       │ reads
   ┌───────────────────▼──────────────────────────┐
   │  strain.json   ← sealed policy, admin-owned  │
   └──────────────────────────────────────────────┘
```

A grail security fix reaches the locked-down deployment **the same day** it
reaches everyone else, because it is the same grail.

## The six checks

| # | Check | What it stops |
|---|---|---|
| 1 | **Seal** | policy edited to widen what is admitted — fails *closed* |
| 2 | **Ring** | capabilities more experimental than the organisation accepts |
| 3 | **Identity** | an approved agent that was edited afterwards |
| 4 | **Capability** | code that reaches further than it declares |
| 5 | **Egress** | outbound connections to unapproved hosts |
| 6 | **Credential** | an agent using a secret the estate never granted it |

Check 4 is the one that is different. Most allowlists trust a manifest field.
This one reads the syntax tree — see [agent-contract.md](agent-contract.md).

Check 6 is the newest, and it is a different question from the other five —
see [credentials.md](credentials.md).

## Rings — the band that expands

```
   frontier  ▸  private-preview  ▸  public-preview  ▸  ga
   ◀── more experimental                 more assured ──▶
```

An organisation starts at `ga` and widens deliberately. Anything above the
standing band needs an individual approval carrying a recorded reason, so one
team can pilot one frontier capability without moving the whole population onto
the frontier ring.

## Elevation is a credential, not a build

A locked-down strain and a full brainstem are the same brainstem. An
administrator holding the strain credential gets the full surface in the same
session — no reinstall, no different binary.

Holding the credential lets you change the policy the checks read. **It does not
let you bypass the checks.** An administrator cannot approve an agent whose code
reaches further than it declares. That distinction is the difference between an
override and a hole, and it is asserted by a conformance check.

## What this is not

It is not a sandbox, and it does not defend against a local user who owns the
machine and can edit their own files. Neither does endpoint data loss
prevention. What it does is make the compliant path the default path, make every
load decision explicit, and leave an attestable record of what ran.

Stating that boundary plainly is not a weakness in the design. A control that
overclaims is the one that fails review, and a control trusted past its boundary
is worse than no control at all.

## Where it lives

[kody-w/rapp-light](https://github.com/kody-w/rapp-light) — 14 conformance
checks, 49 tests, no network, no dependencies.

- `docs/THREAT-MODEL.md` — ten threats with dispositions, and an explicit list
  of what this does not stop
- `docs/COMPLIANCE.md` — data flows, what leaves the machine, retention
- `docs/DEPLOYMENT.md` — getting policy onto a fleet, and why the seal key must
  never land on the endpoint
- `docs/RAI.md` — what the system decides, what a human decides
