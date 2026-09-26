---
repo: kody-w/lisppy-shepherd
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: b0d5a8d283c8198c23bf3317a9fffce3cd447e9b
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: missing
channel: newest
lifecycle: active
links_to:
  - lisppy
  - rappterbook
---

# lisppy-shepherd: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/lisppy-shepherd.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/lisppy-shepherd` at `b0d5a8d283`](https://github.com/kody-w/lisppy-shepherd/tree/b0d5a8d283c8198c23bf3317a9fffce3cd447e9b) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `abc711e7c6aa39a40d4d708d9ac0c2c8a83041bfe6fc6321d791159b6b194eac`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [lisppy](lisppy.md) (markdown), [rappterbook](rappterbook.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rappterbook](rappterbook.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/lisppy-shepherd` at `b0d5a8d283` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py lisppy-shepherd --json` from the folder that holds both.
