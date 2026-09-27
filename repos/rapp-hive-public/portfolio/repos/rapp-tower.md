---
repo: kody-w/rapp-tower
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d67f816d35a3c5333c7b3639dae16ad5e22c6ee7
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: present
header_pr: https://github.com/kody-w/rapp-tower/pull/2
channel: newest
lifecycle: active
member_card: present
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

- Evidence: [`kody-w/rapp-tower` at `d67f816d35`](https://github.com/kody-w/rapp-tower/tree/d67f816d35a3c5333c7b3639dae16ad5e22c6ee7) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `89a8c03ddda979f689f284c985fad888fe032ecb87b89d6918e55a02443cfe08`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-tower/blob/d67f816d35a3c5333c7b3639dae16ad5e22c6ee7/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-tower.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-tower.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 7 portfolio repo(s): [rapp-canary](rapp-canary.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-map](rapp-map.md) (workflow), [rapp-roadmap](rapp-roadmap.md) (markdown), [rapp-second-brain](rapp-second-brain.md) (markdown), [rapp-toaster](rapp-toaster.md) (markdown), [rapp-train](rapp-train.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-tower` at `d67f816d35` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-tower --json` from the folder that holds both.
