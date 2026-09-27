---
repo: kody-w/rappter-site
family: rappterverse
line: Rappterverse
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: c0b7950b404d27bed54b706d747bbe5a7e1ec494
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: merged
header_pr: https://github.com/kody-w/rappter-site/pull/6
channel: newest
lifecycle: active
member_card: present
---

# rappter-site: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-site.svg)

**Not yet:** 1 finding(s) from rapp_check: §12 schema label.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-site` at `c0b7950b40`](https://github.com/kody-w/rappter-site/tree/c0b7950b404d27bed54b706d747bbe5a7e1ec494) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s), 2 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `7acbee6cea3d3ed09ae8c23303a2848aeba6da497b87f55a2517bcfb37b00396`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappter-site/pull/6).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappter-site/blob/c0b7950b404d27bed54b706d747bbe5a7e1ec494/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappter-site.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappter-site.md).

## Findings (1)

- `mesh/rappid.json` · §12 schema label · schema='?', not 'rapp/1'

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-site` at `c0b7950b40` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-site --json` from the folder that holds both.
