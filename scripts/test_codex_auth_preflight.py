#!/usr/bin/env python3
"""Offline structural and executable tests of the actual workflow shell."""
import os
import subprocess
import tempfile
import textwrap
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


def test_executable_paths() -> None:
    # Execute the exact YAML run block. Only the Codex executable is substituted;
    # no API request, credential lookup, install, checkout or publication occurs.
    script = textwrap.dedent(WORKFLOW.split("        run: |\n", 1)[1])
    subprocess.run(["bash", "-n"], input=script, text=True, check=True)
    fake = '''#!/bin/bash
set -eu
echo "$1" >> "$CALLS"
if [[ "$1" == login ]]; then
  [[ "$2" == --with-api-key ]] || exit 90
  supplied=$(cat)
  [[ "$supplied" == "$EXPECTED_KEY" ]] || exit 91
  printf '%s' "$supplied" > "$CODEX_HOME/auth.json"
  printf '%s' "$LOGIN_TEXT"
  printf '%s' "$LOGIN_TEXT" >&2
  exit "$LOGIN_CODE"
fi
[[ "$1" == exec ]] || exit 92
[[ -z "${OPENAI_API_KEY+x}" ]] || exit 93
[[ "$(cat "$CODEX_HOME/auth.json")" == "$EXPECTED_KEY" ]] || exit 94
[[ "$*" == *"--sandbox read-only --skip-git-repo-check"* ]] || exit 95
printf '%s' "$PROBE_TEXT"
printf '%s' "$PROBE_TEXT" >&2
exit "$PROBE_CODE"
'''
    cases = [
        ("missing", 0, 0, "", "", "credential-check", 1, "missing-credential", []),
        ("success", 0, 0, "credential stored", "AUTHENTICATED", "probe", 0, "authenticated", ["login", "exec"]),
        ("login-failed", 7, 0, "unrecognized option", "", "login", 7, "cli-arguments", ["login"]),
        ("login-empty", 8, 0, "", "", "login", 8, "codex-runtime", ["login"]),
        ("auth", 0, 1, "", "401 Unauthorized", "probe", 1, "authentication", ["login", "exec"]),
        ("model", 0, 1, "", "model_not_found", "probe", 1, "authorization-or-model-access", ["login", "exec"]),
        ("permission-underscore", 0, 1, "", "permission_denied", "probe", 1, "authorization-or-model-access", ["login", "exec"]),
        ("permission-hyphen", 0, 1, "", "permission-denied", "probe", 1, "authorization-or-model-access", ["login", "exec"]),
        ("quota", 0, 1, "", "429 insufficient_quota", "probe", 1, "quota", ["login", "exec"]),
        ("rate", 0, 1, "", "429 Too many requests", "probe", 1, "rate-limit", ["login", "exec"]),
        ("network", 0, 1, "", "connection timed out", "probe", 1, "transport", ["login", "exec"]),
        ("sandbox", 0, 1, "", "Landlock sandbox failed", "probe", 1, "sandbox", ["login", "exec"]),
        ("config", 0, 2, "", "TOML parse error", "probe", 2, "client-configuration", ["login", "exec"]),
        ("service", 0, 1, "", "503 Service Unavailable", "probe", 1, "provider-service", ["login", "exec"]),
        ("filesystem", 0, 1, "", "Permission denied", "probe", 1, "local-filesystem", ["login", "exec"]),
        ("empty", 0, 9, "", "", "probe", 9, "codex-runtime", ["login", "exec"]),
        ("stage-isolation", 0, 6, "401 old login diagnostic", "unknown failure", "probe", 6, "codex-runtime", ["login", "exec"]),
        ("client-missing", 127, 0, "command not found", "", "login", 127, "client-unavailable", ["login"]),
    ]
    header = "OpenAI Codex v0.63.0\n--------\nworkdir: /tmp/preflight\nmodel: gpt-5-codex\nprovider: openai\napproval: never\nsandbox: read-only\n--------\n"
    cases.extend([
        ("sandbox-init", 0, 1, "", "error: failed to initialize sandbox", "probe", 1, "sandbox", ["login", "exec"]),
        ("landlock", 0, 1, "", "error running landlock: Sandbox(LandlockRestrict)", "probe", 1, "sandbox", ["login", "exec"]),
        ("sandbox-mention", 0, 1, "", "sandbox enabled\nunknown failure", "probe", 1, "codex-runtime", ["login", "exec"]),
        ("bwrap-mention", 0, 1, "", "bwrap available\nunknown failure", "probe", 1, "codex-runtime", ["login", "exec"]),
    ])
    for name, login, probe, login_text, probe_text, stage, code, category, calls in cases:
        with tempfile.TemporaryDirectory(prefix="preflight-test-") as directory:
            root = Path(directory)
            binary = root / "codex"
            binary.write_text(fake, encoding="utf-8")
            binary.chmod(0o700)
            sentinel = "synthetic-sensitive-value"
            # Also inject a forged workflow command. No raw text may escape.
            poison = sentinel + "\n::error::forged-provider-output\n"
            env = {
                "PATH": str(root) + os.pathsep + os.defpath,
                "RUNNER_TEMP": str(root),
                "GITHUB_STEP_SUMMARY": str(root / "summary"),
                "GITHUB_RUN_ID": "123",
                "OPENAI_API_KEY": "" if name == "missing" else sentinel,
                "EXPECTED_KEY": sentinel,
                "CALLS": str(root / "calls"),
                "LOGIN_CODE": str(login), "PROBE_CODE": str(probe),
                "LOGIN_TEXT": login_text + poison,
                "PROBE_TEXT": header + probe_text + "\n" + poison,
            }
            result = subprocess.run(["bash", "--noprofile", "--norc", "-c", script],
                                    env=env, cwd=root, capture_output=True, text=True, timeout=10)
            summary = (root / "summary").read_text(encoding="utf-8")
            output = result.stdout + result.stderr + summary
            require(result.returncode == code, f"{name}: original exit code lost")
            require(f"- Stage: {stage}" in summary, f"{name}: stage missing")
            require(f"- Exit code: {code}" in summary, f"{name}: exit code missing")
            require(f"- Category: {category}" in summary, f"{name}: wrong category")
            reports = [block for block in summary.split("### Codex authentication preflight\n") if block.strip()]
            require(len(reports) == (2 if stage == "probe" else 1), f"{name}: missing or extra report")
            for report in reports:
                require("- Run ID: 123\n" in report, f"{name}: run identity missing")
                require("- Client: Codex CLI 0.63.0\n" in report, f"{name}: reported client differs from install pin")
            if stage == "probe":
                login_report = reports[0]
                require("- Stage: login\n" in login_report and "- Outcome: passed\n" in login_report
                        and "- Exit code: 0\n" in login_report
                        and "- Category: credential-stored\n" in login_report
                        and "- Category: authenticated\n" not in login_report,
                        f"{name}: login storage confused with provider authentication")
            observed = (root / "calls").read_text().splitlines() if (root / "calls").exists() else []
            require(observed == calls, f"{name}: wrong command sequence")
            require(sentinel not in output and "forged-provider-output" not in output,
                    f"{name}: sensitive provider output escaped")
            require(not (root / "codex-auth-preflight").exists(), f"{name}: auth state retained")
            require(not (root / "codex-auth-preflight.log").exists(), f"{name}: raw log retained")
    print(f"passed {len(cases)} executable preflight scenarios (fake Codex only)")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"passed {len(tests)} Codex auth-preflight checks")
