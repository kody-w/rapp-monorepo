---
repo: kody-w/the-coliseum
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: aa9c429e66663d38fdb43e5a56f83c0f2766e6e9
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
---

# the-coliseum: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/the-coliseum.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/the-coliseum` at `aa9c429e66`](https://github.com/kody-w/the-coliseum/tree/aa9c429e66663d38fdb43e5a56f83c0f2766e6e9) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c18f05d2dac3bda843575270a36de7057df91a0d96f1ad799a576dc626517fdb`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Check it yourself

Clone `kody-w/the-coliseum` at `aa9c429e66` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py the-coliseum --json` from the folder that holds both.
