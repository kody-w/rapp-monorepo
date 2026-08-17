# The agent contract — `rapp-agent/1.0`

A RAPP agent is **one file**. Drop a `*_agent.py` into the agents folder and it
is live on the next request. That is the whole deployment story, and everything
below exists to keep it true as the estate grows.

## The manifest

Every agent declares a top-level `__manifest__`:

```python
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@openrappter/shell",        # @scope/slug
    "version": "1.0.0",
    "display_name": "Shell",
    "description": "Run a shell command and return its output.",
    "author": "Kody Wildfeuer",
    "ring": "ga",                        # ga | public-preview | private-preview | frontier
    "capabilities": ["filesystem-write", "process-exec"],
    "tags": ["openrappter", "shell"],
    "category": "system",
    "quality_tier": "official",
    "requires_env": [],
}
```

`schema`, `name`, `version`, `description` and `capabilities` are required. The
name is `@scope/slug`, lowercase, hyphen-separated.

## Capabilities are verified, never trusted

There are five classes:

| Capability | What it covers |
|---|---|
| `network` | sockets, HTTP clients, SDKs that reach out |
| `process-exec` | `subprocess`, `os.system`, `pty` |
| `credential-access` | `os.getenv`, `keyring`, `netrc`, `getpass` |
| `filesystem-write` | `shutil`, `os.remove`, `Path.write_text` |
| `dynamic-code` | `eval`, `exec`, `pickle`, `ctypes`, `importlib` |

**A declaration is not taken at face value.** An enterprise strain reads the
agent's syntax tree and compares what the code can actually reach against what
it declared. An allowlist that trusts a manifest field is an allowlist of
promises.

Two failure modes, both checked:

- **Under-declaring** is a refusal. An agent that calls `subprocess.run` while
  declaring nothing is not admitted — at approval time, and again at load time.
- **Over-declaring** is a slow poison. An agent claiming `process-exec` it never
  uses gets withheld by an organisation that forbids `process-exec`, for no
  reason, and its owner learns to distrust every declaration.

The honest way to produce the list is to derive it from the syntax tree rather
than write it by hand. That is how all fifteen OpenRappter agents got theirs.

## Reading the environment *is* credential access

`os.getenv("PORT")` and `os.getenv("API_KEY")` are the same capability, and only
the agent's author knows which one it is. Declaring it costs one word.

## Portability

An agent must load with nothing but the base class present. An import inside a
function, or one wrapped in `try/except ModuleNotFoundError`, is fine — the file
still loads alone, which is the property that matters:

```python
try:
    from openrappter.security.exec_safety import ExecSafety
except ModuleNotFoundError:
    # The brainstem loads single-file agents in isolation. Keep the other
    # actions discoverable; fail closed if the safety module is absent.
    ExecSafety = None
```

An unguarded module-level import of anything deeper than the base class turns a
cartridge into a plugin.

## The kernel never changes to accommodate an agent

The brainstem is a loader, an LLM loop, and a response splitter. Anything a
`*_agent.py` can serve does not belong in the kernel. This is what lets one
kernel serve every deployment, including locked-down ones — see
[enterprise.md](enterprise.md).

## Implementations

- [kody-w/rapp-1](https://github.com/kody-w/rapp-1) — the spec and reference
- [kody-w/openrappter](https://github.com/kody-w/openrappter) — 15 conformant agents
- [kody-w/rapp-light](https://github.com/kody-w/rapp-light) — the verifier, as an enterprise strain
