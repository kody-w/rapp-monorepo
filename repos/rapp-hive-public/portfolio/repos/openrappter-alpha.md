---
repo: kody-w/openrappter-alpha
family: release
line: Release Channels
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 235e93e8d08f2028a4b4a3a4231db16783ee7d55
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
also_on:
  - openrappter
links_to:
  - openrappter
  - openrappter-release-train
---

# openrappter-alpha: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/openrappter-alpha.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/openrappter-alpha` at `235e93e8d0`](https://github.com/kody-w/openrappter-alpha/tree/235e93e8d08f2028a4b4a3a4231db16783ee7d55) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `01e74d69d041ca31c54a279fcffab8be556f00b74c3ed83806bb59b665da4d4a`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Release Channels** line, and also OpenRappter ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [openrappter](openrappter.md) (markdown), [openrappter-release-train](openrappter-release-train.md) (workflow).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/openrappter-alpha` at `235e93e8d0` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py openrappter-alpha --json` from the folder that holds both.
