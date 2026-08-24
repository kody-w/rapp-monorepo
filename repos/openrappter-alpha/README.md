# OpenRappter alpha ring

Alpha is an **explicit early promotion** from a vetted nightly. It never follows
a branch automatically. This repository is a maintained pointer, not a source
copy: OpenRappter code remains in [`kody-w/openrappter`](https://github.com/kody-w/openrappter).

The current [closed manifest](.ring/manifest.json) is `disabled`: the recorded
commit and GitHub archive SHA-256 are real, but no promotion receipt or
installable alpha artifact exists. `--ring alpha` must therefore fail closed.

Train: `nightly -> alpha -> canary -> beta -> stable`.

Validate with `node scripts/validate-manifest.mjs .ring/manifest.json alpha`.

Distribution invariant: alpha must descend from a finalized nightly receipt
and is step 2 of the machine-required nightly → alpha → canary → beta chain.
No stable/tag/registry/release/installer path may bypass it; authority is the
release-train tests, not prose.

Target `main` files are informational and never define latest. Clients start
from the monotonic `openrappter-release-train/heads/alpha.json`, then verify its
immutable receipt and exact target manifest commit.

The worker consumes only finalized-sequence+1 and records an immutable
`.ring/applied/<sequence>-<request-id>.json`; it never reads the removed
single acknowledgement path.
