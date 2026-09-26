---
repo: kody-w/rapp-tower
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: ad7192a86cfb96619ee546a0dbb90a77eea17257
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-canary
  - rapp-installer
  - rapp-map
  - rapp-roadmap
  - rapp-second-brain
  - rapp-toaster
  - rapp-train
---

# rapp-tower: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-tower.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-tower` at `ad7192a86c`](https://github.com/kody-w/rapp-tower/tree/ad7192a86cfb96619ee546a0dbb90a77eea17257) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `89a8c03ddda979f689f284c985fad888fe032ecb87b89d6918e55a02443cfe08`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 7 portfolio repo(s): [rapp-canary](rapp-canary.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-map](rapp-map.md) (workflow), [rapp-roadmap](rapp-roadmap.md) (markdown), [rapp-second-brain](rapp-second-brain.md) (markdown), [rapp-toaster](rapp-toaster.md) (markdown), [rapp-train](rapp-train.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-tower` at `ad7192a86c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-tower --json` from the folder that holds both.
