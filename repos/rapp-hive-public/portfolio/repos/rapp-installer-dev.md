---
repo: kody-w/rapp-installer-dev
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: a18c6f8ee19abe97350c731434a5d7f8aaecae3d
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 8
header: missing
channel: newest
lifecycle: active
also_on:
  - rapp1-core
links_to:
  - CommunityRAPP
  - RAPP
  - rapp-installer
  - rapp-installer-canary
---

# rapp-installer-dev: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-installer-dev.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-installer-dev` at `a18c6f8ee1`](https://github.com/kody-w/rapp-installer-dev/tree/a18c6f8ee19abe97350c731434a5d7f8aaecae3d) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `d237bb164f4f2b3d4bf3ab1fe15231e6c1c1e29413f5e226072633a9e86ca349`.
- "experimental" mentions: 8 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line, and also RAPP/1 Core ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-installer-canary](rapp-installer-canary.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-installer-dev` at `a18c6f8ee1` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-installer-dev --json` from the folder that holds both.
