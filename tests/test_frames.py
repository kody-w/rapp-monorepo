from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import uuid

import pytest

from rapp_sdk.errors import (
    FrameStateError,
    FrameValidationError,
    TrustError,
    ValidationError,
)
from rapp_sdk.json_profile import canonical_bytes
from rapp_sdk.trust import MemoryRegistrySequenceStore
from rapp_sdk.frames import (
    FrameConsumer,
    MemoryHeadStore,
    SQLiteHeadStore,
    build_frame,
    inspect_frame,
)
from rapp_sdk.json_profile import H
from rapp_sdk.identity import mint_keyless_rappid

ROOT = Path(__file__).resolve().parents[1]


def _genesis_entry(
    stream_id: str,
    frame_hash: str,
    deprecated: bool = False,
    *,
    old_stream_id: str | None = None,
    new_stream_id: str | None = None,
) -> dict:
    entry = {
        "type": "genesis",
        "stream_id": stream_id,
        "frame_hash": frame_hash,
        "deprecated": deprecated,
    }
    if old_stream_id is not None or new_stream_id is not None:
        entry["old_stream_id"] = old_stream_id
        entry["new_stream_id"] = new_stream_id
    return entry


def _ready_stream(registry_factory, rappid):
    producer_registry = registry_factory.make(sequence=1)
    genesis = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"pulse": 1},
        registry=producer_registry,
        utc="2026-08-23T12:00:00.000Z",
    )
    consumer_registry = registry_factory.make(
        sequence=2, extra_entries=[_genesis_entry(rappid, genesis["frame_hash"])]
    )
    heads = MemoryHeadStore()
    consumer = FrameConsumer(consumer_registry, heads)
    accepted = consumer.accept(genesis, stream_id=rappid)
    return genesis, accepted, consumer_registry, heads, consumer


def test_stateful_frame_chain_tamper_and_rollback(rappid, registry_factory) -> None:
    genesis, accepted, registry, heads, consumer = _ready_stream(registry_factory, rappid)
    second = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"pulse": 2},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    report = inspect_frame(second)
    assert report["payload_hash_matches"] and report["frame_hash_matches"]
    accepted_second = consumer.accept(second, stream_id=rappid)
    assert accepted_second.head.seq == 1

    with pytest.raises(FrameStateError, match="rollback|already accepted"):
        consumer.accept(genesis, stream_id=rappid)

    gap = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"pulse": 3},
        registry=registry,
        head=accepted_second.head,
        utc="2026-08-23T12:00:02.000Z",
    )
    gap["seq"] = 3
    gap["frame_hash"] = H(
        "rapp/1:wave",
        {key: value for key, value in gap.items() if key not in {"frame_hash", "sig"}},
    )
    with pytest.raises(FrameStateError, match="gap"):
        consumer.accept(gap, stream_id=rappid)
    with pytest.raises(ValidationError, match="persisted StreamHead"):
        build_frame(
            kind="body.pulse",
            stream_id=rappid,
            payload={},
            registry=registry,
            head={"seq": 1},
        )


def test_frame_tamper_fails_before_state_transition(rappid, registry_factory) -> None:
    _, accepted, registry, _, consumer = _ready_stream(registry_factory, rappid)
    second = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"pulse": 2},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    payload_tamper = deepcopy(second)
    payload_tamper["payload"]["pulse"] = 3
    with pytest.raises(FrameValidationError) as failure:
        consumer.accept(payload_tamper, stream_id=rappid)
    assert failure.value.step == "2"

    wave_tamper = deepcopy(second)
    wave_tamper["frame_hash"] = "0" * 64
    with pytest.raises(FrameValidationError) as failure:
        consumer.accept(wave_tamper, stream_id=rappid)
    assert failure.value.step == "3"


def test_initial_frame_must_equal_registered_genesis(rappid, registry_factory) -> None:
    producer = registry_factory.make(sequence=1)
    frame = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={},
        registry=producer,
        utc="2026-08-23T12:00:00.000Z",
    )
    wrong = registry_factory.make(
        sequence=2, extra_entries=[_genesis_entry(rappid, "f" * 64)]
    )
    with pytest.raises(FrameStateError, match="registered genesis"):
        FrameConsumer(wrong, MemoryHeadStore()).accept(frame, stream_id=rappid)


def test_deprecated_kind_verifies_history_but_cannot_be_produced(
    rappid, registry_factory
) -> None:
    active_kind = {
        "type": "kind",
        "kind": "body.legacy-event",
        "family": "body",
        "deprecated": False,
    }
    producer = registry_factory.make(sequence=1, extra_entries=[active_kind])
    historical = build_frame(
        kind="body.legacy-event",
        stream_id=rappid,
        payload={"historical": True},
        registry=producer,
        utc="2026-08-23T12:00:00.000Z",
    )
    consumer_registry = registry_factory.make(
        sequence=2,
        extra_entries=[
            {**active_kind, "deprecated": True},
            _genesis_entry(rappid, historical["frame_hash"]),
        ],
    )
    accepted = FrameConsumer(consumer_registry, MemoryHeadStore()).accept(
        historical, stream_id=rappid
    )
    assert accepted.family == "body"
    with pytest.raises(TrustError, match="deprecated"):
        build_frame(
            kind="body.legacy-event",
            stream_id=rappid,
            payload={"new": "forbidden"},
            registry=consumer_registry,
        )


def test_equal_sequence_fork_quarantines_both_branches(rappid, registry_factory) -> None:
    genesis, accepted, registry, heads, consumer = _ready_stream(
        registry_factory, rappid
    )
    left = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"branch": "left"},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    right = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"branch": "right"},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    consumer.accept(left, stream_id=rappid)
    with pytest.raises(FrameStateError, match="fork"):
        consumer.accept(right, stream_id=rappid)
    with pytest.raises(FrameStateError, match="forked"):
        consumer.accept(left, stream_id=rappid)
    reset = build_frame(
        kind="body.re-genesis",
        stream_id=rappid,
        payload={
            "migrated_from": {
                "stream_id": rappid,
                "terminal_seal": "0" * 64,
                "terminal_seq": 1,
            }
        },
        registry=registry,
        utc="2026-08-23T12:05:00.000Z",
        signer=registry_factory.sign,
    )
    reset_registry = registry_factory.make(
        sequence=3,
        extra_entries=[
            _genesis_entry(rappid, genesis["frame_hash"], deprecated=True),
            _genesis_entry(rappid, reset["frame_hash"]),
        ],
    )
    recovered = FrameConsumer(reset_registry, heads).accept(reset, stream_id=rappid)
    assert recovered.re_genesis_reset
    assert not heads.get(rappid).forked


def test_registry_authorized_re_genesis_requires_owner_signature(
    rappid, registry_factory
) -> None:
    old_genesis, accepted, old_registry, heads, _ = _ready_stream(registry_factory, rappid)
    unsigned = {
        "kind": "body.re-genesis",
        "stream_id": rappid,
        "payload": {
            "migrated_from": {
                "stream_id": rappid,
                "terminal_seal": "0" * 64,
                "terminal_seq": accepted.head.seq,
            }
        },
        "registry": old_registry,
        "utc": "2026-08-23T12:05:00.000Z",
    }
    with pytest.raises(FrameValidationError) as failure:
        build_frame(**unsigned)
    assert failure.value.step == "6"

    reset = build_frame(**unsigned, signer=registry_factory.sign)
    new_registry = registry_factory.make(
        sequence=3,
        extra_entries=[
            _genesis_entry(rappid, old_genesis["frame_hash"], deprecated=True),
            _genesis_entry(rappid, reset["frame_hash"]),
        ],
    )
    retired_successor = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"retired": True},
        registry=new_registry,
        head=accepted.head,
        utc="2026-08-23T12:05:01.000Z",
    )
    with pytest.raises(FrameStateError, match="registered genesis changed"):
        FrameConsumer(new_registry, heads).accept(
            retired_successor, stream_id=rappid
        )
    accepted_reset = FrameConsumer(new_registry, heads).accept(reset, stream_id=rappid)
    assert accepted_reset.re_genesis_reset
    assert accepted_reset.head.seq == 0


def test_head_registry_floor_and_explicit_anchor_transition(
    rappid, registry_factory
) -> None:
    genesis, accepted, registry_v2, heads, _ = _ready_stream(
        registry_factory, rappid
    )
    registry_v3 = registry_factory.make(
        sequence=3,
        extra_entries=[_genesis_entry(rappid, genesis["frame_hash"])],
    )
    successor = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"registry": 3},
        registry=registry_v3,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    newest = FrameConsumer(registry_v3, heads).accept(successor, stream_id=rappid)
    stale_successor = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"stale": True},
        registry=registry_v2,
        head=newest.head,
        utc="2026-08-23T12:00:02.000Z",
    )
    with pytest.raises(FrameStateError, match="sequence is below"):
        FrameConsumer(registry_v2, heads).accept(stale_successor, stream_id=rappid)
    assert heads.get(rappid).registry_seq == 3

    replacement_factory = registry_factory.__class__()
    replacement_producer = replacement_factory.make(sequence=1)
    reset = build_frame(
        kind="body.re-genesis",
        stream_id=rappid,
        payload={
            "migrated_from": {
                "stream_id": rappid,
                "terminal_seal": "0" * 64,
                "terminal_seq": newest.head.seq,
            }
        },
        registry=replacement_producer,
        utc="2026-08-23T12:10:00.000Z",
        signer=replacement_factory.sign,
    )
    replacement_registry = replacement_factory.make(
        sequence=2,
        extra_entries=[_genesis_entry(rappid, reset["frame_hash"])],
    )
    with pytest.raises(FrameStateError, match="explicit anchor-transition"):
        FrameConsumer(replacement_registry, heads).accept(reset, stream_id=rappid)
    transitioned = FrameConsumer(
        replacement_registry, heads
    ).accept_anchor_transition_reset(reset, stream_id=rappid)
    assert transitioned.head.registry_anchor == replacement_registry.anchor
    assert transitioned.head.registry_seq == 2


def test_sqlite_head_store_persists_verified_head(rappid, registry_factory) -> None:
    producer = registry_factory.make(sequence=1)
    genesis = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={},
        registry=producer,
        utc="2026-08-23T12:00:00.000Z",
    )
    registry = registry_factory.make(
        sequence=2, extra_entries=[_genesis_entry(rappid, genesis["frame_hash"])]
    )
    path = ROOT / "tests" / f".heads-{uuid.uuid4().hex}.sqlite3"
    try:
        store = SQLiteHeadStore(path)
        accepted = FrameConsumer(registry, store).accept(genesis, stream_id=rappid)
        assert SQLiteHeadStore(path).get(rappid) == accepted.head
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.parametrize("backend", ["memory", "sqlite"])
def test_concurrent_distinct_successors_atomically_quarantine_fork(
    backend, rappid, registry_factory
) -> None:
    producer = registry_factory.make(sequence=1)
    genesis = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={},
        registry=producer,
        utc="2026-08-23T12:00:00.000Z",
    )
    registry = registry_factory.make(
        sequence=2, extra_entries=[_genesis_entry(rappid, genesis["frame_hash"])]
    )
    path = ROOT / "tests" / f".race-{uuid.uuid4().hex}.sqlite3"
    store = MemoryHeadStore() if backend == "memory" else SQLiteHeadStore(path)
    try:
        accepted = FrameConsumer(registry, store).accept(genesis, stream_id=rappid)
        left = build_frame(
            kind="body.pulse",
            stream_id=rappid,
            payload={"branch": "left"},
            registry=registry,
            head=accepted.head,
            utc="2026-08-23T12:00:01.000Z",
        )
        right = build_frame(
            kind="body.pulse",
            stream_id=rappid,
            payload={"branch": "right"},
            registry=registry,
            head=accepted.head,
            utc="2026-08-23T12:00:01.000Z",
        )
        original_commit = store.commit
        armed = True

        def racing_commit(expected_hash, new_head):
            nonlocal armed
            if armed:
                armed = False
                store.commit = original_commit
                FrameConsumer(registry, store).accept(right, stream_id=rappid)
                store.commit = racing_commit
            original_commit(expected_hash, new_head)

        store.commit = racing_commit
        with pytest.raises(FrameStateError, match="quarantined as a fork"):
            FrameConsumer(registry, store).accept(left, stream_id=rappid)
        assert store.get(rappid).forked
    finally:
        path.unlink(missing_ok=True)


def test_concurrent_identical_successor_reports_duplicate(
    rappid, registry_factory
) -> None:
    _, accepted, registry, store, _ = _ready_stream(registry_factory, rappid)
    successor = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"same": True},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    original_commit = store.commit
    armed = True

    def racing_commit(expected_hash, new_head):
        nonlocal armed
        if armed:
            armed = False
            original_commit(expected_hash, new_head)
        original_commit(expected_hash, new_head)

    store.commit = racing_commit
    with pytest.raises(FrameStateError, match="duplicate"):
        FrameConsumer(registry, store).accept(successor, stream_id=rappid)
    assert not store.get(rappid).forked


def test_concurrent_winner_advanced_past_slot_still_quarantines_fork(
    rappid, registry_factory
) -> None:
    _, accepted, registry, store, _ = _ready_stream(registry_factory, rappid)
    contender = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"branch": "contender"},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    winner = build_frame(
        kind="body.pulse",
        stream_id=rappid,
        payload={"branch": "winner"},
        registry=registry,
        head=accepted.head,
        utc="2026-08-23T12:00:01.000Z",
    )
    original_commit = store.commit
    armed = True

    def racing_commit(expected_hash, new_head):
        nonlocal armed
        if armed:
            armed = False
            store.commit = original_commit
            winner_accepted = FrameConsumer(registry, store).accept(
                winner, stream_id=rappid
            )
            winner_next = build_frame(
                kind="body.pulse",
                stream_id=rappid,
                payload={"branch": "winner-next"},
                registry=registry,
                head=winner_accepted.head,
                utc="2026-08-23T12:00:02.000Z",
            )
            FrameConsumer(registry, store).accept(winner_next, stream_id=rappid)
            store.commit = racing_commit
        original_commit(expected_hash, new_head)

    store.commit = racing_commit
    with pytest.raises(FrameStateError, match="quarantined as a fork"):
        FrameConsumer(registry, store).accept(contender, stream_id=rappid)
    persisted = store.get(rappid)
    assert persisted.seq == 2
    assert persisted.forked


def test_identity_reanchored_re_genesis_uses_registry_stream_mapping(
    registry_factory,
) -> None:
    old_stream = mint_keyless_rappid(
        "kody-w",
        "old-organism",
        uuid.UUID("11111111-2222-4333-8444-555555555555"),
    )
    new_stream = mint_keyless_rappid(
        "kody-w",
        "new-organism",
        uuid.UUID("66666666-7777-4888-8999-aaaaaaaaaaaa"),
    )
    producer = registry_factory.make(sequence=1)
    payload = {
        "migrated_from": {
            "stream_id": old_stream,
            "terminal_seal": "0" * 64,
            "terminal_seq": 12,
        }
    }
    reset = build_frame(
        kind="body.re-genesis",
        stream_id=new_stream,
        payload=payload,
        registry=producer,
        utc="2026-08-23T12:10:00.000Z",
        signer=registry_factory.sign,
    )
    tombstone_core = {
        "type": "tombstone",
        "rappid": old_stream,
        "revoked_utc": "2026-08-23T12:09:59.000Z",
    }
    tombstone = {
        **tombstone_core,
        "sig": registry_factory.sign(canonical_bytes(tombstone_core)),
    }
    reanchor_core = {
        "type": "re-anchor",
        "old_rappid": old_stream,
        "new_rappid": new_stream,
        "case": "compromise",
        "utc": "2026-08-23T12:09:59.000Z",
    }
    reanchor = {
        **reanchor_core,
        "sig": registry_factory.sign(canonical_bytes(reanchor_core)),
    }
    mapped_genesis = _genesis_entry(
        new_stream,
        reset["frame_hash"],
        old_stream_id=old_stream,
        new_stream_id=new_stream,
    )
    retired_old_genesis = _genesis_entry(old_stream, "a" * 64, deprecated=True)
    with pytest.raises(TrustError, match="verified identity re-anchor"):
        registry_factory.make(
            sequence=2,
            extra_entries=[retired_old_genesis, mapped_genesis],
            state=MemoryRegistrySequenceStore(),
        )
    with pytest.raises(TrustError, match="only deprecated genesis"):
        registry_factory.make(
            sequence=2,
            extra_entries=[
                _genesis_entry(old_stream, "a" * 64),
                mapped_genesis,
                tombstone,
                reanchor,
            ],
            state=MemoryRegistrySequenceStore(),
        )
    with pytest.raises(TrustError, match="only deprecated genesis"):
        registry_factory.make(
            sequence=2,
            extra_entries=[
                _genesis_entry(old_stream, "b" * 64),
                {**mapped_genesis, "deprecated": True},
                tombstone,
                reanchor,
            ],
            state=MemoryRegistrySequenceStore(),
        )
    registry = registry_factory.make(
        sequence=2,
        extra_entries=[
            retired_old_genesis,
            mapped_genesis,
            tombstone,
            reanchor,
        ],
    )
    registration = registry.genesis_registration(new_stream)
    assert registration.old_stream_id == old_stream
    accepted = FrameConsumer(registry, MemoryHeadStore()).accept(
        reset, stream_id=new_stream
    )
    assert accepted.head.genesis_hash == reset["frame_hash"]
    assert registry.is_stream_retired(old_stream)
    with pytest.raises(TrustError, match="retired stream"):
        build_frame(
            kind="body.pulse",
            stream_id=old_stream,
            payload={"attack": "extend-old-lineage"},
            registry=registry,
        )

    wrong = build_frame(
        kind="body.re-genesis",
        stream_id=new_stream,
        payload={
            "migrated_from": {
                "stream_id": new_stream,
                "terminal_seal": "0" * 64,
                "terminal_seq": 12,
            }
        },
        registry=producer,
        utc="2026-08-23T12:10:00.000Z",
        signer=registry_factory.sign,
    )
    with pytest.raises(FrameValidationError, match="registry stream mapping"):
        FrameConsumer(registry, MemoryHeadStore()).accept(
            wrong, stream_id=new_stream
        )
