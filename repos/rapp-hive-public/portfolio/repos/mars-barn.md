---
repo: kody-w/mars-barn
family: rappterbook
line: Rappterbook
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 2203505846f1192b7ea5431bb0b896332a178798
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 14
header: missing
channel: newest
lifecycle: active
links_to:
  - rappterbook
---

# mars-barn: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/mars-barn.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/mars-barn` at `2203505846`](https://github.com/kody-w/mars-barn/tree/2203505846f1192b7ea5431bb0b896332a178798) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `0eb69725531d869c36118cac183ea83d7c9b818b644f2745e07454d42d03072f`.
- "experimental" mentions: 14 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rappterbook](rappterbook.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rappterbook](rappterbook.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/mars-barn` at `2203505846` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py mars-barn --json` from the folder that holds both.
