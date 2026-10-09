---
repo: kody-w/rapp-petri
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c464e8e3623701cb9c050c64268f801ca8f9c1e6
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-petri/pull/1
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - rapp-installer
  - rapp-skills
  - vbrainstem
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-petri: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-petri.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-petri` at `c464e8e362`](https://github.com/kody-w/rapp-petri/tree/c464e8e3623701cb9c050c64268f801ca8f9c1e6) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `824b8bf9d6da05efafaa8be8f39b939cd63cf85588ae916fa66928e6307ba120`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-petri/blob/c464e8e3623701cb9c050c64268f801ca8f9c1e6/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-petri.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-petri.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [rapp-skills](rapp-skills.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-petri` at `c464e8e362` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-petri --json` from the folder that holds both.
