---
repo: kody-w/rapp-claude-skills
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 4ec5b427757942708c5706cc8a6755b6755f7410
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-claude-skills/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-commons
  - RAR
---

# rapp-claude-skills: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-claude-skills.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-claude-skills` at `4ec5b42775`](https://github.com/kody-w/rapp-claude-skills/tree/4ec5b427757942708c5706cc8a6755b6755f7410) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ae967358d5f98baf4012c1a7ac15e0a70403d57a9fda414704176f4559741601`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-claude-skills/blob/4ec5b427757942708c5706cc8a6755b6755f7410/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-claude-skills.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-claude-skills.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-commons](rapp-commons.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 2: [RAPP](RAPP.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-claude-skills` at `4ec5b42775` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-claude-skills --json` from the folder that holds both.
