---
repo: kody-w/heimdall
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 022079ab0c01c43e091fd6000dea524b3a273164
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-installer
  - RAPPcards
  - twin-egg-hatcher
---

# heimdall: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/heimdall.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/heimdall` at `022079ab0c`](https://github.com/kody-w/heimdall/tree/022079ab0c01c43e091fd6000dea524b3a273164) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c65f2d572f3fc27623af81c1586bf615046f9e47be73108b19231ba034de940d`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAPPcards](RAPPcards.md) (markdown), [twin-egg-hatcher](twin-egg-hatcher.md) (markdown).
Linked from 8: [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAR](RAR.md), [second-seat](second-seat.md), [twin-egg-hatcher](twin-egg-hatcher.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/heimdall` at `022079ab0c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py heimdall --json` from the folder that holds both.
