"""Regression tests for generated repo page README summaries."""

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


def test_first_paragraph_skips_rapp1_network_header():
    gen = _load_generator()
    readme = (
        "# RAR -- RAPP Agent Registry\n\n"
        f"{gen.NETWORK_HEADER_START}\n"
        "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
        "[Start here](https://github.com/kody-w/rapp-installer#start-here)\n"
        f"{gen.NETWORK_HEADER_END}\n\n"
        "> **Spec:** `rapp-registry/1.0` -- canonical registry.\n\n"
        "**The open single-file agent ecosystem.** Browse and build.\n"
    )
    assert gen.first_paragraph(readme) == "> **Spec:** `rapp-registry/1.0` -- canonical registry."


def test_first_paragraph_without_network_header_is_unchanged():
    gen = _load_generator()
    readme = "# Heimdall\n\n> A RAPP front door on the public internet.\n\nSecond paragraph.\n"
    assert gen.first_paragraph(readme) == "> A RAPP front door on the public internet."


def test_rebuild_uses_real_readme_summary_after_network_header(tmp_path, monkeypatch):
    gen = _load_generator()
    (tmp_path / "repos").mkdir()
    _offline(gen, monkeypatch, tmp_path)
    readmes = {
        "RAR": (
            "# RAR -- RAPP Agent Registry\n\n"
            f"{gen.NETWORK_HEADER_START}\n"
            "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
            "[Start here](https://github.com/kody-w/rapp-installer#start-here)\n"
            f"{gen.NETWORK_HEADER_END}\n\n"
            "> **Spec:** `rapp-registry/1.0` -- the canonical agent registry.\n"
        ),
        "heimdall": (
            "# Heimdall\n\n"
            f"{gen.NETWORK_HEADER_START}\n"
            "[![RAPP/1](badge.svg)](portfolio.md) · **New to RAPP?** "
            "[Start here](https://github.com/kody-w/rapp-installer#start-here)\n"
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
    assert "> **Spec:** `rapp-registry/1.0` -- the canonical agent registry." in rar
    assert "> A RAPP front door on the public internet. Real estate, not software." in heimdall
    assert "New to RAPP?" not in rar
    assert "New to RAPP?" not in heimdall
