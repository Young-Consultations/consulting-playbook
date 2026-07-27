#!/usr/bin/env python3
"""Thin adapter around the organization-owned execution schemas."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import jsonschema


CONTRACT_VERSION = "ai-sdlc-contract/v1"


def load_json(value: str) -> dict[str, Any]:
    result = json.loads(value)
    if not isinstance(result, dict):
        raise ValueError("contract payload must be a JSON object")
    return result


def validate(schema_path: str, instance: dict[str, Any]) -> None:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
    except jsonschema.ValidationError as error:
        raise ValueError("payload does not satisfy the canonical schema") from error


def source_parts(value: Any) -> tuple[str, int, str]:
    if isinstance(value, str):
        match = re.fullmatch(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)", value)
        if not match:
            raise ValueError("source_issue must be owner/repository#number")
        return match.group(1), int(match.group(2)), value
    if isinstance(value, dict):
        repository, number = value.get("repository"), value.get("number")
        if not isinstance(repository, str) or not isinstance(number, int) or number < 1:
            raise ValueError("source_issue is malformed")
        return repository, number, f"{repository}#{number}"
    raise ValueError("source_issue is malformed")


def output(name: str, value: Any, destination: str) -> None:
    with Path(destination).open("a", encoding="utf-8") as stream:
        stream.write(f"{name}={value}\n")


def validate_input(args: argparse.Namespace) -> None:
    payload = load_json(args.json)
    validate(args.schema, payload)
    if payload.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unsupported contract version")
    if payload.get("target_repository") != args.expected_repository:
        raise ValueError("execution targets another repository")
    if payload.get("executor") != "codex":
        raise ValueError("executor is not codex")
    if payload.get("draft_pr_only") is not True:
        raise ValueError("only draft pull requests are permitted")
    repository, number, display = source_parts(payload.get("source_issue"))
    component = str(payload.get("project_component", "task"))
    slug = re.sub(r"[^a-z0-9-]+", "-", component.lower()).strip("-") or "task"
    run_id = re.sub(r"[^0-9]", "", os.environ.get("GITHUB_RUN_ID", "0")) or "0"
    for key, value in {
        "source_repository": repository,
        "source_issue_number": number,
        "source_issue": display,
        "project_component": component,
        "branch": f"consulting-codex/{slug}-{number}-{run_id}",
    }.items():
        output(key, value, args.github_output)


def build_result(args: argparse.Namespace) -> None:
    request = load_json(args.input)
    # Field names and values below are those of the shared result contract; this
    # adapter never introduces repository-specific statuses or classifications.
    result: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "source_issue": request.get("source_issue"),
        "target_repository": request.get("target_repository"),
        "executor": request.get("executor"),
        "status": args.status,
        "run_url": args.run_url,
    }
    if args.branch:
        result["branch"] = args.branch
    if args.pull_request_url:
        result["pull_request_url"] = args.pull_request_url
    if args.failure_category:
        result["failure_category"] = args.failure_category
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("validate-input")
    command.add_argument("--schema", required=True)
    command.add_argument("--json", required=True)
    command.add_argument("--expected-repository", required=True)
    command.add_argument("--github-output", required=True)
    command.set_defaults(function=validate_input)
    command = commands.add_parser("validate-result")
    command.add_argument("--schema", required=True)
    command.add_argument("--file", required=True)
    command.set_defaults(function=lambda a: validate(a.schema, load_json(Path(a.file).read_text())))
    command = commands.add_parser("build-result")
    command.add_argument("--input", required=True)
    command.add_argument("--out", required=True)
    command.add_argument("--status", required=True)
    command.add_argument("--branch")
    command.add_argument("--pull-request-url")
    command.add_argument("--failure-category")
    command.add_argument("--run-url", required=True)
    command.set_defaults(function=build_result)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
