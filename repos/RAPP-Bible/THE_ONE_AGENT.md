# The one agent — `rapp_agent.py` / `@rapp/rapp`

> **Historical snapshot.** This page renders fields from the retired ecosystem
> v1.2.0 document. It is not a current action contract. See
> [`RAPP1_STATUS.md`](RAPP1_STATUS.md).

There is one agent that makes the **entire** RAPP ecosystem reachable through natural language. Drop a single file — `rapp_agent.py`, published as **`@rapp/rapp`** in [RAR](https://github.com/kody-w/RAR) — into a brainstem's `agents/` directory, and an operator can orient in the ecosystem, bootstrap their identity and a fresh organism, operate every core scale, record lineage, and **install any specialist agent** for everything deeper. All through conversation.

---

## §1 — The model: navigator + bootstrapper + core-operator + universal-installer

The one agent plays four roles at once:

- **Navigator** — it knows the whole map. `spec`, `ecosystem`, `find`, `protocol`, `help` orient you in the ecosystem. The map is *embedded* so it works offline.
- **Bootstrapper** — it can stand up identity and an organism from nothing: `mint` a rappid, `scaffold` the kernel seed agents, `plant` a door, `memory`-init the store.
- **Core-operator** — it natively drives every core scale: estate (`estate`, `door`, `whoami`), neighborhood (`mount`, `join`, `browse`, `super_rar`, `load`), cubby (`cubby_new`, `cubby_egg`, `cubby_import`), egg (`hatch`), lineage (`bond`, `lineage`).
- **Universal-installer** — its superpower. `install` / `route` pull any specialist agent from RAR, the stores, or a neighborhood's RAR on demand.

### Why it is NOT a monolith

The ecosystem is built **from** single-file agents (ANTIPATTERNS §1 — one term, `agent`, forever). The one agent does **not** reimplement all ~30 specialists. It **reaches** them. Deep specialist work stays in its own agent. The god agent's job is to know *that* a capability exists, *who* owns it, and *how* to install it — then route you there.

> **The contract.** Drop this ONE file in. Through natural language alone the operator can utilize the ENTIRE ecosystem end-to-end. It is airdroppable and offline-safe: it embeds a baseline of the whole map so it works in the woods, and `refresh` re-syncs from the global grail when online.

---

## §2 — The full action surface (41 actions, grouped)

The live agent's `metadata` enum must be a **superset** of every action below. `action=verify` asserts this; any mismatch is drift (see [`DRIFT_TRIANGLE.md`](DRIFT_TRIANGLE.md)).

### Orient — "where am I, what exists"
| Action | Does |
|---|---|
| `spec` | Return the freshest ecosystem spec (embedded baseline offline; refreshed online). |
| `help` | List every action with a one-line description. |
| `protocol` | Surface the neighborhood / network wire protocol. |
| `ecosystem` | Render the parts database — schemas, repos, neuron mesh. |
| `find` | Search the ecosystem for a part by name / kind / tag. |
| `refresh` | Historical action description: re-sync the embedded map from the former ecosystem surfaces. Those surfaces are no longer an active mirror contract. |

### Identity & bootstrap — "set me up"
| Action | Does |
|---|---|
| `whoami` | Read the operator's rappid + estate overview. |
| `mint` | Generate a unique Eternity rappid at first plant. |
| `scaffold` | Fetch + install the kernel seed agents into `agents/`. |
| `plant` | Clone/fork a template and scaffold `soul.md`, `agents/`, memory, a door. |
| `memory` | Initialize / read / write the local memory tier. |
| `door` | Encode a rappid and derive its nine canonical URLs. |

### Estate — "my whole presence"
| Action | Does |
|---|---|
| `estate` | Show / add to / publish the local door catalog. |
| `lineage` | Walk `parent_rappid` back to the species root. |
| `bond` | Append a lifecycle event to `bonds.json` (birth / bond / hatch / graft / launch / rhythm). |
| `beacon` | Publish the discovery beacon so other operators can sniff you. |
| `sniff` | Decentralized BFS discovery of the network (raw URLs, LAN Bonjour, sneakernet). |

### Cubbies & eggs — "carve out a piece and share it"
| Action | Does |
|---|---|
| `cubby_new` | Create a new cubby (a private estate slice). |
| `cubby_list` | List local cubbies. |
| `cubby_show` | Show one cubby's contents. |
| `cubby_collect` | Group local hits into a cubby (secret-filtered). |
| `cubby_egg` | Pack a cubby / organism into a sealed `.egg`. |
| `cubby_import` | Hatch an organism / cubby `.egg`. |
| `hatch` | Universal hatch — introspect an `.egg` and route by kind. |

### Neighborhoods — "join a community and use what they built"
| Action | Does |
|---|---|
| `mount` | Mount a neighborhood gate from a rappid / repo. |
| `join` | Add the operator's rappid to the gate's `members.json` (via PR). |
| `browse` | List a neighborhood's roster + shared agents. |
| `super_rar` | Federated search across local / neighborhood RAR indexes. |
| `load` | Install a shared agent (git-invisible stream). |
| `unload` | Remove a loaded agent. |
| `stash` | Author + publish an agent into a neighborhood. |
| `sync` | Reconcile local + remote neighborhood state. |
| `branch` | Branch a neighborhood for a variant. |
| `invite` | Issue an invite to a private (dark-door) neighborhood. |
| `enter` | Enter a v-neighborhood front door. |
| `qr` | Render the pairing QR + 6-digit safety code for a WebRTC tether. |
| `show_and_tell` | Share a fact / artifact into the neighborhood. |

### Reach + verify — "everything deeper, and stay aligned"
| Action | Does |
|---|---|
| `install` | Pull any specialist agent from RAR / a store / a neighborhood RAR. |
| `route` | Given a need, name the specialist + the exact install command. |
| `mmr` | Compute single-door MMR + tier badge. |
| `verify` | The 4-leg drift self-check (agent ⊇ spec; god == map; Bible pinned). |

**Existing today (28):** `spec, help, protocol, ecosystem, find, refresh, whoami, estate, door, cubby_new, cubby_list, cubby_show, cubby_collect, cubby_egg, cubby_import, super_rar, mount, join, browse, stash, hatch, load, unload, sync, branch, invite, qr, enter, show_and_tell`.

**Added to close gaps (13):** `install, route, mint, scaffold, plant, memory, bond, lineage, beacon, sniff, mmr, verify`.

**Total: 41.**

---

## §3 — How `install` makes the whole ecosystem reachable

`install` is the load-bearing action. Because the ecosystem is built from single-file agents, the one agent does not need to *be* every capability — it needs to be able to *fetch* every capability.

```
operator: "I need to manage twin lifecycles."
  → route need="twin lifecycle"
      ↳ names @rapp/twin_agent + the install command
  → install @rapp/twin_agent
      ↳ pulls twin_agent.py from RAR into agents/
  → "stop my heimdall twin and archive it"
      ↳ now the LLM has the twin_agent's tools and does it
```

The same path works for any depth: sealed encryption (install the doorman), deep memory (install the memory agents), graft / launch / dock (install from the species grail), MMR / leaderboard / dream-catcher / resurrection / proximity / ant-farm (install the matching specialist). The god agent natively does the *single-door* slice of many of these (single-door MMR, local memory tier, lineage frames) and routes you to the specialist for the rest.

---

## §4 — Operator journeys

These are the canonical end-to-end flows the one agent supports:

| Journey | Flow |
|---|---|
| **Fresh install in the woods** | drop `rapp_agent.py` → *"who am I / set me up"* (`mint` → `scaffold` → `plant`) → *"what exists"* (`spec` / `ecosystem` / `find`, all embedded offline). |
| **Join a neighbor's neighborhood and use what they built** | `door` (resolve their rappid) → `mount` → `join` → `browse` → `super_rar where=neighborhood query=X` → `load` (stream git-invisible) / `install` (pull an agent). |
| **Carve a digital organism out of my estate and share it** | `super_rar where=local query=X` → `cubby_collect` (group the hits) → `cubby_egg` → `mount` a neighborhood → `hatch` (mirror it in) — records a bond. |
| **Reach any deep capability I don't have** | `route need='...'` → it names the specialist + the exact install → `install` → now invoke that specialist via natural language. |
| **Stay aligned with canon** | `refresh` (pull the grail) → `spec` (freshest) → `verify` (4-leg drift check). |

---

## §5 — Offline / woods behavior

The one agent is designed for the **Charizard-in-the-woods** hero case: two devices, no internet, sharing over a QR pair.

- It **embeds a baseline** of the whole ecosystem map. `spec`, `ecosystem`, and `find` answer from the embedded copy when offline.
- It **mints, scaffolds, and plants** without a network — identity is content-addressed, not registered with anyone.
- Eggs **hatch** from a local path or a `file://` URL; cubbies are portable offline by design.
- `refresh` re-syncs the embedded map from the global grail **when a connection returns** — never a hard requirement to function.

Local-first is not a fallback mode; it is the default. The network is what you reach *when you can*, not what you *need* to operate.

---

## §6 — Specialist agents the one agent reaches (not reimplements)

| Capability | Owner agent | Reach |
|---|---|---|
| Twin lifecycle (boot / stop / archive / unarchive / purge / list) | `@rapp/twin_agent` | `install @rapp/twin_agent` |
| Egg hatch / introspect / route across the cartridge family | `@rapp/egg_hatcher` | `install @rapp/egg_hatcher` — or use the god agent's native `hatch` for cubby/estate eggs |
| Deep memory (public `memory.json` + per-user private Issue memories + ascended export) | `manage_memory_agent.py` / `context_memory_agent.py` | install the memory agents — the god agent natively does the LOCAL memory tier |
| Sealed encryption (AES-256-GCM sealed-door) | `rapp-doorman` | install the doorman |
| Live WebRTC session capture (`brainstem-egg/2.3-session`) | `pages/vbrainstem.html` exporter | a live tether produces it; the god agent can `hatch` / `mount` one |
| Rapplication source editing | a dedicated source-editor agent / Copilot Studio (Tier 3) | out-of-scope for the god agent |
| graft / launch / dock / bond-rhythm / lineage-rollup | `graft_neighborhood_agent` / `launch_to_public_agent` / `dock_agent` / `bond_rhythm_agent` / `lineage_rollup_agent` | install from the species grail |
| dream-catcher / resurrection / proximity / ant-farm / MMR-leaderboard | the matching specialist in `rapp_brainstem/agents/` | install the specialist; the god agent natively computes single-door MMR + records lineage frames |

This is the whole point: the one agent is the front of the line. It knows what exists, who owns it, and how to get it. Everything else is one `install` away.

---

*Historical provenance: retired ecosystem v1.2.0 fields
`the_one_agent`, `required_actions`, `operator_journeys`, and
`specialist_agents`. Current protocol authority is
[`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json).*
