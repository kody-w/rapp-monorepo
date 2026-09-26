---
repo: kody-w/rapp-skill
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: ff36d917d3a20b459cd37404fdf16ebd9d0a15a0
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - RAPP
  - rapp-1
  - rapp-brainstem
  - rapp-installer
  - rapp-map
  - rapp-skills
  - rapp-toaster
  - rapp-twin
  - RAPP_Store
  - RAR
---

# rapp-skill: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-skill.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-skill` at `ff36d917d3`](https://github.com/kody-w/rapp-skill/tree/ff36d917d3a20b459cd37404fdf16ebd9d0a15a0) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4e4f71525188d045b8ef5457097bf0cfb6d1102d121eedbfaa6cc2bb04e640d9`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 10 portfolio repo(s): [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-brainstem](rapp-brainstem.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-map](rapp-map.md) (markdown), [rapp-skills](rapp-skills.md) (markdown), [rapp-toaster](rapp-toaster.md) (markdown), [rapp-twin](rapp-twin.md) (markdown), [RAPP_Store](RAPP_Store.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-skill` at `ff36d917d3` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-skill --json` from the folder that holds both.
