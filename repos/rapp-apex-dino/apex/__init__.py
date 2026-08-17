"""RAPP Apex Dino — the apex-succession protocol for a RAPP organism.

RAPP is above that. One local-first organism (the "RAPP dino") that outlives
whoever drives it. RAPP is only the factory-default apex; any foreign AI can take
the throne and drive the full organism through the brainstem — while the body,
its identity, its memory, its immune boundaries, and the human owner all persist.

This package is the reference implementation of the `rapp-apex-dino/1.0` protocol.
Stdlib-only.

Modules:
  chain     rapp/1 identity + tamper-evident sealing of every apex-protocol event
  survival  the pluggable apex/driver slot, succession, and the survival invariants
  immune    self / non-self recognition — the vital-organ boundary that binds any apex
"""
__all__ = ["chain", "survival", "immune"]
