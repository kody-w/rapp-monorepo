---
repo: kody-w/red-binder
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 704e7b8ddae9c8fbaf03e074cbad855696ffd445
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 10
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPPcards
  - RAR
---

# red-binder: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/red-binder.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/red-binder` at `704e7b8dda`](https://github.com/kody-w/red-binder/tree/704e7b8ddae9c8fbaf03e074cbad855696ffd445) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `d1c4e6322fa4490fb252b19d52639d98b7317c60c38648b19d8ac9cfdcb00530`.
- "experimental" mentions: 10 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPPcards](RAPPcards.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [RAPPcards](RAPPcards.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/red-binder` at `704e7b8dda` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py red-binder --json` from the folder that holds both.
