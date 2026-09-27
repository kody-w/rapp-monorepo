---
repo: kody-w/pkstop-national-mall
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: d857c075ddcb7736655452a7ad352e5ec64a2b48
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/pkstop-national-mall/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-installer
  - RAPPcards
---

# pkstop-national-mall: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/pkstop-national-mall.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/pkstop-national-mall` at `d857c075dd`](https://github.com/kody-w/pkstop-national-mall/tree/d857c075ddcb7736655452a7ad352e5ec64a2b48) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `b8e392624c96dafe381d9a8c695d38a4dc111e60ed15c3e707c407f5ce0712f7`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/pkstop-national-mall/blob/d857c075ddcb7736655452a7ad352e5ec64a2b48/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/pkstop-national-mall.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/pkstop-national-mall.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/pkstop-national-mall` at `d857c075dd` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py pkstop-national-mall --json` from the folder that holds both.
