---
repo: kody-w/rapp-map
family: learn
line: Learn & Docs
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 81dd6f05ab0969d11253f3fe7f4834288824d17e
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 54
header: missing
version: "v1.0.0"
version_source: release
lts_version: "4c8ba6b"
lts_commit: 4c8ba6bbe73125cc980d0c3b38c59c99e4b231c0
lts_source: known
channel: rapp1-lts
lifecycle: active
---

# rapp-map: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-map.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **LTS:** [`4c8ba6b`](https://github.com/kody-w/rapp-map/tree/4c8ba6bbe73125cc980d0c3b38c59c99e4b231c0) (commit `4c8ba6bbe7`, from the network's built-in known pins, until the estate publishes its LTS pins). **Channel:** `rapp1-lts`: it has a long-term-support pin, so the network builds on that commit; its newer commits are the newest channel.

- Evidence: [`kody-w/rapp-map` at `81dd6f05ab`](https://github.com/kody-w/rapp-map/tree/81dd6f05ab0969d11253f3fe7f4834288824d17e) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s), 26 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c37cc9c787beea0c40fc8065b10b80eafa3b55e295cc43a4e9f44f3579f3f8b0`.
- "experimental" mentions: 54 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `spine/vertebrae/estate-2026-07-25.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Learn & Docs** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 20: [brainstem-harness](brainstem-harness.md), [RAPP-Bible](RAPP-Bible.md), [rapp-brainstem-sdk](rapp-brainstem-sdk.md), [rapp-demos](rapp-demos.md), [rapp-kite](rapp-kite.md), [rapp-kited-twin](rapp-kited-twin.md), [rapp-local-install](rapp-local-install.md), [rapp-model-hive](rapp-model-hive.md), [rapp-monorepo](rapp-monorepo.md), [rapp-omarchy](rapp-omarchy.md), [rapp-overwatch](rapp-overwatch.md), [rapp-ratchet](rapp-ratchet.md), [rapp-release-train](rapp-release-train.md), [rapp-roadmap](rapp-roadmap.md), [rapp-second-brain](rapp-second-brain.md), [rapp-skill](rapp-skill.md), [rapp-spine](rapp-spine.md), [rapp-static-apis](rapp-static-apis.md), [rapp-tower](rapp-tower.md), [rio](rio.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-map` at `81dd6f05ab` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-map --json` from the folder that holds both.
