# Brainstem Bootcamp

**Build the agent on your laptop. Then ship it to Copilot Studio.**

→ **[kody-w.github.io/brainstem-bootcamp](https://kody-w.github.io/brainstem-bootcamp/)**

---

## The pitch in one paragraph

The Microsoft AI platform can answer questions (Copilot) and it can publish agents
(Copilot Studio). What it doesn't hand you is the place in between — a runtime *you*
own, on the machine in front of you, where an agent is actually built, given memory,
and proven before anyone else depends on it. **Brainstem is that on-device launchpad.**
You reach it through developer tooling you already sign into with GitHub. The bootcamp
takes a clean laptop to a published agent in about two hours, and the landing is
Copilot Studio.

## Why this repo exists

This is the marketing asset *and* the syllabus for the next cohort. Everything is public:

| File | What it is |
|------|-----------|
| [`index.html`](index.html) | The landing page — positioning, the six pillars, the comparison table, the hand-off story, CTA |
| [`MARKETING.md`](MARKETING.md) | The actual go-to-market plan: ICP, message ladder, channels, 3-week launch sequence, metrics |
| [`CURRICULUM.md`](CURRICULUM.md) | Four sessions, minute by minute, with the outcome each one has to produce |

## The six reasons (short version)

1. **Determinism, not persuasion** — custom instructions *ask* a model to behave; code in the loop *makes* it behave.
2. **Your data has an address** — state is at `~/.brainstem`. Point at it, back it up, delete it.
3. **Nobody can turn it off** — your loop changes when you change it, not on a preview schedule.
4. **Memory that doesn't expire** — JSON on disk, no rolling window, works with no repo at all.
5. **Same file, three tiers** — laptop → Azure Functions → Teams with no rewrite. That's where most AI projects die.
6. **Same engine, no new keys** — the GitHub Copilot CLI is the preferred backend, so there's nothing new to provision.

Full comparison against prompt files, assistant memory features, and cloud agent
frameworks is on [the page](https://kody-w.github.io/brainstem-bootcamp/#compare).

## Try it before you commit to anything

The 14-step walkthrough runs entirely in a browser — no server, no Python, no install:

**[kody-w.github.io/rapp-brainstem-walkthrough](https://kody-w.github.io/rapp-brainstem-walkthrough/)**

When you're ready for the real thing:

```bash
gh auth login
curl -fsSL https://kody-w.github.io/rapp-installer/install.sh | bash
```

## Join a cohort

[Open a signup issue](https://github.com/kody-w/brainstem-bootcamp/issues/new?template=cohort-signup.yml).
Free. Bring a laptop. Private team cohorts available — say so in the issue.

## Ecosystem

[Brainstem](https://github.com/kody-w/rapp-brainstem) ·
[Installer](https://github.com/kody-w/rapp-installer) ·
[Agent Registry](https://kody-w.github.io/RAR/) ·
[Registry metrics](https://kody-w.github.io/RAR/metrics.html) ·
[Walkthrough](https://kody-w.github.io/rapp-brainstem-walkthrough/)

---

MIT licensed. Independent open-source project, not affiliated with or endorsed by
Microsoft Corporation or GitHub, Inc. Microsoft, Microsoft 365, Copilot, Copilot Studio,
Azure and Teams are trademarks of Microsoft Corporation; GitHub and GitHub Copilot are
trademarks of GitHub, Inc. Named only to describe interoperability. Your access to any
Microsoft or GitHub service is governed solely by your agreement with that vendor.
RAPP and the RAPP family of names are trademarks of the RAPP project.
