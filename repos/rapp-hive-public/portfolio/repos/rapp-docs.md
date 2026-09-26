---
repo: kody-w/rapp-docs
family: learn
line: Learn & Docs
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 0cd0b0a136997991d18dbd267432d47b5677f664
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 3
header: missing
channel: newest
lifecycle: active
links_to:
  - openrappter
  - rapp-1
  - rapp-flight-deck
  - rapp-installer
  - rapp-keyring
  - rapp-light
  - rapp-rings
  - rapp-train
  - rapp-twin
---

# rapp-docs: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-docs.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-docs` at `0cd0b0a136`](https://github.com/kody-w/rapp-docs/tree/0cd0b0a136997991d18dbd267432d47b5677f664) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `25cfe3b0e2dff3466805679f2aefd04ed2c7883780fcc75aec972cf822d5aef3`.
- "experimental" mentions: 3 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Learn & Docs** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 9 portfolio repo(s): [openrappter](openrappter.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-keyring](rapp-keyring.md) (markdown), [rapp-light](rapp-light.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-train](rapp-train.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-docs` at `0cd0b0a136` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-docs --json` from the folder that holds both.
