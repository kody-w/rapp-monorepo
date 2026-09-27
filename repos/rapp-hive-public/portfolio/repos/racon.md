---
repo: kody-w/racon
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 7f941ce190e70852fe9da323f4bba5357946c0d8
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/racon/pull/5
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - cowork-cookbook-rapp
  - rapp-carts
  - rapp-mcp
  - rapp-neighborhood-protocol
---

# racon: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/racon.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/racon` at `7f941ce190`](https://github.com/kody-w/racon/tree/7f941ce190e70852fe9da323f4bba5357946c0d8) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e0b5673fe9f285a0c7fac2ea3c265de70ff87888eb4840b53f6ea404b5f4687c`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/racon/blob/7f941ce190e70852fe9da323f4bba5357946c0d8/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/racon.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/racon.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [cowork-cookbook-rapp](cowork-cookbook-rapp.md) (markdown), [rapp-carts](rapp-carts.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown).
Linked from 4: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-carts](rapp-carts.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/racon` at `7f941ce190` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py racon --json` from the folder that holds both.
