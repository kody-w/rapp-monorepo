---
repo: kody-w/rapp-base
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5963b64575073c599d8ecc3345efd26fc15c2d0e
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-base/pull/6
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-base-template
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-base: certified

![RAPP/1: archived (certified), version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-base.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-base` at `5963b64575`](https://github.com/kody-w/rapp-base/tree/5963b64575073c599d8ecc3345efd26fc15c2d0e) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3df3b7bd22f7d038c208a4d9a70b7f20bf7a542ef594f8426be2775f4a88a461`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-base/blob/5963b64575073c599d8ecc3345efd26fc15c2d0e/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-base.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-base.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-base-template](rapp-base-template.md) (markdown).
Linked from 2: [rapp-base-template](rapp-base-template.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-base` at `5963b64575` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-base --json` from the folder that holds both.
