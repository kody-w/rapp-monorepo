---
repo: kody-w/rapp-eternity
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 03e483d3daba7d8c6d83031c134991211bd3676b
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-eternity/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
---

# rapp-eternity: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-eternity.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-eternity` at `03e483d3da`](https://github.com/kody-w/rapp-eternity/tree/03e483d3daba7d8c6d83031c134991211bd3676b) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `bef95cf6694c053620d52e36998f6eebdd0b46930ff9d01ba3a58ad253adac23`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-eternity/blob/03e483d3daba7d8c6d83031c134991211bd3676b/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-eternity.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-eternity.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-eternity` at `03e483d3da` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-eternity --json` from the folder that holds both.
