---
repo: kody-w/rapp-apex-dino
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d511b366e3170496ae90f56f8b71274a499b5ff0
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-apex-dino/pull/1
channel: newest
lifecycle: active
member_card: present
---

# rapp-apex-dino: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-apex-dino.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-apex-dino` at `d511b366e3`](https://github.com/kody-w/rapp-apex-dino/tree/d511b366e3170496ae90f56f8b71274a499b5ff0) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `0afa8020dccbf85f8d0a9922e9de6cd8679926a11fdccd64ff66bed32da5260e`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-apex-dino/blob/d511b366e3170496ae90f56f8b71274a499b5ff0/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-apex-dino.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-apex-dino.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-open](rapp-open.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-apex-dino` at `d511b366e3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-apex-dino --json` from the folder that holds both.
