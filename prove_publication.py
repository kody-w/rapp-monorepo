#!/usr/bin/env python3
"""Prove snapshot publication cannot bypass review or branch protection."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
AGGREGATE_WORKFLOW = ROOT / ".github" / "workflows" / "aggregate.yml"
SDK_WORKFLOW = ROOT / ".github" / "workflows" / "sdk.yml"
RULESET = ROOT / ".github" / "rulesets" / "protected-main-publication.json"
PINNED_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def load_workflow(path: Path) -> dict:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError(f"{path} must contain a workflow object")
    return document


def action_name(step: dict) -> str:
    return str(step.get("uses", "")).split("@", 1)[0]


class ProtectedPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = load_workflow(AGGREGATE_WORKFLOW)
        cls.sdk = load_workflow(SDK_WORKFLOW)
        cls.ruleset = json.loads(RULESET.read_text(encoding="utf-8"))
        cls.job = cls.aggregate["jobs"]["aggregate"]
        cls.steps = cls.job["steps"]

    def one_action(self, name: str) -> dict:
        matches = [
            step for step in self.steps
            if action_name(step) == name
        ]
        self.assertEqual(len(matches), 1, f"expected exactly one {name} step")
        return matches[0]

    def one_named_step(self, name: str) -> dict:
        matches = [
            step for step in self.steps
            if step.get("name") == name
        ]
        self.assertEqual(len(matches), 1, f"expected exactly one {name!r} step")
        return matches[0]

    def test_publication_is_serialized_and_github_token_is_read_only(self):
        self.assertEqual(
            self.aggregate["concurrency"],
            {
                "group": "estate-snapshot-publication",
                "cancel-in-progress": False,
            },
        )
        self.assertEqual(self.aggregate["permissions"], {"contents": "read"})
        self.assertNotIn("permissions", self.job)

    def test_checkout_is_pinned_and_does_not_persist_credentials(self):
        checkout = self.one_action("actions/checkout")
        self.assertRegex(checkout["uses"], PINNED_ACTION)
        self.assertEqual(
            checkout.get("with"),
            {
                "ref": "main",
                "fetch-depth": 1,
                "persist-credentials": False,
            },
        )

    def test_publisher_token_is_pinned_and_least_privilege(self):
        token = self.one_action("actions/create-github-app-token")
        self.assertRegex(token["uses"], PINNED_ACTION)
        self.assertEqual(token.get("id"), "publisher-token")
        self.assertEqual(
            token.get("if"),
            "steps.snapshot.outputs.changed == 'true'",
        )
        self.assertEqual(
            token.get("with"),
            {
                "client-id": "${{ vars.SNAPSHOT_PUBLISHER_CLIENT_ID }}",
                "private-key": "${{ secrets.SNAPSHOT_PUBLISHER_PRIVATE_KEY }}",
                "owner": "${{ github.repository_owner }}",
                "repositories": "${{ github.event.repository.name }}",
                "permission-contents": "write",
                "permission-pull-requests": "write",
            },
        )

    def test_publication_uses_one_deterministic_non_force_branch(self):
        publish = self.one_named_step(
            "Publish the snapshot branch and pull request"
        )
        self.assertEqual(
            publish.get("if"),
            "steps.snapshot.outputs.changed == 'true'",
        )
        self.assertEqual(
            publish.get("env"),
            {
                "GH_TOKEN": "${{ steps.publisher-token.outputs.token }}",
                "SNAPSHOT_BRANCH": "automation/estate-snapshot",
            },
        )
        run = publish["run"]
        pushes = [
            line.strip() for line in run.splitlines()
            if line.strip().startswith("git push ")
        ]
        self.assertEqual(
            pushes,
            ['git push origin "HEAD:refs/heads/${SNAPSHOT_BRANCH}"'],
        )
        self.assertNotRegex(
            pushes[0],
            r"(?:^|\s)(?:-f|--force(?:-with-lease)?)(?:\s|$)",
        )
        self.assertNotIn("refs/heads/main", pushes[0])
        self.assertNotIn("gh pr merge", run)

    def test_publication_refuses_ambiguous_pull_requests(self):
        run = self.one_named_step(
            "Publish the snapshot branch and pull request"
        )["run"]
        normalized = re.sub(
            r"\s+",
            " ",
            run.replace("\\\n", " "),
        )
        self.assertIn(
            'gh pr list --repo "$GITHUB_REPOSITORY" --state open '
            '--base main --head "$SNAPSHOT_BRANCH" --json number',
            normalized,
        )
        self.assertIn('case "${#OPEN_PRS[@]}" in', run)
        self.assertIn(
            "Multiple open snapshot PRs found; refusing an ambiguous update.",
            run,
        )
        self.assertIn(
            '*) echo "::error::Multiple open snapshot PRs found; refusing '
            'an ambiguous update." exit 1 ;; esac',
            normalized,
        )

    def test_main_ruleset_has_no_bypass_and_blocks_destructive_updates(self):
        self.assertEqual(
            set(self.ruleset),
            {
                "name",
                "target",
                "enforcement",
                "bypass_actors",
                "conditions",
                "rules",
            },
        )
        self.assertEqual(self.ruleset["target"], "branch")
        self.assertEqual(self.ruleset["enforcement"], "active")
        self.assertEqual(self.ruleset["bypass_actors"], [])
        self.assertEqual(
            self.ruleset["conditions"],
            {
                "ref_name": {
                    "include": ["refs/heads/main"],
                    "exclude": [],
                },
            },
        )
        rules = {rule["type"]: rule for rule in self.ruleset["rules"]}
        self.assertEqual(
            set(rules),
            {
                "deletion",
                "non_fast_forward",
                "pull_request",
                "required_status_checks",
            },
        )
        self.assertEqual(rules["deletion"], {"type": "deletion"})
        self.assertEqual(
            rules["non_fast_forward"],
            {"type": "non_fast_forward"},
        )

    def test_main_requires_reviewed_pull_request_checks(self):
        rules = {rule["type"]: rule for rule in self.ruleset["rules"]}
        self.assertEqual(
            rules["pull_request"]["parameters"],
            {
                "allowed_merge_methods": ["merge", "squash", "rebase"],
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_approving_review_count": 0,
                "required_review_thread_resolution": True,
            },
        )
        self.assertEqual(
            rules["required_status_checks"]["parameters"],
            {
                "do_not_enforce_on_create": True,
                "required_status_checks": [
                    {"context": "sdk", "integration_id": 15368},
                    {
                        "context": "GitGuardian Security Checks",
                        "integration_id": 46505,
                    },
                ],
                "strict_required_status_checks_policy": True,
            },
        )

    def test_sdk_check_runs_for_every_pull_request_and_executes_this_proof(self):
        triggers = self.sdk.get("on", self.sdk.get(True))
        self.assertIsInstance(triggers, dict)
        self.assertIn("pull_request", triggers)
        self.assertIsNone(triggers["pull_request"])
        sdk_steps = self.sdk["jobs"]["sdk"]["steps"]
        commands = "\n".join(
            str(step.get("run", "")) for step in sdk_steps
        )
        self.assertRegex(
            commands,
            r"(?m)^\s*python prove_publication\.py\s*$",
        )
        compile_steps = [
            step for step in sdk_steps
            if step.get("name") == "Compile root SDK and tests"
        ]
        self.assertEqual(len(compile_steps), 1)
        self.assertIn(
            "prove_publication.py",
            compile_steps[0]["run"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
