---
repo: kody-w/rapp-static-brainstem
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: b6b416a2626e377e496a471cf3f9d7a4c3a0b1fc
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - rapp-installer
  - rapp-static-apis
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-static-brainstem: certified

![RAPP/1: archived (certified), version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-static-brainstem.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-static-brainstem` at `b6b416a262`](https://github.com/kody-w/rapp-static-brainstem/tree/b6b416a2626e377e496a471cf3f9d7a4c3a0b1fc) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `56086db6b6b7f8ab69f1562f4cc4a620e50951535db4e059d8493f51b46816fa`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-static-brainstem/blob/b6b416a2626e377e496a471cf3f9d7a4c3a0b1fc/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-static-brainstem.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-static-brainstem.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-static-brainstem` at `b6b416a262` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-static-brainstem --json` from the folder that holds both.
