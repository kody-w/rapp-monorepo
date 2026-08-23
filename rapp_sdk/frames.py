"""RAPP/1 frames and a monotonic stateful consumer."""

from __future__ import annotations

import json
import re
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol

from .errors import FrameStateError, FrameValidationError, TrustError, ValidationError
from .identity import classify_stream_id, validate_kind
from .json_profile import H, canonical_bytes
from .trust import SignatureTrust, VerifiedRegistry, parse_detached_jws, verify_detached_jws

FRAME_KEYS = frozenset(
    {
        "spec",
        "kind",
        "stream_id",
        "seq",
        "utc",
        "payload",
        "payload_hash",
        "frame_hash",
        "prev",
        "prev_wave",
        "sig",
    }
)
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
UINT53_MAX = (1 << 53) - 1


def _valid_utc(value: Any) -> bool:
    if not isinstance(value, str) or not _UTC_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return value[17:19] != "60"


def _now_utc() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _uint53(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= UINT53_MAX


def _wave_preimage(frame: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in frame.items() if key not in {"frame_hash", "sig"}}


def _signature_payload(frame: Mapping[str, Any]) -> bytes:
    return canonical_bytes({key: value for key, value in frame.items() if key != "sig"})


def inspect_frame(frame: Mapping[str, Any]) -> dict[str, Any]:
    """Hash/shape inspection only; no trust or chain acceptance is claimed."""

    shape = isinstance(frame, Mapping) and set(frame) == FRAME_KEYS
    try:
        payload_match = (
            shape
            and isinstance(frame.get("payload"), dict)
            and frame.get("payload_hash") == H("rapp/1:particle", frame["payload"])
        )
        wave_match = (
            shape
            and frame.get("frame_hash") == H("rapp/1:wave", _wave_preimage(frame))
        )
    except ValidationError:
        payload_match = wave_match = False
    return {
        "semantics": "structural-inspection",
        "authenticated_acceptance": False,
        "exact_shape": bool(shape),
        "payload_hash_matches": bool(payload_match),
        "frame_hash_matches": bool(wave_match),
    }


@dataclass(frozen=True)
class StreamHead:
    stream_id: str
    seq: int
    frame_hash: str
    payload_hash: str
    utc: str
    genesis_hash: str
    registry_anchor: str
    registry_seq: int
    prev: str | None
    prev_wave: str | None
    parent_utc: str | None
    lineage: tuple[str, ...]
    forked: bool = False


class HeadStore(Protocol):
    def get(self, stream_id: str) -> StreamHead | None: ...

    def commit(self, expected_hash: str | None, head: StreamHead) -> None: ...

    def mark_fork(self, stream_id: str, expected_hash: str) -> None: ...


class MemoryHeadStore:
    def __init__(self) -> None:
        self._heads: dict[str, StreamHead] = {}
        self._lock = threading.Lock()

    def get(self, stream_id: str) -> StreamHead | None:
        with self._lock:
            return self._heads.get(stream_id)

    def commit(self, expected_hash: str | None, head: StreamHead) -> None:
        with self._lock:
            current = self._heads.get(head.stream_id)
            current_hash = current.frame_hash if current else None
            if current_hash != expected_hash:
                raise FrameStateError("4", "head changed concurrently")
            self._heads[head.stream_id] = head

    def mark_fork(self, stream_id: str, expected_hash: str) -> None:
        with self._lock:
            current = self._heads.get(stream_id)
            if current is None or current.frame_hash != expected_hash:
                raise FrameStateError("4", "head changed while recording fork")
            self._heads[stream_id] = StreamHead(**{**current.__dict__, "forked": True})


class SQLiteHeadStore:
    """Cross-process persistent head state with compare-and-swap transitions."""

    _COLUMNS = (
        "stream_id,seq,frame_hash,payload_hash,utc,genesis_hash,registry_seq,"
        "registry_anchor,prev,prev_wave,parent_utc,lineage_json,forked"
    )

    def __init__(self, path: str | Path) -> None:
        self.path = str(Path(path).absolute())
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS stream_heads ("
                "stream_id TEXT PRIMARY KEY, seq INTEGER NOT NULL, frame_hash TEXT NOT NULL,"
                "payload_hash TEXT NOT NULL, utc TEXT NOT NULL, genesis_hash TEXT NOT NULL,"
                "registry_seq INTEGER NOT NULL, registry_anchor TEXT NOT NULL,"
                "prev TEXT, prev_wave TEXT, parent_utc TEXT,"
                "lineage_json TEXT NOT NULL, forked INTEGER NOT NULL)"
            )

    @staticmethod
    def _head(row: tuple[Any, ...] | None) -> StreamHead | None:
        if row is None:
            return None
        return StreamHead(
            stream_id=row[0],
            seq=row[1],
            frame_hash=row[2],
            payload_hash=row[3],
            utc=row[4],
            genesis_hash=row[5],
            registry_seq=row[6],
            registry_anchor=row[7],
            prev=row[8],
            prev_wave=row[9],
            parent_utc=row[10],
            lineage=tuple(json.loads(row[11])),
            forked=bool(row[12]),
        )

    def get(self, stream_id: str) -> StreamHead | None:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                f"SELECT {self._COLUMNS} FROM stream_heads WHERE stream_id=?",
                (stream_id,),
            ).fetchone()
        return self._head(row)

    def commit(self, expected_hash: str | None, head: StreamHead) -> None:
        with sqlite3.connect(self.path, isolation_level=None) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT frame_hash FROM stream_heads WHERE stream_id=?", (head.stream_id,)
            ).fetchone()
            current_hash = row[0] if row else None
            if current_hash != expected_hash:
                connection.execute("ROLLBACK")
                raise FrameStateError("4", "head changed concurrently")
            connection.execute(
                "INSERT INTO stream_heads VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(stream_id) DO UPDATE SET seq=excluded.seq,"
                "frame_hash=excluded.frame_hash,payload_hash=excluded.payload_hash,"
                "utc=excluded.utc,genesis_hash=excluded.genesis_hash,"
                "registry_seq=excluded.registry_seq,"
                "registry_anchor=excluded.registry_anchor,prev=excluded.prev,"
                "prev_wave=excluded.prev_wave,parent_utc=excluded.parent_utc,"
                "lineage_json=excluded.lineage_json,"
                "forked=excluded.forked",
                (
                    head.stream_id,
                    head.seq,
                    head.frame_hash,
                    head.payload_hash,
                    head.utc,
                    head.genesis_hash,
                    head.registry_seq,
                    head.registry_anchor,
                    head.prev,
                    head.prev_wave,
                    head.parent_utc,
                    json.dumps(head.lineage, separators=(",", ":")),
                    int(head.forked),
                ),
            )
            connection.execute("COMMIT")

    def mark_fork(self, stream_id: str, expected_hash: str) -> None:
        with sqlite3.connect(self.path, isolation_level=None) as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE stream_heads SET forked=1 WHERE stream_id=? AND frame_hash=?",
                (stream_id, expected_hash),
            )
            if cursor.rowcount != 1:
                connection.execute("ROLLBACK")
                raise FrameStateError("4", "head changed while recording fork")
            connection.execute("COMMIT")


@dataclass(frozen=True)
class AcceptedFrame:
    frame: Mapping[str, Any]
    family: str
    signature_trust: SignatureTrust | None
    registry_seq: int
    head: StreamHead
    re_genesis_reset: bool = False


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _validate_steps_1_to_3(
    frame: Mapping[str, Any],
    *,
    expected_stream_id: str,
    registry: VerifiedRegistry,
) -> str:
    if not isinstance(registry, VerifiedRegistry):
        raise FrameValidationError("1", "a VerifiedRegistry proof is required")
    try:
        if not isinstance(frame, Mapping) or set(frame) != FRAME_KEYS:
            raise ValidationError("frame must have exactly the eleven members")
        if frame["spec"] != "rapp/1":
            raise ValidationError("spec must be exactly rapp/1")
        validate_kind(frame["kind"])
        family = registry.kind_family(frame["kind"])
        stream_family = classify_stream_id(frame["stream_id"])
        if family != stream_family:
            raise ValidationError("registered kind family is incompatible with stream_id")
        if not _uint53(frame["seq"]):
            raise ValidationError("seq must be a uint53 integer")
        if not _valid_utc(frame["utc"]):
            raise ValidationError("utc must be calendar-valid fixed millisecond UTC")
        if not isinstance(frame["payload"], dict):
            raise ValidationError("payload must be an object")
        for key in ("payload_hash", "frame_hash"):
            if not isinstance(frame[key], str) or not _HEX_RE.fullmatch(frame[key]):
                raise ValidationError(f"{key} must be 64 lowercase hex")
        for key in ("prev", "prev_wave"):
            if frame[key] is not None and (
                not isinstance(frame[key], str) or not _HEX_RE.fullmatch(frame[key])
            ):
                raise ValidationError(f"{key} must be null or 64 lowercase hex")
        if frame["sig"] is not None:
            parse_detached_jws(frame["sig"])
        re_genesis = frame["kind"] == f"{family}.re-genesis"
        if frame["kind"].endswith(".re-genesis") and not re_genesis:
            raise ValidationError("re-genesis kind is not bound to its stream family")
        if re_genesis:
            migrated = frame["payload"].get("migrated_from")
            if (
                set(frame["payload"]) != {"migrated_from"}
                or not isinstance(migrated, dict)
                or set(migrated) != {"stream_id", "terminal_seal", "terminal_seq"}
                or not isinstance(migrated["terminal_seal"], str)
                or not _HEX_RE.fullmatch(migrated["terminal_seal"])
                or not _uint53(migrated["terminal_seq"])
            ):
                raise ValidationError("re-genesis payload has the wrong exact shape")
            classify_stream_id(migrated["stream_id"])
        canonical_bytes(dict(frame))
    except (ValidationError, TrustError) as exc:
        raise FrameValidationError("1", str(exc)) from exc
    if frame["stream_id"] != expected_stream_id:
        raise FrameValidationError("1a", "stream_id does not bind to the declared stream")
    if frame["payload_hash"] != H("rapp/1:particle", frame["payload"]):
        raise FrameValidationError("2", "payload_hash mismatch")
    if frame["frame_hash"] != H("rapp/1:wave", _wave_preimage(frame)):
        raise FrameValidationError("3", "frame_hash mismatch")
    return family


def _validate_frame(
    frame: Mapping[str, Any],
    *,
    expected_stream_id: str,
    registry: VerifiedRegistry,
    head: StreamHead | None,
) -> tuple[str, SignatureTrust | None]:
    family = _validate_steps_1_to_3(
        frame, expected_stream_id=expected_stream_id, registry=registry
    )
    if head is None:
        if frame["seq"] != 0 or frame["prev"] is not None:
            raise FrameValidationError("4", "genesis requires seq=0 and prev=null")
    else:
        if (
            frame["seq"] != head.seq + 1
            or frame["prev"] != head.payload_hash
            or frame["utc"] < head.utc
        ):
            raise FrameValidationError("4", "particle chain, sequence, or utc check failed")
    if family == "swarm" and frame["seq"] > 0:
        if head is None or frame["prev_wave"] != head.frame_hash:
            raise FrameValidationError("5", "swarm prev_wave mismatch")
    elif frame["prev_wave"] is not None:
        raise FrameValidationError("5", "prev_wave must be null for this frame")
    re_genesis = frame["kind"] == f"{family}.re-genesis"
    if re_genesis and frame["seq"] != 0:
        raise FrameValidationError("4", "re-genesis must be a genesis frame")
    signature_trust = None
    if frame["sig"] is None:
        if family == "swarm" or re_genesis:
            raise FrameValidationError("6", "swarm and re-genesis frames require signatures")
    else:
        try:
            signature_trust = verify_detached_jws(
                frame["sig"],
                _signature_payload(frame),
                registry,
                artifact_utc=frame["utc"],
                require_estate_owner=re_genesis,
            )
        except (TrustError, ValidationError) as exc:
            raise FrameValidationError("6", str(exc)) from exc
    return family, signature_trust


class FrameConsumer:
    """Accept frames only through registered genesis and persisted monotonic state."""

    def __init__(self, registry: VerifiedRegistry, heads: HeadStore):
        if not isinstance(registry, VerifiedRegistry):
            raise TrustError("FrameConsumer requires a VerifiedRegistry proof")
        if type(heads) not in {MemoryHeadStore, SQLiteHeadStore}:
            raise TrustError("FrameConsumer requires an SDK monotonic head store")
        self.registry = registry
        self.heads = heads

    def _commit_or_resolve_race(
        self, expected_hash: str | None, new_head: StreamHead
    ) -> None:
        try:
            self.heads.commit(expected_hash, new_head)
            return
        except FrameStateError as original:
            winner = self.heads.get(new_head.stream_id)
            if winner is None:
                raise original
            if winner.forked:
                raise FrameStateError("4", "concurrent winner is already forked") from original
            same_successor_slot = (
                winner.seq == new_head.seq
                and winner.prev == new_head.prev
                and winner.prev_wave == new_head.prev_wave
            )
            if same_successor_slot and winner.frame_hash == new_head.frame_hash:
                raise FrameStateError("4", "concurrent identical successor is a duplicate") from original
            expected_is_ancestor = (
                expected_hash is not None and expected_hash in winner.lineage
            )
            contender_is_winner_ancestor = new_head.frame_hash in winner.lineage
            if contender_is_winner_ancestor:
                raise FrameStateError(
                    "4", "concurrent identical lineage already contains this successor"
                ) from original
            if same_successor_slot or expected_is_ancestor:
                try:
                    self.heads.mark_fork(new_head.stream_id, winner.frame_hash)
                except FrameStateError as mark_error:
                    latest = self.heads.get(new_head.stream_id)
                    if latest is not None and latest.forked:
                        raise FrameStateError(
                            "4", "concurrent distinct successors quarantined as a fork"
                        ) from mark_error
                    raise FrameStateError(
                        "4", "head advanced again while quarantining concurrent fork"
                    ) from mark_error
                raise FrameStateError(
                    "4", "concurrent distinct successors quarantined as a fork"
                ) from original
            raise FrameStateError("4", "head changed concurrently") from original

    def accept(self, frame: Mapping[str, Any], *, stream_id: str) -> AcceptedFrame:
        return self._accept(frame, stream_id=stream_id, allow_anchor_transition=False)

    def accept_anchor_transition_reset(
        self, frame: Mapping[str, Any], *, stream_id: str
    ) -> AcceptedFrame:
        """Explicitly accept only a cryptographically valid new-anchor re-genesis."""

        return self._accept(frame, stream_id=stream_id, allow_anchor_transition=True)

    def _accept(
        self,
        frame: Mapping[str, Any],
        *,
        stream_id: str,
        allow_anchor_transition: bool,
    ) -> AcceptedFrame:
        if self.registry.is_stream_retired(stream_id):
            raise FrameStateError(
                "4", "stream was retired by an identity-reanchored genesis mapping"
            )
        registration = self.registry.genesis_registration(stream_id)
        registered_genesis = registration.frame_hash
        current = self.heads.get(stream_id)
        same_anchor = current is None or current.registry_anchor == self.registry.anchor
        if (
            current is not None
            and same_anchor
            and self.registry.registry_seq < current.registry_seq
        ):
            raise FrameStateError(
                "4", "same-anchor registry sequence is below the persisted head floor"
            )
        if current is not None and not same_anchor and not allow_anchor_transition:
            raise FrameStateError(
                "4", "different registry anchor requires explicit anchor-transition reset"
            )
        family = _validate_steps_1_to_3(
            frame, expected_stream_id=stream_id, registry=self.registry
        )
        if frame["kind"] == f"{family}.re-genesis":
            expected_migrated_stream = (
                registration.old_stream_id
                if registration.new_stream_id == stream_id
                and registration.old_stream_id is not None
                else stream_id
            )
            if frame["payload"]["migrated_from"]["stream_id"] != expected_migrated_stream:
                raise FrameValidationError(
                    "1",
                    "re-genesis migrated_from.stream_id does not match registry stream mapping",
                )
        incoming_seq = frame.get("seq") if isinstance(frame, Mapping) else None
        incoming_hash = frame.get("frame_hash") if isinstance(frame, Mapping) else None
        reset = (
            current is not None
            and incoming_seq == 0
            and registered_genesis != current.genesis_hash
        )
        if current is not None and not same_anchor and not reset:
            raise FrameStateError(
                "4", "anchor transition accepts only an exact newly registered re-genesis"
            )
        if allow_anchor_transition and (current is None or same_anchor):
            raise FrameStateError(
                "4", "anchor-transition reset requires a different out-of-band anchor"
            )
        if current is not None and current.forked and not reset:
            raise FrameStateError("4", "stream is forked; both branches remain refused")
        if (
            current is not None
            and registered_genesis != current.genesis_hash
            and not reset
        ):
            raise FrameStateError(
                "4",
                "registered genesis changed; only the exact owner-signed re-genesis may reset",
            )
        if reset:
            if same_anchor and self.registry.registry_seq <= current.registry_seq:
                raise FrameStateError("4", "genesis reset requires a newer verified registry")
            if incoming_hash != registered_genesis:
                raise FrameStateError("4", "frame is not the newly registered genesis")
            family, signature = _validate_frame(
                frame, expected_stream_id=stream_id, registry=self.registry, head=None
            )
            if frame["kind"] != f"{family}.re-genesis":
                raise FrameStateError("4", "registry-authorized reset requires family re-genesis kind")
            new_head = StreamHead(
                stream_id,
                frame["seq"],
                frame["frame_hash"],
                frame["payload_hash"],
                frame["utc"],
                frame["frame_hash"],
                self.registry.anchor,
                self.registry.registry_seq,
                frame["prev"],
                frame["prev_wave"],
                None,
                (frame["frame_hash"],),
            )
            self._commit_or_resolve_race(current.frame_hash, new_head)
            return AcceptedFrame(
                _freeze(dict(frame)),
                family,
                signature,
                self.registry.registry_seq,
                new_head,
                re_genesis_reset=True,
            )
        if current is None:
            if incoming_hash != registered_genesis:
                raise FrameStateError("4", "initial frame is not the registered genesis")
            family, signature = _validate_frame(
                frame, expected_stream_id=stream_id, registry=self.registry, head=None
            )
            genesis_hash = frame["frame_hash"]
            expected = None
        else:
            if not isinstance(incoming_seq, int) or isinstance(incoming_seq, bool):
                raise FrameValidationError("1", "seq must be a uint53 integer")
            if incoming_seq == current.seq:
                if incoming_hash != current.frame_hash:
                    if current.seq == 0:
                        raise FrameStateError(
                            "4", "alternate genesis is not the registered genesis"
                        )
                    predecessor = StreamHead(
                        stream_id=stream_id,
                        seq=current.seq - 1,
                        frame_hash=current.prev_wave or ("0" * 64),
                        payload_hash=current.prev or ("0" * 64),
                        utc=current.parent_utc or current.utc,
                        genesis_hash=current.genesis_hash,
                        registry_anchor=current.registry_anchor,
                        registry_seq=current.registry_seq,
                        prev=None,
                        prev_wave=None,
                        parent_utc=None,
                        lineage=current.lineage[:-1],
                    )
                    _validate_frame(
                        frame,
                        expected_stream_id=stream_id,
                        registry=self.registry,
                        head=predecessor,
                    )
                    self.heads.mark_fork(stream_id, current.frame_hash)
                    raise FrameStateError("4", "equal-sequence fork detected and stream quarantined")
                raise FrameStateError("4", "frame at this sequence was already accepted")
            if incoming_seq < current.seq:
                raise FrameStateError("4", "head rollback refused")
            if incoming_seq > current.seq + 1:
                raise FrameStateError("4", "branch/gap refused; direct successor required")
            family, signature = _validate_frame(
                frame, expected_stream_id=stream_id, registry=self.registry, head=current
            )
            genesis_hash = current.genesis_hash
            expected = current.frame_hash
        new_head = StreamHead(
            stream_id,
            frame["seq"],
            frame["frame_hash"],
            frame["payload_hash"],
            frame["utc"],
            genesis_hash,
            self.registry.anchor,
            self.registry.registry_seq,
            frame["prev"],
            frame["prev_wave"],
            current.utc if current is not None else None,
            (frame["frame_hash"],)
            if current is None
            else current.lineage + (frame["frame_hash"],),
        )
        self._commit_or_resolve_race(expected, new_head)
        return AcceptedFrame(
            _freeze(dict(frame)), family, signature, self.registry.registry_seq, new_head
        )


def build_frame(
    *,
    kind: str,
    stream_id: str,
    payload: dict[str, Any],
    registry: VerifiedRegistry,
    head: StreamHead | None = None,
    utc: str | None = None,
    signer: Callable[[bytes], str] | None = None,
) -> dict[str, Any]:
    """Build a frame; consumers still require registered-genesis state acceptance."""

    if not isinstance(registry, VerifiedRegistry):
        raise TrustError("build_frame requires a VerifiedRegistry proof")
    if registry.is_stream_retired(stream_id):
        raise TrustError("cannot produce frames on a registry-retired stream")
    family = registry.active_kind_family(validate_kind(kind))
    if classify_stream_id(stream_id) != family:
        raise ValidationError("kind family and stream_id form are incompatible")
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object")
    timestamp = utc or _now_utc()
    if not _valid_utc(timestamp):
        raise ValidationError("utc must use exact millisecond UTC form")
    if head is None:
        seq, prev, prev_wave = 0, None, None
    else:
        if not isinstance(head, StreamHead):
            raise ValidationError("head must be a persisted StreamHead, not an arbitrary mapping")
        if head.stream_id != stream_id or head.forked or head.seq == UINT53_MAX:
            raise ValidationError("head cannot extend this stream")
        seq = head.seq + 1
        prev = head.payload_hash
        prev_wave = head.frame_hash if family == "swarm" else None
    frame: dict[str, Any] = {
        "spec": "rapp/1",
        "kind": kind,
        "stream_id": stream_id,
        "seq": seq,
        "utc": timestamp,
        "payload": payload,
        "payload_hash": H("rapp/1:particle", payload),
        "frame_hash": "",
        "prev": prev,
        "prev_wave": prev_wave,
        "sig": None,
    }
    frame["frame_hash"] = H("rapp/1:wave", _wave_preimage(frame))
    if signer is not None:
        frame["sig"] = signer(_signature_payload(frame))
        parse_detached_jws(frame["sig"])
    _validate_frame(frame, expected_stream_id=stream_id, registry=registry, head=head)
    return frame
