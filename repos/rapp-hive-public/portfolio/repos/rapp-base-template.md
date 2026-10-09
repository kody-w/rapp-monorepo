---
repo: kody-w/rapp-base-template
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 4e0ee323868ec3e77f9a60b4c56aa69c8058cf45
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-base-template/pull/1
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-base
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-base-template: certified

![RAPP/1: archived (certified), version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-base-template.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-base-template` at `4e0ee32386`](https://github.com/kody-w/rapp-base-template/tree/4e0ee323868ec3e77f9a60b4c56aa69c8058cf45) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c67a2961186994d1685385c1a5f7a7d4d4c845d54821e3962a2d53bfdd6a4a25`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-base-template/blob/4e0ee323868ec3e77f9a60b4c56aa69c8058cf45/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-base-template.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-base-template.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-base](rapp-base.md) (markdown).
Linked from 2: [rapp-base](rapp-base.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-base-template` at `4e0ee32386` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-base-template --json` from the folder that holds both.
