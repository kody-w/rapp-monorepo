---
repo: kody-w/rapp-rewind
family: tools
line: Tools & Apps
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 0b9e65c2e6c44332c2775e809bdeeb85a0f1bdac
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.2.1"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-crispy
  - rapp-tools
---

# rapp-rewind: not yet

![RAPP/1: not yet, version v1.2.1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-rewind.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.2.1`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-rewind` at `0b9e65c2e6`](https://github.com/kody-w/rapp-rewind/tree/0b9e65c2e6c44332c2775e809bdeeb85a0f1bdac) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `93fe8c40a0c3d373f3f76923f51691f7d345f3d4afaa27372475115de20d4922`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `rapp_rewind/eggs/rapp_rewind.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-crispy](rapp-crispy.md) (markdown), [rapp-tools](rapp-tools.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-tools](rapp-tools.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-rewind` at `0b9e65c2e6` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-rewind --json` from the folder that holds both.
