---
repo: kody-w/rapp-cortex
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 01e10a4dfd9be675173c536b3b9e84a0601c52e9
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-cortex/pull/1
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-flight-deck
  - rapp-installer
  - rapp-rings
  - rapp-twin
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-cortex: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-cortex.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-cortex` at `01e10a4dfd`](https://github.com/kody-w/rapp-cortex/tree/01e10a4dfd9be675173c536b3b9e84a0601c52e9) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `22298a3e1559322aa1ada572db1a06d35d57011ebd64b2055872bf3d589872c3`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-cortex/blob/01e10a4dfd9be675173c536b3b9e84a0601c52e9/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-cortex.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-cortex.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-cortex` at `01e10a4dfd` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-cortex --json` from the folder that holds both.
