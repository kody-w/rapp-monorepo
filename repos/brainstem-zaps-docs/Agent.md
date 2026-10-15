# Agent guide

Brainstem Zaps is an AI-first, capability-scoped LisPy profile for portable
agent expansion packs. Agents author `.lispy` programs as data; a fixed runtime
parses and executes them. This guide describes the language, frozen
record profile, Python and JavaScript virtual machines, capability broker,
legacy `BasicAgent` compiler, and conformance tests.

## Authoring checklist

1. Define `agent-name`, `agent-description`, `agent-parameters`, and a two-argument
   `agent-run` function.
2. Keep top-level definitions static: literal/quoted/list/dictionary constants
   or lambdas. All executable forms belong in function bodies.
3. Request only the named adapter operations the workflow needs. A request
   never grants authority.
4. Keep model and external asset identifiers content-pinned. Do not embed
   credentials, private memory, or machine-specific absolute paths.
5. Freeze, verify, and inspect the exact resulting digest before the receiving
   app configures a local grant. Any source, closure, runtime, or embedded asset
   change creates a different digest.
6. Use pure execution for untrusted drafts. Attach effects only through a
   recipient-local exact-digest grant, device policy, and installed callback
   contract in the VM's embedded capability kernel.

## Language conventions

The supported Scheme/LisPy subset includes `define`, `lambda`, `if`, `cond`,
`let`, `let*`, `begin`, `quote`, `set!`, `and`, `or`, lists, dictionaries, and
recursive higher-order functions. Its syntax follows familiar LisPy
conventions and keeps the owned LisPy/Brainstem implementation and licensed RAPP
primitives clearly attributed.
Unsupported forms fail closed rather than being delegated to a host evaluator.

The evaluator is deliberately bounded. Its idealized recursive semantics can
express a universal computation; each real run has finite fuel, stack,
allocation, numeric, string, output, and time limits.

## Security rules for contributors

- Never add `eval`, `exec`, dynamic code loading, reflection, shell, filesystem,
  or network primitives to the program environment.
- Never convert raw `SKILL.md` instructions into privileged prompts or
  permissions. `inspect_skill` is review-only and returns no runnable result.
- Never derive trust from an artifact signature, filename, embedded key, or
  self-reported execution trace.
- Keep adapter callbacks and grants outside program data; use exact names,
  versions, content pins, schemas, and per-run budgets.
- Preserve explicit `outcome_unknown` handling and never retry uncertain
  provider effects automatically.
- Keep the vendored RAPP implementation byte-identical to its pinned MIT
  reference; do not add RAPP hash tags or wire envelopes.
- Run `python -m unittest discover -s tests -v` and the Node/browser parity
  tests after runtime changes. Update the trusted runtime pin after changing
  the JavaScript core.

See `AGENTS.md`, `docs/security.md`, and `docs/conformance.md` for contribution
and validation expectations.
