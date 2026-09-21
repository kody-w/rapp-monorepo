# RAPP Hive Hub

**[Open RAPP Hive Hub](https://kody-w.github.io/rapp-hive-hub/hub/)** ·
[Give your AI the skill](https://kody-w.github.io/rapp-hive-hub/hub/skills/hive-network/SKILL.md) ·
[Static API](https://kody-w.github.io/rapp-hive-hub/api/hive-hub/v1/index.json)

The RAPP-focused version of [Hive Hub](https://github.com/kody-w/hive-hub):
find a RAPP Work organization starter, verify its exact package and protocol,
then plan native Organizations and Workspaces with the AI you already use.

Ten downloadable starters include the One-Person Conglomerate, Enterprise
Transformation Firm, Product Launch Company, Open-Source Infrastructure
Foundation, Applied Invention Lab, Independent Game Studio, Micro-Manufacturing
Company, Public-Source Intelligence Bureau, Turnaround Firm, and Federation
Prime Contractor. Each includes scoped teams, a synthetic case, original
artifacts, dependency-linked tasks, a deterministic ZIP, and a verified join card.
These are **starter packages, not running agents or activated companies**.

## Start with an outcome

1. Open the [catalog](https://kody-w.github.io/rapp-hive-hub/hub/#organizations)
   or give your existing AI the linked `hive-network` skill as material to
   inspect. Tell it what you want to accomplish.
2. Choose a seed. Verify the complete Dial Record ID, protocol fingerprint,
   learning bundle, conformance contract, adapter, ZIP digest, and file inventory.
3. Choose an owner label and a new local destination. Use the exact locally
   trusted RAPP Work SDK to plan native setup.
4. Review the complete bounded effects and exact plan hashes before applying.
   Claim a ready task and attach real acceptance evidence.

Reading a skill, downloading a seed, scanning a QR, or saving a local
subscription never approves execution, initializes an organization, or grants
source access. Browser-only AI clients can inspect but cannot claim local setup.

## RAPP by composition, not by rewriting the core

| Layer | Contract |
| --- | --- |
| Product | RAPP-first catalog, native setup workflow, and AI skill |
| Organization seeds | `rapp-work/1`, using the `rapp-work-sdk/1` workspace profile |
| RAPP Work SDK | `kody-w/rapp-work` at `29ead23b21645f8d7682ee00414930ffa9ce0ca6` |
| RAPP/1 | `kody-w/rapp-1` at `591e014ad39e223b00ab343ae26e5d9a867ebeee` |
| Discovery | Unmodified protocol-neutral `hive_hub` core and `api/hive-hub/v1` wire format |
| Existing adapters | RAPP delegation, RAPPID, Payphone, historical Hub, filesystem, and GitHub |

The SDK and specification digests are included in each seed and the AI skill.
Installed RAPP tooling remains the authority; the Hub does not recreate it.
Organization state holds pointers to scoped team and casework Workspaces.
No SDK is silently downloaded or executed, and no generic compatibility is inferred.

This distribution retains the upstream laboratory as an explicitly labeled
generic subscription example. Upstream content identities, exact source
revisions, locked compatibility cards, historical receipts, and seed provenance
are preserved; references to `hive-hub` in those objects are intentional.
Current site indexes, join links, QR destinations, and the contribution workflow
point to **this** repository and its Pages site.

## Safety boundaries

Chants, URLs, repositories, and QR codes are locators, not authority.
Every Hive declares an exact protocol fingerprint, learning bundle,
conformance contract, and adapter. Downloaded content stays inert until
separately verified and approved.

Existing source ACLs remain in charge. `acl-only` is the default; optional
`acl+qr` is a second factor after ACL and contains no repository credentials
or private keys. The Hub adds no collaborators or credentials. Unauthorized
and nonexistent private targets are indistinguishable. Public builds read
only the explicit pinned public manifest, never private dialbooks.

## Build and contribute

Requires Node.js 20.18+ and Python 3.10+ (`python3` on PATH).

```bash
npm ci --ignore-scripts
npm run verify
PYTHONPATH=src:. python3 -B -m unittest discover -s tests -t .
python3 -B scripts/check_public_release.py
npm run build:site
```

Author public inputs and templates, not generated `hub/` or `api/` files.
After intentional source changes, run `npm run sync:release`, `npm run build`,
and `python3 -B scripts/build_release_manifest.py`, then verify. Review generated
changes and immutable receipts before committing.

Pages serves the root of the separate `gh-pages` branch, containing only the
verified `site/` artifact. The source lives on `main`. Rebuild and verify before
publishing an updated artifact; never publish the repository root as the site.
The artifact commit records its source commit and public hash-manifest digest.

The existing publisher login can publish source and configure Pages but lacks
GitHub's `workflow` scope. CI and automatic deployment definitions are therefore
preserved under `.github/workflow-templates/`, **not active workflows**. To enable
automation later, explicitly authorize workflow publication, move the templates
to `.github/workflows/`, and switch the Pages build type from branch deployment
to GitHub Actions. Until then, run the verification commands above before each
manual publication.

The Python module and CLI keep their upstream `hive_hub` / `hive-hub` names.
This repository does **not** publish a competing Python package or publish
upstream releases to PyPI. Inherited release documents describe the underlying
Hive Hub implementation, not a new RAPP SDK release.

## Provenance and deeper reference

Based on public upstream commit
[`1db94d2b1b5d9d4fb6f9d2865c3a2fe543875c31`](https://github.com/kody-w/hive-hub/commit/1db94d2b1b5d9d4fb6f9d2865c3a2fe543875c31).
The MIT license and upstream history are retained. The generic repository is
independent and unchanged.

Inherited documentation remains useful for [organization seeds](docs/ORGANIZATION_SEEDS.md),
[CLI commands](docs/CLI.md), [contracts](docs/CONTRACTS.md), and
[security boundaries](docs/SECURITY.md). Its upstream URLs identify the original
distribution; use this README and this site's `llms.txt` for RAPP Hive Hub entry
points. See [AGENTS.md](AGENTS.md) for the engineering contract.
