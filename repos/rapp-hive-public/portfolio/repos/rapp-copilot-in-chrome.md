---
repo: kody-w/rapp-copilot-in-chrome
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: a947e5fadba102ca55babb16598778e69083e9fd
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-copilot-in-chrome/pull/19
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-1
  - rapp-messaging
  - rapp-toaster
---

# rapp-copilot-in-chrome: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-copilot-in-chrome.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-copilot-in-chrome` at `a947e5fadb`](https://github.com/kody-w/rapp-copilot-in-chrome/tree/a947e5fadba102ca55babb16598778e69083e9fd) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `bd1900503e499210d3992d7ba98a4a9cf9fe9077fb5a3723a0c8c4954afa1b72`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-copilot-in-chrome/blob/a947e5fadba102ca55babb16598778e69083e9fd/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-copilot-in-chrome.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-copilot-in-chrome.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-1](rapp-1.md) (markdown), [rapp-messaging](rapp-messaging.md) (markdown), [rapp-toaster](rapp-toaster.md) (markdown).
Linked from 2: [rapp-copilot-in-edge](rapp-copilot-in-edge.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-copilot-in-chrome` at `a947e5fadb` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-copilot-in-chrome --json` from the folder that holds both.
