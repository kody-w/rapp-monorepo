---
repo: kody-w/scout-brainstem-bootstrap
family: connect
line: Brainstem Connect
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 0c384d8ed35c30359ca338d1a87e62f78335a547
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 48
header: merged
header_pr: https://github.com/kody-w/scout-brainstem-bootstrap/pull/2
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-1
  - rapp-installer
---

# scout-brainstem-bootstrap: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/scout-brainstem-bootstrap.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/scout-brainstem-bootstrap` at `0c384d8ed3`](https://github.com/kody-w/scout-brainstem-bootstrap/tree/0c384d8ed35c30359ca338d1a87e62f78335a547) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `c06ea5d5d976335a005b1bd029904ebc15876090c7f922b6ed8618cb9b5481ff`.
- "experimental" mentions: 48 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/scout-brainstem-bootstrap/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/scout-brainstem-bootstrap/blob/0c384d8ed35c30359ca338d1a87e62f78335a547/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/scout-brainstem-bootstrap.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/scout-brainstem-bootstrap.md).

On the map: the **Brainstem Connect** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-1](rapp-1.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/scout-brainstem-bootstrap` at `0c384d8ed3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py scout-brainstem-bootstrap --json` from the folder that holds both.
