#!/usr/bin/env python3
"""Static regression checks for the disabled next-MVP target boundary."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/codex-execute.yml").read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def test_exact_reusable_workflow_inputs() -> None:
    inputs = section(WORKFLOW, "    inputs:\n", "    secrets:\n")
    assert "execution_input_json:" in inputs
    assert "concurrency_group:" in inputs
    assert inputs.count("        required: true") == 2
    for legacy in ("execution_input:", "execution_input_artifact:", "execution_input_run_id:"):
        assert legacy not in inputs


def test_only_documented_result_secret_is_declared() -> None:
    secrets = section(WORKFLOW, "    secrets:\n", "\nconcurrency:\n")
    assert "CODEX_RESULT_TOKEN:" in secrets
    assert secrets.count("required: true") == 1
    assert "secrets: inherit" not in WORKFLOW


def test_disabled_boundary_is_read_only_and_fail_closed() -> None:
    assert "contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "pull-requests: write" not in WORKFLOW
    assert "registry-disabled:" in WORKFLOW
    assert "exit 1" in WORKFLOW


def test_disabled_boundary_has_no_effect_path() -> None:
    forbidden = (
        "openai/codex-action",
        "git push",
        "gh pr create",
        "gh pr merge",
        "actions/checkout",
        "ai_sdlc_contracts",
        "PORTFOLIO_TASKS_TOKEN",
        "ORG_CONTROL_PLANE_TOKEN",
        "status:approved",
        "execution_input_artifact",
        "execution_input_run_id",
        "ai-sdlc-v2.1.0",
    )
    for value in forbidden:
        assert value not in WORKFLOW


def test_concurrency_is_transport_only() -> None:
    assert "group: ${{ inputs.concurrency_group }}" in WORKFLOW
    assert "not authorization or an idempotency identity" in WORKFLOW


if __name__ == "__main__":
    tests = sorted(
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    for _, test in tests:
        test()
    print(f"passed {len(tests)} target-boundary checks")
