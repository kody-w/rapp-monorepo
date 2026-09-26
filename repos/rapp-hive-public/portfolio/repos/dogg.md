---
repo: kody-w/dogg
family: dogg
line: DOGG & Commons
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: d72ba3a0b0eaa231daee79be88eaf2dd27d537da
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - dogg-markets
  - dogg-planet
  - rapp-1
  - rapp-organism
  - RAR
---

# dogg: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/dogg.svg)

**Not yet:** 3 finding(s) from rapp_check: §7.4 chain gap ×3.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/dogg` at `d72ba3a0b0`](https://github.com/kody-w/dogg/tree/d72ba3a0b0eaa231daee79be88eaf2dd27d537da) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 3 finding(s), 37 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e4bfa3609054f89280c50e5b08083e1a4683d742a37bc46eb0b5e4238bc79b0d`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (3)

- `tests/fixture_markets_frame.json` · §7.4 chain gap · stream markets:@kody-w/dogg-markets expected seq 0, found 30
- `ticks/864.json` · §7.4 chain gap · stream tick:@kody-w/global expected seq 0, found 864
- `world/864.json` · §7.4 chain gap · stream world:@kody-w/dogg expected seq 0, found 864

On the map: the **DOGG & Commons** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [dogg-markets](dogg-markets.md) (markdown), [dogg-planet](dogg-planet.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-organism](rapp-organism.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 8: [dogg-canon](dogg-canon.md), [dogg-markets](dogg-markets.md), [dogg-planet](dogg-planet.md), [rapp-brain](rapp-brain.md), [rapp-monorepo](rapp-monorepo.md), [rapp-organism](rapp-organism.md), [rapp-specs](rapp-specs.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/dogg` at `d72ba3a0b0` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py dogg --json` from the folder that holds both.
