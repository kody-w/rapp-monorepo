---
repo: kody-w/rapp-postflight
family: estate
line: Estate & Ops
wave: 2
status: certified
verdict: CLEAN
evidence_commit: e4d8178bc0b86735d92b14a40203a824dbeb73ab
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-postflight/pull/7
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-installer
---

# rapp-postflight: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-postflight.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-postflight` at `e4d8178bc0`](https://github.com/kody-w/rapp-postflight/tree/e4d8178bc0b86735d92b14a40203a824dbeb73ab) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `fb3bc1dd820cfc2973e1944f44745d0c578dbe6b479f1ea7a50acf08c7d3ca49`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-postflight/blob/e4d8178bc0b86735d92b14a40203a824dbeb73ab/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-postflight.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-postflight.md).

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 4: [rapp-bench](rapp-bench.md), [rapp-monorepo](rapp-monorepo.md), [rapp-quests](rapp-quests.md), [rapp-support](rapp-support.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-postflight` at `e4d8178bc0` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-postflight --json` from the folder that holds both.
