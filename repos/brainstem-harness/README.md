# brainstem-harness

**Run RAPP `agent.py` files on the [GitHub Copilot harness](https://devblogs.microsoft.com/agent-framework/build-production-ready-agents-with-the-github-copilot-harness-and-agent-framework/) — and prove the port didn't change them.**

```bash
python3 brainstem_agent.py discover agents/
python3 brainstem_agent.py compare  agents/ --case "MeetingCost:people=6,minutes=45"
python3 brainstem_agent.py emit     agents/ -o harness_app.py
python3 brainstem_agent.py run      agents/ --prompt "what does a 6-person 45-min meeting cost?"
```

---

## The finding this is built on

A RAPP agent has a `name`, a `metadata` dict carrying a JSON Schema, and a `perform(**kwargs)`. An Agent Framework tool wants a name, a description, a JSON Schema, and a callable.

**They are the same four things.** Measured against `agent-framework 1.13.0` / `agent-framework-github-copilot 1.0.1`:

```python
tool(fn, name=agent.name, description=..., schema=agent.metadata["parameters"])
```

accepts a RAPP schema **byte-identical**. Nothing is translated, so nothing can drift.

That is the whole design, and it matters more than convenience. A converter that **re-implemented** `perform()` in the harness idiom would make a side-by-side benchmark meaningless — you would be measuring the transcription, not the harness. Here the *same function object* runs on both sides and the *same schema* describes it, so a difference in results is a difference in the harness.

The emitted app **imports** each agent from its original file rather than copying it, for the same reason: a generated copy drifts the first time anyone edits either side.

## Verified end to end

Against the two agents in `~/.copilot/skills/rapp/agents/`:

| path | result |
|---|---|
| native brainstem `perform()` | `6 people x 45 min x $120/hr loaded = $540.00` |
| harness tool, invoked directly | identical |
| **real Copilot agent loop**, model-driven | identical |

```
  2/2 identical of the judgeable — adapter faithful
```

## Three verdicts, each observed firing

A comparison that has never detected a mismatch is indistinguishable from one that cannot.

| verdict | when | proven by |
|---|---|---|
| `MATCH` | faithful adapter, deterministic agent | the real agents above |
| `DIFFER` | adapter changed behaviour | deliberately corrupting `to_tool` to uppercase results — caught |
| `INCONC` | agent is not deterministic | a deliberately stateful agent |

That third one is a flaw found in **this tool**, by testing it. `compare` necessarily calls `perform()` twice, so a stateful agent returns two different answers and the difference was being blamed on the adapter — a confident, wrong accusation. It now probes the agent against *itself* first, and reports **no conclusion** rather than an accusation it cannot support.

## What needs credentials, and what doesn't

`discover`, `emit` and `compare` need **no** credentials and no network. They exercise the adapter only.

`run` drives the real Copilot loop and needs an authenticated Copilot CLI.

Keeping that line visible is deliberate: most of what goes wrong in a port is provable without a model in the way, and an auth failure should never be mistaken for a broken port.

## Side-by-side signal

`compare` reports timing per case. From the run above, on this machine:

```
native  (0.01ms)   harness (0.19ms)     steady state
                   harness (52.9ms)     first call — SDK warm-up, not per-call cost
```

The native brainstem is a direct Python call; the harness adds a tool-dispatch layer. Both are noise next to a model call, which is the honest framing — the harness is not competing with `perform()`, it is competing with *the rest of what a brainstem has to build itself*: permissions, sessions, MCP, streaming, observability.

## What the harness gives you that the brainstem doesn't

From the SDK, verified present in `GitHubCopilotOptions`:

```
system_message, cli_path, model, timeout, log_level, on_permission_request,
mcp_servers, provider, instruction_directories, skill_directories,
disabled_skills, base_directory, on_pre_tool_use, on_function_approval
```

Human-in-the-loop approval per action, MCP servers, session resume by id, OpenTelemetry tracing, and instruction directories. A RAPP brainstem gets single-file portability and zero install; this is the trade being measured.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install agent-framework-github-copilot
```

Python ≥3.10. `run` additionally needs the Copilot CLI on `PATH` and an active Copilot subscription.

## A bug this found in itself

The self-hosting claim below was false when first written — `brainstem_agent.py` could not
convert itself, failing with `AttributeError: 'NoneType' object has no attribute '__dict__'`.

The cause was general, not cosmetic. Loading an agent file via `exec_module` without first
registering it in `sys.modules` breaks **any agent that uses `@dataclass`**: dataclasses
resolve a field's type through `sys.modules.get(cls.__module__).__dict__`, which is `None`
for a module executed but never registered. Every such agent would have been reported
unusable, with an error naming nothing useful.

Fixed, and verified against a separate dataclass-using agent as well as this file.

## It is itself a RAPP agent

`brainstem_agent.py` carries a `name`, a `metadata` schema and a `perform()` — so it converts its own kind, including itself. That is not a trick; it is the cheapest available proof that the contract it targets is the contract it honours.

MIT © RAPP ecosystem — see the [map](https://github.com/kody-w/rapp-map).
