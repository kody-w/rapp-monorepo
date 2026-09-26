"""scripts/build_repo_pages.py keeps the Bible-authored text on every rebuild.

The nightly-sync workflow rebuilds every repo page from INVENTORY and live
repository data. These checks run the generator offline, with synthetic
repository data, and make sure a rebuild emits each hand-kept note and role
again and leaves the hand-kept repos/_index.md alone, so the dispositions that
tests/test_mirror_contract.py requires survive the nightly.
"""

import importlib.util
import sys

import pytest

from .conftest import REPO_ROOT

SCRIPTS = REPO_ROOT / "scripts"


def _load_generator():
    sys.path.insert(0, str(SCRIPTS))
    try:
        from pii_terms import PIIRosterNotConfigured

        spec = importlib.util.spec_from_file_location(
            "build_repo_pages_under_test", SCRIPTS / "build_repo_pages.py"
        )
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except PIIRosterNotConfigured:
            pytest.skip("PII roster not configured (CI injects it)")
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def _offline(gen, monkeypatch, root):
    monkeypatch.setattr(gen, "REPO_ROOT", root)
    monkeypatch.setattr(
        gen,
        "gh_repo",
        lambda name: {
            "private": False,
            "description": "Synthetic description.",
            "default_branch": "main",
            "updated_at": "2026-01-01T00:00:00Z",
            "license": {"spdx_id": "MIT"},
            "homepage": None,
        },
    )
    monkeypatch.setattr(gen, "gh_readme", lambda name: "# Title\n\nSynthetic summary.\n")


def test_hand_kept_text_matches_the_committed_pages():
    gen = _load_generator()
    for table in (gen.HAND_KEPT_NOTES, gen.HAND_KEPT_ROLES):
        for name, text in table.items():
            page = (REPO_ROOT / "repos" / f"{name}.md").read_text(encoding="utf-8")
            assert text in page, f"repos/{name}.md no longer carries its hand-kept text"


def test_first_paragraph_skips_rapp1_network_header():
    gen = _load_generator()
    readme = (
        "# RAR — RAPP Agent Registry\n\n"
        f"{gen.NETWORK_HEADER_START}\n"
        "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
        "[Start here: get your Brainstem →](https://github.com/kody-w/rapp-installer#start-here)\n"
        f"{gen.NETWORK_HEADER_END}\n\n"
        "> **Spec:** `rapp-registry/1.0` — canonical registry.\n\n"
        "**The open single-file agent ecosystem.** Browse, build, collect, and share AI agents.\n"
    )
    assert (
        gen.first_paragraph(readme)
        == "**The open single-file agent ecosystem.** Browse, build, collect, and share AI agents."
    )


def test_first_paragraph_without_network_header_is_unchanged():
    gen = _load_generator()
    readme = "# OpenRappter\n\nSerious local AI for real business work.\n\nSecond paragraph.\n"
    assert gen.first_paragraph(readme) == "Serious local AI for real business work."


def test_first_paragraph_skips_html_and_navigation_lines():
    gen = _load_generator()
    readme = (
        "# rapp-mcp\n\n"
        "<div><a href=\"https://example.test\">badge</a></div>\n\n"
        "**[Docs](https://example.test)** · **[Spec](SPEC.md)**\n\n"
        "[![CI](badge.svg)](LICENSE)\n\n"
        "Two pure-stdlib, single-file MCP servers expose local RAPP agents.\n"
    )
    assert (
        gen.first_paragraph(readme)
        == "Two pure-stdlib, single-file MCP servers expose local RAPP agents."
    )


def test_first_paragraph_prefers_plain_prose_over_notice_blockquote():
    gen = _load_generator()
    readme = (
        "# RAPP\n\n"
        "> **Repository authority:** this is a notice with [relative](./PHILOSOPHY.md).\n\n"
        "The migration map is [the adaptation inventory](./RAPP1_ADAPTATION_INVENTORY.json); "
        "the ledger is [source provenance](./HISTORICAL_SOURCE_LEDGER.json).\n"
        "\n"
        "This repository is an experimental source checkout, not a currently shipped product.\n"
    )
    assert gen.first_paragraph(readme) == (
        "This repository is an experimental source checkout, not a currently shipped product."
    )


def test_first_paragraph_unwraps_blockquote_when_no_plain_prose_exists():
    gen = _load_generator()
    readme = "# Heimdall\n\n> A RAPP front door on the public internet.\n> Real estate, not software.\n\n## Visit\n"
    assert gen.first_paragraph(readme) == (
        "A RAPP front door on the public internet. Real estate, not software."
    )


def test_first_paragraph_absolutizes_relative_links_and_images():
    gen = _load_generator()
    readme = (
        "# RAPP\n\n"
        "Read [the philosophy](./PHILOSOPHY.md), [setup](.github/skills/README.md), "
        "[API](#api), and see ![diagram](assets/map%20one.png).\n"
    )
    assert gen.first_paragraph(readme, repo="RAPP", branch="main") == (
        "Read [the philosophy](https://github.com/kody-w/RAPP/blob/main/PHILOSOPHY.md), "
        "[setup](https://github.com/kody-w/RAPP/blob/main/.github/skills/README.md), "
        "[API](https://github.com/kody-w/RAPP#api), and see "
        "![diagram](https://raw.githubusercontent.com/kody-w/RAPP/main/assets/map%20one.png)."
    )


def test_first_paragraph_absolutizes_linked_badge_when_it_is_descriptive():
    gen = _load_generator()
    readme = "# X\n\n[![diagram](assets/diagram.svg)](docs/README.md) explains the system.\n"
    assert gen.first_paragraph(readme, repo="X", branch="main") == (
        "[![diagram](https://raw.githubusercontent.com/kody-w/X/main/assets/diagram.svg)]"
        "(https://github.com/kody-w/X/blob/main/docs/README.md) explains the system."
    )


def test_rebuild_keeps_hand_kept_notes_and_roles(tmp_path, monkeypatch):
    gen = _load_generator()
    (tmp_path / "repos").mkdir()
    _offline(gen, monkeypatch, tmp_path)
    entries = {name: (tier, role) for name, tier, role in gen.INVENTORY}
    for name in sorted(set(gen.HAND_KEPT_NOTES) | set(gen.HAND_KEPT_ROLES)):
        tier, role = entries[name]
        ok, message = gen.build_one(name, tier, role)
        assert ok, message
        page = (tmp_path / "repos" / f"{name}.md").read_text(encoding="utf-8")
        assert gen.HAND_KEPT_NOTES.get(name, "") in page
        assert gen.HAND_KEPT_ROLES.get(name, "") in page
    rebuilt_rar = (tmp_path / "repos" / "RAR.md").read_text(encoding="utf-8").lower()
    assert "mirror contract is retired" in rebuilt_rar


def test_rebuild_uses_real_readme_summary_after_network_header(tmp_path, monkeypatch):
    gen = _load_generator()
    (tmp_path / "repos").mkdir()
    _offline(gen, monkeypatch, tmp_path)

    readmes = {
        "RAR": (
            "# RAR — RAPP Agent Registry\n\n"
            f"{gen.NETWORK_HEADER_START}\n"
            "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
            "[Start here: get your Brainstem →](https://github.com/kody-w/rapp-installer#start-here)\n"
            f"{gen.NETWORK_HEADER_END}\n\n"
            "> **Spec:** `rapp-registry/1.0` — the canonical agent registry.\n\n"
            "**The open single-file agent ecosystem.** Browse, build, collect, and share AI agents.\n"
        ),
        "heimdall": (
            "# Heimdall\n\n"
            f"{gen.NETWORK_HEADER_START}\n"
            "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
            "[Start here: get your Brainstem →](https://github.com/kody-w/rapp-installer#start-here)\n"
            f"{gen.NETWORK_HEADER_END}\n\n"
            "> A RAPP front door on the public internet. Real estate, not software.\n"
        ),
    }
    monkeypatch.setattr(gen, "gh_readme", lambda name: readmes[name])
    entries = {name: (tier, role) for name, tier, role in gen.INVENTORY}
    for name in ("RAR", "heimdall"):
        tier, role = entries[name]
        ok, message = gen.build_one(name, tier, role)
        assert ok, message

    rar = (tmp_path / "repos" / "RAR.md").read_text(encoding="utf-8")
    heimdall = (tmp_path / "repos" / "heimdall.md").read_text(encoding="utf-8")
    assert "**The open single-file agent ecosystem.** Browse, build, collect, and share AI agents." in rar
    assert "A RAPP front door on the public internet. Real estate, not software." in heimdall
    assert "New to RAPP?" not in rar
    assert "New to RAPP?" not in heimdall


def test_build_index_leaves_the_hand_kept_index_alone(tmp_path, monkeypatch):
    gen = _load_generator()
    committed = (REPO_ROOT / "repos" / "_index.md").read_text(encoding="utf-8")
    assert gen.INDEX_KEEP_MARKER in committed
    (tmp_path / "repos").mkdir()
    (tmp_path / "repos" / "_index.md").write_text(committed, encoding="utf-8")
    _offline(gen, monkeypatch, tmp_path)
    gen.build_index([(name, tier, role, True, "") for name, tier, role in gen.INVENTORY])
    assert (tmp_path / "repos" / "_index.md").read_text(encoding="utf-8") == committed
