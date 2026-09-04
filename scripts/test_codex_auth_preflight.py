#!/usr/bin/env python3
"""Static security and behavior checks for the manual Codex auth preflight."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/codex-auth-preflight.yml").read_text(
    encoding="utf-8"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def test_manual_and_serialized() -> None:
    trigger = WORKFLOW.split("on:", 1)[1].split("permissions:", 1)[0]
    require("workflow_dispatch:" in trigger, "preflight is not manually dispatched")
    for forbidden in ("pull_request:", "push:", "schedule:", "workflow_call:"):
        require(forbidden not in trigger, f"preflight exposes forbidden trigger: {forbidden}")
    require("group: codex-auth-preflight" in WORKFLOW, "preflight runs are not serialized")
    require("cancel-in-progress: false" in WORKFLOW, "a preflight run can cancel another run")


def test_least_privilege_and_secret_boundary() -> None:
    require("permissions: {}" in WORKFLOW, "preflight has unnecessary GitHub permissions")
    require(
        "environment: consulting-playbook-codex" in WORKFLOW,
        "protected Codex environment is missing",
    )
    require(
        WORKFLOW.count("OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}") == 1,
        "OPENAI_API_KEY must enter only the probe step",
    )
    for forbidden in (
        "actions/checkout",
        "TARGET_PUBLICATION_TOKEN",
        "CODEX_RESULT_TOKEN",
        "secrets: inherit",
        "git push",
        "gh pr",
        "set -x",
        "printenv OPENAI_API_KEY",
    ):
        require(forbidden not in WORKFLOW, f"preflight contains unsafe capability: {forbidden}")


def test_exact_client_and_read_only_probe() -> None:
    require(
        "npm install --global @openai/codex@0.63.0" in WORKFLOW,
        "preflight does not use the target's pinned Codex CLI",
    )
    require(
        "printf '%s' \"$OPENAI_API_KEY\" | codex login --with-api-key" in WORKFLOW,
        "preflight does not use Codex API-key login over stdin",
    )
    login_result = WORKFLOW.index("exit_code=$?", WORKFLOW.index("codex login"))
    unset_secret = WORKFLOW.index("unset OPENAI_API_KEY", login_result)
    probe_guard = WORKFLOW.index('if [[ "$exit_code" -eq 0 ]]', login_result)
    require(
        login_result < unset_secret < probe_guard,
        "raw key must be unset after every login attempt and before the probe",
    )
    require(
        WORKFLOW.count("unset OPENAI_API_KEY") == 1,
        "raw key cleanup must have one unambiguous location",
    )
    require("--sandbox read-only" in WORKFLOW, "provider probe is not read-only")
    require("--skip-git-repo-check" in WORKFLOW, "provider probe requires a repository checkout")
    require("Do not use tools. Reply with AUTHENTICATED only." in WORKFLOW, "probe prompt is not fixed")


def test_sanitized_diagnostics() -> None:
    for category in (
        "missing-credential",
        "authentication",
        "authorization-or-model-access",
        "quota",
        "rate-limit",
        "transport",
        "codex-runtime",
    ):
        require(category in WORKFLOW, f"missing safe failure category: {category}")
    for forbidden in ('cat "$preflight_log"', 'tee "$preflight_log"', "upload-artifact"):
        require(forbidden not in WORKFLOW, f"provider output can escape: {forbidden}")
    require("trap cleanup EXIT" in WORKFLOW, "temporary credentials and output are not cleaned")
    require("provider output withheld" in WORKFLOW, "failure diagnostic is not explicitly sanitized")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"passed {len(tests)} Codex auth-preflight checks")
