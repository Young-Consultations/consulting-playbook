#!/usr/bin/env python3
"""No-network tests for authenticated default-branch and isolated content checkout."""
from __future__ import annotations

import subprocess
import json
import os
import tempfile
import base64
import textwrap
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
                with (patch("codex_target_adapter.attest_default_branch", side_effect=BaselineError("unavailable")),
                      patch.object(effects, "_block_stale_draft")):
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


    def test_executor_must_equal_external_release_before_content_read(self):
        for authorized, observed, good in (("", EXECUTOR, False), ("main", EXECUTOR, False),
                                            (OTHER, EXECUTOR, False), (EXECUTOR, EXECUTOR, True)):
            effects = GitHubEffects()
            with (patch.dict(os.environ, {"AUTHORIZED_EXECUTOR_SHA": authorized}),
                  patch("codex_target_adapter._take_secret", return_value="read-token"),
                  patch("codex_target_adapter.subprocess.check_output", return_value=observed),
                  patch("codex_target_adapter.attest_default_branch") as attest,
                  patch("codex_target_adapter.checkout_attested_base") as checkout):
                if good:
                    effects.prepare_content("delivery-42", 10)
                    attest.assert_called_once()
                    checkout.assert_called_once()
                else:
                    with self.assertRaises(AdapterError):
                        effects.prepare_content("delivery-42", 10)
                    attest.assert_not_called()
                    checkout.assert_not_called()

    def test_workflow_guard_rejects_mutable_wrong_missing_and_unregistered_executors(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/codex-execute.yml").read_text()
        guard = textwrap.dedent(workflow.split("python3 - <<'PYTHON'\n", 1)[1].split("          PYTHON", 1)[0])
        reference = TARGET + "/.github/workflows/codex-execute.yml@codex-adapter-v9.0.0"
        entry = {"workflow_ref": reference, "conformance": {"adapter_commit_sha": EXECUTOR,
                 "adapter_ref": "codex-adapter-v9.0.0", "status": "pass"}}
        encoded = json.dumps({"content": base64.b64encode(json.dumps({"registry_format_version": 1,
                        "repositories": {TARGET: entry}}).encode()).decode()})
        for control, ref, workflow_sha, checkout_sha, good in (
            ("", reference, EXECUTOR, EXECUTOR, False),
            (OTHER, TARGET + "/.github/workflows/codex-execute.yml@main", EXECUTOR, EXECUTOR, False),
            (OTHER, reference + "-wrong", EXECUTOR, EXECUTOR, False),
            (OTHER, reference, SHA, EXECUTOR, False),
            (OTHER, reference, EXECUTOR, SHA, False),
            (OTHER, reference, EXECUTOR, EXECUTOR, True),
        ):
            with tempfile.NamedTemporaryFile() as output:
                env = {"CONTROL_PLANE_SHA": control, "OBSERVED_WORKFLOW_REF": ref,
                       "OBSERVED_WORKFLOW_SHA": workflow_sha, "GITHUB_OUTPUT": output.name}
                with (patch.dict(os.environ, env),
                      patch("subprocess.check_output", side_effect=[encoded, checkout_sha]) as calls):
                    if good:
                        exec(guard, {})
                        self.assertEqual(Path(output.name).read_text(), "executor_sha=" + EXECUTOR + "\n")
                        self.assertIn("?ref=" + OTHER, calls.call_args_list[0].args[0][-1])
                    else:
                        with self.assertRaises(SystemExit):
                            exec(guard, {})
                        self.assertEqual(Path(output.name).read_text(), "")
        self.assertLess(workflow.index("id: executor-binding"), workflow.index("from codex_target_adapter import admit"))

    def test_real_publisher_race_windows_and_durable_provenance(self):
        from codex_target_adapter import reconcile_ownership
        base = attest_default_branch(TARGET, "delivery-42", EXECUTOR, token="read-token",
                                     timeout_seconds=10, read=read)
        for stale_phase in (None, PublicationPhase.BEFORE_PUSH,
                            PublicationPhase.AFTER_PUSH_BEFORE_PR, PublicationPhase.AFTER_PR):
            for unreadable in (False, True):
                effects = GitHubEffects()
                effects._content_checkout = type("Prepared", (), {"base": base, "root": Path("/unused")})()
                effects._content_read_token = "read-token"
                phases = iter((PublicationPhase.BEFORE_PUSH, PublicationPhase.AFTER_PUSH_BEFORE_PR,
                               PublicationPhase.AFTER_PR))
                remote = {"body": "", "pushes": 0, "creates": 0, "edits": 0}
                def observation(*args, **kwargs):
                    phase = next(phases)
                    if phase == stale_phase and unreadable:
                        raise BaselineError("unreadable")
                    return type("Observed", (), {"content_sha": OTHER if phase == stale_phase else SHA})()
                def run(command, **kwargs):
                    if command[1:3] == ["diff", "--cached"]:
                        return subprocess.CompletedProcess(command, 1)
                    if command[1] == "push":
                        remote["pushes"] += 1
                    return subprocess.CompletedProcess(command, 0)
                def gh(*args, **kwargs):
                    if args[:2] == ("pr", "create"):
                        remote["creates"] += 1
                        remote["body"] = args[args.index("--body") + 1]
                        return "https://github.com/" + TARGET + "/pull/7"
                    if args[:2] == ("pr", "view"):
                        return json.dumps({"body": remote["body"], "headRefName": "codex/delivery-42",
                                           "isDraft": True, "state": "OPEN"})
                    if args[:2] == ("pr", "edit"):
                        remote["edits"] += 1
                        remote["body"] = args[args.index("--body") + 1]
                        return ""
                    if args[:2] == ("api", "--paginate"):
                        return "codex/delivery-42"
                    if args[:2] == ("pr", "list"):
                        return json.dumps([{"url": "https://github.com/" + TARGET + "/pull/7", "body": remote["body"],
                                            "state": "OPEN", "isDraft": True}])
                    raise AssertionError(args)
                with (patch("codex_target_adapter.subprocess.run", side_effect=run),
                      patch("codex_target_adapter.subprocess.check_output", return_value=SHA),
                      patch("codex_target_adapter.attest_default_branch", side_effect=observation),
                      patch.object(effects, "_publication_git_environment", return_value=({}, "/nonexistent/askpass")),
                      patch.object(effects, "_gh", side_effect=gh)):
                    if stale_phase is None:
                        effects.publish("codex/delivery-42", "delivery-42", "a" * 64, 30)
                    else:
                        with self.assertRaises(AdapterError) as ctx:
                            effects.publish("codex/delivery-42", "delivery-42", "a" * 64, 30)
                        self.assertEqual(ctx.exception.status, "ambiguous-rejected")
                    self.assertEqual(remote["pushes"], int(stale_phase != PublicationPhase.BEFORE_PUSH))
                    created = stale_phase in (None, PublicationPhase.AFTER_PR)
                    self.assertEqual(remote["creates"], int(created))
                    self.assertEqual(remote["edits"], int(stale_phase == PublicationPhase.AFTER_PR))
                    if created:
                        self.assertIn("executor-sha: " + EXECUTOR, remote["body"])
                        self.assertIn("content-base-sha: " + SHA, remote["body"])
                    if stale_phase == PublicationPhase.AFTER_PR:
                        self.assertIn("ai-sdlc-publication-blocked:", remote["body"])
                        with self.assertRaises(AdapterError):
                            reconcile_ownership(effects.discover("codex/delivery-42", "delivery-42", 10), "a" * 64)

    def test_block_failure_preserves_partial_identity(self):
        base = attest_default_branch(TARGET, "delivery-42", EXECUTOR, token="read-token",
                                     timeout_seconds=10, read=read)
        effects = GitHubEffects()
        effects._content_checkout = type("Prepared", (), {"base": base})()
        for failure in (subprocess.CalledProcessError(1, "gh"), subprocess.TimeoutExpired("gh", 1)):
            with patch.object(effects, "_gh", side_effect=failure):
                with self.assertRaises(AdapterError) as ctx:
                    effects._block_stale_draft("https://github.com/" + TARGET + "/pull/7", "codex/delivery-42", None, 1)
                self.assertEqual(ctx.exception.branch, "codex/delivery-42")
                self.assertTrue(ctx.exception.pr.endswith("/pull/7"))

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
