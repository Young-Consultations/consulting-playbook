#!/usr/bin/env python3
"""Real Git isolation and API-backed ownership regressions; no external effects."""
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from codex_target_adapter import GitHubEffects, canonical_digest, run_adapter, TARGET
from task_content_baseline import BaselineError, TaskBase
from task_content_checkout import TrustedContentCheckout, _git_environment, copy_candidate_data
from test_codex_execute_contract import payload


class PublicationIsolationTests(unittest.TestCase):
    def test_publication_hook_rejects_even_fastforward_updates_to_existing_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, remote = root / "source", root / "remote.git"
            source.mkdir()
            def git(*args, cwd=source):
                return subprocess.run(["git", *args], cwd=cwd, env=_git_environment(),
                                      capture_output=True, text=True, check=True).stdout.strip()
            git("init", "--quiet"); git("config", "user.name", "test"); git("config", "user.email", "test@example.com")
            (source / "content").write_text("base")
            git("add", "content"); git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            git("init", "--quiet", "--bare", str(remote))
            git("push", str(remote), "HEAD:refs/heads/codex/collision")
            (source / "content").write_text("candidate")
            git("commit", "-qam", "candidate")
            candidate = git("rev-parse", "HEAD")
            effects = GitHubEffects()
            effects._publication_token = "test-only-token"
            env, helper = effects._publication_git_environment()
            try:
                env["AI_SDLC_EXPECTED_REF"] = "refs/heads/codex/collision"
                rejected = subprocess.run(["git", "push", str(remote), candidate + ":refs/heads/codex/collision"],
                                          cwd=source, env=env, capture_output=True)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(git("rev-parse", "refs/heads/codex/collision", cwd=remote), base)
                env["AI_SDLC_EXPECTED_REF"] = "refs/heads/codex/new-owned"
                created = subprocess.run(["git", "push", str(remote), candidate + ":refs/heads/codex/new-owned"],
                                         cwd=source, env=env, capture_output=True)
                self.assertEqual(created.returncode, 0, created.stderr)
                self.assertEqual(git("rev-parse", "refs/heads/codex/new-owned", cwd=remote), candidate)
            finally:
                Path(helper).unlink(missing_ok=True)

    def test_model_git_configuration_hooks_filters_and_url_rewrites_never_run(self):
        actual_run = subprocess.run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, base_repo, remote = root / "model", root / "base.git", root / "published.git"
            source.mkdir()
            def git(*args, cwd=source):
                return actual_run(["git", *args], cwd=cwd, env=_git_environment(),
                                  capture_output=True, text=True, check=True).stdout.strip()
            git("init", "--quiet")
            git("config", "user.name", "test")
            git("config", "user.email", "test@example.com")
            (source / "docs").mkdir()
            (source / "docs/change.md").write_text("baseline")
            git("add", "docs/change.md")
            git("commit", "-qm", "baseline")
            base_sha = git("rev-parse", "HEAD")
            git("clone", "--quiet", "--bare", str(source), str(base_repo))
            git("init", "--quiet", "--bare", str(remote))
            sentinel = root / "must-not-exist"
            attack = f"touch {sentinel}"
            # Install mutations only after test fixture setup. No privileged
            # Git command is permitted to run in source after this point.
            with (source / ".git/config").open("a") as stream:
                stream.write(f'\n[core]\n fsmonitor = "{attack}"\n'
                             f'[filter "evil"]\n clean = "{attack}"\n required = true\n'
                             f'[url "file:///untrusted"]\n insteadOf = https://github.com/\n')
            for hook in ("pre-commit", "pre-push", "post-checkout"):
                path = source / ".git/hooks" / hook
                path.write_text("#!/bin/sh\n" + attack + "\n")
                path.chmod(0o755)
            (source / ".git/info/attributes").write_text("* filter=evil\n")
            (source / "docs/.gitattributes").write_text("* filter=evil\n")
            (source / "docs/change.md").write_text("candidate")
            base = TaskBase(TARGET, "main", base_sha, "c" * 40, "delivery-42")
            effects = GitHubEffects()
            effects._content_checkout = type("Model", (), {"root": source, "base": base})()
            effects._content_read_token = "read-only-test-token"
            def fresh_checkout(*args, **kwargs):
                checkout = TrustedContentCheckout(base, tempfile.TemporaryDirectory(prefix="trusted-publisher-test-"))
                git("clone", "--quiet", str(base_repo), str(checkout.root))
                return checkout
            pushes = []
            def run(command, **kwargs):
                if command[0] == "git":
                    self.assertNotEqual(Path(kwargs.get("cwd", ".")), source)
                if command[:2] == ["git", "push"]:
                    self.assertEqual(command[2], f"https://github.com/{TARGET}.git")
                    pushes.append(command[-1])
                    command = [*command[:2], str(remote), command[-1]]
                return actual_run(command, **kwargs)
            try:
                with (patch("codex_target_adapter.checkout_attested_base", side_effect=fresh_checkout),
                      patch("codex_target_adapter.subprocess.run", side_effect=run),
                      patch("codex_target_adapter.run_candidate_tests", return_value=True),
                      patch("codex_target_adapter.attest_default_branch", return_value=base),
                      patch.object(effects, "_publication_git_environment", return_value=(_git_environment(), "/nonexistent/helper")),
                      patch.object(effects, "_gh", return_value=f"https://github.com/{TARGET}/pull/7"),
                      redirect_stdout(io.StringIO())):
                    self.assertTrue(effects.has_candidate_changes(30))
                    self.assertEqual(effects.validate_candidate(30), (True, "passed"))
                    effects.publish("codex/delivery-42", "delivery-42", "a" * 64, 30)
                self.assertFalse(sentinel.exists())
                self.assertNotEqual(effects._publication_checkout.root, source)
                self.assertNotIn("evil", (effects._publication_checkout.root / ".git/config").read_text())
                self.assertEqual(len(pushes), 1)
                commit = pushes[0].split(":")[0]
                self.assertEqual(git("rev-parse", commit + "^", cwd=remote), base_sha)
                self.assertEqual(git("show", commit + ":docs/change.md", cwd=remote), "candidate")
            finally:
                if effects._publication_checkout is not None:
                    effects._publication_checkout.close()

    def test_links_and_nested_metadata_cannot_enter_the_trusted_checkout(self):
        for kind in ("link", "nested-git"):
            with tempfile.TemporaryDirectory() as directory:
                source, destination = Path(directory) / "model", Path(directory) / "publisher"
                source.mkdir(); destination.mkdir()
                (destination / ".git").mkdir()
                (source / "docs").mkdir()
                if kind == "link":
                    (source / "docs/external").symlink_to("/etc/passwd")
                else:
                    (source / "docs/.git").mkdir()
                with self.assertRaises(BaselineError):
                    copy_candidate_data(source, destination, time.monotonic() + 10)
                self.assertTrue((destination / ".git").is_dir())


class DraftOwnershipTests(unittest.TestCase):
    def test_actual_discovery_rejects_changed_or_incomplete_bindings_before_model(self):
        for defect in (None, "ref", "head", "parent", "digest", "fork", "base", "unreadable", "orphan"):
            value = payload()
            digest = canonical_digest(value)
            executor, base, candidate = "c" * 40, "a" * 40, "f" * 40
            branch = "codex/delivery-42"
            body = (f"<!-- ai-sdlc-delivery-id: delivery-42; payload-sha256: {digest} -->\n"
                    f"<!-- ai-sdlc-provenance: executor-sha: {executor}; content-base-sha: {base}; candidate-sha: {candidate} -->")
            pr = {"url": f"https://github.com/{TARGET}/pull/7", "body": body, "isDraft": True,
                  "state": "OPEN", "headRefOid": candidate, "headRefName": branch,
                  "headRepository": {"nameWithOwner": TARGET}, "baseRefName": "main"}
            if defect == "head": pr["headRefOid"] = "b" * 40
            if defect == "fork": pr["headRepository"] = {"nameWithOwner": "OtherOwner/foreign"}
            if defect == "base": pr["baseRefName"] = "unreviewed-base"
            effects = GitHubEffects()
            def gh(*args, **kwargs):
                self.assertGreater(kwargs["timeout_seconds"], 0)
                if args[:2] == ("api", "--paginate"): return branch
                if args[:2] == ("pr", "list"): return json.dumps([] if defect == "orphan" else [pr])
                if args[:2] == ("api", f"repos/{TARGET}/git/ref/heads/{branch}"):
                    if defect == "unreadable": raise subprocess.TimeoutExpired("gh", 1)
                    return json.dumps({"ref": "refs/heads/" + branch, "object": {"type": "commit", "sha": "b" * 40 if defect == "ref" else candidate}})
                if args[:2] == ("api", f"repos/{TARGET}/commits/{candidate}"):
                    return json.dumps({"sha": candidate, "parents": [{"sha": "b" * 40 if defect == "parent" else base}],
                                       "commit": {"message": effects._commit_message("delivery-42", "0" * 64 if defect == "digest" else digest, executor, base)}})
                if args[:2] == ("api", f"repos/{TARGET}"): return "main"
                raise AssertionError(args)
            with (patch.object(effects, "_gh", side_effect=gh), patch.object(effects, "codex") as model):
                result = run_adapter(json.dumps(value), value["concurrency_group"], "trusted", {"trusted"}, effects,
                                     prior_result_effect="none").result
            self.assertEqual(result["execution_status"], "duplicate-reused" if defect is None else "ambiguous-rejected", defect)
            model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
