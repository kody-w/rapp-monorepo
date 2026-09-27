---
repo: kody-w/obsidian-binder
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 66a6254212c9f502d88513a6d9454502f9ce042c
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/obsidian-binder/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPPcards
  - twin-binder
---

# obsidian-binder: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/obsidian-binder.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/obsidian-binder` at `66a6254212`](https://github.com/kody-w/obsidian-binder/tree/66a6254212c9f502d88513a6d9454502f9ce042c) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f94703efdf965c55e05ba43ed7f09046367fde51573078be99220fcaa641bf9c`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/obsidian-binder/blob/66a6254212c9f502d88513a6d9454502f9ce042c/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/obsidian-binder.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/obsidian-binder.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPPcards](RAPPcards.md) (markdown), [twin-binder](twin-binder.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/obsidian-binder` at `66a6254212` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py obsidian-binder --json` from the folder that holds both.
