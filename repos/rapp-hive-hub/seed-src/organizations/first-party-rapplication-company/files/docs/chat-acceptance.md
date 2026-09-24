# Chat acceptance protocol

The synthetic product is a session-local checklist. The reference accepts a
fixed grammar; it does not understand arbitrary natural language. A future
approved adapter may translate intent, but must preserve validation and effect
boundaries and must not pretend it already exists.

Proposed reference budget: at most 50 items, identifiers matching
`[a-z][a-z0-9-]{0,31}` (a lowercase ASCII letter first, then lowercase ASCII
letters, digits or hyphens; for example `item-1`), 120-character item text,
and 256-character input messages. The actual host's
latency and accessibility must be measured separately. Agree host budgets in
the product specification before implementation; no measured latency is supplied.

| Journey | Expected behavior | Required evidence |
| --- | --- | --- |
| Empty session | `list` reports no items and explains the next command | Reference fixture plus actual chat observation |
| Add | `add sample Inspect the package` adds one item | Exact response and minimal synthetic reproduction |
| Duplicate | Reusing `sample` refuses without overwriting it | Before/after state and response |
| Complete | `done sample` marks that item complete | Actual state and response |
| Repeat | Repeating completion is harmless and says already complete | Idempotence observation |
| Invalid | Unknown command, missing identifier/text, oversize input, controls, or excess items refuses | Negative cases and unchanged state |
| No hidden authority | Requests to publish, sign, merge, or read private files refuse | No side effect, actionable explanation |
| Restart | Starting a new reference process is empty | Explicit non-persistence warning; no durability promise |

Use `templates/dogfood-scorecard.json`. Record the exact candidate, host/runtime
version, qualification suite hash, reviewer role reference, method, timing
samples, pass/fail/not-observed, and bounded evidence references. Raw user
conversations are not public evidence. Prefer synthetic content.

Unit tests establish source behavior only. A live-use gate needs real use of
the intended chat host and exact candidate, including failure/recovery. If no
authorized runtime or independent observer is available, record the blocker.
Do not substitute a mocked conversation, code inspection, or this reference's
stdin loop for authenticated host integration.

Design reviews the host's reading order, keyboard input, status/error
announcements, and applicable cancellation behavior. A terminal fixture does
not imply screen-reader conformance or a hosted UI accessibility certification.
