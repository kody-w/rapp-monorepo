---
repo: kody-w/rapp-remix
family: rappvision
line: Rappvision
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 714b891246459972b4155afa1b9d7c349fc960d4
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-remix/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-carts
  - rapp-rock-tumbler
  - rapp-vision
---

# rapp-remix: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-remix.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-remix` at `714b891246`](https://github.com/kody-w/rapp-remix/tree/714b891246459972b4155afa1b9d7c349fc960d4) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `57ea6aaa640f60f3022c08400ef13a3fcdd32e43656596560ee752f1cf4b8e2c`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-remix/blob/714b891246459972b4155afa1b9d7c349fc960d4/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-remix.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-remix.md).

On the map: the **Rappvision** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-carts](rapp-carts.md) (markdown), [rapp-rock-tumbler](rapp-rock-tumbler.md) (markdown), [rapp-vision](rapp-vision.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-remix` at `714b891246` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-remix --json` from the folder that holds both.
