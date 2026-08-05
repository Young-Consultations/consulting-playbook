#!/usr/bin/env python3
"""Repository-specific policy adapter for canonical AI-SDLC execution input.

The organization-owned ai_sdlc_contracts package validates canonical schemas,
contract versions, normalization, correlation behavior, and result contracts.
This module only consumes already validated execution input and applies the
consulting-playbook authorization policy.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

EXPECTED_EXECUTOR = "codex"
ALLOWED_MODES = {"verify", "implement"}
SENSITIVE_LABELS = {"sensitive", "sensitivity:sensitive"}
APPROVAL_LABEL = "status:approved"
DRAFT_ONLY_KEYS = ("draft_pr_only", "draft_only")
NO_AUTO_MERGE_KEYS = ("auto_merge", "automatic_merge", "merge_automatically")


def load_payload(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("execution input must be a JSON object")
    return payload


def field(payload: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload[name]
    return default


def issue_parts(value: Any) -> tuple[str, int, str]:
    if isinstance(value, str):
        match = re.fullmatch(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)", value)
        if not match:
            raise ValueError("source issue must identify an open GitHub issue")
        return match.group(1), int(match.group(2)), value
    if isinstance(value, dict):
        repository = value.get("repository") or value.get("repo")
        number = value.get("number") or value.get("issue_number")
        kind = value.get("type") or value.get("kind") or "issue"
        state = value.get("state")
        if not isinstance(repository, str) or not isinstance(number, int) or number < 1:
            raise ValueError("source issue must identify an open GitHub issue")
        if str(kind).lower() not in {"issue", "github_issue"}:
            raise ValueError("source must be a GitHub issue")
        if state is not None and str(state).lower() != "open":
            raise ValueError("source issue must be open")
        return repository, number, f"{repository}#{number}"
    raise ValueError("source issue must identify an open GitHub issue")


def labels_from(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    labels: set[str] = set()
    for item in value:
        if isinstance(item, str):
            labels.add(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            labels.add(item["name"])
    return labels


def bool_field(payload: dict[str, Any], keys: tuple[str, ...], default: bool | None = None) -> bool | None:
    value = field(payload, *keys, default=default)
    if isinstance(value, bool) or value is None:
        return value
    raise ValueError("boolean publication policy is malformed")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "task"


def write_output(path: str | None, values: dict[str, Any]) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def validate_policy(payload: dict[str, Any], expected_repository: str) -> dict[str, Any]:
    if field(payload, "target_repository", "repository") != expected_repository:
        raise ValueError("execution targets another repository")
    if str(field(payload, "executor", default="")).lower() != EXPECTED_EXECUTOR:
        raise ValueError("executor is not Codex")

    source_repository, source_number, source_display = issue_parts(field(payload, "source_issue", "source"))
    labels = labels_from(field(payload, "labels", "source_labels", default=[]))
    if APPROVAL_LABEL not in labels and field(payload, "approved", "explicitly_approved") is not True:
        raise ValueError("source issue is missing explicit approval")
    if labels & SENSITIVE_LABELS or field(payload, "sensitive", "contains_sensitive_data", default=False) is True:
        raise ValueError("source issue is marked sensitive")

    if bool_field(payload, DRAFT_ONLY_KEYS, default=True) is not True:
        raise ValueError("publication must remain draft-only")
    if bool_field(payload, NO_AUTO_MERGE_KEYS, default=False) is not False:
        raise ValueError("automatic merge is not permitted")
    if field(payload, "base_branch", "target_branch", default="main") != "main":
        raise ValueError("target branch must be main")

    mode = str(field(payload, "execution_mode", "mode", default="implement")).lower()
    if mode not in ALLOWED_MODES:
        raise ValueError("unsupported execution mode")

    task_id = str(field(payload, "task_id", "id", default=f"issue-{source_number}"))
    correlation_id = str(field(payload, "correlation_id", default=task_id))
    component = str(field(payload, "project_component", "component", "title", default="task"))
    run_id = re.sub(r"[^0-9]", "", os.environ.get("GITHUB_RUN_ID", "0")) or "0"
    branch = f"consulting-codex/{slugify(task_id)}-{source_number}-{run_id}"

    return {
        "source_repository": source_repository,
        "source_issue_number": source_number,
        "source_issue": source_display,
        "project_component": component,
        "execution_mode": mode,
        "task_id": task_id,
        "correlation_id": correlation_id,
        "branch": branch,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    command = subcommands.add_parser("validate")
    command.add_argument("--input", required=True)
    command.add_argument("--expected-repository", required=True)
    command.add_argument("--github-output")
    command.add_argument("--env-output")
    args = parser.parse_args()
    outputs = validate_policy(load_payload(args.input), args.expected_repository)
    write_output(args.github_output, outputs)
    write_output(args.env_output, outputs)


if __name__ == "__main__":
    main()
