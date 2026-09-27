---
repo: kody-w/rapp_orion
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 58e3ad74ce7c7e4fc6454a124028b4d490583a85
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 8
header: merged
header_pr: https://github.com/kody-w/rapp_orion/pull/3
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-installer
---

# rapp_orion: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp_orion.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp_orion` at `58e3ad74ce`](https://github.com/kody-w/rapp_orion/tree/58e3ad74ce7c7e4fc6454a124028b4d490583a85) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `1f2d80410bcae8d0f2a465ba39fc2ad07e5fb1a60e76ec2ee21a44a782688f41`.
- "experimental" mentions: 8 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp_orion/pull/3).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp_orion/blob/58e3ad74ce7c7e4fc6454a124028b4d490583a85/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp_orion.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp_orion.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp_orion` at `58e3ad74ce` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp_orion --json` from the folder that holds both.
