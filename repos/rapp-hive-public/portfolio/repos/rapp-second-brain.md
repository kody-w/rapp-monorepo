---
repo: kody-w/rapp-second-brain
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c71de71f2ed4de039ba19725d0f3c407756e5fa0
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 6
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-map
  - rapp-train
---

# rapp-second-brain: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-second-brain.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-second-brain` at `c71de71f2e`](https://github.com/kody-w/rapp-second-brain/tree/c71de71f2ed4de039ba19725d0f3c407756e5fa0) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `265258e021a50e286d93ed7308a60feee8bfadba9221ddb132682899e797a3d5`.
- "experimental" mentions: 6 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-map](rapp-map.md) (markdown), [rapp-train](rapp-train.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-secondbrain](rapp-secondbrain.md), [rapp-tower](rapp-tower.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-second-brain` at `c71de71f2e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-second-brain --json` from the folder that holds both.
