#!/usr/bin/env python3
"""Repository-specific path and secret validation for generated changes."""
from __future__ import annotations

import argparse
from collections import Counter
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


def run(*args: str, worktree: Path | None = None, encoding: str = "utf-8") -> str:
    return subprocess.run(args, cwd=worktree, check=True, encoding=encoding, errors="strict", capture_output=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Trusted validator of untrusted task content")
    parser.add_argument("--worktree", type=Path, default=Path.cwd())
    args = parser.parse_args()
    worktree = args.worktree.resolve(strict=True)
    if not (worktree / ".git").exists():
        raise SystemExit("candidate validation requires a Git checkout")
    def git(*parts: str) -> str:
        # Paths must decode exactly. Blob/diff bytes use a reversible mapping
        # so every ASCII credential marker survives arbitrary binary content.
        binary = parts[0] == "cat-file" or (parts[0] == "diff" and "--name-only" not in parts)
        return run("git", *parts, worktree=worktree, encoding="latin-1" if binary else "utf-8")
    try:
        entries = iter(git("status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"))
    except UnicodeDecodeError:
        raise SystemExit("candidate path names must be UTF-8")
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
        if SECRET_VALUE.search(name):
            raise SystemExit("a credential-like value was detected in a candidate path")
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
    baseline_values: dict[str, Counter[str]] = {}
    def new_occurrence(values: Counter[str], name: str) -> bool:
        if not values:
            return False
        if name not in baseline_values:
            try:
                baseline_values[name] = Counter(SECRET_VALUE.findall(git("cat-file", "blob", "HEAD:" + name)))
            except subprocess.CalledProcessError:
                baseline_values[name] = Counter()
        return any(count > baseline_values[name][value] for value, count in values.items())

    for name in git("diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z").split("\0"):
        if name and new_occurrence(Counter(SECRET_VALUE.findall(git("cat-file", "blob", ":0:" + name))), name):
            raise SystemExit("a credential-like value was detected in generated content")
    for name in files:
        path = worktree / name
        if path.is_symlink():
            raise SystemExit("candidate links are not supported")
        if path.is_file():
            if not path.resolve().is_relative_to(worktree):
                raise SystemExit("candidate path escapes the worktree")
            # Inspect final file bytes as well as staged/unstaged diffs. Git
            # emits no added lines for binary files. Count complete tokens
            # once; retain an unfinished token or short prefix between chunks.
            pending = ""
            values: Counter[str] = Counter()
            with path.open("rb") as stream:
                while block := stream.read(65536):
                    text = pending + block.decode("latin-1")
                    matches = list(SECRET_VALUE.finditer(text))
                    unfinished = matches[-1] if matches and matches[-1].end() == len(text) else None
                    complete = matches[:-1] if unfinished else matches
                    values.update(match.group() for match in complete)
                    if new_occurrence(values, name):
                        raise SystemExit("a credential-like value was detected in generated content")
                    start = unfinished.start() if unfinished else max(
                        complete[-1].end() if complete else 0, len(text) - 32, 0)
                    pending = text[start:]
            values.update(SECRET_VALUE.findall(pending))
            if new_occurrence(values, name):
                raise SystemExit("a credential-like value was detected in generated content")


if __name__ == "__main__":
    main()
