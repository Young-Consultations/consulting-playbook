#!/usr/bin/env python3
"""Read-only, exact-SHA target workbase materialization for approved ADR-013.

No executable code or policy is loaded from the fetched content. The caller
must authenticate the GitHub API independently with a contents:read token
and use a distinct temporary checkout, never the pinned executor root.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import shutil
import stat
from pathlib import Path
from typing import Any, Callable

from task_content_baseline import BaselineError, TaskBase, require_exact_content_checkout


def copy_candidate_data(source: Path, destination: Path, deadline: float) -> None:
    """Copy working-tree bytes only; never inspect or import model Git metadata.

    Source directories/files are opened relative to directory descriptors with
    O_NOFOLLOW. Links, devices, sockets and nested repositories fail closed.
    The destination is a fresh, independently fetched checkout outside the model
    workspace and retains its protected .git directory.
    """
    if source.resolve() == destination.resolve():
        raise BaselineError("candidate and publication workspace must be distinct")
    for entry in destination.iterdir():
        remaining_time(deadline)
        if entry.name == ".git":
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()

    def copy_directory(fd: int, target: Path, top: bool = False) -> None:
        for name in os.listdir(fd):
            remaining_time(deadline)
            if top and name == ".git":
                continue
            if name.casefold() == ".git":
                raise BaselineError("nested repository metadata is not candidate data")
            metadata = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(metadata.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    (target / name).mkdir(mode=0o755)
                    copy_directory(child, target / name)
                finally:
                    os.close(child)
            elif stat.S_ISREG(metadata.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                with os.fdopen(child, "rb") as stream, (target / name).open("xb") as output:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise BaselineError("candidate is not a regular file")
                    while True:
                        remaining_time(deadline)
                        block = stream.read(1024 * 1024)
                        if not block:
                            break
                        output.write(block)
                (target / name).chmod(0o755 if metadata.st_mode & 0o111 else 0o644)
            else:
                raise BaselineError("candidate links and special files are not supported")

    fd = os.open(source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        copy_directory(fd, destination, top=True)
        remaining_time(deadline)
    finally:
        os.close(fd)


def remaining_time(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("content-baseline", 0)
    return remaining


def _git_environment() -> dict[str, str]:
    # Neutralize runner/user git configuration, hooks, and content-side smudge
    # filters before checking out a repository with untrusted .gitattributes.
    env = {k: v for k, v in os.environ.items()
           if k in {"PATH", "HOME", "LANG", "LC_ALL", "CI", "GITHUB_ACTIONS"}}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "core.hooksPath",
        "GIT_CONFIG_VALUE_0": os.devnull,
        "GIT_CONFIG_KEY_1": "core.fsmonitor",
        "GIT_CONFIG_VALUE_1": "false",
    })
    return env


class TrustedContentCheckout:
    """Keeps an isolated content checkout alive until caller explicitly closes."""

    def __init__(self, base: TaskBase, directory: tempfile.TemporaryDirectory[str]):
        self.base = base
        self._directory = directory
        self.root = Path(directory.name) / "content"
        self.root.mkdir(mode=0o700)

    def close(self) -> None:
        self._directory.cleanup()

    def __enter__(self) -> "TrustedContentCheckout":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _read_github_json(
    endpoint: str, *,
    token: str,
    timeout_seconds: float,
    runner: Callable[..., str] = subprocess.check_output,
) -> dict[str, Any]:
    # gh receives credentials through a tightly scoped environment, never
    # through arguments or subprocess output.
    env = _git_environment()
    env["GH_TOKEN"] = token
    raw = runner(["gh", "api", endpoint], text=True, env=env,
                 stderr=subprocess.DEVNULL, timeout=timeout_seconds)
    try:
        value = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise BaselineError("content provenance API returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise BaselineError("content provenance API returned a non-object")
    return value


def attest_default_branch(
    repository: str, delivery_id: str, executor_sha: str, *,
    token: str, timeout_seconds: float,
    read: Callable[..., dict[str, Any]] = _read_github_json,
    deadline: float | None = None,
) -> TaskBase:
    """Resolve an exact branch+commit identity without relying on mutable refs."""
    if not token or timeout_seconds <= 0:
        raise BaselineError("authenticated read-only content provenance is unavailable")
    deadline = min(time.monotonic() + timeout_seconds, deadline) if deadline is not None else time.monotonic() + timeout_seconds
    repository_info = read(
        f"repos/{repository}", token=token, timeout_seconds=remaining_time(deadline)
    )
    if repository_info.get("full_name") != repository:
        raise BaselineError("repository metadata does not bind to target")
    branch_name = repository_info.get("default_branch")
    if not isinstance(branch_name, str) or not branch_name or ".." in branch_name:
        raise BaselineError("unsafe default-branch metadata")
    branch_info = read(
        f"repos/{repository}/branches/{branch_name}",
        token=token, timeout_seconds=remaining_time(deadline),
    )
    remaining_time(deadline)
    return TaskBase.from_github(
        repository=repository, delivery_id=delivery_id,
        executor_sha=executor_sha, repo_response=repository_info,
        branch_response=branch_info,
    )


def checkout_attested_base(
    base: TaskBase, *, token: str, timeout_seconds: float,
    run: Callable[..., subprocess.CompletedProcess[Any]] = subprocess.run,
    deadline: float | None = None,
) -> TrustedContentCheckout:
    """Fetch the authorized default branch and require exact SHA equality.

    The read token is used only by git fetch, never persisted into git config,
    remote URLs, command arguments, or the later model environment.
    """
    if not token or timeout_seconds <= 0:
        raise BaselineError("content read token is unavailable")
    deadline = min(time.monotonic() + timeout_seconds, deadline) if deadline is not None else time.monotonic() + timeout_seconds
    temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(
        prefix="ai-sdlc-task-content-"
    )
    checkout = TrustedContentCheckout(base, temp)
    env = _git_environment()
    def call(*command: str, auth: bool = False) -> str:
        command_env = dict(env)
        if auth:
            # An ephemeral askpass helper is created outside the content root
            # and contains no credential literal.
            command_env.update(
                GIT_ASKPASS=str(Path(temp.name) / "read-askpass.sh"),
                GIT_USERNAME="x-access-token", GIT_PASSWORD=token,
            )
        p = run(list(command), cwd=checkout.root, env=command_env,
                text=True, capture_output=True, timeout=remaining_time(deadline),
                check=False)
        remaining_time(deadline)
        if p.returncode != 0:
            raise BaselineError("authenticated exact content checkout failed")
        return p.stdout.strip()
    try:
        helper = Path(temp.name) / "read-askpass.sh"
        helper.write_text(
            '#!/bin/sh\ncase "$1" in\n'
            '  *Username*) printf "%s\\n" "$GIT_USERNAME" ;;\n'
            '  *Password*) printf "%s\\n" "$GIT_PASSWORD" ;;\n'
            '  *) printf "%s\\n" "" ;;\nesac\n',
            encoding="utf-8",
        )
        helper.chmod(0o700)
        call("git", "init", "--quiet")
        call("git", "-c", "core.hooksPath=/dev/null", "fetch",
             "--no-tags", "--depth=1",
             f"https://github.com/{base.repository}.git",
             f"refs/heads/{base.default_branch}", auth=True)
        # The branch might have moved during fetch; do not silently take a
        # newer or older version than the attested exact GitHub API commit.
        fetched = call("git", "rev-parse", "--verify", "FETCH_HEAD")
        if fetched != base.content_sha:
            raise BaselineError("default branch moved during content checkout")
        call("git", "-c", "core.hooksPath=/dev/null",
             "checkout", "--detach", "--force", base.content_sha)
        observed = call("git", "rev-parse", "--verify", "HEAD")
        dirty = bool(call("git", "status", "--porcelain=v1", "-z"))
        require_exact_content_checkout(base, observed, dirty)
        return checkout
    except Exception:
        checkout.close()
        raise
    finally:
        try:
            (Path(temp.name) / "read-askpass.sh").unlink(missing_ok=True)
        except OSError:
            pass
