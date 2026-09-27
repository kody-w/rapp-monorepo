---
repo: kody-w/rapp-version-selector
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 0dab2506284f53b08085e26bde0432e5c18ab775
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 9
header: present
header_pr: https://github.com/kody-w/rapp-version-selector/pull/5
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-installer
---

# rapp-version-selector: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-version-selector.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-version-selector` at `0dab250628`](https://github.com/kody-w/rapp-version-selector/tree/0dab2506284f53b08085e26bde0432e5c18ab775) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c3ac3198623fdae346277722da083539abd2fcc1bf3de31ca1354ff717ca1bc5`.
- "experimental" mentions: 9 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-version-selector/blob/0dab2506284f53b08085e26bde0432e5c18ab775/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-version-selector.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-version-selector.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-version-selector` at `0dab250628` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-version-selector --json` from the folder that holds both.
