# rapp-body — the RAPP organism's biography

`kody-w/rapp-body` is the RAPP ecosystem's own **frames repo**: the whole organism recorded
as a public, rapp/1 hash-chained sequence of frames — cradle to grave — plus **`player.html`**, a
flip book that plays the frames so you can watch the body be born, grow, and transform.

One sentence: **`kody-w/twin/frames` is the biography of a twin; this repo is the biography
of RAPP itself.** The live chain uses the ratified `rapp/1` envelope and the same
public-by-construction discipline at body scale.

The chain runs **reconstructed** frames (git archaeology, the prenatal cradle) →
**witnessed** frames (live pulses from genesis forward). The film literally develops at
genesis: the player renders the reconstructed segment in sepia and the witnessed segment in
full colour.

---

## Repository layout

```
rapp-body/
├── frames/                 # the biography — append-only, chained, content-addressed
│   ├── 0.json … N.json     #   one frame per slice, named <seq>.json (twin convention)
│   ├── index.json          #   manifest: ONE fetch loads the whole timeline map
│   └── legacy/             #   sealed pre-§7 chain retained byte-for-byte for audit
├── vitals.json             # latest-frame pointer + current health rollup (static API)
├── rappid.json             # the body's Eternity identity (rapp/1)
├── sweeps/latest.json      # optional input: latest mesh-sweep verdict (feeds vitals)
├── player.html             # the flip book — self-contained, zero-CDN, watch the body change
├── tools/
│   ├── _rapp1.mjs          #   canonical rapp/1 JCS, hash spaces, build, and verify
│   ├── _frame.mjs          #   body frame construction, IO, index/vitals, no-churn helper
│   ├── _gh.mjs             #   zero-dep GitHub access (token-optional, cache-optional)
│   ├── _census.mjs         #   the cell census: spec.repos ∪ spine registry, deduped, layered
│   ├── reconstruct.mjs     #   prenatal frames from git history (run once)
│   ├── pulse.mjs           #   the witnessed frame-taker (daily)
│   └── verify-chain.mjs    #   the validator (exit 0 clean / 1 broken)
└── .github/workflows/pulse.yml
```

---

## The frame format (`rapp/1`)

Every live frame has exactly these 11 keys:

```json
{
  "spec": "rapp/1",
  "kind": "body.pulse" | "body.pulse-reconstructed",
  "stream_id": "rappid:@kody-w/rapp-body:817839d2…",
  "seq": 21,
  "utc": "2026-07-08T23:24:35.633Z",
  "payload": { … the slice … },
  "payload_hash": "…",
  "frame_hash": "…",
  "prev": "…" | null,
  "prev_wave": null,
  "sig": null
}
```

**Canonicalization.** Hash inputs use the exact-value rapp/1 JCS profile: null, booleans,
integers, strings, arrays, and objects only (no floats). Object keys sort by Unicode code
point, not JavaScript UTF-16 order.

```
payload_hash = sha256( utf8("rapp/1:particle") || 0x0A || utf8(canonical(payload)) )
frame_hash   = sha256( utf8("rapp/1:wave")    || 0x0A ||
                       utf8(canonical(frame without frame_hash and sig)) )
```

The two spaces separate the payload particle from its full envelope wave. Signatures are
optional off-swarm and are currently omitted (`sig: null`).

**Chain rules** (all enforced by `verify-chain.mjs`):

- `seq` is contiguous from 0, no gaps or duplicates.
- `prev[0] == null`; `prev[n] == payload_hash[n-1]`.
- This chain is off-swarm, so every `prev_wave` is `null`. On a swarm it links to the
  preceding `frame_hash`.
- `utc` is fixed-millisecond UTC and monotonic non-decreasing.
- `stream_id` is stable and equals the canonical identity in `rappid.json`.
- The reconstructed segment is a contiguous **prefix**: no witnessed frame precedes it, and
  no reconstructed frame appears after genesis.
- Every reconstructed frame carries `payload.provenance.evidence[]` and never claims witness.

`frames/legacy/**` is the sealed pre-§7 `rapp-frame/2.0` chain retained for audit. It is
verified under its own legacy payload-hash/link rules, and `frames/legacy/SEAL.json` binds
the canonical legacy head in the `rapp/1:seal` hash space.

### The payload

```jsonc
{
  "taken_ts": "…",
  "provenance": { "mode": "witnessed" | "reconstructed", "evidence": ["…"] },
  "skeleton": {
    "spec_version": "1.1.0",
    "homes": { "historical_rapp": {…} },                          // immutable census input
    "mirrors_identical": null,                                    // retired; schema continuity only
    "spine": { "registry_sha256": "…", "foundation_sha256": "…" }
  },
  "census": {
    "basis": "witnessed",
    "count": 54, "present": 51, "transport_unreadable": 0,
    "repos": [ { "name", "owner", "layer", "category",
                 "status",          // present | stale | absent_unconfirmed | absent | vanished | unreachable
                 "reachable",       // === status "present"
                 "stale",           // true ⇒ unreadable this run, carrying last-known forward
                 "head_sha", "pushed_at", "created_at" } … ],
    "born": ["…"], "vanished": ["…"]                             // vs the previous frame — POSITIVE evidence only
  },
  "vitals": {
    "sync": { "verdict": "DRIFT-FOUND", "findings": 13, "high": 3, … },  // from sweeps/latest.json
    "drift_issues": { "open": 1, "by_severity": {…} },                   // live open drift() issues
    "mirrors_identical": null
  },
  "events": [ { "type": "birth"|"vanish"|"heads-advanced"|"sweep"|"drift-delta"|"genesis"|"heartbeat"|"observation-gap"|… } ]
}
```

An unreadable source is **never** silently dropped — it becomes an explicit
`{ "type": "observation-gap", … }` event, so absence is always visible.

### Doctrine — an observation gap is *transport*, not *biography*

The single most important rule of the frame-taker (learned the hard way — rate-limiting
once produced frames that "vanished" 33 live repos purely because HTTP 403 made them
unreadable):

- **A gap never changes the census.** A repo unreadable this run but present last frame
  KEEPS its last-known entry (`stale: true`), emits an `observation-gap`, and produces **no**
  born / vanish / census change. `head_sha` is carried forward, so the no-churn fingerprint
  is unchanged — a blind run mints nothing.
- **`vanish` requires positive evidence.** A repo is only recorded gone after an HTTP 404 on
  the repo itself, **confirmed on two consecutive runs** (`present → 404 → 404`). 429 / 403 /
  network are our blindness, never proof of death.
- **Coherence gate.** If **any** spec home is unreadable, or **> 20 %** of the census repos
  are transport-unreadable, `pulse.mjs` refuses to mint and **exits 3** (`slice incoherent`).
  `--force-degraded` overrides it (minting a clearly-marked stale slice). **CI always runs
  with `GITHUB_TOKEN`**, so it never trips the gate.
- **The no-churn fingerprint excludes observation gaps and stale markers entirely.**
- **`verify-chain` enforces it too:** any frame where a repo appears in a born/vanish change
  while also carrying a same-frame observation-gap **fails** verification (defense in depth).

---

## Quickstart

Requires **Node ≥ 20**, zero npm dependencies.

```bash
# 1. Prenatal frames from git history (run once — the cradle):
node tools/reconstruct.mjs

# 2. Take a live witnessed slice (mints a frame only if something changed):
node tools/pulse.mjs
node tools/pulse.mjs --heartbeat        # force a weekly liveness frame
node tools/pulse.mjs --force-degraded   # mint even when the slice is incoherent
#   exit 0 = minted or clean no-change · 1 = internal error · 3 = slice incoherent (refused)

# 3. Prove the whole biography is intact:
node tools/verify-chain.mjs          # exit 0 = OK, 1 = broken (with reasons)

# 4. Watch it:
python3 -m http.server 8000          # then open http://localhost:8000/player.html
```

**No-churn rule (hard).** If the skeleton + census + vitals are materially identical to the
previous frame (timestamps, observation gaps, and stale markers all ignored), `pulse.mjs`
prints `no change; no frame` and mints nothing. `--heartbeat` overrides it. This is what
keeps the biography honest — a frame means the body actually changed.

### Environment

| var | effect |
| --- | --- |
| `GITHUB_TOKEN` / `GH_TOKEN` | used when present (5000 req/hr); the tools are anonymous-safe without it. **CI always sets it** so the coherence gate never trips |
| `RAPP_CACHE_DIR` | read-through disk cache of GitHub responses (polite, offline, deterministic runs); caches 200 bodies and 404 sentinels — never transport failures |
| `RAPP_CACHE_ONLY=1` | forbid the network — a cache miss becomes an unreadable source (proves an offline run) |
| `RAPP_BODY_ROOT` | run against a throwaway body in another dir (used by the self-tests) |

---

## The static-API surface (`rapp-static-api/1.0` — the repo IS the API)

Everything is raw-loadable over `raw.githubusercontent.com`, CORS-open, no server:

- **`frames/index.json`** — the manifest: `{ seq, path, utc, kind, payload_hash,
  frame_hash, prev, prev_wave }` per frame. One fetch loads the whole timeline; the
  player walks it.
- **`vitals.json`** — the latest-frame pointer + a health rollup (spec version,
  mirrors_identical, repo counts, drift, observation gaps).
- **`frames/<seq>.json`** — each slice, lazy-loaded on demand.

---

## Identity

`rappid.json` mints the body's identity under **rapp/1** (ratified schema name,
CONSTITUTION Art. LIV, 2026-07-15; canonical Eternity form per Art. XXXIV.1 / XXXVI.1;
formerly styled rapp-rappid/2.0). The string is self-locating:

```
rappid:@kody-w/rapp-body:817839d299ddfb173097c58a0434c5c1ef5cd2cd55086c46cfe728bf9bfeb657
                         └─ the 64-hex tail is an opaque JOIN KEY, never derived from the slug
```

The 64-hex tail is **not** a hash of `<owner>/<slug>` — the hash is the join key, the slug is
just addressing. How the tail is anchored depends on whether the organism holds a master
keypair (RAPP/specs/SPEC.md §2.3, pages/vault/Architecture/Rappid.md):

- **keyed** organisms anchor on `sha256(master_pubkey_SPKI)` — the key *is* the identity;
- **keyless** organisms anchor on a stable UUID/commit-derived hash:
  `hashlib.sha256(uuid.uuid4().bytes).hexdigest()` (the `bond.py` mint idiom).

**rapp-body is keyless** (it holds no master keypair), so its tail is
`sha256(uuid4().bytes)`. The preimage UUID is recorded in `rappid.json._legacy_uuid`, and the
one-time re-anchor from the earlier (incorrect) `sha256('<owner>/<slug>')` id is recorded in
`_migrated_from` per SPEC.md §2.3.

The identity is the **worldline**, not any single slice: no one frame IS the body — the
chained sequence is. `stream_id` is outside the payload, so changing it would preserve the
`payload_hash` but necessarily change the envelope's `frame_hash`. A keypair signature is
optional off-swarm and omitted here; `prev` carries the particle chain.

---

## The census (which repos are organs)

The cell census is composed, never invented, from explicitly pinned inputs:

- **Historical ecosystem v1.2.0 `repos`** (10 cluster groups) — read only from
  `kody-w/RAPP@789e6c5245f18e9685450fd6105dc26867837895:specs/ecosystem-spec.json`.
  This is an immutable census input, not protocol authority or a registry. The
  former `rapp-god`/`rapp-map` byte-identical contract is retired, so
  `mirrors_identical` is now always `null` and remains only for frame-schema
  continuity.
- **`kody-w/rapp-spine` `registry.json`** — the layer taxonomy
  (`kernel · map · runtime · distribution · identity · network · leviathan`, plus
  `uncataloged`) and each repo's placement.

The census is the **union** of both, deduped. Layer comes from the spine;
cluster/category is historical metadata from the pinned snapshot. Current
protocol authority is the exact `kody-w/rapp-1` rev-5 pin.

---

## Conformance

`tools/_rapp1.mjs` mirrors the reference `kody-w/rapp-1/rapp.py`. The verifier replays
every frame in sequence, recomputes both hash spaces, checks `prev`/`prev_wave`, rejects
unknown specs and kinds, validates the static head pointers, and separately verifies the
sealed legacy audit chain.

---

## The door

[Herald](https://kody-w.github.io/rapp-body/door/) is the body's doorman: a frame-grounded
chat posting that answers from the public biography with clickable receipts. Its
`born_of_frame` pin is frame `24`. Under Lexicon R6, **Herald** here names the Herald
**POSTING**, not the herald key or the Herald rank.
