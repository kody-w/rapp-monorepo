---
repo: kody-w/rappvision-rappterbox
family: rappvision
line: Rappvision
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 6af62eb0cdef26ad35ca85a480626af6f2918494
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
also_on:
  - rappterverse
links_to:
  - rapp-vision
---

# rappvision-rappterbox: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappvision-rappterbox.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappvision-rappterbox` at `6af62eb0cd`](https://github.com/kody-w/rappvision-rappterbox/tree/6af62eb0cdef26ad35ca85a480626af6f2918494) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `507d1f961fab018f8be9bb2fc867f9ad7baeb4c5647142cadd58d8767e9809a2`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Rappvision** line, and also Rappterverse ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-vision](rapp-vision.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-vision](rapp-vision.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappvision-rappterbox` at `6af62eb0cd` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappvision-rappterbox --json` from the folder that holds both.
