---
repo: kody-w/AI-Agent-Templates-Pilot
family: agents-rar
line: Agents (RAR)
wave: 2
status: certified
verdict: CLEAN
evidence_commit: 5bb20e2f46765294cda795688e0800ef56aa177f
checked: 2026-09-26
checker: kody-w/rapp-1 rapp_check.py at 591e014
experimental_mentions: 0
header: missing
channel: newest
lifecycle: active
---

# AI-Agent-Templates-Pilot: certified

![RAPP/1: certified](https://kody-w.github.io/rapp-hive-public/portfolio/badges/AI-Agent-Templates-Pilot.svg)

**Certified:** rapp-1's own checker gave **CLEAN** (no RAPP artifacts, found by a complete bounded scan) at the evidence commit.

**Version:** none recorded (no root VERSION file and no GitHub release). **Channel:** `newest`: it has no long-term-support pin, so its newest commit is the one in use.

- Evidence: [`kody-w/AI-Agent-Templates-Pilot` at `5bb20e2f46`](https://github.com/kody-w/AI-Agent-Templates-Pilot/tree/5bb20e2f46765294cda795688e0800ef56aa177f) on `main`, checked 2026-09-26.
- Checker: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py), verdict **CLEAN**. The raw output stays in the maintainer's sweep folder, outside the Hive; its SHA-256 is `9606736d4919d1ffdc5fb4d596e79ce4b97155755a5837151b92c2f38a9e6a70`.
- "experimental" mentions: 0 (whole word, any case, in tracked text files at the evidence commit, leaving out the network's own files: the repo's card `.rapp/member.md` and, in the network's public copy, `portfolio/`, `members/`, `notices/` and `PUBLISHED.md`; tracked, not a gate).
- Network header: not yet added.

On the map: the **Agents (RAR)** line ([subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)).

## Links

Linked from 1: [rapp-monorepo](rapp-monorepo.md).

Counted from markdown links to `github.com/kody-w/<repo>` or `kody-w.github.io/<repo>`, pin files, workflow `uses:` and `repository:` lines, and submodules, at the evidence commit; only public repos in this portfolio count.

## Check it yourself

Clone `kody-w/AI-Agent-Templates-Pilot` at `5bb20e2f46` and `kody-w/rapp-1` at `591e014`, then run `python3 -B rapp-1/rapp_check.py AI-Agent-Templates-Pilot --json` from the folder that holds both.
