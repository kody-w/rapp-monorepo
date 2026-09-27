---
repo: kody-w/RAPP_Hub
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5426aeae93457c6a1cd0c0aab27654c73ab13ef7
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/RAPP_Hub/pull/3
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP_Store
---

# RAPP_Hub: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPP_Hub.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPP_Hub` at `5426aeae93`](https://github.com/kody-w/RAPP_Hub/tree/5426aeae93457c6a1cd0c0aab27654c73ab13ef7) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `8ccd9a53f724cd3c6093d0139de0ae3c3bee27c5495a31052d31a27496a31cf6`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/RAPP_Hub/blob/5426aeae93457c6a1cd0c0aab27654c73ab13ef7/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/RAPP_Hub.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/RAPP_Hub.md).

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [RAPP_Store](RAPP_Store.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [RAPP_Desktop](RAPP_Desktop.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPP_Hub` at `5426aeae93` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPP_Hub --json` from the folder that holds both.
