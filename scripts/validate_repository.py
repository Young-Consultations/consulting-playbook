#!/usr/bin/env python3
"""Repository-specific path and secret validation for generated changes."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path


ALLOWED_ROOTS = {"README.md", "docs", "playbooks", "templates", "scripts", ".github"}
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env($|\.)|credentials|secrets?($|\.)|.*\.(pem|key)$)", re.I)
SECRET_VALUE = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})")


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def main() -> None:
    entries = run("git", "status", "--porcelain=v1", "-z").split("\0")
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
    # Include untracked files in the content scan without staging their contents.
    content = run("git", "diff", "--no-ext-diff")
    for name in files:
        path = Path(name)
        if path.is_file() and name in run("git", "ls-files", "--others", "--exclude-standard").splitlines():
            content += path.read_text(encoding="utf-8", errors="replace")
    if SECRET_VALUE.search(content):
        raise SystemExit("a credential-like value was detected in generated content")


if __name__ == "__main__":
    main()
