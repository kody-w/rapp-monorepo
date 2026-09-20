# Hive shape

Profile: [`rapp-hive/1`](https://github.com/kody-w/rapp-work/blob/main/protocols/rapp-hive/1/SPEC.md)
Spec pin (§1 requires the exact SHA-256 in the signed §13 registry entry):

```
79aeef7bc5000f4a7b09483844b035c66adf817475540e583138f2e6b432c822
```

## Archetype

`open-source-infrastructure-foundation` — chosen because its mission is
"preserving honest failures and evidence-based release gates", which is exactly
what this lab is for, and its teams land on real lanes here: **triage** (failing
matrix cases), **release** (the matrix *is* the gate), **security** (installers
run as root on strangers' machines), **docs**, **maintainers**, **community**.

Rejected: `applied-invention-lab` (proving an invention, not sustaining
infrastructure); `one-person-conglomerate` (right for the estate, wrong for this
lab); `federation-prime-contractor` (hive-of-hives — premature).

## Channels

Exactly one channel has role `authority` (§3).

| Channel | Kind | Role | Why |
| --- | --- | --- | --- |
| your private repo | `github` | **authority** | §11 makes Git the contribution and reconciliation substrate |
| the NAS | `nas` | projection | §9: a mirror "never becomes authority by availability or timestamp" |

The always-on box produces the most frames, so it is precisely the one that must
not win by default. `bin/deploy.sh` is one-way and fails if the NAS does not
byte-match the repo.

## Dimensions and mutation keys

Each runner is a **dimension** (§7): its own RAPPID and immutable local frames,
never an authoritative Hive. A run's result is a candidate mutating a key like:

```
installer:<distro>:<image>
```

Keys are opaque text, not paths (§14.1). This matters: a workstation matrix
behind a pip proxy and the NAS matrix on open pypi mutate the **same** key. When
they disagree, Dream Catcher classifies it as a concurrent conflict requiring a
signed reconciliation instead of letting one silently overwrite the other. That
disagreement is real signal about the installer, and today it would just vanish.

## Boundaries

- `results/` is gitignored. Runs may test other estates' distros; that output
  stays local-only on the NAS. §2: data class travels with the data, not the box.
- `config.sh` is gitignored — §13 excludes live channel locators from anything
  shareable. Tracked code is the DOGG projection; `config.sh` is the estate.
- A public template cut from this repo gets a **distinct** RAPPID and its own
  `world_id`; hatching never joins the hatcher to this Hive (§13).
