---
repo: kody-w/ShadowRAPP
family: rappterverse
line: Rappterverse
wave: 2
status: certified
verdict: CLEAN
evidence_commit: f32669853b355a4319313a3aefa0a4e8d77eb674
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: merged
header_pr: https://github.com/kody-w/ShadowRAPP/pull/2
channel: newest
lifecycle: active
member_card: present
---

# ShadowRAPP: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/ShadowRAPP.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/ShadowRAPP` at `f32669853b`](https://github.com/kody-w/ShadowRAPP/tree/f32669853b355a4319313a3aefa0a4e8d77eb674) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `1cfee39bf5cab6c71b0176d1f6103f291db0b1df49ee3969c8dc718da3c820dd`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: merged, awaiting the next sweep (https://github.com/kody-w/ShadowRAPP/pull/2).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/ShadowRAPP/blob/f32669853b355a4319313a3aefa0a4e8d77eb674/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/ShadowRAPP.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/ShadowRAPP.md).

On the map: the **Rappterverse** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/ShadowRAPP` at `f32669853b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py ShadowRAPP --json` from the folder that holds both.
