#!/usr/bin/env python3
"""Fail-closed idempotent publication preflight for the target repository."""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

DELIVERY_MARKER_PREFIX = "<!-- ai-sdlc-delivery-id: "
DIGEST_MARKER_PREFIX = "<!-- ai-sdlc-payload-sha256: "
MARKER_SUFFIX = " -->"
METADATA_FIELDS = ("delivery_id", "payload_digest", "target_repository", "branch", "source_issue")


class GitHubAPI(Protocol):
    def branch_exists(self, repository: str, branch: str) -> bool: ...
    def pull_requests(self, repository: str, branch: str) -> list[dict[str, Any]]: ...
    def create_draft(self, repository: str, branch: str, title: str, body: str) -> str: ...


@dataclass(frozen=True)
class Decision:
    state: str
    terminal_status: str
    pr_url: str = ""
    failure_category: str = ""
    message: str = ""


def marker(metadata: dict[str, str]) -> str:
    return (f"{DELIVERY_MARKER_PREFIX}{metadata['delivery_id']}{MARKER_SUFFIX}\n"
            f"{DIGEST_MARKER_PREFIX}{metadata['payload_digest']}{MARKER_SUFFIX}")


def parse_marker(body: str) -> dict[str, Any] | None:
    deliveries = [line for line in body.splitlines() if line.startswith(DELIVERY_MARKER_PREFIX)]
    digests = [line for line in body.splitlines() if line.startswith(DIGEST_MARKER_PREFIX)]
    if len(deliveries) != 1 or len(digests) != 1:
        return None
    if not deliveries[0].endswith(MARKER_SUFFIX) or not digests[0].endswith(MARKER_SUFFIX):
        return None
    return {
        "delivery_id": deliveries[0][len(DELIVERY_MARKER_PREFIX):-len(MARKER_SUFFIX)],
        "payload_digest": digests[0][len(DIGEST_MARKER_PREFIX):-len(MARKER_SUFFIX)],
    }


def classify(api: GitHubAPI, metadata: dict[str, str]) -> Decision:
    repository, branch = metadata["target_repository"], metadata["branch"]
    branch_exists = api.branch_exists(repository, branch)
    prs = api.pull_requests(repository, branch)
    matching, conflicting = [], []
    for pr in prs:
        parsed = parse_marker(str(pr.get("body") or ""))
        expected = {"delivery_id": metadata["delivery_id"], "payload_digest": metadata["payload_digest"]}
        (matching if parsed == expected else conflicting).append(pr)
    if conflicting:
        return Decision("ambiguous", "blocked", failure_category="publication_ambiguous", message="conflicting or invalid publication ownership marker")
    open_prs = [pr for pr in matching if str(pr.get("state", "")).upper() == "OPEN"]
    closed_prs = [pr for pr in matching if str(pr.get("state", "")).upper() != "OPEN"]
    if closed_prs:
        return Decision("blocked", "blocked", failure_category="manual_recovery_required", message="a prior managed pull request is closed or merged")
    if len(open_prs) > 1:
        return Decision("ambiguous", "blocked", failure_category="publication_ambiguous", message="multiple managed open pull requests exist")
    if len(open_prs) == 1:
        pr = open_prs[0]
        if not branch_exists or not pr.get("isDraft", False):
            return Decision("blocked", "blocked", failure_category="publication_policy_violation", message="managed publication is not an open draft with a remote branch")
        return Decision("reuse-completed-delivery", "reused", str(pr.get("url") or ""), message="reused existing managed draft publication")
    if branch_exists:
        return Decision("blocked", "blocked", failure_category="orphaned_branch", message="deterministic branch exists without a managed pull request")
    return Decision("new-delivery", "ready")


class GhAPI:
    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(("gh", *args), text=True, capture_output=True, check=check)

    def branch_exists(self, repository: str, branch: str) -> bool:
        result = self._run("api", f"repos/{repository}/git/ref/heads/{branch}", check=False)
        if result.returncode not in (0, 1):
            raise RuntimeError("GitHub branch query failed")
        return result.returncode == 0

    def pull_requests(self, repository: str, branch: str) -> list[dict[str, Any]]:
        result = self._run("pr", "list", "--repo", repository, "--state", "all", "--head", branch,
                           "--json", "url,state,isDraft,body")
        value = json.loads(result.stdout)
        if not isinstance(value, list):
            raise RuntimeError("GitHub pull request query returned malformed data")
        return value

    def create_draft(self, repository: str, branch: str, title: str, body: str) -> str:
        result = self._run("pr", "create", "--repo", repository, "--base", "main", "--head", branch,
                           "--draft", "--title", title, "--body", body)
        return result.stdout.strip()


def load_metadata(path: str) -> dict[str, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    metadata = {name: payload.get(name) for name in METADATA_FIELDS}
    if any(not isinstance(value, str) or not value for value in metadata.values()):
        raise ValueError("publication metadata is incomplete")
    return metadata  # type: ignore[return-value]


def emit(decision: Decision, output: str | None) -> None:
    values = decision.__dict__
    print(json.dumps(values, sort_keys=True))
    if output:
        with Path(output).open("a", encoding="utf-8") as stream:
            for key, value in values.items():
                stream.write(f"{key}={str(value).replace(chr(10), ' ')}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "publish"))
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--github-output")
    parser.add_argument("--title", default="Consulting: managed Codex delivery")
    parser.add_argument("--branch-created", action="store_true", help="this invocation just created the remote branch")
    args = parser.parse_args()
    metadata = load_metadata(args.metadata)
    api = GhAPI()
    decision = classify(api, metadata)
    safe_to_create = decision.state == "new-delivery" or (
        args.branch_created and decision.failure_category == "orphaned_branch"
    )
    if args.command == "publish" and safe_to_create:
        body = f"Automated implementation of {metadata['source_issue']}. Human review is required.\n\n{marker(metadata)}"
        try:
            api.create_draft(metadata["target_repository"], metadata["branch"], args.title, body)
        except subprocess.CalledProcessError:
            pass  # A competing creator may have won; re-query without sleeping.
        decision = classify(api, metadata)
    emit(decision, args.github_output)
    if decision.state in {"ambiguous", "blocked", "new-delivery"} and args.command == "publish":
        raise SystemExit(1)
    if decision.state in {"ambiguous", "blocked"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
