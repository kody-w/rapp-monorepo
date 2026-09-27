---
repo: kody-w/rappterbook-governance
family: rappterbook
line: Rappterbook
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 1cb2f037d273383639b176485987f65433bc41fd
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rappterbook-governance/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - rappterbook
---

# rappterbook-governance: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbook-governance.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbook-governance` at `1cb2f037d2`](https://github.com/kody-w/rappterbook-governance/tree/1cb2f037d273383639b176485987f65433bc41fd) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `07c3f5f71350c1cfa57a7ab554b5f00e6be9ec3d8712e68de4d2b039f8817348`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterbook-governance/blob/1cb2f037d273383639b176485987f65433bc41fd/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterbook-governance.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterbook-governance.md).

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rappterbook](rappterbook.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbook-governance` at `1cb2f037d2` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbook-governance --json` from the folder that holds both.
