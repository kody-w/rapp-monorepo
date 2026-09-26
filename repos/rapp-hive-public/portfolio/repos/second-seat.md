---
repo: kody-w/second-seat
family: neighborhoods
line: Neighborhoods
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 79f70a28cccb7f84b25e1c6ab868d052f322d13f
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - heimdall
  - rapp-1
---

# second-seat: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/second-seat.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/second-seat` at `79f70a28cc`](https://github.com/kody-w/second-seat/tree/79f70a28cccb7f84b25e1c6ab868d052f322d13f) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `dab91fb902b9d5adb6ce8e7aa94ba15a285008817eddabcc1cb6c5500d44bad6`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Neighborhoods** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [heimdall](heimdall.md) (markdown), [rapp-1](rapp-1.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/second-seat` at `79f70a28cc` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py second-seat --json` from the folder that holds both.
