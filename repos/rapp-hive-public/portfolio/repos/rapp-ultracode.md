---
repo: kody-w/rapp-ultracode
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 1f39faee45d1fba175e85a6f187a16ffbb65cf6c
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-ultracode/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-dynamic-workflows
---

# rapp-ultracode: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-ultracode.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-ultracode` at `1f39faee45`](https://github.com/kody-w/rapp-ultracode/tree/1f39faee45d1fba175e85a6f187a16ffbb65cf6c) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `20f84391ba7e751f215ed151a4d4d19e8340093d2e2be4ed72fb17c0e921ac8c`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-ultracode/blob/1f39faee45d1fba175e85a6f187a16ffbb65cf6c/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-ultracode.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-ultracode.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-dynamic-workflows](rapp-dynamic-workflows.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-ultracode` at `1f39faee45` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-ultracode --json` from the folder that holds both.
