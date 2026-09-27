---
repo: kody-w/sentinel
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: e3222361765929d7685ab85978b8cac171020cba
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/sentinel/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-1
  - rapp-sentinel
---

# sentinel: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/sentinel.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/sentinel` at `e322236176`](https://github.com/kody-w/sentinel/tree/e3222361765929d7685ab85978b8cac171020cba) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `55d4b74d9b0f1a1c3027ff5df5cd8ce77251998a419ddd8a9dfc249fa049d601`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/sentinel/blob/e3222361765929d7685ab85978b8cac171020cba/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/sentinel.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/sentinel.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-1](rapp-1.md) (markdown), [rapp-sentinel](rapp-sentinel.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-sentinel](rapp-sentinel.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/sentinel` at `e322236176` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py sentinel --json` from the folder that holds both.
