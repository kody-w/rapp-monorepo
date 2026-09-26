---
repo: kody-w/rapp-hive-public
family: hive
line: Hive
wave: 1
status: certified
verdict: CLEAN
evidence_commit: eafa6de7e04a3d536c21976c1d85e845a499cd7b
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 41
header: present
channel: newest
lifecycle: active
links_to:
  - hive-hub
  - RAPP
  - rapp-1
  - rapp-model-hive
  - rapp-work
  - RAR
---

# rapp-hive-public: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hive-public.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-hive-public` at `eafa6de7e0`](https://github.com/kody-w/rapp-hive-public/tree/eafa6de7e04a3d536c21976c1d85e845a499cd7b) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a57abfdd32e977223ed69718ed69672e1a9be7f5ef32e8966979453885e80253`.
- "experimental" mentions: 41 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.

On the map: the **Hive** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 6 portfolio repo(s): [hive-hub](hive-hub.md) (markdown), [RAPP](RAPP.md) (markdown), [rapp-1](rapp-1.md) (markdown), [rapp-model-hive](rapp-model-hive.md) (markdown), [rapp-work](rapp-work.md) (markdown), [RAR](RAR.md) (markdown).
Linked from 1: [rapp-model-hive](rapp-model-hive.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-hive-public` at `eafa6de7e0` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-hive-public --json` from the folder that holds both.
