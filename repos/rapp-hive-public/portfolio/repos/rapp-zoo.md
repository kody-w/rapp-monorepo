---
repo: kody-w/rapp-zoo
family: twins
line: Twins
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: cb0f63ff015edd6da0055d1214f8eb3c9bd23a30
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 3
header: present
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
also_on:
  - worlds
links_to:
  - RAPP
  - RAR
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-zoo: certified

![RAPP/1: archived (certified), version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-zoo.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-zoo` at `cb0f63ff01`](https://github.com/kody-w/rapp-zoo/tree/cb0f63ff015edd6da0055d1214f8eb3c9bd23a30) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 5 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3aa73b8ef743e651d67a88fcddbc2d26ec286bebdb21e8775ab5c0263865e63f`.
- "experimental" mentions: 3 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-zoo/blob/cb0f63ff015edd6da0055d1214f8eb3c9bd23a30/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-zoo.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-zoo.md).

On the map: the **Twins** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 7: [cowork-cookbook-rapp](cowork-cookbook-rapp.md), [dimensional-bottles](dimensional-bottles.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [RAPP_Store](RAPP_Store.md), [rappterbox](rappterbox.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-zoo` at `cb0f63ff01` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-zoo --json` from the folder that holds both.
