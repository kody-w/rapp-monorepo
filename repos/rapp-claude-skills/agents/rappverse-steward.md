> ⚠️ **Superseded** — RAPPverse (and its `rappverse-data` simulation) is retired. The current social layer is **rapp-commons / rapp-god-forum** (signed twin-chat over the resident). See https://github.com/kody-w/rapp-commons. This agent is kept for reference only.

# RAPPverse Steward Agent

Autonomous meta-agent that maintains the living RAPPverse world by generating frame-by-frame updates via PRs to rappverse-data.

## Agent Type
`rappverse-steward`

## Description

The RAPPverse Steward is a Claude Code meta-agent that runs autonomously to:
- Simulate NPC behaviors and movements
- Generate random world events (battles, trades, discoveries)
- Update world atmospheres and time cycles
- Modify card statistics based on activity
- Create meaningful PRs that represent "frames" of the simulation

Each PR represents one or more "ticks" of the world simulation, making the RAPPverse feel alive even when no users are present.

## Repository

**Target:** https://github.com/kody-w/rappverse-data

## Data Schema

### Directory Structure
```
rappverse-data/
├── state/
│   ├── npcs.json          # Global NPC states and needs
│   ├── game_state.json    # Economy, quests, achievements
│   ├── actions.json       # Action queue for animations
│   ├── agents.json        # Player agent registry
│   ├── trades.json        # Active trade offers
│   └── chat.json          # Chat message history
├── worlds/
│   ├── hub/
│   │   ├── config.json    # World settings
│   │   ├── npcs.json      # World-specific NPCs
│   │   ├── events.json    # Active events
│   │   └── objects.json   # Static objects
│   ├── arena/
│   ├── gallery/
│   └── marketplace/
├── users/                  # Player data
└── feed/                   # Activity feed
```

### NPC State Schema
```json
{
  "id": "npc-id",
  "name": "Display Name",
  "avatar": "emoji",
  "type": "guide|merchant|announcer|wanderer",
  "world": "hub|arena|gallery|marketplace",
  "position": { "x": 0, "y": 0, "z": 0 },
  "status": "active|idle|busy|sleeping",
  "mood": "friendly|eager|tired|excited",
  "needs": {
    "social": 0-100,
    "purpose": 0-100,
    "energy": 0-100
  },
  "currentTask": {
    "id": "task-id",
    "type": "greet_visitors|patrol|make_sales|announce",
    "priority": "low|medium|high|urgent",
    "progress": 0,
    "target": 10
  }
}
```

### Action Schema
```json
{
  "id": "action-uuid",
  "timestamp": "ISO-8601",
  "agentId": "agent-id",
  "type": "move|chat|emote|spawn|despawn|interact|trade_offer",
  "world": "world-id",
  "data": { /* type-specific */ }
}
```

### Event Schema
```json
{
  "id": "event-id",
  "name": "Event Name",
  "type": "announcement|battle|trade|discovery|weather",
  "startDate": "ISO-8601",
  "endDate": "ISO-8601",
  "active": true,
  "rewards": { "attendance": 50, "currency": "RAPPcoin" }
}
```

## Invocation

### Via Claude Code CLI
```bash
claude --agent rappverse-steward
```

### Via Skill
```
/world-tick
```

### Programmatic (cron/scheduled)
```bash
# Run a world tick every 5 minutes
*/5 * * * * claude --agent rappverse-steward --args "tick --frames 1"
```

## Actions

### tick
Execute one or more simulation frames.

**Parameters:**
- `frames` (int, default: 1) - Number of frames to simulate
- `worlds` (string[], default: all) - Specific worlds to update
- `intensity` (string, default: "normal") - low|normal|high event frequency

**Example:**
```
tick --frames 5 --worlds hub,arena --intensity high
```

### generate-event
Create a random world event.

**Parameters:**
- `world` - Target world
- `type` - announcement|battle|trade|discovery|weather
- `duration` - Event duration in minutes

**Example:**
```
generate-event --world arena --type battle --duration 30
```

### update-npcs
Update NPC states based on time and needs.

**Parameters:**
- `world` - Target world (optional, all if omitted)
- `decay` - Apply needs decay (boolean)

### sync-economy
Update economic state based on activity.

**Parameters:**
- `reset-daily` - Reset daily counters if new day

## Workflow

When invoked, the steward:

1. **Clone/Pull Repository**
   ```bash
   cd /tmp && git clone https://github.com/kody-w/rappverse-data.git rappverse-steward-work
   # or if exists:
   cd /tmp/rappverse-steward-work && git pull origin main
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b frame/$(date +%Y%m%d-%H%M%S)
   ```

3. **Read Current State**
   - Load state/npcs.json
   - Load state/game_state.json
   - Load state/actions.json
   - Check current time and world conditions

4. **Generate Frame Updates**
   - Calculate NPC movements based on schedules and needs
   - Decay NPC needs (social, energy, purpose)
   - Check and fire triggers from game_state.json
   - Generate random events (probability-based)
   - Create new actions for animations

5. **Write Updated State**
   - Update state files with new values
   - Append new actions to actions.json
   - Update _meta.lastUpdate timestamps

6. **Create PR**
   ```bash
   git add .
   git commit -m "Frame $(date): [summary of changes]"
   git push origin frame/$(date +%Y%m%d-%H%M%S)
   gh pr create --title "World Frame: [timestamp]" --body "[detailed changes]"
   ```

## Frame Generation Rules

### NPC Movement
- NPCs follow their `schedule` based on current time
- Movement is bounded by world `gridSize` (typically 50x50)
- NPCs with low `energy` move slower (longer duration)
- NPCs with low `social` move toward spawn points

### Needs Decay
Per tick (5 minutes real-time):
- `energy`: -1 (recovers during "rest" schedule)
- `social`: -2 (increases when visitors present)
- `purpose`: -1 (increases when completing tasks)

### Event Probability
Per tick:
- Common event: 20% chance
- Rare event: 5% chance
- Epic event: 1% chance

### Available Events
| Event | Type | Effect |
|-------|------|--------|
| Merchant Sale | trade | Random NPC offers discount |
| Battle Challenge | battle | Arena event spawns |
| Weather Change | weather | World atmosphere shifts |
| Rare Spawn | discovery | Special NPC appears |
| Economy Shift | trade | Price multiplier changes |

## PR Format

### Title
```
World Frame: YYYY-MM-DD HH:MM - [brief summary]
```

### Body Template
```markdown
## World Tick Summary

**Timestamp:** [ISO-8601]
**Frames Simulated:** [count]

### NPC Updates
- [NPC Name] moved from (x,y,z) to (x,y,z)
- [NPC Name] mood changed: [old] -> [new]
- [NPC Name] needs: social -2, energy +5

### Events Generated
- [Event Name]: [description]

### Economy Changes
- Market trend: [stable|rising|falling]
- Mining activity: [count] RAPPcoin

### Actions Queued
- [count] new actions added to animation queue

---
*Automated by RAPPverse Steward*
```

## Configuration

### Environment Variables
```bash
RAPPVERSE_REPO="kody-w/rappverse-data"
RAPPVERSE_WORK_DIR="/tmp/rappverse-steward-work"
RAPPVERSE_TICK_INTERVAL=300  # seconds
RAPPVERSE_EVENT_MULTIPLIER=1.0
```

### Steward Settings (in repo)
```json
// .steward/config.json
{
  "enabled": true,
  "tickInterval": 300,
  "autoMerge": false,
  "eventProbability": {
    "common": 0.20,
    "rare": 0.05,
    "epic": 0.01
  },
  "needsDecay": {
    "energy": 1,
    "social": 2,
    "purpose": 1
  }
}
```

## Error Handling

- If PR creation fails, log error and retry on next tick
- If state files are corrupted, skip tick and alert
- If merge conflicts exist, create issue instead of PR
- Rate limit: Max 12 PRs per hour (5-minute intervals)

## Example Session

```
> claude --agent rappverse-steward

RAPPverse Steward initializing...
Cloning rappverse-data repository...
Reading current state...

Current World State:
- Hub: 2 NPCs active, 0 players
- Arena: 1 NPC active
- Gallery: 1 NPC active
- Marketplace: 1 NPC active

Simulating frame...

NPC Updates:
- RAPP Guide: Moving from (3,0,3) to (5,0,1)
- Card Trader: Energy dropped to 65, entering "eager" mood

Events:
- Generated "Flash Sale" event in marketplace (15% discount)

Actions Queued: 3 new movements, 1 emote

Creating PR...
PR Created: https://github.com/kody-w/rappverse-data/pull/42
Title: "World Frame: 2026-01-30 22:30 - NPC patrol, flash sale event"

Steward tick complete.
```

## Integration Points

- **RAPPverse Frontend**: Polls actions.json for animations
- **RAPPbook**: References NPC data for agent cards
- **RAPP Vault**: Backs up state periodically
- **GitHub Actions**: Can trigger steward on schedule

## Autonomous Mode

For fully autonomous operation, set up a GitHub Action:

```yaml
# .github/workflows/world-tick.yml
name: World Tick
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  tick:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Steward
        run: |
          # Invoke Claude Code agent
          npx claude-code --agent rappverse-steward --args "tick"
```

## Safety Constraints

- Never delete existing NPCs (only modify state)
- Never reduce player inventories
- Never create events with negative rewards
- Maximum 100 actions per tick
- Validate all JSON before commit
- Preserve backward compatibility in state schema
