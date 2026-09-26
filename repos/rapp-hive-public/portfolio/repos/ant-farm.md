---
repo: kody-w/ant-farm
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: afe687cc00ad51f418f69f88a0418ca6bada8133
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - RAPPcards
---

# ant-farm: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/ant-farm.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/ant-farm` at `afe687cc00`](https://github.com/kody-w/ant-farm/tree/afe687cc00ad51f418f69f88a0418ca6bada8133) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8289131295146a6dfbf77298f31edefde4039fdac211215c942365b72af85db4`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 2: [RAPP](RAPP.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/ant-farm` at `afe687cc00` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py ant-farm --json` from the folder that holds both.
