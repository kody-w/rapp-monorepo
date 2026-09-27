---
repo: kody-w/rapp-support
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 899af6404d2c0ddc1281a59a72f206f5566ede0f
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-support/pull/10
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-installer
  - rapp-postflight
---

# rapp-support: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-support.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-support` at `899af6404d`](https://github.com/kody-w/rapp-support/tree/899af6404d2c0ddc1281a59a72f206f5566ede0f) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8a2f8930d0cf7cb693120be3330170a35c9f53ec287a11be292b9d56c2431cba`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-support/blob/899af6404d2c0ddc1281a59a72f206f5566ede0f/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-support.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-support.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [rapp-postflight](rapp-postflight.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-support` at `899af6404d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-support --json` from the folder that holds both.
