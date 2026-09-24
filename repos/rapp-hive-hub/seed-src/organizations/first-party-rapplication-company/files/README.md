# First-Party Rapplication Company — starter case

Build a small chat-operated checklist rapplication with a careful internal
release process. **Every supplied scenario is SYNTHETIC.** This package contains
neither a company identity nor agents, live chat access, credentials, approvals,
signed records, customers, or a shipped product.

The usable reference is deliberately small: an in-memory checklist with a
fixed command grammar. It does not use a model or connect to a chat service.
An authorized host may later expose the same bounded behavior in its existing
chat. That integration and real internal use are tasks, not claims made here.

## Inspect first

Read `docs/operating-model.md`, `docs/pipeline.md`, and the casework task board.
The ready task is `configure-company`. Select a founder-CEO persona label and
real role holders through your existing owner-approved environment; do not
invent identities or treat role labels as grants.

The seven teams are `ceo-office`, `product`, `design`, `engineering`, `quality`,
`release`, and `support`. Shared inputs, forms, and accepted deliverables live
in the separate casework workspace. Native setup requires the exact dependency
pins in `seed.json`, a consumer-selected destination and owner label, and
approval of complete scaffold and pointer-registration plans. The Organization
holds pointers only. No setup, code execution, or publication follows from
downloading this package.

## Reproduce the reference after separate execution approval

From this starter directory, with Python 3.10+ and no third-party packages:

```sh
python3 -B reference/test_checklist.py
printf 'list\nadd package Check the public package\ndone package\nlist\n' \
  | python3 -B reference/checklist.py
```

Each line is one command and produces one JSON response. Supported commands:
`help`, `list`, `add <id> <text>`, and `done <id>`. State lasts only for that
process and disappears on exit. There is no automatic save, telemetry, network,
shell execution, installation, signing, or publication. Unknown or invalid
commands refuse without changing the checklist.

The tests prove only the reference's local behavior. They do not prove a chat
adapter, RAPP/1 record validity, authorization, real dogfooding, accessibility
of a host, or a release. Record missing capabilities as blockers.

## Work the case

1. Configure the charter and write a narrow product specification.
2. Build and freeze a complete candidate, support, tests, dependencies, and
   proposed public projection by exact hashes.
3. Use an explicitly authorized internal channel, then perform actual chat
   journeys. Collect minimal feedback; critique hidden details as well as copy.
4. Fix observed defects. A changed subject needs fresh internal release,
   dogfood, critique, and verification; old success cannot qualify new bytes.
5. Obtain independent verification and a separate external decision. The CEO
   may recommend shipment, never self-approve or merge.
6. Review the exact public distribution, nested privacy scan, licenses, PR
   text, and current CI. Promotion stops at a ready PR for the owner. Record
   completion only after the owner actually merges that checked head.

`templates/*.json` are unfilled data forms, including the decision-receipt
form. They are **not** canonical RAPP/1 frames, signed receipts, observations,
or authority. Production recording must use the existing trusted native
protocol, checker, identities, and approval mechanisms without adding envelope
fields or replacing the organization model. Keep private evidence private.
