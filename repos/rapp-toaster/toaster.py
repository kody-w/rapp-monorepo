#!/usr/bin/env python3
"""Compatibility launcher for the authoritative Agent Skill converter."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent / "scripts" / "toast.py"),
    run_name="__main__",
)
