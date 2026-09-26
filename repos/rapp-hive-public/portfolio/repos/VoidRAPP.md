---
repo: kody-w/VoidRAPP
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 375968ece213b0c71312f6c1b2304baf928cdb1d
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: no-readme
channel: newest
lifecycle: active
---

# VoidRAPP: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/VoidRAPP.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/VoidRAPP` at `375968ece2`](https://github.com/kody-w/VoidRAPP/tree/375968ece213b0c71312f6c1b2304baf928cdb1d) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3bd2fa49c7314cd373ea437d46c3c5ea82f978f0ddcdd86076e41e5fd5eef6da`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: no README (skipped).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Check it yourself

Clone `kody-w/VoidRAPP` at `375968ece2` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py VoidRAPP --json` from the folder that holds both.
