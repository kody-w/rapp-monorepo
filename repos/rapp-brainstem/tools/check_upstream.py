#!/usr/bin/env python3
"""Fail closed when the public Grail installer bytes drift from the lock."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "rapp-brainstem-drift-check"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> int:
    lock = json.loads(
        (ROOT / "installer-lock.json").read_text(encoding="utf-8")
    )
    failures = []
    for platform_id, artifact in lock["artifacts"].items():
        digest = hashlib.sha256(fetch(artifact["url"])).hexdigest()
        if digest != artifact["sha256"]:
            failures.append(
                f"{platform_id}: expected {artifact['sha256']}, got {digest}"
            )
        else:
            print(f"OK {platform_id} {digest}")
    target = lock["target"]
    tag_ref = f"refs/tags/{target['tag']}"
    result = subprocess.run(
        [
            "git",
            "ls-remote",
            "--tags",
            target["repository"],
            tag_ref,
            f"{tag_ref}^{{}}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    resolved = {
        line.split()[0]
        for line in result.stdout.splitlines()
        if len(line.split()) >= 2
    }
    if result.returncode != 0 or target["commit"] not in resolved:
        failures.append(
            f"tag {target['tag']} does not resolve to {target['commit']}"
        )
    else:
        print(f"OK tag {target['tag']} -> {target['commit']}")
    version = fetch(target["version_url"]).decode("utf-8").strip()
    if version != target["version"]:
        failures.append(
            f"version: expected {target['version']}, got {version}"
        )
    else:
        print(f"OK version {version}")
    checkout = ROOT / f".upstream-check-{os.getpid()}"
    try:
        if checkout.exists():
            shutil.rmtree(checkout)
        initialized = subprocess.run(
            ["git", "init", "--bare", str(checkout)],
            text=True,
            capture_output=True,
            check=False,
        )
        fetched = subprocess.run(
            [
                "git",
                f"--git-dir={checkout}",
                "fetch",
                "--depth=1",
                "--filter=blob:none",
                target["repository"],
                target["commit"],
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        tree = subprocess.run(
            [
                "git",
                f"--git-dir={checkout}",
                "rev-parse",
                "FETCH_HEAD:rapp_brainstem",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        runtime_tree = tree.stdout.strip() if tree.returncode == 0 else None
        if (
            initialized.returncode != 0
            or fetched.returncode != 0
            or runtime_tree != target["tree"]
        ):
            failures.append(
                f"tree: expected {target['tree']}, got {runtime_tree}"
            )
        else:
            print(f"OK tree rapp_brainstem {runtime_tree}")
    finally:
        shutil.rmtree(checkout, ignore_errors=True)
    if failures:
        print("UPSTREAM RELEASE DRIFT")
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
