---
repo: kody-w/rapp-alpha
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 44be78a718cab332937a4fe5fd8c99c7e8bc573e
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 12
header: missing
channel: newest
lifecycle: active
links_to:
  - CommunityRAPP
  - rapp-installer
  - rapp-nightly
  - RAR
---

# rapp-alpha: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-alpha.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-alpha` at `44be78a718`](https://github.com/kody-w/rapp-alpha/tree/44be78a718cab332937a4fe5fd8c99c7e8bc573e) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `85ebf01ddf36eee6264080690901d64fd3ae8c51406ae7eb17e434f279730b76`.
- "experimental" mentions: 12 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-nightly](rapp-nightly.md) (pin), [RAR](RAR.md) (markdown).
Linked from 3: [rapp-beta](rapp-beta.md), [rapp-canary](rapp-canary.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-alpha` at `44be78a718` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-alpha --json` from the folder that holds both.
