---
repo: kody-w/RAPP_hippo
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: c55d62315104540f859a9e9db6d14fc385739f8e
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 9
header: missing
version: "1.0.0"
version_source: VERSION
channel: newest
lifecycle: active
links_to:
  - CommunityRAPP
  - rapp-installer
---

# RAPP_hippo: certified

![RAPP/1: certified, version 1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPP_hippo.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPP_hippo` at `c55d623151`](https://github.com/kody-w/RAPP_hippo/tree/c55d62315104540f859a9e9db6d14fc385739f8e) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c378d83e4b6167b58dca8fdb36a7a228935988e5f4f73f38dc6bb2cc0e1f6a10`.
- "experimental" mentions: 9 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [CommunityRAPP](CommunityRAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPP_hippo` at `c55d623151` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPP_hippo --json` from the folder that holds both.
