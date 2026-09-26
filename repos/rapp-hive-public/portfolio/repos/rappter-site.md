---
repo: kody-w/rappter-site
family: rappterverse
line: Rappterverse
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 6ed01825d66b051ebfa4bc9a2e9e236bdff08cc3
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: no-readme
channel: newest
lifecycle: active
---

# rappter-site: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-site.svg)

**Not yet:** 1 finding(s) from rapp_check: §12 schema label.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-site` at `6ed01825d6`](https://github.com/kody-w/rappter-site/tree/6ed01825d66b051ebfa4bc9a2e9e236bdff08cc3) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s), 2 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `7acbee6cea3d3ed09ae8c23303a2848aeba6da497b87f55a2517bcfb37b00396`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: no README (skipped).

## Findings (1)

- `mesh/rappid.json` · §12 schema label · schema='?', not 'rapp/1'

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Check it yourself

Clone `kody-w/rappter-site` at `6ed01825d6` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-site --json` from the folder that holds both.
