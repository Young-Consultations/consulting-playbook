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
    return subprocess.run(args, cwd=worktree, check=True, text=True, errors="replace", capture_output=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Trusted validator of untrusted task content")
    parser.add_argument("--worktree", type=Path, default=Path.cwd())
    args = parser.parse_args()
    worktree = args.worktree.resolve(strict=True)
    if not (worktree / ".git").exists():
        raise SystemExit("candidate validation requires a Git checkout")
    def git(*parts: str) -> str:
        return run("git", *parts, worktree=worktree)
    entries = iter(git("status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"))
    files: list[str] = []
    for entry in entries:
        if not entry:
            continue
        name = entry[3:]
        files.append(name)
        if "R" in entry[:2] or "C" in entry[:2]:
            original = next(entries, "")
            if original:
                files.append(original)
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

    content = added_content(git("diff", "--no-ext-diff", "--no-textconv"))
    content += "\n" + added_content(git("diff", "--cached", "--no-ext-diff", "--no-textconv"))
    if SECRET_VALUE.search(content):
        raise SystemExit("a credential-like value was detected in generated content")
    baseline_values: dict[str, set[str]] = {}
    def new_value(text: str, name: str, partial: bool = False) -> bool:
        matches = list(SECRET_VALUE.finditer(text))
        if not matches:
            return False
        if name not in baseline_values:
            try:
                baseline_values[name] = set(SECRET_VALUE.findall(git("cat-file", "blob", "HEAD:" + name)))
            except subprocess.CalledProcessError:
                baseline_values[name] = set()
        for match in matches:
            value = match.group()
            if value in baseline_values[name]:
                continue
            if partial and match.end() == len(text) and any(
                    baseline.startswith(value) for baseline in baseline_values[name]):
                continue
            return True
        return False

    for name in git("diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z").split("\0"):
        if name and new_value(git("cat-file", "blob", ":0:" + name), name):
            raise SystemExit("a credential-like value was detected in generated content")
    for name in files:
        path = worktree / name
        if path.is_symlink():
            raise SystemExit("candidate links are not supported")
        if path.is_file():
            if not path.resolve().is_relative_to(worktree):
                raise SystemExit("candidate path escapes the worktree")
            # Inspect final file bytes as well as staged/unstaged diffs. Git
            # emits no added lines for binary files. Bound memory use and keep
            # overlap so markers split across chunks are still detected.
            overlap = ""
            with path.open("rb") as stream:
                while block := stream.read(65536):
                    text = overlap + block.decode("utf-8", errors="replace")
                    if new_value(text, name, partial=True):
                        raise SystemExit("a credential-like value was detected in generated content")
                    width = max([128, *(len(value) + 1 for value in baseline_values.get(name, set()))])
                    overlap = text[-width:]
            if new_value(overlap, name):
                raise SystemExit("a credential-like value was detected in generated content")


if __name__ == "__main__":
    main()
