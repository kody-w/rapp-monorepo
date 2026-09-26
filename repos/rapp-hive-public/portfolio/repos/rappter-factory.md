---
repo: kody-w/rappter-factory
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 652702855bcde92e3b2aeac5712dcd35971f54a0
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
links_to:
  - rappterbook
---

# rappter-factory: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-factory.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-factory` at `652702855b`](https://github.com/kody-w/rappter-factory/tree/652702855bcde92e3b2aeac5712dcd35971f54a0) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c05ad7ceaf78050255980042e63bb0d8d899cffd028f6ad2dc30b5380389a75f`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rappterbook](rappterbook.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-factory` at `652702855b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-factory --json` from the folder that holds both.
