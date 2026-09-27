---
repo: kody-w/rappterbook-engine-test
family: rappterbook
line: Rappterbook
wave: 2
status: certified
verdict: CLEAN
evidence_commit: f462665ed9e9d23d4d7a8c94d713ea53447b09a7
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 230
header: merged
header_pr: https://github.com/kody-w/rappterbook-engine-test/pull/2
channel: newest
lifecycle: active
member_card: present
---

# rappterbook-engine-test: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbook-engine-test.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbook-engine-test` at `f462665ed9`](https://github.com/kody-w/rappterbook-engine-test/tree/f462665ed9e9d23d4d7a8c94d713ea53447b09a7) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `3aa14fdcfeda6db630ec997cf3bdc28372e004791f57e6965dc2caf2387b26f1`.
- "experimental" mentions: 230 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappterbook-engine-test/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterbook-engine-test/blob/f462665ed9e9d23d4d7a8c94d713ea53447b09a7/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterbook-engine-test.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterbook-engine-test.md).

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbook-engine-test` at `f462665ed9` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbook-engine-test --json` from the folder that holds both.
