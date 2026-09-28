from __future__ import annotations

import pytest

import rapp_cli.twin_hatch as twin_hatch_module

FAIL_CLOSED_TEST = "test_hatch_fails_closed_without_secure_directory_handles"
FAIL_CLOSED_REASON = (
    "twin hatch fails closed without secure directory handles; Windows support needs "
    "handle-relative traversal that opens reparse points without following them"
)


def pytest_collection_modifyitems(items):
    if twin_hatch_module._secure_walk_supported():
        return
    skip = pytest.mark.skip(reason=FAIL_CLOSED_REASON)
    for item in items:
        if item.path.name == "test_twin_hatch.py" and item.name != FAIL_CLOSED_TEST:
            item.add_marker(skip)
