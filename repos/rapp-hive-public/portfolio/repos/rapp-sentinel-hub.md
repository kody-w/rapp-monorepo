---
repo: kody-w/rapp-sentinel-hub
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 6529b29cc7a42d3b2a9f2f4b24d250915d120eba
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-sentinel-hub/pull/3
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
also_on:
  - estate
links_to:
  - rapp-1
  - rapp-sentinel
  - RAR
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rapp-sentinel-hub: certified

![RAPP/1: archived (certified)](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-sentinel-hub.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-sentinel-hub` at `6529b29cc7`](https://github.com/kody-w/rapp-sentinel-hub/tree/6529b29cc7a42d3b2a9f2f4b24d250915d120eba) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f9190c399f457218233ef57c91fe1efae8c700505aecd907d76b0daed5ef3fa3`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-sentinel-hub/blob/6529b29cc7a42d3b2a9f2f4b24d250915d120eba/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-sentinel-hub.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-sentinel-hub.md).

On the map: the **Agents (RAR)** line, and also Estate & Ops ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-1](rapp-1.md) (markdown), [rapp-sentinel](rapp-sentinel.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-sentinel](rapp-sentinel.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-sentinel-hub` at `6529b29cc7` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-sentinel-hub --json` from the folder that holds both.
