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

Each repo's README gets one marked line (today, of 317: 13 carry it, 2 held, 286 waiting for their pull request (wave 2 waits for the owner's approval), 15 without a README (skipped), 1 not checked (they could not be cloned)): its badge (served from this folder by GitHub Pages, so the URL never changes) and a link to [Start here](https://github.com/kody-w/rapp-installer#start-here) for anyone without a Brainstem yet. "experimental" mentions are tracked here as a metric; they are not a gate yet.

**Member cards:** 12 of 317 repos carry their card in the RAPP Hive (`.rapp/member.md`, the repo's own side of its pointer in `members/`); the file of each repo that has one links it.

A Hive holds only markdown, so each badge is `badges/<repo>.svg.md`: its front matter tells GitHub Pages to serve it as `https://kody-w.github.io/rapp-hive-public/portfolio/badges/<repo>.svg` (image/svg+xml).

## The map

**[Subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)** (zoomable; click a station for its portfolio file and its repo) · [poster PDF](https://kody-w.github.io/rapp-hive-public/portfolio/subway.pdf) · [SVG](https://kody-w.github.io/rapp-hive-public/portfolio/subway.svg)

Lines are the families below; stations are repos, filled by status (hollow when deprecated, superseded or archived); the RAPP/1 Core line runs in layer order and ends at `rapp-installer`, the Start here terminal. It is drawn from these files by the `rapp1_network` package (its release copy is in [`tools/`](https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/tools)), and the links between repos come from each file's `links_to`.

**Version 7**, crawled 2026-09-26 13:41 UTC. Every crawl is one RAPP/1 frame, a `body.pulse` on the network's body stream `rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def`. The [timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html) lists every version with its pulse hashes and what changed, and each version's maps stay under `versions/`.

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
| [lisppy](repos/lisppy.md) | certified |  | CLEAN | a5db2db | 2026-09-26 | 1 | present |
| [RAPP](repos/RAPP.md) | certified | v1.0.0 | COMPLIANT | 4afb635 | 2026-09-26 | 162 | present |
| [rapp-1](repos/rapp-1.md) | certified | LTS 591e014 | COMPLIANT | bae4e3c | 2026-09-26 | 0 | present |
| [rapp-drift-lint](repos/rapp-drift-lint.md) | certified |  | CLEAN | 92a97a1 | 2026-09-26 | 0 | present |
| [rapp-installer](repos/rapp-installer.md) | certified | v1.0.0 · LTS brainstem-v0.6.9 | CLEAN | 49db80c | 2026-09-26 | 11 | held: the owner holds the grail repo (PR #48 stays open) |
| [rapp-work](repos/rapp-work.md) | certified | LTS 29ead23 | COMPLIANT | 4d1a527 | 2026-09-26 | 0 | present |
| [rapp-workspace](repos/rapp-workspace.md) | certified |  | COMPLIANT | 52d4f19 | 2026-09-26 | 50 | held: waiting on G24 (front door editable) |

### Hive (7)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-hub](repos/hive-hub.md) | certified |  | CLEAN | 2fd4223 | 2026-09-26 | 5 | present |
| [hive-hub-join](repos/hive-hub-join.md) | certified |  | CLEAN | 7ae4e25 | 2026-09-26 | 0 | present |
| [hive-hub-mcp](repos/hive-hub-mcp.md) | certified |  | CLEAN | 312eedc | 2026-09-26 | 0 | present |
| [rapp-hive-hub](repos/rapp-hive-hub.md) | certified |  | COMPLIANT | 1c15452 | 2026-09-26 | 7 | present |
| [rapp-hive-hub-join](repos/rapp-hive-hub-join.md) | certified |  | CLEAN | 3598da1 | 2026-09-26 | 0 | present |
| [rapp-hive-public](repos/rapp-hive-public.md) | certified |  | CLEAN | 2c65e5a | 2026-09-26 | 41 | present |
| [rapp-model-hive](repos/rapp-model-hive.md) | not yet |  | DRIFT | 1bda54d | 2026-09-26 | 18 | present |

### Agents (RAR) (1)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [RAR](repos/RAR.md) | certified | v1.0.0 | COMPLIANT | d284fad | 2026-09-26 | 161 | present |

## Wave 2: the rest of the RAPP family (302)

### Hive (2)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-showcase](repos/hive-showcase.md) | certified |  | CLEAN | 331fb28 | 2026-09-26 | 7 | not yet added |
| [rapp-hive-app](repos/rapp-hive-app.md) | certified |  | CLEAN | 20880d5 | 2026-09-26 | 0 | not yet added |

### Agents (RAR) (21)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [AI-Agent-Templates-Pilot](repos/AI-Agent-Templates-Pilot.md) | certified |  | CLEAN | 5bb20e2 | 2026-09-26 | 0 | not yet added |
| [cowork-cookbook-rapp](repos/cowork-cookbook-rapp.md) | not yet | v1.0.0 | DRIFT | 2e2a392 | 2026-09-26 | 0 | not yet added |
| [obsidian-binder](repos/obsidian-binder.md) | certified |  | CLEAN | 277a98d | 2026-09-26 | 0 | not yet added |
| [rapp-agents](repos/rapp-agents.md) | certified | v1.0.0 | CLEAN | 3de844f | 2026-09-26 | 0 | not yet added |
| [rapp-carts](repos/rapp-carts.md) | certified | v1.0.0 | CLEAN | eeed973 | 2026-09-26 | 0 | not yet added |
| [rapp-claude-skills](repos/rapp-claude-skills.md) | certified | v1.0.0 | CLEAN | d675bf0 | 2026-09-26 | 0 | not yet added |
| [rapp-egg-hub](repos/rapp-egg-hub.md) | not yet | v1.0.0 | DRIFT | 4c49318 | 2026-09-26 | 11 | not yet added |
| [rapp-hatchery](repos/rapp-hatchery.md) | certified |  | CLEAN | 9af32d0 | 2026-09-26 | 4 | not yet added |
| [rapp-leviathan-hub](repos/rapp-leviathan-hub.md) | not yet |  | DRIFT | bfefc79 | 2026-09-26 | 0 | not yet added |
| [rapp-packs](repos/rapp-packs.md) | certified |  | CLEAN | 19cb75f | 2026-09-26 | 0 | not yet added |
| [rapp-sentinel-hub](repos/rapp-sentinel-hub.md) | certified |  | CLEAN | b3a4dfb | 2026-09-26 | 0 | not yet added |
| [rapp-skill](repos/rapp-skill.md) | certified |  | CLEAN | ff36d91 | 2026-09-26 | 0 | not yet added |
| [rapp-skills](repos/rapp-skills.md) | certified |  | CLEAN | aaac415 | 2026-09-26 | 0 | not yet added |
| [rapp-stack-cubby](repos/rapp-stack-cubby.md) | certified | v0.1.0rc11 | COMPLIANT | 1fee389 | 2026-09-26 | 13 | not yet added |
| [rapp-store-archive](repos/rapp-store-archive.md) | certified |  | CLEAN | da2b364 | 2026-09-26 | 0 | not yet added |
| [rapp-toaster](repos/rapp-toaster.md) | certified |  | CLEAN | d54ba84 | 2026-09-26 | 0 | not yet added |
| [RAPP_Hub](repos/RAPP_Hub.md) | certified |  | CLEAN | 00ac2f7 | 2026-09-26 | 0 | not yet added |
| [RAPP_Sense_Store](repos/RAPP_Sense_Store.md) | certified |  | CLEAN | 36efba8 | 2026-09-26 | 0 | not yet added |
| [RAPP_Store](repos/RAPP_Store.md) | not yet | v1.0.0 | DRIFT | c979a60 | 2026-09-26 | 76 | not yet added |
| [RAPPcards](repos/RAPPcards.md) | certified |  | CLEAN | 5bfcea8 | 2026-09-26 | 2 | not yet added |
| [red-binder](repos/red-binder.md) | certified |  | CLEAN | 704e7b8 | 2026-09-26 | 10 | not yet added |

### Brainstem (19)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-agent](repos/brainstem-agent.md) | certified |  | CLEAN | a8801a2 | 2026-09-26 | 59 | not yet added |
| [brainstem-copilot](repos/brainstem-copilot.md) | certified |  | CLEAN | 7f912fa | 2026-09-26 | 4 | not yet added |
| [brainstem-harness](repos/brainstem-harness.md) | certified |  | CLEAN | dbabbf2 | 2026-09-26 | 0 | not yet added |
| [chat](repos/chat.md) | certified |  | CLEAN | 3daf0fc | 2026-09-26 | 0 | not yet added |
| [ez-rapp](repos/ez-rapp.md) | certified | v0.1.3 | CLEAN | 40c8349 | 2026-09-26 | 0 | not yet added |
| [rapp-brainfreeze](repos/rapp-brainfreeze.md) | certified |  | CLEAN | d7d816c | 2026-09-26 | 2 | not yet added |
| [rapp-brainfreeze-studio](repos/rapp-brainfreeze-studio.md) | certified |  | CLEAN | 7d9f065 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem](repos/rapp-brainstem.md) | certified | v0.2.1 | COMPLIANT | dd1f8f7 | 2026-09-26 | 3 | not yet added |
| [rapp-brainstem-foundation](repos/rapp-brainstem-foundation.md) | unchecked |  |  |  | 2026-09-26 |  | none (not checked) |
| [rapp-brainstem-frontier-template](repos/rapp-brainstem-frontier-template.md) | certified |  | CLEAN | cb31f5f | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-sdk](repos/rapp-brainstem-sdk.md) | certified | v1.0.0 | CLEAN | 418fd69 | 2026-09-26 | 0 | not yet added |
| [rapp-light](repos/rapp-light.md) | certified |  | CLEAN | 01a7e1b | 2026-09-26 | 5 | not yet added |
| [rapp-petri](repos/rapp-petri.md) | certified |  | CLEAN | b1f953c | 2026-09-26 | 0 | not yet added |
| [rapp-quests](repos/rapp-quests.md) | certified |  | CLEAN | d2eb2e2 | 2026-09-26 | 0 | not yet added |
| [rapp-static-brainstem](repos/rapp-static-brainstem.md) | certified | v1.2.0 | CLEAN | 0173eb8 | 2026-09-26 | 0 | not yet added |
| [rapp-vscode-extension](repos/rapp-vscode-extension.md) | certified | v1.0.0 | CLEAN | 774e9f4 | 2026-09-26 | 0 | no README (skipped) |
| [skillstem](repos/skillstem.md) | certified |  | CLEAN | 385e40e | 2026-09-26 | 0 | not yet added |
| [stemcell](repos/stemcell.md) | certified |  | CLEAN | 7cc90dd | 2026-09-26 | 6 | not yet added |
| [vbrainstem](repos/vbrainstem.md) | not yet |  | DRIFT | ee5499f | 2026-09-26 | 2 | not yet added |

### Brainstem Connect (16)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-brainstem-claude](repos/rapp-brainstem-claude.md) | certified |  | CLEAN | 2211bd9 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-claude-desktop](repos/rapp-brainstem-claude-desktop.md) | certified |  | CLEAN | e84ba0f | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-cline](repos/rapp-brainstem-cline.md) | certified |  | CLEAN | bc92807 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-codex](repos/rapp-brainstem-codex.md) | certified |  | CLEAN | 34364fb | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-copilot](repos/rapp-brainstem-copilot.md) | certified |  | CLEAN | 1ed120e | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-cursor](repos/rapp-brainstem-cursor.md) | certified |  | CLEAN | 8a7a3c5 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-gemini](repos/rapp-brainstem-gemini.md) | certified |  | CLEAN | c9c5011 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-goose](repos/rapp-brainstem-goose.md) | certified |  | CLEAN | 57c1656 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-kiro](repos/rapp-brainstem-kiro.md) | certified |  | CLEAN | f33042f | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-mcp](repos/rapp-brainstem-mcp.md) | certified |  | CLEAN | e9cca1b | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-opencode](repos/rapp-brainstem-opencode.md) | certified |  | CLEAN | c689b44 | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-plugin](repos/rapp-brainstem-plugin.md) | certified |  | CLEAN | aa3793e | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-vscode](repos/rapp-brainstem-vscode.md) | certified |  | CLEAN | 4e5be0a | 2026-09-26 | 0 | not yet added |
| [rapp-brainstem-windsurf](repos/rapp-brainstem-windsurf.md) | certified |  | CLEAN | 6e64c3c | 2026-09-26 | 0 | not yet added |
| [rapp-mcp](repos/rapp-mcp.md) | certified |  | CLEAN | a6bb38e | 2026-09-26 | 2 | not yet added |
| [scout-brainstem-bootstrap](repos/scout-brainstem-bootstrap.md) | certified |  | CLEAN | 2565d0a | 2026-09-26 | 48 | not yet added |

### Learn & Docs (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-bootcamp](repos/brainstem-bootcamp.md) | certified |  | CLEAN | c690f51 | 2026-09-26 | 0 | not yet added |
| [dimensional-bottles](repos/dimensional-bottles.md) | certified |  | COMPLIANT | cbe0bab | 2026-09-26 | 0 | not yet added |
| [learn-brainstem](repos/learn-brainstem.md) | certified |  | CLEAN | 504ace3 | 2026-09-26 | 0 | not yet added |
| [RAPP-Bible](repos/RAPP-Bible.md) | certified |  | CLEAN | 9520783 | 2026-09-26 | 9 | not yet added |
| [rapp-brainstem-walkthrough](repos/rapp-brainstem-walkthrough.md) | certified | v0.6.16 | CLEAN | 8393e67 | 2026-09-26 | 4 | not yet added |
| [rapp-demos](repos/rapp-demos.md) | certified | v1.0.0 | CLEAN | dabd593 | 2026-09-26 | 0 | not yet added |
| [rapp-docs](repos/rapp-docs.md) | certified |  | CLEAN | 0cd0b0a | 2026-09-26 | 3 | not yet added |
| [rapp-education-shorts](repos/rapp-education-shorts.md) | certified |  | CLEAN | bbda5b7 | 2026-09-26 | 0 | not yet added |
| [rapp-lab-kit](repos/rapp-lab-kit.md) | certified |  | CLEAN | f73b292 | 2026-09-26 | 0 | not yet added |
| [rapp-map](repos/rapp-map.md) | not yet | v1.0.0 · LTS 4c8ba6b | DRIFT | 81dd6f0 | 2026-09-26 | 54 | not yet added |
| [rapp-mapp](repos/rapp-mapp.md) | certified |  | CLEAN | 4743d74 | 2026-09-26 | 0 | not yet added |
| [rapp-mission](repos/rapp-mission.md) | certified |  | CLEAN | 93e2514 | 2026-09-26 | 0 | not yet added |
| [rapp-roadmap](repos/rapp-roadmap.md) | certified |  | CLEAN | 60fea67 | 2026-09-26 | 1 | not yet added |
| [rapp-specs](repos/rapp-specs.md) | certified |  | COMPLIANT | 7053682 | 2026-09-26 | 0 | not yet added |
| [rapp-spine](repos/rapp-spine.md) | certified |  | CLEAN | b21ebe1 | 2026-09-26 | 0 | not yet added |
| [rapp-wiki-observatory](repos/rapp-wiki-observatory.md) | certified |  | CLEAN | ccccb5c | 2026-09-26 | 0 | not yet added |
| [rapp_docs](repos/rapp_docs.md) | certified |  | CLEAN | 45d6ee5 | 2026-09-26 | 0 | not yet added |
| [rappdex](repos/rappdex.md) | certified |  | CLEAN | 10017cc | 2026-09-26 | 0 | not yet added |

### Release Channels (19)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [openrappter-alpha](repos/openrappter-alpha.md) | certified |  | CLEAN | 235e93e | 2026-09-26 | 0 | not yet added |
| [openrappter-beta](repos/openrappter-beta.md) | certified |  | CLEAN | c29c6d4 | 2026-09-26 | 0 | not yet added |
| [openrappter-canary](repos/openrappter-canary.md) | certified |  | CLEAN | a86599c | 2026-09-26 | 0 | not yet added |
| [openrappter-nightly](repos/openrappter-nightly.md) | certified |  | CLEAN | ea34fa6 | 2026-09-26 | 0 | not yet added |
| [openrappter-release-train](repos/openrappter-release-train.md) | certified |  | CLEAN | 525e19f | 2026-09-26 | 0 | not yet added |
| [rapp-alpha](repos/rapp-alpha.md) | certified |  | CLEAN | 44be78a | 2026-09-26 | 12 | not yet added |
| [rapp-beta](repos/rapp-beta.md) | certified |  | CLEAN | 562b5e1 | 2026-09-26 | 12 | not yet added |
| [rapp-brainstem-beta](repos/rapp-brainstem-beta.md) | certified |  | CLEAN | 349c5c0 | 2026-09-26 | 0 | not yet added |
| [rapp-canary](repos/rapp-canary.md) | certified |  | COMPLIANT | 7ac5c77 | 2026-09-26 | 20 | not yet added |
| [rapp-flight](repos/rapp-flight.md) | certified |  | CLEAN | 17bc55c | 2026-09-26 | 2 | not yet added |
| [rapp-flight-deck](repos/rapp-flight-deck.md) | certified |  | CLEAN | f33f265 | 2026-09-26 | 1 | not yet added |
| [rapp-installer-canary](repos/rapp-installer-canary.md) | certified |  | CLEAN | 8bb6b75 | 2026-09-26 | 7 | not yet added |
| [rapp-installer-dev](repos/rapp-installer-dev.md) | certified |  | CLEAN | 452ef43 | 2026-09-26 | 8 | not yet added |
| [rapp-mirror-releases](repos/rapp-mirror-releases.md) | certified | v0.2.0 | CLEAN | f10ff84 | 2026-09-26 | 0 | not yet added |
| [rapp-nightly](repos/rapp-nightly.md) | certified |  | CLEAN | 27d6261 | 2026-09-26 | 12 | not yet added |
| [rapp-release-train](repos/rapp-release-train.md) | certified |  | CLEAN | d38837a | 2026-09-26 | 6 | not yet added |
| [rapp-rings](repos/rapp-rings.md) | certified |  | CLEAN | 4eb4fca | 2026-09-26 | 1 | not yet added |
| [rapp-shape-aibast](repos/rapp-shape-aibast.md) | certified |  | CLEAN | e8a66b0 | 2026-09-26 | 21 | not yet added |
| [rapp-train](repos/rapp-train.md) | certified |  | CLEAN | d271983 | 2026-09-26 | 0 | not yet added |

### OpenRappter (8)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [homebrew-tap](repos/homebrew-tap.md) | certified |  | CLEAN | 5d39f7e | 2026-09-26 | 0 | no README (skipped) |
| [openrappter](repos/openrappter.md) | certified | v1.13.1-bar | CLEAN | d8601aa | 2026-09-26 | 1 | not yet added |
| [rappter-cli](repos/rappter-cli.md) | certified |  | CLEAN | c7b9193 | 2026-09-26 | 0 | not yet added |
| [rappter-plays-palworld](repos/rappter-plays-palworld.md) | certified |  | CLEAN | 88f59b6 | 2026-09-26 | 0 | not yet added |
| [rappter-plays-pokemon](repos/rappter-plays-pokemon.md) | certified |  | CLEAN | dfda5a8 | 2026-09-26 | 4 | not yet added |
| [rappter-prompts](repos/rappter-prompts.md) | certified |  | CLEAN | ee16258 | 2026-09-26 | 0 | not yet added |
| [rappter-vui](repos/rappter-vui.md) | certified |  | CLEAN | 20d949b | 2026-09-26 | 0 | not yet added |
| [rappterhub](repos/rappterhub.md) | certified |  | CLEAN | e06632d | 2026-09-26 | 0 | not yet added |

### Rappterbook (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [mars-barn](repos/mars-barn.md) | certified |  | CLEAN | 2203505 | 2026-09-26 | 14 | not yet added |
| [rappbook-admin](repos/rappbook-admin.md) | certified |  | CLEAN | 33f9f0d | 2026-09-26 | 0 | not yet added |
| [rappterbook](repos/rappterbook.md) | not yet | v1.0.0 | DRIFT | 52515cc | 2026-09-26 | 4166 | not yet added |
| [rappterbook-agent](repos/rappterbook-agent.md) | certified |  | CLEAN | 8d15842 | 2026-09-26 | 2 | not yet added |
| [rappterbook-agent-dna](repos/rappterbook-agent-dna.md) | certified |  | CLEAN | b054f18 | 2026-09-26 | 0 | not yet added |
| [rappterbook-agent-exchange](repos/rappterbook-agent-exchange.md) | certified |  | CLEAN | 7285ab1 | 2026-09-26 | 4 | not yet added |
| [rappterbook-api](repos/rappterbook-api.md) | certified |  | CLEAN | a3f5202 | 2026-09-26 | 1 | not yet added |
| [rappterbook-autopilot](repos/rappterbook-autopilot.md) | certified |  | CLEAN | a6b65c3 | 2026-09-26 | 0 | not yet added |
| [rappterbook-commons](repos/rappterbook-commons.md) | certified |  | CLEAN | 9f2dc28 | 2026-09-26 | 0 | not yet added |
| [rappterbook-engine-test](repos/rappterbook-engine-test.md) | certified |  | CLEAN | 040cc86 | 2026-09-26 | 230 | no README (skipped) |
| [rappterbook-first-bond](repos/rappterbook-first-bond.md) | certified |  | CLEAN | 6da27b3 | 2026-09-26 | 0 | not yet added |
| [rappterbook-governance](repos/rappterbook-governance.md) | certified |  | CLEAN | 3b8e793 | 2026-09-26 | 0 | not yet added |
| [rappterbook-impossible-product](repos/rappterbook-impossible-product.md) | certified | frame-03.2 | CLEAN | 08a4481 | 2026-09-26 | 0 | not yet added |
| [rappterbook-join](repos/rappterbook-join.md) | certified |  | CLEAN | fdaa23a | 2026-09-26 | 0 | not yet added |
| [rappterbook-knowledge-graph](repos/rappterbook-knowledge-graph.md) | certified |  | CLEAN | ff6a9c7 | 2026-09-26 | 0 | not yet added |
| [rappterbook-market-maker](repos/rappterbook-market-maker.md) | certified |  | CLEAN | 8306b50 | 2026-09-26 | 0 | not yet added |
| [rappterbook-mars-barn](repos/rappterbook-mars-barn.md) | certified |  | CLEAN | 5d9ca2f | 2026-09-26 | 13 | not yet added |
| [rappterbook-phantom](repos/rappterbook-phantom.md) | certified |  | CLEAN | 999d76c | 2026-09-26 | 0 | not yet added |
| [rappterbook-seedmaker](repos/rappterbook-seedmaker.md) | certified |  | CLEAN | 11688fd | 2026-09-26 | 0 | no README (skipped) |
| [rappterbook-social-graph](repos/rappterbook-social-graph.md) | certified |  | CLEAN | acb1957 | 2026-09-26 | 0 | not yet added |
| [rappterbook-v2](repos/rappterbook-v2.md) | certified |  | CLEAN | ed4a91f | 2026-09-26 | 0 | no README (skipped) |
| [rappterbook-v2-state](repos/rappterbook-v2-state.md) | certified |  | CLEAN | 7bb79f1 | 2026-09-26 | 32 | not yet added |
| [rappterbook-vm](repos/rappterbook-vm.md) | certified |  | CLEAN | 10e39a1 | 2026-09-26 | 4 | not yet added |

### Rappterverse (11)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [CrystalRAPP](repos/CrystalRAPP.md) | certified |  | CLEAN | 5fd0ef7 | 2026-09-26 | 1 | no README (skipped) |
| [rappter-distro](repos/rappter-distro.md) | not yet |  | DRIFT | fe8d558 | 2026-09-26 | 29 | not yet added |
| [rappter-factory](repos/rappter-factory.md) | certified |  | CLEAN | 6527028 | 2026-09-26 | 2 | not yet added |
| [rappter-mmo](repos/rappter-mmo.md) | certified |  | CLEAN | 757291f | 2026-09-26 | 0 | no README (skipped) |
| [rappter-site](repos/rappter-site.md) | not yet |  | DRIFT | 6ed0182 | 2026-09-26 | 1 | no README (skipped) |
| [rappterbox](repos/rappterbox.md) | certified | v0.12.2 | COMPLIANT | 656d127 | 2026-09-26 | 24 | not yet added |
| [RappterNest](repos/RappterNest.md) | certified |  | CLEAN | 67d7be5 | 2026-09-26 | 0 | no README (skipped) |
| [rappterverse](repos/rappterverse.md) | certified |  | CLEAN | 6819ad7 | 2026-09-26 | 1 | not yet added |
| [rappterverse-data](repos/rappterverse-data.md) | certified |  | CLEAN | cff8bb0 | 2026-09-26 | 0 | not yet added |
| [ShadowRAPP](repos/ShadowRAPP.md) | certified |  | CLEAN | 0ead081 | 2026-09-26 | 0 | no README (skipped) |
| [VoidRAPP](repos/VoidRAPP.md) | certified |  | CLEAN | 375968e | 2026-09-26 | 0 | no README (skipped) |

### Rappvision (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-remix](repos/rapp-remix.md) | certified |  | CLEAN | 04cb6f5 | 2026-09-26 | 0 | not yet added |
| [rapp-video](repos/rapp-video.md) | certified |  | CLEAN | 5516a84 | 2026-09-26 | 6 | not yet added |
| [rapp-vision](repos/rapp-vision.md) | certified | oil-field-season-v1.0.0 | CLEAN | c988c19 | 2026-09-26 | 0 | not yet added |
| [rappvision-after-midnight-maps](repos/rappvision-after-midnight-maps.md) | certified |  | CLEAN | 43dd543 | 2026-09-26 | 0 | not yet added |
| [rappvision-brainstem-notes](repos/rappvision-brainstem-notes.md) | certified |  | CLEAN | 70a1b6f | 2026-09-26 | 0 | not yet added |
| [rappvision-creature-office-hours](repos/rappvision-creature-office-hours.md) | certified |  | CLEAN | be8a56f | 2026-09-26 | 0 | not yet added |
| [rappvision-field-notes](repos/rappvision-field-notes.md) | certified |  | CLEAN | 02fd87a | 2026-09-26 | 0 | not yet added |
| [rappvision-kitchen-table-physics](repos/rappvision-kitchen-table-physics.md) | certified |  | CLEAN | a2133bd | 2026-09-26 | 0 | not yet added |
| [rappvision-new-way-of-work](repos/rappvision-new-way-of-work.md) | certified |  | CLEAN | 36aa36a | 2026-09-26 | 0 | no README (skipped) |
| [rappvision-null-arcade](repos/rappvision-null-arcade.md) | certified |  | CLEAN | 9211c75 | 2026-09-26 | 0 | not yet added |
| [rappvision-one-minute-orchestra](repos/rappvision-one-minute-orchestra.md) | certified |  | CLEAN | e376927 | 2026-09-26 | 1 | not yet added |
| [rappvision-patch-notes-tomorrow](repos/rappvision-patch-notes-tomorrow.md) | certified |  | CLEAN | aa4403d | 2026-09-26 | 0 | not yet added |
| [rappvision-pigeon-post](repos/rappvision-pigeon-post.md) | certified |  | CLEAN | 836983f | 2026-09-26 | 10 | not yet added |
| [rappvision-pokemon](repos/rappvision-pokemon.md) | certified |  | CLEAN | 3c693cf | 2026-09-26 | 0 | not yet added |
| [rappvision-prompt-frontier](repos/rappvision-prompt-frontier.md) | certified |  | CLEAN | 5249417 | 2026-09-26 | 0 | not yet added |
| [rappvision-protocol-minute](repos/rappvision-protocol-minute.md) | certified |  | CLEAN | 0a72c43 | 2026-09-26 | 0 | not yet added |
| [rappvision-rappid-zoo](repos/rappvision-rappid-zoo.md) | certified |  | CLEAN | 34244eb | 2026-09-26 | 0 | not yet added |
| [rappvision-rappterbox](repos/rappvision-rappterbox.md) | certified |  | CLEAN | 6af62eb | 2026-09-26 | 0 | not yet added |
| [rappvision-receipt-culture](repos/rappvision-receipt-culture.md) | certified |  | CLEAN | cd22ff3 | 2026-09-26 | 0 | not yet added |
| [rappvision-repair-manual](repos/rappvision-repair-manual.md) | certified |  | CLEAN | 8bdced4 | 2026-09-26 | 0 | not yet added |
| [rappvision-rnr](repos/rappvision-rnr.md) | certified |  | CLEAN | eb9d288 | 2026-09-26 | 0 | not yet added |
| [rappvision-signal-garden](repos/rappvision-signal-garden.md) | certified |  | CLEAN | 831bd38 | 2026-09-26 | 0 | not yet added |
| [rappvision-tiny-bureau](repos/rappvision-tiny-bureau.md) | certified |  | CLEAN | f3296c1 | 2026-09-26 | 0 | not yet added |

### Twins (15)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [echo-brainstem](repos/echo-brainstem.md) | certified |  | COMPLIANT | e9f5c46 | 2026-09-26 | 2 | not yet added |
| [lumen-brainstem](repos/lumen-brainstem.md) | certified |  | COMPLIANT | 11d0aee | 2026-09-26 | 2 | not yet added |
| [rapp-kite](repos/rapp-kite.md) | certified | v1.0.0 | CLEAN | f3e7e2d | 2026-09-26 | 0 | not yet added |
| [rapp-kited-twin](repos/rapp-kited-twin.md) | certified | v1.0.0 | CLEAN | 9f844ec | 2026-09-26 | 0 | not yet added |
| [rapp-overwatch](repos/rapp-overwatch.md) | certified |  | CLEAN | 8205512 | 2026-09-26 | 0 | not yet added |
| [rapp-ratchet](repos/rapp-ratchet.md) | certified |  | CLEAN | 187bff1 | 2026-09-26 | 0 | not yet added |
| [rapp-twin](repos/rapp-twin.md) | certified |  | CLEAN | 588fead | 2026-09-26 | 1 | not yet added |
| [rapp-twin-hub](repos/rapp-twin-hub.md) | certified |  | CLEAN | 97fb82d | 2026-09-26 | 0 | not yet added |
| [rapp-twin-in-residence](repos/rapp-twin-in-residence.md) | certified |  | CLEAN | ec47ca5 | 2026-09-26 | 1 | not yet added |
| [rapp-zoo](repos/rapp-zoo.md) | certified | v1.2.0 | COMPLIANT | 7a0eeb9 | 2026-09-26 | 3 | not yet added |
| [sim-demo-twin](repos/sim-demo-twin.md) | certified |  | COMPLIANT | bf03e7e | 2026-09-26 | 1 | not yet added |
| [tide-brainstem](repos/tide-brainstem.md) | certified |  | COMPLIANT | 72162a8 | 2026-09-26 | 2 | not yet added |
| [twin-binder](repos/twin-binder.md) | certified |  | CLEAN | 5e41cd9 | 2026-09-26 | 0 | not yet added |
| [twin-egg-hatcher](repos/twin-egg-hatcher.md) | certified |  | CLEAN | 6e96a7e | 2026-09-26 | 0 | not yet added |
| [wildhaven-ai-homes-twin](repos/wildhaven-ai-homes-twin.md) | certified |  | COMPLIANT | 395e970 | 2026-09-26 | 24 | not yet added |

### Neighborhoods (22)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [heimdall](repos/heimdall.md) | certified |  | COMPLIANT | 022079a | 2026-09-26 | 2 | not yet added |
| [microsoft-se-team-neighborhood](repos/microsoft-se-team-neighborhood.md) | certified | v1.0.0 | COMPLIANT | 6f00b05 | 2026-09-26 | 2 | not yet added |
| [pkstop-central-park-bandshell](repos/pkstop-central-park-bandshell.md) | certified |  | COMPLIANT | 42b79c0 | 2026-09-26 | 1 | not yet added |
| [pkstop-national-mall](repos/pkstop-national-mall.md) | certified |  | COMPLIANT | b8d2bf3 | 2026-09-26 | 1 | not yet added |
| [pkstop-pike-place-market](repos/pkstop-pike-place-market.md) | certified |  | COMPLIANT | d2962af | 2026-09-26 | 1 | not yet added |
| [pkstop-santa-monica-pier](repos/pkstop-santa-monica-pier.md) | certified |  | COMPLIANT | d6a176f | 2026-09-26 | 1 | not yet added |
| [pkstop-the-bean](repos/pkstop-the-bean.md) | certified |  | COMPLIANT | f992abc | 2026-09-26 | 2 | not yet added |
| [public-art-collective](repos/public-art-collective.md) | certified |  | CLEAN | a10019d | 2026-09-26 | 1 | not yet added |
| [rapp-herdr](repos/rapp-herdr.md) | certified |  | CLEAN | e75b9b3 | 2026-09-26 | 0 | not yet added |
| [rapp-neighborhood-protocol](repos/rapp-neighborhood-protocol.md) | certified | v1.0.0 | CLEAN | 44e0c6e | 2026-09-26 | 0 | not yet added |
| [RAPP-Network](repos/RAPP-Network.md) | certified | v1.0.0 | CLEAN | a22f3f2 | 2026-09-26 | 0 | not yet added |
| [rapp-plant-smoke-20260505-233637](repos/rapp-plant-smoke-20260505-233637.md) | certified |  | COMPLIANT | 3db61bf | 2026-09-26 | 0 | not yet added |
| [rapp-resident](repos/rapp-resident.md) | certified |  | CLEAN | de07d30 | 2026-09-26 | 0 | not yet added |
| [rapp-sealed](repos/rapp-sealed.md) | certified | v1.0.0 | CLEAN | c6e35c8 | 2026-09-26 | 0 | not yet added |
| [rapp-test-neighbor](repos/rapp-test-neighbor.md) | certified | v1.0.0 | COMPLIANT | d830223 | 2026-09-26 | 1 | not yet added |
| [rapp-virtual-as400](repos/rapp-virtual-as400.md) | certified |  | CLEAN | 2b510ed | 2026-09-26 | 0 | not yet added |
| [rapp-vision-neighborhood](repos/rapp-vision-neighborhood.md) | certified |  | CLEAN | 2e6c62e | 2026-09-26 | 0 | not yet added |
| [rapp-vneighborhood](repos/rapp-vneighborhood.md) | certified |  | CLEAN | b727e96 | 2026-09-26 | 0 | not yet added |
| [rapp-work-cubbies](repos/rapp-work-cubbies.md) | certified |  | CLEAN | 6d90613 | 2026-09-26 | 0 | not yet added |
| [second-seat](repos/second-seat.md) | certified |  | CLEAN | 79f70a2 | 2026-09-26 | 0 | not yet added |
| [vneighborhood-design-studio](repos/vneighborhood-design-studio.md) | certified |  | CLEAN | 6d2770b | 2026-09-26 | 0 | not yet added |
| [vneighborhood-research-lab](repos/vneighborhood-research-lab.md) | certified |  | CLEAN | ba9413e | 2026-09-26 | 0 | not yet added |

### Organism & Platform (20)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [braintrust-template](repos/braintrust-template.md) | certified |  | CLEAN | 90779fb | 2026-09-26 | 1 | not yet added |
| [CommunityRAPP](repos/CommunityRAPP.md) | certified | v1.0.0 | CLEAN | 4931285 | 2026-09-26 | 9 | not yet added |
| [rapp-ai](repos/rapp-ai.md) | certified | v1.0.0 | CLEAN | eaee484 | 2026-09-26 | 7 | not yet added |
| [rapp-apex-dino](repos/rapp-apex-dino.md) | certified |  | CLEAN | f7c0c7c | 2026-09-26 | 0 | not yet added |
| [rapp-base](repos/rapp-base.md) | certified | v1.2.0 | CLEAN | 7e4b8a5 | 2026-09-26 | 0 | not yet added |
| [rapp-base-template](repos/rapp-base-template.md) | certified | v1.2.0 | CLEAN | 0242efb | 2026-09-26 | 0 | not yet added |
| [rapp-body](repos/rapp-body.md) | certified |  | COMPLIANT | afdefe2 | 2026-09-26 | 0 | not yet added |
| [rapp-brain](repos/rapp-brain.md) | certified |  | COMPLIANT | a8dc7bc | 2026-09-26 | 0 | not yet added |
| [rapp-cortex](repos/rapp-cortex.md) | certified |  | CLEAN | 63101ef | 2026-09-26 | 1 | not yet added |
| [rapp-dino](repos/rapp-dino.md) | certified |  | CLEAN | b598a82 | 2026-09-26 | 0 | not yet added |
| [rapp-hippocampus](repos/rapp-hippocampus.md) | certified |  | CLEAN | 45005c0 | 2026-09-26 | 1 | not yet added |
| [rapp-membrane](repos/rapp-membrane.md) | certified |  | CLEAN | 62da93d | 2026-09-26 | 0 | not yet added |
| [rapp-nervous-system](repos/rapp-nervous-system.md) | certified |  | CLEAN | 4068ccf | 2026-09-26 | 1 | not yet added |
| [rapp-organism](repos/rapp-organism.md) | certified |  | CLEAN | a1139d2 | 2026-09-26 | 206 | not yet added |
| [rapp-platform](repos/rapp-platform.md) | certified |  | CLEAN | d7f3f7d | 2026-09-26 | 1 | not yet added |
| [rapp-second-brain](repos/rapp-second-brain.md) | certified |  | CLEAN | c71de71 | 2026-09-26 | 6 | not yet added |
| [rapp-secondbrain](repos/rapp-secondbrain.md) | certified |  | CLEAN | 7846dfd | 2026-09-26 | 0 | not yet added |
| [rapp-spinal-cord](repos/rapp-spinal-cord.md) | certified |  | CLEAN | d6fcb97 | 2026-09-26 | 1 | not yet added |
| [RAPP_hippo](repos/RAPP_hippo.md) | certified | v1.0.0 | CLEAN | c55d623 | 2026-09-26 | 9 | not yet added |
| [RAPPsquared](repos/RAPPsquared.md) | certified |  | CLEAN | c99214c | 2026-09-26 | 0 | not yet added |

### DOGG & Commons (11)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [dogg](repos/dogg.md) | not yet |  | DRIFT | d72ba3a | 2026-09-26 | 0 | not yet added |
| [dogg-canon](repos/dogg-canon.md) | certified |  | COMPLIANT | ceb60aa | 2026-09-26 | 0 | not yet added |
| [dogg-markets](repos/dogg-markets.md) | certified |  | COMPLIANT | 0fd776d | 2026-09-26 | 0 | not yet added |
| [dogg-planet](repos/dogg-planet.md) | certified |  | COMPLIANT | 52574ef | 2026-09-26 | 0 | not yet added |
| [rapp-commons](repos/rapp-commons.md) | not yet | v1.0.0 | DRIFT | 560eacc | 2026-09-26 | 0 | not yet added |
| [rapp-dog-hub](repos/rapp-dog-hub.md) | certified |  | CLEAN | 7d72114 | 2026-09-26 | 0 | no README (skipped) |
| [rapp-frame-net](repos/rapp-frame-net.md) | certified |  | CLEAN | ad6f248 | 2026-09-26 | 0 | not yet added |
| [rapp-god-forum](repos/rapp-god-forum.md) | certified |  | CLEAN | 65f82e3 | 2026-09-26 | 0 | not yet added |
| [rapp-open](repos/rapp-open.md) | certified |  | CLEAN | 797f225 | 2026-09-26 | 0 | not yet added |
| [rappidverse-field](repos/rappidverse-field.md) | certified |  | CLEAN | 7c7e313 | 2026-09-26 | 0 | not yet added |
| [workroom](repos/workroom.md) | certified |  | CLEAN | 2815ba2 | 2026-09-26 | 1 | not yet added |

### Tools & Apps (30)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [copilot-harness-sdk](repos/copilot-harness-sdk.md) | certified |  | CLEAN | 8683889 | 2026-09-26 | 40 | not yet added |
| [dynamics365-business-process-api](repos/dynamics365-business-process-api.md) | certified |  | CLEAN | 0c04dc2 | 2026-09-26 | 1 | not yet added |
| [lisppy-shepherd](repos/lisppy-shepherd.md) | certified |  | CLEAN | b0d5a8d | 2026-09-26 | 1 | not yet added |
| [rapp-cli](repos/rapp-cli.md) | certified |  | CLEAN | df8cd16 | 2026-09-26 | 1 | not yet added |
| [rapp-copilot-in-chrome](repos/rapp-copilot-in-chrome.md) | certified |  | CLEAN | d95365b | 2026-09-26 | 0 | not yet added |
| [rapp-copilot-in-edge](repos/rapp-copilot-in-edge.md) | certified |  | CLEAN | ba7c262 | 2026-09-26 | 0 | not yet added |
| [rapp-crispy](repos/rapp-crispy.md) | not yet | v1.5.1 | DRIFT | 5fb6086 | 2026-09-26 | 0 | not yet added |
| [rapp-dataverse](repos/rapp-dataverse.md) | certified |  | CLEAN | bd843bb | 2026-09-26 | 0 | not yet added |
| [rapp-doorman](repos/rapp-doorman.md) | certified | v1.0.0 | CLEAN | bc9099e | 2026-09-26 | 0 | not yet added |
| [rapp-dynamic-workflows](repos/rapp-dynamic-workflows.md) | certified |  | CLEAN | b8b1de6 | 2026-09-26 | 8 | not yet added |
| [rapp-imessage-launchpad](repos/rapp-imessage-launchpad.md) | certified |  | CLEAN | f0b57ff | 2026-09-26 | 0 | not yet added |
| [rapp-keyring](repos/rapp-keyring.md) | certified | v0.1.0 | CLEAN | 8938672 | 2026-09-26 | 0 | not yet added |
| [rapp-local-install](repos/rapp-local-install.md) | certified |  | CLEAN | 8795f5b | 2026-09-26 | 0 | not yet added |
| [rapp-messaging](repos/rapp-messaging.md) | certified |  | CLEAN | 0586678 | 2026-09-26 | 0 | not yet added |
| [rapp-omarchy](repos/rapp-omarchy.md) | certified |  | CLEAN | 6a1c509 | 2026-09-26 | 2 | not yet added |
| [rapp-oneclick-deploy](repos/rapp-oneclick-deploy.md) | not yet |  | DRIFT | b42ea35 | 2026-09-26 | 2 | not yet added |
| [rapp-projects](repos/rapp-projects.md) | certified | v0.1.1 | CLEAN | 2b37502 | 2026-09-26 | 0 | not yet added |
| [rapp-recall](repos/rapp-recall.md) | certified | v0.1.0 | CLEAN | cfd5491 | 2026-09-26 | 30 | not yet added |
| [rapp-rewind](repos/rapp-rewind.md) | not yet | v1.2.1 | DRIFT | 0b9e65c | 2026-09-26 | 0 | not yet added |
| [rapp-sdk](repos/rapp-sdk.md) | certified | v0.2.0 | CLEAN | 402a7e0 | 2026-09-26 | 27 | not yet added |
| [rapp-shot](repos/rapp-shot.md) | not yet | v1.3.1 | DRIFT | e99ca10 | 2026-09-26 | 0 | not yet added |
| [rapp-static-apis](repos/rapp-static-apis.md) | certified | v1.0.0 | CLEAN | 63bea74 | 2026-09-26 | 0 | not yet added |
| [rapp-static-mcp](repos/rapp-static-mcp.md) | certified |  | CLEAN | 2f4efd2 | 2026-09-26 | 0 | not yet added |
| [rapp-tools](repos/rapp-tools.md) | certified | workspace-v0.1.0 | CLEAN | 5dd7a3d | 2026-09-26 | 0 | not yet added |
| [rapp-ultracode](repos/rapp-ultracode.md) | certified |  | CLEAN | f27181f | 2026-09-26 | 1 | not yet added |
| [rapp-voice](repos/rapp-voice.md) | not yet | v1.1.1 | DRIFT | 28e16c4 | 2026-09-26 | 0 | not yet added |
| [rapp-vui](repos/rapp-vui.md) | certified |  | CLEAN | d15a6f6 | 2026-09-26 | 0 | not yet added |
| [rapp-workspace-manager](repos/rapp-workspace-manager.md) | certified | v1.0.0 | COMPLIANT | c5a6574 | 2026-09-26 | 1 | not yet added |
| [RAPP_Desktop](repos/RAPP_Desktop.md) | certified | v1.0.0 | CLEAN | 0aea2ec | 2026-09-26 | 0 | not yet added |
| [RAPPAIClaudeCodePlayground](repos/RAPPAIClaudeCodePlayground.md) | certified |  | CLEAN | 4f5bde0 | 2026-09-26 | 0 | not yet added |

### Estate & Ops (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-bake-off](repos/rapp-bake-off.md) | certified |  | CLEAN | 318d632 | 2026-09-26 | 0 | not yet added |
| [rapp-bench](repos/rapp-bench.md) | certified |  | CLEAN | 1b157a8 | 2026-09-26 | 0 | not yet added |
| [rapp-distro](repos/rapp-distro.md) | certified |  | CLEAN | dad5879 | 2026-09-26 | 0 | not yet added |
| [rapp-estate](repos/rapp-estate.md) | certified |  | CLEAN | acc17dc | 2026-09-26 | 0 | no README (skipped) |
| [rapp-infrastructure-city](repos/rapp-infrastructure-city.md) | certified |  | CLEAN | 9b8f467 | 2026-09-26 | 0 | not yet added |
| [rapp-metrics](repos/rapp-metrics.md) | certified |  | CLEAN | 2940500 | 2026-09-26 | 0 | not yet added |
| [rapp-monorepo](repos/rapp-monorepo.md) | not yet |  | DRIFT | 81cc7de | 2026-09-26 | 4329 | not yet added |
| [rapp-parity](repos/rapp-parity.md) | certified |  | COMPLIANT | cb5ce3d | 2026-09-26 | 0 | not yet added |
| [rapp-personpower](repos/rapp-personpower.md) | certified |  | CLEAN | fcd4b9e | 2026-09-26 | 0 | not yet added |
| [rapp-postflight](repos/rapp-postflight.md) | certified |  | CLEAN | 4d2ef44 | 2026-09-26 | 0 | not yet added |
| [rapp-refresh](repos/rapp-refresh.md) | certified | v1.0.0 | CLEAN | 84cc9bb | 2026-09-26 | 0 | not yet added |
| [rapp-roadside](repos/rapp-roadside.md) | not yet | v1.0.0 | DRIFT | 8082439 | 2026-09-26 | 0 | not yet added |
| [rapp-rock-tumbler](repos/rapp-rock-tumbler.md) | certified |  | CLEAN | cb3dd66 | 2026-09-26 | 0 | not yet added |
| [rapp-sentinel](repos/rapp-sentinel.md) | certified |  | CLEAN | eebfa42 | 2026-09-26 | 1 | not yet added |
| [rapp-support](repos/rapp-support.md) | certified |  | CLEAN | 533059c | 2026-09-26 | 0 | not yet added |
| [rapp-tower](repos/rapp-tower.md) | certified |  | CLEAN | ad7192a | 2026-09-26 | 4 | not yet added |
| [rapp-version-selector](repos/rapp-version-selector.md) | certified |  | CLEAN | 79a007f | 2026-09-26 | 9 | not yet added |
| [sentinel](repos/sentinel.md) | certified |  | CLEAN | d62e7a6 | 2026-09-26 | 0 | not yet added |

### Worlds & Play (26)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [ant-farm](repos/ant-farm.md) | certified |  | COMPLIANT | afe687c | 2026-09-26 | 1 | not yet added |
| [double-jump](repos/double-jump.md) | certified | v0.1.0 | CLEAN | 5097b61 | 2026-09-26 | 17 | not yet added |
| [leviathan](repos/leviathan.md) | certified |  | CLEAN | 42d02ad | 2026-09-26 | 0 | not yet added |
| [racon](repos/racon.md) | certified | v1.0.0 | CLEAN | 2e709f5 | 2026-09-26 | 0 | not yet added |
| [RaGo](repos/RaGo.md) | certified | v2.1.0 | CLEAN | 426239e | 2026-09-26 | 0 | not yet added |
| [rapp-basket](repos/rapp-basket.md) | certified |  | CLEAN | 3636fb9 | 2026-09-26 | 0 | not yet added |
| [rapp-burrow](repos/rapp-burrow.md) | certified |  | CLEAN | 36f57fa | 2026-09-26 | 0 | not yet added |
| [rapp-coop](repos/rapp-coop.md) | certified |  | CLEAN | d718932 | 2026-09-26 | 0 | not yet added |
| [rapp-eternity](repos/rapp-eternity.md) | certified |  | CLEAN | 17bb6d2 | 2026-09-26 | 0 | not yet added |
| [rapp-fps](repos/rapp-fps.md) | certified |  | CLEAN | 9eacce9 | 2026-09-26 | 0 | no README (skipped) |
| [rapp-heir](repos/rapp-heir.md) | certified |  | CLEAN | 58362a4 | 2026-09-26 | 3 | not yet added |
| [rapp-holo](repos/rapp-holo.md) | certified |  | CLEAN | ff29652 | 2026-09-26 | 0 | not yet added |
| [rapp-hologram](repos/rapp-hologram.md) | certified | v1.0.0 | CLEAN | 4c98188 | 2026-09-26 | 0 | not yet added |
| [rapp-lantern](repos/rapp-lantern.md) | not yet |  | DRIFT | 1af70be | 2026-09-26 | 0 | not yet added |
| [rapp-moment](repos/rapp-moment.md) | certified | v1.1.0 | CLEAN | 229db18 | 2026-09-26 | 0 | not yet added |
| [rapp-moonshots](repos/rapp-moonshots.md) | certified |  | CLEAN | 789f933 | 2026-09-26 | 3 | not yet added |
| [rapp-pets](repos/rapp-pets.md) | certified |  | CLEAN | 2ab70ab | 2026-09-26 | 0 | not yet added |
| [rapp-play-pokemon](repos/rapp-play-pokemon.md) | certified |  | CLEAN | 10a2c56 | 2026-09-26 | 1 | not yet added |
| [rapp-snap](repos/rapp-snap.md) | certified |  | CLEAN | 9fed5a9 | 2026-09-26 | 0 | not yet added |
| [rapp-zoo-v2](repos/rapp-zoo-v2.md) | not yet | v0.1.0 | DRIFT | b394aa5 | 2026-09-26 | 0 | not yet added |
| [rapp_orion](repos/rapp_orion.md) | certified |  | CLEAN | 7ba9bd9 | 2026-09-26 | 8 | not yet added |
| [rappid](repos/rappid.md) | not yet |  | DRIFT | c988d79 | 2026-09-26 | 0 | not yet added |
| [rio](repos/rio.md) | not yet | v1.0.0 | DRIFT | 1062e28 | 2026-09-26 | 0 | not yet added |
| [rionet](repos/rionet.md) | certified |  | CLEAN | ee9ee28 | 2026-09-26 | 0 | not yet added |
| [sim-art-collective](repos/sim-art-collective.md) | certified |  | COMPLIANT | fb62888 | 2026-09-26 | 1 | not yet added |
| [the-coliseum](repos/the-coliseum.md) | certified |  | CLEAN | aa9c429 | 2026-09-26 | 0 | not yet added |
