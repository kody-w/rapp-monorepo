from __future__ import annotations

import shutil
import os
import io
import struct
import uuid
import zipfile
from pathlib import Path

import pytest

from rapp_sdk.eggs import (
    _patch_utf8_flags,
    accept_egg,
    extract_egg,
    inspect_egg,
    pack_egg,
)
from rapp_sdk.json_profile import canonical_bytes
from rapp_sdk.identity import mint_keyless_rappid
from rapp_sdk.errors import EggValidationError

ROOT = Path(__file__).resolve().parents[1]


def test_deterministic_organism_egg_and_extraction(rappid, registry) -> None:
    args = dict(
        variant="organism",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={},
        files={"soul.md": b"controlled\n", "rappid.json": b"{}\n"},
        registry=registry,
    )
    first = pack_egg(**args)
    second = pack_egg(**args)
    assert first == second
    inspected = inspect_egg(first)
    assert inspected.container == "zip"
    assert inspected.signature_state == "absent"
    assert inspected.semantics == "structural-inspection"
    assert (
        accept_egg(first, registry=registry).semantics
        == "verified-with-authenticated-registry"
    )

    destination = ROOT / "tests" / f".extract-{uuid.uuid4().hex}"
    try:
        written = extract_egg(first, destination, registry=registry)
        assert {path.relative_to(destination).as_posix() for path in written} == {
            "rappid.json",
            "soul.md",
        }
        assert (destination / "soul.md").read_bytes() == b"controlled\n"
    finally:
        shutil.rmtree(destination, ignore_errors=True)


def test_json_session_variant(rappid, registry) -> None:
    egg = pack_egg(
        variant="session",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={"runtime": "test", "transcript": [{"role": "user"}]},
        files=None,
        registry=registry,
    )
    assert not egg.startswith(b"PK")
    assert inspect_egg(egg).manifest["contents"] == ()


def test_egg_path_and_variant_protections(rappid, registry) -> None:
    with pytest.raises(EggValidationError, match="path"):
        pack_egg(
            variant="organism",
            rappid=rappid,
            created_utc="2026-08-23T12:00:00.000Z",
            payload={},
            files={"../escape": b"x", "rappid.json": b"{}", "soul.md": b"x"},
            registry=registry,
        )


def test_recursive_variant_and_budget_protections(rappid, registry) -> None:
    child = pack_egg(
        variant="organism",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={},
        files={"rappid.json": b"{}", "soul.md": b"soul"},
        registry=registry,
    )
    neighborhood = pack_egg(
        variant="neighborhood",
        rappid=rappid,
        created_utc="2026-08-23T12:00:01.000Z",
        payload={"members": [rappid]},
        files={"kody-w--sdk-test.egg": child},
        registry=registry,
    )
    accepted = accept_egg(neighborhood, registry=registry)
    assert accepted.children["kody-w--sdk-test.egg"].manifest["variant"] == "organism"
    with pytest.raises(EggValidationError, match="aggregate"):
        accept_egg(
            neighborhood,
            registry=registry,
            max_aggregate_bytes=len(neighborhood),
        )
    with pytest.raises(EggValidationError, match="nesting"):
        accept_egg(neighborhood, registry=registry, max_depth=1)

    wrong_child = pack_egg(
        variant="session",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={"runtime": "x", "transcript": []},
        files=None,
        registry=registry,
    )
    with pytest.raises(EggValidationError, match="children"):
        pack_egg(
            variant="neighborhood",
            rappid=rappid,
            created_utc="2026-08-23T12:00:01.000Z",
            payload={"members": [rappid]},
            files={"kody-w--sdk-test.egg": wrong_child},
            registry=registry,
        )


def test_extraction_fails_closed_without_no_follow_primitives(
    rappid, registry, monkeypatch
) -> None:
    egg = pack_egg(
        variant="organism",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={},
        files={"rappid.json": b"{}", "soul.md": b"soul"},
        registry=registry,
    )
    monkeypatch.delattr(os, "O_NOFOLLOW")
    with pytest.raises(EggValidationError, match="requires descriptor-relative"):
        extract_egg(egg, ROOT / "tests" / ".must-not-exist", registry=registry)
    with pytest.raises(EggValidationError, match="requires"):
        pack_egg(
            variant="organism",
            rappid=rappid,
            created_utc="2026-08-23T12:00:00.000Z",
            payload={},
            files={"rappid.json": b"{}"},
            registry=registry,
        )


def test_zip_comments_and_non_deterministic_metadata_are_refused(
    rappid, registry
) -> None:
    egg = pack_egg(
        variant="organism",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={},
        files={"rappid.json": b"{}", "soul.md": b"soul"},
        registry=registry,
    )
    archive_comment = bytearray(egg)
    eocd = archive_comment.rfind(b"PK\x05\x06")
    struct.pack_into("<H", archive_comment, eocd + 20, 3)
    archive_comment.extend(b"bad")
    with pytest.raises(EggValidationError, match="archive comments"):
        inspect_egg(bytes(archive_comment))

    inspected = inspect_egg(egg)
    stream = io.BytesIO()
    ordered = [("manifest.json", canonical_bytes(dict(inspected.manifest)))]
    ordered.extend(
        (item["path"], inspected.files[item["path"]])
        for item in inspected.manifest["contents"]
    )
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for index, (name, data) in enumerate(ordered):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 0
            info.external_attr = 0
            info.comment = b"entry-comment" if index == 1 else b""
            archive.writestr(info, data)
    with pytest.raises(EggValidationError, match="deterministic|metadata"):
        inspect_egg(_patch_utf8_flags(stream.getvalue()))

    changed_metadata = bytearray(egg)
    eocd = changed_metadata.rfind(b"PK\x05\x06")
    central = struct.unpack_from("<I", changed_metadata, eocd + 16)[0]
    external = struct.unpack_from("<I", changed_metadata, central + 38)[0]
    struct.pack_into("<I", changed_metadata, central + 38, external ^ 1)
    with pytest.raises(EggValidationError, match="deterministic reconstruction"):
        inspect_egg(bytes(changed_metadata))
    with pytest.raises(EggValidationError, match="signature"):
        pack_egg(
            variant="invite",
            rappid=rappid,
            created_utc="2026-08-23T12:00:00.000Z",
            payload={
                "target_rappid": rappid,
                "target_url": "https://example.invalid/",
                "target_kind": "estate",
            },
            files=None,
            registry=registry,
        )


def test_neighborhood_rejects_owner_slug_filename_collisions(
    rappid, registry
) -> None:
    same_owner_slug = mint_keyless_rappid(
        "kody-w",
        "sdk-test",
        uuid.UUID("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"),
    )
    child = pack_egg(
        variant="organism",
        rappid=same_owner_slug,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={},
        files={"rappid.json": b"{}", "soul.md": b"soul"},
        registry=registry,
    )
    with pytest.raises(EggValidationError, match="collide"):
        pack_egg(
            variant="neighborhood",
            rappid=rappid,
            created_utc="2026-08-23T12:00:01.000Z",
            payload={"members": [rappid, same_owner_slug]},
            files={"kody-w--sdk-test.egg": child},
            registry=registry,
        )


def test_signed_invite_inspection_is_recursively_frozen(
    rappid, registry, registry_factory
) -> None:
    invite = pack_egg(
        variant="invite",
        rappid=rappid,
        created_utc="2026-08-23T12:00:00.000Z",
        payload={
            "target_rappid": rappid,
            "target_url": "https://example.invalid/estate",
            "target_kind": "estate",
        },
        files=None,
        registry=registry,
        signer=registry_factory.sign,
    )
    accepted = accept_egg(invite, registry=registry)
    original_hash = accepted.egg_hash
    with pytest.raises(TypeError):
        accepted.manifest["payload"]["target_url"] = "https://attacker.invalid/"
    with pytest.raises(TypeError):
        accepted.manifest["contents"] += (
            {"path": "forged", "hash": "0" * 64},
        )
    assert accepted.egg_hash == original_hash
    assert accepted.manifest["payload"]["target_url"] == (
        "https://example.invalid/estate"
    )
