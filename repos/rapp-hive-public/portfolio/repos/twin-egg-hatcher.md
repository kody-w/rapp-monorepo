---
repo: kody-w/twin-egg-hatcher
family: twins
line: Twins
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 6e96a7ed24b3f70a8568543510792236d5a53a8d
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - heimdall
  - RAPP
  - rapp-installer
---

# twin-egg-hatcher: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/twin-egg-hatcher.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/twin-egg-hatcher` at `6e96a7ed24`](https://github.com/kody-w/twin-egg-hatcher/tree/6e96a7ed24b3f70a8568543510792236d5a53a8d) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3f38f4b663c089560b4d8e020b7a8e090e07a108107370f962fa85fce46fdb18`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Twins** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [heimdall](heimdall.md) (markdown), [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 6: [heimdall](heimdall.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/twin-egg-hatcher` at `6e96a7ed24` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py twin-egg-hatcher --json` from the folder that holds both.
