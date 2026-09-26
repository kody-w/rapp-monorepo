---
repo: kody-w/rapp-release-train
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d38837a61ba5e12f5bb00f3aa95d6e5107f5cbb2
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 6
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-canary
  - rapp-map
  - rapp-static-apis
---

# rapp-release-train: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-release-train.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-release-train` at `d38837a61b`](https://github.com/kody-w/rapp-release-train/tree/d38837a61ba5e12f5bb00f3aa95d6e5107f5cbb2) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `80398384c27f2b406b319a83f7aa247eb3750cd19a65757684b1b0bcc23487e9`.
- "experimental" mentions: 6 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-canary](rapp-canary.md) (markdown), [rapp-map](rapp-map.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-release-train` at `d38837a61b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-release-train --json` from the folder that holds both.
