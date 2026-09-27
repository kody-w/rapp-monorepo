---
repo: kody-w/rappdex
family: learn
line: Learn & Docs
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 25ff78e626e185dd9cf34249baeaebace6a625af
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rappdex/pull/1
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-mapp
  - rapp-pets
---

# rappdex: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappdex.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappdex` at `25ff78e626`](https://github.com/kody-w/rappdex/tree/25ff78e626e185dd9cf34249baeaebace6a625af) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `fc7fe76499adc40b675b44223d7003570c6f53191bc8716c326a82ae933b0131`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rappdex/blob/25ff78e626e185dd9cf34249baeaebace6a625af/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rappdex.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rappdex.md).

On the map: the **Learn & Docs** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-mapp](rapp-mapp.md) (markdown), [rapp-pets](rapp-pets.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-pets](rapp-pets.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappdex` at `25ff78e626` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappdex --json` from the folder that holds both.
