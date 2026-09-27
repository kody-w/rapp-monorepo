---
repo: kody-w/ez-rapp
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: cd3a32b4babb0c07edbefb9d3190112bf173cbee
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/ez-rapp/pull/2
version: "v0.1.3"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - CommunityRAPP
  - rapp-installer
  - RAR
---

# ez-rapp: certified

![RAPP/1: certified, version v0.1.3](https://kody-w.github.io/rapp-hive-public/portfolio/badges/ez-rapp.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.1.3`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/ez-rapp` at `cd3a32b4ba`](https://github.com/kody-w/ez-rapp/tree/cd3a32b4babb0c07edbefb9d3190112bf173cbee) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a1269766f58c0be55ac2afa595f6555507937ba1619db49a680b5eda1dc25052`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/ez-rapp/blob/cd3a32b4babb0c07edbefb9d3190112bf173cbee/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/ez-rapp.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/ez-rapp.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 2: [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/ez-rapp` at `cd3a32b4ba` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py ez-rapp --json` from the folder that holds both.
