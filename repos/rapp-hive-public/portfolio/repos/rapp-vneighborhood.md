---
repo: kody-w/rapp-vneighborhood
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 624993f7acf11991ff955a0ad9d8e105c54c9353
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-vneighborhood/pull/3
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-commons
  - rapp-mcp
  - rapp-neighborhood-protocol
  - rapp-sealed
  - vneighborhood-design-studio
  - vneighborhood-research-lab
---

# rapp-vneighborhood: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-vneighborhood.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-vneighborhood` at `624993f7ac`](https://github.com/kody-w/rapp-vneighborhood/tree/624993f7acf11991ff955a0ad9d8e105c54c9353) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `00305f82285231402a89e8ac0701c964bf708fbb83de18e0ae95f3f7de43bd54`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-vneighborhood/blob/624993f7acf11991ff955a0ad9d8e105c54c9353/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-vneighborhood.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-vneighborhood.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 6 portfolio repo(s): [rapp-commons](rapp-commons.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-sealed](rapp-sealed.md) (markdown), [vneighborhood-design-studio](vneighborhood-design-studio.md) (markdown), [vneighborhood-research-lab](vneighborhood-research-lab.md) (markdown).
Linked from 9: [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md), [rapp-spine](rapp-spine.md), [rapp-test-neighbor](rapp-test-neighbor.md), [vneighborhood-design-studio](vneighborhood-design-studio.md), [vneighborhood-research-lab](vneighborhood-research-lab.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-vneighborhood` at `624993f7ac` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-vneighborhood --json` from the folder that holds both.
