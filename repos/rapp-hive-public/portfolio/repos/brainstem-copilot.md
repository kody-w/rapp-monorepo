---
repo: kody-w/brainstem-copilot
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 7f912fa2b93e4b88c74a3db1e286f1a3e2d33d06
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 4
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-installer
---

# brainstem-copilot: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/brainstem-copilot.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/brainstem-copilot` at `7f912fa2b9`](https://github.com/kody-w/brainstem-copilot/tree/7f912fa2b93e4b88c74a3db1e286f1a3e2d33d06) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8551e1ecdc6351efdbb1da3cff55ac65ff00071c24f612924e0b63be52146987`.
- "experimental" mentions: 4 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/brainstem-copilot` at `7f912fa2b9` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py brainstem-copilot --json` from the folder that holds both.
