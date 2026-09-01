# WHAT IT IS

`Push, Friction, Motion` is a paired 24-second instructional film and live
simulator from Theo & Nia, an explicitly fictional synthetic educator duo.

# WHY IT MATTERS

It gives a newcomer one auditable physical relationship: applied force must be
considered together with kinetic friction and mass before acceleration is known.

# LOCATION

- Encoded film: `media/push-friction-motion.mp4` and `.webm`
- Live replay: `live/index.html`
- Channel manifest: `channel.json`

# EVIDENCE

The baseline independently evaluates to friction 4.90 N, net force 5.10 N, and
acceleration 2.55 m/s². `evidence.json` binds both encodes by SHA-256 and records
codec, dimension, browser, reset, rejection, math, and privacy checks.

# BOUNDARIES

This is a synthetic educational model for a block already sliding right on a
flat horizontal surface, with constant applied force, kinetic friction, and
g = 9.8 m/s². It omits static friction, air drag, rotation, surface deformation,
and any change in the coefficient during a run.

# KNOWN COMPROMISES

The film has no narration and relies on large, persistent on-screen instruction;
its quiet tonal bed and paper-like taps are deterministic and original. Block
travel is illustrative; the numeric claim is acceleration, not a scale-accurate
distance animation.

# NEXT DECISION

Decide whether a future episode should add a timed sliding-distance extension
or keep the channel focused on one equation per replay.
