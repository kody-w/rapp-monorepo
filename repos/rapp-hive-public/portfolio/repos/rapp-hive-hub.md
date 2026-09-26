---
repo: kody-w/rapp-hive-hub
family: hive
line: Hive
wave: 1
status: certified
verdict: COMPLIANT
evidence_commit: 1c154522dcc80a3ed3870e3c72bc430e6ed56bf9
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 7
header: present
header_pr: https://github.com/kody-w/rapp-hive-hub/pull/6
channel: newest
lifecycle: active
member_card: present
links_to:
  - hive-hub
  - rapp-1
  - rapp-installer
  - rapp-work
---

# rapp-hive-hub: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hive-hub.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-hive-hub` at `1c154522dc`](https://github.com/kody-w/rapp-hive-hub/tree/1c154522dcc80a3ed3870e3c72bc430e6ed56bf9) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 12 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `cb999693c8270d70976c00776d4e8769721a0613a1e385f2955215cc6d42e84f`.
- "experimental" mentions: 7 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-hive-hub/blob/1c154522dcc80a3ed3870e3c72bc430e6ed56bf9/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-hive-hub.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-hive-hub.md).

On the map: the **Hive** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [hive-hub](hive-hub.md) (markdown), [rapp-1](rapp-1.md) (pin), [rapp-installer](rapp-installer.md) (markdown), [rapp-work](rapp-work.md) (pin).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-hive-hub` at `1c154522dc` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-hive-hub --json` from the folder that holds both.
