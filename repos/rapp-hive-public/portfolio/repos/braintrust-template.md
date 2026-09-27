---
repo: kody-w/braintrust-template
family: organism
line: Organism & Platform
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 83c9ab2accb34340838face8aa1d052526ec373e
checked: 2026-09-27
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 1
header: present
header_pr: https://github.com/kody-w/braintrust-template/pull/8
channel: newest
lifecycle: active
member_card: present
links_to:
  - RAPP
  - RAPPcards
---

# braintrust-template: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/braintrust-template.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/braintrust-template` at `83c9ab2acc`](https://github.com/kody-w/braintrust-template/tree/83c9ab2accb34340838face8aa1d052526ec373e) on `main`, checked 2026-09-27.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `f87e47b8a4f3bd83ac0df317d4748c296a1ac9da553940937cec103e6d4b1116`.
- "experimental" mentions: 1 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: present in `README.md`.
- Member card: [`.rapp/member.md`](https://github.com/kody-w/braintrust-template/blob/83c9ab2accb34340838face8aa1d052526ec373e/.rapp/member.md) at the evidence commit: this repo's card in the RAPP Hive, beside its pointer [`members/braintrust-template.md`](https://github.com/kody-w/rapp-hive-public/blob/main/members/braintrust-template.md).

On the map: the **Organism & Platform** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 2 portfolio repo(s): [RAPP](RAPP.md) (markdown), [RAPPcards](RAPPcards.md) (markdown).
Linked from 2: [RAPP](RAPP.md), [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/braintrust-template` at `83c9ab2acc` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py braintrust-template --json` from the folder that holds both.
