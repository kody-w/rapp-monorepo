---
repo: kody-w/rapp-omarchy
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 6a1c509299b7a89dbb8faab1ab07bcecef8866a2
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
  - rapp-herdr
  - rapp-map
  - rapp-projects
  - rapp-sdk
  - rapp-workspace
---

# rapp-omarchy: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-omarchy.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-omarchy` at `6a1c509299`](https://github.com/kody-w/rapp-omarchy/tree/6a1c509299b7a89dbb8faab1ab07bcecef8866a2) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `30c48aab58124048986b24704d48b89b79129e66c5167bf7d254258ae34dbfb0`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 7 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown, workflow), [rapp-herdr](rapp-herdr.md) (markdown, workflow), [rapp-map](rapp-map.md) (markdown, workflow), [rapp-projects](rapp-projects.md) (markdown, workflow), [rapp-sdk](rapp-sdk.md) (markdown, workflow), [rapp-workspace](rapp-workspace.md) (markdown, workflow).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-omarchy` at `6a1c509299` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-omarchy --json` from the folder that holds both.
