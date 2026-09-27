---
repo: kody-w/rappter-mmo
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5d45256b46d2373e5bb5c10b2faf920ba7341be8
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/rappter-mmo/pull/2
channel: newest
lifecycle: active
member_card: present
also_on:
  - worlds
---

# rappter-mmo: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-mmo.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-mmo` at `5d45256b46`](https://github.com/kody-w/rappter-mmo/tree/5d45256b46d2373e5bb5c10b2faf920ba7341be8) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `022da5ff88afc4f74ea8de9e737dba1b4e13a8573f9681f860a72617d38ab9a0`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappter-mmo/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappter-mmo/blob/5d45256b46d2373e5bb5c10b2faf920ba7341be8/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappter-mmo.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappter-mmo.md).

On the map: the **Rappterverse** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-mmo` at `5d45256b46` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-mmo --json` from the folder that holds both.
