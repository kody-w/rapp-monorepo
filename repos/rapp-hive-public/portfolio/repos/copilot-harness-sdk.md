---
repo: kody-w/copilot-harness-sdk
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5a66a54aa8ef13b3591ce036bd0edbf4694d947c
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 40
header: present
header_pr: https://github.com/kody-w/copilot-harness-sdk/pull/10
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-brainfreeze-studio
  - RAR
---

# copilot-harness-sdk: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/copilot-harness-sdk.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/copilot-harness-sdk` at `5a66a54aa8`](https://github.com/kody-w/copilot-harness-sdk/tree/5a66a54aa8ef13b3591ce036bd0edbf4694d947c) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f195f3b6a0bd3097c1e222eba8e26af928fd44060ce9caeb5ce61c01ad9ca97e`.
- "experimental" mentions: 40 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/copilot-harness-sdk/blob/5a66a54aa8ef13b3591ce036bd0edbf4694d947c/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/copilot-harness-sdk.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/copilot-harness-sdk.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-brainfreeze-studio](rapp-brainfreeze-studio.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 4: [learn-brainstem](learn-brainstem.md), [rapp-brainfreeze-studio](rapp-brainfreeze-studio.md), [rapp-monorepo](rapp-monorepo.md), [stemcell](stemcell.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/copilot-harness-sdk` at `5a66a54aa8` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py copilot-harness-sdk --json` from the folder that holds both.
