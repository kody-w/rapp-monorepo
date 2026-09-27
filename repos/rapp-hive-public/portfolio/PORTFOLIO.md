# RAPP/1 portfolio

Every public RAPP repo, each with an **earned** RAPP/1 status. RAPP/1 is the LTS version for the whole network: a repo is certified when rapp-1's own checker passes it at a recorded commit.

**Notices:** 317 active, 0 deprecated, 0 superseded, 0 archived, 0 left the network. The [notices page](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) lists every repo that is not active or has left, and what changed in this version; [how to deprecate, move or version a repo](https://kody-w.github.io/rapp-hive-public/portfolio/lifecycle.html).

| Wave | certified | not yet | unchecked | total |
|---|---|---|---|---|
| 1: the RAPP/1 stack | 14 | 1 | 0 | 15 |
| 2: the rest of the RAPP family | 279 | 22 | 1 | 302 |
| **all** | 293 | 23 | 1 | 317 |

- **certified**: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py) says COMPLIANT or CLEAN at the recorded commit.
- **not yet**: drift or unverified; each file says why.
- **unchecked**: it could not be cloned or checked (for example, an empty repository); its file says why.
- **rapp1-lts**: the repo has a long-term-support pin (the network's built-in known pins, until the estate publishes its LTS pins; the Version column shows `LTS` and its label); **newest**: no pin, so its newest commit is the one in use. Open questions about a repo's channel are on the [channel notices](https://kody-w.github.io/rapp-hive-public/portfolio/channel-notices.html) page; they change no channel. **deprecated**, **superseded** and **archived** come first in the Status column; each repo's file says since when and why.

Each repo's README gets one marked line (today, of 317: 197 carry it, 14 in an open pull request, 56 merged, awaiting the next sweep, 2 held, 45 waiting for their pull request (wave 2 waits for the owner's approval), 2 without a README (skipped), 1 not checked (they could not be cloned)): its badge (served from this folder by GitHub Pages, so the URL never changes) and a link to [Start here](https://github.com/kody-w/rapp-installer#start-here) for anyone without a Brainstem yet. "experimental" mentions are tracked here as a metric; they are not a gate yet.

**Member cards:** 252 of 317 repos carry their card in the RAPP Hive (`.rapp/member.md`, the repo's own side of its pointer in `members/`); the file of each repo that has one links it.

A Hive holds only markdown, so each badge is `badges/<repo>.svg.md`: its front matter tells GitHub Pages to serve it as `https://kody-w.github.io/rapp-hive-public/portfolio/badges/<repo>.svg` (image/svg+xml).

## The map

**[Subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)** (zoomable; click a station for its portfolio file and its repo) · [poster PDF](https://kody-w.github.io/rapp-hive-public/portfolio/subway.pdf) · [SVG](https://kody-w.github.io/rapp-hive-public/portfolio/subway.svg)

Lines are the families below; stations are repos, filled by status (hollow when deprecated, superseded or archived); the RAPP/1 Core line runs in layer order and ends at `rapp-installer`, the Start here terminal. It is drawn from these files by the `rapp1_network` package (its release copy is in [`tools/`](https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/tools)), and the links between repos come from each file's `links_to`.

**Version 9**, crawled 2026-09-27 01:06 UTC. Every crawl is one RAPP/1 frame, a `body.pulse` on the network's body stream `rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def`. The [timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html) lists every version with its pulse hashes and what changed, and each version's maps stay under `versions/`.

| Line | Stations | certified | not yet | unchecked |
|---|---|---|---|---|
| [RAPP/1 Core](lines/rapp1-core.md) | 7 | 7 | 0 | 0 |
| [Hive](lines/hive.md) | 9 | 8 | 1 | 0 |
| [Agents (RAR)](lines/agents-rar.md) | 22 | 18 | 4 | 0 |
| [Brainstem](lines/brainstem.md) | 19 | 17 | 1 | 1 |
| [Brainstem Connect](lines/connect.md) | 16 | 16 | 0 | 0 |
| [Learn & Docs](lines/learn.md) | 18 | 17 | 1 | 0 |
| [Release Channels](lines/release.md) | 19 | 19 | 0 | 0 |
| [OpenRappter](lines/openrappter.md) | 8 | 8 | 0 | 0 |
| [Rappterbook](lines/rappterbook.md) | 23 | 22 | 1 | 0 |
| [Rappterverse](lines/rappterverse.md) | 11 | 9 | 2 | 0 |
| [Rappvision](lines/rappvision.md) | 23 | 23 | 0 | 0 |
| [Twins](lines/twins.md) | 15 | 15 | 0 | 0 |
| [Neighborhoods](lines/neighborhoods.md) | 22 | 22 | 0 | 0 |
| [Organism & Platform](lines/organism.md) | 20 | 20 | 0 | 0 |
| [DOGG & Commons](lines/dogg.md) | 11 | 9 | 2 | 0 |
| [Tools & Apps](lines/tools.md) | 30 | 25 | 5 | 0 |
| [Estate & Ops](lines/estate.md) | 18 | 16 | 2 | 0 |
| [Worlds & Play](lines/worlds.md) | 26 | 22 | 4 | 0 |

## Wave 1: the RAPP/1 stack (15)

### RAPP/1 Core (7)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [lisppy](repos/lisppy.md) | certified |  | CLEAN | a5db2db | 2026-09-27 | 1 | present |
| [RAPP](repos/RAPP.md) | certified | v1.0.0 | COMPLIANT | 3a8020f | 2026-09-27 | 196 | present |
| [rapp-1](repos/rapp-1.md) | certified | LTS 591e014 | COMPLIANT | bae4e3c | 2026-09-27 | 0 | present |
| [rapp-drift-lint](repos/rapp-drift-lint.md) | certified |  | CLEAN | 92a97a1 | 2026-09-27 | 0 | present |
| [rapp-installer](repos/rapp-installer.md) | certified | v1.0.0 · LTS brainstem-v0.6.9 | CLEAN | 0e43ee5 | 2026-09-27 | 11 | held: the owner holds the grail repo (PR #48 stays open) |
| [rapp-work](repos/rapp-work.md) | certified | LTS 29ead23 | COMPLIANT | 4d1a527 | 2026-09-27 | 0 | present |
| [rapp-workspace](repos/rapp-workspace.md) | certified |  | COMPLIANT | 52d4f19 | 2026-09-27 | 50 | held: waiting on G24 (front door editable) |

### Hive (7)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-hub](repos/hive-hub.md) | certified |  | CLEAN | 2fd4223 | 2026-09-27 | 5 | present |
| [hive-hub-join](repos/hive-hub-join.md) | certified |  | CLEAN | 7ae4e25 | 2026-09-27 | 0 | present |
| [hive-hub-mcp](repos/hive-hub-mcp.md) | certified |  | CLEAN | 312eedc | 2026-09-27 | 0 | present |
| [rapp-hive-hub](repos/rapp-hive-hub.md) | certified |  | COMPLIANT | 1c15452 | 2026-09-27 | 7 | present |
| [rapp-hive-hub-join](repos/rapp-hive-hub-join.md) | certified |  | CLEAN | 3598da1 | 2026-09-27 | 0 | present |
| [rapp-hive-public](repos/rapp-hive-public.md) | certified |  | CLEAN | 6c301cd | 2026-09-27 | 41 | present |
| [rapp-model-hive](repos/rapp-model-hive.md) | not yet |  | DRIFT | c88331a | 2026-09-27 | 18 | present |

### Agents (RAR) (1)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [RAR](repos/RAR.md) | certified | v1.0.0 | COMPLIANT | bc2bbd6 | 2026-09-27 | 160 | present |

## Wave 2: the rest of the RAPP family (302)

### Hive (2)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-showcase](repos/hive-showcase.md) | certified |  | CLEAN | 331fb28 | 2026-09-27 | 7 | not yet added |
| [rapp-hive-app](repos/rapp-hive-app.md) | certified |  | CLEAN | 482b4e4 | 2026-09-27 | 0 | present |

### Agents (RAR) (21)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [AI-Agent-Templates-Pilot](repos/AI-Agent-Templates-Pilot.md) | certified |  | CLEAN | 5bb20e2 | 2026-09-27 | 0 | not yet added |
| [cowork-cookbook-rapp](repos/cowork-cookbook-rapp.md) | not yet | v1.0.0 | DRIFT | d309e37 | 2026-09-27 | 0 | present |
| [obsidian-binder](repos/obsidian-binder.md) | certified |  | CLEAN | 66a6254 | 2026-09-27 | 0 | present |
| [rapp-agents](repos/rapp-agents.md) | certified | v1.0.0 | CLEAN | 88cf98a | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-carts](repos/rapp-carts.md) | certified | v1.0.0 | CLEAN | 135d0a5 | 2026-09-27 | 0 | present |
| [rapp-claude-skills](repos/rapp-claude-skills.md) | certified | v1.0.0 | CLEAN | 4ec5b42 | 2026-09-27 | 0 | present |
| [rapp-egg-hub](repos/rapp-egg-hub.md) | not yet | v1.0.0 | DRIFT | 602f08e | 2026-09-27 | 11 | present |
| [rapp-hatchery](repos/rapp-hatchery.md) | certified |  | CLEAN | 1a7fd78 | 2026-09-27 | 4 | present |
| [rapp-leviathan-hub](repos/rapp-leviathan-hub.md) | not yet |  | DRIFT | 953419d | 2026-09-27 | 0 | present |
| [rapp-packs](repos/rapp-packs.md) | certified |  | CLEAN | 19cb75f | 2026-09-27 | 0 | not yet added |
| [rapp-sentinel-hub](repos/rapp-sentinel-hub.md) | certified |  | CLEAN | 64fb4d1 | 2026-09-27 | 0 | present |
| [rapp-skill](repos/rapp-skill.md) | certified |  | CLEAN | 5fc3ac5 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-skills](repos/rapp-skills.md) | certified |  | CLEAN | 9b58c9b | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-stack-cubby](repos/rapp-stack-cubby.md) | certified | v0.1.0rc11 | COMPLIANT | 1fee389 | 2026-09-27 | 13 | not yet added |
| [rapp-store-archive](repos/rapp-store-archive.md) | certified |  | CLEAN | a07796e | 2026-09-27 | 0 | present |
| [rapp-toaster](repos/rapp-toaster.md) | certified |  | CLEAN | 5abff70 | 2026-09-27 | 0 | present |
| [RAPP_Hub](repos/RAPP_Hub.md) | certified |  | CLEAN | 5426aea | 2026-09-27 | 0 | present |
| [RAPP_Sense_Store](repos/RAPP_Sense_Store.md) | certified |  | CLEAN | 563552f | 2026-09-27 | 0 | present |
| [RAPP_Store](repos/RAPP_Store.md) | not yet | v1.0.0 | DRIFT | f81d84c | 2026-09-27 | 76 | PR open |
| [RAPPcards](repos/RAPPcards.md) | certified |  | CLEAN | 045026a | 2026-09-27 | 2 | present |
| [red-binder](repos/red-binder.md) | certified |  | CLEAN | 6e34d1d | 2026-09-27 | 10 | present |

### Brainstem (19)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-agent](repos/brainstem-agent.md) | certified |  | CLEAN | a8801a2 | 2026-09-27 | 59 | not yet added |
| [brainstem-copilot](repos/brainstem-copilot.md) | certified |  | CLEAN | 57b8efe | 2026-09-27 | 4 | present |
| [brainstem-harness](repos/brainstem-harness.md) | certified |  | CLEAN | cc3a131 | 2026-09-27 | 0 | present |
| [chat](repos/chat.md) | certified |  | CLEAN | 5882892 | 2026-09-27 | 0 | present |
| [ez-rapp](repos/ez-rapp.md) | certified | v0.1.3 | CLEAN | cd3a32b | 2026-09-27 | 0 | present |
| [rapp-brainfreeze](repos/rapp-brainfreeze.md) | certified |  | CLEAN | 7423614 | 2026-09-27 | 2 | present |
| [rapp-brainfreeze-studio](repos/rapp-brainfreeze-studio.md) | certified |  | CLEAN | 36e57c6 | 2026-09-27 | 3 | present |
| [rapp-brainstem](repos/rapp-brainstem.md) | certified | v0.2.1 | COMPLIANT | 04b1152 | 2026-09-27 | 3 | merged, awaiting the next sweep |
| [rapp-brainstem-foundation](repos/rapp-brainstem-foundation.md) | unchecked |  |  |  | 2026-09-27 |  | none (not checked) |
| [rapp-brainstem-frontier-template](repos/rapp-brainstem-frontier-template.md) | certified |  | CLEAN | f3510d7 | 2026-09-27 | 0 | present |
| [rapp-brainstem-sdk](repos/rapp-brainstem-sdk.md) | certified | v1.0.0 | CLEAN | 8175627 | 2026-09-27 | 0 | present |
| [rapp-light](repos/rapp-light.md) | certified |  | CLEAN | 2d3501f | 2026-09-27 | 5 | present |
| [rapp-petri](repos/rapp-petri.md) | certified |  | CLEAN | 83eca7e | 2026-09-27 | 0 | present |
| [rapp-quests](repos/rapp-quests.md) | certified |  | CLEAN | 2abe9d5 | 2026-09-27 | 0 | present |
| [rapp-static-brainstem](repos/rapp-static-brainstem.md) | certified | v1.2.0 | CLEAN | 0173eb8 | 2026-09-27 | 0 | not yet added |
| [rapp-vscode-extension](repos/rapp-vscode-extension.md) | certified | v1.0.0 | CLEAN | 616046e | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [skillstem](repos/skillstem.md) | certified |  | CLEAN | 9e13b5a | 2026-09-27 | 0 | present |
| [stemcell](repos/stemcell.md) | certified |  | CLEAN | ac57403 | 2026-09-27 | 6 | present |
| [vbrainstem](repos/vbrainstem.md) | not yet |  | DRIFT | 8c3d1fa | 2026-09-27 | 2 | present |

### Brainstem Connect (16)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-brainstem-claude](repos/rapp-brainstem-claude.md) | certified |  | CLEAN | e3651db | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-claude-desktop](repos/rapp-brainstem-claude-desktop.md) | certified |  | CLEAN | bd07bdc | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-cline](repos/rapp-brainstem-cline.md) | certified |  | CLEAN | 6dca285 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-codex](repos/rapp-brainstem-codex.md) | certified |  | CLEAN | b1a9760 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-copilot](repos/rapp-brainstem-copilot.md) | certified |  | CLEAN | 3726803 | 2026-09-27 | 0 | present |
| [rapp-brainstem-cursor](repos/rapp-brainstem-cursor.md) | certified |  | CLEAN | c4ba3ef | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-gemini](repos/rapp-brainstem-gemini.md) | certified |  | CLEAN | f77ef9d | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-goose](repos/rapp-brainstem-goose.md) | certified |  | CLEAN | f938337 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-kiro](repos/rapp-brainstem-kiro.md) | certified |  | CLEAN | 63b0e88 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-mcp](repos/rapp-brainstem-mcp.md) | certified |  | CLEAN | c7cedcc | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-opencode](repos/rapp-brainstem-opencode.md) | certified |  | CLEAN | 9e6bc15 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-plugin](repos/rapp-brainstem-plugin.md) | certified |  | CLEAN | aa3793e | 2026-09-27 | 0 | not yet added |
| [rapp-brainstem-vscode](repos/rapp-brainstem-vscode.md) | certified |  | CLEAN | cbc13d3 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-brainstem-windsurf](repos/rapp-brainstem-windsurf.md) | certified |  | CLEAN | 0fac814 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-mcp](repos/rapp-mcp.md) | certified | LTS cd22b1e | CLEAN | cd22b1e | 2026-09-27 | 2 | present |
| [scout-brainstem-bootstrap](repos/scout-brainstem-bootstrap.md) | certified |  | CLEAN | 0c384d8 | 2026-09-27 | 48 | merged, awaiting the next sweep |

### Learn & Docs (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-bootcamp](repos/brainstem-bootcamp.md) | certified |  | CLEAN | 40061a1 | 2026-09-27 | 0 | present |
| [dimensional-bottles](repos/dimensional-bottles.md) | certified |  | COMPLIANT | 66d4681 | 2026-09-27 | 0 | present |
| [learn-brainstem](repos/learn-brainstem.md) | certified |  | CLEAN | 766606d | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [RAPP-Bible](repos/RAPP-Bible.md) | certified |  | CLEAN | 05b89af | 2026-09-27 | 17 | PR open |
| [rapp-brainstem-walkthrough](repos/rapp-brainstem-walkthrough.md) | certified | v0.6.16 | CLEAN | d310e4b | 2026-09-27 | 4 | present |
| [rapp-demos](repos/rapp-demos.md) | certified | v1.0.0 | CLEAN | cc9cfb1 | 2026-09-27 | 0 | present |
| [rapp-docs](repos/rapp-docs.md) | certified |  | CLEAN | 3042120 | 2026-09-27 | 3 | present |
| [rapp-education-shorts](repos/rapp-education-shorts.md) | certified |  | CLEAN | 18e055a | 2026-09-27 | 0 | present |
| [rapp-lab-kit](repos/rapp-lab-kit.md) | certified |  | CLEAN | 14ad3b3 | 2026-09-27 | 0 | present |
| [rapp-map](repos/rapp-map.md) | not yet | v1.0.0 · LTS 4c8ba6b | DRIFT | 48b6c38 | 2026-09-27 | 54 | present |
| [rapp-mapp](repos/rapp-mapp.md) | certified |  | CLEAN | ddbf312 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-mission](repos/rapp-mission.md) | certified |  | CLEAN | d00cc3b | 2026-09-27 | 0 | present |
| [rapp-roadmap](repos/rapp-roadmap.md) | certified |  | CLEAN | e160749 | 2026-09-27 | 1 | present |
| [rapp-specs](repos/rapp-specs.md) | certified |  | COMPLIANT | 2264920 | 2026-09-27 | 0 | present |
| [rapp-spine](repos/rapp-spine.md) | certified |  | CLEAN | 8d61da5 | 2026-09-27 | 0 | not yet added |
| [rapp-wiki-observatory](repos/rapp-wiki-observatory.md) | certified |  | CLEAN | c284d06 | 2026-09-27 | 0 | present |
| [rapp_docs](repos/rapp_docs.md) | certified |  | CLEAN | 86640cd | 2026-09-27 | 0 | present |
| [rappdex](repos/rappdex.md) | certified |  | CLEAN | 25ff78e | 2026-09-27 | 0 | present |

### Release Channels (19)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [openrappter-alpha](repos/openrappter-alpha.md) | certified |  | CLEAN | 235e93e | 2026-09-27 | 0 | not yet added |
| [openrappter-beta](repos/openrappter-beta.md) | certified |  | CLEAN | c29c6d4 | 2026-09-27 | 0 | not yet added |
| [openrappter-canary](repos/openrappter-canary.md) | certified |  | CLEAN | a86599c | 2026-09-27 | 0 | not yet added |
| [openrappter-nightly](repos/openrappter-nightly.md) | certified |  | CLEAN | ea34fa6 | 2026-09-27 | 0 | not yet added |
| [openrappter-release-train](repos/openrappter-release-train.md) | certified |  | CLEAN | eeb7803 | 2026-09-27 | 0 | present |
| [rapp-alpha](repos/rapp-alpha.md) | certified |  | CLEAN | 44be78a | 2026-09-27 | 12 | not yet added |
| [rapp-beta](repos/rapp-beta.md) | certified |  | CLEAN | 562b5e1 | 2026-09-27 | 12 | not yet added |
| [rapp-brainstem-beta](repos/rapp-brainstem-beta.md) | certified |  | CLEAN | cd55de1 | 2026-09-27 | 0 | present |
| [rapp-canary](repos/rapp-canary.md) | certified |  | COMPLIANT | 7ac5c77 | 2026-09-27 | 20 | not yet added |
| [rapp-flight](repos/rapp-flight.md) | certified |  | CLEAN | 18197ea | 2026-09-27 | 2 | present |
| [rapp-flight-deck](repos/rapp-flight-deck.md) | certified |  | CLEAN | ac6ff67 | 2026-09-27 | 1 | present |
| [rapp-installer-canary](repos/rapp-installer-canary.md) | certified |  | CLEAN | 8bb6b75 | 2026-09-27 | 7 | not yet added |
| [rapp-installer-dev](repos/rapp-installer-dev.md) | certified |  | CLEAN | df51a9d | 2026-09-27 | 8 | not yet added |
| [rapp-mirror-releases](repos/rapp-mirror-releases.md) | certified | v0.2.0 | CLEAN | 94d4cd5 | 2026-09-27 | 0 | present |
| [rapp-nightly](repos/rapp-nightly.md) | certified |  | CLEAN | 27d6261 | 2026-09-27 | 12 | not yet added |
| [rapp-release-train](repos/rapp-release-train.md) | certified |  | CLEAN | 5f37baa | 2026-09-27 | 6 | not yet added |
| [rapp-rings](repos/rapp-rings.md) | certified |  | CLEAN | 4750f73 | 2026-09-27 | 1 | present |
| [rapp-shape-aibast](repos/rapp-shape-aibast.md) | certified |  | CLEAN | e8a66b0 | 2026-09-27 | 21 | not yet added |
| [rapp-train](repos/rapp-train.md) | certified |  | CLEAN | 1726ca5 | 2026-09-27 | 0 | present |

### OpenRappter (8)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [homebrew-tap](repos/homebrew-tap.md) | certified |  | CLEAN | 9c132ab | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [openrappter](repos/openrappter.md) | certified | v1.13.1-bar | CLEAN | d8601aa | 2026-09-27 | 1 | PR open |
| [rappter-cli](repos/rappter-cli.md) | certified |  | CLEAN | 3c5bb44 | 2026-09-27 | 0 | present |
| [rappter-plays-palworld](repos/rappter-plays-palworld.md) | certified |  | CLEAN | d07fa96 | 2026-09-27 | 0 | present |
| [rappter-plays-pokemon](repos/rappter-plays-pokemon.md) | certified |  | CLEAN | 8cf4799 | 2026-09-27 | 4 | merged, awaiting the next sweep |
| [rappter-prompts](repos/rappter-prompts.md) | certified |  | CLEAN | 3fc33ef | 2026-09-27 | 0 | present |
| [rappter-vui](repos/rappter-vui.md) | certified |  | CLEAN | b96b8a2 | 2026-09-27 | 0 | present |
| [rappterhub](repos/rappterhub.md) | certified |  | CLEAN | 2386561 | 2026-09-27 | 0 | present |

### Rappterbook (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [mars-barn](repos/mars-barn.md) | certified |  | CLEAN | 2203505 | 2026-09-27 | 14 | PR open |
| [rappbook-admin](repos/rappbook-admin.md) | certified |  | CLEAN | 13fe250 | 2026-09-27 | 0 | present |
| [rappterbook](repos/rappterbook.md) | not yet | v1.0.0 | DRIFT | c1df360 | 2026-09-27 | 4167 | merged, awaiting the next sweep |
| [rappterbook-agent](repos/rappterbook-agent.md) | certified |  | CLEAN | 832de42 | 2026-09-27 | 2 | merged, awaiting the next sweep |
| [rappterbook-agent-dna](repos/rappterbook-agent-dna.md) | certified |  | CLEAN | 16a5ddb | 2026-09-27 | 0 | present |
| [rappterbook-agent-exchange](repos/rappterbook-agent-exchange.md) | certified |  | CLEAN | 8559ceb | 2026-09-27 | 4 | merged, awaiting the next sweep |
| [rappterbook-api](repos/rappterbook-api.md) | certified |  | CLEAN | 8c50370 | 2026-09-27 | 1 | present |
| [rappterbook-autopilot](repos/rappterbook-autopilot.md) | certified |  | CLEAN | fac2ad1 | 2026-09-27 | 0 | present |
| [rappterbook-commons](repos/rappterbook-commons.md) | certified |  | CLEAN | 2aba29e | 2026-09-27 | 0 | present |
| [rappterbook-engine-test](repos/rappterbook-engine-test.md) | certified |  | CLEAN | f462665 | 2026-09-27 | 230 | merged, awaiting the next sweep |
| [rappterbook-first-bond](repos/rappterbook-first-bond.md) | certified |  | CLEAN | 332e7a0 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterbook-governance](repos/rappterbook-governance.md) | certified |  | CLEAN | 1cb2f03 | 2026-09-27 | 0 | present |
| [rappterbook-impossible-product](repos/rappterbook-impossible-product.md) | certified | frame-03.2 | CLEAN | afabf42 | 2026-09-27 | 0 | present |
| [rappterbook-join](repos/rappterbook-join.md) | certified |  | CLEAN | 0657c32 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterbook-knowledge-graph](repos/rappterbook-knowledge-graph.md) | certified |  | CLEAN | 337ef55 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterbook-market-maker](repos/rappterbook-market-maker.md) | certified |  | CLEAN | a2f3a5d | 2026-09-27 | 0 | present |
| [rappterbook-mars-barn](repos/rappterbook-mars-barn.md) | certified |  | CLEAN | f654201 | 2026-09-27 | 13 | present |
| [rappterbook-phantom](repos/rappterbook-phantom.md) | certified |  | CLEAN | e176f45 | 2026-09-27 | 0 | present |
| [rappterbook-seedmaker](repos/rappterbook-seedmaker.md) | certified |  | CLEAN | 68bc493 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterbook-social-graph](repos/rappterbook-social-graph.md) | certified |  | CLEAN | 77b8b1e | 2026-09-27 | 0 | present |
| [rappterbook-v2](repos/rappterbook-v2.md) | certified |  | CLEAN | 37087c5 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterbook-v2-state](repos/rappterbook-v2-state.md) | certified |  | CLEAN | 5e1b4e2 | 2026-09-27 | 32 | present |
| [rappterbook-vm](repos/rappterbook-vm.md) | certified |  | CLEAN | 302c899 | 2026-09-27 | 4 | present |

### Rappterverse (11)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [CrystalRAPP](repos/CrystalRAPP.md) | certified |  | CLEAN | e2747c0 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [rappter-distro](repos/rappter-distro.md) | not yet |  | DRIFT | c34b057 | 2026-09-27 | 29 | present |
| [rappter-factory](repos/rappter-factory.md) | certified |  | CLEAN | 88712b0 | 2026-09-27 | 2 | present |
| [rappter-mmo](repos/rappter-mmo.md) | certified |  | CLEAN | 5d45256 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappter-site](repos/rappter-site.md) | not yet |  | DRIFT | c0b7950 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [rappterbox](repos/rappterbox.md) | certified | v0.12.2 | COMPLIANT | 734c69d | 2026-09-27 | 24 | merged, awaiting the next sweep |
| [RappterNest](repos/RappterNest.md) | certified |  | CLEAN | 8da2b07 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rappterverse](repos/rappterverse.md) | certified |  | CLEAN | c531a64 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [rappterverse-data](repos/rappterverse-data.md) | certified |  | CLEAN | cff8bb0 | 2026-09-27 | 0 | PR open |
| [ShadowRAPP](repos/ShadowRAPP.md) | certified |  | CLEAN | f326698 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [VoidRAPP](repos/VoidRAPP.md) | certified |  | CLEAN | 9634ccd | 2026-09-27 | 0 | merged, awaiting the next sweep |

### Rappvision (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-remix](repos/rapp-remix.md) | certified |  | CLEAN | 714b891 | 2026-09-27 | 0 | present |
| [rapp-video](repos/rapp-video.md) | certified |  | CLEAN | 2984dcb | 2026-09-27 | 6 | present |
| [rapp-vision](repos/rapp-vision.md) | certified | oil-field-season-v1.0.0 | CLEAN | c988c19 | 2026-09-27 | 0 | PR open |
| [rappvision-after-midnight-maps](repos/rappvision-after-midnight-maps.md) | certified |  | CLEAN | 43dd543 | 2026-09-27 | 0 | not yet added |
| [rappvision-brainstem-notes](repos/rappvision-brainstem-notes.md) | certified |  | CLEAN | 70a1b6f | 2026-09-27 | 0 | not yet added |
| [rappvision-creature-office-hours](repos/rappvision-creature-office-hours.md) | certified |  | CLEAN | be8a56f | 2026-09-27 | 0 | not yet added |
| [rappvision-field-notes](repos/rappvision-field-notes.md) | certified |  | CLEAN | d8866b3 | 2026-09-27 | 0 | present |
| [rappvision-kitchen-table-physics](repos/rappvision-kitchen-table-physics.md) | certified |  | CLEAN | a2133bd | 2026-09-27 | 0 | not yet added |
| [rappvision-new-way-of-work](repos/rappvision-new-way-of-work.md) | certified |  | CLEAN | 36aa36a | 2026-09-27 | 0 | no README (skipped) |
| [rappvision-null-arcade](repos/rappvision-null-arcade.md) | certified |  | CLEAN | 9211c75 | 2026-09-27 | 0 | not yet added |
| [rappvision-one-minute-orchestra](repos/rappvision-one-minute-orchestra.md) | certified |  | CLEAN | e376927 | 2026-09-27 | 1 | not yet added |
| [rappvision-patch-notes-tomorrow](repos/rappvision-patch-notes-tomorrow.md) | certified |  | CLEAN | aa4403d | 2026-09-27 | 0 | not yet added |
| [rappvision-pigeon-post](repos/rappvision-pigeon-post.md) | certified |  | CLEAN | 836983f | 2026-09-27 | 10 | not yet added |
| [rappvision-pokemon](repos/rappvision-pokemon.md) | certified |  | CLEAN | 3c693cf | 2026-09-27 | 0 | not yet added |
| [rappvision-prompt-frontier](repos/rappvision-prompt-frontier.md) | certified |  | CLEAN | 601794c | 2026-09-27 | 0 | present |
| [rappvision-protocol-minute](repos/rappvision-protocol-minute.md) | certified |  | CLEAN | 0a72c43 | 2026-09-27 | 0 | not yet added |
| [rappvision-rappid-zoo](repos/rappvision-rappid-zoo.md) | certified |  | CLEAN | 0bc219c | 2026-09-27 | 0 | present |
| [rappvision-rappterbox](repos/rappvision-rappterbox.md) | certified |  | CLEAN | 6af62eb | 2026-09-27 | 0 | not yet added |
| [rappvision-receipt-culture](repos/rappvision-receipt-culture.md) | certified |  | CLEAN | cd22ff3 | 2026-09-27 | 0 | not yet added |
| [rappvision-repair-manual](repos/rappvision-repair-manual.md) | certified |  | CLEAN | 8bdced4 | 2026-09-27 | 0 | not yet added |
| [rappvision-rnr](repos/rappvision-rnr.md) | certified |  | CLEAN | 77a8064 | 2026-09-27 | 0 | present |
| [rappvision-signal-garden](repos/rappvision-signal-garden.md) | certified |  | CLEAN | 831bd38 | 2026-09-27 | 0 | not yet added |
| [rappvision-tiny-bureau](repos/rappvision-tiny-bureau.md) | certified |  | CLEAN | f3296c1 | 2026-09-27 | 0 | not yet added |

### Twins (15)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [echo-brainstem](repos/echo-brainstem.md) | certified |  | COMPLIANT | d90f6fd | 2026-09-27 | 2 | present |
| [lumen-brainstem](repos/lumen-brainstem.md) | certified |  | COMPLIANT | b0a5270 | 2026-09-27 | 2 | present |
| [rapp-kite](repos/rapp-kite.md) | certified | v1.0.0 | CLEAN | 6c1c056 | 2026-09-27 | 0 | present |
| [rapp-kited-twin](repos/rapp-kited-twin.md) | certified | v1.0.0 | CLEAN | 7db7cc9 | 2026-09-27 | 0 | present |
| [rapp-overwatch](repos/rapp-overwatch.md) | certified |  | CLEAN | 868a5da | 2026-09-27 | 0 | present |
| [rapp-ratchet](repos/rapp-ratchet.md) | certified |  | CLEAN | 5e64dea | 2026-09-27 | 0 | present |
| [rapp-twin](repos/rapp-twin.md) | certified |  | CLEAN | 83cd87e | 2026-09-27 | 1 | present |
| [rapp-twin-hub](repos/rapp-twin-hub.md) | certified |  | CLEAN | 3b7bc76 | 2026-09-27 | 0 | present |
| [rapp-twin-in-residence](repos/rapp-twin-in-residence.md) | certified |  | CLEAN | 32345d7 | 2026-09-27 | 1 | present |
| [rapp-zoo](repos/rapp-zoo.md) | certified | v1.2.0 | COMPLIANT | 7a0eeb9 | 2026-09-27 | 3 | not yet added |
| [sim-demo-twin](repos/sim-demo-twin.md) | certified |  | COMPLIANT | 4079ce1 | 2026-09-27 | 1 | present |
| [tide-brainstem](repos/tide-brainstem.md) | certified |  | COMPLIANT | 048413b | 2026-09-27 | 2 | present |
| [twin-binder](repos/twin-binder.md) | certified |  | CLEAN | 9176dbe | 2026-09-27 | 0 | present |
| [twin-egg-hatcher](repos/twin-egg-hatcher.md) | certified |  | CLEAN | b30821a | 2026-09-27 | 0 | present |
| [wildhaven-ai-homes-twin](repos/wildhaven-ai-homes-twin.md) | certified |  | COMPLIANT | 507b206 | 2026-09-27 | 24 | merged, awaiting the next sweep |

### Neighborhoods (22)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [heimdall](repos/heimdall.md) | certified |  | COMPLIANT | 4faa05f | 2026-09-27 | 2 | present |
| [microsoft-se-team-neighborhood](repos/microsoft-se-team-neighborhood.md) | certified | v1.0.0 | COMPLIANT | 260dbfa | 2026-09-27 | 2 | present |
| [pkstop-central-park-bandshell](repos/pkstop-central-park-bandshell.md) | certified |  | COMPLIANT | 49256f0 | 2026-09-27 | 1 | present |
| [pkstop-national-mall](repos/pkstop-national-mall.md) | certified |  | COMPLIANT | d857c07 | 2026-09-27 | 1 | present |
| [pkstop-pike-place-market](repos/pkstop-pike-place-market.md) | certified |  | COMPLIANT | d3b96a3 | 2026-09-27 | 1 | present |
| [pkstop-santa-monica-pier](repos/pkstop-santa-monica-pier.md) | certified |  | COMPLIANT | ff728ea | 2026-09-27 | 1 | present |
| [pkstop-the-bean](repos/pkstop-the-bean.md) | certified |  | COMPLIANT | 7964814 | 2026-09-27 | 4 | present |
| [public-art-collective](repos/public-art-collective.md) | certified |  | CLEAN | 1920955 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [rapp-herdr](repos/rapp-herdr.md) | certified |  | CLEAN | fcbe1e8 | 2026-09-27 | 0 | present |
| [rapp-neighborhood-protocol](repos/rapp-neighborhood-protocol.md) | certified | v1.0.0 | CLEAN | 85d11fc | 2026-09-27 | 0 | present |
| [RAPP-Network](repos/RAPP-Network.md) | certified | v1.0.0 | CLEAN | 33f6ba6 | 2026-09-27 | 0 | present |
| [rapp-plant-smoke-20260505-233637](repos/rapp-plant-smoke-20260505-233637.md) | certified |  | COMPLIANT | 8dcfb31 | 2026-09-27 | 0 | present |
| [rapp-resident](repos/rapp-resident.md) | certified |  | CLEAN | 1d7a0e3 | 2026-09-27 | 0 | present |
| [rapp-sealed](repos/rapp-sealed.md) | certified | v1.0.0 | CLEAN | e427eaf | 2026-09-27 | 0 | present |
| [rapp-test-neighbor](repos/rapp-test-neighbor.md) | certified | v1.0.0 | COMPLIANT | 3cc46ae | 2026-09-27 | 1 | present |
| [rapp-virtual-as400](repos/rapp-virtual-as400.md) | certified |  | CLEAN | 6016907 | 2026-09-27 | 0 | present |
| [rapp-vision-neighborhood](repos/rapp-vision-neighborhood.md) | certified |  | CLEAN | 97114b2 | 2026-09-27 | 0 | present |
| [rapp-vneighborhood](repos/rapp-vneighborhood.md) | certified |  | CLEAN | 624993f | 2026-09-27 | 0 | present |
| [rapp-work-cubbies](repos/rapp-work-cubbies.md) | certified |  | CLEAN | 8197e2a | 2026-09-27 | 0 | present |
| [second-seat](repos/second-seat.md) | certified |  | CLEAN | 1fa834b | 2026-09-27 | 0 | present |
| [vneighborhood-design-studio](repos/vneighborhood-design-studio.md) | certified |  | CLEAN | da1220d | 2026-09-27 | 0 | present |
| [vneighborhood-research-lab](repos/vneighborhood-research-lab.md) | certified |  | CLEAN | c553eb7 | 2026-09-27 | 0 | present |

### Organism & Platform (20)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [braintrust-template](repos/braintrust-template.md) | certified |  | CLEAN | 83c9ab2 | 2026-09-27 | 1 | present |
| [CommunityRAPP](repos/CommunityRAPP.md) | certified | v1.0.0 | CLEAN | cc23741 | 2026-09-27 | 9 | merged, awaiting the next sweep |
| [rapp-ai](repos/rapp-ai.md) | certified | v1.0.0 | CLEAN | cc9e88d | 2026-09-27 | 7 | merged, awaiting the next sweep |
| [rapp-apex-dino](repos/rapp-apex-dino.md) | certified |  | CLEAN | d511b36 | 2026-09-27 | 0 | present |
| [rapp-base](repos/rapp-base.md) | certified | v1.2.0 | CLEAN | 7e4b8a5 | 2026-09-27 | 0 | PR open |
| [rapp-base-template](repos/rapp-base-template.md) | certified | v1.2.0 | CLEAN | 0242efb | 2026-09-27 | 0 | PR open |
| [rapp-body](repos/rapp-body.md) | certified |  | COMPLIANT | afdefe2 | 2026-09-27 | 0 | not yet added |
| [rapp-brain](repos/rapp-brain.md) | certified |  | COMPLIANT | 695e793 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-cortex](repos/rapp-cortex.md) | certified |  | CLEAN | 3b1d61a | 2026-09-27 | 1 | present |
| [rapp-dino](repos/rapp-dino.md) | certified |  | CLEAN | e9cd9c0 | 2026-09-27 | 0 | present |
| [rapp-hippocampus](repos/rapp-hippocampus.md) | certified |  | CLEAN | 18edfa1 | 2026-09-27 | 1 | present |
| [rapp-membrane](repos/rapp-membrane.md) | certified |  | CLEAN | db26f24 | 2026-09-27 | 0 | present |
| [rapp-nervous-system](repos/rapp-nervous-system.md) | certified |  | CLEAN | dfc114a | 2026-09-27 | 1 | present |
| [rapp-organism](repos/rapp-organism.md) | certified |  | CLEAN | 93d800d | 2026-09-27 | 206 | not yet added |
| [rapp-platform](repos/rapp-platform.md) | certified |  | CLEAN | ba6c555 | 2026-09-27 | 1 | present |
| [rapp-second-brain](repos/rapp-second-brain.md) | certified |  | CLEAN | 0cdf76e | 2026-09-27 | 6 | present |
| [rapp-secondbrain](repos/rapp-secondbrain.md) | certified |  | CLEAN | 23cf473 | 2026-09-27 | 0 | present |
| [rapp-spinal-cord](repos/rapp-spinal-cord.md) | certified |  | CLEAN | 43741e3 | 2026-09-27 | 1 | present |
| [RAPP_hippo](repos/RAPP_hippo.md) | certified | v1.0.0 | CLEAN | 8443b75 | 2026-09-27 | 9 | merged, awaiting the next sweep |
| [RAPPsquared](repos/RAPPsquared.md) | certified |  | CLEAN | e19d82f | 2026-09-27 | 0 | present |

### DOGG & Commons (11)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [dogg](repos/dogg.md) | not yet |  | DRIFT | 6c13129 | 2026-09-27 | 0 | present |
| [dogg-canon](repos/dogg-canon.md) | certified |  | COMPLIANT | 5cb9927 | 2026-09-27 | 0 | present |
| [dogg-markets](repos/dogg-markets.md) | certified |  | COMPLIANT | 3c3c1a1 | 2026-09-27 | 0 | present |
| [dogg-planet](repos/dogg-planet.md) | certified |  | COMPLIANT | 921f1bc | 2026-09-27 | 0 | present |
| [rapp-commons](repos/rapp-commons.md) | not yet | v1.0.0 | DRIFT | 4793bca | 2026-09-27 | 0 | present |
| [rapp-dog-hub](repos/rapp-dog-hub.md) | certified |  | CLEAN | c904967 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-frame-net](repos/rapp-frame-net.md) | certified |  | CLEAN | ad6f248 | 2026-09-27 | 0 | not yet added |
| [rapp-god-forum](repos/rapp-god-forum.md) | certified |  | CLEAN | c7c2e52 | 2026-09-27 | 0 | present |
| [rapp-open](repos/rapp-open.md) | certified |  | CLEAN | e3f39c8 | 2026-09-27 | 0 | present |
| [rappidverse-field](repos/rappidverse-field.md) | certified |  | CLEAN | b302db4 | 2026-09-27 | 0 | present |
| [workroom](repos/workroom.md) | certified |  | CLEAN | 7089c37 | 2026-09-27 | 1 | present |

### Tools & Apps (30)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [copilot-harness-sdk](repos/copilot-harness-sdk.md) | certified |  | CLEAN | 4c33b57 | 2026-09-27 | 40 | PR open |
| [dynamics365-business-process-api](repos/dynamics365-business-process-api.md) | certified |  | CLEAN | 9b5fa43 | 2026-09-27 | 1 | present |
| [lisppy-shepherd](repos/lisppy-shepherd.md) | certified |  | CLEAN | 3774249 | 2026-09-27 | 1 | present |
| [rapp-cli](repos/rapp-cli.md) | certified |  | CLEAN | df8cd16 | 2026-09-27 | 1 | PR open |
| [rapp-copilot-in-chrome](repos/rapp-copilot-in-chrome.md) | certified |  | CLEAN | a947e5f | 2026-09-27 | 0 | present |
| [rapp-copilot-in-edge](repos/rapp-copilot-in-edge.md) | certified |  | CLEAN | b26c48f | 2026-09-27 | 0 | present |
| [rapp-crispy](repos/rapp-crispy.md) | not yet | v1.5.1 | DRIFT | ed03f36 | 2026-09-27 | 0 | present |
| [rapp-dataverse](repos/rapp-dataverse.md) | certified |  | CLEAN | de40b94 | 2026-09-27 | 0 | present |
| [rapp-doorman](repos/rapp-doorman.md) | certified | v1.0.0 | CLEAN | ad58a21 | 2026-09-27 | 0 | present |
| [rapp-dynamic-workflows](repos/rapp-dynamic-workflows.md) | certified |  | CLEAN | b8b1de6 | 2026-09-27 | 8 | PR open |
| [rapp-imessage-launchpad](repos/rapp-imessage-launchpad.md) | certified |  | CLEAN | 91b94e8 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-keyring](repos/rapp-keyring.md) | certified | v0.1.0 | CLEAN | b7dac71 | 2026-09-27 | 0 | present |
| [rapp-local-install](repos/rapp-local-install.md) | certified |  | CLEAN | 7e93ebe | 2026-09-27 | 0 | present |
| [rapp-messaging](repos/rapp-messaging.md) | certified |  | CLEAN | 0586678 | 2026-09-27 | 0 | not yet added |
| [rapp-omarchy](repos/rapp-omarchy.md) | certified |  | CLEAN | 381f2a1 | 2026-09-27 | 2 | merged, awaiting the next sweep |
| [rapp-oneclick-deploy](repos/rapp-oneclick-deploy.md) | not yet |  | DRIFT | b42ea35 | 2026-09-27 | 2 | PR open |
| [rapp-projects](repos/rapp-projects.md) | certified | v0.1.1 | CLEAN | b8197c5 | 2026-09-27 | 0 | present |
| [rapp-recall](repos/rapp-recall.md) | certified | v0.1.0 | CLEAN | 2cd3f5c | 2026-09-27 | 30 | present |
| [rapp-rewind](repos/rapp-rewind.md) | not yet | v1.2.1 | DRIFT | ebd89a6 | 2026-09-27 | 0 | present |
| [rapp-sdk](repos/rapp-sdk.md) | certified | v0.2.0 | CLEAN | ede0fd4 | 2026-09-27 | 27 | present |
| [rapp-shot](repos/rapp-shot.md) | not yet | v1.3.1 | DRIFT | 0a3c2df | 2026-09-27 | 0 | present |
| [rapp-static-apis](repos/rapp-static-apis.md) | certified | v1.0.0 | CLEAN | f18927c | 2026-09-27 | 0 | present |
| [rapp-static-mcp](repos/rapp-static-mcp.md) | certified |  | CLEAN | 07bbdb8 | 2026-09-27 | 0 | present |
| [rapp-tools](repos/rapp-tools.md) | certified | workspace-v0.1.0 | CLEAN | ae2c005 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-ultracode](repos/rapp-ultracode.md) | certified |  | CLEAN | 1f39fae | 2026-09-27 | 1 | present |
| [rapp-voice](repos/rapp-voice.md) | not yet | v1.1.1 | DRIFT | 78fda5b | 2026-09-27 | 0 | present |
| [rapp-vui](repos/rapp-vui.md) | certified |  | CLEAN | ec37727 | 2026-09-27 | 0 | present |
| [rapp-workspace-manager](repos/rapp-workspace-manager.md) | certified | v1.0.0 | COMPLIANT | cadf2a9 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [RAPP_Desktop](repos/RAPP_Desktop.md) | certified | v1.0.0 | CLEAN | 03c8adf | 2026-09-27 | 0 | present |
| [RAPPAIClaudeCodePlayground](repos/RAPPAIClaudeCodePlayground.md) | certified |  | CLEAN | 3abfe5d | 2026-09-27 | 0 | present |

### Estate & Ops (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-bake-off](repos/rapp-bake-off.md) | certified |  | CLEAN | e52fe2c | 2026-09-27 | 0 | present |
| [rapp-bench](repos/rapp-bench.md) | certified |  | CLEAN | 396eeeb | 2026-09-27 | 0 | present |
| [rapp-distro](repos/rapp-distro.md) | certified |  | CLEAN | dad5879 | 2026-09-27 | 0 | PR open |
| [rapp-estate](repos/rapp-estate.md) | certified |  | CLEAN | acc17dc | 2026-09-27 | 0 | no README (skipped) |
| [rapp-infrastructure-city](repos/rapp-infrastructure-city.md) | certified |  | CLEAN | 1d62cc0 | 2026-09-27 | 0 | present |
| [rapp-metrics](repos/rapp-metrics.md) | certified |  | CLEAN | be6f588 | 2026-09-27 | 0 | present |
| [rapp-monorepo](repos/rapp-monorepo.md) | not yet |  | DRIFT | 0f1755e | 2026-09-27 | 4381 | not yet added |
| [rapp-parity](repos/rapp-parity.md) | certified |  | COMPLIANT | cad9fb5 | 2026-09-27 | 0 | present |
| [rapp-personpower](repos/rapp-personpower.md) | certified |  | CLEAN | 7bd8d29 | 2026-09-27 | 0 | present |
| [rapp-postflight](repos/rapp-postflight.md) | certified |  | CLEAN | e4d8178 | 2026-09-27 | 0 | present |
| [rapp-refresh](repos/rapp-refresh.md) | certified | v1.0.0 | CLEAN | 920c3f4 | 2026-09-27 | 0 | present |
| [rapp-roadside](repos/rapp-roadside.md) | not yet | v1.0.0 | DRIFT | 8082439 | 2026-09-27 | 0 | not yet added |
| [rapp-rock-tumbler](repos/rapp-rock-tumbler.md) | certified |  | CLEAN | e91fd2c | 2026-09-27 | 0 | present |
| [rapp-sentinel](repos/rapp-sentinel.md) | certified |  | CLEAN | 6468f1d | 2026-09-27 | 1 | present |
| [rapp-support](repos/rapp-support.md) | certified |  | CLEAN | 899af64 | 2026-09-27 | 0 | present |
| [rapp-tower](repos/rapp-tower.md) | certified |  | CLEAN | d67f816 | 2026-09-27 | 4 | present |
| [rapp-version-selector](repos/rapp-version-selector.md) | certified |  | CLEAN | 0dab250 | 2026-09-27 | 9 | present |
| [sentinel](repos/sentinel.md) | certified |  | CLEAN | e322236 | 2026-09-27 | 0 | present |

### Worlds & Play (26)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [ant-farm](repos/ant-farm.md) | certified |  | COMPLIANT | a61c7fe | 2026-09-27 | 1 | present |
| [double-jump](repos/double-jump.md) | certified | v0.1.0 | CLEAN | 5b1846e | 2026-09-27 | 17 | present |
| [leviathan](repos/leviathan.md) | certified |  | CLEAN | acb77ae | 2026-09-27 | 0 | present |
| [racon](repos/racon.md) | certified | v1.0.0 | CLEAN | 7f941ce | 2026-09-27 | 0 | present |
| [RaGo](repos/RaGo.md) | certified | v2.1.0 | CLEAN | cff87bc | 2026-09-27 | 0 | present |
| [rapp-basket](repos/rapp-basket.md) | certified |  | CLEAN | 4963916 | 2026-09-27 | 0 | present |
| [rapp-burrow](repos/rapp-burrow.md) | certified |  | CLEAN | 2f52927 | 2026-09-27 | 0 | present |
| [rapp-coop](repos/rapp-coop.md) | certified |  | CLEAN | 721e40e | 2026-09-27 | 0 | present |
| [rapp-eternity](repos/rapp-eternity.md) | certified |  | CLEAN | 03e483d | 2026-09-27 | 0 | present |
| [rapp-fps](repos/rapp-fps.md) | certified |  | CLEAN | 6e00362 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp-heir](repos/rapp-heir.md) | certified |  | CLEAN | ab99a26 | 2026-09-27 | 3 | merged, awaiting the next sweep |
| [rapp-holo](repos/rapp-holo.md) | certified |  | CLEAN | ec8e062 | 2026-09-27 | 0 | present |
| [rapp-hologram](repos/rapp-hologram.md) | certified | v1.0.0 | CLEAN | 421b90d | 2026-09-27 | 0 | present |
| [rapp-lantern](repos/rapp-lantern.md) | not yet |  | DRIFT | 1af70be | 2026-09-27 | 0 | PR open |
| [rapp-moment](repos/rapp-moment.md) | certified | v1.1.0 | CLEAN | d82ba10 | 2026-09-27 | 0 | present |
| [rapp-moonshots](repos/rapp-moonshots.md) | certified |  | CLEAN | 789f933 | 2026-09-27 | 3 | not yet added |
| [rapp-pets](repos/rapp-pets.md) | certified |  | CLEAN | d0384fa | 2026-09-27 | 0 | present |
| [rapp-play-pokemon](repos/rapp-play-pokemon.md) | certified |  | CLEAN | 9537146 | 2026-09-27 | 1 | merged, awaiting the next sweep |
| [rapp-snap](repos/rapp-snap.md) | certified |  | CLEAN | 127de5b | 2026-09-27 | 0 | present |
| [rapp-zoo-v2](repos/rapp-zoo-v2.md) | not yet | v0.1.0 | DRIFT | e7f2377 | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rapp_orion](repos/rapp_orion.md) | certified |  | CLEAN | 58e3ad7 | 2026-09-27 | 8 | merged, awaiting the next sweep |
| [rappid](repos/rappid.md) | not yet |  | DRIFT | 885d24f | 2026-09-27 | 0 | merged, awaiting the next sweep |
| [rio](repos/rio.md) | not yet | v1.0.0 | DRIFT | 1062e28 | 2026-09-27 | 0 | not yet added |
| [rionet](repos/rionet.md) | certified |  | CLEAN | ee9ee28 | 2026-09-27 | 0 | not yet added |
| [sim-art-collective](repos/sim-art-collective.md) | certified |  | COMPLIANT | dcf6048 | 2026-09-27 | 1 | present |
| [the-coliseum](repos/the-coliseum.md) | certified |  | CLEAN | a823126 | 2026-09-27 | 0 | present |
