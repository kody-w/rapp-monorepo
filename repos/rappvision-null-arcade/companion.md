# WHAT IT IS

A paired RAPP Vision pilot for fictional speedrunner/game designer Jax Byte:
a 22-second portrait film and a deterministic live integrity speedrun.

# WHY IT MATTERS

The pair makes score trust observable. A valid route records `03.580`; a cheat
is rejected and cannot replace it. The viewer learns the proof in the film,
then reproduces both outcomes in the replay.

# LOCATION

- Guided film: `media/null-arcade-integrity-run.mp4` or `.webm`
- Live replay: `live/index.html`
- Thumbnail: `thumbs/null-arcade-integrity-run.svg`

# EVIDENCE

`evidence.json` binds both encoded files by SHA-256, records codec, dimensions,
duration, and audio presence, and records the deterministic live contract test.

# BOUNDARIES

Jax Byte, Null Arcade, the course, scores, visuals, and audio are fictional or
synthetic. No copyrighted arcade assets, real people, private data, or external
gameplay were used.

# KNOWN COMPROMISES

The replay uses fixed route timestamps rather than wall-clock timing so scripted
and manual runs remain deterministic. Reset preserves the verified record by
design; reloading the page starts a fresh session.

# NEXT DECISION

Decide whether a future episode should add a second valid route with a different
verified score while keeping the same integrity rules.
