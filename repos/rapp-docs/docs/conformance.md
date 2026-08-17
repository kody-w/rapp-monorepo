# Conformance — why every RAPP repo ships a gate

A claim in a README is a claim. A claim with a gate is a property.

Every repository in the RAPP ecosystem ships a `conformance.py` that proves its
own README against its own running code. Nothing passes on inspection, and
nothing passes because a document says so.

```bash
python3 conformance.py            # human-readable
python3 conformance.py --json     # for CI
```

Exit codes: `0` all passed · `1` one or more failed · `2` could not run.

## The current gates

| Repo | Checks | Proves |
|---|---|---|
| [rapp-1](https://github.com/kody-w/rapp-1) | 18 | the protocol suite — identity, canonicalization, frames, the egg |
| [rapp-keyring](https://github.com/kody-w/rapp-keyring) | 12 | no network, no argv exposure, redaction, tamper-evident audit |
| [rapp-light](https://github.com/kody-w/rapp-light) | 14 | no kernel, fail-closed, capability verification, credential refusal |
| [openrappter](https://github.com/kody-w/openrappter) | 9 | the agent contract, kernel wire parity, portability |

## What makes a good check

**Prove it against the running thing.** RAPP Keyring's C1 claims the program
opens no network connections. It does not grep for `import socket` and stop
there — it runs the CLI with `socket()` booby-trapped and fails if the process
exits with the trap code.

**Attack your own claim.** C2 claims secret values never reach `argv`. It stores
a secret while taking hundreds of thousands of `ps` snapshots, and fails if the
marker ever appears in any process's arguments.

**Check the boring direction too.** A control that fires on `json.loads` gets
switched off, and then it protects nothing. rapp-light's L4 exists solely to
prove that ordinary code raises no finding.

**Run the gate on yourself.** Three real defects in this ecosystem were found by
a gate examining its own repository:

- rapp-light's credential organ under-declared `filesystem-write` — it appends
  to the audit record. Check 4 refused the organ until it was fixed.
- rapp-light's L1 grepped for kernel markers as text and failed on the file
  containing those markers as data. It now reads the syntax tree, which is the
  same false-positive discipline L4 exists to enforce.
- OpenRappter's `demo_recorder_agent` hard-imported a sibling agent at module
  level and would not have loaded standalone.

A gate that has never failed on its own author has not been tried.

## Suppression must be reviewable

A scanner that cannot be silenced gets switched off entirely. RAPP Keyring's
credential scan accepts an inline pragma, and requires a reason, so the
suppression is visible in a diff rather than invisible:

```python
# rapp-keyring: allow synthetic PEM fixture, not a real key
```

`--no-pragma` ignores every suppression, so an auditor can always see the full
picture.

## No silent caps

If a gate bounds its own coverage — sampling, top-N, skipping when a dependency
is absent — it reports `SKIP`, never `PASS`. Silent truncation reads as "covered
everything" when it did not.
