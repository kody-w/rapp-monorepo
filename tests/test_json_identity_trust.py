from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import UnsupportedAlgorithm
import rapp_sdk.identity as identity_module

from rapp_sdk.errors import CanonicalizationError, TrustError, ValidationError
from rapp_sdk.identity import (
    classify_stream_id,
    mint_keyed_rappid,
    mint_keyless_rappid,
    validate_kind,
    validate_rappid,
)
from rapp_sdk.json_profile import H, Hb, canonical_bytes, strict_loads
from rapp_sdk.trust import (
    MemoryRegistrySequenceStore,
    SQLiteRegistrySequenceStore,
    TrustedProvisionalResolution,
    VerifiedRegistry,
    parse_detached_jws,
    verify_registry,
    verify_detached_jws,
)

ROOT = Path(__file__).resolve().parents[1]


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def test_controlled_jcs_and_hash_vectors() -> None:
    value = {"numbers": [333333333.33333329, 1e30, 4.5, 2e-3, 1e-27]}
    expected = b'{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}'
    assert canonical_bytes(value) == expected
    assert H("rapp/1:particle", value) == hashlib.sha256(
        b"rapp/1:particle\n" + expected
    ).hexdigest()
    assert Hb("rapp/1:egg", b"abc") == hashlib.sha256(
        b"rapp/1:egg\nabc"
    ).hexdigest()


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"n":9007199254740993}',
        b'{"n":1e999}',
        b'{"s":"\\ud800"}',
    ],
)
def test_strict_profile_refuses_invalid_inputs(raw: bytes) -> None:
    with pytest.raises(CanonicalizationError):
        strict_loads(raw)


def test_depth_limit() -> None:
    accepted = b"[" * 64 + b"0" + b"]" * 64
    assert strict_loads(accepted)
    raw = b"[" * 65 + b"0" + b"]" * 65
    with pytest.raises(CanonicalizationError, match="depth"):
        strict_loads(raw)
    recursion_bomb = b"[" * 2000 + b"0" + b"]" * 2000
    with pytest.raises(CanonicalizationError, match="nesting"):
        strict_loads(recursion_bomb)


def test_identity_and_grammar_vectors() -> None:
    source = uuid.UUID("00112233-4455-4677-8899-aabbccddeeff")
    expected_tail = hashlib.sha256(b"rapp/1:rappid\n" + source.bytes).hexdigest()
    value = mint_keyless_rappid("kody-w", "sdk-test", source)
    assert value == f"rappid:@kody-w/sdk-test:{expected_tail}"
    assert validate_rappid(value).tail == expected_tail
    assert classify_stream_id(value) == "body"
    assert classify_stream_id(value + ":primary") == "memory"
    assert classify_stream_id("net:planet") == "swarm"
    assert validate_kind("memory.chat-turn") == "memory.chat-turn"
    for invalid in ("Memory.chat", "memory_chat", "memory.chat.extra"):
        with pytest.raises(ValidationError):
            validate_kind(invalid)
    with pytest.raises(ValidationError, match="SPKI"):
        mint_keyed_rappid("kody-w", "invalid-key", b"not-der")


def test_unsupported_spki_algorithm_surfaces_validation_error(monkeypatch) -> None:
    def unsupported(value):
        raise UnsupportedAlgorithm("unsupported test key")

    monkeypatch.setattr(identity_module.serialization, "load_der_public_key", unsupported)
    with pytest.raises(ValidationError, match="SPKI"):
        mint_keyed_rappid("kody-w", "unsupported-key", b"synthetic-der")


def test_detached_jws_requires_opaque_verified_registry(registry_factory) -> None:
    key = ed25519.Ed25519PrivateKey.generate()
    spki = key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    kid = mint_keyed_rappid("kody-w", "signer", spki)
    header = {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": kid}
    protected = _b64(canonical_bytes(header))
    payload = b'{"event":"controlled"}'
    signature = key.sign(protected.encode() + b"." + payload)
    compact = protected + ".." + _b64(signature)
    parsed = parse_detached_jws(compact)
    registry = registry_factory.make(
        extra_entries=[
            {
                "type": "spki",
                "rappid": kid,
                "spki_der_b64": base64.b64encode(spki).decode("ascii"),
                "deprecated": False,
            }
        ]
    )
    trust = verify_detached_jws(
        parsed,
        payload,
        registry,
        artifact_utc="2026-08-23T12:00:00.000Z",
    )
    assert trust.kid == kid and not trust.owner_tenure_verified
    with pytest.raises(TypeError, match="produced only"):
        VerifiedRegistry()
    forged_proof = object.__new__(VerifiedRegistry)
    with pytest.raises(TrustError, match="not produced"):
        verify_detached_jws(
            parsed,
            payload,
            forged_proof,
            artifact_utc="2026-08-23T12:00:00.000Z",
        )
    with pytest.raises(TrustError, match="VerifiedRegistry"):
        verify_detached_jws(
            parsed,
            payload,
            object(),
            artifact_utc="2026-08-23T12:00:00.000Z",
        )


def test_registry_signature_freshness_and_monotonic_state(registry_factory) -> None:
    first = registry_factory.make(sequence=4)
    assert first.registry_seq == 4
    with pytest.raises(TrustError, match="rollback"):
        registry_factory.make(sequence=3)
    mirror_state = MemoryRegistrySequenceStore()
    registry_factory.make(sequence=6, state=mirror_state)
    with pytest.raises(TrustError, match="rollback"):
        verify_registry(
            registry_factory.raw(sequence=5),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=mirror_state,
            source="https://authorized-mirror.example.test/registry.json",
            fetched_at=registry_factory.now,
            now=registry_factory.now,
            max_age_seconds=60,
        )
    class NoOpState:
        def check_and_store(self, *args):
            return None

    with pytest.raises(TrustError, match="SDK monotonic"):
        verify_registry(
            registry_factory.raw(sequence=5),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=NoOpState(),
            source=registry_factory.source,
            fetched_at=registry_factory.now,
            now=registry_factory.now,
            max_age_seconds=60,
        )
    with pytest.raises(TrustError, match="stale"):
        verify_registry(
            registry_factory.raw(sequence=5),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=MemoryRegistrySequenceStore(),
            source=registry_factory.source,
            fetched_at=registry_factory.now - timedelta(seconds=61),
            now=registry_factory.now,
            max_age_seconds=60,
        )

    unsigned = {
        "schema": "rapp/1-registry",
        "registry_seq": 5,
        "entries": registry_factory.base_entries(),
    }
    forged = {**unsigned, "sig": registry_factory.sign(canonical_bytes(unsigned))}
    forged["entries"][0] = {"type": "estate_owner", "rappid": mint_keyless_rappid(
        "kody-w", "forged", uuid.UUID("11111111-2222-4333-8444-555555555555")
    )}
    with pytest.raises(TrustError):
        verify_registry(
            canonical_bytes(forged),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=MemoryRegistrySequenceStore(),
            source=registry_factory.source,
            fetched_at=registry_factory.now,
            now=registry_factory.now,
            max_age_seconds=60,
        )

    append_state = MemoryRegistrySequenceStore()
    registry_factory.make(sequence=1, state=append_state)
    changed = strict_loads(registry_factory.raw(sequence=2))
    changed["entries"] = [
        entry
        for entry in changed["entries"]
        if not (entry["type"] == "egg-variant" and entry["variant"] == "estate")
    ]
    unsigned_changed = {key: value for key, value in changed.items() if key != "sig"}
    changed["sig"] = registry_factory.sign(canonical_bytes(unsigned_changed))
    with pytest.raises(TrustError, match="removed"):
        verify_registry(
            canonical_bytes(changed),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=append_state,
            source=registry_factory.source,
            fetched_at=registry_factory.now,
            now=registry_factory.now,
            max_age_seconds=60,
        )


def test_hash_space_allocation_is_closed() -> None:
    with pytest.raises(CanonicalizationError, match="not allocated"):
        H("rapp/1:rappid", {})
    with pytest.raises(CanonicalizationError, match="not allocated"):
        Hb("rapp/1:particle", b"x")


def test_noncanonical_base64url_is_refused(registry_factory) -> None:
    valid = registry_factory.sign(b"payload")
    protected, _, signature = valid.split(".")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    index = alphabet.index(signature[-1])
    assert index & 0b11 == 0
    same_bytes_noncanonical = signature[:-1] + alphabet[index + 1]
    assert base64.urlsafe_b64decode(signature + "==") == base64.urlsafe_b64decode(
        same_bytes_noncanonical + "=="
    )
    with pytest.raises(ValidationError, match="canonical base64url"):
        parse_detached_jws(protected + ".." + same_bytes_noncanonical)


def test_sqlite_registry_state_persists_rollback_floor(registry_factory) -> None:
    path = ROOT / "tests" / f".registry-{uuid.uuid4().hex}.sqlite3"
    try:
        state = SQLiteRegistrySequenceStore(path)
        registry_factory.make(sequence=2, state=state)
        with pytest.raises(TrustError, match="rollback"):
            registry_factory.make(
                sequence=1, state=SQLiteRegistrySequenceStore(path)
            )
    finally:
        path.unlink(missing_ok=True)


def test_registry_owner_succession_chains_from_out_of_band_anchor(
    registry_factory,
) -> None:
    new_key = ed25519.Ed25519PrivateKey.generate()
    new_spki = new_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    new_owner = mint_keyed_rappid("kody-w", "next-estate-owner", new_spki)
    utc = "2026-08-23T12:00:00.000Z"
    core = {
        "type": "re-anchor",
        "old_rappid": registry_factory.anchor,
        "new_rappid": new_owner,
        "case": "rotation",
        "utc": utc,
    }
    old_key_sig = registry_factory.sign(canonical_bytes(core))
    reanchor_without_sig = {**core, "old_key_sig": old_key_sig}
    reanchor = {
        **reanchor_without_sig,
        "sig": registry_factory.sign(canonical_bytes(reanchor_without_sig)),
    }
    entries = [
        entry
        for entry in registry_factory.base_entries()
        if entry["type"] != "estate_owner"
    ]
    entries.extend(
        [
            {
                "type": "spki",
                "rappid": new_owner,
                "spki_der_b64": base64.b64encode(new_spki).decode("ascii"),
                "deprecated": False,
            },
            reanchor,
            {"type": "estate_owner", "rappid": new_owner},
        ]
    )
    unsigned = {"schema": "rapp/1-registry", "registry_seq": 8, "entries": entries}
    registry = {
        **unsigned,
        "sig": registry_factory.sign(
            canonical_bytes(unsigned), key=new_key, kid=new_owner
        ),
    }
    state = MemoryRegistrySequenceStore()
    registry_factory.make(sequence=7, state=state)
    proof = verify_registry(
        canonical_bytes(registry),
        out_of_band_anchor=registry_factory.anchor,
        anchor_spki_der=registry_factory.spki,
        state=state,
        source=registry_factory.source,
        fetched_at=registry_factory.now,
        now=registry_factory.now,
        max_age_seconds=60,
    )
    assert proof.owner_at("2026-08-23T11:59:59.999Z") == registry_factory.anchor
    assert proof.owner_at(utc) == new_owner
    historical_payload = b'{"historical":true}'
    historical_sig = registry_factory.sign(historical_payload)
    assert verify_detached_jws(
        historical_sig,
        historical_payload,
        proof,
        artifact_utc="2026-08-23T11:59:59.999Z",
    ).kid == registry_factory.anchor
    with pytest.raises(TrustError, match="superseded"):
        verify_detached_jws(
            historical_sig,
            historical_payload,
            proof,
            artifact_utc=utc,
        )


def test_compromised_root_cannot_authorize_its_own_estate_takeover(
    registry_factory,
) -> None:
    attacker_key = ed25519.Ed25519PrivateKey.generate()
    attacker_spki = attacker_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    attacker = mint_keyed_rappid("kody-w", "attacker-owner", attacker_spki)
    utc = "2026-08-23T12:00:00.000Z"
    tombstone_core = {
        "type": "tombstone",
        "rappid": registry_factory.anchor,
        "revoked_utc": utc,
    }
    tombstone = {
        **tombstone_core,
        "sig": registry_factory.sign(canonical_bytes(tombstone_core)),
    }
    reanchor_core = {
        "type": "re-anchor",
        "old_rappid": registry_factory.anchor,
        "new_rappid": attacker,
        "case": "compromise",
        "utc": utc,
    }
    reanchor = {
        **reanchor_core,
        "sig": registry_factory.sign(canonical_bytes(reanchor_core)),
    }
    entries = [
        entry
        for entry in registry_factory.base_entries()
        if entry["type"] != "estate_owner"
    ]
    entries.extend(
        [
            {
                "type": "spki",
                "rappid": attacker,
                "spki_der_b64": base64.b64encode(attacker_spki).decode("ascii"),
                "deprecated": False,
            },
            tombstone,
            reanchor,
            {"type": "estate_owner", "rappid": attacker},
        ]
    )
    unsigned = {"schema": "rapp/1-registry", "registry_seq": 9, "entries": entries}
    registry = {
        **unsigned,
        "sig": registry_factory.sign(
            canonical_bytes(unsigned), key=attacker_key, kid=attacker
        ),
    }
    with pytest.raises(TrustError, match="newly supplied out-of-band anchor"):
        verify_registry(
            canonical_bytes(registry),
            out_of_band_anchor=registry_factory.anchor,
            anchor_spki_der=registry_factory.spki,
            state=MemoryRegistrySequenceStore(),
            source=registry_factory.source,
            fetched_at=registry_factory.now,
            now=registry_factory.now,
            max_age_seconds=60,
        )


def test_every_reanchor_case_fails_closed_without_required_evidence(
    registry_factory,
) -> None:
    def owner_signed(entry: dict) -> dict:
        return {**entry, "sig": registry_factory.sign(canonical_bytes(entry))}

    compromised = mint_keyless_rappid(
        "kody-w",
        "compromised",
        uuid.UUID("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"),
    )
    compromise = owner_signed(
        {
            "type": "re-anchor",
            "old_rappid": compromised,
            "new_rappid": mint_keyless_rappid(
                "kody-w",
                "replacement",
                uuid.UUID("bbbbbbbb-cccc-4ddd-8eee-ffffffffffff"),
            ),
            "case": "compromise",
            "utc": "2026-08-23T12:00:00.000Z",
        }
    )
    with pytest.raises(TrustError, match="same-registry tombstone"):
        registry_factory.make(extra_entries=[compromise], state=MemoryRegistrySequenceStore())
    late_tombstone_core = {
        "type": "tombstone",
        "rappid": compromised,
        "revoked_utc": "2026-08-23T12:00:00.001Z",
    }
    late_tombstone = {
        **late_tombstone_core,
        "sig": registry_factory.sign(canonical_bytes(late_tombstone_core)),
    }
    with pytest.raises(TrustError, match="no later than re-anchor"):
        registry_factory.make(
            extra_entries=[late_tombstone, compromise],
            state=MemoryRegistrySequenceStore(),
        )
    tombstone_core = {
        "type": "tombstone",
        "rappid": compromised,
        "revoked_utc": "2026-08-23T12:00:00.000Z",
    }
    tombstone = {
        **tombstone_core,
        "sig": registry_factory.sign(canonical_bytes(tombstone_core)),
    }
    accepted_compromise = registry_factory.make(
        extra_entries=[tombstone, compromise],
        state=MemoryRegistrySequenceStore(),
    )
    assert accepted_compromise.reanchored_at(compromised) == compromise["utc"]

    provisional = "rappid:@kody-w/legacy:" + ("a" * 32)
    upgrade = owner_signed(
        {
            "type": "re-anchor",
            "old_rappid": provisional,
            "new_rappid": mint_keyless_rappid(
                "kody-w",
                "upgraded",
                uuid.UUID("cccccccc-dddd-4eee-8fff-aaaaaaaaaaaa"),
            ),
            "case": "upgrade",
            "utc": "2026-08-23T12:00:01.000Z",
        }
    )
    with pytest.raises(TrustError, match="trusted provisional-owner"):
        registry_factory.make(extra_entries=[upgrade], state=MemoryRegistrySequenceStore())
    accepted_upgrade = registry_factory.make(
        extra_entries=[upgrade],
        state=MemoryRegistrySequenceStore(),
        trusted_provisional_resolutions=(
            TrustedProvisionalResolution(
                provisional,
                "kody-w",
                "owner-controlled historical resolution ledger",
            ),
        ),
    )
    assert accepted_upgrade.reanchored_at(provisional) == "2026-08-23T12:00:01.000Z"

    old_key = ed25519.Ed25519PrivateKey.generate()
    old_spki = old_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    tagged_old = mint_keyed_rappid("kody-w", "pre-rev3", old_spki)
    tag_migrate = owner_signed(
        {
            "type": "re-anchor",
            "old_rappid": tagged_old,
            "new_rappid": mint_keyless_rappid(
                "kody-w",
                "tagged-replacement",
                uuid.UUID("dddddddd-eeee-4fff-8aaa-bbbbbbbbbbbb"),
            ),
            "case": "tag-migrate",
            "utc": "2026-08-23T12:00:02.000Z",
        }
    )
    with pytest.raises(TrustError, match="untagged tail"):
        registry_factory.make(
            extra_entries=[
                {
                    "type": "spki",
                    "rappid": tagged_old,
                    "spki_der_b64": base64.b64encode(old_spki).decode("ascii"),
                    "deprecated": True,
                },
                tag_migrate,
            ],
            state=MemoryRegistrySequenceStore(),
        )
    untagged_old = (
        "rappid:@kody-w/pre-rev3-valid:" + hashlib.sha256(old_spki).hexdigest()
    )
    valid_tag_migrate = owner_signed(
        {
            **{key: value for key, value in tag_migrate.items() if key != "sig"},
            "old_rappid": untagged_old,
        }
    )
    accepted_tag_migrate = registry_factory.make(
        extra_entries=[
            {
                "type": "spki",
                "rappid": untagged_old,
                "spki_der_b64": base64.b64encode(old_spki).decode("ascii"),
                "deprecated": True,
            },
            valid_tag_migrate,
        ],
        state=MemoryRegistrySequenceStore(),
    )
    assert accepted_tag_migrate.reanchored_at(untagged_old) == valid_tag_migrate["utc"]
    payload = b'{"pre_rev3":true}'
    header = {
        "alg": "EdDSA",
        "b64": False,
        "crit": ["b64"],
        "kid": untagged_old,
    }
    protected = _b64(canonical_bytes(header))
    old_signature = (
        protected
        + ".."
        + _b64(old_key.sign(protected.encode("ascii") + b"." + payload))
    )
    assert verify_detached_jws(
        old_signature,
        payload,
        accepted_tag_migrate,
        artifact_utc="2026-08-23T12:00:01.999Z",
    ).kid == untagged_old
    with pytest.raises(TrustError, match="superseded"):
        verify_detached_jws(
            old_signature,
            payload,
            accepted_tag_migrate,
            artifact_utc=valid_tag_migrate["utc"],
        )
