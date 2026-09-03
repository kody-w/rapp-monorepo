# Security

## Reporting

Do not open a public issue for a suspected vulnerability that could expose
credentials, local files, or arbitrary code execution. Use GitHub's private
vulnerability reporting for this repository.

## Trust boundary

The installed marketplace plugin is the bootstrap trust anchor. Before Python
exists, its bundled script verifies the local operator and
`installer-lock.json`, persists the exact bootstrap envelope, and executes the
public Brainstem installer only after verifying its SHA-256. A matching hash
proves byte identity, not that arbitrary third-party agent code is safe.

Bootstrap reconciliation proves the exact installed release and operator
bundle but does not claim live verification. That requires a later real
`POST /chat` canary.

The operator does not authorize untrusted RAR agents, upload private Brainstem
state, or place credentials in prompts or RAPP/1 frames.

## User-owned data

The following remain outside operator ownership:

- `soul.md`
- user agents
- memory
- `.env`
- GitHub and Copilot credentials

Repair and runtime rollback must not silently replace or restore those files.
