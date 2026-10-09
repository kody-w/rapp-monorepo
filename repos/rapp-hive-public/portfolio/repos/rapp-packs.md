---
repo: kody-w/rapp-packs
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: a2d60e52eefae322a7489f1014b5385098ba3720
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAR
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-packs: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-packs.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-packs` at `a2d60e52ee`](https://github.com/kody-w/rapp-packs/tree/a2d60e52eefae322a7489f1014b5385098ba3720) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `bc54dfebed0de35a8e275bacee83dcd59c219099a82ee2464877dc068402c747`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-packs/blob/a2d60e52eefae322a7489f1014b5385098ba3720/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-packs.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-packs.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [RAR](RAR.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-packs` at `a2d60e52ee` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-packs --json` from the folder that holds both.
