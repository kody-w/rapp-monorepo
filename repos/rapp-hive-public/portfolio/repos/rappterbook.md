---
repo: kody-w/rappterbook
family: rappterbook
line: Rappterbook
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 52515cc28de089d4661e9c7d2c63c72de58a1935
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4166
header: missing
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - lisppy
  - lisppy-shepherd
  - mars-barn
  - openrappter
  - RAPP
  - rapp-installer
  - rappterbook-knowledge-graph
  - rappterbook-mars-barn
  - RAR
---

# rappterbook: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbook.svg)

**Not yet:** 12 finding(s) from rapp_check: §9 egg ×10, §12 schema label, verification unavailable; 1 of them unverified.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbook` at `52515cc28d`](https://github.com/kody-w/rappterbook/tree/52515cc28de089d4661e9c7d2c63c72de58a1935) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 12 finding(s), 6 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e2cb0fa4c99f38b4095595de3d07f0d530141dede828eb385a2849e73d28f6f9`.
- "experimental" mentions: 4166 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (12)

- `state/commons/rappid.json` · §12 schema label · schema='?', not 'rapp/1'
- `.` · verification unavailable · bounded frame discovery JSON budget exhausted (unverified)
- `awakening.rappterbook.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `docs/egg/examples/sparky.rappter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `docs/kodyTwinAI.rapp.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `eggs/rappterbook-cohesive.network.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `kodyTwinAI.rapp.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `medic.rapp.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `state/phylogeny/founders/azure-mind.rappter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: JSON egg bytes MUST equal canonical(manifest))
- `state/phylogeny/founders/gold-storm.rappter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: JSON egg bytes MUST equal canonical(manifest))
- `state/phylogeny/founders/scarlet-fang.rappter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: JSON egg bytes MUST equal canonical(manifest))
- `state/phylogeny/founders/verdant-vow.rappter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: JSON egg bytes MUST equal canonical(manifest))

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 9 portfolio repo(s): [lisppy](lisppy.md) (markdown), [lisppy-shepherd](lisppy-shepherd.md) (markdown), [mars-barn](mars-barn.md) (markdown), [openrappter](openrappter.md) (markdown), [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rappterbook-knowledge-graph](rappterbook-knowledge-graph.md) (markdown), [rappterbook-mars-barn](rappterbook-mars-barn.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 20: [lisppy](lisppy.md), [lisppy-shepherd](lisppy-shepherd.md), [mars-barn](mars-barn.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-leviathan-hub](rapp-leviathan-hub.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [rappter-factory](rappter-factory.md), [rappterbook-agent](rappterbook-agent.md), [rappterbook-agent-dna](rappterbook-agent-dna.md), [rappterbook-governance](rappterbook-governance.md), [rappterbook-knowledge-graph](rappterbook-knowledge-graph.md), [rappterbook-market-maker](rappterbook-market-maker.md), [rappterbook-mars-barn](rappterbook-mars-barn.md), [rappterbook-phantom](rappterbook-phantom.md), [rappterbook-social-graph](rappterbook-social-graph.md), [rappterbook-v2-state](rappterbook-v2-state.md), [rappterbook-vm](rappterbook-vm.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbook` at `52515cc28d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbook --json` from the folder that holds both.
