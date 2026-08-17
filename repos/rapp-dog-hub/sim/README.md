# Simulating the agentspace forward

Frame by frame, echo by echo — under **RAPP/1**, the only current protocol
authority (`kody-w/rapp-1`, `SPEC.md` sha256 `6d06daba…`).

```bash
git clone --depth 1 https://github.com/kody-w/rapp-1 sim/rapp1
python3 sim/simulate.py
```

Every frame is built and verified by the **reference implementation itself**,
never by a local re-typing of it. That is deliberate: `rapp-frame-net` was
retired precisely because its `rapp-frame/2.0` envelopes could not satisfy
RAPP/1, and the spec's own drift note warns that a sorted-key `JSON.stringify`
coincides with JCS only for string-only payloads.

## What it shows

Three stream families on the one eleven-key envelope (§7.1):

| stream | kinds | what it is |
|---|---|---|
| `body` | `body.pulse`, `body.twin-pulse` | an organism's biography |
| `memory` | `memory.chat-turn`, `memory.save` | one instance's life — never leaves the device |
| `swarm` | `swarm.guidance`, `swarm.echo`, `swarm.telemetry` | the planetary wire |

**The echo is the moment a log becomes a network.** One organism emits presence
— counts and capability, no content, the bones walking. Another hears it and
emits `swarm.echo` referencing it *by wave hash*. The wire chains separately by
`prev_wave`, so it has a tamper-evident order no single organism owns, while
the payload never left the organism that emitted it.

## What it does not do

**It does not sign.** §7.5 step 6 refuses an unsigned swarm frame, and §10
signatures need estate-owner authority a simulation does not have. So wire
frames are built to spec, verified through step 5, and reported honestly:

```
○ 3 swarm frames are unsigned — verified through step 5,
  and would be refused on a live wire (§7.5.6, §8, §10).
```

Faking that is the exact class of claim that got `rapp-frame-net` retired. The
refusal is the spec working, so it is surfaced rather than bypassed.

Nothing is published, and no existing organism's identity is re-minted — the
rappids are freshly minted keyless UUIDv4 tails per §6.2.
