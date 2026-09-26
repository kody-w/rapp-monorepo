---
repo: kody-w/RAPPcards
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5bfcea8d6aaa78e988827783b44e0d384ed3c14a
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 2
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-installer
  - RAR
  - red-binder
---

# RAPPcards: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/RAPPcards.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/RAPPcards` at `5bfcea8d6a`](https://github.com/kody-w/RAPPcards/tree/5bfcea8d6aaa78e988827783b44e0d384ed3c14a) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `968e50bac9d1d60e98fc1be165180d4a88085f5af3344d91adca3a662684ae23`.
- "experimental" mentions: 2 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 4 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [RAR](RAR.md) (markdown), [red-binder](red-binder.md) (markdown).
Linked from 22: [ant-farm](ant-farm.md), [braintrust-template](braintrust-template.md), [echo-brainstem](echo-brainstem.md), [heimdall](heimdall.md), [lumen-brainstem](lumen-brainstem.md), [microsoft-se-team-neighborhood](microsoft-se-team-neighborhood.md), [obsidian-binder](obsidian-binder.md), [pkstop-central-park-bandshell](pkstop-central-park-bandshell.md), [pkstop-national-mall](pkstop-national-mall.md), [pkstop-pike-place-market](pkstop-pike-place-market.md), [pkstop-santa-monica-pier](pkstop-santa-monica-pier.md), [pkstop-the-bean](pkstop-the-bean.md), [public-art-collective](public-art-collective.md), [rapp-monorepo](rapp-monorepo.md), [rapp-spine](rapp-spine.md), [rapp-test-neighbor](rapp-test-neighbor.md), [red-binder](red-binder.md), [sim-art-collective](sim-art-collective.md), [sim-demo-twin](sim-demo-twin.md), [tide-brainstem](tide-brainstem.md), [twin-binder](twin-binder.md), [wildhaven-ai-homes-twin](wildhaven-ai-homes-twin.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/RAPPcards` at `5bfcea8d6a` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py RAPPcards --json` from the folder that holds both.
