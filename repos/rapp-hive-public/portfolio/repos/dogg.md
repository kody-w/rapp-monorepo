---
repo: kody-w/dogg
family: dogg
line: DOGG & Commons
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 7525dd71c4d7d59fabc28647789eb0860381c84b
checked: 2026-10-08
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

**Not yet:** 4 finding(s) from rapp_check: §7.4 chain gap ×3, §7 frame verification step 4.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/dogg` at `7525dd71c4`](https://github.com/kody-w/dogg/tree/7525dd71c4d7d59fabc28647789eb0860381c84b) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 4 finding(s), 399 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c0d545def96ad10d576008f78dc270e5f095333606df2eeb2485a858d6fa6016`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/dogg/blob/7525dd71c4d7d59fabc28647789eb0860381c84b/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/dogg.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/dogg.md).

## Findings (4)

- `tests/fixture_markets_frame.json` · §7.4 chain gap · stream markets:@kody-w/dogg-markets expected seq 0, found 30
- `ticks/2304.json` · §7.4 chain gap · stream tick:@kody-w/global expected seq 0, found 2304
- `witness-battlestation/359.json` · §7 frame verification step 4 · prev != head payload_hash
- `world/2304.json` · §7.4 chain gap · stream world:@kody-w/dogg expected seq 0, found 2304

On the map: the **DOGG & Commons** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [dogg-markets](dogg-markets.md) (markdown), [dogg-planet](dogg-planet.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-organism](rapp-organism.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 10: [dogg-canon](dogg-canon.md), [dogg-kestrel](dogg-kestrel.md), [dogg-markets](dogg-markets.md), [dogg-merlin](dogg-merlin.md), [dogg-planet](dogg-planet.md), [rapp-brain](rapp-brain.md), [rapp-monorepo](rapp-monorepo.md), [rapp-organism](rapp-organism.md), [rapp-specs](rapp-specs.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/dogg` at `7525dd71c4` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py dogg --json` from the folder that holds both.
