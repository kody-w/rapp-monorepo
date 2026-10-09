---
repo: kody-w/rappterbook-agent
family: rappterbook
line: Rappterbook
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 01ec54cecfac8a16ff703193a169bd6d6cbf6c6e
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: present
header_pr: https://github.com/kody-w/rappterbook-agent/pull/3
channel: newest
lifecycle: active
member_card: present
links_to:
  - openrappter
  - rappterbook
---

# rappterbook-agent: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappterbook-agent.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappterbook-agent` at `01ec54cecf`](https://github.com/kody-w/rappterbook-agent/tree/01ec54cecfac8a16ff703193a169bd6d6cbf6c6e) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `2e61745a5cfacd5e2079931a9b5c6fe41a597459f2a567429754278ac13d6742`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappterbook-agent/blob/01ec54cecfac8a16ff703193a169bd6d6cbf6c6e/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappterbook-agent.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappterbook-agent.md).

On the map: the **Rappterbook** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [openrappter](openrappter.md) (markdown), [rappterbook](rappterbook.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappterbook-agent` at `01ec54cecf` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappterbook-agent --json` from the folder that holds both.
