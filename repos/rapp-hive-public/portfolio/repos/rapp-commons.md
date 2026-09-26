---
repo: kody-w/rapp-commons
family: dogg
line: DOGG & Commons
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 560eacce518ca3fbf5709b4ceb60e2adc401be84
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
  - RAPP-Bible
  - rapp-mcp
  - rapp-neighborhood-protocol
  - rapp-static-apis
---

# rapp-commons: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-commons.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-commons` at `560eacce51`](https://github.com/kody-w/rapp-commons/tree/560eacce518ca3fbf5709b4ceb60e2adc401be84) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s), 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `2b22eb60ed2be12111ee738125a1af7a1177adbc5e697bc2e46d7381e74561c3`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `.well-known/neighborhood.egg` · §9 egg · not a conformant rapp/1-egg (schema=rapp/1-egg; §10: invite verification requires estate_owner_rappid)

On the map: the **DOGG & Commons** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [RAPP](RAPP.md) (markdown), [RAPP-Bible](RAPP-Bible.md) (markdown), [rapp-mcp](rapp-mcp.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (markdown).
Linked from 16: [double-jump](double-jump.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-claude-skills](rapp-claude-skills.md), [rapp-god-forum](rapp-god-forum.md), [rapp-monorepo](rapp-monorepo.md), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md), [rapp-resident](rapp-resident.md), [rapp-spine](rapp-spine.md), [rapp-vneighborhood](rapp-vneighborhood.md), [RAPP_Store](RAPP_Store.md), [rappter-distro](rappter-distro.md), [rappterbook-commons](rappterbook-commons.md), [RAR](RAR.md), [vneighborhood-design-studio](vneighborhood-design-studio.md), [vneighborhood-research-lab](vneighborhood-research-lab.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-commons` at `560eacce51` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-commons --json` from the folder that holds both.
