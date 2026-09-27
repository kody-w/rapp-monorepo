---
repo: kody-w/rapp-keyring
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: b7dac71e7730216ae4992ca7dcf349c8fa094c98
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-keyring/pull/1
version: "0.1.0"
version_source: VERSION
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-light
  - rapp-train
---

# rapp-keyring: certified

![RAPP/1: certified, version 0.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-keyring.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.1.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-keyring` at `b7dac71e77`](https://github.com/kody-w/rapp-keyring/tree/b7dac71e7730216ae4992ca7dcf349c8fa094c98) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `cbeec080845a605eac7628a023f99b8ef171d3c73e0d8baafd38732d55569e00`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-keyring/blob/b7dac71e7730216ae4992ca7dcf349c8fa094c98/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-keyring.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-keyring.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-light](rapp-light.md) (markdown), [rapp-train](rapp-train.md) (markdown).
Linked from 3: [rapp-docs](rapp-docs.md), [rapp-light](rapp-light.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-keyring` at `b7dac71e77` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-keyring --json` from the folder that holds both.
