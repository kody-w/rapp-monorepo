---
repo: kody-w/RAPP-Network
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 33f6ba6c5ea970b44a0514b0913fdfe6ccd29f01
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/RAPP-Network/pull/8
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-mcp
---

# RAPP-Network: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPP-Network.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPP-Network` at `33f6ba6c5e`](https://github.com/kody-w/RAPP-Network/tree/33f6ba6c5ea970b44a0514b0913fdfe6ccd29f01) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `429ce617ec45dd8092b702df9a57f943c619aa8a56ea9775de12d3059ecf2db1`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/RAPP-Network/blob/33f6ba6c5ea970b44a0514b0913fdfe6ccd29f01/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/RAPP-Network.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/RAPP-Network.md).

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown).
Linked from 4: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPP-Network` at `33f6ba6c5e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPP-Network --json` from the folder that holds both.
