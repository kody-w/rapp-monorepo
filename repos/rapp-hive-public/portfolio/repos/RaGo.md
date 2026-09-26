---
repo: kody-w/RaGo
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 426239e6964ca978346aba777c7389f56c521edb
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v2.1.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-lantern
---

# RaGo: certified

![RAPP/1: certified, version v2.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RaGo.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v2.1.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RaGo` at `426239e696`](https://github.com/kody-w/RaGo/tree/426239e6964ca978346aba777c7389f56c521edb) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9269bc0ae7dfbc4523d498160c7c4cd5a818c29b2cb8b8c4a9c406abfe166d31`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-lantern](rapp-lantern.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RaGo` at `426239e696` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RaGo --json` from the folder that holds both.
