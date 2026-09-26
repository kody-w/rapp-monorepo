---
repo: kody-w/rapp-recall
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: cfd5491d60746496b2a04e4f15529f14fa959148
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 30
header: missing
version: "v0.1.0"
version_source: release
channel: newest
lifecycle: active
---

# rapp-recall: certified

![RAPP/1: certified, version v0.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-recall.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.1.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-recall` at `cfd5491d60`](https://github.com/kody-w/rapp-recall/tree/cfd5491d60746496b2a04e4f15529f14fa959148) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `30a4811a2f40a32466c6fdbd41ebec759ec47b890ad1ae4532ec4700114bdfc9`.
- "experimental" mentions: 30 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-recall` at `cfd5491d60` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-recall --json` from the folder that holds both.
