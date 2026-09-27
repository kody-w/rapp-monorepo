---
repo: kody-w/rapp-crispy
family: tools
line: Tools & Apps
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: ed03f3689e98f300878a0b07463573ffa4917c39
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: present
header_pr: https://github.com/kody-w/rapp-crispy/pull/5
version: "v1.5.1"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-tools
  - rapp-voice
---

# rapp-crispy: not yet

![RAPP/1: not yet, version v1.5.1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-crispy.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** `v1.5.1`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-crispy` at `ed03f3689e`](https://github.com/kody-w/rapp-crispy/tree/ed03f3689e98f300878a0b07463573ffa4917c39) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `735a69b36575f12900581f34fbf5f3d1a074bb8897622d7e35c22420373577cc`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-crispy/blob/ed03f3689e98f300878a0b07463573ffa4917c39/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-crispy.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-crispy.md).

## Findings (1)

- `rapp_crispy/eggs/rapp_crispy.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [rapp-tools](rapp-tools.md) (markdown), [rapp-voice](rapp-voice.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-rewind](rapp-rewind.md), [rapp-tools](rapp-tools.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-crispy` at `ed03f3689e` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-crispy --json` from the folder that holds both.
