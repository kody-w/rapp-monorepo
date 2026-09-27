---
repo: kody-w/rapp-wiki-observatory
family: learn
line: Learn & Docs
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c284d0633edcab12412b79b8c98d4059f83d47d1
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-wiki-observatory/pull/1
channel: newest
lifecycle: active
member_card: present
---

# rapp-wiki-observatory: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-wiki-observatory.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-wiki-observatory` at `c284d0633e`](https://github.com/kody-w/rapp-wiki-observatory/tree/c284d0633edcab12412b79b8c98d4059f83d47d1) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `86132d970403b6afe65241a8f2faf6831556cd08cd58135a55778540622479e0`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-wiki-observatory/blob/c284d0633edcab12412b79b8c98d4059f83d47d1/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-wiki-observatory.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-wiki-observatory.md).

On the map: the **Learn & Docs** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-wiki-observatory` at `c284d0633e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-wiki-observatory --json` from the folder that holds both.
