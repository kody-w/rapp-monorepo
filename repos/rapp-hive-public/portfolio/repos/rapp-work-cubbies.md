---
repo: kody-w/rapp-work-cubbies
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 8197e2a13be0906db6a85eac07cb81683f5d0ca6
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-work-cubbies/pull/12
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-neighborhood-protocol
  - rapp-spine
---

# rapp-work-cubbies: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-work-cubbies.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-work-cubbies` at `8197e2a13b`](https://github.com/kody-w/rapp-work-cubbies/tree/8197e2a13be0906db6a85eac07cb81683f5d0ca6) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e06766a2557d7533438bc09f1a77f716948ed7e14fead62705a0c2da2468719f`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-work-cubbies/blob/8197e2a13be0906db6a85eac07cb81683f5d0ca6/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-work-cubbies.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-work-cubbies.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-spine](rapp-spine.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-work-cubbies` at `8197e2a13b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-work-cubbies --json` from the folder that holds both.
