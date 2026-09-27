---
repo: kody-w/rapp-overwatch
family: twins
line: Twins
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 868a5da6d31952843ed49707a515cd07b36b5eae
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-overwatch/pull/7
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-1
  - rapp-map
  - rapp-sentinel
---

# rapp-overwatch: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-overwatch.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-overwatch` at `868a5da6d3`](https://github.com/kody-w/rapp-overwatch/tree/868a5da6d31952843ed49707a515cd07b36b5eae) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c7e7a9e560986dfc0f2342a2a76e1b52ce32c5bc14015c640c809eb945336999`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-overwatch/blob/868a5da6d31952843ed49707a515cd07b36b5eae/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-overwatch.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-overwatch.md).

On the map: the **Twins** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-1](rapp-1.md) (markdown), [rapp-map](rapp-map.md) (markdown), [rapp-sentinel](rapp-sentinel.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-ratchet](rapp-ratchet.md), [rapp-sentinel](rapp-sentinel.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-overwatch` at `868a5da6d3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-overwatch --json` from the folder that holds both.
