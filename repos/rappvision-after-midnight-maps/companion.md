# WHAT IT IS

**After Midnight Maps** is a paired 26-second ambient film and deterministic live map replay by Sol Navarro, an explicitly fictional synthetic cartographer.

# WHY IT MATTERS

It makes a bounded computational claim visible: moving one waypoint changes only the adjacent route legs and total distance. The fixed endpoints, Haversine rule, and preserved original route do not change.

# LOCATION

- Film: `media/after-midnight-maps.mp4` or `media/after-midnight-maps.webm`
- Live replay: `live/index.html`
- Thumbnail: `thumbs/after-midnight-maps.svg`

# EVIDENCE

`evidence.json` binds both encodes by SHA-256, records codec probes, independent route calculations, interaction assertions, reset state, and privacy checks.

# BOUNDARIES

All creator identity, place names, coordinates, and route conditions are synthetic. Great-circle distance is not a street route, accessibility assessment, forecast, safety check, or travel recommendation.

# KNOWN COMPROMISES

The film uses a deterministic generated paper-map abstraction rather than geographic tiles. The live drag is bounded to the chart and intentionally rejects coordinates outside its fictional survey extent.

# NEXT DECISION

Try the live replay: move Lumen Bend, compare both routes, attempt the invalid move, then reset to the canonical baseline.
