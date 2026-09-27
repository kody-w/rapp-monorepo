---
repo: kody-w/rappter-plays-palworld
family: openrappter
line: OpenRappter
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d07fa9639f740bba3e5f21e2b4b0d2d5769b95fc
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rappter-plays-palworld/pull/1
channel: newest
lifecycle: active
member_card: present
also_on:
  - worlds
links_to:
  - openrappter
  - rappter-plays-pokemon
---

# rappter-plays-palworld: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappter-plays-palworld.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappter-plays-palworld` at `d07fa9639f`](https://github.com/kody-w/rappter-plays-palworld/tree/d07fa9639f740bba3e5f21e2b4b0d2d5769b95fc) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `30365c1595020a48cab127af5555911e64f00692df5507da5a93b3f4b68c0b57`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappter-plays-palworld/blob/d07fa9639f740bba3e5f21e2b4b0d2d5769b95fc/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappter-plays-palworld.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappter-plays-palworld.md).

On the map: the **OpenRappter** line, and also Worlds & Play ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [openrappter](openrappter.md) (markdown), [rappter-plays-pokemon](rappter-plays-pokemon.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappter-plays-palworld` at `d07fa9639f` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappter-plays-palworld --json` from the folder that holds both.
