# RAPP/1 portfolio

Every public RAPP repo, each with an **earned** RAPP/1 status. RAPP/1 is the LTS version for the whole network: a repo is certified when rapp-1's own checker passes it at a recorded commit.

**Notices:** 102 active, 0 deprecated, 0 superseded, 218 archived, 3 left the network. The [notices page](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) lists every repo that is not active or has left, and what changed in this version; [how to deprecate, move or version a repo](https://kody-w.github.io/rapp-hive-public/portfolio/lifecycle.html).

| Wave | certified | not yet | unchecked | total |
|---|---|---|---|---|
| 1: the RAPP/1 stack | 14 | 1 | 0 | 15 |
| 2: the rest of the RAPP family | 287 | 17 | 1 | 305 |
| **all** | 301 | 18 | 1 | 320 |

- **certified**: [`rapp_check.py` at `591e014`](https://github.com/kody-w/rapp-1/blob/591e014ad39e223b00ab343ae26e5d9a867ebeee/rapp_check.py) says COMPLIANT or CLEAN at the recorded commit.
- **not yet**: drift or unverified; each file says why.
- **unchecked**: it could not be cloned or checked (for example, an empty repository); its file says why.
- **rapp1-lts**: the repo has a long-term-support pin (the network's built-in known pins, until the estate publishes its LTS pins; the Version column shows `LTS` and its label); **newest**: no pin, so its newest commit is the one in use. Open questions about a repo's channel are on the [channel notices](https://kody-w.github.io/rapp-hive-public/portfolio/channel-notices.html) page; they change no channel. **deprecated**, **superseded** and **archived** come first in the Status column; each repo's file says since when and why.

Each repo's README gets one marked line (today, of 320: 279 carry it, 4 in an open pull request, 14 merged, awaiting the next sweep, 2 held, 18 waiting for their pull request (wave 2 waits for the owner's approval), 2 without a README (skipped), 1 not checked (they could not be cloned)): its badge (served from this folder by GitHub Pages, so the URL never changes) and a link to [Start here](https://github.com/kody-w/rapp-installer#start-here) for anyone without a Brainstem yet. "experimental" mentions are tracked here as a metric; they are not a gate yet.

**Member cards:** 294 of 320 repos carry their card in the RAPP Hive (`.rapp/member.md`, the repo's own side of its pointer in `members/`); the file of each repo that has one links it.

A Hive holds only markdown, so each badge is `badges/<repo>.svg.md`: its front matter tells GitHub Pages to serve it as `https://kody-w.github.io/rapp-hive-public/portfolio/badges/<repo>.svg` (image/svg+xml).

## The map

**[Subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html)** (zoomable; click a station for its portfolio file and its repo) · [poster PDF](https://kody-w.github.io/rapp-hive-public/portfolio/subway.pdf) · [SVG](https://kody-w.github.io/rapp-hive-public/portfolio/subway.svg)

Lines are the families below; stations are repos, filled by status (hollow when deprecated, superseded or archived); the RAPP/1 Core line runs in layer order and ends at `rapp-installer`, the Start here terminal. It is drawn from these files by the `rapp1_network` package (its release copy is in [`tools/`](https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/tools)), and the links between repos come from each file's `links_to`.

**Version 11**, crawled 2026-10-08 23:13 UTC. Every crawl is one RAPP/1 frame, a `body.pulse` on the network's body stream `rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def`. The [timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html) lists every version with its pulse hashes and what changed, and each version's maps stay under `versions/`.

| Line | Stations | certified | not yet | unchecked |
|---|---|---|---|---|
| [RAPP/1 Core](lines/rapp1-core.md) | 7 | 7 | 0 | 0 |
| [Hive](lines/hive.md) | 9 | 8 | 1 | 0 |
| [Agents (RAR)](lines/agents-rar.md) | 21 | 19 | 2 | 0 |
| [Brainstem](lines/brainstem.md) | 21 | 19 | 1 | 1 |
| [Brainstem Connect](lines/connect.md) | 16 | 16 | 0 | 0 |
| [Learn & Docs](lines/learn.md) | 18 | 17 | 1 | 0 |
| [Release Channels](lines/release.md) | 18 | 18 | 0 | 0 |
| [OpenRappter](lines/openrappter.md) | 8 | 8 | 0 | 0 |
| [Rappterbook](lines/rappterbook.md) | 23 | 22 | 1 | 0 |
| [Rappterverse](lines/rappterverse.md) | 11 | 9 | 2 | 0 |
| [Rappvision](lines/rappvision.md) | 23 | 23 | 0 | 0 |
| [Twins](lines/twins.md) | 15 | 15 | 0 | 0 |
| [Neighborhoods](lines/neighborhoods.md) | 21 | 21 | 0 | 0 |
| [Organism & Platform](lines/organism.md) | 20 | 20 | 0 | 0 |
| [DOGG & Commons](lines/dogg.md) | 13 | 11 | 2 | 0 |
| [Tools & Apps](lines/tools.md) | 30 | 26 | 4 | 0 |
| [Estate & Ops](lines/estate.md) | 18 | 16 | 2 | 0 |
| [Worlds & Play](lines/worlds.md) | 26 | 24 | 2 | 0 |
| [RAPP Projects](lines/projects.md) | 2 | 2 | 0 | 0 |

## Wave 1: the RAPP/1 stack (15)

### RAPP/1 Core (7)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [lisppy](repos/lisppy.md) | **archived** · certified |  | CLEAN | 138c18b | 2026-10-08 | 1 | present |
| [RAPP](repos/RAPP.md) | certified | v1.0.0 | COMPLIANT | 30b54e8 | 2026-10-08 | 196 | present |
| [rapp-1](repos/rapp-1.md) | certified | LTS 591e014 | COMPLIANT | 74edecc | 2026-10-08 | 0 | present |
| [rapp-drift-lint](repos/rapp-drift-lint.md) | **archived** · certified |  | CLEAN | 31aefc5 | 2026-10-08 | 0 | present |
| [rapp-installer](repos/rapp-installer.md) | certified | v1.0.0 · LTS brainstem-v0.6.9 | CLEAN | 0e43ee5 | 2026-10-08 | 11 | held: the owner holds the grail repo (PR #48 stays open) |
| [rapp-work](repos/rapp-work.md) | certified | LTS 29ead23 | COMPLIANT | 4d1a527 | 2026-10-08 | 0 | present |
| [rapp-workspace](repos/rapp-workspace.md) | **archived** · certified |  | COMPLIANT | 93b87bc | 2026-10-08 | 50 | held: waiting on G24 (front door editable) |

### Hive (7)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-hub](repos/hive-hub.md) | **archived** · certified |  | CLEAN | 0968590 | 2026-10-08 | 5 | present |
| [hive-hub-join](repos/hive-hub-join.md) | **archived** · certified |  | CLEAN | 64374f0 | 2026-10-08 | 0 | present |
| [hive-hub-mcp](repos/hive-hub-mcp.md) | **archived** · certified |  | CLEAN | 0a12a51 | 2026-10-08 | 0 | present |
| [rapp-hive-hub](repos/rapp-hive-hub.md) | **archived** · certified |  | COMPLIANT | 901d633 | 2026-10-08 | 7 | present |
| [rapp-hive-hub-join](repos/rapp-hive-hub-join.md) | **archived** · certified |  | CLEAN | a0943d6 | 2026-10-08 | 0 | present |
| [rapp-hive-public](repos/rapp-hive-public.md) | certified |  | CLEAN | 0824a30 | 2026-10-08 | 41 | present |
| [rapp-model-hive](repos/rapp-model-hive.md) | **archived** · not yet |  | DRIFT | d4a9479 | 2026-10-08 | 18 | present |

### Agents (RAR) (1)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [RAR](repos/RAR.md) | certified | v1.0.0 | COMPLIANT | 74d722c | 2026-10-08 | 160 | present |

## Wave 2: the rest of the RAPP family (305)

### Hive (2)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [hive-showcase](repos/hive-showcase.md) | **archived** · certified |  | CLEAN | 3a4c8b1 | 2026-10-08 | 7 | present |
| [rapp-hive-app](repos/rapp-hive-app.md) | **archived** · certified |  | CLEAN | c2a5c9b | 2026-10-08 | 0 | present |

### Agents (RAR) (20)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [AI-Agent-Templates-Pilot](repos/AI-Agent-Templates-Pilot.md) | **archived** · certified |  | CLEAN | 588ab9b | 2026-10-08 | 0 | present |
| [cowork-cookbook-rapp](repos/cowork-cookbook-rapp.md) | **archived** · certified | v1.0.0 | COMPLIANT | 37556e6 | 2026-10-08 | 0 | present |
| [obsidian-binder](repos/obsidian-binder.md) | **archived** · certified |  | CLEAN | 8bcc9e8 | 2026-10-08 | 0 | present |
| [rapp-carts](repos/rapp-carts.md) | **archived** · certified | v1.0.0 | CLEAN | b1c1296 | 2026-10-08 | 0 | present |
| [rapp-claude-skills](repos/rapp-claude-skills.md) | **archived** · certified | v1.0.0 | CLEAN | f972b86 | 2026-10-08 | 0 | present |
| [rapp-egg-hub](repos/rapp-egg-hub.md) | **archived** · not yet | v1.0.0 | DRIFT | 6bf1759 | 2026-10-08 | 11 | present |
| [rapp-hatchery](repos/rapp-hatchery.md) | **archived** · certified |  | CLEAN | 6deabe0 | 2026-10-08 | 4 | present |
| [rapp-leviathan-hub](repos/rapp-leviathan-hub.md) | **archived** · certified |  | COMPLIANT | 11fc0f4 | 2026-10-08 | 0 | present |
| [rapp-packs](repos/rapp-packs.md) | **archived** · certified |  | CLEAN | a2d60e5 | 2026-10-08 | 0 | present |
| [rapp-sentinel-hub](repos/rapp-sentinel-hub.md) | **archived** · certified |  | CLEAN | 6529b29 | 2026-10-08 | 0 | present |
| [rapp-skill](repos/rapp-skill.md) | **archived** · certified |  | CLEAN | aa225cc | 2026-10-08 | 0 | present |
| [rapp-skills](repos/rapp-skills.md) | certified |  | CLEAN | df63393 | 2026-10-08 | 0 | present |
| [rapp-stack-cubby](repos/rapp-stack-cubby.md) | **archived** · certified | v0.1.0rc11 | COMPLIANT | 1fee389 | 2026-10-08 | 13 | not yet added |
| [rapp-store-archive](repos/rapp-store-archive.md) | **archived** · certified |  | CLEAN | 85c2259 | 2026-10-08 | 0 | present |
| [rapp-toaster](repos/rapp-toaster.md) | **archived** · certified |  | CLEAN | bf5dc8a | 2026-10-08 | 0 | present |
| [RAPP_Hub](repos/RAPP_Hub.md) | **archived** · certified |  | CLEAN | 1422120 | 2026-10-08 | 0 | present |
| [RAPP_Sense_Store](repos/RAPP_Sense_Store.md) | certified |  | CLEAN | 563552f | 2026-10-08 | 0 | present |
| [RAPP_Store](repos/RAPP_Store.md) | not yet | v1.0.0 | DRIFT | f81d84c | 2026-10-08 | 76 | PR open |
| [RAPPcards](repos/RAPPcards.md) | certified |  | CLEAN | 045026a | 2026-10-08 | 2 | present |
| [red-binder](repos/red-binder.md) | **archived** · certified |  | CLEAN | c64d6d8 | 2026-10-08 | 10 | present |

### Brainstem (21)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-agent](repos/brainstem-agent.md) | **archived** · certified |  | CLEAN | 06df496 | 2026-10-08 | 59 | present |
| [brainstem-copilot](repos/brainstem-copilot.md) | **archived** · certified |  | CLEAN | 22c256d | 2026-10-08 | 4 | present |
| [brainstem-distro](repos/brainstem-distro.md) | certified |  | CLEAN | 636173f | 2026-10-08 | 8 | not yet added |
| [brainstem-harness](repos/brainstem-harness.md) | **archived** · certified |  | CLEAN | 3eed344 | 2026-10-08 | 0 | present |
| [brainstem-mcp](repos/brainstem-mcp.md) | certified |  | CLEAN | fb50745 | 2026-10-08 | 0 | not yet added |
| [chat](repos/chat.md) | **archived** · certified |  | CLEAN | d6677d1 | 2026-10-08 | 0 | present |
| [ez-rapp](repos/ez-rapp.md) | **archived** · certified | v0.1.3 | CLEAN | 20a2ff4 | 2026-10-08 | 0 | present |
| [rapp-brainfreeze](repos/rapp-brainfreeze.md) | certified |  | CLEAN | 3ed8ee7 | 2026-10-08 | 2 | present |
| [rapp-brainfreeze-studio](repos/rapp-brainfreeze-studio.md) | certified |  | CLEAN | 9e621b4 | 2026-10-08 | 4 | present |
| [rapp-brainstem](repos/rapp-brainstem.md) | **archived** · certified | v0.2.1 | COMPLIANT | 4154e95 | 2026-10-08 | 3 | present |
| [rapp-brainstem-foundation](repos/rapp-brainstem-foundation.md) | unchecked |  |  |  | 2026-10-08 |  | none (not checked) |
| [rapp-brainstem-frontier-template](repos/rapp-brainstem-frontier-template.md) | certified |  | CLEAN | f3510d7 | 2026-10-08 | 0 | present |
| [rapp-brainstem-sdk](repos/rapp-brainstem-sdk.md) | certified | v1.0.0 | CLEAN | 8175627 | 2026-10-08 | 0 | present |
| [rapp-light](repos/rapp-light.md) | **archived** · certified |  | CLEAN | d051bb1 | 2026-10-08 | 5 | present |
| [rapp-petri](repos/rapp-petri.md) | **archived** · certified |  | CLEAN | c464e8e | 2026-10-08 | 0 | present |
| [rapp-quests](repos/rapp-quests.md) | **archived** · certified |  | CLEAN | 602eddb | 2026-10-08 | 0 | present |
| [rapp-static-brainstem](repos/rapp-static-brainstem.md) | **archived** · certified | v1.2.0 | CLEAN | b6b416a | 2026-10-08 | 1 | present |
| [rapp-vscode-extension](repos/rapp-vscode-extension.md) | **archived** · certified | v1.0.0 | CLEAN | 616046e | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [skillstem](repos/skillstem.md) | **archived** · certified |  | CLEAN | dd9ff09 | 2026-10-08 | 0 | present |
| [stemcell](repos/stemcell.md) | **archived** · certified |  | CLEAN | 43fa960 | 2026-10-08 | 6 | present |
| [vbrainstem](repos/vbrainstem.md) | not yet |  | DRIFT | 8c3d1fa | 2026-10-08 | 2 | present |

### Brainstem Connect (16)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-brainstem-claude](repos/rapp-brainstem-claude.md) | certified |  | CLEAN | 209a6ae | 2026-10-08 | 0 | present |
| [rapp-brainstem-claude-desktop](repos/rapp-brainstem-claude-desktop.md) | certified |  | CLEAN | 5603dc2 | 2026-10-08 | 0 | present |
| [rapp-brainstem-cline](repos/rapp-brainstem-cline.md) | certified |  | CLEAN | 0f38868 | 2026-10-08 | 0 | present |
| [rapp-brainstem-codex](repos/rapp-brainstem-codex.md) | certified |  | CLEAN | 7fdf62c | 2026-10-08 | 0 | present |
| [rapp-brainstem-copilot](repos/rapp-brainstem-copilot.md) | certified |  | CLEAN | 3726803 | 2026-10-08 | 0 | present |
| [rapp-brainstem-cursor](repos/rapp-brainstem-cursor.md) | certified |  | CLEAN | 3cc91ed | 2026-10-08 | 0 | present |
| [rapp-brainstem-gemini](repos/rapp-brainstem-gemini.md) | certified |  | CLEAN | c447c6e | 2026-10-08 | 0 | present |
| [rapp-brainstem-goose](repos/rapp-brainstem-goose.md) | certified |  | CLEAN | d559eb7 | 2026-10-08 | 0 | present |
| [rapp-brainstem-kiro](repos/rapp-brainstem-kiro.md) | certified |  | CLEAN | 22b9731 | 2026-10-08 | 0 | present |
| [rapp-brainstem-mcp](repos/rapp-brainstem-mcp.md) | certified |  | CLEAN | 7a9ae5d | 2026-10-08 | 0 | present |
| [rapp-brainstem-opencode](repos/rapp-brainstem-opencode.md) | certified |  | CLEAN | f901852 | 2026-10-08 | 0 | present |
| [rapp-brainstem-plugin](repos/rapp-brainstem-plugin.md) | certified |  | CLEAN | 4134864 | 2026-10-08 | 0 | present |
| [rapp-brainstem-vscode](repos/rapp-brainstem-vscode.md) | certified |  | CLEAN | 33bebac | 2026-10-08 | 0 | present |
| [rapp-brainstem-windsurf](repos/rapp-brainstem-windsurf.md) | certified |  | CLEAN | be2d0e9 | 2026-10-08 | 0 | present |
| [rapp-mcp](repos/rapp-mcp.md) | certified | LTS cd22b1e | CLEAN | d403423 | 2026-10-08 | 2 | present |
| [scout-brainstem-bootstrap](repos/scout-brainstem-bootstrap.md) | certified |  | CLEAN | ab5e16e | 2026-10-08 | 48 | present |

### Learn & Docs (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [brainstem-bootcamp](repos/brainstem-bootcamp.md) | **archived** · certified |  | CLEAN | 31f366d | 2026-10-08 | 0 | present |
| [dimensional-bottles](repos/dimensional-bottles.md) | **archived** · certified |  | COMPLIANT | 7890381 | 2026-10-08 | 0 | present |
| [learn-brainstem](repos/learn-brainstem.md) | **archived** · certified |  | CLEAN | 2bafbde | 2026-10-08 | 0 | present |
| [RAPP-Bible](repos/RAPP-Bible.md) | certified |  | CLEAN | 093ae84 | 2026-10-08 | 17 | present |
| [rapp-brainstem-walkthrough](repos/rapp-brainstem-walkthrough.md) | certified | v0.6.16 | CLEAN | d310e4b | 2026-10-08 | 4 | present |
| [rapp-demos](repos/rapp-demos.md) | certified | v1.0.0 | CLEAN | cc9cfb1 | 2026-10-08 | 0 | present |
| [rapp-docs](repos/rapp-docs.md) | **archived** · certified |  | CLEAN | e7f181c | 2026-10-08 | 3 | present |
| [rapp-education-shorts](repos/rapp-education-shorts.md) | **archived** · certified |  | CLEAN | 67b1987 | 2026-10-08 | 0 | present |
| [rapp-lab-kit](repos/rapp-lab-kit.md) | **archived** · certified |  | CLEAN | fd97886 | 2026-10-08 | 0 | present |
| [rapp-map](repos/rapp-map.md) | not yet | v1.0.0 · LTS 4c8ba6b | DRIFT | 48b6c38 | 2026-10-08 | 54 | present |
| [rapp-mapp](repos/rapp-mapp.md) | **archived** · certified |  | CLEAN | e564ef2 | 2026-10-08 | 0 | present |
| [rapp-mission](repos/rapp-mission.md) | **archived** · certified |  | CLEAN | 0c75b85 | 2026-10-08 | 0 | present |
| [rapp-roadmap](repos/rapp-roadmap.md) | **archived** · certified |  | CLEAN | a00cc3f | 2026-10-08 | 1 | present |
| [rapp-specs](repos/rapp-specs.md) | certified |  | COMPLIANT | 94d5f41 | 2026-10-08 | 0 | present |
| [rapp-spine](repos/rapp-spine.md) | **archived** · certified |  | CLEAN | e63ecbd | 2026-10-08 | 0 | present |
| [rapp-wiki-observatory](repos/rapp-wiki-observatory.md) | **archived** · certified |  | CLEAN | ebfc19f | 2026-10-08 | 0 | present |
| [rapp_docs](repos/rapp_docs.md) | **archived** · certified |  | CLEAN | 99b147e | 2026-10-08 | 0 | present |
| [rappdex](repos/rappdex.md) | **archived** · certified |  | CLEAN | 413f544 | 2026-10-08 | 0 | present |

### Release Channels (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [openrappter-alpha](repos/openrappter-alpha.md) | certified |  | CLEAN | 235e93e | 2026-10-08 | 0 | not yet added |
| [openrappter-beta](repos/openrappter-beta.md) | certified |  | CLEAN | c29c6d4 | 2026-10-08 | 0 | not yet added |
| [openrappter-canary](repos/openrappter-canary.md) | certified |  | CLEAN | a86599c | 2026-10-08 | 0 | not yet added |
| [openrappter-nightly](repos/openrappter-nightly.md) | certified |  | CLEAN | ea34fa6 | 2026-10-08 | 0 | not yet added |
| [openrappter-release-train](repos/openrappter-release-train.md) | certified |  | CLEAN | 9389280 | 2026-10-08 | 0 | present |
| [rapp-alpha](repos/rapp-alpha.md) | certified |  | CLEAN | 63dcd39 | 2026-10-08 | 11 | not yet added |
| [rapp-beta](repos/rapp-beta.md) | certified |  | CLEAN | 20b4ec5 | 2026-10-08 | 11 | not yet added |
| [rapp-brainstem-beta](repos/rapp-brainstem-beta.md) | certified |  | CLEAN | cd55de1 | 2026-10-08 | 0 | present |
| [rapp-canary](repos/rapp-canary.md) | certified |  | COMPLIANT | deedfff | 2026-10-08 | 20 | not yet added |
| [rapp-flight](repos/rapp-flight.md) | **archived** · certified |  | CLEAN | 8b36b6b | 2026-10-08 | 2 | present |
| [rapp-flight-deck](repos/rapp-flight-deck.md) | certified |  | CLEAN | ac6ff67 | 2026-10-08 | 1 | present |
| [rapp-installer-canary](repos/rapp-installer-canary.md) | **archived** · certified |  | CLEAN | 4c28726 | 2026-10-08 | 7 | not yet added |
| [rapp-installer-dev](repos/rapp-installer-dev.md) | **archived** · certified |  | CLEAN | 34d37e8 | 2026-10-08 | 8 | not yet added |
| [rapp-mirror-releases](repos/rapp-mirror-releases.md) | certified | v0.2.0 | CLEAN | 94d4cd5 | 2026-10-08 | 0 | present |
| [rapp-nightly](repos/rapp-nightly.md) | certified |  | CLEAN | 62ccf49 | 2026-10-08 | 11 | not yet added |
| [rapp-release-train](repos/rapp-release-train.md) | certified |  | CLEAN | aa9115c | 2026-10-08 | 6 | not yet added |
| [rapp-rings](repos/rapp-rings.md) | certified |  | CLEAN | 4750f73 | 2026-10-08 | 1 | present |
| [rapp-train](repos/rapp-train.md) | certified |  | CLEAN | d788f28 | 2026-10-08 | 0 | present |

### OpenRappter (8)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [homebrew-tap](repos/homebrew-tap.md) | **archived** · certified |  | CLEAN | 9c132ab | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [openrappter](repos/openrappter.md) | certified | v1.13.1-bar | CLEAN | 07c9af3 | 2026-10-08 | 1 | PR open |
| [rappter-cli](repos/rappter-cli.md) | **archived** · certified |  | CLEAN | 0549ac4 | 2026-10-08 | 0 | present |
| [rappter-plays-palworld](repos/rappter-plays-palworld.md) | **archived** · certified |  | CLEAN | e4cb72b | 2026-10-08 | 0 | present |
| [rappter-plays-pokemon](repos/rappter-plays-pokemon.md) | **archived** · certified |  | CLEAN | a613b28 | 2026-10-08 | 4 | present |
| [rappter-prompts](repos/rappter-prompts.md) | certified |  | CLEAN | 9c5fec3 | 2026-10-08 | 0 | present |
| [rappter-vui](repos/rappter-vui.md) | **archived** · certified |  | CLEAN | a5c049e | 2026-10-08 | 0 | present |
| [rappterhub](repos/rappterhub.md) | **archived** · certified |  | CLEAN | 5bd4c39 | 2026-10-08 | 0 | present |

### Rappterbook (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [mars-barn](repos/mars-barn.md) | certified |  | CLEAN | b7f4c59 | 2026-10-08 | 14 | present |
| [rappbook-admin](repos/rappbook-admin.md) | certified |  | CLEAN | 13fe250 | 2026-10-08 | 0 | present |
| [rappterbook](repos/rappterbook.md) | not yet | v1.0.0 | DRIFT | f15d757 | 2026-10-08 | 4530 | present |
| [rappterbook-agent](repos/rappterbook-agent.md) | certified |  | CLEAN | 01ec54c | 2026-10-08 | 2 | present |
| [rappterbook-agent-dna](repos/rappterbook-agent-dna.md) | certified |  | CLEAN | 16a5ddb | 2026-10-08 | 0 | present |
| [rappterbook-agent-exchange](repos/rappterbook-agent-exchange.md) | certified |  | CLEAN | debfdaf | 2026-10-08 | 4 | present |
| [rappterbook-api](repos/rappterbook-api.md) | certified |  | CLEAN | 8c50370 | 2026-10-08 | 1 | present |
| [rappterbook-autopilot](repos/rappterbook-autopilot.md) | certified |  | CLEAN | fac2ad1 | 2026-10-08 | 0 | present |
| [rappterbook-commons](repos/rappterbook-commons.md) | certified |  | CLEAN | 2aba29e | 2026-10-08 | 0 | present |
| [rappterbook-engine-test](repos/rappterbook-engine-test.md) | certified |  | CLEAN | f462665 | 2026-10-08 | 230 | merged, awaiting the next sweep |
| [rappterbook-first-bond](repos/rappterbook-first-bond.md) | certified |  | CLEAN | 7187d0c | 2026-10-08 | 0 | present |
| [rappterbook-governance](repos/rappterbook-governance.md) | certified |  | CLEAN | 1cb2f03 | 2026-10-08 | 0 | present |
| [rappterbook-impossible-product](repos/rappterbook-impossible-product.md) | certified | frame-03.2 | CLEAN | afabf42 | 2026-10-08 | 0 | present |
| [rappterbook-join](repos/rappterbook-join.md) | certified |  | CLEAN | 0292f41 | 2026-10-08 | 0 | present |
| [rappterbook-knowledge-graph](repos/rappterbook-knowledge-graph.md) | certified |  | CLEAN | 016fb61 | 2026-10-08 | 0 | present |
| [rappterbook-market-maker](repos/rappterbook-market-maker.md) | certified |  | CLEAN | a2f3a5d | 2026-10-08 | 0 | present |
| [rappterbook-mars-barn](repos/rappterbook-mars-barn.md) | certified |  | CLEAN | f654201 | 2026-10-08 | 13 | present |
| [rappterbook-phantom](repos/rappterbook-phantom.md) | certified |  | CLEAN | e176f45 | 2026-10-08 | 0 | present |
| [rappterbook-seedmaker](repos/rappterbook-seedmaker.md) | certified |  | CLEAN | 68bc493 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rappterbook-social-graph](repos/rappterbook-social-graph.md) | certified |  | CLEAN | 77b8b1e | 2026-10-08 | 0 | present |
| [rappterbook-v2](repos/rappterbook-v2.md) | certified |  | CLEAN | 37087c5 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rappterbook-v2-state](repos/rappterbook-v2-state.md) | certified |  | CLEAN | 5e1b4e2 | 2026-10-08 | 32 | present |
| [rappterbook-vm](repos/rappterbook-vm.md) | certified |  | CLEAN | 5642775 | 2026-10-08 | 4 | present |

### Rappterverse (11)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [CrystalRAPP](repos/CrystalRAPP.md) | **archived** · certified |  | CLEAN | e2747c0 | 2026-10-08 | 1 | merged, awaiting the next sweep |
| [rappter-distro](repos/rappter-distro.md) | **archived** · not yet |  | DRIFT | ecca8a4 | 2026-10-08 | 29 | present |
| [rappter-factory](repos/rappter-factory.md) | **archived** · certified |  | CLEAN | 9505657 | 2026-10-08 | 2 | present |
| [rappter-mmo](repos/rappter-mmo.md) | **archived** · certified |  | CLEAN | 5d45256 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rappter-site](repos/rappter-site.md) | **archived** · not yet |  | DRIFT | c0b7950 | 2026-10-08 | 1 | merged, awaiting the next sweep |
| [rappterbox](repos/rappterbox.md) | **archived** · certified | v0.12.2 | COMPLIANT | 5822206 | 2026-10-08 | 24 | present |
| [RappterNest](repos/RappterNest.md) | **archived** · certified |  | CLEAN | 8da2b07 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rappterverse](repos/rappterverse.md) | certified |  | CLEAN | 934abec | 2026-10-08 | 1 | merged, awaiting the next sweep |
| [rappterverse-data](repos/rappterverse-data.md) | **archived** · certified |  | CLEAN | 886c981 | 2026-10-08 | 0 | present |
| [ShadowRAPP](repos/ShadowRAPP.md) | **archived** · certified |  | CLEAN | f326698 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [VoidRAPP](repos/VoidRAPP.md) | **archived** · certified |  | CLEAN | 9634ccd | 2026-10-08 | 0 | merged, awaiting the next sweep |

### Rappvision (23)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-remix](repos/rapp-remix.md) | **archived** · certified |  | CLEAN | 50ff42c | 2026-10-08 | 0 | present |
| [rapp-video](repos/rapp-video.md) | **archived** · certified |  | CLEAN | be10ac8 | 2026-10-08 | 6 | present |
| [rapp-vision](repos/rapp-vision.md) | certified | oil-field-season-v1.0.0 | CLEAN | 419ead6 | 2026-10-08 | 0 | PR open |
| [rappvision-after-midnight-maps](repos/rappvision-after-midnight-maps.md) | **archived** · certified |  | CLEAN | aa41001 | 2026-10-08 | 0 | present |
| [rappvision-brainstem-notes](repos/rappvision-brainstem-notes.md) | **archived** · certified |  | CLEAN | 90e7e1f | 2026-10-08 | 0 | present |
| [rappvision-creature-office-hours](repos/rappvision-creature-office-hours.md) | **archived** · certified |  | CLEAN | 511f34f | 2026-10-08 | 0 | present |
| [rappvision-field-notes](repos/rappvision-field-notes.md) | **archived** · certified |  | CLEAN | 888fdd2 | 2026-10-08 | 0 | present |
| [rappvision-kitchen-table-physics](repos/rappvision-kitchen-table-physics.md) | **archived** · certified |  | CLEAN | 47efebd | 2026-10-08 | 0 | present |
| [rappvision-new-way-of-work](repos/rappvision-new-way-of-work.md) | **archived** · certified |  | CLEAN | 36aa36a | 2026-10-08 | 0 | no README (skipped) |
| [rappvision-null-arcade](repos/rappvision-null-arcade.md) | **archived** · certified |  | CLEAN | 80253b7 | 2026-10-08 | 0 | present |
| [rappvision-one-minute-orchestra](repos/rappvision-one-minute-orchestra.md) | **archived** · certified |  | CLEAN | 0811085 | 2026-10-08 | 1 | present |
| [rappvision-patch-notes-tomorrow](repos/rappvision-patch-notes-tomorrow.md) | **archived** · certified |  | CLEAN | 8a9ecf4 | 2026-10-08 | 0 | present |
| [rappvision-pigeon-post](repos/rappvision-pigeon-post.md) | **archived** · certified |  | CLEAN | 4a7f85a | 2026-10-08 | 10 | present |
| [rappvision-pokemon](repos/rappvision-pokemon.md) | **archived** · certified |  | CLEAN | 21726d2 | 2026-10-08 | 0 | present |
| [rappvision-prompt-frontier](repos/rappvision-prompt-frontier.md) | **archived** · certified |  | CLEAN | ee8fa8a | 2026-10-08 | 0 | present |
| [rappvision-protocol-minute](repos/rappvision-protocol-minute.md) | **archived** · certified |  | CLEAN | f2bf8af | 2026-10-08 | 0 | present |
| [rappvision-rappid-zoo](repos/rappvision-rappid-zoo.md) | **archived** · certified |  | CLEAN | c6c2689 | 2026-10-08 | 0 | present |
| [rappvision-rappterbox](repos/rappvision-rappterbox.md) | **archived** · certified |  | CLEAN | dcf8f71 | 2026-10-08 | 0 | present |
| [rappvision-receipt-culture](repos/rappvision-receipt-culture.md) | **archived** · certified |  | CLEAN | 13e370d | 2026-10-08 | 0 | present |
| [rappvision-repair-manual](repos/rappvision-repair-manual.md) | **archived** · certified |  | CLEAN | 6f22e6f | 2026-10-08 | 0 | present |
| [rappvision-rnr](repos/rappvision-rnr.md) | **archived** · certified |  | CLEAN | 658cb1f | 2026-10-08 | 0 | present |
| [rappvision-signal-garden](repos/rappvision-signal-garden.md) | **archived** · certified |  | CLEAN | 29ed8a6 | 2026-10-08 | 0 | present |
| [rappvision-tiny-bureau](repos/rappvision-tiny-bureau.md) | **archived** · certified |  | CLEAN | cf8d14c | 2026-10-08 | 0 | present |

### Twins (15)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [echo-brainstem](repos/echo-brainstem.md) | **archived** · certified |  | COMPLIANT | 0d84ff0 | 2026-10-08 | 2 | present |
| [lumen-brainstem](repos/lumen-brainstem.md) | **archived** · certified |  | COMPLIANT | 7f41cfd | 2026-10-08 | 2 | present |
| [rapp-kite](repos/rapp-kite.md) | **archived** · certified | v1.0.0 | CLEAN | e010530 | 2026-10-08 | 0 | present |
| [rapp-kited-twin](repos/rapp-kited-twin.md) | certified | v1.0.0 | CLEAN | 7db7cc9 | 2026-10-08 | 0 | present |
| [rapp-overwatch](repos/rapp-overwatch.md) | **archived** · certified |  | CLEAN | 319104f | 2026-10-08 | 0 | present |
| [rapp-ratchet](repos/rapp-ratchet.md) | **archived** · certified |  | CLEAN | dc73e83 | 2026-10-08 | 0 | present |
| [rapp-twin](repos/rapp-twin.md) | certified |  | CLEAN | 83cd87e | 2026-10-08 | 1 | present |
| [rapp-twin-hub](repos/rapp-twin-hub.md) | **archived** · certified |  | CLEAN | c60714b | 2026-10-08 | 0 | present |
| [rapp-twin-in-residence](repos/rapp-twin-in-residence.md) | **archived** · certified |  | CLEAN | 4118cc7 | 2026-10-08 | 1 | present |
| [rapp-zoo](repos/rapp-zoo.md) | **archived** · certified | v1.2.0 | COMPLIANT | cb0f63f | 2026-10-08 | 3 | present |
| [sim-demo-twin](repos/sim-demo-twin.md) | **archived** · certified |  | COMPLIANT | 5f79fa6 | 2026-10-08 | 1 | present |
| [tide-brainstem](repos/tide-brainstem.md) | **archived** · certified |  | COMPLIANT | e134cee | 2026-10-08 | 2 | present |
| [twin-binder](repos/twin-binder.md) | **archived** · certified |  | CLEAN | 2b01e90 | 2026-10-08 | 0 | present |
| [twin-egg-hatcher](repos/twin-egg-hatcher.md) | certified |  | CLEAN | b30821a | 2026-10-08 | 0 | present |
| [wildhaven-ai-homes-twin](repos/wildhaven-ai-homes-twin.md) | **archived** · certified |  | COMPLIANT | 122c415 | 2026-10-08 | 24 | present |

### Neighborhoods (21)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [heimdall](repos/heimdall.md) | **archived** · certified |  | COMPLIANT | 2fe7950 | 2026-10-08 | 2 | present |
| [microsoft-se-team-neighborhood](repos/microsoft-se-team-neighborhood.md) | certified | v1.0.0 | COMPLIANT | 260dbfa | 2026-10-08 | 2 | present |
| [pkstop-central-park-bandshell](repos/pkstop-central-park-bandshell.md) | **archived** · certified |  | COMPLIANT | fd4b422 | 2026-10-08 | 1 | present |
| [pkstop-national-mall](repos/pkstop-national-mall.md) | **archived** · certified |  | COMPLIANT | 0960cb7 | 2026-10-08 | 1 | present |
| [pkstop-pike-place-market](repos/pkstop-pike-place-market.md) | **archived** · certified |  | COMPLIANT | 63eb295 | 2026-10-08 | 1 | present |
| [pkstop-santa-monica-pier](repos/pkstop-santa-monica-pier.md) | **archived** · certified |  | COMPLIANT | e6e52b9 | 2026-10-08 | 1 | present |
| [pkstop-the-bean](repos/pkstop-the-bean.md) | **archived** · certified |  | COMPLIANT | 4ad4e93 | 2026-10-08 | 2 | present |
| [public-art-collective](repos/public-art-collective.md) | **archived** · certified |  | CLEAN | 09f9887 | 2026-10-08 | 1 | present |
| [rapp-herdr](repos/rapp-herdr.md) | **archived** · certified |  | CLEAN | c23f4f6 | 2026-10-08 | 0 | present |
| [rapp-neighborhood-protocol](repos/rapp-neighborhood-protocol.md) | certified | v1.0.0 | CLEAN | 85d11fc | 2026-10-08 | 0 | present |
| [rapp-plant-smoke-20260505-233637](repos/rapp-plant-smoke-20260505-233637.md) | **archived** · certified |  | COMPLIANT | 8086683 | 2026-10-08 | 0 | present |
| [rapp-resident](repos/rapp-resident.md) | **archived** · certified |  | CLEAN | d3bf63c | 2026-10-08 | 0 | present |
| [rapp-sealed](repos/rapp-sealed.md) | certified | v1.0.0 | CLEAN | e427eaf | 2026-10-08 | 0 | present |
| [rapp-test-neighbor](repos/rapp-test-neighbor.md) | **archived** · certified | v1.0.0 | COMPLIANT | 12004e2 | 2026-10-08 | 1 | present |
| [rapp-virtual-as400](repos/rapp-virtual-as400.md) | **archived** · certified |  | CLEAN | be8f1bd | 2026-10-08 | 0 | present |
| [rapp-vision-neighborhood](repos/rapp-vision-neighborhood.md) | **archived** · certified |  | CLEAN | 0db1569 | 2026-10-08 | 0 | present |
| [rapp-vneighborhood](repos/rapp-vneighborhood.md) | **archived** · certified |  | CLEAN | 2315bc7 | 2026-10-08 | 0 | present |
| [rapp-work-cubbies](repos/rapp-work-cubbies.md) | **archived** · certified |  | CLEAN | b2dd7ce | 2026-10-08 | 0 | present |
| [second-seat](repos/second-seat.md) | **archived** · certified |  | CLEAN | acf4ff9 | 2026-10-08 | 0 | present |
| [vneighborhood-design-studio](repos/vneighborhood-design-studio.md) | **archived** · certified |  | CLEAN | 185afe7 | 2026-10-08 | 0 | present |
| [vneighborhood-research-lab](repos/vneighborhood-research-lab.md) | **archived** · certified |  | CLEAN | 4fe048b | 2026-10-08 | 0 | present |

### Organism & Platform (20)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [braintrust-template](repos/braintrust-template.md) | **archived** · certified |  | CLEAN | e4690a6 | 2026-10-08 | 1 | present |
| [CommunityRAPP](repos/CommunityRAPP.md) | certified | v1.0.0 | CLEAN | e72fd82 | 2026-10-08 | 9 | present |
| [rapp-ai](repos/rapp-ai.md) | **archived** · certified | v1.0.0 | CLEAN | f9789f8 | 2026-10-08 | 7 | present |
| [rapp-apex-dino](repos/rapp-apex-dino.md) | **archived** · certified |  | CLEAN | cc25f5b | 2026-10-08 | 0 | present |
| [rapp-base](repos/rapp-base.md) | **archived** · certified | v1.2.0 | CLEAN | 5963b64 | 2026-10-08 | 0 | present |
| [rapp-base-template](repos/rapp-base-template.md) | **archived** · certified | v1.2.0 | CLEAN | 4e0ee32 | 2026-10-08 | 0 | present |
| [rapp-body](repos/rapp-body.md) | **archived** · certified |  | COMPLIANT | 84f0783 | 2026-10-08 | 0 | present |
| [rapp-brain](repos/rapp-brain.md) | **archived** · certified |  | COMPLIANT | 14daaef | 2026-10-08 | 0 | present |
| [rapp-cortex](repos/rapp-cortex.md) | **archived** · certified |  | CLEAN | 01e10a4 | 2026-10-08 | 1 | present |
| [rapp-dino](repos/rapp-dino.md) | **archived** · certified |  | CLEAN | 3611b4c | 2026-10-08 | 0 | present |
| [rapp-hippocampus](repos/rapp-hippocampus.md) | **archived** · certified |  | CLEAN | 3c8d394 | 2026-10-08 | 1 | present |
| [rapp-membrane](repos/rapp-membrane.md) | **archived** · certified |  | CLEAN | 6fd2f53 | 2026-10-08 | 0 | present |
| [rapp-nervous-system](repos/rapp-nervous-system.md) | certified |  | CLEAN | dfc114a | 2026-10-08 | 1 | present |
| [rapp-organism](repos/rapp-organism.md) | **archived** · certified |  | CLEAN | 52bb52b | 2026-10-08 | 206 | present |
| [rapp-platform](repos/rapp-platform.md) | **archived** · certified |  | CLEAN | 3634be4 | 2026-10-08 | 1 | present |
| [rapp-second-brain](repos/rapp-second-brain.md) | **archived** · certified |  | CLEAN | da54afe | 2026-10-08 | 6 | present |
| [rapp-secondbrain](repos/rapp-secondbrain.md) | **archived** · certified |  | CLEAN | 521b60b | 2026-10-08 | 0 | present |
| [rapp-spinal-cord](repos/rapp-spinal-cord.md) | **archived** · certified |  | CLEAN | 106aaec | 2026-10-08 | 1 | present |
| [RAPP_hippo](repos/RAPP_hippo.md) | **archived** · certified | v1.0.0 | CLEAN | aa790f3 | 2026-10-08 | 9 | present |
| [RAPPsquared](repos/RAPPsquared.md) | **archived** · certified |  | CLEAN | 9aaa628 | 2026-10-08 | 0 | present |

### DOGG & Commons (13)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [dogg](repos/dogg.md) | not yet |  | DRIFT | 7525dd7 | 2026-10-08 | 0 | present |
| [dogg-canon](repos/dogg-canon.md) | **archived** · certified |  | COMPLIANT | f239270 | 2026-10-08 | 0 | present |
| [dogg-kestrel](repos/dogg-kestrel.md) | certified |  | COMPLIANT | ba40973 | 2026-10-08 | 0 | not yet added |
| [dogg-markets](repos/dogg-markets.md) | **archived** · certified |  | COMPLIANT | 7332aa2 | 2026-10-08 | 0 | present |
| [dogg-merlin](repos/dogg-merlin.md) | certified |  | COMPLIANT | e61875a | 2026-10-08 | 0 | not yet added |
| [dogg-planet](repos/dogg-planet.md) | **archived** · certified |  | COMPLIANT | e1c78f8 | 2026-10-08 | 0 | present |
| [rapp-commons](repos/rapp-commons.md) | not yet | v1.0.0 | DRIFT | 4793bca | 2026-10-08 | 0 | present |
| [rapp-dog-hub](repos/rapp-dog-hub.md) | **archived** · certified |  | CLEAN | c904967 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rapp-frame-net](repos/rapp-frame-net.md) | **archived** · certified |  | CLEAN | 143cd94 | 2026-10-08 | 0 | present |
| [rapp-god-forum](repos/rapp-god-forum.md) | **archived** · certified |  | CLEAN | 3b77205 | 2026-10-08 | 0 | present |
| [rapp-open](repos/rapp-open.md) | **archived** · certified |  | CLEAN | b876fdb | 2026-10-08 | 0 | present |
| [rappidverse-field](repos/rappidverse-field.md) | **archived** · certified |  | CLEAN | 7ae7693 | 2026-10-08 | 0 | present |
| [workroom](repos/workroom.md) | **archived** · certified |  | CLEAN | 92bee17 | 2026-10-08 | 1 | present |

### Tools & Apps (30)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [copilot-harness-sdk](repos/copilot-harness-sdk.md) | certified |  | CLEAN | 5a66a54 | 2026-10-08 | 40 | present |
| [dynamics365-business-process-api](repos/dynamics365-business-process-api.md) | certified |  | CLEAN | 9b5fa43 | 2026-10-08 | 1 | present |
| [lisppy-shepherd](repos/lisppy-shepherd.md) | **archived** · certified |  | CLEAN | 87604ec | 2026-10-08 | 1 | present |
| [rapp-cli](repos/rapp-cli.md) | **archived** · certified |  | CLEAN | d3bfe5e | 2026-10-08 | 1 | present |
| [rapp-copilot-in-chrome](repos/rapp-copilot-in-chrome.md) | certified |  | CLEAN | 4e866c8 | 2026-10-08 | 0 | present |
| [rapp-copilot-in-edge](repos/rapp-copilot-in-edge.md) | **archived** · certified |  | CLEAN | 356d2e8 | 2026-10-08 | 0 | present |
| [rapp-crispy](repos/rapp-crispy.md) | **archived** · not yet | v1.5.1 | DRIFT | ba4a5da | 2026-10-08 | 0 | present |
| [rapp-dataverse](repos/rapp-dataverse.md) | **archived** · certified |  | CLEAN | bd3d829 | 2026-10-08 | 0 | present |
| [rapp-doorman](repos/rapp-doorman.md) | **archived** · certified | v1.0.0 | CLEAN | a3d120e | 2026-10-08 | 0 | present |
| [rapp-dynamic-workflows](repos/rapp-dynamic-workflows.md) | **archived** · certified |  | CLEAN | 2394819 | 2026-10-08 | 8 | present |
| [rapp-imessage-launchpad](repos/rapp-imessage-launchpad.md) | **archived** · certified |  | CLEAN | a2a0b54 | 2026-10-08 | 0 | present |
| [rapp-keyring](repos/rapp-keyring.md) | certified | v0.1.0 | CLEAN | b7dac71 | 2026-10-08 | 0 | present |
| [rapp-local-install](repos/rapp-local-install.md) | **archived** · certified |  | CLEAN | c7ef119 | 2026-10-08 | 0 | present |
| [rapp-messaging](repos/rapp-messaging.md) | **archived** · certified |  | CLEAN | 09508e8 | 2026-10-08 | 0 | present |
| [rapp-omarchy](repos/rapp-omarchy.md) | **archived** · certified |  | CLEAN | fd41eda | 2026-10-08 | 2 | present |
| [rapp-oneclick-deploy](repos/rapp-oneclick-deploy.md) | **archived** · certified |  | COMPLIANT | 663175b | 2026-10-08 | 2 | present |
| [rapp-projects](repos/rapp-projects.md) | **archived** · certified | v0.1.1 | CLEAN | 29c923e | 2026-10-08 | 0 | present |
| [rapp-recall](repos/rapp-recall.md) | **archived** · certified | v0.1.0 | CLEAN | 1e35c23 | 2026-10-08 | 30 | present |
| [rapp-rewind](repos/rapp-rewind.md) | **archived** · not yet | v1.2.1 | DRIFT | e15fbde | 2026-10-08 | 0 | present |
| [rapp-sdk](repos/rapp-sdk.md) | **archived** · certified | v0.2.0 | CLEAN | b007fc2 | 2026-10-08 | 27 | present |
| [rapp-shot](repos/rapp-shot.md) | **archived** · not yet | v1.3.1 | DRIFT | 749168d | 2026-10-08 | 0 | present |
| [rapp-static-apis](repos/rapp-static-apis.md) | certified | v1.0.0 | CLEAN | c1679f0 | 2026-10-08 | 0 | present |
| [rapp-static-mcp](repos/rapp-static-mcp.md) | **archived** · certified |  | CLEAN | d6ff961 | 2026-10-08 | 0 | present |
| [rapp-tools](repos/rapp-tools.md) | **archived** · certified | workspace-v0.1.0 | CLEAN | 776a9d5 | 2026-10-08 | 0 | present |
| [rapp-ultracode](repos/rapp-ultracode.md) | **archived** · certified |  | CLEAN | 01c0c0c | 2026-10-08 | 1 | present |
| [rapp-voice](repos/rapp-voice.md) | **archived** · not yet | v1.1.1 | DRIFT | ec7dcf9 | 2026-10-08 | 0 | present |
| [rapp-vui](repos/rapp-vui.md) | **archived** · certified |  | CLEAN | 6a6a3b6 | 2026-10-08 | 0 | present |
| [rapp-workspace-manager](repos/rapp-workspace-manager.md) | **archived** · certified | v1.0.0 | COMPLIANT | 2308872 | 2026-10-08 | 1 | present |
| [RAPP_Desktop](repos/RAPP_Desktop.md) | **archived** · certified | v1.0.0 | CLEAN | 4c7826c | 2026-10-08 | 0 | present |
| [RAPPAIClaudeCodePlayground](repos/RAPPAIClaudeCodePlayground.md) | **archived** · certified |  | CLEAN | 7fa9396 | 2026-10-08 | 0 | present |

### Estate & Ops (18)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [rapp-bake-off](repos/rapp-bake-off.md) | **archived** · certified |  | CLEAN | 306b2af | 2026-10-08 | 0 | present |
| [rapp-bench](repos/rapp-bench.md) | **archived** · certified |  | CLEAN | 862224c | 2026-10-08 | 0 | present |
| [rapp-distro](repos/rapp-distro.md) | certified |  | CLEAN | d90c745 | 2026-10-08 | 0 | PR open |
| [rapp-estate](repos/rapp-estate.md) | **archived** · certified |  | CLEAN | acc17dc | 2026-10-08 | 0 | no README (skipped) |
| [rapp-infrastructure-city](repos/rapp-infrastructure-city.md) | **archived** · certified |  | CLEAN | dafe7e0 | 2026-10-08 | 0 | present |
| [rapp-metrics](repos/rapp-metrics.md) | **archived** · certified |  | CLEAN | afb5733 | 2026-10-08 | 0 | present |
| [rapp-monorepo](repos/rapp-monorepo.md) | not yet |  | DRIFT | 0fc3233 | 2026-10-08 | 4455 | present |
| [rapp-parity](repos/rapp-parity.md) | **archived** · certified |  | COMPLIANT | aefd483 | 2026-10-08 | 0 | present |
| [rapp-personpower](repos/rapp-personpower.md) | **archived** · certified |  | CLEAN | 85104a0 | 2026-10-08 | 0 | present |
| [rapp-postflight](repos/rapp-postflight.md) | **archived** · certified |  | CLEAN | 52bb6d7 | 2026-10-08 | 0 | present |
| [rapp-refresh](repos/rapp-refresh.md) | **archived** · certified | v1.0.0 | CLEAN | fb7c7cd | 2026-10-08 | 0 | present |
| [rapp-roadside](repos/rapp-roadside.md) | **archived** · not yet | v1.0.0 | DRIFT | a7cbe2c | 2026-10-08 | 0 | present |
| [rapp-rock-tumbler](repos/rapp-rock-tumbler.md) | **archived** · certified |  | CLEAN | c9223d3 | 2026-10-08 | 0 | present |
| [rapp-sentinel](repos/rapp-sentinel.md) | **archived** · certified |  | CLEAN | 1e73ad5 | 2026-10-08 | 1 | present |
| [rapp-support](repos/rapp-support.md) | **archived** · certified |  | CLEAN | ba55c22 | 2026-10-08 | 0 | present |
| [rapp-tower](repos/rapp-tower.md) | **archived** · certified |  | CLEAN | fb396e9 | 2026-10-08 | 4 | present |
| [rapp-version-selector](repos/rapp-version-selector.md) | **archived** · certified |  | CLEAN | 8f64e89 | 2026-10-08 | 9 | present |
| [sentinel](repos/sentinel.md) | **archived** · certified |  | CLEAN | f625338 | 2026-10-08 | 0 | present |

### Worlds & Play (26)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [ant-farm](repos/ant-farm.md) | **archived** · certified |  | COMPLIANT | db7f4a1 | 2026-10-08 | 1 | present |
| [double-jump](repos/double-jump.md) | **archived** · certified | v0.1.0 | CLEAN | 2dc5dea | 2026-10-08 | 17 | present |
| [leviathan](repos/leviathan.md) | **archived** · certified |  | CLEAN | 8c5409d | 2026-10-08 | 0 | present |
| [racon](repos/racon.md) | **archived** · certified | v1.0.0 | CLEAN | 0d5d5bd | 2026-10-08 | 0 | present |
| [RaGo](repos/RaGo.md) | **archived** · certified | v2.1.0 | CLEAN | 8207e2c | 2026-10-08 | 0 | present |
| [rapp-basket](repos/rapp-basket.md) | **archived** · certified |  | CLEAN | 9b3691e | 2026-10-08 | 0 | present |
| [rapp-burrow](repos/rapp-burrow.md) | **archived** · certified |  | CLEAN | 9bcd07e | 2026-10-08 | 0 | present |
| [rapp-coop](repos/rapp-coop.md) | **archived** · certified |  | CLEAN | 64ed924 | 2026-10-08 | 0 | present |
| [rapp-eternity](repos/rapp-eternity.md) | **archived** · certified |  | CLEAN | 9fc691d | 2026-10-08 | 0 | present |
| [rapp-fps](repos/rapp-fps.md) | **archived** · certified |  | CLEAN | 6e00362 | 2026-10-08 | 0 | merged, awaiting the next sweep |
| [rapp-heir](repos/rapp-heir.md) | **archived** · certified |  | CLEAN | 5999d27 | 2026-10-08 | 3 | present |
| [rapp-holo](repos/rapp-holo.md) | **archived** · certified |  | CLEAN | 3f0a323 | 2026-10-08 | 0 | present |
| [rapp-hologram](repos/rapp-hologram.md) | **archived** · certified | v1.0.0 | CLEAN | ca0544b | 2026-10-08 | 0 | present |
| [rapp-lantern](repos/rapp-lantern.md) | **archived** · certified |  | COMPLIANT | 3e5f4b9 | 2026-10-08 | 0 | present |
| [rapp-moment](repos/rapp-moment.md) | **archived** · certified | v1.1.0 | CLEAN | 04f2c0a | 2026-10-08 | 0 | present |
| [rapp-moonshots](repos/rapp-moonshots.md) | **archived** · certified |  | CLEAN | 384c1c9 | 2026-10-08 | 3 | present |
| [rapp-pets](repos/rapp-pets.md) | **archived** · certified |  | CLEAN | 116b4f6 | 2026-10-08 | 0 | present |
| [rapp-play-pokemon](repos/rapp-play-pokemon.md) | **archived** · certified |  | CLEAN | 9619ef0 | 2026-10-08 | 1 | present |
| [rapp-snap](repos/rapp-snap.md) | **archived** · certified |  | CLEAN | f35e5cb | 2026-10-08 | 0 | present |
| [rapp-zoo-v2](repos/rapp-zoo-v2.md) | **archived** · not yet | v0.1.0 | DRIFT | d6204b3 | 2026-10-08 | 0 | present |
| [rapp_orion](repos/rapp_orion.md) | **archived** · certified |  | CLEAN | 2710071 | 2026-10-08 | 8 | present |
| [rappid](repos/rappid.md) | **archived** · not yet |  | DRIFT | 17467d2 | 2026-10-08 | 0 | present |
| [rio](repos/rio.md) | **archived** · certified | v1.0.0 | COMPLIANT | e49264b | 2026-10-08 | 0 | present |
| [rionet](repos/rionet.md) | **archived** · certified |  | CLEAN | 620dffc | 2026-10-08 | 0 | present |
| [sim-art-collective](repos/sim-art-collective.md) | **archived** · certified |  | COMPLIANT | a0f392e | 2026-10-08 | 1 | present |
| [the-coliseum](repos/the-coliseum.md) | **archived** · certified |  | CLEAN | 018283e | 2026-10-08 | 0 | present |

### RAPP Projects (2)

| Repo | Status | Version | Verdict | Commit | Checked | "experimental" | Header |
|---|---|---|---|---|---|---|---|
| [grail-vault](repos/grail-vault.md) | certified |  | CLEAN | a83c384 | 2026-10-08 | 0 | not yet added |
| [rapp-chatgpt](repos/rapp-chatgpt.md) | certified | v1.2.0 | CLEAN | 8bef36d | 2026-10-08 | 0 | not yet added |
