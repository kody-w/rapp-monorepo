# `brainstem-zaps/1` frozen record

The portable distribution file is `.lispy`: exactly one expression
`(brainstem-zap "BASE64_CANONICAL_PAYLOAD")`, optionally with a detached JWS
string as its second argument. Base64 is framing, not encryption. The payload
remains the canonical RAPP value below; it has the same content address in
Python and the browser VM. No appended executable forms are permitted.
Recipient-owned signer keys are external; verified signatures are never grants.
Legacy canonical `.zap` JSON records remain readable for compatibility.

## Serialization and identity

A `.zap` file is exactly one UTF-8 JSON object serialized as RFC 8785 JCS by
the vendored, byte-identical RAPP/1 reference. There is no prefix, footer,
second record, appended expression, or new RAPP frame. Duplicate JSON member
names, noncanonical bytes, trailing material, invalid I-JSON, unknown fields,
unknown profiles, and unsupported required versions are refused.

The root record has these fields only:

- `profile`: `brainstem-zaps/1`
- `format_version`: integer `1`
- `runtime`: `brainstem-zaps-runtime/1` plus pinned Python and JavaScript
  runtime closure hashes
- `source`, `source_sha256`, and complete executable-definition `closure`
- source-derived `metadata` and `input_schema`
- `requested_capabilities` (requests, not grants)
- `resource_limits`
- embedded or explicitly pinned `assets`
- content-pinned `references` and `models`

The program digest is exactly
`H("rapp/1:particle", payload)`, where `H` and the canonicalizer come from the
pinned RAPP reference. The on-disk bytes are that canonical payload's UTF-8
bytes. The RAPP separator is the reference's LF; this profile adds no H/Hb tags
or other RAPP namespace claims. No other RAPP tags are used.

JavaScript verifies and hashes the exact file bytes. It checks canonical token
spelling, key order, duplicate absence, strict EOF, and UTF-8 while doing so; it
does **not** create replacement payload bytes with a second canonicalizer.

## Integrity checks

The Python verifier canonicalizes with the pinned reference and requires a
byte-for-byte match. Both VMs require:

1. the supported profile/version and exact field set;
2. a matching source SHA-256 and a valid bounded source parse;
3. source-derived complete definition closure and metadata equality;
4. an exact local Python runtime pin or JavaScript runtime pin supplied by the
   receiving app's trusted build;
5. embedded asset size/hash matches and supplied bytes for each external asset;
6. matching app-local recipient grant for the exact program digest before any
   granted effect is possible.

Changing source, closure, runtime pin, or an embedded asset changes the particle
digest. An external asset must be supplied and hash-checked before execution.
References and model pins are identifiers only; the VM does not fetch them.
Adapters that resolve them must enforce the exact frozen pin themselves.

## Limits and portable data

The profile rejects unsupported fields and uses strict finite numeric bounds.
Resource ceilings are part of the frozen record and can only be reduced by
device policy. Pack contents must not embed credentials, private memory, or
machine-specific absolute paths. Small assets may be embedded in base64. Larger
model weights remain external immutable pins rather than copied gigabytes.

The unsigned record proves only integrity of those exact bytes. A sealed
signature can authenticate a publisher only against the receiver's preexisting
trusted key store, using RAPP detached JWS Ed25519/P-256 semantics. Neither a
signature nor a key shipped in a pack grants effects. Unknown keys and modified
signatures are refused. The subordinate profile/registry remains draft until
adopted by its authority; implementation conformance does not ratify a registry.
