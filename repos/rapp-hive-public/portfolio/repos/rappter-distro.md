---
repo: kody-w/rappter-distro
family: rappterverse
line: Rappterverse
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: fe8d558b3930a14b95bc21987c3f4923d8dc1c04
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 29
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-commons
  - rapp-installer
---

# rappter-distro: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-distro.svg)

**Not yet:** 4 finding(s) from rapp_check: §9 egg ×4.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-distro` at `fe8d558b39`](https://github.com/kody-w/rappter-distro/tree/fe8d558b3930a14b95bc21987c3f4923d8dc1c04) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 4 finding(s), 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a0714eb26d63b48c01fd68eeef73332cc5db645ca9b668d7642be99c9880dd47`.
- "experimental" mentions: 29 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (4)

- `examples/rapp-commons/.well-known/neighborhood.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: JSON egg bytes MUST equal canonical(manifest))
- `rapp-zoo/starters/journal.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `rapp-zoo/starters/playtime.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `rapp-zoo/starters/workday.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-commons](rapp-commons.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 4: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-distro` at `fe8d558b39` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-distro --json` from the folder that holds both.
