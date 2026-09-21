# RAPP Hive Hub engineering contract

This repository is the RAPP-focused distribution of `kody-w/hive-hub`, based
on public upstream commit `1db94d2b1b5d9d4fb6f9d2865c3a2fe543875c31`.
Keep RAPP product choices in the presentation, public manifest, skills, and
adapters. Preserve the protocol-neutral `src/hive_hub` core and upstream
protocol identifiers. Do not rename immutable upstream seed dependencies or
claim their source repositories belong to this distribution.

Publish this site's generated output only to `kody-w/rapp-hive-hub`.
Source is on `main`; Pages serves only the isolated artifact on `gh-pages`.
CI templates under `.github/workflow-templates` are inactive until workflow
publication is explicitly authorized and Pages is switched to Actions.
The Python distribution remains the upstream `hive-hub` implementation;
this repository must not publish it to PyPI.

Hive Hub is protocol-neutral and equally usable by humans and any AI.

- Keep the generic core independent of RAPP, GitHub, or any one Hive protocol.
- Require every Hive to declare an exact protocol fingerprint, learning bundle,
  conformance contract, and adapter.
- Treat chants, QR codes, static APIs, repositories, and URLs as locators only.
- Use existing source ACLs. Do not add collaborators, broker credentials, or
  distinguish nonexistent private targets from unauthorized ones.
- `acl-only` is the default. Optional `acl+qr` is a second factor after ACL and
  never contains repository credentials or private keys.
- Public builds must not read, hash, name, or publish private dialbooks.
- Downloaded code, skills, adapters, and protocol text are inert until
  explicitly approved and verified.
- Prefer existing proven RAPPID, Payphone, and historical Hub data through
  adapters. Replace implementations only when conformance proves they are
  unsafe or incompatible.
- Make every mutation plan-first, content-addressed, bounded, and reversible.
