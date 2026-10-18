#!/usr/bin/env python3
"""No-network tests for authenticated default-branch and isolated content checkout."""
from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch
from pathlib import Path

from codex_target_adapter import AdapterError, GitHubEffects
from task_content_baseline import BaselineError, PublicationPhase
from task_content_checkout import attest_default_branch, checkout_attested_base

SHA = "a" * 40
OTHER = "b" * 40
EXECUTOR = "c" * 40
TARGET = "Young-Consultations/consulting-playbook"


def read(endpoint: str, **kwargs: object) -> dict:
    assert kwargs["token"] == "read-token"
    assert kwargs["timeout_seconds"] == 10
    if endpoint == f"repos/{TARGET}":
        return {"full_name": TARGET, "default_branch": "main"}
    if endpoint == f"repos/{TARGET}/branches/main":
        return {"name": "main", "commit": {"sha": SHA}}
    raise AssertionError("unexpected GitHub read endpoint")


class ContentCheckoutTests(unittest.TestCase):
    def test_immutable_sha_is_derived_from_independent_read_endpoints(self):
        base = attest_default_branch(
            TARGET, "delivery-42", EXECUTOR, token="read-token",
            timeout_seconds=10, read=read,
        )
        self.assertEqual(base.content_sha, SHA)
        self.assertEqual(base.executor_sha, EXECUTOR)

    def test_missing_token_and_wrong_repository_never_authorize_content(self):
        with self.assertRaises(BaselineError):
            attest_default_branch(
                TARGET, "delivery-42", EXECUTOR, token="", timeout_seconds=10, read=read,
            )
        def wrong_repo(endpoint: str, **kwargs: object) -> dict:
            return {"full_name": "DifferentOwner/foreign", "default_branch": "main"}
        with self.assertRaises(BaselineError):
            attest_default_branch(
                TARGET, "delivery-42", EXECUTOR, token="read-token",
                timeout_seconds=10, read=wrong_repo,
            )

    def test_read_only_git_fetch_has_exact_worktree_and_no_persisted_token(self):
        base = attest_default_branch(
            TARGET, "delivery-42", EXECUTOR, token="read-token",
            timeout_seconds=10, read=read,
        )
        commands = []
        def fake_git(command, **kw):
            commands.append((command, kw))
            assert "read-token" not in " ".join(command)
            if command[:3] == ["git", "rev-parse", "--verify"]:
                return subprocess.CompletedProcess(command, 0, SHA + "\n", "")
            return subprocess.CompletedProcess(command, 0, "", "")
        with checkout_attested_base(base, token="read-token", timeout_seconds=10, run=fake_git) as checkout:
            self.assertTrue(checkout.root.is_dir())
            self.assertEqual(len(commands), 6)
            self.assertEqual(commands[1][0][0:4], ["git", "-c", "core.hooksPath=/dev/null", "fetch"])
            self.assertEqual(commands[1][1]["env"]["GIT_PASSWORD"], "read-token")
            self.assertFalse(any("GIT_PASSWORD" in kw["env"] for i,(_,kw) in enumerate(commands) if i!=1))
            self.assertFalse((checkout.root.parent/"read-askpass.sh").exists())
            self.assertTrue(all(kw["env"].get("GIT_CONFIG_NOSYSTEM")=="1" for _,kw in commands))
        self.assertFalse(checkout.root.exists())

    def test_publisher_head_attestation_preserves_partial_branch_and_pr(self):
        base = attest_default_branch(
            TARGET, "delivery-42", EXECUTOR, token="read-token",
            timeout_seconds=10, read=read,
        )
        effects = GitHubEffects()
        effects._content_checkout = type("Prepared", (), {"base": base})()
        effects._content_read_token = "read-token"
        for phase, expected in (
            (PublicationPhase.BEFORE_PUSH, "no topic push"),
            (PublicationPhase.AFTER_PUSH_BEFORE_PR, "quarantined"),
            (PublicationPhase.AFTER_PR, "human review required"),
        ):
            with self.subTest(phase=phase):
                with patch("codex_target_adapter.attest_default_branch", side_effect=BaselineError("unavailable")):
                    with self.assertRaises(AdapterError) as ctx:
                        effects._check_content_base_head(
                            phase, "codex/delivery-42", 10,
                            pr="https://github.com/Young-Consultations/consulting-playbook/pull/7"
                            if phase == PublicationPhase.AFTER_PR else None,
                        )
                self.assertIn(expected, ctx.exception.safe_message)
                self.assertEqual(ctx.exception.branch, "codex/delivery-42")
                self.assertEqual(ctx.exception.status, "ambiguous-rejected")
                if phase == PublicationPhase.AFTER_PR:
                    self.assertIn("/pull/7", ctx.exception.pr)


    def test_branch_moving_during_fetch_fails_closed_and_cleans_up(self):
        base = attest_default_branch(
            TARGET, "delivery-42", EXECUTOR, token="read-token",
            timeout_seconds=10, read=read,
        )
        def moved(command, **kw):
            if command[:3] == ["git", "rev-parse", "--verify"]:
                return subprocess.CompletedProcess(command, 0, OTHER+"\n", "")
            return subprocess.CompletedProcess(command, 0, "", "")
        with self.assertRaisesRegex(BaselineError, "branch moved"):
            checkout_attested_base(base, token="read-token", timeout_seconds=10, run=moved)


if __name__ == "__main__":
    unittest.main()
