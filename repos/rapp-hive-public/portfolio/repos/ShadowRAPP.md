---
repo: kody-w/ShadowRAPP
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 0ead081d10baf7365abd14dcade51535a01d3366
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: no-readme
channel: newest
lifecycle: active
---

# ShadowRAPP: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/ShadowRAPP.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/ShadowRAPP` at `0ead081d10`](https://github.com/kody-w/ShadowRAPP/tree/0ead081d10baf7365abd14dcade51535a01d3366) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `1cfee39bf5cab6c71b0176d1f6103f291db0b1df49ee3969c8dc718da3c820dd`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: no README (skipped).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Check it yourself

Clone `kody-w/ShadowRAPP` at `0ead081d10` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py ShadowRAPP --json` from the folder that holds both.
