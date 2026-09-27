---
repo: kody-w/openrappter-release-train
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: eeb78033ae20b4806c667423738825868b0ab4ab
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/openrappter-release-train/pull/7
channel: newest
lifecycle: active
member_card: present
also_on:
  - openrappter
links_to:
  - openrappter
---

# openrappter-release-train: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/openrappter-release-train.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/openrappter-release-train` at `eeb78033ae`](https://github.com/kody-w/openrappter-release-train/tree/eeb78033ae20b4806c667423738825868b0ab4ab) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `826c8262a1c4cd100c4fa1abb482241ae87a0ca2bf63985c506d84c009d6762b`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/openrappter-release-train/blob/eeb78033ae20b4806c667423738825868b0ab4ab/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/openrappter-release-train.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/openrappter-release-train.md).

On the map: the **Release Channels** line, and also OpenRappter ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [openrappter](openrappter.md) (markdown).
Linked from 5: [openrappter-alpha](openrappter-alpha.md), [openrappter-beta](openrappter-beta.md), [openrappter-canary](openrappter-canary.md), [openrappter-nightly](openrappter-nightly.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/openrappter-release-train` at `eeb78033ae` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py openrappter-release-train --json` from the folder that holds both.
