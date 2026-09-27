---
repo: kody-w/rappter-plays-pokemon
family: openrappter
line: OpenRappter
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 8cf47995c749caa582034a3e5e5977931fba59ab
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: merged
header_pr: https://github.com/kody-w/rappter-plays-pokemon/pull/13
channel: newest
lifecycle: active
member_card: present
also_on:
  - worlds
---

# rappter-plays-pokemon: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-plays-pokemon.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-plays-pokemon` at `8cf47995c7`](https://github.com/kody-w/rappter-plays-pokemon/tree/8cf47995c749caa582034a3e5e5977931fba59ab) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `bec4815ee65f2a9effc61b4c1aea6eeb030503254c05e997786bf2e988f04c80`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappter-plays-pokemon/pull/13).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappter-plays-pokemon/blob/8cf47995c749caa582034a3e5e5977931fba59ab/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappter-plays-pokemon.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappter-plays-pokemon.md).

On the map: the **OpenRappter** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-play-pokemon](rapp-play-pokemon.md), [rappter-plays-palworld](rappter-plays-palworld.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-plays-pokemon` at `8cf47995c7` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-plays-pokemon --json` from the folder that holds both.
