---
repo: kody-w/RaGo
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: cff87bc642d0c39eb8f03048bc66d3c81b95bcd0
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/RaGo/pull/3
version: "v2.1.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-lantern
---

# RaGo: certified

![RAPP/1: certified, version v2.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RaGo.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v2.1.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RaGo` at `cff87bc642`](https://github.com/kody-w/RaGo/tree/cff87bc642d0c39eb8f03048bc66d3c81b95bcd0) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9269bc0ae7dfbc4523d498160c7c4cd5a818c29b2cb8b8c4a9c406abfe166d31`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/RaGo/blob/cff87bc642d0c39eb8f03048bc66d3c81b95bcd0/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/RaGo.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/RaGo.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-lantern](rapp-lantern.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RaGo` at `cff87bc642` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RaGo --json` from the folder that holds both.
