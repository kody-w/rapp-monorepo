---
repo: kody-w/rapp-kite
family: twins
line: Twins
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 6c1c05641dd9b19b8037d40c06ed3835378d4531
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-kite/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-map
  - rapp-neighborhood-protocol
  - rapp-sealed
  - vbrainstem
---

# rapp-kite: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-kite.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-kite` at `6c1c05641d`](https://github.com/kody-w/rapp-kite/tree/6c1c05641dd9b19b8037d40c06ed3835378d4531) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9d0618f7bcf5c8f1567172cd821d3d1e2163d2a87025b02e44ff2d0b03da2af5`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-kite/blob/6c1c05641dd9b19b8037d40c06ed3835378d4531/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-kite.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-kite.md).

On the map: the **Twins** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [rapp-map](rapp-map.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-sealed](rapp-sealed.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).
Linked from 5: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-doorman](rapp-doorman.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-kite` at `6c1c05641d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-kite --json` from the folder that holds both.
