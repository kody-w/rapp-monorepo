# OpenRappter beta ring

Beta points only at a **prerelease** promoted from a proven canary. This
repository is a maintained pointer, not a divergent code copy.

The current [manifest](.ring/manifest.json) records the real
`v0.1.0-beta.10` tag, exact commit, and measured GitHub archive SHA-256. It is
`unpublished` because no verified installable OpenRappter beta ring artifact is
available. `--ring beta` must fail closed rather than install something else.

Train: `nightly -> alpha -> canary -> beta -> stable`.

Validate with `node scripts/validate-manifest.mjs .ring/manifest.json beta`.

Distribution invariant: beta must descend from finalized nightly, alpha, and
canary receipts and is the final prerequisite before any stable/tag/npm/PyPI,
GitHub release, or installer-channel publication. Release-train tests enforce
the rule; there is no bypass flag.

Target `main` files are informational and cannot replay latest. Clients trust
only `openrappter-release-train/heads/beta.json`, its immutable finalized
receipt, and the exact target manifest commit named there.

Beta consumes the same tagged candidate bundle promoted by prior rings and
records one immutable sequence acknowledgement. Continuous snapshot candidates
remain non-stable and never satisfy the release constitution.
