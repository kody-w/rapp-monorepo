---
repo: kody-w/rapp-chatgpt
family: projects
line: RAPP Projects
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 8bef36de47220145a28fec5e72f2382a13773f6b
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.2.0"
version_source: release
channel: newest
lifecycle: active
links_to:
  - RAR
---

# rapp-chatgpt: certified

![RAPP/1: certified, version v1.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-chatgpt.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-chatgpt` at `8bef36de47`](https://github.com/kody-w/rapp-chatgpt/tree/8bef36de47220145a28fec5e72f2382a13773f6b) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `4fb3b8f7b43ee9aaa1f4bedf9927037e1dc34d0b0d56515f09e67133f9a2b587`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **RAPP Projects** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [RAR](RAR.md) (markdown).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-chatgpt` at `8bef36de47` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-chatgpt --json` from the folder that holds both.
