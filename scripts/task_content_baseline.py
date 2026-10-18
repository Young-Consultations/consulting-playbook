#!/usr/bin/env python3
"""Exact-SHA task workbase provenance and non-atomic publication guards.

This module is trust-boundary logic, not permission to run REAL. A separate
adapter/worktree integration and security review must invoke the guards.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

_SHA = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"Young-Consultations/[A-Za-z0-9._-]+\Z")
_BRANCH = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,200}\Z")
_IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


class BaselineError(ValueError):
    """Untrusted or ambiguous workbase identity; no Codex authorization."""


@dataclass(frozen=True)
class TaskBase:
    repository: str
    default_branch: str
    content_sha: str
    executor_sha: str
    delivery_id: str

    @classmethod
    def from_github(
        cls, *,
        repository: str,
        delivery_id: str,
        executor_sha: str,
        repo_response: dict[str, Any],
        branch_response: dict[str, Any],
    ) -> "TaskBase":
        """Bind two read-only GitHub responses to exact target/branch/SHA.

        The adapter must authenticate the read transport and separately fetch
        this exact SHA into an isolated, clean content checkout.
        """
        if _REPO.fullmatch(repository) is None:
            raise BaselineError("target repository is not authorized")
        if _IDENTITY.fullmatch(delivery_id) is None:
            raise BaselineError("delivery identity is invalid")
        if _SHA.fullmatch(executor_sha) is None:
            raise BaselineError("trusted executor SHA is not immutable")
        if not isinstance(repo_response, dict) or repo_response.get("full_name") != repository:
            raise BaselineError("GitHub repository identity does not match target")
        branch = repo_response.get("default_branch")
        if not isinstance(branch, str) or _BRANCH.fullmatch(branch) is None:
            raise BaselineError("default branch identity is invalid")
        if branch.startswith("/") or ".." in branch or branch.endswith("/") or "//" in branch:
            raise BaselineError("default branch ref contains an unsafe segment")
        if not isinstance(branch_response, dict) or branch_response.get("name") != branch:
            raise BaselineError("default branch evidence does not match repository")
        commit = branch_response.get("commit")
        sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(sha, str) or _SHA.fullmatch(sha) is None:
            raise BaselineError("default branch evidence lacks exact commit SHA")
        return cls(repository, branch, sha, executor_sha, delivery_id)


class PublicationPhase(str, Enum):
    BEFORE_PUSH = "before-push"
    AFTER_PUSH_BEFORE_PR = "after-push-before-pr"
    AFTER_PR = "after-pr"


class PublicationDisposition(str, Enum):
    READY = "ready"
    REJECT_NO_REMOTE_EFFECT = "reject-no-remote-effect"
    QUARANTINE_OWNED_TOPIC = "quarantine-owned-topic"
    BLOCK_DRAFT_REVIEW = "block-draft-review"


@dataclass(frozen=True)
class PublicationDecision:
    disposition: PublicationDisposition
    phase: PublicationPhase
    base_sha: str
    observed_sha: str

    @property
    def may_continue(self) -> bool:
        return self.disposition == PublicationDisposition.READY


def verify_publication_head(
    base: TaskBase,
    observed_head_sha: str,
    phase: PublicationPhase,
) -> PublicationDecision:
    """Pure guard; caller must enforce the returned disposition.

    A read in any phase cannot atomically lock a different GitHub ref.
    After-push branches and after-PR drafts may exist, must be recorded
    against the original delivery, and must never be auto-reused for Codex.
    """
    if not isinstance(phase, PublicationPhase):
        raise BaselineError("unknown publication phase")
    if not isinstance(observed_head_sha, str) or _SHA.fullmatch(observed_head_sha) is None:
        raise BaselineError("current default HEAD is not independently verifiable")
    if observed_head_sha == base.content_sha:
        return PublicationDecision(PublicationDisposition.READY, phase, base.content_sha, observed_head_sha)
    disposition = {
        PublicationPhase.BEFORE_PUSH: PublicationDisposition.REJECT_NO_REMOTE_EFFECT,
        PublicationPhase.AFTER_PUSH_BEFORE_PR: PublicationDisposition.QUARANTINE_OWNED_TOPIC,
        PublicationPhase.AFTER_PR: PublicationDisposition.BLOCK_DRAFT_REVIEW,
    }[phase]
    return PublicationDecision(disposition, phase, base.content_sha, observed_head_sha)


def require_exact_content_checkout(base: TaskBase, checkout_head_sha: str, dirty: bool) -> None:
    """Fail before the model if content checkout provenance differs."""
    if not isinstance(checkout_head_sha, str) or _SHA.fullmatch(checkout_head_sha) is None:
        raise BaselineError("content worktree commit cannot be authenticated")
    if checkout_head_sha != base.content_sha or dirty is not False:
        raise BaselineError("content worktree is stale or unclean")
