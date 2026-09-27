---
repo: kody-w/rapp-heir
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: ab99a260da51119f5e4474392ccc0109ca948f81
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 3
header: merged
header_pr: https://github.com/kody-w/rapp-heir/pull/2
channel: newest
lifecycle: active
member_card: present
---

# rapp-heir: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-heir.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-heir` at `ab99a260da`](https://github.com/kody-w/rapp-heir/tree/ab99a260da51119f5e4474392ccc0109ca948f81) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f130c7c4365580d96e0f1858c92c92092b80e1841fe9bf1014379713b8bd7a8c`.
- "experimental" mentions: 3 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp-heir/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-heir/blob/ab99a260da51119f5e4474392ccc0109ca948f81/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-heir.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-heir.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-heir` at `ab99a260da` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-heir --json` from the folder that holds both.
