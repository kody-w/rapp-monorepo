---
repo: kody-w/rapp-spinal-cord
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 43741e3e480f3de1a54e04ba37101e63bd985875
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-spinal-cord/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-flight-deck
  - rapp-installer
  - rapp-rings
  - rapp-twin
---

# rapp-spinal-cord: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-spinal-cord.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-spinal-cord` at `43741e3e48`](https://github.com/kody-w/rapp-spinal-cord/tree/43741e3e480f3de1a54e04ba37101e63bd985875) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `12bf36d7d8d0f900d1183b3d7b7976e22439622843be4123d1be858587f8c5c2`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-spinal-cord/blob/43741e3e480f3de1a54e04ba37101e63bd985875/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-spinal-cord.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-spinal-cord.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-spinal-cord` at `43741e3e48` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-spinal-cord --json` from the folder that holds both.
