"""Synthetic fixed-grammar checklist reference; no host adapter or release authority."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

MAX_ITEMS = 50
MAX_TEXT = 120
MAX_MESSAGE = 256
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,31}")
IDENTIFIER_GUIDANCE = (
    "Use an ID matching [a-z][a-z0-9-]{0,31}: start with a lowercase ASCII letter, "
    "then use only lowercase ASCII letters, digits, or hyphens (1-32 characters). "
    "Example: item-1."
)
HELP = (
    "Use: list | add <id> <text> | done <id> | help. "
    f"{IDENTIFIER_GUIDANCE} "
    "Items exist only in this process. I cannot publish, sign, or merge."
)


def _text_valid(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 1 <= len(value) <= MAX_TEXT
        and value == value.strip()
        and value.isprintable()
    )


def _copy_items(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list) or len(items) > MAX_ITEMS:
        raise ValueError("Invalid checklist state.")
    seen: set[str] = set()
    result = []
    for item in items:
        if (
            not isinstance(item, dict)
            or set(item) != {"id", "text", "done"}
            or not isinstance(item["id"], str)
            or IDENTIFIER.fullmatch(item["id"]) is None
            or item["id"] in seen
            or not _text_valid(item["text"])
            or type(item["done"]) is not bool
        ):
            raise ValueError("Invalid checklist state.")
        seen.add(item["id"])
        result.append(dict(item))
    return result


def respond(
    items: list[dict[str, Any]], message: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    state = _copy_items(items)

    def answer(status: str, text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return state, {
            "status": status,
            "message": text,
            "items": [dict(item) for item in state],
            "effects": "process-memory-only",
        }

    if (
        not isinstance(message, str)
        or not 1 <= len(message) <= MAX_MESSAGE
        or not message.isprintable()
    ):
        return answer("refused", f"Use one printable command of at most {MAX_MESSAGE} characters. {HELP}")
    parts = message.strip().split(maxsplit=2)
    if parts == ["help"]:
        return answer("ok", HELP)
    if parts == ["list"]:
        text = f"{len(state)} item(s)." if state else "No items yet. Try: add sample Inspect the package"
        return answer("ok", text)
    if len(parts) == 3 and parts[0] == "add":
        identifier, text = parts[1], parts[2]
        if IDENTIFIER.fullmatch(identifier) is None or not _text_valid(text):
            return answer("refused", f"{IDENTIFIER_GUIDANCE} Use printable text of 1-120 characters.")
        if any(item["id"] == identifier for item in state):
            return answer("refused", "That ID already exists. Choose another ID; no item was changed.")
        if len(state) == MAX_ITEMS:
            return answer("refused", f"This reference allows at most {MAX_ITEMS} items.")
        state.append({"id": identifier, "text": text, "done": False})
        return answer("ok", f"Added {identifier}.")
    if len(parts) == 2 and parts[0] == "done":
        for item in state:
            if item["id"] == parts[1]:
                if item["done"]:
                    return answer("ok", f"Already done: {item['id']}.")
                item["done"] = True
                return answer("ok", f"Completed {item['id']}.")
        return answer("refused", "No item has that ID. Use list to inspect the current checklist.")
    return answer("refused", HELP)


def main() -> None:
    state: list[dict[str, Any]] = []
    while True:
        line = sys.stdin.readline(MAX_MESSAGE + 2)
        if not line:
            break
        if len(line) > MAX_MESSAGE and not line.endswith("\n"):
            remainder = line
            while remainder and not remainder.endswith("\n"):
                remainder = sys.stdin.readline(MAX_MESSAGE + 2)
        state, reply = respond(state, line.removesuffix("\n"))
        print(json.dumps(reply, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
