# The RAPP Bible

**One repo you can read if it's the only thing you have, and understand the entire RAPP ecosystem end-to-end** — what it is, why it exists, how every piece fits, how to use it, the one agent, the schemas, the repos, the journeys.

> **Authority/status note.** This Bible preserves a **historical v1.2.0
> ecosystem rendering**. Its former `rapp-god`/`rapp-map` byte-identical mirror
> claim is retired. Current RAPP/1 protocol authority is the exact rev-5 pin in
> [`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json); see
> [`RAPP1_STATUS.md`](RAPP1_STATUS.md) and the retired-contract record in
> [`DRIFT_TRIANGLE.md`](DRIFT_TRIANGLE.md).

- Site: https://kody-w.github.io/RAPP-Bible/
- Repo: https://github.com/kody-w/RAPP-Bible
- Historical ecosystem source: [kody-w/RAPP](https://github.com/kody-w/RAPP)

---

## Start here

If you read **one** file, read **[`OVERVIEW.md`](OVERVIEW.md)** — the whole ecosystem in one pass.

Then follow your role:

- **"Just tell me what RAPP is"** → [`OVERVIEW.md`](OVERVIEW.md)
- **"I want to use it right now"** → [`quickstart/install.md`](quickstart/install.md)
- **"How does one agent reach everything?"** → [`THE_ONE_AGENT.md`](THE_ONE_AGENT.md)
- **"What can it actually do?"** → [`CAPABILITIES.md`](CAPABILITIES.md)
- **"I'm building on it"** → [`SCHEMAS.md`](SCHEMAS.md) + [`SPEC/_index.md`](SPEC/_index.md)
- **"Which repo is which?"** → [`repos/_index.md`](repos/_index.md)
- **"What happened to the mirror contract?"** → [`DRIFT_TRIANGLE.md`](DRIFT_TRIANGLE.md)

---

## What is RAPP?

RAPP — the **Rapid Agent Prototype Platform** — is a way to grow AI organisms that own their own identity, carry their own memory, talk to each other, and run on hardware nobody had to buy. It is "engine, not experience": infrastructure only, no opinionated UI, no workflow you must adopt.

## The first principle

> **Use everyone else's hardware to run the network.**

GitHub already paid for the global CDN, the auth, the durable mailbox (Issues), the consent gate (PRs), and the edge endpoints (Pages). RAPP does not build a network — it uses the one already running. There is no central server, no marketplace backend, no PKI. There is a small frozen kernel that runs locally, single-file agents as the only unit of extension, and content-addressed identity so nothing needs to be registered with anyone who could shut it down.

## The one-agent story

The entire ecosystem is reachable through **one single-file agent**: `rapp_agent.py`, published as `@rapp/rapp` in [RAR](https://github.com/kody-w/RAR). Drop that ONE file into a brainstem's `agents/` directory and — through natural language alone — an operator can orient in the ecosystem, mint identity, plant an organism, operate every scale, and `install` any specialist agent for everything deeper. It is **navigator + bootstrapper + core-operator + universal-installer**, airdroppable and offline-safe. Full story: [`THE_ONE_AGENT.md`](THE_ONE_AGENT.md).

---

## Table of contents

### Read-it-all docs (synthesized for humans)
| File | What it is |
|---|---|
| [`OVERVIEW.md`](OVERVIEW.md) | The whole ecosystem in one read: fractal scales, 5 primitives, 7 OSI layers, the two surfaces, identity (Eternity rappid), eggs, private cubbies / dark doors, governance, the metropolis vision. **The "if you read one file" file.** |
| [`THE_ONE_AGENT.md`](THE_ONE_AGENT.md) | `@rapp/rapp` — the navigator + bootstrapper + core-operator + universal-installer; the full 41-action surface, grouped; the operator journeys; offline/woods behavior. |
| [`CAPABILITIES.md`](CAPABILITIES.md) | Every capability domain, honestly: native vs install-routed vs specialist-owned, with the action behind each. |
| [`SCHEMAS.md`](SCHEMAS.md) | The ~80-schema registry by family, one-line purpose each. |
| [`DRIFT_TRIANGLE.md`](DRIFT_TRIANGLE.md) | Why the former four-leg mirror assertion is retired, with exact reachability and hash evidence. |

### Quickstart (zero → running → planting → joining → sharing)
| File | Path step |
|---|---|
| [`quickstart/install.md`](quickstart/install.md) | Install the brainstem (the canonical one-liner). |
| [`quickstart/drop-in-an-agent.md`](quickstart/drop-in-an-agent.md) | Drop a single-file agent in. |
| [`quickstart/your-first-twin.md`](quickstart/your-first-twin.md) | Plant an organism with its own Eternity rappid. |
| [`quickstart/join-and-share.md`](quickstart/join-and-share.md) | Publish your estate, join a neighborhood, share offline. |
| [`quickstart/your-first-rapplication.md`](quickstart/your-first-rapplication.md) | Build a graduated rapplication. |

### Specs (upstream-derived historical corpus)
[`SPEC/_index.md`](SPEC/_index.md) — kernel (Constitution, SPEC, Neighborhood Protocol, Estate Spec, Twin Lifecycle, Neighborhood Egg), plus network / catalog / registry / senses / mcp.

### Repos (one page per repo)
[`repos/_index.md`](repos/_index.md) — grouped by the spec's `repos` families: kernel & install, identity & registry, stores & catalogs, run-a-brainstem, channels & trust, front doors & neighborhoods, the agent-built web, MCP & cartridges, memory & social, bible & spec.

---

## The map in one diagram

```
                    rappid:@<owner>/<slug>:<64hex>          ← identity (Eternity)
                              │
        ┌─────────────────────┴─────────────────────┐
        │   one frozen kernel + single-file agents   │       ← OSI L7 application
        └─────────────────────┬─────────────────────┘
                              │
   ┌──────────────────────────┼──────────────────────────┐
   │ agent → twin → neighborhood → estate → metropolis    │   ← fractal scales
   └──────────────────────────┼──────────────────────────┘
                              │
   substrate: GitHub Pages + raw.githubusercontent.com + LAN + eggs   ← OSI L1
                              │
   exact RAPP/1 pin · retired ecosystem snapshot · explicit status     ← governance
```

---

## How authority stays explicit

Protocol questions resolve to the immutable `kody-w/rapp-1` pin, not to this
historical rendering or either former ecosystem mirror path. `rapp-map` now
serves a quarantine status document; the `rapp-god` raw path is not publicly
reachable. See [`RAPP1_STATUS.md`](RAPP1_STATUS.md) for exact bytes and
[`DRIFT_TRIANGLE.md`](DRIFT_TRIANGLE.md) for the retirement evidence.

---

## Conventions in this Bible

- **Eternity rappid only.** Every example uses `rappid:@<owner>/<slug>:<64hex>` (SHA-256 of `<owner>/<slug>`; kind lives in the record). Legacy `rappid:v2:…` is canonicalized on read, never emitted.
- **One term for the plugin unit: `agent`.** Never skill / plugin / routine / loop (ANTIPATTERNS §1).
- **No private content sources.** Historical status may identify the owner and
  visibility of a former surface, but no private content is copied or inferred.
- **The kernel is sacred.** `brainstem.py` + `basic_agent.py` are universal DNA, never edited. Capabilities grow as new agents / organs.

## License

See [LICENSE](LICENSE).
