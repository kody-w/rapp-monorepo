"""Who this organism is — the per-clone identity config.

A RAPP dino is not a fork of anyone. Each clone is a fresh organism with its OWN
owner and its OWN identity. This module answers "whose dino is this?" from, in
order: `organism.json` at the repo root (written by hatch.py), then the APEX_OWNER
/ APEX_SLUG environment, then a git-config fallback, then a safe placeholder.

Keeping this in one place means chain.py (identity + memory) and immune.py (the
self-boundary) agree on who the body is, so a new owner's dino protects the new
owner's body — never silently inheriting the hatchery author's identity.
"""
import json
import os
import re
import subprocess
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_CONFIG = _REPO / "organism.json"

DEFAULT_SLUG = "rapp-dino"


def _slugify(s):
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s


def _git_login():
    for args in (["config", "user.username"], ["config", "user.name"]):
        try:
            out = subprocess.run(["git", *args], capture_output=True, text=True, timeout=3)
            if out.returncode == 0 and out.stdout.strip():
                return _slugify(out.stdout)
        except (OSError, subprocess.SubprocessError):
            pass
    return ""


def load():
    """Return {owner, slug, rappid?, created_utc?, default_apex?}. Never raises."""
    data = {}
    if _CONFIG.exists():
        try:
            data = json.loads(_CONFIG.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    owner = _slugify(data.get("owner") or os.environ.get("APEX_OWNER") or _git_login() or "you")
    slug = _slugify(data.get("slug") or os.environ.get("APEX_SLUG") or DEFAULT_SLUG)
    out = {"owner": owner, "slug": slug}
    for k in ("rappid", "created_utc", "default_apex"):
        if data.get(k):
            out[k] = data[k]
    return out


def owner():
    return load()["owner"]


def slug():
    return load()["slug"]


def config_path():
    return _CONFIG
