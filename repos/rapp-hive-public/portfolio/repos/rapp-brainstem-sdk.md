---
repo: kody-w/rapp-brainstem-sdk
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 8175627eed09f5616fcbab60599ea96123e824a3
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-brainstem-sdk/pull/4
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-map
  - rapp-mcp
  - RAR
  - vbrainstem
---

# rapp-brainstem-sdk: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-brainstem-sdk.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-brainstem-sdk` at `8175627eed`](https://github.com/kody-w/rapp-brainstem-sdk/tree/8175627eed09f5616fcbab60599ea96123e824a3) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4e2dd54742eed36dc773f8a0012f242355e2dfdd48d0f9bb886cee7d87457a42`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-brainstem-sdk/blob/8175627eed09f5616fcbab60599ea96123e824a3/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-brainstem-sdk.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-brainstem-sdk.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [rapp-map](rapp-map.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [RAR](RAR.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).
Linked from 6: [cowork-cookbook-rapp](cowork-cookbook-rapp.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAPP_Store](RAPP_Store.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-brainstem-sdk` at `8175627eed` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-brainstem-sdk --json` from the folder that holds both.
