---
repo: kody-w/rapp-hive-hub-join
family: hive
line: Hive
wave: 1
status: certified
verdict: CLEAN
evidence_commit: 3598da15c3d5c4e6d6fbb79c2dd1f741b88df0b8
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-hive-hub-join/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - hive-hub-mcp
---

# rapp-hive-hub-join: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hive-hub-join.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-hive-hub-join` at `3598da15c3`](https://github.com/kody-w/rapp-hive-hub-join/tree/3598da15c3d5c4e6d6fbb79c2dd1f741b88df0b8) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3d2b10e20b8ebaac91eaf915af2828613bcb9a629ef626a9dd695696dc2d98e0`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-hive-hub-join/blob/3598da15c3d5c4e6d6fbb79c2dd1f741b88df0b8/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-hive-hub-join.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-hive-hub-join.md).

On the map: the **Hive** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [hive-hub-mcp](hive-hub-mcp.md) (markdown).
Linked from 2: [hive-hub-mcp](hive-hub-mcp.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-hive-hub-join` at `3598da15c3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-hive-hub-join --json` from the folder that holds both.
