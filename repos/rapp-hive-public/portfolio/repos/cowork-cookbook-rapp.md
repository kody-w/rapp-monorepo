---
repo: kody-w/cowork-cookbook-rapp
family: agents-rar
line: Agents (RAR)
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: d309e37d6c6732c6a48f31711cacf7deeef20a8a
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/cowork-cookbook-rapp/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-brainstem-sdk
  - rapp-egg-hub
  - rapp-neighborhood-protocol
  - rapp-zoo
  - RAPP_Store
---

# cowork-cookbook-rapp: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/cowork-cookbook-rapp.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/cowork-cookbook-rapp` at `d309e37d6c`](https://github.com/kody-w/cowork-cookbook-rapp/tree/d309e37d6c6732c6a48f31711cacf7deeef20a8a) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `257db8edaa3d37ee7b713f789195858216c2d7801b06d37ebcde749a306bfa24`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/cowork-cookbook-rapp/blob/d309e37d6c6732c6a48f31711cacf7deeef20a8a/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/cowork-cookbook-rapp.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/cowork-cookbook-rapp.md).

## Findings (1)

- `cowork_cookbook.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [rapp-brainstem-sdk](rapp-brainstem-sdk.md) (markdown), [rapp-egg-hub](rapp-egg-hub.md) (markdown), [rapp-neighborhood-protocol](rapp-neighborhood-protocol.md) (markdown), [rapp-zoo](rapp-zoo.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown).
Linked from 4: [racon](racon.md), [RAPP](RAPP.md), [rapp-carts](rapp-carts.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/cowork-cookbook-rapp` at `d309e37d6c` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py cowork-cookbook-rapp --json` from the folder that holds both.
