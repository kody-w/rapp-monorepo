# Protected snapshot publication

`Aggregate the estate` generates and proves a complete snapshot before it
changes any remote ref. A successful run advances the deterministic
`automation/estate-snapshot` branch with a normal (never forced) push and
creates or updates its pull request to `main`. The concurrency group serializes
scheduled and manual runs. If generation, gating, staging, or token minting
fails, the prior remote snapshot is untouched. A rejected/racing push also
leaves the prior branch tip intact.

The workflow intentionally does not publish with `GITHUB_TOKEN`. Pushes made
with that token do not normally start downstream workflows, and PR workflows
can require manual approval. Instead, the pinned
`actions/create-github-app-token` step requests an installation token limited
to:

- repository contents: read and write
- pull requests: read and write
- metadata: read (implicit for every GitHub App)

Do not grant the App Actions, Workflows, Administration, or organization-wide
access. Install it only on `kody-w/rapp-monorepo`. The explicit
`permission-contents: write` and `permission-pull-requests: write` inputs make
token creation fail closed if the installation lacks either permission.
App-authored push and PR events start the `sdk` and GitGuardian checks normally.

## Credential setup

Create and install the least-privilege GitHub App, then set its client ID and
private key:

```bash
gh variable set SNAPSHOT_PUBLISHER_CLIENT_ID \
  --repo kody-w/rapp-monorepo --body '<github-app-client-id>'
gh secret set SNAPSHOT_PUBLISHER_PRIVATE_KEY \
  --repo kody-w/rapp-monorepo < path/to/github-app-private-key.pem
```

Until both values exist and the App is installed with both write permissions,
publication fails before any remote ref changes.

`python3 prove_publication.py` pins these workflow properties and the reviewed
ruleset shape in CI. Any change to publication credentials, branch targeting,
push semantics, pull-request ambiguity handling, bypass actors, or required
checks must update that executable contract and pass its mutation-resistant
proofs.

## Reviewed ruleset payload

`.github/rulesets/protected-main-publication.json` applies only to `main`. It:

- requires every change to arrive through a pull request;
- blocks deletion and non-fast-forward (force) updates;
- requires the `sdk` check from GitHub Actions App ID `15368`;
- requires `GitGuardian Security Checks` from GitGuardian App ID `46505`;
- requires the PR head to be current with `main`; and
- requires no approval, code-owner approval, or last-pusher approval, avoiding
  an impossible self-approval while still requiring a merge through a PR.

The integration IDs and check names were observed on this repository's PR
checks. `bypass_actors` is empty, so the publisher App cannot bypass `main`.

An administrator must review and apply the payload. This command is exact for
initial creation and is intentionally **not** run by a workflow:

```bash
gh api --method POST \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2026-03-10' \
  repos/kody-w/rapp-monorepo/rulesets \
  --input .github/rulesets/protected-main-publication.json
```

Before applying, confirm the contexts still originate from the pinned Apps:

```bash
HEAD_SHA="$(gh pr list --repo kody-w/rapp-monorepo --state open --limit 1 \
  --json headRefOid --jq '.[0].headRefOid')"
gh api "repos/kody-w/rapp-monorepo/commits/${HEAD_SHA}/check-runs" \
  --jq '.check_runs[] | [.name, .app.id, .app.slug] | @tsv'
```

Applying the ruleset requires repository Administration write permission. The
workflow never requests or receives that permission.
