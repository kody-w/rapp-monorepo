---
repo: kody-w/chat
family: brainstem
line: Brainstem
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 3daf0fcaedd9772ddebe6ca31299d94d7a52b35a
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-installer
  - rapp-mapp
  - vbrainstem
---

# chat: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/chat.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/chat` at `3daf0fcaed`](https://github.com/kody-w/chat/tree/3daf0fcaedd9772ddebe6ca31299d94d7a52b35a) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `5c051564546b0181a38c71340b8b0a0d73893d3a7afff9240141cc0e04fd6bd3`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Brainstem** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-installer](rapp-installer.md) (markdown), [rapp-mapp](rapp-mapp.md) (markdown), [vbrainstem](vbrainstem.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/chat` at `3daf0fcaed` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py chat --json` from the folder that holds both.
