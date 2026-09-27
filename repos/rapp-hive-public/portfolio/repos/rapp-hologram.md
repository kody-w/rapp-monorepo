---
repo: kody-w/rapp-hologram
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 421b90d64fe1fef143258ec9b7be2f3a06d97fbc
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-hologram/pull/4
version: "1.0.0"
version_source: VERSION
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-moment
---

# rapp-hologram: certified

![RAPP/1: certified, version 1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hologram.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-hologram` at `421b90d64f`](https://github.com/kody-w/rapp-hologram/tree/421b90d64fe1fef143258ec9b7be2f3a06d97fbc) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ac162b6666e5f1abc2d3f38a131dabdb306dc620c64c5688defb24cf5b3c81fa`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-hologram/blob/421b90d64fe1fef143258ec9b7be2f3a06d97fbc/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-hologram.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-hologram.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-moment](rapp-moment.md) (markdown).
Linked from 4: [double-jump](double-jump.md), [rapp-moment](rapp-moment.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-hologram` at `421b90d64f` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-hologram --json` from the folder that holds both.
