---
repo: kody-w/rapp-static-apis
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 63bea74fbf04de6da9453accb842f7130d2d3db4
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-map
  - rapp-mcp
  - RAR
---

# rapp-static-apis: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-static-apis.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-static-apis` at `63bea74fbf`](https://github.com/kody-w/rapp-static-apis/tree/63bea74fbf04de6da9453accb842f7130d2d3db4) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e3341ad052e00b3a9430279ea34b591ba0806d66be28a3982e88530eba6fbba5`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-map](rapp-map.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 16: [rapp-ai](rapp-ai.md), [rapp-basket](rapp-basket.md), [RAPP-Bible](RAPP-Bible.md), [rapp-commons](rapp-commons.md), [rapp-dataverse](rapp-dataverse.md), [rapp-lantern](rapp-lantern.md), [rapp-mcp](rapp-mcp.md), [rapp-monorepo](rapp-monorepo.md), [rapp-release-train](rapp-release-train.md), [rapp-skills](rapp-skills.md), [rapp-snap](rapp-snap.md), [rapp-spine](rapp-spine.md), [rapp-static-brainstem](rapp-static-brainstem.md), [rapp-static-mcp](rapp-static-mcp.md), [rappter-prompts](rappter-prompts.md), [rappter-vui](rappter-vui.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-static-apis` at `63bea74fbf` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-static-apis --json` from the folder that holds both.
