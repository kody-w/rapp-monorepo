from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from rapp_sdk.identity import mint_keyed_rappid, mint_keyless_rappid
from rapp_sdk.json_profile import canonical_bytes
from rapp_sdk.trust import MemoryRegistrySequenceStore, VerifiedRegistry, verify_registry

ROOT = Path(__file__).resolve().parents[1]


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class RegistryFactory:
    def __init__(self) -> None:
        self.key = ed25519.Ed25519PrivateKey.generate()
        self.spki = self.key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.anchor = mint_keyed_rappid("kody-w", "test-estate-owner", self.spki)
        self.state = MemoryRegistrySequenceStore()
        self.source = "https://registry.example.test/rapp-1-registry.json"
        self.now = datetime(2026, 8, 23, 16, 0, tzinfo=timezone.utc)

    def sign(self, payload: bytes, *, key=None, kid: str | None = None) -> str:
        signing_key = key or self.key
        signer = kid or self.anchor
        header = {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": signer}
        protected = b64url(canonical_bytes(header))
        signature = signing_key.sign(protected.encode("ascii") + b"." + payload)
        return protected + ".." + b64url(signature)

    def base_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = [
            {"type": "estate_owner", "rappid": self.anchor},
            {
                "type": "spki",
                "rappid": self.anchor,
                "spki_der_b64": base64.b64encode(self.spki).decode("ascii"),
                "deprecated": False,
            },
        ]
        for kind, family in (
            ("body.pulse", "body"),
            ("body.re-genesis", "body"),
            ("memory.chat-turn", "memory"),
            ("memory.re-genesis", "memory"),
            ("swarm.echo", "swarm"),
            ("swarm.re-genesis", "swarm"),
        ):
            entries.append(
                {"type": "kind", "kind": kind, "family": family, "deprecated": False}
            )
        for variant in (
            "organism",
            "rapplication",
            "session",
            "invite",
            "neighborhood",
            "estate",
        ):
            entries.append(
                {"type": "egg-variant", "variant": variant, "deprecated": False}
            )
        entries.append({"type": "error-code", "code": "test-refusal"})
        return entries

    def make(
        self,
        *,
        sequence: int = 1,
        extra_entries: list[dict[str, Any]] | None = None,
        state=None,
        trusted_provisional_resolutions=(),
    ) -> VerifiedRegistry:
        raw = self.raw(sequence=sequence, extra_entries=extra_entries)
        return verify_registry(
            raw,
            out_of_band_anchor=self.anchor,
            anchor_spki_der=self.spki,
            state=state or self.state,
            source=self.source,
            fetched_at=self.now,
            now=self.now,
            max_age_seconds=60,
            trusted_provisional_resolutions=trusted_provisional_resolutions,
        )

    def raw(
        self,
        *,
        sequence: int = 1,
        extra_entries: list[dict[str, Any]] | None = None,
    ) -> bytes:
        unsigned = {
            "schema": "rapp/1-registry",
            "registry_seq": sequence,
            "entries": self.base_entries() + list(extra_entries or []),
        }
        registry = {**unsigned, "sig": self.sign(canonical_bytes(unsigned))}
        return canonical_bytes(registry)


@pytest.fixture
def rappid() -> str:
    return mint_keyless_rappid(
        "kody-w", "sdk-test", uuid.UUID("00112233-4455-4677-8899-aabbccddeeff")
    )


@pytest.fixture
def registry_factory() -> RegistryFactory:
    return RegistryFactory()


@pytest.fixture
def registry(registry_factory) -> VerifiedRegistry:
    return registry_factory.make()
