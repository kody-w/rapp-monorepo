---
repo: kody-w/dogg
family: dogg
line: DOGG & Commons
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 954ea08ce63fa208befef2f23459f0829ef8eaeb
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/dogg/pull/11
channel: newest
lifecycle: active
member_card: present
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

- Evidence: [`kody-w/dogg` at `954ea08ce6`](https://github.com/kody-w/dogg/tree/954ea08ce63fa208befef2f23459f0829ef8eaeb) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 3 finding(s), 37 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `561eccc442d8bfc75bada54a5c57f4f82d4c7eac5e6c8d000d3825ae180b64ff`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/dogg/blob/954ea08ce63fa208befef2f23459f0829ef8eaeb/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/dogg.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/dogg.md).

## Findings (3)

- `tests/fixture_markets_frame.json` · §7.4 chain gap · stream markets:@kody-w/dogg-markets expected seq 0, found 30
- `ticks/1152.json` · §7.4 chain gap · stream tick:@kody-w/global expected seq 0, found 1152
- `world/864.json` · §7.4 chain gap · stream world:@kody-w/dogg expected seq 0, found 864

On the map: the **DOGG & Commons** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [dogg-markets](dogg-markets.md) (markdown), [dogg-planet](dogg-planet.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-organism](rapp-organism.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 8: [dogg-canon](dogg-canon.md), [dogg-markets](dogg-markets.md), [dogg-planet](dogg-planet.md), [rapp-brain](rapp-brain.md), [rapp-monorepo](rapp-monorepo.md), [rapp-organism](rapp-organism.md), [rapp-specs](rapp-specs.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/dogg` at `954ea08ce6` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py dogg --json` from the folder that holds both.
