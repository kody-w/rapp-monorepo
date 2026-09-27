---
repo: kody-w/rapp-carts
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 135d0a5747ebcf6abc77e984c157594e8d1ccaf1
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-carts/pull/4
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - cowork-cookbook-rapp
  - racon
  - rapp-egg-hub
  - rapp-mcp
  - rapp-neighborhood-protocol
  - RAPP_Store
---

# rapp-carts: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-carts.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-carts` at `135d0a5747`](https://github.com/kody-w/rapp-carts/tree/135d0a5747ebcf6abc77e984c157594e8d1ccaf1) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `48b42fad649fb7bbd916be42136ec62d46f4232e44821d7676d8040288244229`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-carts/blob/135d0a5747ebcf6abc77e984c157594e8d1ccaf1/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-carts.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-carts.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 6 portfolio repo(s): [cowork-cookbook-rapp](cowork-cookbook-rapp.md) (markdown), [racon](racon.md) (markdown), [rapp-egg-hub](rapp-egg-hub.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown).
Linked from 6: [racon](racon.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [rapp-remix](rapp-remix.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-carts` at `135d0a5747` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-carts --json` from the folder that holds both.
