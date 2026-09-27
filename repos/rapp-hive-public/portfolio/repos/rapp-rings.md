---
repo: kody-w/rapp-rings
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 4750f738d0b2e3ffc667d4e9af14c48aa609c34f
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-rings/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-flight-deck
  - rapp-installer
  - rapp-twin
---

# rapp-rings: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-rings.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-rings` at `4750f738d0`](https://github.com/kody-w/rapp-rings/tree/4750f738d0b2e3ffc667d4e9af14c48aa609c34f) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `77b3d5806a543d2b6d8189a957b7bbdf0936ffb115049f5acfc2db5075941065`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-rings/blob/4750f738d0b2e3ffc667d4e9af14c48aa609c34f/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-rings.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-rings.md).

On the map: the **Release Channels** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 12: [rapp-cortex](rapp-cortex.md), [rapp-docs](rapp-docs.md), [rapp-flight](rapp-flight.md), [rapp-flight-deck](rapp-flight-deck.md), [rapp-hippocampus](rapp-hippocampus.md), [rapp-monorepo](rapp-monorepo.md), [rapp-nervous-system](rapp-nervous-system.md), [rapp-platform](rapp-platform.md), [rapp-sdk](rapp-sdk.md), [rapp-spinal-cord](rapp-spinal-cord.md), [rapp-twin](rapp-twin.md), [rapp-twin-in-residence](rapp-twin-in-residence.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-rings` at `4750f738d0` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-rings --json` from the folder that holds both.
