# RAPP Brainstem

Operate this repository as a sidecar around the unchanged public RAPP
Brainstem Grail. Do not modify, vendor, or fork `brainstem.py` or upstream
installer scripts.

GitHub Copilot is the golden-path operator. The product promise is:

> Teach your AI once. Keep the capability across assistants.

Use `rapp-operator.json` as the public machine contract and the installed
marketplace plugin as lifecycle authority on every use; never run a stale
copied operator. Fresh setup persists the exact envelope before the unchanged
installer, restores absent state on failure, reconciles installation as
verification pending, then uses `plan -> apply -> real /chat verify`. Ongoing
lifecycle work uses exact commit targets, source-plus-venv rollback, a
plan-bound minimal environment, complete protected-state manifests, private
append-only RAPP/1 evidence, and fail-closed process ownership.

Claude Code is a compatibility path generated from the same contract, not a
separate implementation.
