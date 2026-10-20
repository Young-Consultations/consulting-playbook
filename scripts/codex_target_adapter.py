#!/usr/bin/env python3
"""Fail-closed target adapter for the consulting-playbook repository.

The pure ``run_adapter`` entry point is intentionally dependency-injected so
TC-MVP-CI-001 can exercise every transition without Codex or GitHub effects.
The command-line adapter uses ``gh`` only after admission and reconciliation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator, FormatChecker
from codex_auth_handoff import handoff_startup_auth, isolated_codex_home, submit_stdin_prompt
from candidate_test_sandbox import sandbox_ready, run_candidate_tests
from task_content_baseline import BaselineError, PublicationDisposition, PublicationPhase, verify_publication_head
from task_content_checkout import TrustedContentCheckout, attest_default_branch, checkout_attested_base, remaining_time

ROOT = Path(__file__).resolve().parents[1]
TARGET = "Young-Consultations/consulting-playbook"
MARKER = "ai-sdlc-delivery-id"
ALLOWED_TYPES = {"automation", "documentation", "feature", "testing"}
SAFE_ENV = {"PATH", "HOME", "LANG", "LC_ALL", "CI", "GITHUB_ACTIONS"}
SECRET_NAMES = ("OPENAI_API_KEY", "TARGET_PUBLICATION_TOKEN", "CONTENT_READ_TOKEN", "TRUSTED_CALLERS")
SECRET_FD_ENV = "CODEX_ADAPTER_SECRETS_FD"
_RUNTIME_SECRETS: dict[str, str] = {}


def _bootstrap_secret_environment() -> None:
    """Re-exec once so runner secrets never remain in this process environment."""
    inherited_fd = os.environ.pop(SECRET_FD_ENV, None)
    if inherited_fd is not None:
        fd = int(inherited_fd)
        try:
            with os.fdopen(fd, "r", encoding="utf-8") as stream:
                loaded = json.load(stream)
        except (OSError, ValueError, TypeError) as exc:
            raise AdapterError("authentication", "Execution credentials could not be isolated", "failed") from exc
        if not isinstance(loaded, dict) or any(not isinstance(value, str) for value in loaded.values()):
            raise AdapterError("authentication", "Execution credentials could not be isolated", "failed")
        _RUNTIME_SECRETS.update(loaded)
        return

    available = {name: os.environ.pop(name) for name in SECRET_NAMES if name in os.environ}
    if not available:
        return
    fd = os.memfd_create("codex-adapter-secrets", flags=0)
    os.set_inheritable(fd, True)
    os.write(fd, json.dumps(available).encode())
    os.lseek(fd, 0, os.SEEK_SET)
    clean_env = dict(os.environ)
    clean_env[SECRET_FD_ENV] = str(fd)
    os.execve(sys.executable, [sys.executable, *sys.argv], clean_env)


def _take_secret(name: str) -> str:
    if name in _RUNTIME_SECRETS:
        return _RUNTIME_SECRETS.pop(name)
    return os.environ.pop(name)


def _take_optional_secret(name: str) -> str:
    if name in _RUNTIME_SECRETS:
        return _RUNTIME_SECRETS.pop(name)
    return os.environ.pop(name, "")


class AdapterError(Exception):
    def __init__(self, category: str, message: str, status: str = "rejected",
                 *, branch: str | None = None, pr: str | None = None):
        self.category, self.safe_message, self.status = category, message[:500], status
        self.branch, self.pr = branch, pr
        super().__init__(self.safe_message)


class Effects(Protocol):
    def discover(self, branch: str, delivery_id: str, timeout_seconds: float) -> "Ownership": ...
    def prepare_content(self, delivery_id: str, timeout_seconds: float) -> None: ...
    def codex(self, instructions: str, timeout_seconds: float) -> None: ...
    def has_candidate_changes(self, timeout_seconds: float) -> bool: ...
    def validate_candidate(self, timeout_seconds: float) -> tuple[bool, str]: ...
    def verify_recovered_publication(self, branch: str, pr: str, timeout_seconds: float) -> None: ...
    def publish(self, branch: str, delivery_id: str, digest: str, timeout_seconds: float) -> str: ...


@dataclass
class Outcome:
    result: dict[str, Any]
    source_issue: str | None


@dataclass
class Ownership:
    """Remote branch and pull-request state observed in one preflight."""

    branch_exists: bool
    pull_requests: list[dict[str, Any]]


def canonical_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")


def _safe_identity(value: Any, fallback: str) -> str:
    """Project an untrusted identity into the result contract without echoing it."""
    return value if isinstance(value, str) and _IDENTITY.fullmatch(value) else fallback


def _safe_repository(value: Any) -> str:
    return value if isinstance(value, str) and _REPOSITORY.fullmatch(value) else TARGET


def _result(payload: dict[str, Any], started: str, status: str, category: str,
            message: str | None, *, branch: str | None = None, pr: str | None = None,
            validation: str = "not-run", tests: str = "not-run") -> dict[str, Any]:
    result = {
        "contract_version": "ai-sdlc-contract/v2",
        "correlation_id": _safe_identity(payload.get("correlation_id"), "rejected-correlation"),
        "delivery_id": _safe_identity(payload.get("delivery_id"), "rejected-delivery"),
        "execution_status": status,
        "target_repository": _safe_repository(payload.get("target_repository")),
        "branch_name": branch,
        "pull_request_url": pr,
        "workflow_url": os.getenv("GITHUB_SERVER_URL", "https://github.com") + "/" +
            os.getenv("GITHUB_REPOSITORY", TARGET) + "/actions/runs/" + os.getenv("GITHUB_RUN_ID", "1"),
        "validation_result": validation,
        "test_result": tests,
        "failure_category": category,
        "failure_message": message,
        "started_at": started,
        "completed_at": _now(),
    }
    schema = json.loads((ROOT / "contracts/execution-result.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(result)
    return result


def admit(raw: str, transport_group: str, caller: str, trusted_callers: set[str]) -> dict[str, Any]:
    if caller not in trusted_callers:
        raise AdapterError("authentication", "Caller is not authorized for target execution")
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        raise AdapterError("contract-validation", "Execution input is not valid JSON")
    if not isinstance(payload, dict):
        raise AdapterError("contract-validation", "Execution input must be an object")
    schema = json.loads((ROOT / "contracts/execution-input.schema.json").read_text())
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload))
    if errors:
        raise AdapterError("contract-validation", "Execution input does not conform to execution-input/v2")
    if payload["concurrency_group"] != transport_group or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,254}", transport_group):
        raise AdapterError("contract-validation", "Transport concurrency group is invalid or does not match payload")
    # Activation and route admission remain control-plane policy. The target
    # independently enforces only its immutable repository capability boundary.
    if payload["target_repository"] != TARGET:
        raise AdapterError("repository-routing", "Execution input targets a different repository")
    if payload["contract_version"] != "ai-sdlc-contract/v2":
        raise AdapterError("contract-validation", "Target does not support this contract version")
    if payload["task_type"] not in ALLOWED_TYPES:
        raise AdapterError("authorization", "Task type is not authorized for this target")
    if payload["execution_mode"] not in {"verify", "implement"} or payload["executor"] != "codex" or payload["draft_pr_only"] is not True:
        raise AdapterError("authorization", "Execution policy is not authorized")
    expected = f"codex/{payload['delivery_id'].lower()}"
    if payload["requested_branch"] not in (None, expected):
        raise AdapterError("authorization", "Requested branch contradicts delivery ownership")
    return payload


def reconcile_ownership(snapshot: Ownership, digest: str) -> dict[str, Any] | None:
    """Return one reusable managed draft or reject every ambiguous remote state."""
    owned = snapshot.pull_requests
    if snapshot.branch_exists != bool(owned):
        raise AdapterError(
            "publication",
            "Delivery branch and managed pull-request state are inconsistent",
            "ambiguous-rejected",
        )
    if any(item.get("digest") != digest for item in owned):
        raise AdapterError(
            "authorization",
            "Delivery ID is already bound to a different payload",
            "ambiguous-rejected",
        )
    if len(owned) > 1 or any(
        not item.get("draft") or item.get("state") != "OPEN" or item.get("blocked", False) for item in owned
    ):
        raise AdapterError(
            "publication",
            "Delivery ownership is ambiguous",
            "ambiguous-rejected",
        )
    return owned[0] if owned else None


def run_adapter(raw: str, transport_group: str, caller: str, trusted_callers: set[str],
                effects: Effects, *, prior_result_effect: str = "not-checked") -> Outcome:
    started, parsed, phase = _now(), {}, "admission"
    source_issue = None
    validation_status, test_status = "not-run", "not-run"
    try:
        try:
            candidate = json.loads(raw)
            if isinstance(candidate, dict):
                parsed = candidate
        except Exception:
            pass
        payload = admit(raw, transport_group, caller, trusted_callers)
        # Only an admitted issue reference may cross the workflow output boundary.
        # ``parsed`` remains useful for constructing a schema-safe rejection result,
        # but its fields are otherwise untrusted transport data.
        source_issue = payload["source_issue"]
        # The bound, authenticated result preflight must have run before any
        # target remote operation. An old pinned action emits no proof and is
        # deliberately unsafe to use after this target change.
        if prior_result_effect not in {"none", "managed-draft"}:
            raise AdapterError(
                "authorization", "Bound terminal-result preflight proof is absent or invalid",
                "ambiguous-rejected",
            )
        deadline = time.monotonic() + payload["timeout_minutes"] * 60
        def remaining() -> float:
            budget = deadline - time.monotonic()
            if budget <= 0:
                raise AdapterError("timeout", "Admitted execution timeout expired", "failed")
            return budget

        digest = canonical_digest(payload)
        branch = f"codex/{payload['delivery_id'].lower()}"
        phase = "discovery"
        ownership = effects.discover(branch, payload["delivery_id"], remaining())
        remaining()
        reusable = reconcile_ownership(ownership, digest)
        if prior_result_effect == "managed-draft" and reusable is None:
            raise AdapterError(
                "authorization", "Prior managed draft cannot be verified as an owned open draft",
                "ambiguous-rejected",
            )
        if reusable is not None:
            pr = reusable["url"]
            return Outcome(_result(payload, started, "duplicate-reused", "none", None,
                                   branch=branch, pr=pr, validation="passed", tests="passed"), payload["source_issue"])
        if payload["execution_mode"] == "verify":
            phase = "validation"
            valid, phase = effects.validate_candidate(remaining())
            remaining()
            if not valid:
                category = "tests" if phase == "tests" else "validation"
                validation_status = "passed" if phase == "tests" else "failed"
                test_status = "failed" if phase == "tests" else "not-run"
                raise AdapterError(category, "Repository did not pass policy checks", "failed")
            validation_status = test_status = "passed"
            return Outcome(_result(payload, started, "verified", "none", None,
                                   validation=validation_status, tests=test_status), source_issue)
        phase = "content-baseline"
        effects.prepare_content(payload["delivery_id"], remaining())
        remaining()
        phase = "codex"
        effects.codex(payload["instructions"], remaining())
        remaining()
        if not effects.has_candidate_changes(remaining()):
            raise AdapterError("codex-runtime", "Codex produced no candidate changes", "failed")
        phase = "validation"
        valid, phase = effects.validate_candidate(remaining())
        remaining()
        if not valid:
            category = "tests" if phase == "tests" else "validation"
            validation_status = "passed" if phase == "tests" else "failed"
            test_status = "failed" if phase == "tests" else "not-run"
            raise AdapterError(category, "Candidate did not pass repository policy", "failed")
        validation_status = test_status = "passed"
        phase = "publication"
        try:
            pr = effects.publish(branch, payload["delivery_id"], digest, remaining())
            remaining()
        except AdapterError as exc:
            if exc.safe_message == "create-race":
                ownership = effects.discover(branch, payload["delivery_id"], remaining())
                remaining()
                reusable = reconcile_ownership(ownership, digest)
                if reusable is not None:
                    effects.verify_recovered_publication(branch, reusable["url"], remaining())
                    remaining()
                    return Outcome(_result(payload, started, "duplicate-reused", "none", None,
                                           branch=branch, pr=reusable["url"], validation="passed", tests="passed"), payload["source_issue"])
                raise AdapterError(
                    "publication",
                    "Delivery ownership is ambiguous after publication create race",
                    "ambiguous-rejected",
                ) from exc
            raise
        return Outcome(_result(payload, started, "draft-pr-created", "none", None,
                               branch=branch, pr=pr, validation="passed", tests="passed"), payload["source_issue"])
    except AdapterError as exc:
        return Outcome(_result(parsed, started, exc.status, exc.category, exc.safe_message,
                               branch=exc.branch, pr=exc.pr,
                               validation=validation_status, tests=test_status), source_issue)
    except subprocess.TimeoutExpired:
        return Outcome(_result(parsed, started, "failed", "timeout", "Admitted execution timeout expired",
                               validation=validation_status, tests=test_status), source_issue)
    except Exception as exc:
        # Effect failures are deliberately classified without reflecting command,
        # API, path, token, or exception text into the externally transported result.
        if isinstance(exc, KeyError):
            category, message = "authentication", "Required execution credentials are unavailable"
        elif isinstance(exc, FileNotFoundError):
            category, message = "dependency", "Required execution dependency is unavailable"
        elif phase == "content-baseline":
            category, message = "dependency", "Exact content workbase could not be established"
        elif phase == "codex":
            category, message = "codex-runtime", "Codex execution failed"
        elif phase == "validation" or phase == "tests":
            category, message = phase, "Candidate validation could not complete"
            if phase == "validation":
                validation_status = "failed"
            else:
                validation_status, test_status = "passed", "failed"
        elif phase == "publication":
            category, message = "publication", "Draft pull request publication failed"
        else:
            category, message = "dependency", "Target execution dependency failed"
        return Outcome(_result(parsed, started, "failed", category, message,
                               validation=validation_status, tests=test_status), source_issue)


class GitHubEffects:
    def __init__(self) -> None:
        self._publication_token: str | None = None
        self._content_read_token: str | None = None
        self._content_checkout: TrustedContentCheckout | None = None
        self._publication_digest: str | None = None
        self._candidate_sha: str | None = None

    def prepare_content(self, delivery_id: str, timeout_seconds: float) -> None:
        """Attest a clean exact-SHA workbase before any cost-bearing model call."""
        if self._content_checkout is not None:
            raise AdapterError("authorization", "Task content baseline was already prepared", "ambiguous-rejected")
        deadline = time.monotonic() + timeout_seconds
        try:
            token = _take_secret("CONTENT_READ_TOKEN")
            self._content_read_token = token
            # The workflow job's contents:read token is distinct from the
            # publisher credential, and is never forwarded to the model.
            executor = subprocess.check_output(
                ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, text=True,
                timeout=remaining_time(deadline), env={k: v for k, v in os.environ.items() if k in SAFE_ENV},
            ).strip()
            authorized = os.environ.get("AUTHORIZED_EXECUTOR_SHA", "")
            if not re.fullmatch(r"[0-9a-f]{40}", authorized) or executor != authorized:
                raise BaselineError("executor differs from independently authorized release")
            base = attest_default_branch(
                TARGET, delivery_id, executor_sha=executor, token=token,
                timeout_seconds=remaining_time(deadline), deadline=deadline,
            )
            self._content_checkout = checkout_attested_base(
                base, token=token, timeout_seconds=remaining_time(deadline), deadline=deadline,
            )
            remaining_time(deadline)
        except subprocess.TimeoutExpired as exc:
            self.close()
            raise AdapterError("timeout", "Admitted execution timeout expired during content baseline", "failed") from exc
        except (KeyError, BaselineError, subprocess.CalledProcessError,
                subprocess.TimeoutExpired, OSError, ValueError) as exc:
            self.close()
            raise AdapterError(
                "dependency", "Authenticated current task-content base is unavailable", "failed"
            ) from exc

    def close(self) -> None:
        if self._content_checkout is not None:
            self._content_checkout.close()
            self._content_checkout = None
        self._content_read_token = None

    def _working_content_root(self) -> Path:
        if self._content_checkout is None:
            raise AdapterError("authorization", "Exact content workbase proof is missing", "ambiguous-rejected")
        return self._content_checkout.root

    def _publication_credential(self) -> str:
        if self._publication_token is None:
            self._publication_token = _take_secret("TARGET_PUBLICATION_TOKEN")
        return self._publication_token

    def _gh(self, *args: str, timeout_seconds: float) -> str:
        env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
        env["GH_TOKEN"] = self._publication_credential()
        return subprocess.check_output(["gh", *args], text=True, env=env, stderr=subprocess.DEVNULL,
                                       timeout=timeout_seconds)


    def _publication_git_environment(self) -> tuple[dict[str, str], str]:
        """Create a secret-free askpass helper and publication-only Git environment."""
        env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
        token = self._publication_credential()
        askpass_script = """#!/bin/sh
case "$1" in
  *Username*) printf '%s\\n' "$GIT_USERNAME" ;;
  *Password*) printf '%s\\n' "$GIT_PASSWORD" ;;
  *) printf '%s\\n' "" ;;
esac
"""
        askpass_path = os.path.join(ROOT, ".git", "ai_sdlc_askpass.sh")
        with open(askpass_path, "w", encoding="utf-8") as askpass_file:
            askpass_file.write(askpass_script)
        os.chmod(askpass_path, 0o700)
        return {
            **env,
            "GIT_ASKPASS": askpass_path,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_USERNAME": "x-access-token",
            "GIT_PASSWORD": token,
        }, askpass_path

    def discover(self, branch: str, delivery_id: str, timeout_seconds: float) -> Ownership:
        branch_names = self._gh(
            "api",
            "--paginate",
            f"repos/{TARGET}/branches?per_page=100",
            "--jq",
            ".[].name",
            timeout_seconds=timeout_seconds,
        )
        branch_exists = branch in branch_names.splitlines()
        raw = self._gh("pr", "list", "--repo", TARGET, "--state", "all", "--head", branch,
                       "--json", "url,state,isDraft,body", timeout_seconds=timeout_seconds)
        found = []
        pattern = re.compile(rf"<!--\s*{MARKER}:\s*{re.escape(delivery_id)};\s*payload-sha256:\s*([0-9a-f]{{64}})\s*-->")
        for pr in json.loads(raw):
            match = pattern.search(pr.get("body") or "")
            if match:
                found.append({"url": pr["url"], "state": pr["state"], "draft": pr["isDraft"], "digest": match.group(1),
                              "blocked": "<!-- ai-sdlc-publication-blocked:" in (pr.get("body") or "")})
            else:
                found.append({"url": pr["url"], "state": pr["state"], "draft": pr["isDraft"], "digest": "conflict"})
        return Ownership(branch_exists=branch_exists, pull_requests=found)

    def codex(self, instructions: str, timeout_seconds: float) -> None:
        workspace = self._working_content_root()
        deadline = time.monotonic() + timeout_seconds

        def budget() -> float:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired("codex", timeout_seconds)
            return remaining

        # Fail before invoking Codex unless the publication identity can use the
        # same authenticated Git transport required for the eventual branch push.
        # API permission metadata is checked first, then an actual dry-run push
        # closes the gap that previously allowed a cost-bearing Codex execution
        # to succeed before publication authentication failed.
        try:
            can_push = self._gh(
                "api",
                f"repos/{TARGET}",
                "--jq",
                ".permissions.push",
                timeout_seconds=budget(),
            ).strip()
        except subprocess.CalledProcessError as exc:
            raise AdapterError(
                "publication",
                "Publication identity readiness check failed",
                "failed",
            ) from exc
        if can_push != "true":
            raise AdapterError(
                "authorization",
                "Publication identity does not have repository write access",
                "failed",
            )

        remote = f"https://github.com/{TARGET}.git"
        run_id = os.getenv("GITHUB_RUN_ID", "local")
        run_attempt = os.getenv("GITHUB_RUN_ATTEMPT", "1")
        probe_ref = f"refs/heads/ai-sdlc-preflight-{run_id}-{run_attempt}"
        push_env, askpass_path = self._publication_git_environment()
        try:
            probe = subprocess.run(
                ["git", "push", "--dry-run", remote, f"HEAD:{probe_ref}"],
                cwd=workspace,
                env=push_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=budget(),
            )
        finally:
            try:
                os.remove(askpass_path)
            except OSError:
                pass
        if probe.returncode:
            raise AdapterError(
                "publication",
                "Publication git transport readiness check failed",
                "failed",
            )

        if not sandbox_ready(budget()):
            raise AdapterError("dependency", "Candidate test sandbox is unavailable", "failed")

        # Consume the secret before any child process is created. In
        # particular, a model-launched command must not be able to recover it
        # from this adapter's live environment via /proc.
        api_key = _take_secret("OPENAI_API_KEY")
        with isolated_codex_home(prefix="codex-target-") as codex_home:
            # Match the controlled preflight: authenticate into isolated,
            # ephemeral state over stdin and do not expose the raw key to the
            # model execution or any command it launches.
            env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
            env["CODEX_HOME"] = codex_home
            login = subprocess.run(
                ["codex", "login", "--with-api-key"],
                input=api_key,
                text=True,
                cwd=workspace,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=budget(),
            )
            api_key = ""
            if login.returncode:
                raise AdapterError("authentication", "Codex authentication failed", "failed")

            # `codex login` writes auth.json. A workspace-write sandbox may
            # read paths outside the workspace, so leaving that file present
            # would expose the API key to model-launched commands. Replace it
            # with a FIFO for each auth manager. Codex needs the prompt on
            # stdin before it starts the second manager; remove that manager's
            # FIFO as soon as it connects, before model tools can run.
            auth_path = Path(codex_home) / "auth.json"
            try:
                auth_payload = auth_path.read_bytes()
                auth_path.unlink()
                os.mkfifo(auth_path, 0o600)
            except OSError as exc:
                raise AdapterError(
                    "authentication",
                    "Codex authentication state could not be isolated",
                    "failed",
                ) from exc

            command = [
                "codex", "exec", "--model", "gpt-5.3-codex",
                "--sandbox", "workspace-write", "-C", str(workspace), "-",
            ]
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                text=True,
                cwd=workspace,
                env=env,
            )
            try:
                def submit_prompt() -> None:
                    submit_stdin_prompt(proc, instructions, budget)

                try:
                    handoff_startup_auth(auth_path, auth_payload, proc, budget, submit_prompt)
                except subprocess.TimeoutExpired as exc:
                    raise AdapterError("authentication", "Codex authentication handoff timed out", "failed") from exc
                except (OSError, RuntimeError) as exc:
                    raise AdapterError("authentication", "Codex authentication handoff failed", "failed") from exc
                auth_payload = b""
                proc.communicate(timeout=budget())
            except Exception:
                if proc.poll() is None:
                    proc.kill()
                if proc.stdin is not None:
                    proc.stdin.close()
                proc.wait()
                raise
            finally:
                try:
                    auth_path.unlink()
                except FileNotFoundError:
                    pass
        if proc.returncode:
            raise AdapterError("codex-runtime", "Codex execution failed", "failed")

    def has_candidate_changes(self, timeout_seconds: float) -> bool:
        env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
        return bool(subprocess.check_output(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=normal"],
            cwd=self._working_content_root(), env=env, timeout=timeout_seconds,
        ))

    def validate_candidate(self, timeout_seconds: float) -> tuple[bool, str]:
        # Policy validation remains pinned. Candidate-owned tests run only
        # inside the credential-free namespace sandbox on a disposable snapshot.
        env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
        deadline = time.monotonic() + timeout_seconds
        candidate = self._content_checkout.root if self._content_checkout else ROOT
        commands = [
            (["python", str(ROOT / "scripts/validate_repository.py"), "--worktree", str(candidate)],
             "validation", ROOT),
            (["git", "diff", "--check"], "validation", candidate),
        ]
        for command, phase, cwd in commands:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout_seconds)
            if subprocess.run(command, cwd=cwd, env=env, timeout=remaining).returncode:
                return False, phase
        if not run_candidate_tests(candidate, remaining_time(deadline)):
            return False, "tests"
        return True, "passed"

    def _check_content_base_head(self, phase: PublicationPhase, branch: str,
                                 timeout_seconds: float, pr: str | None = None) -> None:
        deadline = time.monotonic() + timeout_seconds
        if self._content_checkout is None or not self._content_read_token:
            raise AdapterError("authorization", "Task-content base evidence is missing",
                               "ambiguous-rejected", branch=branch, pr=pr)
        try:
            observed = attest_default_branch(
                TARGET, self._content_checkout.base.delivery_id,
                self._content_checkout.base.executor_sha,
                token=self._content_read_token, timeout_seconds=remaining_time(deadline), deadline=deadline,
            ).content_sha
            remaining_time(deadline)
        except (BaselineError, KeyError, OSError, ValueError,
                subprocess.CalledProcessError, subprocess.TimeoutExpired):
            observed = None
        decision = verify_publication_head(
            self._content_checkout.base, observed, phase,
        )
        if not decision.may_continue:
            if phase == PublicationPhase.AFTER_PR and pr:
                self._block_stale_draft(pr, branch, decision.observed_sha,
                                        timeout_seconds, deadline=deadline)
            detail = {
                PublicationDisposition.REJECT_NO_REMOTE_EFFECT:
                    "Stale or unverifiable default branch before publication; no topic push",
                PublicationDisposition.QUARANTINE_OWNED_TOPIC:
                    "Stale or unverifiable default branch after topic push; quarantine review required",
                PublicationDisposition.BLOCK_DRAFT_REVIEW:
                    "Stale or unverifiable default branch after draft creation; human review required",
            }[decision.disposition]
            raise AdapterError("publication", self._publication_failure_message(detail), "ambiguous-rejected",
                               branch=branch, pr=pr)

    def verify_recovered_publication(self, branch: str, pr: str, timeout_seconds: float) -> None:
        """A recovered create response is not proof that the draft base is current."""
        self._check_content_base_head(PublicationPhase.AFTER_PR, branch, timeout_seconds, pr=pr)

    def _block_stale_draft(self, pr: str, branch: str, observed: str | None,
                           timeout_seconds: float, *, deadline: float | None = None) -> None:
        """Persist a blocked state on the exact owned draft; never report success."""
        deadline = min(time.monotonic() + timeout_seconds, deadline) if deadline is not None else time.monotonic() + timeout_seconds
        base = self._content_checkout.base
        marker = f"<!-- {MARKER}: {base.delivery_id}; payload-sha256: {self._publication_digest} -->"
        try:
            snapshot = json.loads(self._gh(
                "pr", "view", pr, "--repo", TARGET, "--json", "body,headRefName,isDraft,state",
                timeout_seconds=remaining_time(deadline),
            ))
            remaining_time(deadline)
            body = snapshot["body"]
            if (snapshot["headRefName"] != branch or not snapshot["isDraft"]
                    or snapshot["state"] != "OPEN" or not self._publication_digest or marker not in body):
                raise ValueError("draft ownership unavailable")
            evidence = (f"<!-- ai-sdlc-publication-blocked: stale-or-unverifiable-base -->\n"
                        f"BLOCKED: default branch changed or could not be verified after publication.\n"
                        f"Executor SHA: `{base.executor_sha}`; content base SHA: `{base.content_sha}`; "
                        f"observed HEAD: `{observed or 'unverifiable'}`. Human reconciliation required.\n\n")
            self._gh("pr", "edit", pr, "--repo", TARGET, "--body", evidence + body,
                     timeout_seconds=remaining_time(deadline))
            remaining_time(deadline)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError,
                ValueError, KeyError, TypeError) as exc:
            raise AdapterError(
                "publication", self._publication_failure_message(
                    "Stale draft blocking could not be confirmed; human reconciliation required"),
                "ambiguous-rejected", branch=branch, pr=pr,
            ) from exc

    def _publication_failure_message(self, detail: str) -> str:
        # These immutable identities survive ref changes in the canonical
        # result, which is logged and forwarded to the durable source receipt.
        if not self._candidate_sha or not self._publication_digest or self._content_checkout is None:
            return detail
        base = self._content_checkout.base
        evidence = {"candidate_sha": self._candidate_sha,
                    "payload_sha256": self._publication_digest,
                    "executor_sha": base.executor_sha, "content_base_sha": base.content_sha}
        return detail + "; evidence=" + json.dumps(evidence, separators=(",", ":"))

    def _log_publication_evidence(self, stage: str, branch: str, delivery_id: str) -> None:
        # Record push intent and completion independently of mutable branch refs.
        # No credentials or task instructions enter the workflow log.
        base = self._content_checkout.base
        print(json.dumps({"publication_evidence": {
            "stage": stage, "repository": TARGET, "branch": branch,
            "delivery_id": delivery_id, "payload_sha256": self._publication_digest,
            "executor_sha": base.executor_sha, "content_base_sha": base.content_sha,
            "candidate_sha": self._candidate_sha,
        }}, sort_keys=True), flush=True)

    def _reconcile_timed_out_push(self, branch: str, delivery_id: str, deadline: float) -> AdapterError:
        observation = "unverified"
        try:
            raw = self._gh("api", f"repos/{TARGET}/git/ref/heads/{branch}",
                           timeout_seconds=remaining_time(deadline))
            remaining_time(deadline)
            remote = json.loads(raw)
            if (remote.get("ref") == "refs/heads/" + branch
                    and remote.get("object", {}).get("type") == "commit"):
                observation = "exact-candidate" if remote["object"].get("sha") == self._candidate_sha else "different-object"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError,
                ValueError, TypeError, KeyError, AttributeError):
            pass
        self._log_publication_evidence("push-timeout-" + observation, branch, delivery_id)
        return AdapterError(
            "publication", self._publication_failure_message(
                "Push timed out; remote=" + observation + "; human reconciliation required"),
            "ambiguous-rejected", branch=branch,
        )

    def publish(self, branch: str, delivery_id: str, digest: str, timeout_seconds: float) -> str:
        self._publication_digest = digest
        workspace = self._working_content_root()
        env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_TERMINAL_PROMPT="0")
        deadline = time.monotonic() + timeout_seconds
        def budget() -> float:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired("publication", timeout_seconds)
            return remaining

        subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "checkout", "-b", branch], check=True, cwd=workspace, env=env, timeout=budget())
        subprocess.run(["git", "add", "-A"], check=True, cwd=workspace, env=env, timeout=budget())
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=workspace, env=env,
                          timeout=budget()).returncode == 0:
            raise AdapterError("codex-runtime", "Codex produced no candidate changes", "failed")
        subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                        "-c", "user.name=ai-sdlc-target", "-c",
                        "user.email=ai-sdlc@users.noreply.github.com", "commit", "-m", f"AI-SDLC delivery {delivery_id}"], check=True, cwd=workspace, env=env,
                       timeout=budget())
        self._candidate_sha = subprocess.check_output(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=workspace, env=env,
            text=True, timeout=budget(),
        ).strip()
        if not re.fullmatch(r"[0-9a-f]{40}", self._candidate_sha):
            raise AdapterError("publication", "Candidate commit identity is invalid", "ambiguous-rejected", branch=branch)
        parent = subprocess.check_output(
            ["git", "rev-parse", self._candidate_sha + "^"], cwd=workspace, env=env,
            text=True, timeout=budget(),
        ).strip()
        if parent != self._content_checkout.base.content_sha:
            raise AdapterError("publication", "Candidate parent does not match attested content",
                               "ambiguous-rejected", branch=branch)
        self._check_content_base_head(PublicationPhase.BEFORE_PUSH, branch, budget())
        remote = f"https://github.com/{TARGET}.git"
        push_env, askpass_path = self._publication_git_environment()
        self._log_publication_evidence("push-intent", branch, delivery_id)
        try:
            pushed = subprocess.run(
                ["git", "push", remote, f"{self._candidate_sha}:refs/heads/{branch}"],
                cwd=workspace,
                env=push_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=budget() * 0.8,
            )
        except subprocess.TimeoutExpired as exc:
            raise self._reconcile_timed_out_push(branch, delivery_id, deadline) from exc
        finally:
            try:
                os.remove(askpass_path)
            except OSError:
                pass
        if pushed.returncode:
            stderr_text = (pushed.stderr or b"").decode("utf-8", errors="replace").lower()
            if "non-fast-forward" in stderr_text or "fetch first" in stderr_text:
                raise AdapterError("publication", "create-race")
            raise AdapterError(
                "publication",
                "Draft branch publication failed",
                "failed",
            )
        self._log_publication_evidence("push-completed", branch, delivery_id)
        self._check_content_base_head(PublicationPhase.AFTER_PUSH_BEFORE_PR,
                                      branch, budget())
        base = self._content_checkout.base
        body = (f"<!-- {MARKER}: {delivery_id}; payload-sha256: {digest} -->\n"
                f"<!-- ai-sdlc-provenance: executor-sha: {base.executor_sha}; content-base-sha: {base.content_sha}; candidate-sha: {self._candidate_sha} -->\n\n"
                f"Executor SHA: `{base.executor_sha}`\nContent base SHA: `{base.content_sha}`\n\n"
                "Automated draft; human review and merge are required. Reverify default-branch HEAD before marking ready.")
        # The commit is already durable on the remote branch. Retry only PR
        # creation so a transient GitHub CLI/API failure cannot strand that
        # branch and make every later delivery attempt fail its non-force push.
        for attempt in range(3):
            try:
                pr = self._gh("pr", "create", "--repo", TARGET, "--draft", "--head", branch, "--title",
                              f"AI-SDLC delivery {delivery_id}", "--body", body,
                              timeout_seconds=budget()).strip()
                self._check_content_base_head(PublicationPhase.AFTER_PR,
                                              branch, budget(), pr=pr)
                return pr
            except subprocess.CalledProcessError:
                if attempt == 2:
                    raise AdapterError("publication", "create-race")
        raise AssertionError("unreachable")


def main() -> int:
    _bootstrap_secret_environment()
    raw = os.environ.get("EXECUTION_INPUT_JSON", "")
    trusted_callers = {
        value.strip()
        for value in _take_optional_secret("TRUSTED_CALLERS").split(",")
        if value.strip()
    }
    effects = GitHubEffects()
    try:
        outcome = run_adapter(raw, os.environ.get("CONCURRENCY_GROUP", ""), os.environ.get("CALLER_LOGIN", ""),
                              trusted_callers, effects,
                              prior_result_effect=os.environ.get("PRIOR_RESULT_EFFECT", "not-checked"))
    finally:
        effects.close()
    output = json.dumps(outcome.result, sort_keys=True, separators=(",", ":"))
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        safe_issue = (outcome.source_issue or "").replace("\r", "").replace("\n", " ").strip()
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"execution_result={output}\nsource_issue={safe_issue}\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
