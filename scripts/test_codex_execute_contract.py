#!/usr/bin/env python3
"""Offline contract, adapter, evidence, and security regression checks."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any
from unittest.mock import patch

import codex_target_adapter as adapter_module
from codex_target_adapter import (
    AdapterError,
    GitHubEffects,
    Ownership,
    TARGET,
    canonical_digest,
    run_adapter,
)
from run_tc_mvp_ci_001 import EXPECTED_COMPATIBILITY_BLOBS, git_blob_sha1, validate_pin

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/codex-execute.yml").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def payload(**changes: Any) -> dict[str, Any]:
    delivery_id = "delivery-42"
    value = {
        "contract_version": "ai-sdlc-contract/v2",
        "correlation_id": "correlation-42",
        "delivery_id": delivery_id,
        "source_issue": "Young-Consultations/portfolio-tasks#135",
        "target_repository": TARGET,
        "task_type": "documentation",
        "execution_mode": "implement",
        "project": "consulting-playbook",
        "priority": "p0",
        "executor": "codex",
        "parallel_safe": False,
        "draft_pr_only": True,
        "instructions": "Update the approved consulting artifact.",
        "requested_branch": f"codex/{delivery_id}",
        "concurrency_group": "ai-sdlc.consulting.delivery-42",
        "timeout_minutes": 40,
    }
    value.update(changes)
    return value


class FakeEffects:
    def __init__(
        self,
        *,
        found: list[dict[str, Any]] | None = None,
        race: list[dict[str, Any]] | None = None,
        publish_failure: str | None = None,
        branch_exists: bool | None = None,
        race_branch_exists: bool | None = None,
        validation_result: tuple[bool, str] = (True, "passed"),
        candidate_changes: bool = True,
    ) -> None:
        self.found = found or []
        self.race = race
        self.publish_failure = publish_failure
        self.validation_result = validation_result
        self.candidate_changes = candidate_changes
        self.branch_exists = bool(self.found) if branch_exists is None else branch_exists
        self.race_branch_exists = (
            bool(race) if race_branch_exists is None else race_branch_exists
        )
        self.discoveries = 0
        self.codex_calls = 0
        self.publish_calls = 0
        self.validation_calls = 0

    def discover(self, *_: Any) -> Ownership:
        self.discoveries += 1
        if self.discoveries > 1 and self.race is not None:
            return Ownership(self.race_branch_exists, self.race)
        return Ownership(self.branch_exists, self.found)

    def codex(self, *_: Any) -> None:
        self.codex_calls += 1
        return None

    def validate_candidate(self, *_: Any) -> tuple[bool, str]:
        self.validation_calls += 1
        return self.validation_result

    def has_candidate_changes(self, *_: Any) -> bool:
        return self.candidate_changes

    def publish(self, *_: Any) -> str:
        self.publish_calls += 1
        if self.publish_failure:
            raise AdapterError("publication", self.publish_failure, "failed")
        return "https://github.com/Young-Consultations/consulting-playbook/pull/7"


class MissingCredentialEffects(FakeEffects):
    def codex(self, *_: Any) -> None:
        raise KeyError("TARGET_PUBLICATION_TOKEN")


def execute(value: dict[str, Any], effects: FakeEffects | None = None) -> dict[str, Any]:
    return run_adapter(
        json.dumps(value),
        value["concurrency_group"],
        "router-app",
        {"router-app"},
        effects or FakeEffects(),
    ).result


def managed(value: dict[str, Any], *, digest: str | None = None) -> dict[str, Any]:
    return {
        "url": "https://github.com/Young-Consultations/consulting-playbook/pull/7",
        "state": "OPEN",
        "draft": True,
        "digest": digest or canonical_digest(value),
    }


def test_exact_dispatch_and_receiver_boundary() -> None:
    trigger = WORKFLOW.split("on:", 1)[1].split("permissions:", 1)[0]
    inputs = trigger.split("inputs:", 1)[1]
    require("workflow_dispatch:" in trigger and "workflow_call:" not in WORKFLOW, "target must expose only workflow_dispatch")
    require(inputs.count("execution_input_json:") == 1 and inputs.count("concurrency_group:") == 1, "target inputs differ")
    workflow_lines = {line.strip() for line in WORKFLOW.splitlines()}
    require(
        "uses: Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v2.4.4"
        in workflow_lines,
        "receiver is not exactly and immutably pinned",
    )
    receiver = next(
        line.removeprefix("uses: ") for line in workflow_lines
        if line.startswith("uses: Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@")
    )
    requirements = (ROOT / "docs/requirements/NextMVP.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture/InterfaceArchitecture.md").read_text(encoding="utf-8")
    require(f"It shall invoke\n`{receiver}`" in requirements, "normative receiver requirement differs from target workflow")
    require(f"`{receiver}`" in architecture, "interface architecture differs from target workflow")
    require("CODEX_TRUSTED_JOURNAL_AUTHORS" not in WORKFLOW, "target supplies control-plane trust policy")
    require("secrets: inherit" not in WORKFLOW, "workflow broadly inherits secrets")
    receiver = WORKFLOW.split("  report:", 1)[1]
    require(receiver.count("CODEX_RESULT_TOKEN:") == 1, "receiver must receive only its delivery token")


def test_security_and_publication_guards() -> None:
    workflow_lines = {line.strip() for line in WORKFLOW.splitlines()}
    require("persist-credentials: false" in WORKFLOW, "checkout persists credentials")
    require("permissions:\n  contents: read" in WORKFLOW, "workflow permissions are broader than read-only")
    require("environment: consulting-playbook-codex" in WORKFLOW, "target environment boundary is missing")
    preparation = WORKFLOW.index("name: Prepare Codex workspace sandbox")
    credential_handoff = WORKFLOW.index("OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}")
    require(preparation < credential_handoff, "sandbox preparation must precede credential handoff")
    require(
        "kernel.unprivileged_userns_clone=1" in WORKFLOW
        and "kernel.apparmor_restrict_unprivileged_userns=0" in WORKFLOW,
        "GitHub runner no longer prepares the workspace-write sandbox",
    )
    sandbox_step = WORKFLOW.split("name: Prepare Codex workspace sandbox", 1)[1].split("name: Install Codex CLI", 1)[0]
    require(
        "|| true" not in sandbox_step
        and '[[ "$(sysctl -n kernel.unprivileged_userns_clone)" == "1" ]]' in sandbox_step
        and '[[ "$(sysctl -n kernel.apparmor_restrict_unprivileged_userns)" == "0" ]]' in sandbox_step,
        "sandbox preparation must fail closed when a required sysctl is unavailable",
    )
    require(
        "name: Enforce canonical execution outcome" in WORKFLOW
        and "needs.execute.outputs.execution_result != ''" in WORKFLOW
        and "if: ${{ always()" in WORKFLOW,
        "failed execution must make the job red while preserving receiver delivery",
    )
    require(
        "run: exec python3 scripts/codex_target_adapter.py" in workflow_lines,
        "runner shell remains as a secret-bearing ancestor",
    )
    require("gh pr merge" not in WORKFLOW and "git push origin main" not in WORKFLOW, "workflow can bypass draft review")
    require("CODEX_TARGET_TRUSTED_CALLERS" in WORKFLOW, "dispatch caller allowlist is missing")
    require(
        "run: npm install --global @openai/codex@0.154.0" in workflow_lines,
        "Codex CLI is not exactly pinned",
    )
    adapter = (ROOT / "scripts/codex_target_adapter.py").read_text(encoding="utf-8")
    require(
        '"codex", "exec", "--model", "gpt-5.3-codex"' in adapter,
        "Codex execution model is not exactly pinned",
    )
    require(
        '["codex", "login", "--with-api-key"]' in adapter,
        "production execution does not use the proven login flow",
    )
    require(
        '"--sandbox", "workspace-write", "-C", str(ROOT)' in adapter,
        "Codex does not use the bounded writable target workspace",
    )
    require(
        "run: python -m pip install --disable-pip-version-check --no-input 'jsonschema[format]==4.26.0'"
        in workflow_lines,
        "runtime validator is not exactly pinned",
    )


def test_runtime_secrets_cross_reexec_without_environment_exposure() -> None:
    captured: dict[str, str] = {}

    def stop_at_exec(executable: str, argv: list[str], env: dict[str, str]) -> None:
        require(executable == sys.executable and argv[0] == sys.executable, "adapter re-exec target drifted")
        require(all(name not in env for name in adapter_module.SECRET_NAMES), "secret crossed re-exec in environment")
        fd = int(env[adapter_module.SECRET_FD_ENV])
        os.lseek(fd, 0, os.SEEK_SET)
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            captured.update(json.load(stream))
        raise RuntimeError("exec intercepted")

    with (
        patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "openai-sentinel",
                "TARGET_PUBLICATION_TOKEN": "github-sentinel",
                "TRUSTED_CALLERS": "trusted-sentinel",
            },
            clear=True,
        ),
        patch("codex_target_adapter.os.execve", side_effect=stop_at_exec),
    ):
        try:
            adapter_module._bootstrap_secret_environment()
        except RuntimeError as exc:
            require(str(exc) == "exec intercepted", "unexpected bootstrap failure")
        else:
            raise ValueError("adapter did not replace its secret-bearing process image")
        require(
            all(name not in os.environ for name in adapter_module.SECRET_NAMES),
            "adapter retained a runtime secret",
        )

    require(
        captured
        == {
            "OPENAI_API_KEY": "openai-sentinel",
            "TARGET_PUBLICATION_TOKEN": "github-sentinel",
            "TRUSTED_CALLERS": "trusted-sentinel",
        },
        "anonymous secret handoff changed credential bytes",
    )

    adapter_module._RUNTIME_SECRETS.clear()
    fd = os.memfd_create("test-inherited-secrets", flags=0)
    os.write(fd, json.dumps(captured).encode())
    os.lseek(fd, 0, os.SEEK_SET)
    with patch.dict(os.environ, {adapter_module.SECRET_FD_ENV: str(fd)}, clear=True):
        adapter_module._bootstrap_secret_environment()
        require(adapter_module.SECRET_FD_ENV not in os.environ, "inherited secret FD remained in environment")
        require(
            adapter_module._RUNTIME_SECRETS == captured,
            "re-executed adapter did not load inherited runtime secrets",
        )
        try:
            os.fstat(fd)
        except OSError:
            pass
        else:
            raise ValueError("inherited secret FD remained open after loading")
        require(
            adapter_module._take_secret("OPENAI_API_KEY") == "openai-sentinel"
            and adapter_module._take_secret("TARGET_PUBLICATION_TOKEN") == "github-sentinel"
            and adapter_module._take_optional_secret("TRUSTED_CALLERS") == "trusted-sentinel",
            "loaded runtime secrets could not be consumed",
        )
        require(not adapter_module._RUNTIME_SECRETS, "consumed runtime secrets remained in memory store")


def test_production_codex_runtime_matches_preflight_boundary() -> None:
    calls: list[dict[str, Any]] = []
    executions: list[dict[str, Any]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        call = {"command": command, **kwargs}
        if command[:3] == ["git", "push", "--dry-run"]:
            call["askpass_script"] = Path(kwargs["env"]["GIT_ASKPASS"]).read_text(encoding="utf-8")
        calls.append(call)
        if command == ["codex", "login", "--with-api-key"]:
            auth_path = Path(kwargs["env"]["CODEX_HOME"]) / "auth.json"
            auth_path.write_text(
                json.dumps({"auth_mode": "apikey", "OPENAI_API_KEY": kwargs["input"]}),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(command, 0)

    class FakeCodexProcess:
        def __init__(self, command: list[str], **kwargs: Any):
            self.command, self.kwargs, self.returncode = command, kwargs, None
            self.auth_payloads: list[str] = []

            class Input:
                def __init__(self) -> None:
                    self.value = ""
                    self.closed = threading.Event()

                def write(self, value: str) -> None:
                    self.value += value

                def close(self) -> None:
                    self.closed.set()

            self.input = Input()
            self.stdin = self.input
            self._reader = threading.Thread(target=self._read_auth)
            self._reader.start()
            executions.append({"command": command, **kwargs, "process": self})

        def _read_auth(self) -> None:
            path = Path(self.kwargs["env"]["CODEX_HOME"]) / "auth.json"
            self.auth_payloads.append(path.read_text(encoding="utf-8"))
            require(self.input.closed.wait(5), "Codex prompt was not submitted after config auth")
            self.auth_payloads.append(path.read_text(encoding="utf-8"))

        def poll(self) -> int | None:
            return self.returncode

        def communicate(self, timeout: float) -> tuple[None, None]:
            self.kwargs["input"] = self.input.value
            self.kwargs["timeout"] = timeout
            self._reader.join(timeout)
            require(not self._reader.is_alive(), "Codex did not consume both startup authentication reads")
            auth_path = Path(self.kwargs["env"]["CODEX_HOME"]) / "auth.json"
            self.auth_path_absent_during_execution = not auth_path.exists()
            self.returncode = 0
            return None, None

        def kill(self) -> None:
            self.returncode = -9

        def wait(self) -> int:
            assert self.returncode is not None
            return self.returncode

    effects = GitHubEffects()
    def fake_submit_prompt(proc: FakeCodexProcess, prompt: str, remaining: Any) -> None:
        proc.stdin.write(prompt)
        proc.stdin.close()
        proc.stdin = None

    with (
        patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sentinel-openai-key",
                "TARGET_PUBLICATION_TOKEN": "sentinel-publication-token",
                "CODEX_PROFILE": "ambient-profile-must-not-cross-boundary",
            },
            clear=False,
        ),
        patch.object(effects, "_gh", return_value="true\n") as github,
        patch("codex_target_adapter.subprocess.run", side_effect=fake_run),
        patch("codex_target_adapter.subprocess.Popen", side_effect=FakeCodexProcess),
        patch("codex_target_adapter.submit_stdin_prompt", side_effect=fake_submit_prompt),
    ):
        effects.codex("Implement the admitted task.", 30)
        require("OPENAI_API_KEY" not in os.environ, "adapter retained the raw OpenAI credential")

    github.assert_called_once_with(
        "api",
        f"repos/{TARGET}",
        "--jq",
        ".permissions.push",
        timeout_seconds=github.call_args.kwargs["timeout_seconds"],
    )
    require(len(calls) == 2 and len(executions) == 1, "production runtime did not perform transport probe, login, and execution")
    probe, login, execution = calls[0], calls[1], executions[0]
    require(probe["command"][:3] == ["git", "push", "--dry-run"], "publication transport was not proven before Codex")
    require(
        probe["env"]["GIT_USERNAME"] == "x-access-token"
        and probe["env"]["GIT_PASSWORD"] == "sentinel-publication-token"
        and probe["env"]["GIT_TERMINAL_PROMPT"] == "0",
        "publication dry-run did not use the controlled Git credential boundary",
    )
    require(
        "sentinel-publication-token" not in " ".join(probe["command"])
        and "sentinel-publication-token" not in probe["askpass_script"],
        "publication credential leaked into Git arguments or helper content",
    )
    require(
        "*Username*" in probe["askpass_script"] and "$GIT_PASSWORD" in probe["askpass_script"],
        "publication askpass helper does not distinguish username and password prompts",
    )
    require(login["command"] == ["codex", "login", "--with-api-key"], "Codex login command drifted")
    require(login["input"] == "sentinel-openai-key", "Codex login did not receive the credential over stdin")
    require(
        execution["process"].kwargs["input"] == "Implement the admitted task.",
        "Codex execution did not receive admitted instructions",
    )
    require(login["cwd"] == ROOT and execution["cwd"] == ROOT, "Codex did not run from the target repository root")
    require(
        "OPENAI_API_KEY" not in login["env"] and "OPENAI_API_KEY" not in execution["env"],
        "raw OpenAI credential was exposed to a child environment",
    )
    require(
        "TARGET_PUBLICATION_TOKEN" not in login["env"]
        and "TARGET_PUBLICATION_TOKEN" not in execution["env"],
        "publication credential was exposed to a Codex child environment",
    )
    require(
        "CODEX_PROFILE" not in login["env"] and "CODEX_PROFILE" not in execution["env"],
        "ambient Codex profile crossed the controlled runtime boundary",
    )
    require(
        login["env"]["CODEX_HOME"] == execution["env"]["CODEX_HOME"],
        "login and execution did not share isolated authentication state",
    )
    require(
        not Path(login["env"]["CODEX_HOME"]).exists(),
        "ephemeral Codex authentication state was retained",
    )
    require(
        execution["process"].auth_path_absent_during_execution,
        "Codex authentication remained readable while model tools could run",
    )
    require(
        len(execution["process"].auth_payloads) == 2
        and all(json.loads(payload).get("OPENAI_API_KEY") == "sentinel-openai-key"
                for payload in execution["process"].auth_payloads),
        "Codex did not receive both startup authentication reads",
    )
    require(
        execution["command"] == [
            "codex", "exec", "--model", "gpt-5.3-codex",
            "--sandbox", "workspace-write", "-C", str(ROOT), "-",
        ],
        "production Codex client, model, sandbox, or workspace differs from policy",
    )

    with patch("codex_target_adapter.subprocess.check_output", side_effect=[b"", b"?? docs/probe.md\0"]) as status:
        require(not effects.has_candidate_changes(10), "unchanged checkout appeared to have a candidate")
        require(effects.has_candidate_changes(10), "new repository file was not recognized as a candidate")
        require(
            all(call.args[0][:3] == ["git", "status", "--porcelain=v1"] for call in status.call_args_list),
            "candidate detection no longer examines repository status",
        )

    class StoppedCodexProcess:
        stdin = None

        def poll(self) -> None:
            return None

        def kill(self) -> None:
            pass

        def wait(self) -> int:
            return -9

    for failure in (RuntimeError("auth reader exited"),
                    subprocess.TimeoutExpired("codex auth", 1)):
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "sentinel-openai-key"}, clear=False),
            patch.object(effects, "_gh", return_value="true\n"),
            patch("codex_target_adapter.subprocess.run", side_effect=fake_run),
            patch("codex_target_adapter.subprocess.Popen", return_value=StoppedCodexProcess()),
            patch("codex_target_adapter.handoff_startup_auth", side_effect=failure),
        ):
            try:
                effects.codex("Do not execute.", 30)
            except AdapterError as exc:
                require(exc.category == "authentication", "handoff failure lost authentication category")
            else:
                raise ValueError("handoff failure did not fail closed")

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "sentinel-openai-key"}, clear=False),
        patch.object(effects, "_gh", return_value="false\n"),
        patch("codex_target_adapter.subprocess.run") as denied_run,
    ):
        try:
            effects.codex("Do not execute.", 30)
        except AdapterError as exc:
            require(exc.category == "authorization", "publication denial used the wrong category")
        else:
            raise ValueError("publication denial did not fail closed")
        require(not denied_run.called, "Codex ran without repository write access")

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "sentinel-openai-key"}, clear=False),
        patch.object(
            effects,
            "_gh",
            side_effect=subprocess.CalledProcessError(1, ["gh", "api"]),
        ),
        patch("codex_target_adapter.subprocess.run") as unavailable_run,
    ):
        try:
            effects.codex("Do not execute.", 30)
        except AdapterError as exc:
            require(exc.category == "publication", "publication probe failure used the wrong category")
        else:
            raise ValueError("failed publication readiness probe did not fail closed")
        require(not unavailable_run.called, "Codex ran after publication readiness failed")

    probe_effects = GitHubEffects()
    with (
        patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sentinel-openai-key",
                "TARGET_PUBLICATION_TOKEN": "sentinel-publication-token",
            },
            clear=False,
        ),
        patch.object(probe_effects, "_gh", return_value="true\n"),
        patch(
            "codex_target_adapter.subprocess.run",
            return_value=subprocess.CompletedProcess(["git", "push", "--dry-run"], 1),
        ) as failed_probe,
        patch("codex_target_adapter.subprocess.Popen") as blocked_codex,
    ):
        try:
            probe_effects.codex("Do not execute.", 30)
        except AdapterError as exc:
            require(
                exc.category == "publication"
                and exc.safe_message == "Publication git transport readiness check failed",
                "transport denial did not retain publication readiness classification",
            )
        else:
            raise ValueError("failed Git transport readiness probe did not fail closed")
        require(failed_probe.call_count == 1, "transport readiness did not stop at the failed dry-run")
        require(not blocked_codex.called, "Codex started after Git transport readiness failed")
        require(
            "OPENAI_API_KEY" in os.environ,
            "OpenAI credential was consumed before publication transport readiness passed",
        )

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "sentinel-openai-key"}, clear=False),
        patch.object(effects, "_gh", side_effect=KeyError("TARGET_PUBLICATION_TOKEN")),
        patch("codex_target_adapter.subprocess.run") as missing_token_run,
    ):
        try:
            effects.codex("Do not execute.", 30)
        except KeyError:
            pass
        else:
            raise ValueError("missing publication credential was misclassified by the Codex effect")
        require(not missing_token_run.called, "Codex ran without the publication credential")

    def fail_login_after_transport_probe(
        command: list[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        if command[:3] == ["git", "push", "--dry-run"]:
            return subprocess.CompletedProcess(command, 0)
        return subprocess.CompletedProcess(command, 1)

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "sentinel-openai-key"}, clear=False),
        patch.object(effects, "_gh", return_value="true\n"),
        patch(
            "codex_target_adapter.subprocess.run",
            side_effect=fail_login_after_transport_probe,
        ) as failed_login,
    ):
        try:
            effects.codex("Do not execute.", 30)
        except AdapterError as exc:
            require(exc.category == "authentication", "login failure used the wrong category")
        else:
            raise ValueError("failed Codex login did not fail closed")
        require(failed_login.call_count == 2, "Codex login did not follow exactly one successful transport probe")



def test_publication_transport_auth_and_failure_classification() -> None:
    def exercise(stderr: bytes) -> tuple[AdapterError, dict[str, Any]]:
        effects = GitHubEffects()
        effects._publication_token = "sentinel-publication-token"
        observed: dict[str, Any] = {}

        def fake_publish_run(
            command: list[str], **kwargs: Any
        ) -> subprocess.CompletedProcess[Any]:
            if command[:3] == ["git", "diff", "--cached"]:
                return subprocess.CompletedProcess(command, 1)
            if command[:2] == ["git", "push"]:
                observed["command"] = command
                observed["env"] = kwargs["env"]
                helper_path = Path(kwargs["env"]["GIT_ASKPASS"])
                observed["helper_path"] = helper_path
                observed["helper"] = helper_path.read_text(encoding="utf-8")
                return subprocess.CompletedProcess(command, 1, stderr=stderr)
            return subprocess.CompletedProcess(command, 0)

        with patch("codex_target_adapter.subprocess.run", side_effect=fake_publish_run):
            try:
                effects.publish("codex/delivery-42", "delivery-42", "a" * 64, 30)
            except AdapterError as exc:
                observed["helper_removed"] = not observed["helper_path"].exists()
                return exc, observed
        raise ValueError("failed publication unexpectedly succeeded")

    denied, observed = exercise(b"fatal: Authentication failed for repository")
    require(
        denied.category == "publication"
        and denied.status == "failed"
        and denied.safe_message == "Draft branch publication failed",
        "ordinary Git publication failure was misclassified as a create race",
    )
    require(
        observed["env"]["GIT_USERNAME"] == "x-access-token"
        and observed["env"]["GIT_PASSWORD"] == "sentinel-publication-token"
        and observed["env"]["GIT_TERMINAL_PROMPT"] == "0",
        "publication push did not use the controlled Git credential environment",
    )
    require(
        "sentinel-publication-token" not in " ".join(observed["command"])
        and "sentinel-publication-token" not in observed["helper"],
        "publication token leaked into Git arguments or helper content",
    )
    require(
        "*Username*" in observed["helper"] and "$GIT_PASSWORD" in observed["helper"],
        "publication helper does not answer Git username and password prompts separately",
    )
    require(observed["helper_removed"], "publication askpass helper was retained after push failure")

    raced, _ = exercise(b"! [rejected] HEAD -> delivery (non-fast-forward)\nerror: failed to push some refs")
    require(
        raced.category == "publication" and raced.safe_message == "create-race",
        "non-fast-forward publication race no longer enters reconciliation",
    )

def test_canonical_policy_and_result() -> None:
    verify_effects = FakeEffects()
    result = execute(payload(execution_mode="verify"), verify_effects)
    require(result["execution_status"] == "verified", "verify mode did not complete canonically")
    require(result["branch_name"] is None and result["pull_request_url"] is None, "verify mode published state")
    require(result["validation_result"] == "passed" and result["test_result"] == "passed", "verify evidence is incomplete")
    require(verify_effects.validation_calls == 1, "verify mode skipped repository validation")
    unchanged = FakeEffects(candidate_changes=False)
    blocked = execute(payload(), unchanged)
    require(
        blocked["execution_status"] == "failed"
        and blocked["failure_category"] == "codex-runtime"
        and blocked["validation_result"] == "not-run"
        and blocked["test_result"] == "not-run"
        and blocked["pull_request_url"] is None,
        "empty implementation was mistaken for a successful no-changes result",
    )
    require(
        unchanged.validation_calls == 0 and unchanged.publish_calls == 0,
        "empty implementation reached baseline validation or publication",
    )
    missing_credential = execute(payload(), MissingCredentialEffects())
    require(
        missing_credential["execution_status"] == "failed"
        and missing_credential["failure_category"] == "authentication",
        "missing publication credential did not retain canonical authentication classification",
    )
    failed = execute(
        payload(execution_mode="verify"),
        FakeEffects(validation_result=(False, "tests")),
    )
    require(
        failed["execution_status"] == "failed"
        and failed["failure_category"] == "tests"
        and failed["validation_result"] == "passed"
        and failed["test_result"] == "failed",
        "verify mode reported success after repository tests failed",
    )
    rejected = execute(payload(target_repository="Young-Consultations/slugger"))
    require(rejected["execution_status"] == "rejected" and rejected["failure_category"] == "repository-routing", "wrong target was admitted")
    old_shape = payload(task_id="TASK-42")
    require(execute(old_shape)["failure_category"] == "contract-validation", "obsolete input field was admitted")


def test_rejected_source_issue_is_not_exposed() -> None:
    value = payload(source_issue="bad\nexecution_result=forged\nsource_issue=Young-Consultations/x#1")
    outcome = run_adapter(
        json.dumps(value),
        value["concurrency_group"],
        "router-app",
        {"router-app"},
        FakeEffects(),
    )
    require(outcome.result["failure_category"] == "contract-validation", "invalid issue was admitted")
    require(outcome.source_issue is None, "rejected issue was exposed as a workflow output")


def test_idempotency_and_create_race() -> None:
    value = payload()
    reused = execute(value, FakeEffects(found=[managed(value)]))
    require(reused["execution_status"] == "duplicate-reused", "managed draft was not reused")
    conflict = execute(value, FakeEffects(found=[managed(value, digest="0" * 64)]))
    require(conflict["execution_status"] == "ambiguous-rejected", "ownership conflict did not fail closed")
    orphan_effects = FakeEffects(branch_exists=True)
    orphan = execute(value, orphan_effects)
    require(orphan["execution_status"] == "ambiguous-rejected", "orphan branch did not fail closed")
    require(
        orphan_effects.codex_calls == 0 and orphan_effects.publish_calls == 0,
        "orphan branch reached executor or publication",
    )
    race = execute(
        value,
        FakeEffects(
            publish_failure="create-race",
            race=[managed(value), managed(value)],
        ),
    )
    require(race["execution_status"] == "ambiguous-rejected", "ambiguous create race did not fail closed")


def test_exact_shared_blobs_and_evidence() -> None:
    pin = json.loads((ROOT / "config/mvp-conformance-pin.json").read_text(encoding="utf-8"))
    require(validate_pin(pin) == [], "conformance pin is invalid")
    for relative, expected in EXPECTED_COMPATIBILITY_BLOBS.items():
        require(git_blob_sha1((ROOT / relative).read_bytes()) == expected, f"shared file differs: {relative}")
    report = json.loads((ROOT / ".ai-sdlc/conformance/tc-mvp-ci-001.json").read_text(encoding="utf-8"))
    require(report["adapter_revision"] == pin["adapter_revision"], "report and pin revisions differ")
    require(len(report["scenario_results"]) == 29, "report does not contain the complete oracle")
    require(all(row["result"] == "pass" for row in report["scenario_results"]), "report contains a failed scenario")
    require(all(value == 0 for value in report["effect_traps"].values()), "report records a prohibited effect")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"passed {len(tests)} target-adapter checks")
