---
repo: kody-w/rapp-refresh
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 920c3f4b72535136850b6c78ec4af79d5afe10c4
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-refresh/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
---

# rapp-refresh: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-refresh.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-refresh` at `920c3f4b72`](https://github.com/kody-w/rapp-refresh/tree/920c3f4b72535136850b6c78ec4af79d5afe10c4) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ce0473c5815ca1e0335ba269ef12bea466e72d15179b472e43a45402fac537d3`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-refresh/blob/920c3f4b72535136850b6c78ec4af79d5afe10c4/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-refresh.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-refresh.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-refresh` at `920c3f4b72` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-refresh --json` from the folder that holds both.
