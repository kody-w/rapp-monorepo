---
repo: kody-w/rapp-brainstem-claude
family: connect
line: Brainstem Connect
wave: 2
status: certified
verdict: CLEAN
evidence_commit: e3651db29bc849fcaad18ef97f8bcdb15b019a75
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/rapp-brainstem-claude/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-brainstem-copilot
  - rapp-installer
---

# rapp-brainstem-claude: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-brainstem-claude.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-brainstem-claude` at `e3651db29b`](https://github.com/kody-w/rapp-brainstem-claude/tree/e3651db29bc849fcaad18ef97f8bcdb15b019a75) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `dc0cb9ed0c303f56588680fbea7d2b5a6d4115b9e084b1569d2955ce749ea05e`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp-brainstem-claude/pull/1).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-brainstem-claude/blob/e3651db29bc849fcaad18ef97f8bcdb15b019a75/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-brainstem-claude.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-brainstem-claude.md).

On the map: the **Brainstem Connect** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-brainstem-copilot](rapp-brainstem-copilot.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 13: [rapp-brainstem-claude-desktop](rapp-brainstem-claude-desktop.md), [rapp-brainstem-cline](rapp-brainstem-cline.md), [rapp-brainstem-codex](rapp-brainstem-codex.md), [rapp-brainstem-copilot](rapp-brainstem-copilot.md), [rapp-brainstem-cursor](rapp-brainstem-cursor.md), [rapp-brainstem-gemini](rapp-brainstem-gemini.md), [rapp-brainstem-goose](rapp-brainstem-goose.md), [rapp-brainstem-kiro](rapp-brainstem-kiro.md), [rapp-brainstem-mcp](rapp-brainstem-mcp.md), [rapp-brainstem-opencode](rapp-brainstem-opencode.md), [rapp-brainstem-vscode](rapp-brainstem-vscode.md), [rapp-brainstem-windsurf](rapp-brainstem-windsurf.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-brainstem-claude` at `e3651db29b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-brainstem-claude --json` from the folder that holds both.
