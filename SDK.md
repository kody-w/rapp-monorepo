# RAPP organism SDK

`rapp_sdk` is the root SDK for inspecting this captured 196-organ estate and
for implementing the current RAPP/1 protocol. It does not import or execute
captured repositories.

## Install

Python 3.11 or newer is required.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install .
```

For development and verification:

```bash
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest tests -q
```

The SDK root is always explicit. A globally installed CLI does not guess which
checkout or runtime lineage is authoritative.

```bash
rapp-sdk --root /path/to/rapp-monorepo status
rapp-sdk --root /path/to/rapp-monorepo authority
rapp-sdk --root /path/to/rapp-monorepo alignment
rapp-sdk --root /path/to/rapp-monorepo systems
rapp-sdk --root /path/to/rapp-monorepo organs
rapp-sdk --root /path/to/rapp-monorepo organ rapp-1
rapp-sdk --root /path/to/rapp-monorepo read rapp-1 SPEC.md
rapp-sdk chat --endpoint https://explicit.example/chat "hello"
```

Use the global `--json` option for machine-readable output.

## Authority and trust

The user-designated current protocol source is
[`kody-w/rapp-1`](https://github.com/kody-w/rapp-1). In this snapshot,
`repos/rapp-1/SPEC.md` is 41,952 bytes with SHA-256 `cea7847f…`; Map's
`d2cd5a…` structural pin names those bytes. The retired `kody-w/RAPP` target
still records an older 41,880-byte `6723c7…` structural pin. That target record
is useful drift evidence and does not redefine the current standard.

No checked-in record is the missing authenticated section-13 registry. Full
authenticated conformance remains false until the owner publishes:

1. a signed, monotonic `rapp/1-registry`;
2. the keyed estate-owner rappid through an out-of-band channel;
3. its matching canonical SPKI;
4. freshness policy and owner-authorized lifecycle records.

The SDK never constructs this evidence from repository names, commits, Map,
Spine, or the stale RAPP site.

## Structural versus authenticated APIs

| API | Result semantics |
|---|---|
| `Organism`, `inspect_authority`, `inspect_alignment` | Snapshot and declared-evidence reporting only |
| `SafeSpecimen.read_*` | No-follow content access; never import or execution |
| `strict_loads`, `canonical_bytes`, `H`, `Hb` | RAPP/1 structural primitives |
| `inspect_frame`, `inspect_egg`, `parse_refusal` | Structural inspection only |
| `verify_registry` | Authenticated proof after signature, anchor, source, freshness, and monotonic-state verification |
| `FrameConsumer.accept` | Stateful frame acceptance using a `VerifiedRegistry` and persisted heads |
| `accept_egg` | Recursive egg acceptance using a `VerifiedRegistry` |
| `accept_refusal` | Exact refusal acceptance with a registered error code |

`VerifiedRegistry` is opaque and frozen. It cannot be created with a caller
assertion such as `authenticated=True`; only `verify_registry` can produce it.
A verifier call requires raw registry bytes, the out-of-band anchor, canonical
SPKI DER, source URL, fetch/check times, freshness limit, and a monotonic state
store:

```python
from datetime import datetime, timezone
from rapp_sdk import SQLiteRegistrySequenceStore, verify_registry

proof = verify_registry(
    raw_registry,
    out_of_band_anchor=anchor_rappid,
    anchor_spki_der=owner_spki_der,
    state=SQLiteRegistrySequenceStore("registry-state.sqlite3"),
    source="https://approved.example/rapp-1-registry.json",
    fetched_at=fetched_at,
    now=datetime.now(timezone.utc),
    max_age_seconds=3600,
)
```

Registry verification enforces every re-anchor case. Provisional upgrades
additionally require an explicit `TrustedProvisionalResolution` from the
caller's out-of-band evidence. Compromise requires a same-registry tombstone,
tag migration verifies the historical untagged SPKI digest, and signatures by
superseded keyed rappids are refused at and after their recorded cutover UTC.

`SQLiteHeadStore` provides persistent, compare-and-swap stream heads.
`FrameConsumer` enforces registered genesis, contiguous successors, rollback
refusal, equal-sequence fork quarantine, branch/gap refusal, and only
registry-authorized owner-signed re-genesis resets.

## Specimen safety

`repos/**` is a read-only cage. Safe access:

- accepts only a manifest-listed organ that is classified exactly once;
- requires manifest/taxonomy equality;
- rejects separators and dot components in organ names;
- rejects absolute paths, traversal, directories, and symlink components;
- fails closed on platforms without descriptor-relative no-follow primitives.

Egg extraction likewise uses descriptor-relative `mkdir`/`open` operations
with `O_DIRECTORY` and `O_NOFOLLOW`. It verifies the complete recursively
bounded egg before creating the destination.

## Alignment evidence

`rapp-sdk alignment` reports Map/Spine projection coverage, observation
freshness, generator provenance, authority-pin conflicts, and active legacy
frame/egg/wire claims. Live-head values and crawl findings recorded in
`ORGANISM.json` are labeled as cartographer evidence; the SDK does not pretend
that they were dynamically fetched during an offline invocation.
