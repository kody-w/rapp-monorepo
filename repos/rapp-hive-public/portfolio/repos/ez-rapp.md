---
repo: kody-w/ez-rapp
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 40c8349f1d98024f2e4268786b8e4e9a23a8b11b
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v0.1.3"
version_source: release
channel: newest
lifecycle: active
links_to:
  - CommunityRAPP
  - rapp-installer
  - RAR
---

# ez-rapp: certified

![RAPP/1: certified, version v0.1.3](https://kody-w.github.io/rapp-hive-public/portfolio/badges/ez-rapp.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.1.3`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/ez-rapp` at `40c8349f1d`](https://github.com/kody-w/ez-rapp/tree/40c8349f1d98024f2e4268786b8e4e9a23a8b11b) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a1269766f58c0be55ac2afa595f6555507937ba1619db49a680b5eda1dc25052`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 2: [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/ez-rapp` at `40c8349f1d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py ez-rapp --json` from the folder that holds both.
