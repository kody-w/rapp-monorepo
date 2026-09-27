---
repo: kody-w/RAPP_Desktop
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 03c8adf13aa7155a0791e0af4b9288331a3225cb
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/RAPP_Desktop/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-installer
  - RAPP_Hub
  - RAPP_Store
---

# RAPP_Desktop: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPP_Desktop.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPP_Desktop` at `03c8adf13a`](https://github.com/kody-w/RAPP_Desktop/tree/03c8adf13aa7155a0791e0af4b9288331a3225cb) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a7b688ff8510cb9a6793fd3572f2dd77b2f0fb1a73c4dcc49330a42335803f6e`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/RAPP_Desktop/blob/03c8adf13aa7155a0791e0af4b9288331a3225cb/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/RAPP_Desktop.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/RAPP_Desktop.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [RAPP_Hub](RAPP_Hub.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown).
Linked from 3: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPP_Desktop` at `03c8adf13a` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPP_Desktop --json` from the folder that holds both.
