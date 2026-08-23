# RAPP Desktop

RAPP Desktop is the resident Electron companion for the RAPP Brainstem. It
keeps chat, projects, the agent store, and the implementation hub in one
local-first desktop experience while the Brainstem remains the engine of
record.

## Companion behavior

- Starts as a single-instance desktop companion and stays available from the
  system tray when its window is closed.
- Attaches to `RAPP_BRAINSTEM_URL` or the global Brainstem on
  `http://127.0.0.1:7071`.
- Wakes an installed global Brainstem automatically. A bundled legacy engine
  remains available as an offline-compatible fallback.
- Sends chat through the RAPP/1 `/chat` contract without exposing Brainstem
  secrets to the renderer.
- Browses and installs RAPP Store agents and skills, clones Hub
  implementations, and manages projects under `~/.rapp`.

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ Electron main process                                      │
│  lifecycle · tray · Brainstem client · filesystem · Git     │
├──────────────────── typed, capability-scoped IPC ───────────┤
│ sandboxed preload                                           │
├──────────────────────── contextBridge ──────────────────────┤
│ React renderer                                              │
│  chat · store · hub · projects · settings                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              └── RAPP/1 → Brainstem /chat
```

The renderer has no Node.js integration, no generic IPC primitive, and no
direct network access in packaged builds. The main process validates every
IPC sender and input, restricts file operations to RAPP-owned directories,
allows only HTTPS external navigation, and denies renderer permission
requests.

## Development

Prerequisites: Node.js 20+ and Python 3.

```bash
npm install
npm run dev
```

`npm run dev` starts Vite and Electron together. Closing the window hides the
companion; use the tray menu to quit it.

## Build and test

```bash
npm run typecheck
npm test
npm run dist
```

`npm run dist` creates platform installers in `release/` with
`electron-builder`.

## Install from source

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/kody-w/RAPP_Desktop/main/install/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/kody-w/RAPP_Desktop/main/install/install.ps1 | iex
```

## RAPP ecosystem

| Component | Description |
|---|---|
| [RAPP Desktop](https://github.com/kody-w/RAPP_Desktop) | Resident AI companion |
| [RAPP Installer](https://github.com/kody-w/rapp-installer) | Brainstem bootstrapper and Azure deploy |
| [RAPP Hub](https://github.com/kody-w/RAPP_Hub) | Implementation registry |
| [RAPP Store](https://github.com/kody-w/RAPP_Store) | Agent and skill packages |

## License

Apache 2.0
