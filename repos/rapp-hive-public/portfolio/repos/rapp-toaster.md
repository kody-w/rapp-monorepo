---
repo: kody-w/rapp-toaster
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5abff7027cb43ac1186f68285ff87525bdd32974
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-toaster/pull/5
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-skills
---

# rapp-toaster: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-toaster.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-toaster` at `5abff7027c`](https://github.com/kody-w/rapp-toaster/tree/5abff7027cb43ac1186f68285ff87525bdd32974) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `491d3b1969e00d32eacfe100391536eeb5b23b8059cde7c398631680a72abd7f`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-toaster/blob/5abff7027cb43ac1186f68285ff87525bdd32974/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-toaster.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-toaster.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-skills](rapp-skills.md) (markdown).
Linked from 5: [rapp-copilot-in-chrome](rapp-copilot-in-chrome.md), [rapp-copilot-in-edge](rapp-copilot-in-edge.md), [rapp-monorepo](rapp-monorepo.md), [rapp-skill](rapp-skill.md), [rapp-tower](rapp-tower.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-toaster` at `5abff7027c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-toaster --json` from the folder that holds both.
