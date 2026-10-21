#!/usr/bin/env python3
"""Offline DEF-0125 exact-SHA content-baseline and Git-race regressions."""
from __future__ import annotations

import unittest

from task_content_baseline import (
    BaselineError,
    PublicationDisposition,
    PublicationPhase,
    TaskBase,
    require_exact_content_checkout,
    verify_publication_head,
)

SHA = "a" * 40
NEXT = "b" * 40
EXECUTOR = "c" * 40
TARGET = "Young-Consultations/consulting-playbook"


def make_base(*, repository=TARGET, branch="main", sha=SHA, executor=EXECUTOR):
    return TaskBase.from_github(
        repository=repository,
        delivery_id="delivery-167",
        executor_sha=executor,
        repo_response={"full_name": repository, "default_branch": branch},
        branch_response={"name": branch, "commit": {"sha": sha}},
    )


class ExactContentBaseTests(unittest.TestCase):
    def test_good_exact_sha_binding_keeps_independent_executor_and_content(self):
        base = make_base()
        self.assertEqual((base.executor_sha, base.content_sha), (EXECUTOR, SHA))
        self.assertNotEqual(base.executor_sha, base.content_sha)
        require_exact_content_checkout(base, SHA, False)

    def test_untrusted_target_and_invalid_evidence_fail_closed(self):
        attempts = [
            {"repository": "OtherOwner/other"},
            {"branch": "../main"},
            {"branch": "refs/heads//main"},
            {"sha": "main"},
            {"sha": SHA.upper()},
            {"sha": ""},
            {"executor": "codex-adapter-v3.1.0"},
        ]
        for arguments in attempts:
            with self.subTest(arguments=arguments):
                with self.assertRaises(BaselineError):
                    make_base(**arguments)
        with self.assertRaises(BaselineError):
            TaskBase.from_github(
                repository=TARGET, delivery_id="delivery-167",
                executor_sha=EXECUTOR,
                repo_response={"full_name": "OtherOwner/other", "default_branch": "main"},
                branch_response={"name": "main", "commit": {"sha": SHA}},
            )
        with self.assertRaises(BaselineError):
            TaskBase.from_github(
                repository=TARGET, delivery_id="delivery-167",
                executor_sha=EXECUTOR,
                repo_response={"full_name": TARGET, "default_branch": "main"},
                branch_response={"name": "unexpected", "commit": {"sha": SHA}},
            )

    def test_dirty_or_wrong_checkout_is_not_model_ready(self):
        base = make_base()
        for sha, dirty in ((NEXT, False), (SHA, True), ("main", False)):
            with self.subTest(sha=sha, dirty=dirty):
                with self.assertRaises(BaselineError):
                    require_exact_content_checkout(base, sha, dirty)

    def test_checked_publication_head_has_three_distinct_race_windows(self):
        base = make_base()
        expected = [
            (PublicationPhase.BEFORE_PUSH, PublicationDisposition.REJECT_NO_REMOTE_EFFECT),
            (PublicationPhase.AFTER_PUSH_BEFORE_PR, PublicationDisposition.QUARANTINE_OWNED_TOPIC),
            (PublicationPhase.AFTER_PR, PublicationDisposition.BLOCK_DRAFT_REVIEW),
        ]
        for phase, disposition in expected:
            with self.subTest(phase=phase):
                decision = verify_publication_head(base, NEXT, phase)
                self.assertEqual(decision.disposition, disposition)
                self.assertFalse(decision.may_continue)
                self.assertEqual((decision.base_sha, decision.observed_sha), (SHA, NEXT))
                self.assertTrue(decision.observation_verified)
                ready = verify_publication_head(base, SHA, phase)
                self.assertTrue(ready.observation_verified)
                self.assertTrue(ready.may_continue)

    def test_unverifiable_head_preserves_the_phase_and_remote_effect_action(self):
        base = make_base()
        expected = [
            (PublicationPhase.BEFORE_PUSH, PublicationDisposition.REJECT_NO_REMOTE_EFFECT),
            (PublicationPhase.AFTER_PUSH_BEFORE_PR, PublicationDisposition.QUARANTINE_OWNED_TOPIC),
            (PublicationPhase.AFTER_PR, PublicationDisposition.BLOCK_DRAFT_REVIEW),
        ]
        # None models an inaccessible API response; non-SHA values model
        # malformed or mutable responses. None of these can authorize work,
        # including after a topic push or a created draft already exists.
        for phase, disposition in expected:
            for head in ("", "main", "AB" * 20, None, {}, SHA + "0"):
                with self.subTest(phase=phase, head=head):
                    decision = verify_publication_head(base, head, phase)
                    self.assertEqual(decision.phase, phase)
                    self.assertEqual(decision.disposition, disposition)
                    self.assertIsNone(decision.observed_sha)
                    self.assertFalse(decision.observation_verified)
                    self.assertFalse(decision.may_continue)
                    self.assertEqual(decision.base_sha, SHA)

    def test_unknown_phase_fails_closed(self):
        base = make_base()
        with self.assertRaises(BaselineError):
            verify_publication_head(base, SHA, "before-push")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
