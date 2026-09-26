---
repo: kody-w/rapp-roadside
family: estate
line: Estate & Ops
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: 8082439a103572faf2d46fde204baa8eb4bb76de
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
version: "v1.0.0"
version_source: release
channel: newest
lifecycle: active
---

# rapp-roadside: not yet

![RAPP/1: not yet, version v1.0.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-roadside.svg)

**Not yet:** 1 finding(s) from rapp_check: §7.6 duplicate position.

**Version:** `v1.0.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-roadside` at `8082439a10`](https://github.com/kody-w/rapp-roadside/tree/8082439a103572faf2d46fde204baa8eb4bb76de) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `5b1932680a92ba249df95e59fea1177592792df542d0257fb6a7e0804c6ab393`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `rev-13-frame.json, roadside-frame.json` · §7.6 duplicate position · stream rappid:@kody-w/rar-installer-troubleshooter:296872e9cd739d0549707b5c22abfd3654c3667652ea55dedaa5621b9e5f733b has 2 frames at seq 0

On the map: the **Estate & Ops** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 2: [rapp-monorepo](rapp-monorepo.md), [RAR](RAR.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-roadside` at `8082439a10` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-roadside --json` from the folder that holds both.
