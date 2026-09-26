---
repo: kody-w/vbrainstem
family: brainstem
line: Brainstem
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: ee5499fed56f4d0e46c94f8be034e073adc55b2b
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
links_to:
  - CommunityRAPP
  - dogg
  - rapp-1
  - rapp-brainstem
  - rapp-installer
  - rapp-mission
  - rapp-personpower
  - rapp-skills
  - RAR
---

# vbrainstem: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/vbrainstem.svg)

**Not yet:** 1 finding(s) from rapp_check: §7.4 chain gap.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/vbrainstem` at `ee5499fed5`](https://github.com/kody-w/vbrainstem/tree/ee5499fed56f4d0e46c94f8be034e073adc55b2b) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `88c39e270098b50bc4dbd2f1731500fa364dd0588037916bed30e9f271a400e8`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `vbrainstem-setup/FRAME.json` · §7.4 chain gap · stream rappid:@kody-w/vbrainstem-setup:228be404333c42b53ecd48fae5e4d9f3a2e10fc459da19065b3f91adce70d228 expected seq 0, found 5

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 9 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [dogg](dogg.md) (markdown), [rapp-1](rapp-1.md) (markdown, pin), [rapp-brainstem](rapp-brainstem.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-mission](rapp-mission.md) (markdown), [rapp-personpower](rapp-personpower.md) (markdown), [rapp-skills](rapp-skills.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 13: [chat](chat.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-brainstem-sdk](rapp-brainstem-sdk.md), [rapp-brainstem-walkthrough](rapp-brainstem-walkthrough.md), [rapp-doorman](rapp-doorman.md), [rapp-kite](rapp-kite.md), [rapp-mission](rapp-mission.md), [rapp-monorepo](rapp-monorepo.md), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md), [rapp-petri](rapp-petri.md), [rapp-skills](rapp-skills.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/vbrainstem` at `ee5499fed5` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py vbrainstem --json` from the folder that holds both.
