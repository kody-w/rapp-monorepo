---
repo: kody-w/rapp-brainstem
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 4154e95c43502b35edd1243276015aede9c9a6d2
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 3
header: present
header_pr: https://github.com/kody-w/rapp-brainstem/pull/3
version: "v0.2.1"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - rapp-installer
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-brainstem: certified

![RAPP/1: archived (certified), version v0.2.1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-brainstem.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v0.2.1`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-brainstem` at `4154e95c43`](https://github.com/kody-w/rapp-brainstem/tree/4154e95c43502b35edd1243276015aede9c9a6d2) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 9 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ee3acd71cca48c4a59718066531043185ca2573194605f62d5c27632b8e174a4`.
- "experimental" mentions: 3 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-brainstem/blob/4154e95c43502b35edd1243276015aede9c9a6d2/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-brainstem.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-brainstem.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 4: [brainstem-bootcamp](brainstem-bootcamp.md), [rapp-monorepo](rapp-monorepo.md), [rapp-skill](rapp-skill.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-brainstem` at `4154e95c43` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-brainstem --json` from the folder that holds both.
