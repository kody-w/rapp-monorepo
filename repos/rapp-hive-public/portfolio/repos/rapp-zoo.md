---
repo: kody-w/rapp-zoo
family: twins
line: Twins
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 7a0eeb9c647feac1e0aa27ee662442a3a4929339
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 3
header: missing
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: active
also_on:
  - worlds
links_to:
  - RAR
---

# rapp-zoo: certified

![RAPP/1: certified, version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-zoo.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-zoo` at `7a0eeb9c64`](https://github.com/kody-w/rapp-zoo/tree/7a0eeb9c647feac1e0aa27ee662442a3a4929339) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 5 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3aa73b8ef743e651d67a88fcddbc2d26ec286bebdb21e8775ab5c0263865e63f`.
- "experimental" mentions: 3 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Twins** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [RAR](RAR.md) (markdown).
Linked from 7: [cowork-cookbook-rapp](cowork-cookbook-rapp.md), [dimensional-bottles](dimensional-bottles.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [RAPP_Store](RAPP_Store.md), [rappterbox](rappterbox.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-zoo` at `7a0eeb9c64` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-zoo --json` from the folder that holds both.
