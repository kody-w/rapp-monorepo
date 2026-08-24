"""The retired ecosystem mirror claim cannot silently become active again."""

import json

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
