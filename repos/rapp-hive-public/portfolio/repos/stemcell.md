---
repo: kody-w/stemcell
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 7cc90dd25a395d9feb3bb3e1efeafdbcee62acce
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 6
header: missing
channel: newest
lifecycle: active
links_to:
  - copilot-harness-sdk
---

# stemcell: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/stemcell.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/stemcell` at `7cc90dd25a`](https://github.com/kody-w/stemcell/tree/7cc90dd25a395d9feb3bb3e1efeafdbcee62acce) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `b9581c1928b98f65e9bc3382e03d9ef7163af4effc025000d031b49270cdd7f2`.
- "experimental" mentions: 6 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [copilot-harness-sdk](copilot-harness-sdk.md) (markdown, pin).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/stemcell` at `7cc90dd25a` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py stemcell --json` from the folder that holds both.
