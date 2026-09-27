---
repo: kody-w/pkstop-the-bean
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 7964814db72efdd29d8135ed303ed24023296193
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: present
header_pr: https://github.com/kody-w/pkstop-the-bean/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-installer
  - RAPPcards
---

# pkstop-the-bean: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/pkstop-the-bean.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/pkstop-the-bean` at `7964814db7`](https://github.com/kody-w/pkstop-the-bean/tree/7964814db72efdd29d8135ed303ed24023296193) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `0f8738c1cc5b9b34b89e02c0eba05d14c613e4d556be8f9ce42192257a67b089`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/pkstop-the-bean/blob/7964814db72efdd29d8135ed303ed24023296193/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/pkstop-the-bean.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/pkstop-the-bean.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/pkstop-the-bean` at `7964814db7` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py pkstop-the-bean --json` from the folder that holds both.
