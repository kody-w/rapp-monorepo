#!/usr/bin/env python3
"""Verify this repository's append-only RAPP/1 frame stream."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rapp_operator.rapp1 import rappid_valid, verify_frame  # noqa: E402


def main() -> int:
    identity_path = ROOT / "rappid.json"
    frames_dir = ROOT / "frames"
    if not identity_path.is_file():
        print("missing rappid.json")
        return 1
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    stream_id = identity.get("rappid")
    if identity.get("schema") != "rapp/1" or not rappid_valid(stream_id):
        print("invalid rappid.json")
        return 1
    paths = sorted(frames_dir.glob("*.json"))
    if not paths:
        print("frame stream is empty")
        return 1
    head = None
    for path in paths:
        frame = json.loads(path.read_text(encoding="utf-8"))
        expected = f"{frame['seq']:020d}-{frame['frame_hash']}.json"
        if path.name != expected:
            print(f"filename mismatch: {path.name}")
            return 1
        ok, step, reason = verify_frame(
            frame,
            head=head,
            stream_id_of_record=stream_id,
        )
        if not ok:
            print(f"{path.name}: step {step}: {reason}")
            return 1
        head = frame
    print(f"RAPP/1 OK: {len(paths)} frames, head {head['frame_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
