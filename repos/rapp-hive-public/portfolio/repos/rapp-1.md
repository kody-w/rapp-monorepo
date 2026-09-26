---
repo: kody-w/rapp-1
family: rapp1-core
line: RAPP/1 Core
wave: 1
status: certified
verdict: COMPLIANT
evidence_commit: bae4e3cacc33e82e7fcf9fe73d2fd043da97801d
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-1/pull/43
lts_version: "591e014"
lts_commit: 591e014ad39e223b00ab343ae26e5d9a867ebeee
lts_source: known
channel: rapp1-lts
lifecycle: active
member_card: present
links_to:
  - RAPP
  - rapp-installer
---

# rapp-1: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-1.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **LTS:** [`591e014`](https://github.com/kody-w/rapp-1/tree/591e014ad39e223b00ab343ae26e5d9a867ebeee) (commit `591e014ad3`, from the network's built-in known pins, until the estate publishes its LTS pins). **Channel:** `rapp1-lts`: it has a long-term-support pin, so the network builds on that commit; its newer commits are the newest channel.

- Evidence: [`kody-w/rapp-1` at `bae4e3cacc`](https://github.com/kody-w/rapp-1/tree/bae4e3cacc33e82e7fcf9fe73d2fd043da97801d) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 18 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `051fb8de0af0ab55f21f7f2e6f842c5c39534618e2b61a4cf590e8d9369ebfe3`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-1/blob/bae4e3cacc33e82e7fcf9fe73d2fd043da97801d/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-1.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-1.md).

On the map: the **RAPP/1 Core** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown).
Linked from 56: [dogg](dogg.md), [dogg-canon](dogg-canon.md), [dogg-markets](dogg-markets.md), [dogg-planet](dogg-planet.md), [echo-brainstem](echo-brainstem.md), [hive-hub](hive-hub.md), [lumen-brainstem](lumen-brainstem.md), [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [pkstop-central-park-bandshell](pkstop-central-park-bandshell.md), [pkstop-national-mall](pkstop-national-mall.md), [pkstop-pike-place-market](pkstop-pike-place-market.md), [pkstop-santa-monica-pier](pkstop-santa-monica-pier.md), [pkstop-the-bean](pkstop-the-bean.md), [RAPP](RAPP.md), [rapp-brain](rapp-brain.md), [rapp-brainfreeze](rapp-brainfreeze.md), [rapp-copilot-in-chrome](rapp-copilot-in-chrome.md), [rapp-copilot-in-edge](rapp-copilot-in-edge.md), [rapp-docs](rapp-docs.md), [rapp-dog-hub](rapp-dog-hub.md), [rapp-egg-hub](rapp-egg-hub.md), [rapp-estate](rapp-estate.md), [rapp-eternity](rapp-eternity.md), [rapp-hive-hub](rapp-hive-hub.md), [rapp-hive-public](rapp-hive-public.md), [rapp-mapp](rapp-mapp.md), [rapp-model-hive](rapp-model-hive.md), [rapp-monorepo](rapp-monorepo.md), [rapp-omarchy](rapp-omarchy.md), [rapp-organism](rapp-organism.md), [rapp-overwatch](rapp-overwatch.md), [rapp-parity](rapp-parity.md), [rapp-ratchet](rapp-ratchet.md), [rapp-sentinel](rapp-sentinel.md), [rapp-sentinel-hub](rapp-sentinel-hub.md), [rapp-skill](rapp-skill.md), [rapp-skills](rapp-skills.md), [rapp-specs](rapp-specs.md), [rapp-spine](rapp-spine.md), [rapp-test-neighbor](rapp-test-neighbor.md), [rapp-toaster](rapp-toaster.md), [rapp-tools](rapp-tools.md), [rapp-work](rapp-work.md), [rapp-workspace](rapp-workspace.md), [rapp-workspace-manager](rapp-workspace-manager.md), [RAPP_Store](RAPP_Store.md), [rappdex](rappdex.md), [RAR](RAR.md), [scout-brainstem-bootstrap](scout-brainstem-bootstrap.md), [second-seat](second-seat.md), [sentinel](sentinel.md), [sim-art-collective](sim-art-collective.md), [sim-demo-twin](sim-demo-twin.md), [tide-brainstem](tide-brainstem.md), [vbrainstem](vbrainstem.md), [wildhaven-ai-homes-twin](wildhaven-ai-homes-twin.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-1` at `bae4e3cacc` into `rapp-1` and again at `591e014` into `rapp-1-checker`, then run `python3 -B rapp-1-checker/rapp_check.py rapp-1 --json` from the folder that holds both.
