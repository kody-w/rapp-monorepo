---
repo: kody-w/rappterbox
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 582220655e10aaff4627e073da1e5311669a50f9
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 24
header: present
header_pr: https://github.com/kody-w/rappterbox/pull/5
version: "0.12.2"
version_source: VERSION
channel: newest
lifecycle: archived
since: 2026-10-08
member_card: present
links_to:
  - RAPP
  - rapp-zoo
  - RAR
  - wildhaven-ai-homes-twin
---

> **Archived since 2026-10-08.** The repo is archived on GitHub (read-only); the crawl still checks it, and this file and its badge stay.

# rappterbox: certified

![RAPP/1: archived (certified), version 0.12.2](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbox.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v0.12.2`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbox` at `582220655e`](https://github.com/kody-w/rappterbox/tree/582220655e10aaff4627e073da1e5311669a50f9) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9b813d9ef347cb14572eaec77aa1c91c3de663c49619861f7138b3a47850a132`.
- "experimental" mentions: 24 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterbox/blob/582220655e10aaff4627e073da1e5311669a50f9/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterbox.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterbox.md).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-zoo](rapp-zoo.md) (markdown), [RAR](RAR.md) (markdown), [wildhaven-ai-homes-twin](wildhaven-ai-homes-twin.md) (markdown).
Linked from 6: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-egg-hub](rapp-egg-hub.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbox` at `582220655e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbox --json` from the folder that holds both.
