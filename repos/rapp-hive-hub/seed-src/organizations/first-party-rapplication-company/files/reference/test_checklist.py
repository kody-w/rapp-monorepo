from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from checklist import HELP, MAX_ITEMS, MAX_MESSAGE, MAX_TEXT, respond

ROOT = Path(__file__).resolve().parents[1]


class ChecklistTests(unittest.TestCase):
    def test_synthetic_acceptance_cases(self) -> None:
        fixture = json.loads((ROOT / "data/acceptance-cases.json").read_text())
        self.assertEqual(fixture["classification"], "public-synthetic")
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                state = []
                statuses = []
                for command in case["commands"]:
                    state, reply = respond(state, command)
                    statuses.append(reply["status"])
                    self.assertEqual(reply["items"], state)
                    self.assertEqual(reply["effects"], "process-memory-only")
                self.assertEqual(statuses, case["statuses"])
                self.assertEqual(state, case["items"])

    def test_input_and_response_do_not_alias_state(self) -> None:
        original = [{"id": "sample", "text": "Original", "done": False}]
        saved = copy.deepcopy(original)
        state, reply = respond(original, "done sample")
        self.assertEqual(original, saved)
        self.assertTrue(state[0]["done"])
        reply["items"][0]["text"] = "Changed response"
        self.assertEqual(state[0]["text"], "Original")

    def test_refusals_preserve_state(self) -> None:
        original, _ = respond([], "add sample Original")
        for command in ["unknown", "add sample Replacement", "done absent", "list extra", "add"]:
            with self.subTest(command=command):
                state, reply = respond(original, command)
                self.assertEqual(state, original)
                self.assertEqual(reply["status"], "refused")

    def test_message_bounds_and_controls(self) -> None:
        for message in ["", " " * 3, "a" * (MAX_MESSAGE + 1), "list\nadd a Text", "list\t", "list\0"]:
            with self.subTest(message=repr(message)):
                state, reply = respond([], message)
                self.assertEqual(state, [])
                self.assertEqual(reply["status"], "refused")
        self.assertEqual(respond([], "list" + " " * (MAX_MESSAGE - 4))[1]["status"], "ok")

    def test_text_bounds(self) -> None:
        state, reply = respond([], "add sample " + "x" * MAX_TEXT)
        self.assertEqual(reply["status"], "ok")
        unchanged, refused = respond(state, "add extra " + "x" * (MAX_TEXT + 1))
        self.assertEqual(refused["status"], "refused")
        self.assertEqual(unchanged, state)

    def test_identifier_bounds(self) -> None:
        for identifier in ["UPPER", "1start", "-start", "with_underscore", "a.b", "\u00e9", "a" * 33]:
            with self.subTest(identifier=identifier):
                state, reply = respond([], f"add {identifier} Text")
                self.assertEqual(state, [])
                self.assertEqual(reply["status"], "refused")
                self.assertIn("[a-z][a-z0-9-]{0,31}", reply["message"])
                self.assertIn("start with a lowercase ASCII letter", reply["message"])
                self.assertIn("then use only lowercase ASCII letters, digits, or hyphens", reply["message"])
                self.assertIn("1-32 characters", reply["message"])
                self.assertIn("Example: item-1.", reply["message"])
        for identifier in ["a", "item-1", "a" * 32]:
            with self.subTest(identifier=identifier):
                self.assertEqual(respond([], f"add {identifier} Text")[1]["status"], "ok")

    def test_item_count_limit(self) -> None:
        state = []
        for index in range(MAX_ITEMS):
            state, reply = respond(state, f"add item-{index} Synthetic item")
            self.assertEqual(reply["status"], "ok")
        unchanged, reply = respond(state, "add overflow Extra")
        self.assertEqual(reply["status"], "refused")
        self.assertEqual(unchanged, state)

    def test_repeat_completion_is_idempotent(self) -> None:
        state, _ = respond([], "add sample Inspect")
        once, _ = respond(state, "done sample")
        twice, reply = respond(once, "done sample")
        self.assertEqual(once, twice)
        self.assertIn("Already done", reply["message"])

    def test_help_has_no_mutation_or_authority(self) -> None:
        state, reply = respond([], "help")
        self.assertEqual(state, [])
        self.assertEqual(reply["message"], HELP)
        self.assertIn("cannot publish, sign, or merge", reply["message"])
        self.assertIn("[a-z][a-z0-9-]{0,31}", reply["message"])
        self.assertIn("Example: item-1.", reply["message"])

    def test_determinism(self) -> None:
        expected = respond([], "add sample Inspect")
        for _ in range(10):
            self.assertEqual(respond([], "add sample Inspect"), expected)

    def test_external_instructions_are_only_refused_data(self) -> None:
        for message in ["publish", "sign", "merge", "run shell", "read private files", "delete all"]:
            with self.subTest(message=message):
                state, reply = respond([], message)
                self.assertEqual(state, [])
                self.assertEqual(reply["status"], "refused")

    def test_non_text_messages_refuse(self) -> None:
        for message in [None, 1, True, [], {}, b"list"]:
            with self.subTest(message=message):
                self.assertEqual(respond([], message)[1]["status"], "refused")

    def test_invalid_supplied_state_is_not_silently_repaired(self) -> None:
        valid = {"id": "sample", "text": "Inspect", "done": False}
        bad_states = [
            None,
            {},
            [valid, valid],
            [{**valid, "done": 1}],
            [{**valid, "extra": True}],
            [{**valid, "text": "\n"}],
            [{**valid, "id": "UPPER"}],
            [valid] * (MAX_ITEMS + 1),
        ]
        for state in bad_states:
            with self.subTest(state=state), self.assertRaises(ValueError):
                respond(state, "list")

    def test_stdio_is_deterministic_and_new_process_is_empty(self) -> None:
        command = [sys.executable, "-B", str(ROOT / "reference/checklist.py")]
        messages = "list\nadd sample Inspect\ndone sample\nlist\n"
        first = subprocess.run(command, input=messages, text=True, capture_output=True, check=True)
        second = subprocess.run(command, input=messages, text=True, capture_output=True, check=True)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, "")
        replies = [json.loads(line) for line in first.stdout.splitlines()]
        self.assertEqual(len(replies), 4)
        self.assertEqual(replies[0]["items"], [])
        self.assertEqual(replies[-1]["items"], [{"id": "sample", "text": "Inspect", "done": True}])

    def test_oversized_stdio_line_is_one_refusal(self) -> None:
        command = [sys.executable, "-B", str(ROOT / "reference/checklist.py")]
        result = subprocess.run(
            command,
            input=("x" * (MAX_MESSAGE * 5)) + "\nadd sample Inspect\nlist\n",
            text=True,
            capture_output=True,
            check=True,
        )
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([reply["status"] for reply in replies], ["refused", "ok", "ok"])
        self.assertEqual(replies[0]["items"], [])
        self.assertEqual(len(replies[-1]["items"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
