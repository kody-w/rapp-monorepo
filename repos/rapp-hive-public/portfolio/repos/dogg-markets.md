---
repo: kody-w/dogg-markets
family: dogg
line: DOGG & Commons
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 0fd776d2193471be537e374b9db959c9bea7690a
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - dogg
  - rapp-1
---

# dogg-markets: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/dogg-markets.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/dogg-markets` at `0fd776d219`](https://github.com/kody-w/dogg-markets/tree/0fd776d2193471be537e374b9db959c9bea7690a) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 216 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `75879ff6b02360df4a0726f9748366b6072f08193fe8c6781f1c69ee778b36dc`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **DOGG & Commons** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [dogg](dogg.md) (markdown), [rapp-1](rapp-1.md) (markdown).
Linked from 3: [dogg](dogg.md), [rapp-monorepo](rapp-monorepo.md), [rapp-specs](rapp-specs.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/dogg-markets` at `0fd776d219` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py dogg-markets --json` from the folder that holds both.
