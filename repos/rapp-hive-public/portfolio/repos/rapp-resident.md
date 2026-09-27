---
repo: kody-w/rapp-resident
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 1d7a0e370bd6cb68d0eaf4ab7b72922a13e8ffd5
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-resident/pull/4
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-commons
---

# rapp-resident: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-resident.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-resident` at `1d7a0e370b`](https://github.com/kody-w/rapp-resident/tree/1d7a0e370bd6cb68d0eaf4ab7b72922a13e8ffd5) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `120ee01a4ff69c46e98871cdeea45309f8a290397e477442ed63b0c2ab5d9325`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-resident/blob/1d7a0e370bd6cb68d0eaf4ab7b72922a13e8ffd5/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-resident.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-resident.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-commons](rapp-commons.md) (markdown).
Linked from 5: [RAPP-Bible](RAPP-Bible.md), [rapp-god-forum](rapp-god-forum.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [rappterbook-commons](rappterbook-commons.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-resident` at `1d7a0e370b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-resident --json` from the folder that holds both.
