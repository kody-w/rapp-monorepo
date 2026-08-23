"""Trust-first command line for the organism inventory and RAPP/1 wire."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any

from .alignment import inspect_alignment
from .authority import inspect_authority
from .errors import RappRefusal, RappSDKError
from .inventory import Organism, SafeSpecimen
from .wire import ChatClient, ChatRequest

TRUST_LINE = "NOT FULLY RAPP/1 CONFORMANT — authenticated section-13 registry absent"


def _emit_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _lead() -> None:
    print(TRUST_LINE)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rapp-sdk")
    parser.add_argument(
        "--root",
        help="explicit snapshot/SDK root (required except for chat)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="snapshot and conformance status")
    commands.add_parser("systems", help="list architecture systems")
    commands.add_parser("organs", help="list captured repositories")
    organ = commands.add_parser("organ", help="show one captured repository")
    organ.add_argument("name")
    commands.add_parser("authority", help="inspect structural authority and blockers")
    alignment = commands.add_parser("alignment", help="report Map/Spine projection drift")
    alignment.add_argument("--stale-after-days", type=int, default=7)
    read = commands.add_parser("read", help="safely read a specimen file")
    read.add_argument("organ")
    read.add_argument("path")
    read.add_argument("--max-bytes", type=int, default=1024 * 1024)
    chat = commands.add_parser("chat", help="call an explicit exact RAPP/1 /chat endpoint")
    chat.add_argument("--endpoint", required=True)
    chat.add_argument("--timeout", type=float, default=30.0)
    chat.add_argument("--session-id")
    chat.add_argument("--idempotency-key")
    chat.add_argument("text")
    return parser


def _status(root: str) -> dict[str, Any]:
    organism = Organism(root, allow_drift=True)
    try:
        authority_report = inspect_authority(root).as_dict()
    except RappSDKError as exc:
        authority_report = {
            "state": "unavailable-safe-access-refused",
            "reason": str(exc),
            "authenticated_registry": "unavailable",
            "full_conformance": False,
        }
    return {
        "trust": {
            "state": "not-fully-rapp-1-conformant",
            "authenticated_registry": "absent",
            "full_conformance": False,
        },
        "organism": organism.summary(),
        "authority_report": authority_report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command != "chat" and args.root is None:
        parser.error("--root is required for snapshot and architecture commands")
    root = str(Path(args.root).absolute()) if args.root is not None else None
    try:
        if args.command == "status":
            assert root is not None
            value = _status(root)
            if args.json:
                _emit_json(value)
            else:
                _lead()
                snapshot = value["organism"]["snapshot"]
                print(
                    f"{snapshot['repositories']} organs, {snapshot['files']} files, "
                    f"{snapshot['bytes']} captured bytes"
                )
                report = value["authority_report"]
                if report.get("state") == "unavailable-safe-access-refused":
                    print(f"authority inspection unavailable: {report['reason']}")
                    print(f"architecture drift: {value['organism']['architecture_drift']}")
                else:
                    current = report["normative_source_current"]
                    target = report["target_structural_pin"]
                    print(
                        f"normative SPEC: {current['byte_length']} bytes at "
                        f"{current['snapshot_commit'][:12]}; target pin: {target['state']}; "
                        f"architecture drift: "
                        f"{value['organism']['architecture_drift']}"
                    )
            return 0
        if args.command == "chat":
            result = ChatClient(args.endpoint, timeout=args.timeout).chat(
                ChatRequest(args.text, args.session_id, args.idempotency_key)
            )
            if args.json:
                _emit_json(result.as_dict())
            else:
                _lead()
                print(result.response)
                print(f"session_id: {result.session_id}")
                if result.agent_logs:
                    print("agent_logs:")
                    for log in result.agent_logs:
                        print(f"- {log}")
            return 0
        if args.command == "alignment":
            assert root is not None
            value = inspect_alignment(
                root, stale_after_days=args.stale_after_days
            ).as_dict()
            if args.json:
                _emit_json(value)
            else:
                _lead()
                print(
                    "alignment evidence: declared live state is not dynamically fetched; "
                    "authenticated acceptance: false"
                )
                for projection in value["projections"]:
                    print(
                        f"{projection['id']}: coverage "
                        f"{projection['coverage_relationship']['against_current_snapshot']}; "
                        f"freshness={projection['freshness']['state']}; "
                        f"captured_commit_matches_manifest="
                        f"{projection['daily_checks']['captured_commit_matches_manifest']}"
                    )
                for conflict in value["conflicts"]:
                    print(
                        f"CONFLICT {conflict['type']}: {conflict['id']} "
                        f"({conflict['evidence_mode']})"
                    )
            return 0
        assert root is not None
        organism = Organism(root)
        if args.command == "systems":
            value = organism.systems()
            if args.json:
                _emit_json({"trust_state": "not-fully-rapp-1-conformant", "systems": value})
            else:
                _lead()
                for system in value:
                    print(
                        f"{system['id']}: {system['name']} "
                        f"({len(system['organs'])} organs; {system['lifecycle']})"
                    )
            return 0
        if args.command == "organs":
            value = organism.organs()
            if args.json:
                _emit_json({"trust_state": "not-fully-rapp-1-conformant", "organs": value})
            else:
                _lead()
                for organ in value:
                    print(f"{organ['repo']} {organ['commit']} [{organ['system']}]")
            return 0
        if args.command == "organ":
            value = organism.organ(args.name)
            if args.json:
                _emit_json({"trust_state": "not-fully-rapp-1-conformant", "organ": value})
            else:
                _lead()
                print(f"{value['repo']} @ {value['commit']}")
                print(
                    f"system={value['system']} files={value['files']} bytes={value['bytes']} "
                    f"skipped={len(value.get('skipped_large', []))} "
                    f"withheld={len(value.get('withheld', []))}"
                )
            return 0
        if args.command == "authority":
            value = inspect_authority(root).as_dict()
            if args.json:
                _emit_json(value)
            else:
                _lead()
                source = value["normative_source_current"]
                print(f"normative protocol authority: {source['repository']} ({source['url']})")
                print(
                    f"current normative SPEC: {source['byte_length']} bytes; "
                    f"sha256 {source['sha256']}"
                )
                target = value["target_structural_pin"]
                print(
                    f"RAPP target pin: {target['state']} "
                    f"({target['byte_length']} bytes at {target['commit']})"
                )
                map_pin = value["map_structural_pin"]
                print(
                    f"rapp-map pin matches current bytes: "
                    f"{map_pin['matches_normative_source_current_bytes']}"
                )
                print(
                    f"rapp-spine old pin equals Map current pin: "
                    f"{value['spine_pin_claim']['commits_equal']}"
                )
                print(f"authenticated registry: {value['authenticated_registry']}")
                for blocker in value["owner_action_blockers"]:
                    print(f"BLOCKED: {blocker}")
            return 0
        if args.command == "read":
            octets = SafeSpecimen(organism).read_bytes(
                args.organ, args.path, max_bytes=args.max_bytes
            )
            if args.json:
                _emit_json(
                    {
                        "trust_state": "not-fully-rapp-1-conformant",
                        "organ": args.organ,
                        "path": args.path,
                        "encoding": "base64",
                        "bytes": len(octets),
                        "content": base64.b64encode(octets).decode("ascii"),
                    }
                )
            else:
                _lead()
                print(f"SPECIMEN ONLY — no import or execution: {args.organ}/{args.path}")
                sys.stdout.flush()
                sys.stdout.buffer.write(octets)
                if not octets.endswith(b"\n"):
                    sys.stdout.buffer.write(b"\n")
            return 0
    except RappRefusal as exc:
        if args.json:
            _emit_json({"error": {"code": exc.code, "step": exc.step}})
        else:
            _lead()
            print(str(exc), file=sys.stderr)
        return 2
    except (RappSDKError, OSError, ValueError) as exc:
        if args.json:
            _emit_json({"sdk_error": type(exc).__name__, "message": str(exc)})
        else:
            print(f"rapp-sdk: {exc}", file=sys.stderr)
        return 2
    return 2
