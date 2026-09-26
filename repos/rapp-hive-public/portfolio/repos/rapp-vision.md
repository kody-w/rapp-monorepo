---
repo: kody-w/rapp-vision
family: rappvision
line: Rappvision
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c988c195d7a705d7ae139c81d384a5bc9f0d2c5e
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "oil-field-season-v1.0.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - rapp-rock-tumbler
  - rappvision-rappterbox
---

# rapp-vision: certified

![RAPP/1: certified, version oil-field-season-v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-vision.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `oil-field-season-v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-vision` at `c988c195d7`](https://github.com/kody-w/rapp-vision/tree/c988c195d7a705d7ae139c81d384a5bc9f0d2c5e) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `14a1bcfc18e7f5d3ca364f2fa32c8d72f815d11a72f28ee7fa58faf9c28e405f`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Rappvision** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-rock-tumbler](rapp-rock-tumbler.md) (markdown), [rappvision-rappterbox](rappvision-rappterbox.md) (markdown).
Linked from 22: [rapp-metrics](rapp-metrics.md), [rapp-monorepo](rapp-monorepo.md), [rapp-remix](rapp-remix.md), [rapp-sentinel](rapp-sentinel.md), [rappvision-after-midnight-maps](rappvision-after-midnight-maps.md), [rappvision-brainstem-notes](rappvision-brainstem-notes.md), [rappvision-creature-office-hours](rappvision-creature-office-hours.md), [rappvision-field-notes](rappvision-field-notes.md), [rappvision-kitchen-table-physics](rappvision-kitchen-table-physics.md), [rappvision-null-arcade](rappvision-null-arcade.md), [rappvision-one-minute-orchestra](rappvision-one-minute-orchestra.md), [rappvision-patch-notes-tomorrow](rappvision-patch-notes-tomorrow.md), [rappvision-pigeon-post](rappvision-pigeon-post.md), [rappvision-prompt-frontier](rappvision-prompt-frontier.md), [rappvision-protocol-minute](rappvision-protocol-minute.md), [rappvision-rappid-zoo](rappvision-rappid-zoo.md), [rappvision-rappterbox](rappvision-rappterbox.md), [rappvision-receipt-culture](rappvision-receipt-culture.md), [rappvision-repair-manual](rappvision-repair-manual.md), [rappvision-rnr](rappvision-rnr.md), [rappvision-signal-garden](rappvision-signal-garden.md), [rappvision-tiny-bureau](rappvision-tiny-bureau.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-vision` at `c988c195d7` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-vision --json` from the folder that holds both.
