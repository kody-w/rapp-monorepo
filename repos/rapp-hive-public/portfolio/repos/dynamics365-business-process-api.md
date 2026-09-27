---
repo: kody-w/dynamics365-business-process-api
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 9b5fa4302ddcc227db446a3745f41c2667702818
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/dynamics365-business-process-api/pull/1
channel: newest
lifecycle: active
member_card: present
---

# dynamics365-business-process-api: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/dynamics365-business-process-api.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/dynamics365-business-process-api` at `9b5fa4302d`](https://github.com/kody-w/dynamics365-business-process-api/tree/9b5fa4302ddcc227db446a3745f41c2667702818) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `6c2087d4389a0576fa02024ac938ce91f4d5cf57c9019db789f68225a089accd`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/dynamics365-business-process-api/blob/9b5fa4302ddcc227db446a3745f41c2667702818/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/dynamics365-business-process-api.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/dynamics365-business-process-api.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/dynamics365-business-process-api` at `9b5fa4302d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py dynamics365-business-process-api --json` from the folder that holds both.
