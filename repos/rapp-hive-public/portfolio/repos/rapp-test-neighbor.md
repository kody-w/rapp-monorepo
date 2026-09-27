---
repo: kody-w/rapp-test-neighbor
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: COMPLIANT
evidence_commit: 3cc46ae268f09f25e954dc28a88e35051ea71acf
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-test-neighbor/pull/7
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-neighborhood-protocol
  - rapp-vneighborhood
  - RAPPcards
---

# rapp-test-neighbor: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-test-neighbor.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-test-neighbor` at `3cc46ae268`](https://github.com/kody-w/rapp-test-neighbor/tree/3cc46ae268f09f25e954dc28a88e35051ea71acf) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e17135014c15ee864d9bb7a0832e2ba4656a7ab80cb7b3fe299937749f1c5bed`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-test-neighbor/blob/3cc46ae268f09f25e954dc28a88e35051ea71acf/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-test-neighbor.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-test-neighbor.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-vneighborhood](rapp-vneighborhood.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 2: [RAPP](RAPP.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-test-neighbor` at `3cc46ae268` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-test-neighbor --json` from the folder that holds both.
