---
repo: kody-w/openrappter-nightly
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: ea34fa6b210496c629ab39d2bb007f0d65fc6b17
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
also_on:
  - openrappter
links_to:
  - openrappter-release-train
---

# openrappter-nightly: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/openrappter-nightly.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/openrappter-nightly` at `ea34fa6b21`](https://github.com/kody-w/openrappter-nightly/tree/ea34fa6b210496c629ab39d2bb007f0d65fc6b17) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `54aac27727188c4152740c1c0bee7d86cc2a087009a2a646a2d3f58d2ad15cd2`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line, and also OpenRappter ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [openrappter-release-train](openrappter-release-train.md) (workflow).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/openrappter-nightly` at `ea34fa6b21` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py openrappter-nightly --json` from the folder that holds both.
