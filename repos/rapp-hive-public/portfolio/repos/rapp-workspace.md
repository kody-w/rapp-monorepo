---
repo: kody-w/rapp-workspace
family: rapp1-core
line: RAPP/1 Core
wave: 1
status: certified
verdict: COMPLIANT
evidence_commit: 52d4f19df8f502218d77281c970eab3f4618fcbd
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 50
header: held
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
---

# rapp-workspace: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-workspace.svg)

**Certified:** rapp-1's own checker gave **COMPLIANT** (every RAPP artifact passes) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-workspace` at `52d4f19df8`](https://github.com/kody-w/rapp-workspace/tree/52d4f19df8f502218d77281c970eab3f4618fcbd) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **COMPLIANT**, 2 passing artifact(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4f12470cbac262f6b6346046908c11b74d7e16eb37d510abdccfb54d6e4d8a16`.
- "experimental" mentions: 50 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: held back: waiting on G24 (front door editable): its README bytes are part of the Workspace/1 core manifest (repository_evidence), whose SHA-256 is the frozen Workspace/1 identity that rapp-work-sdk/1 pins, so adding a line would change that identity. A successor identity that keeps the README out of the frozen bytes is being prepared; the header lands once the owner accepts it and the front door is editable.

On the map: the **RAPP/1 Core** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (pin), [rapp-1](rapp-1.md) (markdown, pin, workflow).
Linked from 7: [RAPP](RAPP.md), [rapp-model-hive](rapp-model-hive.md), [rapp-monorepo](rapp-monorepo.md), [rapp-omarchy](rapp-omarchy.md), [rapp-tools](rapp-tools.md), [rapp-work](rapp-work.md), [rapp-workspace-manager](rapp-workspace-manager.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-workspace` at `52d4f19df8` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-workspace --json` from the folder that holds both.
