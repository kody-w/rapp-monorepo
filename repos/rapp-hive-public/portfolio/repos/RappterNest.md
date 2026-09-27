---
repo: kody-w/RappterNest
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 8da2b076e2ddccce17ef3d75e57f00cb13c9bc57
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/RappterNest/pull/4
channel: newest
lifecycle: active
member_card: present
---

# RappterNest: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RappterNest.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RappterNest` at `8da2b076e2`](https://github.com/kody-w/RappterNest/tree/8da2b076e2ddccce17ef3d75e57f00cb13c9bc57) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `02650bd6dc540d900136a861a67cf5fed07a91f1dec4adc5f6cc4f5c1b38e163`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/RappterNest/pull/4).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/RappterNest/blob/8da2b076e2ddccce17ef3d75e57f00cb13c9bc57/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/RappterNest.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/RappterNest.md).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RappterNest` at `8da2b076e2` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RappterNest --json` from the folder that holds both.
