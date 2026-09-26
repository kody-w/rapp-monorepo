---
repo: kody-w/RAPP_Sense_Store
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 36efba8f7ca381f7fa39b6b08e5a0f06aec1d946
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - RAPP_Store
  - RAR
---

# RAPP_Sense_Store: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPP_Sense_Store.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPP_Sense_Store` at `36efba8f7c`](https://github.com/kody-w/RAPP_Sense_Store/tree/36efba8f7ca381f7fa39b6b08e5a0f06aec1d946) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `29b5ea55de3fc9c28c79ee09e902dc681045e7053ef03ed43b1880dc5d00130b`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 10: [echo-brainstem](echo-brainstem.md), [lumen-brainstem](lumen-brainstem.md), [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAPP_Store](RAPP_Store.md), [RAR](RAR.md), [tide-brainstem](tide-brainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPP_Sense_Store` at `36efba8f7c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPP_Sense_Store --json` from the folder that holds both.
