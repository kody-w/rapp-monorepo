# Security model

## Goals and trust boundaries

The primary threat is a hostile program traded as an expansion pack. Treat its
source, metadata, requested capabilities, model references, and claimed result
as untrusted data. A content digest detects changes relative to the receiving
app's local approval; it does not authenticate an author. Detached RAPP
Ed25519/P-256 publisher signatures are verified against recipient-owned trusted
SPKI keys. A verified publisher still cannot grant powers on its own.

Trusted components are the fixed runtime pinned by the receiving application,
its local recipient grant and device policy, the in-process adapter registry,
the callback implementations, and the selected replay ledger. These are
application-local inputs; no network broker or service is part of execution.
A bad host, adapter, provider, policy administrator, runtime build, or
operating system is outside what this VM can repair.

## Default-deny effects

An effect is authorized only when all conditions hold:

1. The frozen pack explicitly requests the exact name, version, and operation.
2. A recipient grant names the exact computed `rapp/1:particle` digest and that
   operation.
3. Device policy independently approves that operation and the exact adapter
   name/version/content pin.
4. The installed adapter contract matches the pin and declares that operation.
5. Argument JSON passes the contract, grant, and device-policy schemas.
6. Path and HTTPS egress restrictions are explicit and intersect at all three
   layers when relevant.
7. The per-run budget and replay ledger allow the call.

There are no wildcard grants, automatic approvals, program-supplied handlers,
adapter downloads, or future-standard loaders. Names such as
`mcp.search`, `plugin.review`, `workflow.compose`, and `skill.inspect` are
ordinary request labels until a host separately installs and approves a
matching adapter contract. The browser demo has no handlers and is pure-only.

Python handlers are async callables in an `AdapterBinding`; JavaScript handlers
are async callbacks in the receiving app's local `brokerConfig`. `EffectBroker`
is created inside the VM process; `BrokerConfig` only supplies the local grant,
policy, pinned callback contracts, and replay hook. Neither is a daemon,
network endpoint, or remote authorization call. Pure programs and registered
local effects run offline without Python on iOS/browser. A particular adapter
may itself call a remote service—for example, a Comfy workflow—but only that
workflow then depends on that provider. The VM has no built-in remote service.

Handlers receive bounded plain JSON arguments, never VM environments, host
context objects, provider clients, or callbacks. They return bounded JSON only.
The receiving app must verify that each local callback is the implementation
represented by its configured content pin; the VM does not download or
dynamically load adapter code.

## No ambient host access

Programs run in fresh environments. The language exposes no Python or
JavaScript global namespace, reflection, eval/exec, `Function`, imports,
shell, filesystem, direct network, timers, process handles, native objects, or
arbitrary plugins. Dictionary keys use ordinary inert strings; JavaScript
dictionaries have null prototypes, and lexical bindings use `Map`. Names like
`__proto__`, `constructor`, and `prototype` never resolve to host objects.

Context and inputs are copied through bounded JSON validation. Effects are
asynchronous local syscall calls with opaque callbacks; provider objects do not
enter the program environment. A native iOS host must run the VM inside its OS
sandbox and derive local grants from its permission/entitlement policy. This
core does not configure OS entitlements; that host integration and physical
device enforcement remain untested. External model/reference pins are not
fetched by the VM. Adapters must resolve them under their own exact pin and
egress policy.

## Bounded execution

Independent limits cover artifact/source bytes, token count and size, parse
depth, evaluation fuel, call depth, allocated values, string and collection
sizes, numeric range/overflow, output bytes, wall-clock deadline, effect count,
and adapter timeout. Allocation-prone primitives check budgets before
constructing large collections or strings. Device policy can lower the pack's
resource ceilings; it cannot widen the runtime's hard ceilings.

The browser JavaScript VM verifies exact canonical input bytes with Web Crypto
or Node's built-in crypto. If hashing is unavailable or the trusted runtime pin
is absent, verification refuses. The optional demo pin is a local development
manifest, not an authenticated production trust anchor. Signed sealed `.lispy`
programs reject unknown publishers, unsupported algorithms, changed payloads
and keys whose content address does not match the signer RAPPID. Keys carried
by a program are never added to the trust store.

The browser demo runs the interpreter in a dedicated worker with a wall-clock
termination guard and no network permissions. It has been exercised directly
from local files with zero HTTP requests and no Python/server dependency.
Worker isolation is not a substitute for signing the receiving application or
enforcing its native OS sandbox.

## Effects, replay, and completion

The broker creates run and effect IDs and records its own trace. Trace entries
are not accepted from the program's return data. The default Python and JavaScript replay ledgers are in-memory and process-local;
a host can inject a durable local atomic `claim(program_digest, run_id,
effect_id)` ledger. Custom Python and JavaScript ledger hooks are async and
bounded by the run/effect deadline. A repeated claim is refused. Hosts must
persist/reuse run IDs when they need replay checks across calls or restarts.
The separate recipient integration supplies a tested SQLite unique-claim
ledger; storage/providers are intentionally not part of this language core.

The ledger does not guarantee exactly-once remote behavior. After a timeout or
unclassified adapter failure, the status is `outcome_unknown`; the broker does
not auto-retry. Only an adapter that can positively confirm non-completion
should raise Python `KnownEffectFailure` or JavaScript `KnownEffectFailure`.
Provider callback success, accepted work, generated image, payment completion,
and the agent's final response are separate outcomes. The VM only reports that
the callback returned the value it supplied.

## Markdown skill boundary

`inspect_skill()` reads bounded Markdown as inert text and returns exactly
review-required data plus content-hash provenance. It does not parse
instructions, infer permissions, or create a runnable conversion. A real
program requires explicit `.lispy` source, freezing, and an app-local recipient
grant. This protects only hosts using this runtime; unrelated systems that
privilege raw Markdown remain outside the boundary.
Zap distribution never copies a pack's documentation into global skill or
agent instructions. A traded file contains bounded program data; its
permission requests are not authorizations.

## Residual risk

These controls are defense in depth, not a claim of zero risk. Local conformance
does not prove physical iOS/WKWebView behavior, production runtime attestation,
signature authority, durable-ledger correctness, provider egress enforcement,
adapter safety, provider-side idempotency, or real Comfy/GPU/image/payment
completion. Review every adapter and keep secrets/private memory out of packs.
