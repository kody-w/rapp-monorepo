#!/usr/bin/env python3
"""Append one canonical RAPP/1 body.pulse to this repository."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rapp_operator.rapp1 import (  # noqa: E402
    build_frame,
    canonical_bytes,
    mint_rappid,
    verify_frame,
)


def fixed_utc() -> str:
    value = datetime.now(timezone.utc)
    return (
        value.strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{value.microsecond // 1000:03d}Z"
    )


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def load_frames(stream_id: str) -> list[dict]:
    frames = []
    head = None
    for path in sorted((ROOT / "frames").glob("*.json")):
        frame = json.loads(path.read_text(encoding="utf-8"))
        ok, step, reason = verify_frame(
            frame,
            head=head,
            stream_id_of_record=stream_id,
        )
        if not ok:
            raise SystemExit(f"chain failed at step {step}: {reason}")
        frames.append(frame)
        head = frame
    return frames


def ensure_identity() -> dict:
    path = ROOT / "rappid.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    rappid, anchor = mint_rappid(
        "kody-w",
        "rapp-brainstem",
        uuid_anchor=uuid.uuid4(),
    )
    identity = {
        "schema": "rapp/1",
        "rappid": rappid,
        "kind": "project",
        "name": "AI-operated setup and lifecycle for RAPP Brainstem",
        "uuid_anchor": str(anchor),
        "frames": "frames/",
    }
    atomic_write(
        path,
        (json.dumps(identity, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return identity


def append(stream_id: str, frames: list[dict], payload: dict) -> dict:
    head = frames[-1] if frames else None
    utc = fixed_utc()
    if head is not None and utc < head["utc"]:
        utc = head["utc"]
    frame = build_frame(
        "body.pulse",
        stream_id,
        0 if head is None else head["seq"] + 1,
        utc,
        payload,
        None if head is None else head["payload_hash"],
    )
    ok, step, reason = verify_frame(
        frame,
        head=head,
        stream_id_of_record=stream_id,
    )
    if not ok:
        raise SystemExit(f"refusing invalid frame at step {step}: {reason}")
    target = ROOT / "frames" / (
        f"{frame['seq']:020d}-{frame['frame_hash']}.json"
    )
    atomic_write(target, canonical_bytes(frame))
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--detail", default="")
    args = parser.parse_args()

    identity = ensure_identity()
    frames = load_frames(identity["rappid"])
    if not frames:
        frames.append(append(
            identity["rappid"],
            [],
            {
                "event": "project.created",
                "actor": {"id": args.actor},
                "project": "rapp-brainstem",
                "boundary": "wrap Grail; never fork it",
            },
        ))
    frame = append(
        identity["rappid"],
        frames,
        {
            "event": args.event,
            "actor": {"id": args.actor},
            "detail": args.detail,
        },
    )
    print(frame["frame_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
