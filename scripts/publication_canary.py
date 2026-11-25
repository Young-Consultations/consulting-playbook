"""Offline-only publication canary model. No network, subprocess or credentials.

The model cannot issue readiness evidence. A separately reviewed live transport
and protected authorization are required before any real publication.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re

TARGET = "Young-Consultations/consulting-playbook"
ENVIRONMENT = "consulting-playbook-codex"
RECEIVER = "ai-sdlc-v5.0.0"


class Blocked(ValueError):
    pass


@dataclass(frozen=True)
class Plan:
    run_id: str
    executor_sha: str
    control_plane_sha: str
    base_sha: str
    policy_revision: str

    def __post_init__(self):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", self.run_id):
            raise Blocked("invalid canary identity")
        if any(not re.fullmatch(r"[0-9a-f]{40}", v) for v in
               (self.executor_sha, self.control_plane_sha, self.base_sha)):
            raise Blocked("missing immutable binding")
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", self.policy_revision):
            raise Blocked("invalid policy revision")

    @property
    def branch(self):
        return "ai-sdlc-canary/" + self.run_id

    @property
    def marker(self):
        return json.dumps({"repository": TARGET, "environment": ENVIRONMENT,
                           "receiver": RECEIVER, **self.__dict__},
                          sort_keys=True, separators=(",", ":")) + "\n"

    @property
    def marker_digest(self):
        return sha256(self.marker.encode()).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    # An observed branch is represented by its verified ownership marker digest.
    branch_digest: str | None = None
    # Each PR is (marker digest, is_open, is_draft, exact head/base binding verified).
    prs: tuple = ()
    readable: bool = True


def next_action(plan, snapshot):
    """A pure decision: never create a second PR or overwrite an existing ref."""
    if not snapshot.readable:
        raise Blocked("publication evidence unavailable")
    if snapshot.branch_digest not in (None, plan.marker_digest):
        raise Blocked("branch ownership conflict")
    if len(snapshot.prs) > 1:
        raise Blocked("ambiguous PR ownership")
    if snapshot.prs:
        if snapshot.branch_digest != plan.marker_digest or snapshot.prs[0] != (
                plan.marker_digest, True, True, True):
            raise Blocked("PR ownership or draft binding conflict")
        return "verified-reuse"
    return "create-draft" if snapshot.branch_digest else "push-branch"


def simulate(plan, snapshot=Snapshot(), *, permission=True, dry_run=True,
             push_outcome="success", pr_outcome="success", ambiguous_snapshot=None):
    """Deterministic in-memory effects only; no real transport or secret handling."""
    counts = {"fake_push": 0, "fake_pr": 0, "model_calls": 0,
              "real_external_effects": 0, "cleanup": 0, "merge": 0}
    result = {"simulation": True, "readiness_eligible": False, "counts": counts}
    try:
        action = next_action(plan, snapshot)
        if action == "verified-reuse":
            return dict(result, status=action, snapshot=snapshot)
        if not permission or not dry_run:
            raise Blocked("publisher or transport prerequisite denied")
        if action == "push-branch":
            counts["fake_push"] += 1
            if push_outcome != "success":
                raise Blocked("push denied or uncertain; reconcile before rerun")
            snapshot = Snapshot(plan.marker_digest)
        counts["fake_pr"] += 1
        if pr_outcome == "ambiguous":
            # One readback, never another mutation on uncertainty.
            if ambiguous_snapshot is None or next_action(plan, ambiguous_snapshot) != "verified-reuse":
                raise Blocked("PR creation uncertain; operator reconciliation required")
            snapshot = ambiguous_snapshot
        elif pr_outcome == "success":
            snapshot = Snapshot(plan.marker_digest, ((plan.marker_digest, True, True, True),))
        else:
            raise Blocked("PR creation denied; stop")
        return dict(result, status="simulated-draft-verified", snapshot=snapshot)
    except Blocked as exc:
        return dict(result, status="blocked", reason=str(exc), snapshot=snapshot)
