---
repo: kody-w/twin-binder
family: twins
line: Twins
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5e41cd9088deee8394d22d5941f1fa8bc37b990f
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
also_on:
  - agents-rar
links_to:
  - RAPPcards
---

# twin-binder: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/twin-binder.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/twin-binder` at `5e41cd9088`](https://github.com/kody-w/twin-binder/tree/5e41cd9088deee8394d22d5941f1fa8bc37b990f) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ca1084777a00cb52ecf56f4e87174070700ce57a0be5700331709b84db1bc758`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Twins** line, and also Agents (RAR) ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [RAPPcards](RAPPcards.md) (markdown).
Linked from 2: [obsidian-binder](obsidian-binder.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/twin-binder` at `5e41cd9088` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py twin-binder --json` from the folder that holds both.
