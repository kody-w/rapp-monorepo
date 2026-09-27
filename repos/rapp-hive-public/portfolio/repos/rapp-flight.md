---
repo: kody-w/rapp-flight
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 18197ea1eb5be09a162b927e0591295a507e7f95
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: present
header_pr: https://github.com/kody-w/rapp-flight/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-flight-deck
  - rapp-installer
  - rapp-rings
  - rapp-twin
---

# rapp-flight: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-flight.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-flight` at `18197ea1eb`](https://github.com/kody-w/rapp-flight/tree/18197ea1eb5be09a162b927e0591295a507e7f95) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `144c6a3ad209cdcbff346b6d813c3101127017a8c59f9eaf83baadafef36e183`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-flight/blob/18197ea1eb5be09a162b927e0591295a507e7f95/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-flight.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-flight.md).

On the map: the **Release Channels** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-flight` at `18197ea1eb` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-flight --json` from the folder that holds both.
