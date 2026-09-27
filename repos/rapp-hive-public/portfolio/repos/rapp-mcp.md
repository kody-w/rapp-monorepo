---
repo: kody-w/rapp-mcp
family: connect
line: Brainstem Connect
wave: 2
status: certified
verdict: CLEAN
evidence_commit: cd22b1e964aabc6a71b8b401deb19d2de1f77086
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: present
header_pr: https://github.com/kody-w/rapp-mcp/pull/7
lts_version: "cd22b1e"
lts_commit: cd22b1e964aabc6a71b8b401deb19d2de1f77086
lts_source: known
channel: rapp1-lts
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-static-apis
---

# rapp-mcp: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-mcp.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **LTS:** [`cd22b1e`](https://github.com/kody-w/rapp-mcp/tree/cd22b1e964aabc6a71b8b401deb19d2de1f77086) (commit `cd22b1e964`, from the network's built-in known pins, until the estate publishes its LTS pins). **Channel:** `rapp1-lts`: it has a long-term-support pin, so the network builds on that commit; its newer commits are the newest channel.

- Evidence: [`kody-w/rapp-mcp` at `cd22b1e964`](https://github.com/kody-w/rapp-mcp/tree/cd22b1e964aabc6a71b8b401deb19d2de1f77086) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ca7c5b2255a12be48ca7dbcb0be450c21be3efebc6ad96af194c1b74d633b811`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-mcp/blob/cd22b1e964aabc6a71b8b401deb19d2de1f77086/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-mcp.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-mcp.md).

On the map: the **Brainstem Connect** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (markdown).
Linked from 14: [racon](racon.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-brainstem-sdk](rapp-brainstem-sdk.md), [rapp-carts](rapp-carts.md), [rapp-commons](rapp-commons.md), [rapp-doorman](rapp-doorman.md), [rapp-monorepo](rapp-monorepo.md), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md), [RAPP-Network](RAPP-Network.md), [rapp-spine](rapp-spine.md), [rapp-static-apis](rapp-static-apis.md), [rapp-vneighborhood](rapp-vneighborhood.md), [RAPP_Store](RAPP_Store.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-mcp` at `cd22b1e964` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-mcp --json` from the folder that holds both.
