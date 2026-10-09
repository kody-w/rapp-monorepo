---
repo: kody-w/brainstem-harness
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 3eed344c456ee4d9a64ed27a6ee9bfb074030df6
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/brainstem-harness/pull/1
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - rapp-installer
  - rapp-map
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# brainstem-harness: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/brainstem-harness.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/brainstem-harness` at `3eed344c45`](https://github.com/kody-w/brainstem-harness/tree/3eed344c456ee4d9a64ed27a6ee9bfb074030df6) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9a0fa04752ac06027647c17fb4bde3a35571c6ac8f0ed52ce0dec9e207e630e2`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/brainstem-harness/blob/3eed344c456ee4d9a64ed27a6ee9bfb074030df6/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/brainstem-harness.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/brainstem-harness.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [rapp-map](rapp-map.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/brainstem-harness` at `3eed344c45` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py brainstem-harness --json` from the folder that holds both.
