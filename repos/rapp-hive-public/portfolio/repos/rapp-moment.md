---
repo: kody-w/rapp-moment
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 229db186c505d2f2a693fac41cbbe84cadf7a07c
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "1.1.0"
version_source: VERSION
channel: newest
lifecycle: active
links_to:
  - rapp-hologram
---

# rapp-moment: certified

![RAPP/1: certified, version 1.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-moment.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.1.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-moment` at `229db186c5`](https://github.com/kody-w/rapp-moment/tree/229db186c505d2f2a693fac41cbbe84cadf7a07c) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8ac59f80e42d00e2e84991b9eb95a17465442e614266f89f0eb135d9932fee62`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-hologram](rapp-hologram.md) (markdown).
Linked from 5: [double-jump](double-jump.md), [rapp-egg-hub](rapp-egg-hub.md), [rapp-hologram](rapp-hologram.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-moment` at `229db186c5` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-moment --json` from the folder that holds both.
