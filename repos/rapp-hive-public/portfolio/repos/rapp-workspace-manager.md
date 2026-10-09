---
repo: kody-w/rapp-workspace-manager
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 230887286f8eed0268f2be2b4f87c14d1cfe0a8c
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-workspace-manager/pull/13
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-workspace
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-workspace-manager: certified

![RAPP/1: archived (certified), version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-workspace-manager.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-workspace-manager` at `230887286f`](https://github.com/kody-w/rapp-workspace-manager/tree/230887286f8eed0268f2be2b4f87c14d1cfe0a8c) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 6 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a90812967269ceb71cded6a37b88c8734bf3729dd63fd0ccd8da2816f57f3313`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-workspace-manager/blob/230887286f8eed0268f2be2b4f87c14d1cfe0a8c/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-workspace-manager.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-workspace-manager.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown, workflow), [rapp-workspace](rapp-workspace.md) (markdown, workflow).
Linked from 3: [RAPP](RAPP.md), [rapp-monorepo](rapp-monorepo.md), [rapp-work](rapp-work.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-workspace-manager` at `230887286f` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-workspace-manager --json` from the folder that holds both.
