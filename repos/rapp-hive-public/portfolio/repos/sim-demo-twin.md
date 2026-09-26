---
repo: kody-w/sim-demo-twin
family: twins
line: Twins
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: bf03e7ec77a0da88c12ae62e5fa236340ba2e619
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
  - RAPPcards
---

# sim-demo-twin: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/sim-demo-twin.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/sim-demo-twin` at `bf03e7ec77`](https://github.com/kody-w/sim-demo-twin/tree/bf03e7ec77a0da88c12ae62e5fa236340ba2e619) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4f90c698977d1e24f3c484561977545a569e394881b84205deba34c04a13b3d2`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Twins** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/sim-demo-twin` at `bf03e7ec77` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py sim-demo-twin --json` from the folder that holds both.
