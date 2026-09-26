---
repo: kody-w/rapp-egg-hub
family: agents-rar
line: Agents (RAR)
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 4c49318fcafe526c56802c50131699006501e3e1
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 11
header: missing
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
  - rapp-drift-lint
  - rapp-installer
  - rapp-moment
  - RAPP_Store
  - rappterbox
  - RAR
---

# rapp-egg-hub: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-egg-hub.svg)

**Not yet:** 6 finding(s) from rapp_check: §9 egg ×6.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-egg-hub` at `4c49318fca`](https://github.com/kody-w/rapp-egg-hub/tree/4c49318fcafe526c56802c50131699006501e3e1) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 6 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `31a4529db16f3bc6f8567b7d6873101dc7b365445742ebfdce9d026c9a1fdffa`.
- "experimental" mentions: 11 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (6)

- `eggs/generic-twin.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `eggs/grandma-rose.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `eggs/kody-w.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `eggs/rappterbook-cohesive.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: floats require full-JCS number serialization; use ints/strings)
- `eggs/rock-tumbler.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `eggs/wildhaven-ceo.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 8 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-drift-lint](rapp-drift-lint.md) (workflow), [rapp-installer](rapp-installer.md) (markdown), [rapp-moment](rapp-moment.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown), [rappterbox](rappterbox.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 11: [cowork-cookbook-rapp](cowork-cookbook-rapp.md), [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-brainfreeze-studio](rapp-brainfreeze-studio.md), [rapp-carts](rapp-carts.md), [rapp-monorepo](rapp-monorepo.md), [rapp-rock-tumbler](rapp-rock-tumbler.md), [rapp-spine](rapp-spine.md), [rapp-vision-neighborhood](rapp-vision-neighborhood.md), [RAPP_Store](RAPP_Store.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-egg-hub` at `4c49318fca` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-egg-hub --json` from the folder that holds both.
