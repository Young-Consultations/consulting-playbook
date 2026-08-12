#!/usr/bin/env python3
"""Repository-specific policy adapter for canonical AI-SDLC execution input.

The organization-owned immutable schemas validate the canonical contract.
This module consumes an already schema-validated request and applies only the
consulting-playbook target policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_EXECUTOR = "codex"
ALLOWED_MODES = {"verify", "implement"}
ALLOWED_TASK_TYPES = {"automation", "documentation", "feature", "testing"}
BRANCH_PREFIX = "consulting-codex/"


def load_payload(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("execution input must be a JSON object")
    return payload


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "task"


def delivery_branch(delivery_id: str) -> str:
    """Return a readable, collision-resistant branch for a logical delivery."""
    digest = hashlib.sha256(delivery_id.encode("utf-8")).hexdigest()[:16]
    return f"{BRANCH_PREFIX}{slugify(delivery_id)[:40]}-{digest}"


def validate_requested_branch(requested: Any, delivery_id: str) -> str:
    expected = delivery_branch(delivery_id)
    if requested is None:
        return expected
    if not isinstance(requested, str) or requested != expected:
        raise ValueError("requested branch does not belong to the canonical delivery ID")
    if not requested.startswith(BRANCH_PREFIX) or not re.fullmatch(r"[a-z0-9][a-z0-9./-]{1,254}", requested):
        raise ValueError("requested branch is unsafe or has the wrong target prefix")
    return requested


def write_output(path: str | None, values: dict[str, Any]) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def required_string(payload: dict[str, Any], name: str, *, maximum: int = 256) -> str:
    value = payload.get(name)
    if (not isinstance(value, str) or not value or len(value) > maximum
            or any(ord(character) < 32 for character in value)):
        raise ValueError(f"{name} is required")
    return value


def validate_policy(payload: dict[str, Any], expected_repository: str) -> dict[str, Any]:
    """Apply target-local defense in depth without re-enforcing router activation."""
    if payload.get("contract_version") != "ai-sdlc-contract/v2":
        raise ValueError("unsupported contract version")
    if payload.get("target_repository") != expected_repository:
        raise ValueError("execution targets another repository")
    if payload.get("executor") != EXPECTED_EXECUTOR:
        raise ValueError("executor is not Codex")
    mode = payload.get("execution_mode")
    if mode not in ALLOWED_MODES:
        raise ValueError("unsupported execution mode")
    if payload.get("task_type") not in ALLOWED_TASK_TYPES:
        raise ValueError("unsupported task type")
    if payload.get("draft_pr_only") is not True:
        raise ValueError("publication must remain draft-only")

    delivery_id = required_string(payload, "delivery_id")
    correlation_id = required_string(payload, "correlation_id")
    source_issue = required_string(payload, "source_issue", maximum=512)
    task_id = required_string(payload, "task_id")
    branch = validate_requested_branch(payload.get("requested_branch"), delivery_id)
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return {
        "source_issue": source_issue,
        "project_component": required_string(payload, "project_component", maximum=200),
        "execution_mode": mode,
        "task_id": task_id,
        "correlation_id": correlation_id,
        "delivery_id": delivery_id,
        "payload_digest": digest,
        "target_repository": expected_repository,
        "contract_version": payload["contract_version"],
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
