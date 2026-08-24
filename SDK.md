# RAPP organism SDK

`rapp_sdk` is the root SDK for inspecting this captured 197-organ estate and
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

Every SDK workflow run retains the built wheel and source distribution as a
30-day GitHub Actions artifact. The workflow can also be started manually;
publishing to a package index remains an explicit release decision rather than
an automatic side effect of verification.

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
`d2cd5a…` structural pin names those bytes. The `kody-w/RAPP` public product is
retired, while its target record remains current-but-drifted and records an
older 41,880-byte `6723c7…` structural pin. Current record currency does not
reactivate the product; the record is useful drift evidence and does not
redefine the current standard.

Authority inspection validates every modeled authority subrecord with exact
keys and fail-closed values. Map is valid only when its pin, structural-only
scope, non-conformant status document, and refusal of authenticated-registry
acceptance all agree; a correct hash cannot rescue a false scope or status.

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

Mode-160000 gitlinks are inventory pointers, not readable specimen files. The
manifest exposes their path and exact commit OID; the SDK never dereferences or
executes their external target content.

Egg extraction likewise uses descriptor-relative `mkdir`/`open` operations
with `O_DIRECTORY` and `O_NOFOLLOW`. It verifies the complete recursively
bounded egg before creating the destination.

## Alignment evidence

`rapp-sdk alignment` reports Map/Spine projection coverage, observation
freshness, generator provenance, authority-pin conflicts, and active legacy
frame/egg/wire claims. Live-head values and crawl findings recorded in
`ORGANISM.json` are labeled as cartographer evidence; the SDK does not pretend
that they were dynamically fetched during an offline invocation.

Generator provenance distinguishes named-path presence from derivation.
Because captured code is never executed, the SDK can confirm that the declared
artifact, generator, and inputs are regular files but labels the derivation
check as not performed; `generator_provenance_complete` remains false. Every
path component is opened descriptor-relatively with `O_NOFOLLOW`, and the leaf
is checked with `fstat`; missing platform support or a symlinked parent makes
provenance unavailable rather than silently falling back to pathname `stat`.

The architecture registry is strict by default. `Organism(root)` requires
exact manifest/taxonomy set equality, constrained lifecycle values, both
non-empty Map and Spine projection records, and `rapp-1` in
`authority-contracts-navigation`. Scheduled status/alignment code that must
report drift instead of refusing it uses the explicit
`Organism(root, allow_drift=True)` path and must display `architecture_drift`.

Each projection names a captured `coverage_source` and extractor. Alignment
recomputes the exact current covered and missing organ sets from
`rapp-map/estate-map.json` and `rapp-spine/crawl.json`, attaching a reason to
every missing organ. An unreadable or invalid source is labeled
`not-recomputed`; it never becomes a vacuous empty success.

Alignment renders repository component coverage separately from organism
coverage. It reconciles component counts and the complete omission list
against each projection's `MANIFEST.json` record. Map therefore reports 41/45
captured blobs with four omissions (one skipped `neurons.json` and three
withheld blobs), independently of its 152/197 captured-organ overlap.

`ORGANISM.json` also records the candidate membership predicate and its two
deliberate exclusions. `kody-w/rapp-monorepo` is excluded to avoid recursive
self-capture, and `kody-w/rapp-shape-aibast` is excluded as external
library-layout staging rather than silently disappearing from the estate.
