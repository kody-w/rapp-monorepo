---
repo: kody-w/rapp-ai
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: cc9e88d49191c8850955639dd02efe19975df1c6
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 7
header: merged
header_pr: https://github.com/kody-w/rapp-ai/pull/1
version: "1.0.0"
version_source: VERSION
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-static-apis
---

# rapp-ai: certified

![RAPP/1: certified, version 1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-ai.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-ai` at `cc9e88d491`](https://github.com/kody-w/rapp-ai/tree/cc9e88d49191c8850955639dd02efe19975df1c6) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `106d77051caf3bf9d4128722832842ac1d1c17b0a6e46dd0b3b04ff2a9a5d98d`.
- "experimental" mentions: 7 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp-ai/pull/1).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-ai/blob/cc9e88d49191c8850955639dd02efe19975df1c6/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-ai.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-ai.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-static-apis](rapp-static-apis.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-ai` at `cc9e88d491` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-ai --json` from the folder that holds both.
