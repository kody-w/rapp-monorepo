---
repo: kody-w/rio
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: e49264b9aa5b8d17bcbef246b9507f3ca9bb1d43
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-map
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rio: certified

![RAPP/1: archived (certified), version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rio.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rio` at `e49264b9aa`](https://github.com/kody-w/rio/tree/e49264b9aa5b8d17bcbef246b9507f3ca9bb1d43) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `809890c759d463aa84ef04805b5adf9b8bc7833a115aa53cfdd35e27ab462dcb`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rio/blob/e49264b9aa5b8d17bcbef246b9507f3ca9bb1d43/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rio.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rio.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-map](rapp-map.md) (markdown).
Linked from 4: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rionet](rionet.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rio` at `e49264b9aa` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rio --json` from the folder that holds both.
