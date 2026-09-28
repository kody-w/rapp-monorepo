---
repo: kody-w/rapp-sentinel
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: d9824feac92e1e7f0e859b834c9fd69d1a577741
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/rapp-sentinel/pull/118
channel: newest
lifecycle: active
member_card: present
links_to:
  - openrappter
  - public-art-collective
  - rapp-1
  - rapp-overwatch
  - rapp-ratchet
  - rapp-sentinel-hub
  - rapp-vision
  - sentinel
---

# rapp-sentinel: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-sentinel.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-sentinel` at `d9824feac9`](https://github.com/kody-w/rapp-sentinel/tree/d9824feac92e1e7f0e859b834c9fd69d1a577741) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ed5680a1db0aba4cf17b75edec433d01c98c3992bbbe5d5882fb4addbc44455a`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-sentinel/blob/d9824feac92e1e7f0e859b834c9fd69d1a577741/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-sentinel.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-sentinel.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 8 portfolio repo(s): [openrappter](openrappter.md) (markdown), [public-art-collective](public-art-collective.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-overwatch](rapp-overwatch.md) (markdown), [rapp-ratchet](rapp-ratchet.md) (markdown), [rapp-sentinel-hub](rapp-sentinel-hub.md) (markdown), [rapp-vision](rapp-vision.md) (markdown), [sentinel](sentinel.md) (markdown).
Linked from 8: [rapp-imessage-launchpad](rapp-imessage-launchpad.md), [rapp-monorepo](rapp-monorepo.md), [rapp-overwatch](rapp-overwatch.md), [rapp-sentinel-hub](rapp-sentinel-hub.md), [rapp-vision-neighborhood](rapp-vision-neighborhood.md), [rappterverse](rappterverse.md), [RAR](RAR.md), [sentinel](sentinel.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-sentinel` at `d9824feac9` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-sentinel --json` from the folder that holds both.
