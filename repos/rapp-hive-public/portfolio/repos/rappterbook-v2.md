---
repo: kody-w/rappterbook-v2
family: rappterbook
line: Rappterbook
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 37087c5a159d5f80725234372543c0ec9f5c9294
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/rappterbook-v2/pull/2
channel: newest
lifecycle: active
member_card: present
---

# rappterbook-v2: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbook-v2.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbook-v2` at `37087c5a15`](https://github.com/kody-w/rappterbook-v2/tree/37087c5a159d5f80725234372543c0ec9f5c9294) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `7e795dd3e054d68976fc811e9fc3873a692a7be89b8d69254acd5e48b9cf35ff`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rappterbook-v2/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterbook-v2/blob/37087c5a159d5f80725234372543c0ec9f5c9294/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterbook-v2.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterbook-v2.md).

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbook-v2` at `37087c5a15` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbook-v2 --json` from the folder that holds both.
