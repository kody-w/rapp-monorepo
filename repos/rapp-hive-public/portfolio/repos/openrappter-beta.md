---
repo: kody-w/openrappter-beta
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c29c6d4413a337dfad53c35b841d5dd12cddc7ca
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
also_on:
  - openrappter
links_to:
  - openrappter-release-train
---

# openrappter-beta: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/openrappter-beta.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/openrappter-beta` at `c29c6d4413`](https://github.com/kody-w/openrappter-beta/tree/c29c6d4413a337dfad53c35b841d5dd12cddc7ca) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `68c00ff77ca8f0e25bb06eb2dc308af0e3c8bfe93682613d3e216f14860bf111`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line, and also OpenRappter ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [openrappter-release-train](openrappter-release-train.md) (workflow).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/openrappter-beta` at `c29c6d4413` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py openrappter-beta --json` from the folder that holds both.
