#!/usr/bin/env python3
"""Deterministic repository policy regressions using isolated Git repositories."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VALIDATOR = Path(__file__).resolve().with_name("validate_repository.py")


class RepositoryPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Policy regression")
        self.git("config", "user.email", "policy@example.invalid")
        self.write("consulting/fixture.md", "Existing governed content.\n")
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Fixture baseline")

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=self.root, env=self.env,
            check=True, capture_output=True, text=True,
        )

    def write(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def validate(self, expected: str | None = None) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)], cwd=self.root, env=self.env,
            capture_output=True, text=True,
        )
        if expected is None:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)

    def test_generated_consulting_changes_are_accepted(self) -> None:
        self.write("consulting/fixture.md", "Generated governed modification.\n")
        self.validate()
        self.git("add", "consulting/fixture.md")
        self.validate()
        self.write("consulting/generated.md", "Generated governed addition.\n")
        self.validate()
        self.git("add", "consulting/generated.md")
        self.validate()

    def test_unauthorized_top_level_changes_are_rejected(self) -> None:
        self.write("unauthorized/generated.md", "Generated unauthorized content.\n")
        self.validate("changed path is outside the repository allowlist:")
        self.git("add", "unauthorized/generated.md")
        self.validate("changed path is outside the repository allowlist:")

    def test_credential_file_names_are_rejected(self) -> None:
        for name in (".env", ".env.local", "credentials.json", "secret", "secrets.json", "private.pem", "private.key"):
            with self.subTest(name=name):
                relative = f"consulting/{name}"
                self.write(relative, "Synthetic fixture.\n")
                self.validate("a credential-like file name was detected")
                self.git("add", relative)
                self.validate("a credential-like file name was detected")
                self.git("reset", "--quiet", "HEAD", "--", relative)
                (self.root / relative).unlink()

    def test_generated_credential_values_are_rejected(self) -> None:
        for prefix in ("sk-", "ghp_", "gho_", "ghu_", "ghs_", "ghr_"):
            for state in ("unstaged", "staged", "untracked"):
                with self.subTest(prefix=prefix, state=state):
                    relative = "consulting/generated.md" if state == "untracked" else "consulting/fixture.md"
                    self.write(relative, prefix + "x" * 24 + "\n")
                    if state == "staged":
                        self.git("add", relative)
                        # Ensure the cached diff is scanned independently of the working tree.
                        self.write(relative, "Safe working tree content.\n")
                    self.validate("a credential-like value was detected")
                    self.git("reset", "--quiet", "HEAD", "--", relative)
                    if state == "untracked":
                        (self.root / relative).unlink()
                    else:
                        self.git("checkout", "--", relative)


if __name__ == "__main__":
    unittest.main()
