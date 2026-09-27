---
repo: kody-w/rapp-hatchery
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 1a7fd78dbdb625929cbf3880102ac9c59cb7abef
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: present
header_pr: https://github.com/kody-w/rapp-hatchery/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-brainfreeze
  - rapp-brainfreeze-studio
  - rapp-installer
---

# rapp-hatchery: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hatchery.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-hatchery` at `1a7fd78dbd`](https://github.com/kody-w/rapp-hatchery/tree/1a7fd78dbdb625929cbf3880102ac9c59cb7abef) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f4d41c5b71be473ec729ef0e00299fcee514fd3f4895d4c9e5e5fd104339317f`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-hatchery/blob/1a7fd78dbdb625929cbf3880102ac9c59cb7abef/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-hatchery.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-hatchery.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-brainfreeze](rapp-brainfreeze.md) (markdown), [rapp-brainfreeze-studio](rapp-brainfreeze-studio.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-hatchery` at `1a7fd78dbd` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-hatchery --json` from the folder that holds both.
