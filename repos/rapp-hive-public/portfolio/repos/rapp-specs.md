---
repo: kody-w/rapp-specs
family: learn
line: Learn & Docs
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 94d5f410c6f5258c6391979b6020082d3fd355e0
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-specs/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - dogg
  - dogg-markets
  - dogg-planet
  - rapp-1
---

# rapp-specs: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-specs.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-specs` at `94d5f410c6`](https://github.com/kody-w/rapp-specs/tree/94d5f410c6f5258c6391979b6020082d3fd355e0) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 151 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `98ffd18aa11aae78e503ec5fbb602ace29a59868a2b6af161176bcd2710d5400`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-specs/blob/94d5f410c6f5258c6391979b6020082d3fd355e0/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-specs.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-specs.md).

On the map: the **Learn & Docs** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [dogg](dogg.md) (markdown), [dogg-markets](dogg-markets.md) (markdown), [dogg-planet](dogg-planet.md) (markdown), [rapp-1](rapp-1.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-specs` at `94d5f410c6` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-specs --json` from the folder that holds both.
