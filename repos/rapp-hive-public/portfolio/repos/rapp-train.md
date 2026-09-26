---
repo: kody-w/rapp-train
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d271983be1fb7fda3d58622f80497089c524f8d7
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-canary
  - rapp-installer
---

# rapp-train: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-train.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-train` at `d271983be1`](https://github.com/kody-w/rapp-train/tree/d271983be1fb7fda3d58622f80497089c524f8d7) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9fa94362c45c3169395eca4399fd9707c417b42336fe75fe11474bb98845580f`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-canary](rapp-canary.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 7: [rapp-docs](rapp-docs.md), [rapp-holo](rapp-holo.md), [rapp-keyring](rapp-keyring.md), [rapp-light](rapp-light.md), [rapp-monorepo](rapp-monorepo.md), [rapp-second-brain](rapp-second-brain.md), [rapp-tower](rapp-tower.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-train` at `d271983be1` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-train --json` from the folder that holds both.
