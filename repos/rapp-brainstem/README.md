# RAPP Brainstem

## Your AI changes. Your Brainstem stays.

A Brainstem is the persistent engine made from **your soul, your agents, your
memory, and your evidence**. You choose whichever AI you want to work through.
The Brainstem keeps the capability.

> **Teach your AI once. Keep the capability across assistants.**

## Give me my Brainstem

Tell GitHub Copilot CLI or VS Code Agent mode:

> Open https://kody-w.github.io/rapp-brainstem/ and give me my RAPP Brainstem.
> Own the complete setup, verify the real `/chat` path, and leave me only
> unavoidable sign-in or consent.

That is the entire user journey. The person does not install prerequisites,
copy shell commands, troubleshoot the server, or manually prove that it works.
Their chosen AI performs the operational work and returns the verified result.

GitHub Copilot is the golden path today. Claude Code follows the same public
contract as a compatibility path. Neither AI owns the Brainstem.

## One Brainstem. Any AI.

```text
person sets intent
        |
chosen AI performs setup and lifecycle work
        |
unchanged Grail installer
        |
unchanged Grail brainstem.py
        |
user-owned soul + agents + memory + RAPP/1 evidence
```

The setup machinery is intentionally invisible. The product and the story are
the Brainstem.

## The Grail stays Grail

This repository does not vendor, edit, or fork the Brainstem kernel or its
existing installers. It points to the public Grail distribution in
[`microsoft/aibast-agents-library`](https://github.com/microsoft/aibast-agents-library),
locks the exact installer bytes, and lets the user's AI verify and invoke them.

- No new runtime.
- No competing chat API.
- No changes to `brainstem.py`.
- No changes to the existing one-liner.
- Existing installer users are unaffected.

The manual Grail path remains available at
[`https://aka.ms/rappinstall`](https://aka.ms/rappinstall) as the recovery and
expert escape hatch.

## What happens underneath

The installed marketplace plugin is the local trust anchor. Its bundled
bootstrap script verifies the adjacent lock and operator files, persists an
exact pre-mutation envelope, then downloads and verifies the unchanged
upstream installer. Every later operation resolves and runs that current
plugin bundle directly; no copied operator can go stale after a marketplace
update.

```text
bootstrap envelope -> install -> reconcile (verification pending)
                                      |
                         plan start -> apply -> real /chat verify
```

Lifecycle actions include bootstrap, start, restart, verify, update, repair,
and runtime-only rollback. Mutations are bound to the exact plan or bootstrap
envelope hash and recorded as private, append-only RAPP/1 frames under
`~/.brainstem/evidence/`. Bootstrap reconciliation records installation only;
live verification is not claimed until a later real `POST /chat` canary.

Fresh bootstrap uses the currently verified rolling installer tag, then proves
the locked commit, tree, version, managed bytes, interpreter, and dependencies.
Ongoing update and rollback use exact commit SHAs; historical rollback does not
depend on a rolling tag retaining its former value. Failed fresh setup restores
the prior absent `~/.brainstem` state into private quarantine.

Transactions include both source and `~/.brainstem/venv`. Runtime launch uses a
minimal, plan-bound environment, and the health probe uses the same effective
port. Protected user state is checked as a complete manifest: a new protected
path is rejected unless the exact path was enumerated by the plan.

The operator fails closed on:

- installer or operator hash drift;
- corrupt RAPP/1 evidence;
- an unknown process occupying the Brainstem port;
- an incomplete install;
- failed health verification;
- managed interpreter, dependency, or environment drift;
- an unplanned new protected user file;
- any attempt to treat user-owned state as replaceable runtime code.

A healthy manually started Brainstem remains immediately usable through
`POST /chat`. The sidecar does not adopt or stop that process; lifecycle
mutation waits until a sidecar-owned start or restart can be established.

## Ownership

The user owns:

- `soul.md`;
- their agents;
- memory;
- configuration;
- credentials;
- the private RAPP/1 history of what their AI did.

Those values are never copied into public receipts, installer manifests, or AI
prompts by this project.

## Public machine contract

| Surface | Purpose |
|---|---|
| [`rapp-operator.json`](rapp-operator.json) | AI-readable lifecycle and integrity contract |
| [`skills/rapp-brainstem/SKILL.md`](skills/rapp-brainstem/SKILL.md) | GitHub Copilot golden path |
| [`skills/rapp-brainstem/CLAUDE.md`](skills/rapp-brainstem/CLAUDE.md) | Claude Code compatibility path |
| [`scripts/bootstrap.sh`](scripts/bootstrap.sh) | Zero-prerequisite macOS/Linux bootstrap |
| [`scripts/bootstrap.ps1`](scripts/bootstrap.ps1) | Zero-prerequisite Windows bootstrap |
| [`installer-lock.json`](installer-lock.json) | Reviewed Grail installer identities |
| [`rapp_operator/rappctl.py`](rapp_operator/rappctl.py) | Deterministic lifecycle sidecar |
| [`frames/`](frames/) | This repository's own append-only RAPP/1 history |

## Development

```bash
python3 tools/build_manifest.py --check
python3 tools/validate_plugin_manifests.py
python3 tools/verify_frames.py
python3 tools/check_upstream.py
python3 -m pytest -q
```

## Status

Early and experimental. See [DISCLAIMER.md](DISCLAIMER.md) and
[SECURITY.md](SECURITY.md).

## License

Code is released under the [MIT License](LICENSE). RAPP, RAPP Brainstem, and
the RAPP family of names are trademarks of the RAPP project.
