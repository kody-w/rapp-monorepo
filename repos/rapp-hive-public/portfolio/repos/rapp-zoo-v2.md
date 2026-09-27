---
repo: kody-w/rapp-zoo-v2
family: worlds
line: Worlds & Play
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: e7f237705c2fab773725657313e3015a55a88f06
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/rapp-zoo-v2/pull/2
version: "v0.1.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
---

# rapp-zoo-v2: not yet

![RAPP/1: not yet, version v0.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-zoo-v2.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v0.1.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-zoo-v2` at `e7f237705c`](https://github.com/kody-w/rapp-zoo-v2/tree/e7f237705c2fab773725657313e3015a55a88f06) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `165d6d67c59d3e748bd99e3cc61ca9a73913fc9593b0c8214ecff37311e2f225`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp-zoo-v2/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-zoo-v2/blob/e7f237705c2fab773725657313e3015a55a88f06/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-zoo-v2.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-zoo-v2.md).

## Findings (1)

- `rappter-6be4a324.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: Expecting value: line 1 column 1 (char 0))

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-zoo-v2` at `e7f237705c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-zoo-v2 --json` from the folder that holds both.
