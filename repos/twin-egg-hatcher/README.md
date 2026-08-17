# twin-egg-hatcher

> Generic single-file hatcher for any RAPP digital-organism twin.
> Public mirror — curl-friendly, no auth required.

The hatcher carries no twin identity of its own.  Point it at a twin
repo (public or private), a `.egg` file, or just run it inside a
cloned twin folder, and it materializes a `~/.rapp/twins/<hash>/`
workspace.  The global RAPP brainstem's built-in `Twin` agent reaches
every workspace under that folder — boot, chat, list — so any twin
hatched by this tool federates back to the parent immediately.

> **Canonical home** is the private repo
> [`kody-w/aibast-twin`](https://github.com/kody-w/aibast-twin) — this
> repo is a public mirror so any twin can curl the hatcher without a
> token.

## Install

Requires a brainstem locally first
([`kody-w/rapp-installer`](https://github.com/kody-w/rapp-installer)):

```bash
curl -fsSL https://kody-w.github.io/RAPP/installer/install.sh | bash
```

Then drop the hatcher anywhere you want to use it:

```bash
curl -fsSL https://raw.githubusercontent.com/kody-w/twin-egg-hatcher/main/install.sh | bash
```

That installs `./twin_egg_hatcher_agent.py` in the current folder.

## Three loaders, one hatcher

| Loader | When to use | Example |
|--------|-------------|---------|
| **cwd auto-detect** | Inside a cloned twin repo. | `cd heimdall && python twin_egg_hatcher_agent.py hatch` |
| **`--source REPO`** | Public/private GitHub twin repo. Set `GH_TOKEN` for private. | `python twin_egg_hatcher_agent.py hatch --source kody-w/heimdall` |
| **`--egg PATH`** | Fully exported `.egg` zip — private / air-gapped. | `python twin_egg_hatcher_agent.py hatch --egg ~/Downloads/botsinblazers.egg` |

## What a hatch produces

```
~/.rapp/twins/<32-hex-hash-or-uuid>/
├── rappid.json          preserved verbatim from the source
├── soul.md              the twin's persona (read by the brainstem each turn)
├── agents/              the twin's own agents, copied in
├── HATCH_RECEIPT.json   hatcher version + source pointer + timestamp
└── .brainstem_data/     empty, ready for runtime state
```

## Federate through the global brainstem

```
> Twin(action="list")                                         # see the twin
> Twin(action="boot",  rappid_uuid="<rappid>")                # start on a free port (7081–7200)
> Twin(action="chat",  rappid_uuid="<rappid>", message="...")  # POSTs to the twin's /chat
```

The global brainstem source is never touched in the default
`mode=twin`.

## CLI

```bash
python twin_egg_hatcher_agent.py hatch                       # cwd auto-detect
python twin_egg_hatcher_agent.py hatch --source kody-w/heimdall
python twin_egg_hatcher_agent.py hatch --egg ~/Downloads/twin.egg
python twin_egg_hatcher_agent.py status
python twin_egg_hatcher_agent.py list-twins
python twin_egg_hatcher_agent.py rollback --rappid "<rappid>"

# advanced — extend the brainstem itself with organs/senses from the source
python twin_egg_hatcher_agent.py hatch --mode global --source kody-w/heimdall
```

## Portable agent mode

Drop the file into the global brainstem's `agents/` folder.  The LLM
gets a `HatchTwinEgg` tool with the same actions:

```bash
cp twin_egg_hatcher_agent.py ~/.brainstem/src/rapp_brainstem/agents/
# then via /chat:
#   "Hatch the Heimdall twin from kody-w/heimdall"
#   "Hatch from this egg: ~/Downloads/botsinblazers.egg"
```

## Source contract

For the cwd or `--source` loader, a twin repo needs at minimum:

| File | Required | Purpose |
|------|----------|---------|
| `rappid.json` | yes | Identity.  Must contain a `rappid` field. |
| `soul.md` | strongly recommended | Persona — read by the brainstem every turn. |
| `agents/*.py` | optional | Twin-specific agents. |
| `organs/*.py` | optional | Brainstem extensions (used by `mode=global`). |
| `senses/*.py` | optional | Brainstem sense channels (used by `mode=global`). |

Twins already shaped this way:
[`kody-w/heimdall`](https://github.com/kody-w/heimdall),
[`kody-w/kody-w-twin`](https://github.com/kody-w/kody-w-twin),
[`kody-w/aibast-twin`](https://github.com/kody-w/aibast-twin) (private),
[`kody-w/bots-in-blazers-twin`](https://github.com/kody-w/bots-in-blazers-twin) (private).

## Why one generic hatcher

The egg is the delivery mechanism; the twin is what lives.  Every twin
repo shouldn't ship its own copy of the hatcher — that's
copy-paste-drift waiting to happen.  This file is the single source of
truth; twin repos just hold identity (rappid + soul + agents).

## License

MIT.
