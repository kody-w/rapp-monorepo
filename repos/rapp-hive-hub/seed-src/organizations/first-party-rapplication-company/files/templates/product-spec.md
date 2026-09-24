# Product specification starter — session checklist

**Synthetic proposal; acceptance and effect approval remain pending.**

## Outcome and scope

Help a person add, list, and complete a few checklist items through one
conversation. Start with the reference's documented fixed grammar. Exclude
durable storage, arbitrary shell commands, network calls, account creation,
model inference, autonomous follow-up, and release authority.

The engineering task must separately identify the authorized chat host and any
adapter needed. No adapter or authenticated chat access is included in the seed.

## Proposed acceptance

- Empty, add, list, completion, repeated completion, duplicate, invalid, and
  restart behavior match `docs/chat-acceptance.md`.
- Refused requests make no state change and explain a supported next action.
- No implicit persistence or external effect occurs; the limitation is visible.
- Item IDs, text, message size, and item count are bounded by the reference.
- Product claims distinguish fixed grammar, future intent translation, tests,
  actual chat use, and authority checks.

## Owner and team decisions to record

Intended audience/hypothesis: [not user research]
Authorized host and adapter scope: [required before integration]
Performance budget and measurement method: [agree before measurement]
Host accessibility protocol: [design-owned, not inferred from tests]
Internal channel and signed/unsigned policy: [owner-authorized]
Public destination and publication scope: [owner-authorized separately]
Disconfirmation criterion: [what observed result would stop this product]
Exclusions and risk disposition: [review explicitly]
