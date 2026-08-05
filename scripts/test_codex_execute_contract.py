#!/usr/bin/env python3
"""Regression checks for AI-SDLC target workflow migration."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/codex-execute.yml"
WORKFLOW = WORKFLOW_PATH.read_text(encoding="utf-8")
WRAPPER = (ROOT / ".github/actions/run-codex/action.yml").read_text(encoding="utf-8")
POLICY_PATH = ROOT / "scripts/codex_repository_policy.py"
POLICY = POLICY_PATH.read_text(encoding="utf-8")
SPEC = importlib.util.spec_from_file_location("codex_repository_policy", POLICY_PATH)
policy = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(policy)

PRODUCTION_FILES = [
    path for path in ROOT.rglob("*")
    if path.is_file()
    and ".git" not in path.parts
    and "__pycache__" not in path.parts
    and not path.name.startswith("test_")
]


def check(fragment: str, text: str = WORKFLOW) -> None:
    assert fragment in text, f"missing required fragment: {fragment}"


def sample_payload(**updates):
    payload = {
        "target_repository": "Young-Consultations/consulting-playbook",
        "executor": "codex",
        "source_issue": {
            "repository": "Young-Consultations/portfolio-tasks",
            "number": 42,
            "type": "issue",
            "state": "open",
        },
        "labels": ["status:approved", "executor:codex"],
        "draft_pr_only": True,
        "auto_merge": False,
        "execution_mode": "implement",
        "task_id": "TASK-42",
        "correlation_id": "corr-42",
        "project_component": "documentation",
    }
    payload.update(updates)
    return payload


def run_policy(payload):
    return policy.validate_policy(payload, "Young-Consultations/consulting-playbook")


def test_no_workflow_checks_out_portfolio_tasks_for_shared_schemas() -> None:
    workflows = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / ".github/workflows").glob("*.yml"))
    assert "repository: Young-Consultations/portfolio-tasks" not in workflows
    assert "_execution-contract" not in workflows


def test_no_production_file_declares_v1() -> None:
    offenders = [str(path.relative_to(ROOT)) for path in PRODUCTION_FILES if "ai-sdlc-contract/v1" in path.read_text(encoding="utf-8", errors="replace")]
    assert offenders == []


def test_no_local_production_module_declares_canonical_contract_version() -> None:
    production_python = [path for path in (ROOT / "scripts").glob("*.py") if path.name != "test_codex_execute_contract.py"]
    offenders = [path.name for path in production_python if "CONTRACT_VERSION" in path.read_text(encoding="utf-8")]
    assert offenders == []


def test_workflow_installs_shared_contracts_from_org_github() -> None:
    check("repository: Young-Consultations/.github")
    check("path: shared-platform")
    check("python -m pip install --disable-pip-version-check --no-input ./shared-platform/ai_sdlc_contracts")
    check("python -m ai_sdlc_contracts.execution_input validate")
    check("python -m ai_sdlc_contracts.execution_result validate")


def test_organization_release_is_pinned() -> None:
    check("ref: ai-sdlc-v2.1.0")


def test_workflow_accepts_canonical_router_inputs() -> None:
    for name in ("execution_input_json", "execution_input_artifact", "execution_input_run_id", "concurrency_group"):
        check(f"{name}:")
    assert "execution_input:" not in WORKFLOW


def test_workflow_uses_router_provided_concurrency() -> None:
    check("group: ${{ inputs.concurrency_group }}")


def test_wrong_target_repository_is_rejected() -> None:
    try:
        run_policy(sample_payload(target_repository="Young-Consultations/other"))
        assert False
    except ValueError as error:
        assert "another repository" in str(error)


def test_unsupported_contract_versions_are_rejected_by_org_package() -> None:
    check("--require-version ai-sdlc-contract/v2")
    assert "ai-sdlc-contract/v2" not in POLICY


def test_missing_approval_is_rejected() -> None:
    try:
        run_policy(sample_payload(labels=["executor:codex"], approved=False))
        assert False
    except ValueError as error:
        assert "approval" in str(error)


def test_sensitive_tasks_are_rejected() -> None:
    for update in ({"labels": ["status:approved", "sensitive"]}, {"sensitive": True}):
        try:
            run_policy(sample_payload(**update))
            assert False
        except ValueError as error:
            assert "sensitive" in str(error)


def test_verify_mode_cannot_invoke_codex_or_publish() -> None:
    outputs = run_policy(sample_payload(execution_mode="verify"))
    assert outputs["execution_mode"] == "verify"
    verify_section = WORKFLOW.split("Run verify-mode repository checks", 1)[1].split("Create one task branch", 1)[0]
    assert "run-codex" not in verify_section
    assert "gh pr create" not in verify_section
    assert "git push" not in verify_section
    check("if: steps.policy.outputs.execution_mode == 'implement'")


def test_implement_mode_remains_draft_only() -> None:
    assert run_policy(sample_payload())["execution_mode"] == "implement"
    check("--draft")
    try:
        run_policy(sample_payload(draft_pr_only=False))
        assert False
    except ValueError as error:
        assert "draft-only" in str(error)


def test_no_workflow_uses_secrets_inherit() -> None:
    assert "secrets: inherit" not in WORKFLOW


def test_no_workflow_can_merge_or_push_directly_to_main() -> None:
    forbidden = ("gh pr merge", "--auto", "git push origin main", "git push origin HEAD:main")
    for fragment in forbidden:
        assert fragment not in WORKFLOW
    assert "--base main" in WORKFLOW
    assert "--head \"$BRANCH\"" in WORKFLOW


def test_source_issue_revalidation_and_secret_redaction_preserved() -> None:
    check("Confirm source issue remains approved")
    check('index("status:approved")')
    check('index("sensitivity:sensitive") == null')
    assert "openai-api-key" in WRAPPER
    assert "git status --porcelain" in WRAPPER
    check("credential-like value", (ROOT / "scripts/validate_repository.py").read_text(encoding="utf-8"))


def test_staged_credentials_are_rejected() -> None:
    validator = ROOT / "scripts/validate_repository.py"
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
        readme = repository / "README.md"
        readme.write_text("safe\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "base"], cwd=repository, check=True)
        readme.write_text("ghp_" + "abcdefghijklmnopqrstuvwxyz" + "\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)
        result = subprocess.run([sys.executable, str(validator)], cwd=repository, text=True, capture_output=True)
        assert result.returncode != 0
        assert "credential-like value" in result.stderr


if __name__ == "__main__":
    for name, function in sorted(globals().copy().items()):
        if name.startswith("test_"):
            function()
            print(f"PASS {name}")
