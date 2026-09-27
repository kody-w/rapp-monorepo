---
repo: kody-w/rapp-light
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 2d3501f5de78467fa84e9ecec8a2018a2af61ae5
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 5
header: present
header_pr: https://github.com/kody-w/rapp-light/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-keyring
  - rapp-train
---

# rapp-light: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-light.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-light` at `2d3501f5de`](https://github.com/kody-w/rapp-light/tree/2d3501f5de78467fa84e9ecec8a2018a2af61ae5) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `699b6a02c8268f88b90b23fc2be8bbb992372e940316676750adfdb17c839001`.
- "experimental" mentions: 5 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-light/blob/2d3501f5de78467fa84e9ecec8a2018a2af61ae5/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-light.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-light.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-keyring](rapp-keyring.md) (markdown), [rapp-train](rapp-train.md) (markdown).
Linked from 3: [rapp-docs](rapp-docs.md), [rapp-keyring](rapp-keyring.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-light` at `2d3501f5de` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-light --json` from the folder that holds both.
