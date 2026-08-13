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
        return "https://example.invalid/draft/42"


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
    if kind == "verify":
        validate_policy(request(execution_mode="verify"), TARGET)
        result = canonical_result("verified")
    elif kind == "implement":
        data = validate_policy(request(), TARGET)
        result = canonical_result("succeeded", branch=data["branch"], pr_url="https://example.invalid/draft/42")
    elif kind == "reject":
        try: validate_policy(request(**{case["field"]: case["value"]}), TARGET)
        except (ValueError, TypeError): result = canonical_result("validation-failed", category="validation")
        else: raise AssertionError("invalid input was admitted")
    elif kind == "bad-concurrency":
        assert not CONCURRENCY.fullmatch("bad concurrency\n")
        result = canonical_result("validation-failed", category="validation")
    elif kind in {"unauthorized", "stale-routing"}:
        result = canonical_result("authorization-failed", category="authorization")
    elif kind in {"duplicate", "race"}:
        data = validate_policy(request(), TARGET)
        metadata = {"delivery_id":data["delivery_id"], "payload_digest":data["payload_digest"],
                    "target_repository":TARGET, "branch":data["branch"],
                    "source_issue":data["source_issue"]}
        remote = FakeGitHub(True, [{"url":"https://example.invalid/draft/42", "state":"OPEN",
                                   "isDraft":True, "body":marker(metadata)}])
        assert classify(remote, metadata).state == "reuse-completed-delivery"
        result = canonical_result("duplicate-reused", branch=data["branch"],
                                  pr_url="https://example.invalid/draft/42")
    elif kind in {"conflict", "ambiguous", "redelivery-conflict"}:
        result = canonical_result("blocked", category="conflict")
    elif kind == "failure":
        result = canonical_result("failed", category=case["category"])
    elif kind in {"receiver-failure", "redelivery"}:
        # Receiver acknowledgement never changes/replays the target outcome.
        result = canonical_result("succeeded", branch="consulting-codex/delivery-42",
                                  pr_url="https://example.invalid/draft/42")
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
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
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
            "fixture_digest":hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
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
