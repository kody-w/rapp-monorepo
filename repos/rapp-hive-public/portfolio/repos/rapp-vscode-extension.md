---
repo: kody-w/rapp-vscode-extension
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 616046e608b8a6e9c064ef35ba12fba6702cbb4a
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/rapp-vscode-extension/pull/2
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-installer
---

# rapp-vscode-extension: certified

![RAPP/1: certified, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-vscode-extension.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-vscode-extension` at `616046e608`](https://github.com/kody-w/rapp-vscode-extension/tree/616046e608b8a6e9c064ef35ba12fba6702cbb4a) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `ca78a39543256be480c7f1f0629e8fcb694d738616b984bc5ea6a84b85426476`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/rapp-vscode-extension/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-vscode-extension/blob/616046e608b8a6e9c064ef35ba12fba6702cbb4a/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-vscode-extension.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-vscode-extension.md).

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown).
Linked from 3: [RAPP](RAPP.md), [RAPP-Bible](RAPP-Bible.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-vscode-extension` at `616046e608` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-vscode-extension --json` from the folder that holds both.
