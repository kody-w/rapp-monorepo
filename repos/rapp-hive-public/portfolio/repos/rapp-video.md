---
repo: kody-w/rapp-video
family: rappvision
line: Rappvision
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 2984dcb69e941eb3b183be297f6e0be2b698a431
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 6
header: present
header_pr: https://github.com/kody-w/rapp-video/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-installer
---

# rapp-video: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-video.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-video` at `2984dcb69e`](https://github.com/kody-w/rapp-video/tree/2984dcb69e941eb3b183be297f6e0be2b698a431) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `044bc968fdb03e932f46ced8317fd6fecb93fe3c5692032fb54f6704581f4069`.
- "experimental" mentions: 6 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-video/blob/2984dcb69e941eb3b183be297f6e0be2b698a431/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-video.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-video.md).

On the map: the **Rappvision** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 2: [rapp-brainstem-walkthrough](rapp-brainstem-walkthrough.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-video` at `2984dcb69e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-video --json` from the folder that holds both.
