---
repo: kody-w/pkstop-central-park-bandshell
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 42b79c0f4ace88a055dc4911bc665391d5eb77dd
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
  - rapp-installer
  - RAPPcards
---

# pkstop-central-park-bandshell: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/pkstop-central-park-bandshell.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/pkstop-central-park-bandshell` at `42b79c0f4a`](https://github.com/kody-w/pkstop-central-park-bandshell/tree/42b79c0f4ace88a055dc4911bc665391d5eb77dd) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `bed9564b7048c920949971327be0c5b6d9b9f097d366e49034465fe375942f5e`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/pkstop-central-park-bandshell` at `42b79c0f4a` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py pkstop-central-park-bandshell --json` from the folder that holds both.
