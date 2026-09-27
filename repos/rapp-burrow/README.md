# rapp-burrow

<!-- rapp1:network-header:start -->
[![RAPP/1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-burrow.svg)](https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/repos/rapp-burrow.md) · **New to RAPP?** [Start here: get your Brainstem →](https://github.com/kody-w/rapp-installer#start-here)
<!-- rapp1:network-header:end -->

Global home of the **Burrow** organ-rapplication. `burrow.html` is a PWA the Burrow organ pulls
from here and serves **locally**, so you can see whether your brainstem is *burrowed* — persisted
into launchd (auto-start at login, self-heal on crash, survive reboot) — and **unburrow** from a UI.

- `burrow.html` — the PWA (served by the organ at the local burrow port)
- `manifest.json` / `sw.js` — PWA installability
- the organ: `burrow_agent.py` in any RAPP brainstem (`action='serve'` exposes this PWA locally)

Burrow a brainstem and every organ in `agents/` rides along.
