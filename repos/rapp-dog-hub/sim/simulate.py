#!/usr/bin/env python3
"""
Simulate the agentspace forward, frame by frame and echo by echo.

Every frame here is built and verified by the RAPP/1 reference implementation
(`kody-w/rapp-1`, SPEC.md sha256 6d06daba…), not by a local re-typing of it.
That matters: the retired `rapp-frame-net` was retired precisely because its
`rapp-frame/2.0` envelopes could not satisfy RAPP/1, and the Lexicon's drift
note warns that a sorted-key JSON.stringify only coincides with JCS for
string-only payloads.

What is simulated
-----------------
Three streams, each on the one eleven-key envelope (§7.1):

  body:   an organism's biography           body.pulse / body.twin-pulse
  memory: one organism instance's life      memory.chat-turn / memory.save
  swarm:  the planetary wire                swarm.guidance / swarm.echo

An **echo** is what makes it a network rather than a log: an organism observes
something on the wire and emits `swarm.echo` referencing what it heard. Wire
frames additionally chain by wave (`prev_wave`), so the wire has its own
tamper-evident order independent of any single organism's worldline (§7.4).

What is NOT simulated
---------------------
Signing. §7.5 step 6 refuses an unsigned swarm frame, and §10 signatures
require estate-owner authority this simulation does not have and must not
fake — that is the exact class of claim that got rapp-frame-net retired. So
swarm frames are built to spec, verified through step 5, and reported honestly
as `unsigned: would be refused on a live wire`.

Nothing here is published, and no identity is minted for an existing organism:
the rappids below are freshly minted keyless UUIDv4 tails per §6.2.

    python3 simulate.py            # narrate
    python3 simulate.py --json     # machine-readable
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import uuid
from pathlib import Path

# Clone the authority next to this file:
#   git clone --depth 1 https://github.com/kody-w/rapp-1 sim/rapp1
REF = Path(__file__).resolve().parent / "rapp1"
sys.path.insert(0, str(REF))

try:
    import rapp  # the reference implementation of record
except ImportError:  # pragma: no cover
    sys.exit(f"reference implementation not found at {REF} — clone kody-w/rapp-1 there")


DIM, BOLD, GRN, CYN, YEL, RED, NC = "\033[2m", "\033[1m", "\033[32m", "\033[36m", "\033[33m", "\033[31m", "\033[0m"


def utc(offset_seconds: int, *, base: _dt.datetime | None = None) -> str:
    """§7.4's exact 24-byte form: YYYY-MM-DDTHH:MM:SS.mmmZ."""
    start = base or _dt.datetime(2026, 8, 1, 20, 0, 0, tzinfo=_dt.timezone.utc)
    moment = start + _dt.timedelta(seconds=offset_seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


class Stream:
    """One verified chain. Refuses anything the reference implementation refuses."""

    def __init__(self, stream_id: str, label: str):
        self.stream_id = stream_id
        self.label = label
        self.frames: list[dict] = []
        self.refusals: list[tuple[str, int | None, str]] = []

    @property
    def head(self) -> dict | None:
        return self.frames[-1] if self.frames else None

    @property
    def is_swarm(self) -> bool:
        return self.stream_id.startswith("net:")

    def emit(self, kind: str, payload: dict, when: str, *, prev_wave: str | None = None) -> dict:
        head = self.head
        seq = 0 if head is None else head["seq"] + 1
        prev = None if head is None else head["payload_hash"]

        # §7.4: prev_wave is non-null iff swarm-stream AND seq > 0.
        wave = prev_wave if (self.is_swarm and seq > 0) else None

        frame = rapp.build_frame(
            kind=kind,
            stream_id=self.stream_id,
            seq=seq,
            utc=when,
            payload=payload,
            prev=prev,
            prev_wave=wave,
            sig=None,
        )

        ok, step, reason = rapp.verify_frame(frame, head=head, stream_id_of_record=self.stream_id)

        # Step 6 refuses an unsigned swarm frame. That refusal is CORRECT — it
        # is the spec working — so it is recorded and reported, never bypassed.
        # Match on the reason as well as the step, so a different step-6 failure
        # (an actually-invalid signature) is still a hard refusal.
        unsigned_wire = self.is_swarm and str(step) == "6" and "signed" in (reason or "")

        if not ok and not unsigned_wire:
            self.refusals.append((kind, step, reason))
            raise SystemExit(f"{RED}refused{NC} {kind} at step {step}: {reason}")

        frame["_verified_through"] = 5 if unsigned_wire else 6
        frame["_refusal_reason"] = reason if unsigned_wire else None
        frame["_unsigned_wire"] = unsigned_wire
        self.frames.append(frame)
        return frame


def simulate() -> dict:
    # §6.2 keyless mint: tail = Hb("rapp/1:rappid", uuid4_octets). Fresh
    # identities — never a re-mint of an organism that already exists.
    alpha = rapp.mint_rappid("alpha", "organism", uuid.uuid4().bytes)
    beta = rapp.mint_rappid("beta", "organism", uuid.uuid4().bytes)

    streams = {
        "alpha_body": Stream(alpha, "alpha · biography"),
        "alpha_memory": Stream(f"{alpha}:laptop", "alpha · memory"),
        "beta_body": Stream(beta, "beta · biography"),
        "wire": Stream("net:agentspace", "the planetary wire"),
    }

    story: list[dict] = []

    def step(narration: str, stream_key: str, kind: str, payload: dict, at: int, **kw) -> dict:
        frame = streams[stream_key].emit(kind, payload, utc(at), **kw)
        story.append({"narration": narration, "stream": stream_key, "frame": frame})
        return frame

    # ── T+0 · two organisms are planted ──────────────────────────────────
    step(
        "alpha is planted. Its biography opens with a genesis pulse.",
        "alpha_body", "body.pulse",
        {"event": "planted", "membrane": {"bones": "public", "vault": "local-only"}, "article": "LVI"},
        0,
    )
    step(
        "Its operator plants a twin — the vault half, never on the wire.",
        "alpha_body", "body.twin-pulse",
        {"event": "twin-planted", "fingerprint": "c5e3dd557675b19b", "vault": "off-chain"},
        30,
    )
    step(
        "beta is planted a minute later, independently.",
        "beta_body", "body.pulse",
        {"event": "planted", "membrane": {"bones": "public", "vault": "local-only"}, "article": "LVI"},
        60,
    )

    # ── T+2m · alpha lives. Memory stays on its own worldline ────────────
    step(
        "alpha's operator asks it something. That is memory, not wire — it "
        "never leaves the device.",
        "alpha_memory", "memory.chat-turn",
        {"role": "owner", "turns": 1, "content_hash": "off-chain"},
        120,
    )
    step(
        "alpha stores a durable fact. Still memory. Still local.",
        "alpha_memory", "memory.save",
        {"kind": "preference", "count": 1},
        150,
    )

    # ── T+5m · the wire opens; alpha emits exhaust ───────────────────────
    genesis_wire = step(
        "The wire opens. alpha emits presence — the bones walking. Counts and "
        "capability, no content: this is DOG.",
        "wire", "swarm.guidance",
        {
            "emitter": alpha[-16:],
            "shape": {"roles": 1, "projects": 3, "facts": 7, "accounts": 1},
            "capabilities": ["phone", "second-brain", "twin"],
        },
        300,
    )

    # ── T+6m · THE ECHO ──────────────────────────────────────────────────
    echo = step(
        "beta hears alpha and echoes it. This is the moment a log becomes a "
        "network: beta references what it heard by wave hash, and the wire "
        "chains by prev_wave — an order no single organism owns.",
        "wire", "swarm.echo",
        {
            "emitter": beta[-16:],
            "heard": genesis_wire["frame_hash"],
            "observation": "presence",
            "note": "referenced by wave hash; alpha's payload never left alpha",
        },
        360,
        prev_wave=genesis_wire["frame_hash"],
    )

    # ── T+8m · the echo comes home ───────────────────────────────────────
    step(
        "alpha records that it was heard. The encounter is now in alpha's own "
        "biography, on alpha's own worldline.",
        "alpha_body", "body.pulse",
        {"event": "echoed-by-peer", "peer": beta[-16:], "wave": echo["frame_hash"]},
        480,
    )
    step(
        "beta answers on the wire, chaining to the echo.",
        "wire", "swarm.telemetry",
        {"emitter": beta[-16:], "peers_seen": 1, "frames_verified": 2},
        540,
        prev_wave=echo["frame_hash"],
    )

    # ── T+15m · a year of this, compressed ───────────────────────────────
    for index, (offset, note) in enumerate(
        [(900, "alpha ships something and says so"), (1800, "beta ships something and says so")], start=1
    ):
        which = "alpha" if index == 1 else "beta"
        step(
            note,
            f"{which}_body", "body.pulse",
            {"event": "artifact-published", "kind": "repository"},
            offset,
        )

    return {"alpha": alpha, "beta": beta, "streams": streams, "story": story}


def report(result: dict, as_json: bool) -> int:
    streams: dict[str, Stream] = result["streams"]

    if as_json:
        print(
            json.dumps(
                {
                    "spec": "rapp/1",
                    "reference": "kody-w/rapp-1",
                    "streams": {
                        key: {
                            "stream_id": s.stream_id,
                            "frames": [{k: v for k, v in f.items() if not k.startswith("_")} for f in s.frames],
                        }
                        for key, s in streams.items()
                    },
                },
                indent=2,
            )
        )
        return 0

    print(f"\n{BOLD}  The agentspace, simulated forward{NC}")
    print(f"{DIM}  every frame built and verified by kody-w/rapp-1{NC}\n")

    for entry in result["story"]:
        frame = entry["frame"]
        stream = streams[entry["stream"]]
        mark = f"{YEL}○{NC}" if frame["_unsigned_wire"] else f"{GRN}●{NC}"

        print(f"  {mark} {DIM}{frame['utc']}{NC}  {CYN}{frame['kind']:<18}{NC}{DIM}seq {frame['seq']}  {stream.label}{NC}")
        for line in entry["narration"].split(". "):
            if line.strip():
                print(f"      {line.strip().rstrip('.')}.")
        print(f"      {DIM}particle {frame['payload_hash'][:16]}…  wave {frame['frame_hash'][:16]}…{NC}")
        if frame["prev_wave"]:
            print(f"      {DIM}↳ chains to wave {frame['prev_wave'][:16]}…{NC}")
        print()

    total = sum(len(s.frames) for s in streams.values())
    unsigned = sum(1 for s in streams.values() for f in s.frames if f["_unsigned_wire"])

    print(f"{BOLD}  {total} frames across {len(streams)} streams{NC}\n")
    for s in streams.values():
        kinds = ", ".join(sorted({f["kind"] for f in s.frames}))
        print(f"    {s.label:<22} {len(s.frames)} frames  {DIM}{kinds}{NC}")

    print(f"\n{BOLD}  Conformance{NC}\n")
    print(f"    {GRN}✓{NC} exactly eleven keys, every frame (§7.1)")
    print(f"    {GRN}✓{NC} particle + wave, domain-separated (§5, §7.3)")
    print(f"    {GRN}✓{NC} contiguous seq, prev = predecessor's payload_hash (§7.4)")
    print(f"    {GRN}✓{NC} prev_wave non-null iff swarm-stream and seq > 0 (§7.4)")
    print(f"    {GRN}✓{NC} stream binding, calendar-valid utc (§7.5.1, §7.5.1a)")
    print(f"    {GRN}✓{NC} rappids minted keyless from UUIDv4 octets (§6.2)")

    if unsigned:
        print(f"\n    {YEL}○{NC} {unsigned} swarm frames are {BOLD}unsigned{NC} — verified through step 5,")
        print(f"      and {BOLD}would be refused on a live wire{NC} (§7.5.6, §8, §10).")
        print(f"      {DIM}Signing needs estate-owner authority this simulation does not have.{NC}")
        print(f"      {DIM}Claiming it is the exact defect that retired rapp-frame-net.{NC}")

    print()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate the agentspace forward under RAPP/1.")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    sys.exit(report(simulate(), args.json))
