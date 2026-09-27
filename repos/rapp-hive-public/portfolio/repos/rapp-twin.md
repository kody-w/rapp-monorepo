---
repo: kody-w/rapp-twin
family: twins
line: Twins
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 83cd87e80e4cf9fbb52163380165211569835ae8
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-twin/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-flight-deck
  - rapp-installer
  - rapp-rings
  - rapp-twin-in-residence
---

# rapp-twin: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-twin.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-twin` at `83cd87e80e`](https://github.com/kody-w/rapp-twin/tree/83cd87e80e4cf9fbb52163380165211569835ae8) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8b7be731705e43b437c56e7af1f99e39488e0e40fdce3646be0ececd41bfddd7`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-twin/blob/83cd87e80e4cf9fbb52163380165211569835ae8/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-twin.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-twin.md).

On the map: the **Twins** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-twin-in-residence](rapp-twin-in-residence.md) (markdown).
Linked from 13: [rapp-cortex](rapp-cortex.md), [rapp-docs](rapp-docs.md), [rapp-flight](rapp-flight.md), [rapp-flight-deck](rapp-flight-deck.md), [rapp-hippocampus](rapp-hippocampus.md), [rapp-monorepo](rapp-monorepo.md), [rapp-nervous-system](rapp-nervous-system.md), [rapp-platform](rapp-platform.md), [rapp-rings](rapp-rings.md), [rapp-sdk](rapp-sdk.md), [rapp-skill](rapp-skill.md), [rapp-spinal-cord](rapp-spinal-cord.md), [rapp-twin-in-residence](rapp-twin-in-residence.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-twin` at `83cd87e80e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-twin --json` from the folder that holds both.
