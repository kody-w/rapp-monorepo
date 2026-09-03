#!/usr/bin/env python3
"""Validate the shared Copilot and Claude marketplace plugin metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"{path}: duplicate key {key!r}")
            value[key] = item
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def main() -> int:
    plugin_paths = (
        ROOT / "plugin.json",
        ROOT / ".claude-plugin/plugin.json",
    )
    marketplace_paths = (
        ROOT / ".github/plugin/marketplace.json",
        ROOT / ".claude-plugin/marketplace.json",
    )
    plugin_payloads = [path.read_bytes() for path in plugin_paths]
    marketplace_payloads = [path.read_bytes() for path in marketplace_paths]
    if len(set(plugin_payloads)) != 1:
        raise ValueError("plugin.json copies differ")
    if len(set(marketplace_payloads)) != 1:
        raise ValueError("marketplace.json copies differ")
    plugin = load_json(plugin_paths[0])
    marketplace = load_json(marketplace_paths[0])
    if (
        plugin.get("$schema")
        != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    ):
        raise ValueError("plugin must opt into Agent Plugins v1.0.0")
    if plugin.get("name") != "rapp-brainstem":
        raise ValueError("plugin name must be rapp-brainstem")
    if plugin.get("skills") not in (None, "./skills/") or not (
        ROOT / "skills"
    ).is_dir():
        raise ValueError("plugin skills path is invalid")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise ValueError("marketplace must contain exactly one plugin")
    entry = plugins[0]
    if not isinstance(entry, dict):
        raise ValueError("marketplace plugin entry is invalid")
    if entry.get("name") != plugin["name"]:
        raise ValueError("marketplace and plugin names differ")
    if entry.get("version") != plugin.get("version"):
        raise ValueError("marketplace and plugin versions differ")
    if entry.get("source") != "./":
        raise ValueError("marketplace plugin source must be ./")
    skill = ROOT / "skills/rapp-brainstem/SKILL.md"
    compatibility = ROOT / "skills/rapp-brainstem/CLAUDE.md"
    if not skill.is_file() or not compatibility.is_file():
        raise ValueError("RAPP Brainstem skill contracts are missing")
    print(
        f"Plugin manifests OK: {plugin['name']} v{plugin['version']} "
        "(Copilot + Claude)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
