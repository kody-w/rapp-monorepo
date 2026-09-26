---
repo: kody-w/CommunityRAPP
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 4931285ffb04bf7e9dcdeecdfadb80e352f5ea09
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 9
header: missing
version: "1.0.0"
version_source: VERSION
channel: newest
lifecycle: active
links_to:
  - rapp-installer
---

# CommunityRAPP: certified

![RAPP/1: certified, version 1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/CommunityRAPP.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/CommunityRAPP` at `4931285ffb`](https://github.com/kody-w/CommunityRAPP/tree/4931285ffb04bf7e9dcdeecdfadb80e352f5ea09) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `84cda5c83d7df8d16c362a24bdbb6d28f579bca36ef4a5096a6f9a6f348c9412`.
- "experimental" mentions: 9 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 24: [ez-rapp](ez-rapp.md), [RAPP](RAPP.md), [rapp-ai](rapp-ai.md), [rapp-alpha](rapp-alpha.md), [rapp-beta](rapp-beta.md), [RAPP-Bible](RAPP-Bible.md), [rapp-brainstem-beta](rapp-brainstem-beta.md), [rapp-brainstem-walkthrough](rapp-brainstem-walkthrough.md), [rapp-canary](rapp-canary.md), [rapp-claude-skills](rapp-claude-skills.md), [rapp-installer](rapp-installer.md), [rapp-installer-canary](rapp-installer-canary.md), [rapp-installer-dev](rapp-installer-dev.md), [rapp-monorepo](rapp-monorepo.md), [rapp-nightly](rapp-nightly.md), [rapp-shape-aibast](rapp-shape-aibast.md), [rapp-spine](rapp-spine.md), [rapp-version-selector](rapp-version-selector.md), [RAPP_hippo](RAPP_hippo.md), [rapp_orion](rapp_orion.md), [RAPPsquared](RAPPsquared.md), [rappterverse](rappterverse.md), [RAR](RAR.md), [vbrainstem](vbrainstem.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/CommunityRAPP` at `4931285ffb` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py CommunityRAPP --json` from the folder that holds both.
