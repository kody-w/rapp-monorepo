---
repo: kody-w/rapp-herdr
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: fcbe1e875e45eca5fcd3881b5bbf2e51a40a01d3
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-herdr/pull/2
channel: newest
lifecycle: active
member_card: present
---

# rapp-herdr: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-herdr.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-herdr` at `fcbe1e875e`](https://github.com/kody-w/rapp-herdr/tree/fcbe1e875e45eca5fcd3881b5bbf2e51a40a01d3) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `5d43ca95a6a0235ee78965178331549e979e098039ac7c2d4b74422d9b065fc4`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-herdr/blob/fcbe1e875e45eca5fcd3881b5bbf2e51a40a01d3/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-herdr.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-herdr.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-omarchy](rapp-omarchy.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-herdr` at `fcbe1e875e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-herdr --json` from the folder that holds both.
