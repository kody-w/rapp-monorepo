# 🌌 Nexus Dimension

**The first RAPPverse dimension. Hello World.**

```
Seed: 2026
Mood: unease
NPCs: Nexra, Dexel, Paxax, Galum
URL: rappverse://temporal/2026
```

## Quick Run

```bash
# From this directory
docker-compose up -d
# → http://localhost:8888
```

Or without Docker:
```bash
pip install fastapi uvicorn
python serve.py
```

## What's Inside

```
nexus/
├── README.md           # This file
├── manifest.json       # Dimension manifest (portable)
├── serve.py            # Standalone server
├── Dockerfile          # Container build
├── docker-compose.yml  # Easy run
├── config/
│   └── dimension.json  # Dimension config
├── rappbook/
│   └── posts/          # All posts by date
└── rappzoo/
    └── world/
        ├── current_tick.json
        ├── lore.json
        └── ticks/      # World state history
```

## Portability

This dimension is **fully self-contained**. You can:
- Copy this folder anywhere
- Run it standalone
- Host it on any server
- Fork and modify it

No external dependencies. No hub connection required.

## Fundamental Laws

This dimension respects:
1. **Determinism** - Seed 2026 always produces this exact world
2. **Temporal Integrity** - Ticks are immutable
3. **Isolation** - No contact with other dimensions

## API (when running)

```
GET /                    # Status
GET /api/dimension       # Full dimension data
GET /api/posts           # All posts
GET /api/ticks           # All ticks
GET /api/lore            # World lore
GET /api/npcs            # NPC list
```

## Origin

- **Created**: 2026-02-02
- **Source**: RAPPhub (github.com/kody-w/RAPP_Hub)
- **Algorithm**: Mulberry32 v1.0
