# `rapp1_network/constants.py`

Fixed facts of the RAPP/1 network. Everything here is public; nothing here is a setting.

Source: `rapp1_network/constants.py` (rapp1-network 0.1.5). SHA-256 of the source below: `9fa880a31c823307e460e99a3b86512578b6f8426c86d1d5856d0a69548c3d64` (2482 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/constants.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Fixed facts of the RAPP/1 network. Everything here is public; nothing here is a setting."""

OWNER = "kody-w"
CANON_RAPP1 = "591e014ad39e223b00ab343ae26e5d9a867ebeee"  # kody-w/rapp-1: the checker and the reference rapp.py
RAPP1_REPO = f"https://github.com/{OWNER}/rapp-1.git"

PUBLIC_REPO = "rapp-hive-public"
ROOM = "shared/organism"  # the one published Hive room; its prefix is stripped when published
PORTFOLIO = "portfolio"  # shared/organism/portfolio/ -> portfolio/ in the public copy
PAGES = f"https://{OWNER}.github.io/{PUBLIC_REPO}/{PORTFOLIO}"
PUBLIC_BLOB = f"https://github.com/{OWNER}/{PUBLIC_REPO}/blob/main/{PORTFOLIO}"
REPO_URL = f"https://github.com/{OWNER}/"
INSTALLER = f"https://github.com/{OWNER}/rapp-installer#start-here"

START = "<!-- rapp1:network-header:start -->"
END = "<!-- rapp1:network-header:end -->"

WAVE1 = ("RAPP", "rapp-installer", "rapp-1", "rapp-work", "rapp-workspace", "RAR", "rapp-model-hive",
         "rapp-hive-public", "hive-hub", "rapp-hive-hub", "hive-hub-mcp", "hive-hub-join",
         "rapp-hive-hub-join", "rapp-drift-lint", "lisppy")
STATUSES = ("certified", "not yet", "unchecked")
COLORS = {"certified": "#2da44e", "not yet": "#dfb317", "unchecked": "#9f9f9f"}
MAX_WORKERS = 6  # at most six clones at a time

# The pulse chain: one RAPP/1 body.pulse frame per crawl (SPEC §7, pinned above).
STREAM_SLUG = "rapp1-network"  # the stream's rappid slug; its tail is minted once, keyless (§6.2)
PULSE_KIND = "body.pulse"  # a registered kind of the body family (SPEC §7.2; rapp-1 anchor head rev-16)
PULSE_SCHEMA = "rapp1-network-pulse/1"  # a label for the payload's shape, never an identity (version 1)
PULSE_SCHEMA_2 = "rapp1-network-pulse/2"  # version 2 onwards: /1 plus channels, lifecycles, versions and notices
INDEX_NAME = "rapp-frame-index.json"
PRIVATE_ROOM = "shared/network-pulses"  # an unpublished room, used only if public pulses would cost the badge

# Header pull requests: never merged, never a push to a default branch.
BRANCH = "rapp1/network-header"
TITLE = "RAPP/1 network header: status badge and Start here"
IDENTITY = ("-c", "user.name=kody-w", "-c", "user.email=1735900+kody-w@users.noreply.github.com")
TRAILERS = ("Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\n"
            "Copilot-Session: b6562323-1ad0-4e5e-9951-f2273c033d4a")

# The Hive's rules for one file (kody-w/rapp-model-hive, hive_agent.py).
HIVE_MAX_BYTES = 1 << 20
HIVE_MAX_PATH = 120
HIVE_MAX_PART = 64
`````
{% endraw %}
