---
repo: kody-w/rappvision-rappid-zoo
family: rappvision
line: Rappvision
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 0bc219c3ca35716af8da208c9c4f2e1d7a8fab38
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rappvision-rappid-zoo/pull/1
channel: newest
lifecycle: active
member_card: present
also_on:
  - worlds
links_to:
  - rapp-vision
  - rappid
---

# rappvision-rappid-zoo: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappvision-rappid-zoo.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappvision-rappid-zoo` at `0bc219c3ca`](https://github.com/kody-w/rappvision-rappid-zoo/tree/0bc219c3ca35716af8da208c9c4f2e1d7a8fab38) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `cf045ad46d4ac221e646b75cc7f60a03edee9fdec39a8b684c6ae19f683e6867`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappvision-rappid-zoo/blob/0bc219c3ca35716af8da208c9c4f2e1d7a8fab38/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappvision-rappid-zoo.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappvision-rappid-zoo.md).

On the map: the **Rappvision** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-vision](rapp-vision.md) (markdown), [rappid](rappid.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappvision-rappid-zoo` at `0bc219c3ca` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappvision-rappid-zoo --json` from the folder that holds both.
