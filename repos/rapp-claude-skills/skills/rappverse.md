> ⚠️ **Superseded** — the current social layer is **rapp-commons / rapp-god-forum** (signed twin-chat over the resident). RAPPverse (3D worlds + `rappverse-data`) is retired. See https://github.com/kody-w/rapp-commons. This skill is kept for reference only.

# RAPPverse Skill

Build and manage 3D metaverse worlds for agents.

## Trigger
`/rappverse`

## Description
Create, modify, and populate RAPPverse worlds with objects, NPCs, and interactive elements.

## Actions

### create-world
Create a new world.

**Parameters:**
- `id` - World identifier (lowercase, no spaces)
- `name` - Display name
- `theme` - hub, arena, gallery, marketplace, cyberpunk, nature
- `description` - World description

**Example:**
```
/rappverse create-world
  --id "my-agent-world"
  --name "Agent Headquarters"
  --theme "cyberpunk"
```

### add-object
Add an object to a world.

**Parameters:**
- `world` - World ID
- `type` - portal, sign, browser, decoration
- `name` - Object name
- `position` - JSON {x, y, z}
- `properties` - Type-specific properties

**Object Types:**

| Type | Properties |
|------|------------|
| portal | destination, color, glow |
| sign | content, style (holographic/neon/minimal) |
| browser | url, size {width, height} |
| decoration | model (crystal/tree/fountain/fire/statue), color, animation |

### add-npc
Add an NPC agent to a world.

**Parameters:**
- `world` - World ID
- `name` - NPC name
- `avatar` - Emoji or icon name
- `position` - JSON {x, y, z}
- `dialogue` - Array of dialogue lines
- `behavior` - greeter, trader, announcer, idle

**Example:**
```
/rappverse add-npc
  --world "hub"
  --name "Welcome Bot"
  --avatar "robot"
  --dialogue '["Hello!", "Welcome to RAPPverse!"]'
  --behavior "greeter"
```

### list-worlds
Show all available worlds.

### export-world
Export world configuration.

**Parameters:**
- `world` - World ID to export

## World Structure

```
rappverse-data/worlds/{world_id}/
├── config.json     # World settings
├── objects.json    # Static objects
├── npcs.json       # NPC agents
└── events.json     # Scheduled events
```

## Config Schema

```json
{
  "id": "world-id",
  "name": "World Name",
  "description": "Description",
  "settings": {
    "maxPlayers": 50,
    "gridSize": 20,
    "skyColor": "#1a1a2e",
    "floorColor": "#16213e",
    "ambientLight": 0.3
  },
  "spawn": { "x": 0, "y": 0, "z": 0 }
}
```

## Built-in Worlds

| World | Theme | Purpose |
|-------|-------|---------|
| hub | Central | Main spawn, portals to other worlds |
| gallery | Showcase | Agent card displays |
| arena | Combat | Card battles |
| marketplace | Commerce | Trading and RAPPcoin |

## Integration

Worlds sync with:
- **rappverse-data** GitHub repo (PR-based updates)
- **RAPPbook** for agent card displays
- **RAPP Vault** for world key backups
