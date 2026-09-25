# Brainstem Hatchery

Hatch a RAPP brainstem just in time.

A **hatchling** is a brainstem hatched on demand. It is the unmodified grail engine at a pinned ref, plus
whatever you hatch into it: nothing, a soul and agents, or a rapp/1 organism egg. It runs on its own
loopback port, beside the brainstem you installed. Release it when you're done, or keep it. A hatchling you
keep is a **twin**.

```
egg ──hatch──▶ hatchling ──keep──▶ twin
 ▲                 │
 └─────freeze──────┘      (freezing and thawing are rapp-brainfreeze's job)
```

## Quick start

```bash
python3 -m hatchery hatch                                  # today's grail engine
python3 -m hatchery hatch --egg you--my-desk.egg           # an egg, on the engine commit it expects
python3 -m hatchery hatch --ref <commit> --bare --agent my_agent.py --soul soul.md
python3 -m hatchery list
python3 -m hatchery chat hatchling-7120 "What can you do?"
python3 -m hatchery keep hatchling-7120                    # a twin now; `release all` leaves it alone
python3 -m hatchery release hatchling-7120                 # or: release all
```

From Python, a context manager releases the hatchling when the block ends:

```python
from hatchery import Hatchling

with Hatchling(egg="you--my-desk.egg") as bs:
    print(bs.chat("What can you do?").response)
```

`--egg` also takes an https URL. `--source` takes `grail` (the default), `canary`, a git URL or a local
repository. `--bare` parks the engine's own agents, and hatching an egg is bare by default, because the egg
carries its agents.

## Just in time

- The engine is fetched once into a local mirror, and each hatchling is a local clone of it, detached at the
  pinned commit. A pinned commit that is already in the mirror needs no network.
- Python packages are installed once per set of engine requirements and shared by every hatchling that needs
  the same set.

Measured on 24 Sep 2026 against the grail: the first hatch took 32 s, including the mirror and the packages.
After that, a hatchling with an agent took 2.3 s, and an egg took 1.0 s.

## What it never does

- **It never changes the grail.** Every hatchling's push URL is disabled (`DISABLED-hatchling-is-read-only`),
  and the mirror only fetches.
- **It never writes to your installed brainstem** (`~/.brainstem/src`, port 7071). It reuses that
  brainstem's GitHub sign-in, read-only. If there isn't one, it uses `GITHUB_TOKEN`; failing that, it runs
  GitHub's device sign-in once and keeps the result for later hatchlings.
- **It never takes engine code from an egg.** An egg carries a soul, agents, memory and the engine version it
  expects, and it hatches onto that engine. The hatchery verifies every egg with the RAPP reference
  implementation (vendored verbatim in `hatchery/rapp1.py`) before laying anything in. Each hatch mints a
  fresh instance identity in `instance.json` (rapp/1 §9.4).
- **It never listens beyond loopback** (`BRAINSTEM_LAN_MODE=false`).

## Where things live

| What | Where |
|---|---|
| Hatchlings | `~/.brainstem/hatchlings/<name>/`: the `engine/` checkout, `hatchling.json`, `server.log`, `conversation.json`, `instance.json` for an egg, and `parked-agents/` when bare |
| Engine mirrors, shared venvs, saved sign-in | `~/.brainstem/hatchery/` |

Override the locations with `HATCHERY_ROOT` and `HATCHERY_CACHE`. Set `HATCHERY_PYTHON` to choose the Python;
the default is python3.11, the engine's version.

## Where it fits

| Repo | What it does |
|---|---|
| [rapp-installer](https://github.com/kody-w/rapp-installer) (the grail) | The brainstem engine. The hatchery only reads it. |
| **rapp-hatchery** | Runs brainstems just in time: hatch, chat, keep, release. |
| [rapp-brainfreeze](https://github.com/kody-w/rapp-brainfreeze) | Freezes and thaws a brainstem; lays and reads eggs. |
| [rapp-brainfreeze-studio](https://github.com/kody-w/rapp-brainfreeze-studio) | Turns an egg into a Copilot Studio agent. |

## Not yet

- **Snapshots:** thawing a brainfreeze snapshot stays in rapp-brainfreeze, whose `Throwaway` is meant to
  import from the hatchery next.
- **Restart after a reboot:** a kept twin doesn't restart on its own yet; `hatchery start <name>` brings it
  back. A login service (launchd or systemd) is next.
- **Windows:** untested.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests run offline. The engine is a local git repository whose stand-in brainstem answers `/health` and
`/chat` the same way the real one does.

## License

MIT, Copyright (c) 2026 Kody Wildfeuer.
