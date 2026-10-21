#!/usr/bin/env python3
"""No-network tests for authenticated default-branch and isolated content checkout."""
from __future__ import annotations

import subprocess
import json
import os
import tempfile
import base64
import textwrap
import io
from contextlib import redirect_stdout
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
    assert 0 < kwargs["timeout_seconds"] <= 10
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
            (PublicationPhase.AFTER_PUSH_BEFORE_PR, "quarantine review required"),
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
        runner_reference = reference.replace("@codex-adapter-v", "@refs/tags/codex-adapter-v")
        for control, ref, workflow_sha, checkout_sha, good in (
            ("", runner_reference, EXECUTOR, EXECUTOR, False),
            (OTHER, TARGET + "/.github/workflows/codex-execute.yml@main", EXECUTOR, EXECUTOR, False),
            (OTHER, runner_reference + "-wrong", EXECUTOR, EXECUTOR, False),
            (OTHER, runner_reference, SHA, EXECUTOR, False),
            (OTHER, runner_reference, EXECUTOR, SHA, False),
            (OTHER, runner_reference, EXECUTOR, EXECUTOR, True),
            (OTHER, reference, EXECUTOR, EXECUTOR, False),
            (OTHER, runner_reference.replace("refs/tags/", "refs/heads/"), EXECUTOR, EXECUTOR, False),
            (OTHER, "OtherOwner/foreign/.github/workflows/codex-execute.yml@refs/tags/codex-adapter-v9.0.0", EXECUTOR, EXECUTOR, False),
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
                effects._publication_checkout = effects._content_checkout
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
                                           "headRefOid": effects._candidate_sha, "headRepository": {"nameWithOwner": TARGET},
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

    def test_ambiguous_remote_create_is_rechecked_before_success(self):
        from codex_target_adapter import Ownership, canonical_digest, run_adapter
        from test_codex_execute_contract import payload
        base = attest_default_branch(TARGET, "delivery-42", EXECUTOR, token="read-token",
                                     timeout_seconds=10, read=read)
        value = payload()
        digest = canonical_digest(value)
        for observation, failure in ((head, error) for head in (SHA, OTHER, None)
                                     for error in ("exit", "timeout")):
            effects = GitHubEffects()
            effects._content_checkout = type("Prepared", (), {"base": base, "root": Path("/unused")})()
            effects._publication_checkout = effects._content_checkout
            effects._content_read_token = "read-token"
            remote = {"body": "", "creates": 0, "pushes": 0, "edits": 0}
            clock = [0.0]
            create_budgets, recovery_budgets = [], []
            def gh(*args, **kwargs):
                if args[:2] == ("pr", "create"):
                    remote["body"] = args[args.index("--body") + 1]
                    remote["creates"] += 1
                    if failure == "timeout":
                        create_budgets.append(kwargs["timeout_seconds"])
                        clock[0] += kwargs["timeout_seconds"]
                        raise subprocess.TimeoutExpired("gh", kwargs["timeout_seconds"])
                    raise subprocess.CalledProcessError(1, "gh")  # Remote success, lost response.
                if args[:2] == ("api", "--paginate"):
                    if remote["creates"]: recovery_budgets.append(kwargs["timeout_seconds"])
                    return "codex/delivery-42" if remote["creates"] else ""
                if args[:2] == ("pr", "list"):
                    return json.dumps([{"url": "https://github.com/" + TARGET + "/pull/7",
                                        "body": remote["body"], "headRefName": "codex/delivery-42",
                                        "headRefOid": SHA, "headRepository": {"nameWithOwner": TARGET},
                                        "baseRefName": "main", "isDraft": True, "state": "OPEN"}]
                                      if remote["creates"] else [])
                if args[:2] == ("api", f"repos/{TARGET}/git/ref/heads/codex/delivery-42"):
                    return json.dumps({"ref": "refs/heads/codex/delivery-42", "object": {"sha": SHA}})
                if args[:2] == ("api", f"repos/{TARGET}/commits/{SHA}"):
                    return json.dumps({"sha": SHA, "parents": [{"sha": SHA}],
                                       "commit": {"message": effects._commit_message("delivery-42", digest, EXECUTOR, SHA)}})
                if args[:2] == ("api", f"repos/{TARGET}"): return "main"
                if args[:2] == ("pr", "view"):
                    return json.dumps({"body": remote["body"], "headRefName": "codex/delivery-42",
                                       "headRefOid": effects._candidate_sha, "headRepository": {"nameWithOwner": TARGET},
                                       "isDraft": True, "state": "OPEN"})
                if args[:2] == ("pr", "edit"):
                    remote["body"] = args[args.index("--body") + 1]
                    remote["edits"] += 1
                    return ""
                raise AssertionError(args)
            def run(command, **kwargs):
                if command[1:3] == ["diff", "--cached"]:
                    return subprocess.CompletedProcess(command, 1)
                if command[1] == "push": remote["pushes"] += 1
                return subprocess.CompletedProcess(command, 0)
            recovered = Ownership(True, [{"url": "https://github.com/" + TARGET + "/pull/7",
                                          "state": "OPEN", "draft": True, "digest": digest}])
            observations = [type("Observed", (), {"content_sha": SHA})(),
                            type("Observed", (), {"content_sha": SHA})(),
                            BaselineError("unavailable") if observation is None else
                            type("Observed", (), {"content_sha": observation})()]
            if failure == "timeout" and observation == SHA:
                observations.append(type("Observed", (), {"content_sha": SHA})())
            discover = effects.discover if failure == "timeout" else [Ownership(False, []), recovered]
            with (patch.object(effects, "discover", side_effect=discover),
                  patch("codex_target_adapter.time.monotonic", side_effect=lambda: clock[0]),
                  patch.object(effects, "prepare_content"), patch.object(effects, "codex") as model,
                  patch.object(effects, "has_candidate_changes", return_value=True),
                  patch.object(effects, "validate_candidate", return_value=(True, "passed")),
                  patch.object(effects, "_gh", side_effect=gh),
                  patch.object(effects, "_publication_git_environment", return_value=({}, "/nonexistent/askpass")),
                  patch("codex_target_adapter.subprocess.run", side_effect=run),
                  patch("codex_target_adapter.subprocess.check_output", return_value=SHA),
                  patch("codex_target_adapter.attest_default_branch", side_effect=observations) as reads):
                result = run_adapter(json.dumps(value), value["concurrency_group"], "trusted", {"trusted"},
                                     effects, prior_result_effect="none").result
            self.assertEqual(reads.call_count, 4 if failure == "timeout" and observation == SHA else 3)
            model.assert_called_once()
            self.assertEqual((remote["pushes"], remote["creates"]), (1, 1 if failure == "timeout" else 3))
            if failure == "timeout":
                self.assertEqual(create_budgets, [value["timeout_minutes"] * 60 * 0.8])
                self.assertGreater(recovery_budgets[0], 0)
                self.assertLess(recovery_budgets[0], create_budgets[0])
            self.assertEqual(result["execution_status"], "duplicate-reused" if observation == SHA else "ambiguous-rejected")
            self.assertEqual(remote["edits"], int(observation != SHA))
            self.assertTrue(result["pull_request_url"].endswith("/pull/7"))
            if observation != SHA: self.assertIn("ai-sdlc-publication-blocked:", remote["body"])

    def test_baseline_shares_one_deadline_across_git_and_both_api_reads(self):
        import task_content_checkout as checkout_module
        clock = [0.0]
        budgets = []
        roots = []
        def observed_git(*args, **kwargs):
            budgets.append(kwargs["timeout"])
            clock[0] += 2
            return EXECUTOR
        def api(endpoint, **kwargs):
            budgets.append(kwargs["timeout_seconds"])
            clock[0] += 3
            return {"full_name": TARGET, "default_branch": "main"} if endpoint == f"repos/{TARGET}" else {"name": "main", "commit": {"sha": SHA}}
        def git(command, **kwargs):
            budgets.append(kwargs["timeout"])
            roots.append(kwargs["cwd"])
            clock[0] += 1
            return subprocess.CompletedProcess(command, 0, "", "")
        original_checkout = checkout_module.checkout_attested_base
        original_attest = checkout_module.attest_default_branch
        def attest(*args, **kwargs): return original_attest(*args, **kwargs, read=api)
        def checkout(*args, **kwargs): return original_checkout(*args, **kwargs, run=git)
        effects = GitHubEffects()
        with (patch("time.monotonic", side_effect=lambda: clock[0]),
              patch.dict(os.environ, {"AUTHORIZED_EXECUTOR_SHA": EXECUTOR}),
              patch("codex_target_adapter._take_secret", return_value="read-token"),
              patch("codex_target_adapter.subprocess.check_output", side_effect=observed_git),
              patch("codex_target_adapter.attest_default_branch", side_effect=attest),
              patch("codex_target_adapter.checkout_attested_base", side_effect=checkout)):
            with self.assertRaises(AdapterError) as ctx: effects.prepare_content("delivery-42", 10)
        self.assertEqual(ctx.exception.category, "timeout")
        self.assertEqual(budgets, [10, 8, 5, 2, 1])
        self.assertEqual(clock[0], 10)
        self.assertIsNone(effects._content_checkout)
        self.assertTrue(roots)
        self.assertTrue(all(not path.exists() for path in roots))

    def test_api_deadline_expiry_stops_before_second_read(self):
        clock = [0.0]
        calls = []
        def stalled(endpoint, **kwargs):
            calls.append(endpoint)
            clock[0] += kwargs["timeout_seconds"]
            return {"full_name": TARGET, "default_branch": "main"}
        with patch("time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaises(subprocess.TimeoutExpired):
                attest_default_branch(TARGET, "delivery-42", EXECUTOR, token="read-token", timeout_seconds=10, read=stalled)
        self.assertEqual(len(calls), 1)

    def test_pushed_object_survives_topic_ref_deletion_in_canonical_evidence(self):
        from codex_target_adapter import Ownership, canonical_digest, run_adapter
        from task_content_baseline import TaskBase
        from test_codex_execute_contract import payload
        actual_run = subprocess.run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "content"
            bare = Path(directory) / "remote.git"
            root.mkdir()
            def git(*args, cwd=root):
                return actual_run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
            git("init", "--quiet")
            git("config", "user.name", "test")
            git("config", "user.email", "test@example.com")
            (root / "content.md").write_text("baseline")
            git("add", "content.md")
            git("commit", "-qm", "baseline")
            base_sha = git("rev-parse", "HEAD")
            git("init", "--quiet", "--bare", str(bare))
            base = TaskBase(TARGET, "main", base_sha, EXECUTOR, "delivery-42")
            value = payload()
            effects = GitHubEffects()
            effects._content_checkout = type("Prepared", (), {"base": base, "root": root})()
            effects._publication_checkout = effects._content_checkout
            effects._content_read_token = "read-token"
            pushed = []
            observations = [0]
            def observed(*args, **kwargs):
                observations[0] += 1
                if observations[0] == 2:
                    git("update-ref", "-d", "refs/heads/codex/delivery-42", cwd=bare)
                    return type("Observed", (), {"content_sha": OTHER})()
                return type("Observed", (), {"content_sha": base_sha})()
            def run(command, **kwargs):
                if command[:2] == ["git", "push"]:
                    pushed.append(command[-1].split(":")[0])
                    command = [*command[:2], str(bare), command[-1]]
                return actual_run(command, **kwargs)
            def model(*args): (root / "content.md").write_text("candidate")
            log = io.StringIO()
            with (patch.object(effects, "discover", return_value=Ownership(False, [])),
                  patch.object(effects, "prepare_content"), patch.object(effects, "codex", side_effect=model),
                  patch.object(effects, "has_candidate_changes", return_value=True),
                  patch.object(effects, "validate_candidate", return_value=(True, "passed")),
                  patch.object(effects, "_publication_git_environment", return_value=({}, "/nonexistent/askpass")),
                  patch("codex_target_adapter.attest_default_branch", side_effect=observed),
                  patch("codex_target_adapter.subprocess.run", side_effect=run), redirect_stdout(log)):
                result = run_adapter(json.dumps(value), value["concurrency_group"], "trusted", {"trusted"},
                                     effects, prior_result_effect="none").result
            self.assertEqual(result["execution_status"], "ambiguous-rejected")
            self.assertEqual(result["branch_name"], "codex/delivery-42")
            self.assertNotIn("quarantined", result["failure_message"])
            evidence = json.loads(result["failure_message"].split("; evidence=", 1)[1])
            self.assertEqual(evidence["candidate_sha"], pushed[0])
            self.assertNotEqual(pushed[0], "HEAD")
            self.assertEqual(evidence["payload_sha256"], canonical_digest(value))
            self.assertEqual(evidence["content_base_sha"], base_sha)
            self.assertEqual(evidence["executor_sha"], EXECUTOR)
            self.assertLessEqual(len(result["failure_message"]), 500)
            self.assertEqual(git("cat-file", "-t", evidence["candidate_sha"], cwd=bare), "commit")
            self.assertEqual(git("for-each-ref", "refs/heads/codex/delivery-42", cwd=bare), "")
            records = [json.loads(line)["publication_evidence"] for line in log.getvalue().splitlines()]
            self.assertEqual([r["stage"] for r in records], ["push-intent", "push-completed"])
            self.assertTrue(all(r["candidate_sha"] == pushed[0] and r["delivery_id"] == value["delivery_id"]
                                and r["payload_sha256"] == canonical_digest(value) for r in records))

    def test_final_attestation_and_blocking_share_one_deadline(self):
        from task_content_baseline import TaskBase
        base = TaskBase(TARGET, "main", SHA, EXECUTOR, "delivery-42")
        pr = "https://github.com/" + TARGET + "/pull/7"
        for elapsed_read, elapsed_view, expected_calls, expected_budgets in (
            (3, 2, ["view", "edit"], [7, 5]),
            (10, 0, [], []),
            (3, 7, ["view"], [7]),
        ):
            clock = [0.0]
            calls, budgets = [], []
            effects = GitHubEffects()
            effects._content_checkout = type("Prepared", (), {"base": base})()
            effects._content_read_token = "read-token"
            effects._candidate_sha = "d" * 40
            effects._publication_digest = "e" * 64
            def observe(*args, **kwargs):
                self.assertEqual(kwargs["deadline"], 10)
                self.assertEqual(kwargs["timeout_seconds"], 10)
                clock[0] += elapsed_read
                if elapsed_read == 10: raise subprocess.TimeoutExpired("gh", 10)
                return type("Observed", (), {"content_sha": OTHER})()
            def gh(*args, **kwargs):
                calls.append(args[1]); budgets.append(kwargs["timeout_seconds"])
                if args[1] == "view":
                    clock[0] += elapsed_view
                    return json.dumps({"body": "<!-- ai-sdlc-delivery-id: delivery-42; payload-sha256: " + "e" * 64 + " -->",
                                       "headRefOid": effects._candidate_sha, "headRepository": {"nameWithOwner": TARGET},
                                       "headRefName": "codex/delivery-42", "isDraft": True, "state": "OPEN"})
                clock[0] += 1
                return ""
            with (patch("time.monotonic", side_effect=lambda: clock[0]),
                  patch("codex_target_adapter.attest_default_branch", side_effect=observe),
                  patch.object(effects, "_gh", side_effect=gh)):
                with self.assertRaises(AdapterError) as ctx:
                    effects._check_content_base_head(PublicationPhase.AFTER_PR, "codex/delivery-42", 10, pr=pr)
            self.assertEqual(calls, expected_calls)
            self.assertEqual(budgets, expected_budgets)
            self.assertLessEqual(clock[0], 10)
            self.assertEqual(ctx.exception.pr, pr)
            self.assertEqual(ctx.exception.branch, "codex/delivery-42")
            evidence = json.loads(ctx.exception.safe_message.split("; evidence=", 1)[1])
            self.assertEqual(evidence["candidate_sha"], "d" * 40)
            self.assertLessEqual(len(ctx.exception.safe_message), 500)
            if clock[0] == 10: self.assertIn("could not be confirmed", ctx.exception.safe_message)

    def test_timed_out_push_reconciles_exact_object_and_preserves_partial_result(self):
        from codex_target_adapter import Ownership, canonical_digest, run_adapter
        from task_content_baseline import TaskBase
        from test_codex_execute_contract import payload
        actual_run = subprocess.run
        for remote_state in ("exact", "different", "unavailable"):
            with tempfile.TemporaryDirectory() as directory:
                root, bare = Path(directory) / "content", Path(directory) / "remote.git"
                root.mkdir()
                def git(*args, cwd=root):
                    return actual_run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
                git("init", "--quiet");git("config", "user.name", "test");git("config", "user.email", "test@example.com")
                (root / "content.md").write_text("baseline")
                git("add", "content.md");git("commit", "-qm", "baseline")
                base_sha = git("rev-parse", "HEAD")
                git("init", "--quiet", "--bare", str(bare))
                base = TaskBase(TARGET, "main", base_sha, EXECUTOR, "delivery-42")
                effects = GitHubEffects()
                effects._content_checkout = type("Prepared", (), {"base": base, "root": root})()
                effects._publication_checkout = effects._content_checkout
                effects._content_read_token = "read-token"
                pushes, requests = [], []
                def run(command, **kwargs):
                    if command[:2] == ["git", "push"]:
                        pushes.append(command[-1])
                        actual_run([*command[:2], str(bare), command[-1]], **kwargs)
                        if remote_state == "different":
                            git("update-ref", "refs/heads/codex/delivery-42", base_sha, cwd=bare)
                        raise subprocess.TimeoutExpired(command, kwargs["timeout"])
                    return actual_run(command, **kwargs)
                def gh(*args, **kwargs):
                    requests.append(args)
                    self.assertEqual(args, ("api", f"repos/{TARGET}/git/ref/heads/codex/delivery-42"))
                    self.assertGreater(kwargs["timeout_seconds"], 0)
                    if remote_state == "unavailable": raise subprocess.TimeoutExpired("gh", kwargs["timeout_seconds"])
                    return json.dumps({"ref": "refs/heads/codex/delivery-42", "object": {
                        "type": "commit", "sha": git("rev-parse", "refs/heads/codex/delivery-42", cwd=bare)}})
                def model(*args): (root / "content.md").write_text("candidate")
                value = payload()
                with (patch.object(effects, "discover", return_value=Ownership(False, [])),
                      patch.object(effects, "prepare_content"), patch.object(effects, "codex", side_effect=model) as model_call,
                      patch.object(effects, "has_candidate_changes", return_value=True),
                      patch.object(effects, "validate_candidate", return_value=(True, "passed")),
                      patch.object(effects, "_publication_git_environment", return_value=({}, "/nonexistent/helper")),
                      patch.object(effects, "_gh", side_effect=gh),
                      patch("codex_target_adapter.attest_default_branch", return_value=base),
                      patch("codex_target_adapter.subprocess.run", side_effect=run), redirect_stdout(io.StringIO())):
                    result = run_adapter(json.dumps(value), value["concurrency_group"], "trusted", {"trusted"},
                                         effects, prior_result_effect="none").result
                self.assertEqual(result["execution_status"], "ambiguous-rejected")
                self.assertEqual(result["branch_name"], "codex/delivery-42")
                self.assertIsNone(result["pull_request_url"])
                evidence = json.loads(result["failure_message"].split("; evidence=", 1)[1])
                self.assertEqual(evidence["candidate_sha"], pushes[0].split(":")[0])
                self.assertEqual(evidence["payload_sha256"], canonical_digest(value))
                expected = {"exact": "exact-candidate", "different": "different-object", "unavailable": "unverified"}[remote_state]
                self.assertIn("remote=" + expected, result["failure_message"])
                self.assertEqual((len(pushes), len(requests)), (1, 1))
                model_call.assert_called_once()
                self.assertLessEqual(len(result["failure_message"]), 500)

    def test_expired_push_reconciliation_never_starts_another_api_call(self):
        from task_content_baseline import TaskBase
        effects = GitHubEffects()
        effects._candidate_sha, effects._publication_digest = "d" * 40, "e" * 64
        effects._content_checkout = type("Prepared", (), {"base": TaskBase(TARGET, "main", SHA, EXECUTOR, "delivery-42")})()
        with (patch("time.monotonic", return_value=10), patch.object(effects, "_gh") as gh,
              redirect_stdout(io.StringIO())):
            result = effects._reconcile_timed_out_push("codex/delivery-42", "delivery-42", 10)
        gh.assert_not_called()
        self.assertIn("remote=unverified", result.safe_message)
        self.assertIn("d" * 40, result.safe_message)
        self.assertEqual(result.branch, "codex/delivery-42")

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
