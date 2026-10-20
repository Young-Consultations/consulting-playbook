#!/usr/bin/env python3
"""Execute candidate-owned tests in an isolated, credential-free filesystem.

Only OS/runtime directories and a disposable candidate snapshot are mounted.
No host home, original checkout, runner temporary directory or host /proc is
visible. A missing or unusable namespace sandbox fails closed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import site
import subprocess
import sys
import tempfile
import time

from task_content_checkout import remaining_time

TEST_SCRIPT = "scripts/test_codex_execute_contract.py"


def sandbox_command(snapshot: Path, *, probe: bool = False) -> list[str]:
    command = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session",
               "--cap-drop", "ALL", "--clearenv"]
    mounted = []
    for directory in ("/usr", "/bin", "/lib", "/lib64", str(Path(sys.prefix)), str(Path(sys.base_prefix))):
        path = Path(directory)
        if not path.exists() or any(path == root or path.is_relative_to(root) for root in mounted):
            continue
        # Bind real runtime paths, retaining the conventional symlink aliases.
        if path.is_symlink():
            command += ["--symlink", os.readlink(path), str(path)]
        else:
            command += ["--ro-bind", str(path), str(path)]
            mounted.append(path)
    dependencies = []
    for index, directory in enumerate([*site.getsitepackages(), site.getusersitepackages()]):
        path = Path(directory)
        if not path.is_dir() or any(path == root or path.is_relative_to(root) for root in mounted):
            continue
        destination = f"/test-dependencies/{index}"
        command += ["--ro-bind", str(path), destination]
        dependencies.append(destination)
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--dir", "/tmp/home", "--bind", str(snapshot), "/candidate",
                "--chdir", "/candidate", "--setenv", "HOME", "/tmp/home",
                "--setenv", "PATH", str(Path(sys.executable).parent) + ":/usr/bin:/bin",
                "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
                "--setenv", "GIT_CONFIG_NOSYSTEM", "1", "--setenv", "GIT_CONFIG_GLOBAL", "/dev/null",
                "--setenv", "GIT_TERMINAL_PROMPT", "0"]
    # -I ignores ambient Python paths/user customizations. Only explicitly
    # mounted dependency directories and the candidate script directory follow.
    program = (f"import sys;sys.path[:0]={json.dumps(dependencies)};import jsonschema") if probe else (
        "import sys,runpy;sys.dont_write_bytecode=True;"
        f"sys.path[:0]={json.dumps(['/candidate/scripts', *dependencies])};"
        f"runpy.run_path('/candidate/{TEST_SCRIPT}',run_name='__main__')"
    )
    return [*command, "--", sys.executable, "-I", "-c", program]


def sandbox_ready(timeout_seconds: float) -> bool:
    if shutil.which("bwrap") is None:
        return False
    with tempfile.TemporaryDirectory(prefix="candidate-test-probe-") as directory:
        try:
            return subprocess.run(sandbox_command(Path(directory), probe=True),
                                  env={}, timeout=timeout_seconds,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False


def run_candidate_tests(candidate: Path, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    candidate = candidate.resolve(strict=True)
    script = candidate / TEST_SCRIPT
    # A deleted or redirected test entrypoint cannot report passed tests.
    if not script.is_file() or script.is_symlink() or not script.resolve().is_relative_to(candidate):
        return False
    if shutil.which("bwrap") is None:
        return False
    with tempfile.TemporaryDirectory(prefix="candidate-test-snapshot-") as directory:
        snapshot = Path(directory) / "content"
        try:
            # Copy as data, with symlinks preserved, under the same deadline.
            # Tests may mutate only this disposable snapshot.
            copied = subprocess.run(["cp", "--archive", "--reflink=auto", "--", str(candidate), str(snapshot)],
                                    env={}, timeout=remaining_time(deadline),
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if copied.returncode:
                return False
            completed = subprocess.run(sandbox_command(snapshot), env={},
                                       timeout=remaining_time(deadline),
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            remaining_time(deadline)
            return completed.returncode == 0
        except OSError:
            return False
