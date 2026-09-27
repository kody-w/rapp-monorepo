"""Bible-native docs follow the pinned authority, not the retired mirror contract."""

import json
import re
import uuid
from unittest.mock import Mock

import pytest

from .conftest import REPO_ROOT


EXPECTED_AUTHORITY = {
    "repository": "kody-w/rapp-1",
    "commit": "d2cd5abed48d3f52b86bbb975ac3558286d1db41",
    "spec_path": "SPEC.md",
    "spec_revision": 5,
    "bytes": 41952,
    "sha256": "cea7847f98f9751734995f46fd4e1bde211c8eb9d03dbbb477934213865bb91a",
}


def test_exact_rapp1_authority_pin():
    authority = json.loads(
        (REPO_ROOT / "RAPP1_AUTHORITY.json").read_text(encoding="utf-8")
    )
    for field, expected in EXPECTED_AUTHORITY.items():
        assert authority[field] == expected
    assert authority["structural_pin_only"] is True
    assert authority["authenticated_registry_acceptance"] is False
    assert authority["commit"] in authority["raw_url"]


@pytest.mark.parametrize(
    "path",
    sorted((REPO_ROOT / "quickstart").glob("*.md")),
    ids=lambda path: path.name,
)
def test_live_quickstarts_reject_name_derived_rappids(path):
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"hashlib\s*\.\s*sha256\s*\(\s*owner_repo\b", text), (
        f"{path.relative_to(REPO_ROOT)} derives a rappid tail from a name; "
        "the pinned RAPP/1 section 6.2 forbids this."
    )


@pytest.mark.parametrize(
    "relative_path",
    ["quickstart/join-and-share.md", "quickstart/your-first-twin.md"],
)
@pytest.mark.parametrize(
    "uuid_text,expected_tail",
    [
        (
            "00112233-4455-4677-8899-aabbccddeeff",
            "3edc8783b43579d59a123b50a00c7faf78963a415eac9f05f80ecc826fc756f7",
        ),
        (
            "fedcba98-7654-4321-9abc-0123456789ab",
            "905df49747cc10356bad487dd930d413edf60d746b4f697e40a4834c73dcbeb1",
        ),
    ],
    ids=["first-uuid4", "second-uuid4"],
)
def test_quickstart_mint_matches_pinned_rev5(
    relative_path, uuid_text, expected_tail, monkeypatch, capsys
):
    text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    examples = re.findall(r"^```python\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
    assert len(examples) == 1, f"{relative_path} must have one runnable mint example"

    # Fixed vectors use the raw-octet Hb rule in pinned rev-5 sections 5 and 6.2.
    mint_uuid = Mock(return_value=uuid.UUID(uuid_text))
    monkeypatch.setattr(uuid, "uuid4", mint_uuid)
    namespace = {}
    exec(compile(examples[0], relative_path, "exec"), namespace)

    rappid = namespace["rappid"]
    match = re.fullmatch(
        r"rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)/"
        r"([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})",
        rappid,
    )
    assert match is not None, f"{relative_path} emits a nonconformant rappid"
    assert 1 <= len(match[1]) <= 39
    assert 1 <= len(match[2]) <= 100
    assert f"{match[1]}/{match[2]}" == namespace["owner_repo"]
    assert match[3] == expected_tail
    mint_uuid.assert_called_once_with()
    assert capsys.readouterr().out == f"{rappid}\n"


def test_public_docs_retire_the_old_mirror_contract():
    required_dispositions = {
        "README.md": "retired",
        "OVERVIEW.md": "historical snapshot",
        "CAPABILITIES.md": "historical snapshot",
        "SCHEMAS.md": "historical snapshot",
        "THE_ONE_AGENT.md": "historical snapshot",
        "DRIFT_TRIANGLE.md": "retired ecosystem mirror contract",
        "repos/rapp-god.md": "not a public mirror",
        "repos/rapp-map.md": "quarantined-candidate",
        "repos/RAR.md": "mirror contract is retired",
    }
    for relative_path, marker in required_dispositions.items():
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8").lower()
        assert marker in text, f"{relative_path} lacks disposition {marker!r}"


def test_unreachable_private_raw_url_is_not_published_as_a_source():
    former_raw_url = (
        "raw.githubusercontent.com/kody-w/rapp-god/"
        "main/api/v1/ecosystem-spec.json"
    )
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".html", ".json", ".py", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert former_raw_url not in text, f"{path.relative_to(REPO_ROOT)} republishes retired URL"

    status = (REPO_ROOT / "RAPP1_STATUS.md").read_text(encoding="utf-8")
    assert "`kody-w/rapp-god`, owned by `kody-w`, is private" in status
    assert "exact 14-byte" in status
    assert "d5558cd419c8d46bdc958064cb97f963" in status
    assert "No private content is copied or inferred here." in status
