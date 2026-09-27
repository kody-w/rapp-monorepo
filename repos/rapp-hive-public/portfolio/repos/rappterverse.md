---
repo: kody-w/rappterverse
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c531a649625c79d547485adfad121ddc9cc108ab
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: merged
header_pr: https://github.com/kody-w/rappterverse/pull/7746
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-sentinel
---

# rappterverse: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterverse.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterverse` at `c531a64962`](https://github.com/kody-w/rappterverse/tree/c531a649625c79d547485adfad121ddc9cc108ab) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `0df92430011157f12c04f3b94b19087abfd18e8e9155c97abfe89eb78e9a22aa`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappterverse/pull/7746).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterverse/blob/c531a649625c79d547485adfad121ddc9cc108ab/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterverse.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterverse.md).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-sentinel](rapp-sentinel.md) (markdown).
Linked from 2: [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterverse` at `c531a64962` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterverse --json` from the folder that holds both.
