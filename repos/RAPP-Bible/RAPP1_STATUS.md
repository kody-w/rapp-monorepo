# Historical ecosystem rendering — no active mirror contract

This repository preserves a human rendering of the retired
`rapp-ecosystem-spec/1.0` v1.2.0 snapshot. It is not current RAPP/1 protocol
authority, an authenticated registry, or a byte-identical mirror.
The repository and public-path observations below were recorded at
`2026-08-23T22:08:24Z`.

## Exact protocol authority

- Repository: `kody-w/rapp-1`
- Immutable commit: `d2cd5abed48d3f52b86bbb975ac3558286d1db41`
- Current `main` observed: `0544cee07fd185af9a85286a09649cc1bbe41557`
- Path: `SPEC.md`
- Revision: `rev-5`
- Bytes: `41952`
- SHA-256: `cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a`

The `SPEC.md` bytes at current `main` are byte-identical to the immutable
commit above. [`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json) is a structural
pin only and is not authenticated RAPP/1 section 13 registry evidence.

## Retired ecosystem mirror assertion

The former Bible text claimed that an ecosystem JSON was published
byte-identically at `rapp-map` and `rapp-god`. That claim is retired:

- `kody-w/RAPP@789e6c5245f18e9685450fd6105dc26867837895`,
  `specs/ecosystem-spec.json`: historical v1.2.0 source, 60,479 bytes,
  SHA-256 `0eb8146b62af8e8473d2ca8944ed8aff69e18e41a143eb1ef466f3c3fc153616`.
- `kody-w/rapp-map@f3dd5ed11514d0562eb7fc87afc2eb59ed87aca6`,
  `ecosystem-spec.json`: 1,020-byte `quarantined-candidate` status document,
  SHA-256 `736a9ae026b4be0d602a1a405195115ef1ab15484b5748e1502664b349f41e2d`;
  it is not a mirror.
- `kody-w/rapp-god`, owned by `kody-w`, is private. Without authentication,
  its claimed raw path returns HTTP 404 with the exact 14-byte
  `404: Not Found` body, SHA-256
  `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed`.
  No private content is copied or inferred here.

There are no active byte-identical ecosystem mirrors in this repository.
Reinstatement requires a new public, immutable, byte-for-byte proof from the
owning repositories.
