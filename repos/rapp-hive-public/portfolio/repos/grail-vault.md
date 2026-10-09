---
repo: kody-w/grail-vault
family: projects
line: RAPP Projects
wave: 2
status: certified
verdict: CLEAN
evidence_commit: a83c38438391a6b3dfc8fbb4d6c15b1bed5c94d2
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-installer
---

# grail-vault: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/grail-vault.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/grail-vault` at `a83c384383`](https://github.com/kody-w/grail-vault/tree/a83c38438391a6b3dfc8fbb4d6c15b1bed5c94d2) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `37d1ba1601f0953665093c47e980bbe6872c8f16103605cb4764e0d55a365114`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **RAPP Projects** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/grail-vault` at `a83c384383` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py grail-vault --json` from the folder that holds both.
