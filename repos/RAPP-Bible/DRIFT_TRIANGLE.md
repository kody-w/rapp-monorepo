# Retired ecosystem mirror contract

> **Status: historical.** This page records why the former “drift triangle”
> must not be used as a current authority or verification procedure. Current
> RAPP/1 protocol authority is the exact rev-5 pin in
> [`RAPP1_AUTHORITY.json`](RAPP1_AUTHORITY.json); repository disposition is in
> [`RAPP1_STATUS.md`](RAPP1_STATUS.md).

The v1.2.0 Bible described four representations of an ecosystem snapshot:
an agent action enum, `rapp-god`, `rapp-map`, and this human rendering. It
claimed the two JSON surfaces were byte-identical. The public surfaces no
longer satisfy that contract:

| Former leg | Current observed disposition |
|---|---|
| `kody-w/RAPP:specs/ecosystem-spec.json` | Historical 60,479-byte v1.2.0 source at immutable commit `789e6c5245f18e9685450fd6105dc26867837895`; not RAPP/1 authority or a registry. |
| `kody-w/rapp-map:ecosystem-spec.json` | 1,020-byte `quarantined-candidate` status document; not a mirror. |
| `kody-w/rapp-god:api/v1/ecosystem-spec.json` | Repository owner is `kody-w`; visibility is private; unauthenticated raw fetch returns HTTP 404 and the 14-byte `404: Not Found` sentinel. |
| `kody-w/RAPP-Bible` | Historical human rendering; no machine mirror and no authority precedence. |

## Current rule

There is **no active byte-identical ecosystem mirror set**. A successful fetch,
a matching semantic schema, or authenticated access to a private repository
would not prove a public mirror contract. Consumers must not:

1. treat either former URL as current RAPP/1 authority or registry evidence;
2. report a 404 sentinel as reachable content;
3. use equality between status documents as proof of ecosystem alignment; or
4. claim that this Bible is pinned to a live ecosystem-spec version.

Future reinstatement requires owner-approved public artifacts, immutable commit
URLs, exact lengths and SHA-256 values, and a byte-for-byte comparison. Until
then, the only live invariant documented here is the exact
`kody-w/rapp-1` rev-5 authority pin.

The original v1.2.0 prose remains recoverable in Git history. It is evidence of
the retired assertion, not an instruction to recreate or invent missing
content.
