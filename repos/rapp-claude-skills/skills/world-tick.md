> ⚠️ **Superseded** — RAPPverse (and its `rappverse-data` simulation) is retired. The current social layer is **rapp-commons / rapp-god-forum** (signed twin-chat over the resident). See https://github.com/kody-w/rapp-commons. This skill is kept for reference only.

# World Tick Skill

Simulate one "frame" of the RAPPverse world and create a PR with the changes.

## Trigger
`/world-tick`

## Description

The world-tick skill represents one simulation cycle of the RAPPverse metaverse. It updates NPC positions, generates random events, modifies world atmospheres, and queues actions for the animation system. All changes are submitted as a PR to the rappverse-data repository.

## Quick Start

```bash
# Run a single tick
/world-tick

# Run multiple frames
/world-tick --frames 5

# Target specific world with high event chance
/world-tick --world arena --intensity high
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | int | 1 | Number of frames to simulate |
| `world` | string | all | Specific world to update (hub, arena, gallery, marketplace) |
| `intensity` | string | normal | Event frequency: low (5%), normal (20%), high (50%) |
| `dry-run` | bool | false | Preview changes without creating PR |
| `auto-merge` | bool | false | Auto-merge PR if no conflicts |

## Workflow

### 1. Setup Repository
```bash
# Clone if not exists, otherwise pull latest
WORK_DIR="/tmp/rappverse-tick-$(date +%s)"
git clone https://github.com/kody-w/rappverse-data.git $WORK_DIR
cd $WORK_DIR
git checkout -b tick/$(date +%Y%m%d-%H%M%S)-$(openssl rand -hex 4)
```

### 2. Load Current State
Read and parse:
- `state/npcs.json` - NPC positions, needs, moods
- `state/game_state.json` - Economy, triggers, quests
- `state/actions.json` - Action queue
- `worlds/{world}/events.json` - Active events

### 3. Calculate Time Delta
```javascript
const lastUpdate = new Date(state._meta.lastUpdate);
const now = new Date();
const deltaMinutes = (now - lastUpdate) / 60000;
const tickCount = Math.floor(deltaMinutes / 5); // 5-min ticks
```

### 4. Update NPCs

For each NPC:

**Position Update:**
```javascript
// Check schedule for current activity
const hour = now.getHours();
const activity = npc.schedule.find(s => isInTimeRange(hour, s.time));

// Generate movement toward activity area
if (activity.activity === "patrol") {
  newPos = randomPositionInArea(activity.area, world.gridSize);
} else if (activity.activity === "greet") {
  newPos = nearSpawnPoint(world.spawn);
}
```

**Needs Decay:**
```javascript
npc.needs.energy = Math.max(0, npc.needs.energy - (tickCount * 1));
npc.needs.social = Math.max(0, npc.needs.social - (tickCount * 2));
npc.needs.purpose = Math.max(0, npc.needs.purpose - (tickCount * 1));

// Recover during rest
if (activity.activity === "rest") {
  npc.needs.energy = Math.min(100, npc.needs.energy + (tickCount * 5));
}
```

**Mood Update:**
```javascript
if (npc.needs.energy < 30) npc.mood = "tired";
else if (npc.needs.social < 30) npc.mood = "lonely";
else if (npc.needs.purpose < 30) npc.mood = "bored";
else npc.mood = "friendly";
```

### 5. Generate Events

Roll for events based on intensity:
```javascript
const roll = Math.random();
const threshold = {
  low: { common: 0.05, rare: 0.01, epic: 0.001 },
  normal: { common: 0.20, rare: 0.05, epic: 0.01 },
  high: { common: 0.50, rare: 0.15, epic: 0.05 }
}[intensity];

if (roll < threshold.epic) generateEpicEvent();
else if (roll < threshold.rare) generateRareEvent();
else if (roll < threshold.common) generateCommonEvent();
```

**Event Types:**

| Type | Examples | Duration |
|------|----------|----------|
| Common | NPC emote, small price change, weather shift | 5-15 min |
| Rare | Flash sale, battle challenge, rare NPC spawn | 30-60 min |
| Epic | Boss event, economy boom, world-wide celebration | 2-24 hours |

### 6. Queue Actions

Generate actions for the animation system:
```json
{
  "id": "action-{uuid}",
  "timestamp": "{ISO-8601}",
  "agentId": "{npc-id}",
  "type": "move",
  "world": "{world-id}",
  "data": {
    "from": { "x": 3, "y": 0, "z": 3 },
    "to": { "x": 7, "y": 0, "z": -2 },
    "duration": 2500
  }
}
```

**Action Types:**
- `move` - NPC position change
- `emote` - wave, think, dance, celebrate, clap, bow
- `chat` - NPC dialogue
- `spawn` - NPC appears
- `despawn` - NPC leaves

### 7. Check Triggers

Evaluate game_state triggers:
```javascript
for (const trigger of gameState.triggers) {
  if (!trigger.fired && evaluateCondition(trigger.condition)) {
    executeTriggerAction(trigger);
    trigger.fired = true;
  }
}
```

### 8. Update Timestamps
```javascript
state._meta.lastUpdate = new Date().toISOString();
state._meta.lastProcessedId = lastActionId;
```

### 9. Create PR

```bash
git add state/ worlds/
git commit -m "$(cat <<'EOF'
World Tick: $(date -u +%Y-%m-%dT%H:%M:%SZ)

NPCs Updated: [count]
Events Generated: [count]
Actions Queued: [count]

Co-Authored-By: RAPPverse Steward <steward@rappverse.ai>
EOF
)"

git push origin tick/$(date +%Y%m%d-%H%M%S)-$(openssl rand -hex 4)

gh pr create \
  --title "World Tick: $(date +%Y-%m-%d\ %H:%M) UTC" \
  --body "$(cat <<'EOF'
## Tick Summary

**Timestamp:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Frames:** [count]
**Intensity:** [level]

### Changes

#### NPC Updates
[list of NPC changes]

#### Events
[list of generated events]

#### Actions Queued
[count] new actions for animation

---
*Automated by /world-tick*
EOF
)"
```

## Output

### Success Response
```json
{
  "status": "success",
  "pr_url": "https://github.com/kody-w/rappverse-data/pull/123",
  "summary": {
    "frames": 1,
    "npcs_updated": 5,
    "events_generated": 1,
    "actions_queued": 8
  },
  "changes": [
    "RAPP Guide moved to (5, 0, 2)",
    "Card Trader mood: eager -> tired",
    "Generated 'Flash Sale' event in marketplace"
  ]
}
```

### Dry Run Response
```json
{
  "status": "dry-run",
  "would_update": {
    "state/npcs.json": { "modified": true, "changes": 3 },
    "state/actions.json": { "modified": true, "new_actions": 5 },
    "worlds/hub/events.json": { "modified": true, "new_events": 1 }
  },
  "preview": "[JSON diff]"
}
```

## Event Templates

### Common Events
```json
// Weather Change
{
  "id": "event-weather-{uuid}",
  "name": "Weather Shift",
  "type": "weather",
  "data": { "from": "clear", "to": "cloudy" },
  "duration": 900000
}

// NPC Mood Boost
{
  "id": "event-mood-{uuid}",
  "name": "Good Vibes",
  "type": "atmosphere",
  "data": { "mood_modifier": 1.2 },
  "duration": 600000
}
```

### Rare Events
```json
// Flash Sale
{
  "id": "event-sale-{uuid}",
  "name": "Flash Sale",
  "type": "trade",
  "data": { "discount": 0.15, "merchant": "card-trader-001" },
  "duration": 1800000
}

// Battle Challenge
{
  "id": "event-battle-{uuid}",
  "name": "Battle Challenge",
  "type": "battle",
  "world": "arena",
  "data": { "challenger": "battle-master-001", "stakes": 100 },
  "duration": 3600000
}
```

### Epic Events
```json
// Rare Merchant Spawn
{
  "id": "event-spawn-{uuid}",
  "name": "Mysterious Trader Arrives",
  "type": "discovery",
  "data": {
    "npc": {
      "id": "rare-merchant-{uuid}",
      "name": "Mysterious Trader",
      "avatar": "sparkles",
      "inventory": { "holographic": 5, "epic": 20 }
    }
  },
  "duration": 7200000
}

// Economy Boom
{
  "id": "event-boom-{uuid}",
  "name": "Economy Boom",
  "type": "economy",
  "data": {
    "price_multiplier": 0.5,
    "mining_boost": 2.0,
    "announcement": "The market is thriving! Prices halved!"
  },
  "duration": 14400000
}
```

## Scheduling

### Manual Invocation
```bash
/world-tick
```

### Cron Schedule (via GitHub Actions)
```yaml
# .github/workflows/world-tick.yml
name: World Tick
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:
    inputs:
      frames:
        description: 'Number of frames'
        default: '1'
      intensity:
        description: 'Event intensity'
        default: 'normal'

jobs:
  tick:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          skill: world-tick
          args: --frames ${{ inputs.frames || '1' }} --intensity ${{ inputs.intensity || 'normal' }}
```

### Webhook Trigger
```bash
curl -X POST https://api.github.com/repos/kody-w/rappverse-data/dispatches \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"event_type": "world-tick", "client_payload": {"frames": 1}}'
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `MERGE_CONFLICT` | Concurrent ticks | Wait and retry |
| `RATE_LIMITED` | Too many PRs | Increase tick interval |
| `INVALID_STATE` | Corrupted JSON | Skip tick, alert maintainer |
| `AUTH_FAILED` | Bad GitHub token | Refresh credentials |

## Integration

### With RAPPverse Frontend
The frontend polls `state/actions.json` and animates NPCs based on queued actions.

### With Other Skills
```bash
# Generate event then tick
/rappverse generate-event --world arena --type battle
/world-tick --world arena
```

### With RAPP Pipeline
```bash
# After deploying new agent, tick to spawn
/rapp transcript_to_agent --project_id myagent
/world-tick --intensity high  # Increase spawn chance
```

## Best Practices

1. **Run regularly** - 5-minute intervals keep world alive
2. **Use dry-run first** - Preview changes before committing
3. **Monitor PR queue** - Don't let unmerged PRs pile up
4. **Balance intensity** - Too high = chaotic, too low = static
5. **Review epic events** - May need manual approval

## Metrics

Track tick health:
```json
{
  "ticks_today": 288,
  "prs_created": 288,
  "prs_merged": 285,
  "prs_failed": 3,
  "events_generated": 57,
  "actions_queued": 1440
}
```
