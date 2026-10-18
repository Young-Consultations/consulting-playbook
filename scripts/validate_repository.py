#!/usr/bin/env python3
"""Repository-specific path and secret validation for generated changes."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ALLOWED_ROOTS = {
    ".ai-sdlc",
    ".github",
    "AI_CONTEXT.md",
    "README.md",
    "ai-sdlc",
    "config",
    "conformance",
    "consulting",
    "contracts",
    "docs",
    "playbooks",
    "scripts",
    "templates",
    "tests",
}
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env($|\.)|credentials|secrets?($|\.)|.*\.(pem|key)$)", re.I)
SECRET_VALUE = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})")


def run(*args: str, worktree: Path | None = None) -> str:
    return subprocess.run(args, cwd=worktree, check=True, text=True, capture_output=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Trusted validator of untrusted task content")
    parser.add_argument("--worktree", type=Path, default=Path.cwd())
    args = parser.parse_args()
    worktree = args.worktree.resolve(strict=True)
    if not (worktree / ".git").exists():
        raise SystemExit("candidate validation requires a Git checkout")
    def git(*parts: str) -> str:
        return run("git", *parts, worktree=worktree)
    entries = git("status", "--porcelain=v1", "-z").split("\0")
    files: list[str] = []
    for entry in entries:
        if not entry:
            continue
        name = entry[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        files.append(name)
    for name in files:
        root = Path(name).parts[0]
        if root not in ALLOWED_ROOTS:
            raise SystemExit(f"changed path is outside the repository allowlist: {name}")
        if FORBIDDEN_NAMES.search(name):
            raise SystemExit("a credential-like file name was detected")
    # Scan both working-tree and index changes. Codex may stage a tracked file,
    # in which case the default diff no longer contains its generated content.
    def added_content(diff: str) -> str:
        return "\n".join(
            line[1:] for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )

    content = added_content(git("diff", "--no-ext-diff"))
    content += "\n" + added_content(git("diff", "--cached", "--no-ext-diff"))
    for name in files:
        path = worktree / name
        if path.is_file() and name in git("ls-files", "--others", "--exclude-standard").splitlines():
            content += path.read_text(encoding="utf-8", errors="replace")
    if SECRET_VALUE.search(content):
        raise SystemExit("a credential-like value was detected in generated content")


if __name__ == "__main__":
    main()
