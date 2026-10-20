#!/usr/bin/env python3
"""Candidate tests must inspect candidate content inside the real sandbox."""
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import candidate_test_sandbox as sandbox
from codex_target_adapter import AdapterError, GitHubEffects


class SandboxBoundaryTests(unittest.TestCase):
    def test_missing_tests_and_missing_sandbox_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(sandbox.subprocess, "run") as runner:
                self.assertFalse(sandbox.run_candidate_tests(root, 10))
                runner.assert_not_called()
            (root / "scripts").mkdir()
            (root / sandbox.TEST_SCRIPT).write_text("raise SystemExit(0)")
            with patch.object(sandbox.shutil, "which", return_value=None):
                self.assertFalse(sandbox.run_candidate_tests(root, 10))
                self.assertFalse(sandbox.sandbox_ready(10))

    def test_command_excludes_host_state_and_clears_child_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            command = sandbox.sandbox_command(Path(directory))
            self.assertTrue(all(flag in command for flag in ("--unshare-all", "--clearenv", "--new-session", "--cap-drop")))
            self.assertIn("/candidate/scripts/test_codex_execute_contract.py", command[-1])
            self.assertNotIn("--ro-bind / /", " ".join(command))
            for dangerous in ("/proc", str(Path.home()), "/workspace"):
                self.assertFalse(any(command[i] == "--ro-bind" and command[i + 1] == dangerous
                                     for i in range(len(command) - 1)))

    def test_sandbox_unavailable_stops_before_model_authentication(self):
        effects = GitHubEffects()
        effects._content_checkout = type("Prepared", (), {"root": Path("/candidate")})()
        with (patch.object(effects, "_gh", return_value="true"),
              patch.object(effects, "_publication_git_environment", return_value=({}, "/nonexistent/helper")),
              patch("codex_target_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], 0)),
              patch("codex_target_adapter.sandbox_ready", return_value=False),
              patch("codex_target_adapter._take_secret") as secret,
              patch("codex_target_adapter.subprocess.Popen") as model):
            with self.assertRaises(AdapterError) as ctx: effects.codex("do not run", 10)
        self.assertEqual(ctx.exception.category, "dependency")
        secret.assert_not_called()
        model.assert_not_called()

    def test_adapter_does_not_claim_tests_pass_on_sandbox_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            effects = GitHubEffects()
            effects._content_checkout = type("Prepared", (), {"root": root})()
            with (patch("codex_target_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as policy,
                  patch("codex_target_adapter.run_candidate_tests", return_value=False) as tests):
                self.assertEqual(effects.validate_candidate(10), (False, "tests"))
            self.assertEqual(tests.call_args.args[0], root)
            self.assertFalse(any("test_codex_execute_contract.py" in " ".join(c.args[0]) for c in policy.call_args_list))


class RealNamespaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sandbox.sandbox_ready(10):
            if os.environ.get("REQUIRE_CANDIDATE_SANDBOX") == "1":
                raise RuntimeError("CI requires working namespace sandbox; no skip allowed")
            raise unittest.SkipTest("Local host disallows namespace setup; required integration runs in CI")

    def test_broken_candidate_and_deleted_tests_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/app.py").write_text("answer = 42\n")
            test = root / sandbox.TEST_SCRIPT
            test.write_text("from app import answer\nassert answer == 42\n")
            self.assertTrue(sandbox.run_candidate_tests(root, 30))
            (root / "scripts/app.py").write_text("answer = 0\n")
            self.assertFalse(sandbox.run_candidate_tests(root, 30))
            (root / "scripts/app.py").unlink()
            self.assertFalse(sandbox.run_candidate_tests(root, 30))
            test.unlink()
            self.assertFalse(sandbox.run_candidate_tests(root, 30))

    def test_untrusted_test_has_no_host_credentials_network_or_parent_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "candidate"
            (root / "scripts").mkdir(parents=True)
            sentinel = Path(directory) / "outside-secret"
            sentinel.write_text("host sentinel")
            script = root / sandbox.TEST_SCRIPT
            script.write_text(
                "import os,socket,pathlib\n"
                "assert 'GH_TOKEN' not in os.environ\n"
                "assert 'OPENAI_API_KEY' not in os.environ\n"
                f"assert not pathlib.Path({str(sentinel)!r}).exists()\n"
                f"assert not pathlib.Path('/proc/{os.getpid()}/environ').exists()\n"
                "s=socket.socket();s.settimeout(0.1)\n"
                "try: s.connect(('1.1.1.1',443))\n"
                "except OSError: pass\n"
                "else: raise AssertionError('network available')\n"
                "pathlib.Path('snapshot-write').write_text('local only')\n"
            )
            with patch.dict(os.environ, {"GH_TOKEN": "host-only", "OPENAI_API_KEY": "host-only"}):
                self.assertTrue(sandbox.run_candidate_tests(root, 30))
            self.assertFalse((root / "snapshot-write").exists())
            self.assertEqual(sentinel.read_text(), "host sentinel")

    def test_timeout_terminates_untrusted_test(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / sandbox.TEST_SCRIPT).write_text("import time;time.sleep(60)")
            with self.assertRaises(subprocess.TimeoutExpired): sandbox.run_candidate_tests(root, 0.5)


if __name__ == "__main__":
    unittest.main()
