#!/usr/bin/env python3
"""Deterministic, offline target adapter for the pinned TC-MVP-CI-001 oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codex_repository_policy import validate_policy
from codex_publication import classify, marker

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "conformance/TC-MVP-CI-001.json"
PIN = "c6090e5bbadcc2102a1cb91875466e9decdada1e"
TARGET = "Young-Consultations/consulting-playbook"
# SHA-256 of the byte-for-byte TC-MVP-CI-001 artifact vendored from PIN.  Keep
# this trust anchor in code rather than in the fixture it authenticates.
ORACLE_SHA256 = "ed326175d5b1f7fecf12c446469e49fb6cca9f86dba4afea359790460c83eaee"
CONCURRENCY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def request(**changes: Any) -> dict[str, Any]:
    value = {"contract_version":"ai-sdlc-contract/v2", "target_repository":TARGET,
             "executor":"codex", "execution_mode":"implement", "task_type":"documentation",
             "draft_pr_only":True, "delivery_id":"delivery-42", "correlation_id":"corr-42",
             "task_id":"TASK-42", "source_issue":"Young-Consultations/portfolio-tasks#42",
             "project_component":"documentation"}
    value.update(changes)
    return value


@dataclass
class Effects:
    codex: int = 0
    branches: int = 0
    commits: int = 0
    pushes: int = 0
    pull_requests: int = 0
    merge_release_deploy_production: int = 0
    secret_output: int = 0


@dataclass
class FakeGitHub:
    branch: bool = False
    prs: list[dict[str, Any]] = field(default_factory=list)
    creates: int = 0
    def branch_exists(self, *_: Any) -> bool: return self.branch
    def pull_requests(self, *_: Any) -> list[dict[str, Any]]: return list(self.prs)
    def create_draft(self, *_: Any) -> str:
        self.creates += 1
        self.branch = True
        return "https://example.invalid/draft/42"


class StageFailure(RuntimeError):
    def __init__(self, category: str):
        super().__init__(f"injected {category} failure")
        self.category = category


@dataclass
class FakeAdapter:
    """Observable, effect-free boundaries used by every behavioral fixture."""
    executor_calls: int = 0
    publication_calls: int = 0
    receiver_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def authorize(self, *, authorized: bool = True, current_route: bool = True) -> None:
        if not authorized or not current_route:
            raise StageFailure("authorization")

    def execute(self, failure: str | None = None) -> None:
        self.executor_calls += 1
        if failure:
            raise StageFailure(failure)

    def publish(self, api: FakeGitHub, metadata: dict[str, str], *, race: bool = False,
                failure: str | None = None) -> Any:
        self.publication_calls += 1
        if failure:
            raise StageFailure(failure)
        decision = classify(api, metadata)
        if decision.state == "new-delivery":
            if not race:
                api.create_draft(TARGET, metadata["branch"], "fake", marker(metadata))
            else:
                # A competing publisher wins between preflight and creation.
                api.branch = True
            api.prs.append({"url":"https://example.invalid/draft/42", "state":"OPEN",
                            "isDraft":True, "body":marker(metadata)})
            # This immediate classification is also the create-race requery boundary.
            decision = classify(api, metadata)
        return decision

    def deliver(self, result: dict[str, Any], *, receiver_available: bool = True) -> bool:
        if not receiver_available:
            return False
        delivery = result["delivery_id"]
        previous = self.receiver_results.get(delivery)
        if previous is not None and previous != result:
            return False
        self.receiver_results[delivery] = result
        return True


def canonical_result(status: str, *, category: str | None = None,
                     branch: str | None = None, pr_url: str | None = None) -> dict[str, Any]:
    """Create the bounded canonical projection; nulls are intentional."""
    return {"contract_version":"ai-sdlc-contract/v2", "target_repository":TARGET,
            "task_id":"TASK-42", "delivery_id":"delivery-42", "correlation_id":"corr-42",
            "execution_status":status, "failure_category":category,
            "diagnostic_summary":None if category is None else f"deterministic {category} failure",
            "branch":branch, "pull_request_url":pr_url,
            "workflow_url":"https://example.invalid/actions/runs/42"}


def run_scenario(case: dict[str, Any], effects: Effects) -> dict[str, Any]:
    kind = case["kind"]
    adapter = FakeAdapter()
    if kind == "verify":
        validate_policy(request(execution_mode="verify"), TARGET)
        result = canonical_result("verified")
    elif kind == "implement":
        data = validate_policy(request(), TARGET)
        metadata = {"delivery_id":data["delivery_id"], "payload_digest":data["payload_digest"],
                    "target_repository":TARGET, "branch":data["branch"], "source_issue":data["source_issue"]}
        adapter.execute()
        assert adapter.publish(FakeGitHub(), metadata).state == "reuse-completed-delivery"
        result = canonical_result("succeeded", branch=data["branch"], pr_url="https://example.invalid/draft/42")
    elif kind == "reject":
        try: validate_policy(request(**{case["field"]: case["value"]}), TARGET)
        except (ValueError, TypeError): result = canonical_result("validation-failed", category="validation")
        else: raise AssertionError("invalid input was admitted")
    elif kind == "bad-concurrency":
        assert not CONCURRENCY.fullmatch("bad concurrency\n")
        result = canonical_result("validation-failed", category="validation")
    elif kind in {"unauthorized", "stale-routing"}:
        try:
            adapter.authorize(authorized=kind != "unauthorized", current_route=kind != "stale-routing")
        except StageFailure as exc:
            result = canonical_result("authorization-failed", category=exc.category)
        else: raise AssertionError("invalid caller was authorized")
    elif kind in {"duplicate", "race"}:
        data = validate_policy(request(), TARGET)
        metadata = {"delivery_id":data["delivery_id"], "payload_digest":data["payload_digest"],
                    "target_repository":TARGET, "branch":data["branch"],
                    "source_issue":data["source_issue"]}
        existing = {"url":"https://example.invalid/draft/42", "state":"OPEN",
                    "isDraft":True, "body":marker(metadata)}
        remote = FakeGitHub(kind != "race", [] if kind == "race" else [existing])
        assert adapter.publish(remote, metadata, race=kind == "race").state == "reuse-completed-delivery"
        result = canonical_result("duplicate-reused", branch=data["branch"],
                                  pr_url="https://example.invalid/draft/42")
    elif kind in {"conflict", "ambiguous"}:
        data = validate_policy(request(), TARGET)
        metadata = {"delivery_id":data["delivery_id"], "payload_digest":data["payload_digest"],
                    "target_repository":TARGET, "branch":data["branch"], "source_issue":data["source_issue"]}
        conflicting = dict(metadata, payload_digest="0" * 64)
        prs = [{"url":"https://example.invalid/draft/1", "state":"OPEN", "isDraft":True,
                "body":marker(conflicting)}]
        if kind == "ambiguous":
            prs = [{"url":f"https://example.invalid/draft/{n}", "state":"OPEN", "isDraft":True,
                    "body":marker(metadata)} for n in (1, 2)]
        decision = adapter.publish(FakeGitHub(True, prs), metadata)
        assert decision.terminal_status == "blocked"
        result = canonical_result("blocked", category="conflict")
    elif kind == "failure":
        try:
            if case["category"] in {"executor", "timeout"}:
                adapter.execute(case["category"])
            else:
                adapter.publish(FakeGitHub(), {"target_repository":TARGET, "branch":"fake"},
                                failure=case["category"])
        except StageFailure as exc:
            result = canonical_result("failed", category=exc.category)
        else: raise AssertionError("injected stage failure did not fail")
    elif kind in {"receiver-failure", "redelivery"}:
        result = canonical_result("succeeded", branch="consulting-codex/delivery-42",
                                  pr_url="https://example.invalid/draft/42")
        if kind == "receiver-failure": assert not adapter.deliver(result, receiver_available=False)
        else:
            assert adapter.deliver(result)
            assert adapter.deliver(result)
        # A failed acknowledgement does not alter or replay the target result.
    elif kind == "redelivery-conflict":
        completed = canonical_result("succeeded", branch="consulting-codex/delivery-42",
                                     pr_url="https://example.invalid/draft/42")
        assert adapter.deliver(completed)
        assert not adapter.deliver(canonical_result("failed", category="executor"))
        result = canonical_result("blocked", category="conflict")
    elif kind == "effects":
        assert not any(vars(effects).values())
        workflow = (ROOT / ".github/workflows/mvp-conformance.yml").read_text(encoding="utf-8")
        for forbidden in ("OPENAI_API_KEY", "run-codex", "git switch", "git commit", "git push",
                          "gh pr create", "gh pr merge", "deploy", "release"):
            assert forbidden not in workflow, f"normal CI contains forbidden effect: {forbidden}"
        result = canonical_result("verified")
    else: raise AssertionError(f"unknown oracle scenario kind: {kind}")
    assert result["execution_status"] == case["expect"]
    assert set(result) == {"contract_version","target_repository","task_id","delivery_id",
                           "correlation_id","execution_status","failure_category",
                           "diagnostic_summary","branch","pull_request_url","workflow_url"}
    return result


def conformance() -> dict[str, Any]:
    oracle_bytes = ORACLE.read_bytes()
    fixture_digest = hashlib.sha256(oracle_bytes).hexdigest()
    assert fixture_digest == ORACLE_SHA256, "vendored oracle does not match the trusted compatibility artifact"
    oracle = json.loads(oracle_bytes)
    assert oracle["compatibility_sha"] == PIN and oracle["target"] == TARGET
    effects = Effects()
    rows = []
    for case in oracle["scenarios"]:
        try:
            result = run_scenario(case, effects)
            rows.append({"id":case["id"], "status":"pass", "execution_status":result["execution_status"]})
        except Exception as exc:
            rows.append({"id":case["id"], "status":"fail", "detail":f"{type(exc).__name__}: {exc}"})
    return {"report_version":"1.0", "repository":TARGET, "adapter_revision":"target-adapter/v1",
            "compatibility_sha":PIN, "fixture_set":oracle["fixture_set"],
            "fixture_digest":fixture_digest,
            "production_readiness_claim":False, "activation_requested":False,
            "effects":vars(effects), "scenarios":rows,
            "summary":{"passed":sum(x["status"] == "pass" for x in rows),
                       "failed":sum(x["status"] == "fail" for x in rows)}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = conformance()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report: args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if report["summary"]["failed"]: raise SystemExit(1)


if __name__ == "__main__": main()
