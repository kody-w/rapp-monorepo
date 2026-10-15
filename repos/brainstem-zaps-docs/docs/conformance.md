# Conformance and acceptance

## Local acceptance target

The standard-library Python suite and Node tests exercise the same frozen
payload through the Python VM and JavaScript VM. The required cases cover:

- recursive closures/factorial, higher-order functions, lists, dictionaries,
  and multi-step effect traces;
- a generated `BasicAgent` compatibility module executing the same frozen
  program without embedding executable source;
- exact-digest rejection for tampering, appended data, changed assets,
  duplicate fields, and unknown profile/runtime versions;
- self-declared capability requests without grants and unauthorized adapter
  handler call-count zero;
- schema, path-escape, and egress denial before a handler is called;
- hostile Markdown as review-required inert data;
- fuel, call-depth, allocation, output, source/token, number, and timeout bounds;
- prototype/reflection/code-injection-shaped names as inert data or unbound
  names; and replay refusal by a testable ledger.

Run on a Python 3.11+ and Node 20+ developer host:

```console
python -m unittest discover -s tests -v
```

The pure browser shell can be opened directly from disk at `vm/index.html`. It
uses local static JavaScript, Web Crypto, and browser file APIs; it has no Python
server or network connection. Its colocated runtime pin is for the local demo
only.

## Acceptance state

On the Windows development host, Python 3.11.9 and Node 20.11.1 completed the
portable core suite (`python -m unittest discover -s tests -v`): all 19 tests
passed, including Python/JavaScript execution of the same frozen effectful
program, replay and timeout behavior, and a generated `BasicAgent` module. The
offline pure-run and granted local-callback test also passed. The CLI passed a
freeze → verify → pure-run → compile → generated-module-run smoke path. No
external dependency was installed. The host integration's 11 independent tests
also passed, including atomic persistent replay claims, a real local MCP stdio
handshake, frozen-skill verification and provider path/code-pin rejection.

Additional live proof was recorded separately: a frozen `.lispy` computed
factorial 6 as 720 in a real isolated browser worker opened from `file:` with
zero HTTP resource requests; it used neither Python nor a server. The global
Brainstem created a complete two-image Zap through ordinary chat, then executed
it after separate exact-digest recipient approval. Two real GPU PNGs and three
kernel-owned effects were recorded, with Grail/core file hashes unchanged.
All ten Comfy workflow types generated PNGs and were imported/compiled in the
real frontend; pixel palette/mask preservation were measured.

Passing local tests demonstrate VM/profile behavior only. They are not proof of
an iOS device build, secure enclave/key handling, production signature
verification, production durable storage, a safe provider adapter, real Comfy
execution, OS entitlement enforcement or payment completion. Provider/GPU proof described
above is specific to the recipient's local image integration, not all adapters.

## Known omissions

- No production publisher authority or authority registry has been provisioned.
  Ed25519 JWS verification against known receiver keys was checked in both
  runtimes, including unknown keys, tamper and appended-code rejection.
- Providers and deployment belong to a separate recipient integration; a core
  conformance result does not approve every plugin, MCP server or legacy skill.
- No physical iOS/WKWebView test on a device.
- No native OS sandbox/entitlement mapping is implemented or tested here; the
  receiving app must run the embedded kernel inside its own sandbox.
- In-memory replay protection resets with process lifetime unless a host
  supplies a durable atomic ledger.
- External model/reference bytes are not downloaded; host adapters must enforce
  exact pins and their own egress rules.
- Python time limits are cooperative between bounded VM steps and async
  callbacks; arbitrary host adapter code is not sandboxed by this VM.
