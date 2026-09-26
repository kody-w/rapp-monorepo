---
repo: kody-w/rapp-work
family: rapp1-core
line: RAPP/1 Core
wave: 1
status: certified
verdict: COMPLIANT
evidence_commit: 4d1a5272eaa6c77f1efd4dbbebf01d5b3411260b
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-work/pull/3
lts_version: "29ead23"
lts_commit: 29ead23b21645f8d7682ee00414930ffa9ce0ca6
lts_source: known
channel: rapp1-lts
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-1
  - rapp-workspace
  - rapp-workspace-manager
---

# rapp-work: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-work.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **LTS:** [`29ead23`](https://github.com/kody-w/rapp-work/tree/29ead23b21645f8d7682ee00414930ffa9ce0ca6) (commit `29ead23b21`, from the network's built-in known pins, until the estate publishes its LTS pins). **Channel:** `rapp1-lts`: it has a long-term-support pin, so the network builds on that commit; its newer commits are the newest channel.

- Evidence: [`kody-w/rapp-work` at `4d1a5272ea`](https://github.com/kody-w/rapp-work/tree/4d1a5272eaa6c77f1efd4dbbebf01d5b3411260b) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 1 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `7077263db5435c026db9c50353292240f116308bac08afe6ba8a3012134395cb`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-work/blob/4d1a5272eaa6c77f1efd4dbbebf01d5b3411260b/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-work.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-work.md).

On the map: the **RAPP/1 Core** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (pin), [rapp-1](rapp-1.md) (markdown, pin), [rapp-workspace](rapp-workspace.md) (markdown), [rapp-workspace-manager](rapp-workspace-manager.md) (markdown).
Linked from 8: [hive-hub](hive-hub.md), [rapp-brainstem-plugin](rapp-brainstem-plugin.md), [rapp-hive-hub](rapp-hive-hub.md), [rapp-hive-public](rapp-hive-public.md), [rapp-lab-kit](rapp-lab-kit.md), [rapp-model-hive](rapp-model-hive.md), [rapp-monorepo](rapp-monorepo.md), [rapp-skills](rapp-skills.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-work` at `4d1a5272ea` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-work --json` from the folder that holds both.
