---
repo: kody-w/rapp-skills
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: aaac415cb9c990e6b666a1bfa457a0e69ef76512
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - hive-hub
  - RAPP
  - rapp-1
  - rapp-mission
  - rapp-static-apis
  - rapp-work
  - RAR
  - vbrainstem
---

# rapp-skills: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-skills.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-skills` at `aaac415cb9`](https://github.com/kody-w/rapp-skills/tree/aaac415cb9c990e6b666a1bfa457a0e69ef76512) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3f0843ffd70bf87ffa6003e6a64c9003234d2e1a8cd3b4176a6644ed49e1f7f7`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 8 portfolio repo(s): [hive-hub](hive-hub.md) (markdown), [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (pin), [rapp-mission](rapp-mission.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (pin), [rapp-work](rapp-work.md) (pin), [RAR](RAR.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).
Linked from 7: [learn-brainstem](learn-brainstem.md), [rapp-mission](rapp-mission.md), [rapp-monorepo](rapp-monorepo.md), [rapp-petri](rapp-petri.md), [rapp-skill](rapp-skill.md), [rapp-toaster](rapp-toaster.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-skills` at `aaac415cb9` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-skills --json` from the folder that holds both.
