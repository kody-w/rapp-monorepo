---
repo: kody-w/brainstem-agent
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: a8801a2081df1aee877fa37bdd8611a6cb6383fc
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 59
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-installer
---

# brainstem-agent: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/brainstem-agent.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/brainstem-agent` at `a8801a2081`](https://github.com/kody-w/brainstem-agent/tree/a8801a2081df1aee877fa37bdd8611a6cb6383fc) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `247d898dae74a34585700d5484d5a5a3d8274673646d4b50c6be725c8a8abb63`.
- "experimental" mentions: 59 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/brainstem-agent` at `a8801a2081` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py brainstem-agent --json` from the folder that holds both.
