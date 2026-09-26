---
repo: kody-w/rapp-neighborhood-protocol
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 44e0c6eb49d619932e645fb9d9b12a5fa37f71b1
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-commons
  - rapp-kited-twin
  - rapp-mcp
  - rapp-sealed
  - rapp-vneighborhood
  - RAR
  - vbrainstem
---

# rapp-neighborhood-protocol: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-neighborhood-protocol.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-neighborhood-protocol` at `44e0c6eb49`](https://github.com/kody-w/rapp-neighborhood-protocol/tree/44e0c6eb49d619932e645fb9d9b12a5fa37f71b1) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `34521206d8475a622fd41afb8b0adc571d81f50c7bbc2487e3cc142eb040c0a1`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 8 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-commons](rapp-commons.md) (markdown), [rapp-kited-twin](rapp-kited-twin.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [rapp-sealed](rapp-sealed.md) (markdown), [rapp-vneighborhood](rapp-vneighborhood.md) (markdown), [RAR](RAR.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).
Linked from 21: [cowork-cookbook-rapp](cowork-cookbook-rapp.md), [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [racon](racon.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-carts](rapp-carts.md), [rapp-commons](rapp-commons.md), [rapp-demos](rapp-demos.md), [rapp-doorman](rapp-doorman.md), [rapp-kite](rapp-kite.md), [rapp-monorepo](rapp-monorepo.md), [rapp-sealed](rapp-sealed.md), [rapp-spine](rapp-spine.md), [rapp-stack-cubby](rapp-stack-cubby.md), [rapp-test-neighbor](rapp-test-neighbor.md), [rapp-vneighborhood](rapp-vneighborhood.md), [rapp-work-cubbies](rapp-work-cubbies.md), [RAPP_Store](RAPP_Store.md), [RAR](RAR.md), [vneighborhood-design-studio](vneighborhood-design-studio.md), [vneighborhood-research-lab](vneighborhood-research-lab.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-neighborhood-protocol` at `44e0c6eb49` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-neighborhood-protocol --json` from the folder that holds both.
