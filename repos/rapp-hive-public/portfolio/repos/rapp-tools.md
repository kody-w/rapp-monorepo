---
repo: kody-w/rapp-tools
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5dd7a3daa315224f237da14830d569323fef2763
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "workspace-v0.1.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-1
  - rapp-crispy
  - rapp-rewind
  - rapp-shot
  - rapp-voice
  - rapp-workspace
  - RAPP_Store
  - RAR
---

# rapp-tools: certified

![RAPP/1: certified, version workspace-v0.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-tools.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `workspace-v0.1.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-tools` at `5dd7a3daa3`](https://github.com/kody-w/rapp-tools/tree/5dd7a3daa315224f237da14830d569323fef2763) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `0e5be04a63647b2c019ebd3d0898bc39d8b03511e39b42ecc26a5795d74fa3bb`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 8 portfolio repo(s): [rapp-1](rapp-1.md) (pin), [rapp-crispy](rapp-crispy.md) (markdown), [rapp-rewind](rapp-rewind.md) (markdown), [rapp-shot](rapp-shot.md) (markdown), [rapp-voice](rapp-voice.md) (markdown), [rapp-workspace](rapp-workspace.md) (pin), [RAPP_Store](RAPP_Store.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 5: [rapp-crispy](rapp-crispy.md), [rapp-monorepo](rapp-monorepo.md), [rapp-rewind](rapp-rewind.md), [rapp-shot](rapp-shot.md), [rapp-voice](rapp-voice.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-tools` at `5dd7a3daa3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-tools --json` from the folder that holds both.
