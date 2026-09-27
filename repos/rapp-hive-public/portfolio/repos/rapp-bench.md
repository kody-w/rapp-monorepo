---
repo: kody-w/rapp-bench
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 396eeeb251faf0e5963475e9c9adac9430d5f38b
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-bench/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-postflight
---

# rapp-bench: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-bench.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-bench` at `396eeeb251`](https://github.com/kody-w/rapp-bench/tree/396eeeb251faf0e5963475e9c9adac9430d5f38b) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a41ea2a3664fdb5c84e54b226e96959dae1346eceafc2ec79ab9a5b299093d24`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-bench/blob/396eeeb251faf0e5963475e9c9adac9430d5f38b/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-bench.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-bench.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-postflight](rapp-postflight.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-bench` at `396eeeb251` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-bench --json` from the folder that holds both.
