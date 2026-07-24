#!/usr/bin/env python3
"""Static contract checks for the Codex execution workflow."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "codex-execute.yml"
TEXT = WORKFLOW.read_text()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def init_repo() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="codex-contract-"))
    run(["git", "init"], tmp).check_returncode()
    run(["git", "config", "user.email", "contract@example.com"], tmp).check_returncode()
    run(["git", "config", "user.name", "Contract Test"], tmp).check_returncode()
    (tmp / "README.md").write_text("baseline\n")
    run(["git", "add", "README.md"], tmp).check_returncode()
    run(["git", "commit", "-m", "baseline"], tmp).check_returncode()
    return tmp


def has_generated_changes(repo: Path) -> bool:
    return bool(run(["git", "status", "--porcelain"], repo).stdout.strip())


def target_repository(body: str) -> str:
    patterns = [
        r"<!--\s*target_repository:\s*([^\s<>]+)\s*-->",
        r"(?im)^target_repository:\s*([^\s]+)\s*$",
        r"(?im)^target repository:\s*([^\s]+)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, body)
        if match:
            return match.group(1).strip()

    lines = body.splitlines()
    for index, line in enumerate(lines):
        if re.fullmatch(r"\s*#{2,6}\s*Target repository\s*", line, re.IGNORECASE):
            for candidate in lines[index + 1 :]:
                candidate = candidate.strip()
                if not candidate:
                    continue
                if candidate.startswith("#"):
                    break
                candidate = re.sub(r"^[-*]\s*", "", candidate).strip()
                return candidate.strip("` ")
            break
    return ""


def test_untracked_file_is_valid_change() -> None:
    repo = init_repo()
    (repo / "new-file.txt").write_text("new\n")
    assert_true(has_generated_changes(repo), "untracked file must be detected as a generated change")


def test_unchanged_repository_fails_validation() -> None:
    repo = init_repo()
    assert_true(not has_generated_changes(repo), "unchanged repository must fail generated-change validation")


def test_generated_change_detection_uses_porcelain() -> None:
    assert_true("git status --porcelain" in TEXT, "workflow must use git status --porcelain for change detection")
    assert_true("git diff --quiet" not in TEXT, "workflow must not use git diff --quiet for change detection")


def test_compileall_failure_not_ignored() -> None:
    assert_true("python -m compileall . || true" not in TEXT, "compileall failures must not be suppressed")
    assert_true("python -m compileall ." in TEXT, "workflow should still run Python compilation when applicable")


def test_passing_tests_report_passed() -> None:
    assert_true('pytest\n              test_result="passed"' in TEXT, "test_result must become passed only after pytest succeeds")


def test_missing_test_infrastructure_reports_explicit_state() -> None:
    assert_true('test_result="not-applicable"' in TEXT, "default test result should be not-applicable")
    assert_true('test_result="not-configured"' in TEXT, "missing pytest should report not-configured")


def test_other_repository_target_rejected() -> None:
    repo = target_repository("<!-- target_repository: Young-Consultations/other-repo -->")
    assert_true(repo != "Young-Consultations/consulting-playbook", "other target repository must be rejected")


def test_consulting_repository_target_accepted() -> None:
    repo = target_repository("## Target repository\n`Young-Consultations/consulting-playbook`\n")
    assert_true(repo == "Young-Consultations/consulting-playbook", "consulting-playbook target should be accepted")


def test_third_party_actions_are_pinned_to_full_shas() -> None:
    uses = re.findall(r"uses:\s+(actions/checkout|openai/codex-action)@([^\s#]+)", TEXT)
    assert_true(len(uses) == 2, "expected pinned checkout and codex actions")
    for action, ref in uses:
        assert_true(re.fullmatch(r"[0-9a-f]{40}", ref) is not None, f"{action} must be pinned to a full SHA")
    assert_true("# v" in TEXT, "pinned actions should include release-version comments")


def test_no_auto_merge_or_pull_request_target() -> None:
    assert_true("pull_request_target" not in TEXT, "workflow must not use pull_request_target")
    assert_true("--draft" in TEXT, "workflow must create draft PRs")
    forbidden = [r"gh\s+pr\s+merge", r"merge\s+--auto", r"enable-auto-merge"]
    for pattern in forbidden:
        assert_true(re.search(pattern, TEXT) is None, f"workflow must not introduce {pattern}")


def main() -> None:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
