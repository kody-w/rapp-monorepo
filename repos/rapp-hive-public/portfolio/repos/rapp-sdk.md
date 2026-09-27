---
repo: kody-w/rapp-sdk
family: tools
line: Tools & Apps
wave: 2
status: certified
verdict: CLEAN
evidence_commit: ede0fd4553b72b581c158a1bedaeada4d1ec04ea
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 27
header: present
header_pr: https://github.com/kody-w/rapp-sdk/pull/4
version: "v0.2.0"
version_source: release
channel: newest
lifecycle: active
member_card: present
links_to:
  - rapp-flight-deck
  - rapp-installer
  - rapp-projects
  - rapp-rings
  - rapp-twin
---

# rapp-sdk: certified

![RAPP/1: certified, version v0.2.0](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-sdk.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v0.2.0`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rapp-sdk` at `ede0fd4553`](https://github.com/kody-w/rapp-sdk/tree/ede0fd4553b72b581c158a1bedaeada4d1ec04ea) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `a392c7cad5a5fe809721e59ea91c19f9d42126a410efe172efb248c3c0d50e7c`.
- "experimental" mentions: 27 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/rapp-sdk/blob/ede0fd4553b72b581c158a1bedaeada4d1ec04ea/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/rapp-sdk.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/rapp-sdk.md).

On the map: the **Tools & Apps** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 5 portfolio repo(s): [rapp-flight-deck](rapp-flight-deck.md) (markdown), [rapp-installer](rapp-installer.md) (markdown), [rapp-projects](rapp-projects.md) (markdown), [rapp-rings](rapp-rings.md) (markdown), [rapp-twin](rapp-twin.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rapp-omarchy](rapp-omarchy.md), [rapp-projects](rapp-projects.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rapp-sdk` at `ede0fd4553` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rapp-sdk --json` from the folder that holds both.
