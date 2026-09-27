---
repo: kody-w/rapp-infrastructure-city
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 1d62cc038f049490a87ab8e73a3efecf6b8aa486
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-infrastructure-city/pull/7
channel: newest
lifecycle: active
member_card: present
---

# rapp-infrastructure-city: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-infrastructure-city.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-infrastructure-city` at `1d62cc038f`](https://github.com/kody-w/rapp-infrastructure-city/tree/1d62cc038f049490a87ab8e73a3efecf6b8aa486) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `fa1dc73a00d431adbc6322c17682397097daf3d1007d0723e2d7f8959da84c47`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-infrastructure-city/blob/1d62cc038f049490a87ab8e73a3efecf6b8aa486/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-infrastructure-city.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-infrastructure-city.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-infrastructure-city` at `1d62cc038f` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-infrastructure-city --json` from the folder that holds both.
