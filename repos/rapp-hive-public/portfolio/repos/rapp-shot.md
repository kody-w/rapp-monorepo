---
repo: kody-w/rapp-shot
family: tools
line: Tools & Apps
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 0a3c2dfa62779294706ca6ad997132f1e644d879
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-shot/pull/5
version: "v1.3.1"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-tools
---

# rapp-shot: not yet

![RAPP/1: not yet, version v1.3.1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-shot.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.3.1`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-shot` at `0a3c2dfa62`](https://github.com/kody-w/rapp-shot/tree/0a3c2dfa62779294706ca6ad997132f1e644d879) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `2288be7290234de5c140b9c21d3993207304485b18aa1d8c458fb002c576f110`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-shot/blob/0a3c2dfa62779294706ca6ad997132f1e644d879/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-shot.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-shot.md).

## Findings (1)

- `rapp_shot/eggs/rapp_shot.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-tools](rapp-tools.md) (markdown).
Linked from 2: [rapp-monorepo](rapp-monorepo.md), [rapp-tools](rapp-tools.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-shot` at `0a3c2dfa62` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-shot --json` from the folder that holds both.
