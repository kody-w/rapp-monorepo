---
repo: kody-w/brainstem-agent
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 06df49601056a5e8d94edd834d1bb090d9a67a28
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 59
header: present
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - rapp-installer
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# brainstem-agent: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/brainstem-agent.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/brainstem-agent` at `06df496010`](https://github.com/kody-w/brainstem-agent/tree/06df49601056a5e8d94edd834d1bb090d9a67a28) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `247d898dae74a34585700d5484d5a5a3d8274673646d4b50c6be725c8a8abb63`.
- "experimental" mentions: 59 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/brainstem-agent/blob/06df49601056a5e8d94edd834d1bb090d9a67a28/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/brainstem-agent.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/brainstem-agent.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/brainstem-agent` at `06df496010` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py brainstem-agent --json` from the folder that holds both.
