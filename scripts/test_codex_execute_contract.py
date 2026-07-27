#!/usr/bin/env python3
"""Regression checks for the execution workflow and its policy adapter."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/codex-execute.yml").read_text()
WRAPPER = (ROOT / ".github/actions/run-codex/action.yml").read_text()
ADAPTER = (ROOT / "scripts/execution_contract.py").read_text()
if "jsonschema" not in sys.modules:
    fake_jsonschema = types.ModuleType("jsonschema")
    fake_jsonschema.ValidationError = type("ValidationError", (Exception,), {})
    fake_jsonschema.Draft202012Validator = lambda _schema: types.SimpleNamespace(validate=lambda _value: None)
    sys.modules["jsonschema"] = fake_jsonschema
SPEC = importlib.util.spec_from_file_location("execution_contract", ROOT / "scripts/execution_contract.py")
contract = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(contract)


def check(fragment: str, text: str = WORKFLOW) -> None:
    assert fragment in text, f"missing required fragment: {fragment}"


def test_canonical_input_acceptance() -> None:
    check("execution_input:")
    check("validate-input")


def test_contract_policy_rejections() -> None:
    for fragment in ("unsupported contract version", "execution targets another repository", "executor is not codex", "only draft pull requests"):
        check(fragment, ADAPTER)


def policy_payload(**updates):
    payload = {
        "contract_version": "ai-sdlc-contract/v1",
        "source_issue": "Young-Consultations/portfolio-tasks#42",
        "target_repository": "Young-Consultations/consulting-playbook",
        "executor": "codex",
        "draft_pr_only": True,
        "project_component": "documentation",
    }
    payload.update(updates)
    return payload


def run_policy(payload):
    with tempfile.TemporaryDirectory() as directory:
        schema = Path(directory) / "schema.json"
        destination = Path(directory) / "output"
        # Policy tests isolate repository enforcement from the separately owned schema.
        schema.write_text('{"type":"object"}')
        args = type("Args", (), {
            "json": json.dumps(payload), "schema": str(schema),
            "expected_repository": "Young-Consultations/consulting-playbook",
            "github_output": str(destination),
        })()
        contract.validate_input(args)
        return destination.read_text()


def test_canonical_policy_acceptance() -> None:
    assert "source_issue_number=42" in run_policy(policy_payload())


def test_wrong_repository_rejection() -> None:
    try:
        run_policy(policy_payload(target_repository="Young-Consultations/other"))
        assert False
    except ValueError as error:
        assert "another repository" in str(error)


def test_version_executor_and_draft_rejections() -> None:
    for update in ({"contract_version": "v2"}, {"executor": "other"}, {"draft_pr_only": False}):
        try:
            run_policy(policy_payload(**update))
            assert False
        except ValueError:
            pass


def test_approval_rechecked() -> None:
    check('index("status:approved")')


def test_noop_retried_once() -> None:
    check("Retry Codex once", WRAPPER)
    assert WRAPPER.count("Retry Codex once") == 1
    check("git status --porcelain", WRAPPER)


def test_validation_and_test_fail_closed() -> None:
    check("python scripts/validate_repository.py")
    check("python scripts/test_codex_execute_contract.py")
    assert "continue-on-error" not in WORKFLOW


def test_draft_pr_and_result_reporting() -> None:
    check("--draft")
    check("Validate canonical result")
    check("Upload canonical execution result")
    check("Post result to source issue")


def test_result_schema_survives_contract_checkout_removal() -> None:
    check('cp "$result_schema" "$preserved_result_schema"')
    check('echo "result=$preserved_result_schema"')


def test_staged_credentials_are_rejected() -> None:
    validator = ROOT / "scripts/validate_repository.py"
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
        readme = repository / "README.md"
        readme.write_text("safe\n")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "base"], cwd=repository, check=True)
        readme.write_text("ghp_abcdefghijklmnopqrstuvwxyz\n")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)

        result = subprocess.run(
            [sys.executable, str(validator)], cwd=repository, text=True, capture_output=True
        )

        assert result.returncode != 0
        assert "credential-like value" in result.stderr


def test_security_properties() -> None:
    assert "pull_request_target" not in WORKFLOW
    assert "gh pr merge" not in WORKFLOW
    assert "contents: write" in WORKFLOW and "pull-requests: write" in WORKFLOW
    check("credential-like value", (ROOT / "scripts/validate_repository.py").read_text())


if __name__ == "__main__":
    for name, function in sorted(globals().copy().items()):
        if name.startswith("test_"):
            function()
            print(f"PASS {name}")
