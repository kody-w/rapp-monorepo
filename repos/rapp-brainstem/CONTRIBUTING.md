# Contributing

Changes must preserve these invariants:

1. The upstream Grail Brainstem kernel remains unchanged.
2. Existing upstream one-liner installers remain unchanged.
3. GitHub Copilot is the golden-path operator.
4. Claude Code uses the same canonical contract as a compatibility path.
5. Every lifecycle mutation is plan-hash-bound and recorded as RAPP/1.
6. User-owned soul, agents, memory, config, and credentials are never silently
   modified or included in public evidence.
7. Failures are explicit; no success-shaped fallback is accepted.

Before opening a pull request:

```bash
python3 tools/build_manifest.py --check
python3 tools/verify_frames.py
python3 -m pytest -q
```
