---
repo: kody-w/rappid
family: worlds
line: Worlds & Play
wave: 2
status: not yet
verdict: DRIFT
evidence_commit: c988d7975dadb6a8f055183cdbc4cbb17adfe2ae
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
links_to:
  - rapp-brainstem-frontier-template
---

# rappid: not yet

![RAPP/1: not yet](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rappid.svg)

**Not yet:** 1 finding(s) from rapp_check: §9 egg.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/rappid` at `c988d7975d`](https://github.com/kody-w/rappid/tree/c988d7975dadb6a8f055183cdbc4cbb17adfe2ae) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **DRIFT**, 1 finding(s). The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `e2ae619cadef3c1ffc85160edb37365688be8b91c8c47a3a8646f6695bc47412`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

## Findings (1)

- `rappter-6be4a324.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: Expecting value: line 1 column 1 (char 0))

On the map: the **Worlds & Play** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Links to 1 portfolio repo(s): [rapp-brainstem-frontier-template](rapp-brainstem-frontier-template.md) (markdown).
Linked from 3: [rapp-monorepo](rapp-monorepo.md), [rappidverse-field](rappidverse-field.md), [rappvision-rappid-zoo](rappvision-rappid-zoo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/rappid` at `c988d7975d` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py rappid --json` from the folder that holds both.
