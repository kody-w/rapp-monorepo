---
repo: kody-w/rapp-brainfreeze-studio
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 9e621b479a5fc4100f99b7e984e84649a80e63e3
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: present
header_pr: https://github.com/kody-w/rapp-brainfreeze-studio/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - copilot-harness-sdk
  - rapp-brainfreeze
  - RAPP_Store
  - RAR
---

# rapp-brainfreeze-studio: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-brainfreeze-studio.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-brainfreeze-studio` at `9e621b479a`](https://github.com/kody-w/rapp-brainfreeze-studio/tree/9e621b479a5fc4100f99b7e984e84649a80e63e3) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9e905158718c3f3b38b508236eb4cd632e52f47d1cdfa0748a70a295d1cc2b86`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-brainfreeze-studio/blob/9e621b479a5fc4100f99b7e984e84649a80e63e3/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-brainfreeze-studio.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-brainfreeze-studio.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [copilot-harness-sdk](copilot-harness-sdk.md) (markdown), [rapp-brainfreeze](rapp-brainfreeze.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 3: [copilot-harness-sdk](copilot-harness-sdk.md), [rapp-hatchery](rapp-hatchery.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-brainfreeze-studio` at `9e621b479a` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-brainfreeze-studio --json` from the folder that holds both.
