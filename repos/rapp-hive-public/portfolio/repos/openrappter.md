---
repo: kody-w/openrappter
family: openrappter
line: OpenRappter
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 07c9af387b4521d5ccf8e34522d39a3334c9ee53
checked: 2026-10-08
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: pr-open
header_pr: https://github.com/kody-w/openrappter/pull/470
version: "v1.13.1-bar"
version_source: release
channel: newest
lifecycle: active
member_card: present
---

# openrappter: certified

![RAPP/1: certified, version v1.13.1-bar](https://kody-w.github.io/rapp-hive-public/portfolio/badges/openrappter.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** `v1.13.1-bar`, from the tag of its latest GitHub release. **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/openrappter` at `07c9af387b`](https://github.com/kody-w/openrappter/tree/07c9af387b4521d5ccf8e34522d39a3334c9ee53) on `main`, checked 2026-10-08.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `82c06915a0e51916f422eff0c315ab085a1b24cd0dc1e98d8686bf4b33bad2ee`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: PR open (https://github.com/kody-w/openrappter/pull/470).
- Member card: [`.rapp/member.md`](https://github.com/kody-w/openrappter/blob/07c9af387b4521d5ccf8e34522d39a3334c9ee53/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/openrappter.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/openrappter.md).

On the map: the **OpenRappter** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 16: [openrappter-alpha](openrappter-alpha.md), [openrappter-release-train](openrappter-release-train.md), [RAPP-Bible](RAPP-Bible.md), [rapp-docs](rapp-docs.md), [rapp-messaging](rapp-messaging.md), [rapp-monorepo](rapp-monorepo.md), [rapp-sentinel](rapp-sentinel.md), [rapp-spine](rapp-spine.md), [rapp-stack-cubby](rapp-stack-cubby.md), [rappter-cli](rappter-cli.md), [rappter-plays-palworld](rappter-plays-palworld.md), [rappter-plays-pokemon](rappter-plays-pokemon.md), [rappter-vui](rappter-vui.md), [rappterbook](rappterbook.md), [rappterbook-agent](rappterbook-agent.md), [rappterhub](rappterhub.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/openrappter` at `07c9af387b` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py openrappter --json` from the folder that holds both.
