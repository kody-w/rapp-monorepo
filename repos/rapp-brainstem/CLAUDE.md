# RAPP Brainstem

This repository is the isolated public operator around the unchanged RAPP
Brainstem Grail.

## Non-negotiable boundary

- Never edit, vendor, or fork `brainstem.py`.
- Never edit or republish the upstream one-liner installers.
- Installer URLs and hashes come from `installer-lock.json`.
- The currently installed marketplace plugin bundle is lifecycle authority;
  never execute a stale copied operator from user state.
- `rapp_operator/` may inspect, plan, invoke, and verify the upstream installer
  but must not become a second runtime.
- The unchanged Brainstem `POST /chat` wire remains the execution surface.
- Soul, agents, memory, config, and credentials remain user-owned.

GitHub Copilot is the product golden path. Claude Code is a compatibility
operator and must follow the same local-plugin trust contract and acceptance
gates.

## Commands

```bash
python3 tools/build_manifest.py --check
python3 tools/validate_plugin_manifests.py
python3 tools/verify_frames.py
python3 -m pytest -q
```
