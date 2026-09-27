---
repo: kody-w/double-jump
family: worlds
line: Worlds & Play
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5b1846eb169b1cf91109ed0e9f7c3b0237d492fd
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 17
header: present
header_pr: https://github.com/kody-w/double-jump/pull/2
version: "0.1.0"
version_source: VERSION
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-commons
  - rapp-hologram
  - rapp-moment
---

# double-jump: certified

![RAPP/1: certified, version 0.1.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/double-jump.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.1.0`, from its root VERSION file at the evidence commit. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/double-jump` at `5b1846eb16`](https://github.com/kody-w/double-jump/tree/5b1846eb169b1cf91109ed0e9f7c3b0237d492fd) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `765692c1e8d48907c4f5c9bfc0afc3573f64e8176d995cf6e6c208affb06d396`.
- "experimental" mentions: 17 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/double-jump/blob/5b1846eb169b1cf91109ed0e9f7c3b0237d492fd/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/double-jump.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/double-jump.md).

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 3 portfolio repo(s): [rapp-commons](rapp-commons.md) (markdown), [rapp-hologram](rapp-hologram.md) (markdown), [rapp-moment](rapp-moment.md) (markdown).
Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/double-jump` at `5b1846eb16` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py double-jump --json` from the folder that holds both.
