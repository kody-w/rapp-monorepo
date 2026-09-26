# `rapp1_network/lines.py`

The families, drawn as the subway's lines. A repo belongs to the first line that names it, else to the first line whose token pattern matches one of its name tokens, else to "RAPP Projects". It is also on every other line whose token pattern matches (not the line's parent), which makes it an interchange.

Source: `rapp1_network/lines.py` (rapp1-network 0.1.6). SHA-256 of the source below: `6bf9705b085df39144d13463cd8452c1f9d7400b96027f3bdd8040bfb59f5c40` (10875 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/lines.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The families, drawn as the subway's lines. A repo belongs to the first line that names it, else to the first line
whose token pattern matches one of its name tokens, else to "RAPP Projects". It is also on every other line whose
token pattern matches (not the line's parent), which makes it an interchange.

Every name listed here is a public repo in the portfolio (the lists are published with the tools)."""
from __future__ import annotations

import re


def tokens(name):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return [t for t in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if t]


def _names(text):
    return frozenset(text.split())


# The families are the subway lines. A repo belongs to the first line that names it, else to the first line
# whose token pattern matches one of its name tokens, else to "RAPP Projects". It is also on every other
# line whose token pattern matches (not the line's parent), which makes it an interchange.
LINES = [
    {"id": "rapp1-core", "name": "RAPP/1 Core", "color": "#5f3dc4", "match": r"installer",
     "names": _names("RAPP rapp-1 rapp-installer rapp-work rapp-workspace rapp-drift-lint lisppy"),
     "about": "The RAPP/1 stack in layer order, from layer 0 (RAPP/1) up to the Brainstem, ending at the "
              "Start here terminal."},
    {"id": "hive", "name": "Hive", "color": "#1971c2", "match": r"hive.*",
     "names": _names("rapp-model-hive hive-hub rapp-hive-hub hive-hub-mcp hive-hub-join rapp-hive-hub-join "
                     "rapp-hive-public hive-showcase"),
     "about": "Hives, the hubs that list them, and the ways in."},
    {"id": "agents-rar", "name": "Agents (RAR)", "color": "#c2255c", "match": r"rar|skills?|store|binder",
     "names": _names("RAR rapp-agents RAPP_Store RAPP_Sense_Store rapp-store-archive RAPP_Hub rapp-skill rapp-skills "
                     "rapp-claude-skills rapp-toaster rapp-carts rapp-egg-hub rapp-packs rapp-hatchery "
                     "rapp-sentinel-hub rapp-leviathan-hub AI-Agent-Templates-Pilot rapp-stack-cubby "
                     "cowork-cookbook-rapp RAPPcards red-binder obsidian-binder"),
     "about": "The agent registry, its stores, skills, cartridges and card binders."},
    {"id": "brainstem", "name": "Brainstem", "color": "#e8590c", "match": r".*brainstem.*|stemcell|skillstem",
     "names": _names("rapp-brainstem brainstem-agent rapp-brainstem-foundation rapp-brainstem-frontier-template "
                     "rapp-brainstem-sdk vbrainstem stemcell skillstem brainstem-harness brainstem-copilot chat "
                     "ez-rapp rapp-light rapp-brainfreeze rapp-brainfreeze-studio rapp-petri rapp-quests "
                     "rapp-vscode-extension"),
     "about": "The one surface you talk to: Brainstem engines, strains, harnesses and shells."},
    {"id": "connect", "name": "Brainstem Connect", "color": "#9c36b5", "match": r"", "parent": "brainstem",
     "names": _names("rapp-brainstem-claude rapp-brainstem-claude-desktop rapp-brainstem-cline rapp-brainstem-codex "
                     "rapp-brainstem-copilot rapp-brainstem-cursor rapp-brainstem-gemini rapp-brainstem-goose "
                     "rapp-brainstem-kiro rapp-brainstem-mcp rapp-brainstem-opencode rapp-brainstem-vscode "
                     "rapp-brainstem-windsurf rapp-brainstem-plugin scout-brainstem-bootstrap rapp-mcp"),
     "about": "One line into any AI app: the per-app Brainstem setup pages and bridges."},
    {"id": "learn", "name": "Learn & Docs", "color": "#339af0", "match": r"docs|learn|specs|bible|bootcamp|walkthrough",
     "names": _names("learn-brainstem brainstem-bootcamp rapp-brainstem-walkthrough RAPP-Bible rapp-docs rapp_docs "
                     "rapp-specs rapp-map rapp-mapp rapp-roadmap rapp-mission rapp-education-shorts rapp-demos "
                     "rapp-wiki-observatory dimensional-bottles rapp-spine rapp-lab-kit rappdex"),
     "about": "Guides, specs, maps and teaching material."},
    {"id": "release", "name": "Release Channels", "color": "#212529", "match": r"alpha|beta|canary|nightly|release",
     "names": _names("rapp-alpha rapp-beta rapp-canary rapp-nightly rapp-release-train rapp-installer-canary "
                     "rapp-installer-dev rapp-brainstem-beta openrappter-alpha openrappter-beta openrappter-canary "
                     "openrappter-nightly openrappter-release-train rapp-rings rapp-train rapp-flight rapp-flight-deck "
                     "rapp-mirror-releases rapp-shape-aibast"),
     "about": "Pre-release rings and trains, from canary to stable."},
    {"id": "openrappter", "name": "OpenRappter", "color": "#e03131", "match": r"openrappter.*",
     "names": _names("openrappter homebrew-tap rappterhub rappter-cli rappter-plays-palworld rappter-plays-pokemon "
                     "rappter-prompts rappter-vui"),
     "about": "The local-first OpenRappter agent and what ships around it."},
    {"id": "rappterbook", "name": "Rappterbook", "color": "#0b7285", "match": r"rappterbook.*",
     "names": _names("rappbook-admin mars-barn"),
     "about": "The social network for AI agents and its swarm projects."},
    {"id": "rappterverse", "name": "Rappterverse", "color": "#15aabf", "match": r"rappterverse.*|rappterbox|rappternest",
     "names": _names("rappterverse rappterverse-data rappterbox RappterNest rappter-site rappter-mmo rappter-factory "
                     "rappter-distro CrystalRAPP VoidRAPP ShadowRAPP"),
     "about": "RappterBox, the Rappterverse worlds and their dimensions."},
    {"id": "rappvision", "name": "Rappvision", "color": "#f06595", "match": r"rappvision.*",
     "names": _names("rapp-vision rapp-video rapp-remix"),
     "about": "Video channels, shorts and the studio that makes them."},
    {"id": "twins", "name": "Twins", "color": "#9c6644", "match": r"twins?",
     "names": _names("echo-brainstem lumen-brainstem tide-brainstem sim-demo-twin rapp-twin rapp-twin-hub "
                     "rapp-twin-in-residence rapp-kited-twin twin-binder twin-egg-hatcher wildhaven-ai-homes-twin "
                     "rapp-zoo rapp-kite rapp-overwatch rapp-ratchet"),
     "about": "Digital twins: planted, kited, hatched and watching."},
    {"id": "neighborhoods", "name": "Neighborhoods", "color": "#be4bdb", "match": r"v?neighborhood.*|neighbor|pkstop",
     "names": _names("heimdall second-seat microsoft-se-team-neighborhood public-art-collective rapp-herdr "
                     "rapp-virtual-as400 rapp-resident rapp-work-cubbies rapp-sealed RAPP-Network "
                     "rapp-plant-smoke-20260505-233637 rapp-test-neighbor"),
     "about": "Front doors and sealed twin neighborhoods."},
    {"id": "organism", "name": "Organism & Platform", "color": "#862e2e",
     "match": r"body|brain|cortex|hippocampus|hippo|membrane|nervous|spinal|organism",
     "names": _names("rapp-body rapp-brain rapp-cortex rapp-hippocampus RAPP_hippo CommunityRAPP rapp-ai "
                     "rapp-membrane rapp-nervous-system rapp-spinal-cord rapp-organism rapp-second-brain "
                     "rapp-secondbrain rapp-apex-dino rapp-dino rapp-platform rapp-base rapp-base-template "
                     "RAPPsquared braintrust-template"),
     "about": "The organism's body parts, memory tiers and platform bases."},
    {"id": "dogg", "name": "DOGG & Commons", "color": "#3d5a80", "match": r"dogg.*|commons",
     "names": _names("dogg dogg-markets dogg-planet dogg-canon rapp-dog-hub rappidverse-field rapp-commons "
                     "rapp-god-forum rapp-open rapp-frame-net workroom"),
     "about": "The federated DOGG network, the commons and the wire between estates."},
    {"id": "tools", "name": "Tools & Apps", "color": "#3b5bdb", "match": r"",
     "names": _names("rapp-cli rapp-sdk rapp-tools rapp-static-apis rapp-static-mcp rapp-dynamic-workflows "
                     "rapp-ultracode rapp-dataverse rapp-local-install rapp-oneclick-deploy rapp-workspace-manager "
                     "rapp-projects copilot-harness-sdk dynamics365-business-process-api lisppy-shepherd "
                     "RAPPAIClaudeCodePlayground rapp-copilot-in-chrome rapp-copilot-in-edge rapp-doorman rapp-keyring "
                     "rapp-omarchy RAPP_Desktop rapp-imessage-launchpad rapp-messaging rapp-voice rapp-crispy "
                     "rapp-recall rapp-rewind rapp-shot rapp-vui"),
     "about": "Command lines, SDKs, bridges and local-first desktop apps."},
    {"id": "estate", "name": "Estate & Ops", "color": "#495057", "match": r"estate|sentinel",
     "names": _names("rapp-estate rapp-infrastructure-city rapp-monorepo rapp-distro rapp-parity rapp-sentinel "
                     "sentinel rapp-tower rapp-bake-off rapp-rock-tumbler rapp-personpower rapp-bench rapp-postflight "
                     "rapp-support rapp-refresh rapp-roadside rapp-version-selector rapp-metrics"),
     "about": "Running the estate: inventories, watchdogs, benches, resets and support."},
    {"id": "worlds", "name": "Worlds & Play", "color": "#845ef7",
     "match": r"holo|hologram|zoo|pets|pokemon|palworld|mmo",
     "names": _names("racon rio rionet RaGo rappid rapp-zoo-v2 rapp-pets rapp-play-pokemon rapp-fps rapp-holo "
                     "rapp-hologram rapp-moment rapp-snap rapp-lantern rapp-basket rapp-burrow rapp-eternity rapp-coop "
                     "rapp-heir rapp-moonshots rapp_orion ant-farm double-jump leviathan the-coliseum "
                     "sim-art-collective"),
     "about": "Games, worlds, holograms and swarm experiments."},
    {"id": "projects", "name": "RAPP Projects", "color": "#a0522d", "match": r"",
     "names": frozenset(), "about": "Everything else in the family, until it gets a line of its own."},
]
LINE = {line["id"]: line for line in LINES}
# The Core line's stations, in layer order (the organism's layers 0 to 5), ending at the Start here terminal.
TRUNK = [("rapp-1", "0 RAPP/1"), ("rapp-drift-lint", "1 Estate"), ("rapp-work", "1-2 Estate, Organization"),
         ("rapp-model-hive", "3 Hive"), ("rapp-workspace", "4 Your device"), ("lisppy", "5 Brainstem"),
         ("RAPP", "5 Brainstem"), ("rapp-installer", "Start here")]


def line_of(name):
    """(primary line, other lines): named first, else by the earliest name token a line matches."""
    toks = tokens(name)
    lines_for = lambda t: [line["id"] for line in LINES if line["match"] and re.fullmatch(line["match"], t)]
    primary = (next((line["id"] for line in LINES if name in line["names"]), None)
               or next((ids[0] for t in toks for ids in [lines_for(t)] if ids), None) or "projects")
    also = {i for t in toks for i in lines_for(t)} - {primary, LINE[primary].get("parent")}
    if name in dict(TRUNK) and primary != "rapp1-core":
        also.add("rapp1-core")
    order = {line["id"]: n for n, line in enumerate(LINES)}
    return primary, sorted(also, key=order.get)
`````
{% endraw %}
