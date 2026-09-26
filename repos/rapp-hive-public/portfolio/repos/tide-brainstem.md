---
repo: kody-w/tide-brainstem
family: twins
line: Twins
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 72162a8c6b97c344caff2c102bd897e725d180ef
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
also_on:
  - brainstem
links_to:
  - RAPP
  - rapp-1
  - RAPP_Sense_Store
  - RAPP_Store
  - RAPPcards
---

# tide-brainstem: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/tide-brainstem.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/tide-brainstem` at `72162a8c6b`](https://github.com/kody-w/tide-brainstem/tree/72162a8c6b97c344caff2c102bd897e725d180ef) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `56de4a21a12abe16ef00e0551de5bd9b1f536fc7d1a674e4b3d6fa38a6c36ab9`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Twins** line, and also Brainstem ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [RAPP_Sense_Store](RAPP_Sense_Store.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 2: [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/tide-brainstem` at `72162a8c6b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py tide-brainstem --json` from the folder that holds both.
