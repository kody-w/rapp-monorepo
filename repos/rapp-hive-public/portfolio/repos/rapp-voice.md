---
repo: kody-w/rapp-voice
family: tools
line: Tools & Apps
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 28e16c43f6c5ed1c2cdf47d8788ca8d655498ce8
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.1.1"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-tools
---

# rapp-voice: not yet

![RAPP/1: not yet, version v1.1.1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-voice.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.1.1`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-voice` at `28e16c43f6`](https://github.com/kody-w/rapp-voice/tree/28e16c43f6c5ed1c2cdf47d8788ca8d655498ce8) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4e0214a9755dadb16bd157b53f76c111ab248e5ccaadd0822460cd53ca945cfa`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `rapp_voice/eggs/rapp_voice.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-tools](rapp-tools.md) (markdown).
Linked from 3: [rapp-crispy](rapp-crispy.md), [rapp-monorepo](rapp-monorepo.md), [rapp-tools](rapp-tools.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-voice` at `28e16c43f6` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-voice --json` from the folder that holds both.
