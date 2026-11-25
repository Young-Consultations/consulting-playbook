"""Run the real canary orchestration against an in-memory GitHub API."""
import base64
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import unquote

from publication_canary_transport import (
    ADAPTER_TAG, Blocked, C, GitHub, RECEIVER, T, TARGET, WORKFLOW,
    authorization, body, marker_path, run, title,
)

EXEC = "a" * 40
CONTROL = "b" * 40
BASE = "c" * 40
TREE = "d" * 40
HEAD = "e" * 40
NEW_TREE = "f" * 40
OWNER = "synthetic-owner"
PUBLISHER = "synthetic-publisher"
URL = "https://github.com/" + TARGET + "/pull/7"


def env():
    return {
        "GITHUB_REPOSITORY": TARGET, "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/tags/" + ADAPTER_TAG, "GITHUB_WORKFLOW_REF": WORKFLOW,
        "GITHUB_RUN_ATTEMPT": "1", "GITHUB_SHA": EXEC, "GITHUB_WORKFLOW_SHA": EXEC,
        "GITHUB_ACTOR": OWNER, "GITHUB_TRIGGERING_ACTOR": OWNER, "CANARY_APPROVER": OWNER,
        "CANARY_PUBLISHER": PUBLISHER, "CANARY_ID": "test-1", "CANARY_BASE_SHA": BASE,
        "AUTHORIZED_CONTROL_PLANE_SHA": CONTROL, "PUBLICATION_POLICY_REVISION": "1",
        "CANARY_CONFIRMATION": "publish-one-draft",
        "CANARY_AUTHORIZATION": ":".join(("automation-safe", "test-1", EXEC, CONTROL, BASE, "1", PUBLISHER)),
    }


def b64(value):
    if isinstance(value, dict):
        value = json.dumps(value)
    return {"encoding": "base64", "content": base64.b64encode(value.encode()).decode()}


class Fake:
    def __init__(self, plan):
        self.plan = plan
        self.head = None
        self.pr = None
        self.posts = []
        self.reads = []
        self.permission = True
        self.control_sha = CONTROL
        self.adapter_sha = EXEC
        self.main_sha = BASE
        self.publisher = PUBLISHER
        self.ref_error = False
        self.pr_error = None
        self.foreign_marker = False
        self.unreadable = False
        self.registry_sha = EXEC
        self.base_marker = False
        self.ref = "refs/heads/" + plan.branch

    def ref_value(self, sha, ref=None):
        return {"ref": ref or self.ref, "object": {"type": "commit", "sha": sha}}

    def draft(self):
        return {"number": 7, "html_url": URL, "state": "open", "draft": True,
                "user": {"login": PUBLISHER}, "title": title(self.plan), "body": body(self.plan),
                "head": {"repo": {"full_name": TARGET}, "ref": self.plan.branch, "sha": HEAD},
                "base": {"repo": {"full_name": TARGET}, "ref": "main", "sha": BASE}}

    def call(self, method, path, data=None):
        if method == "POST":
            self.posts.append((path, data))
            if path == T + "/git/trees":
                assert data["base_tree"] == TREE
                assert data["tree"] == [{"path": marker_path(self.plan), "mode": "100644",
                                         "type": "blob", "content": self.plan.marker}]
                return {"sha": NEW_TREE}
            if path == T + "/git/commits":
                assert data["parents"] == [BASE] and data["tree"] == NEW_TREE
                return {"sha": HEAD}
            if path == T + "/git/refs":
                assert self.head is None and data == {"ref": self.ref, "sha": HEAD}
                self.head = HEAD
                if self.ref_error:
                    raise Blocked("uncertain ref creation")
                return self.ref_value(HEAD)
            if path == T + "/pulls":
                assert data == {"title": title(self.plan), "body": body(self.plan),
                                "head": self.plan.branch, "base": "main", "draft": True}
                if self.pr_error == "denied":
                    raise Blocked("HTTP 403")
                if self.pr_error == "unknown":
                    raise Blocked("uncertain create")
                self.pr = self.draft()
                if self.pr_error == "stored-unknown":
                    raise Blocked("uncertain create")
                return self.pr
            raise AssertionError("unexpected mutation")
        assert method == "GET"
        self.reads.append(path)
        if path == C + "/commits/" + RECEIVER:
            return {"sha": self.control_sha}
        workflow = TARGET + "/.github/workflows/codex-execute.yml@" + ADAPTER_TAG
        if path == C + "/contents/release/current-runtime.json?ref=main":
            return b64({"release_state": "published", "control_plane": {
                "tag": RECEIVER, "tag_published": True, "tag_commit_sha": CONTROL},
                "targets": {TARGET: {"enabled": True, "workflow_ref": workflow}}})
        if path == C + "/contents/config/codex-repositories.json?ref=" + CONTROL:
            return b64({"registry_format_version": 1, "repositories": {TARGET: {
                "workflow_ref": workflow, "draft_pr_only": True, "conformance": {
                    "status": "pass", "adapter_ref": ADAPTER_TAG, "adapter_commit_sha": self.registry_sha}}}})
        if path == "/user":
            return {"login": self.publisher}
        if path == T:
            return {"full_name": TARGET, "default_branch": "main", "permissions": {"push": self.permission}}
        if path == T + "/commits/" + ADAPTER_TAG:
            return {"sha": self.adapter_sha}
        if path == T + "/git/ref/heads/main":
            return self.ref_value(self.main_sha, "refs/heads/main")
        if path == T + "/git/matching-refs/heads/" + self.plan.branch:
            if self.unreadable:
                raise Blocked("unreadable refs")
            return [] if self.head is None else [self.ref_value(self.head)]
        if path.startswith(T + "/pulls?"):
            assert "state=all" in path and self.plan.branch in unquote(path)
            return [] if self.pr is None else [{"number": 7}]
        if path == T + "/pulls/7":
            return self.pr
        if path == T + "/git/commits/" + BASE:
            return {"sha": BASE, "tree": {"sha": TREE}}
        if path == T + "/git/trees/" + TREE + "?recursive=1":
            return {"truncated": False, "tree": [{"path": marker_path(self.plan)}] if self.base_marker else []}
        if path == T + "/git/commits/" + HEAD:
            return {"sha": HEAD, "parents": [{"sha": BASE}]}
        if path == T + "/compare/" + BASE + "..." + HEAD:
            return {"ahead_by": 1, "behind_by": 0,
                    "files": [{"filename": marker_path(self.plan), "status": "added"}]}
        if path == T + "/contents/" + marker_path(self.plan) + "?ref=" + HEAD:
            return b64("foreign" if self.foreign_marker else self.plan.marker)
        raise AssertionError("unexpected read " + path)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.env = env()
        self.plan, _ = authorization(self.env)
        self.fake = Fake(self.plan)
        self.addCleanup(patch.stopall)
        patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("real HTTP attempted")).start()
        patch("socket.create_connection", side_effect=AssertionError("real socket attempted")).start()
        patch("subprocess.Popen", side_effect=AssertionError("subprocess attempted")).start()

    def execute(self):
        return run(self.env, self.fake, self.fake)

    def deny(self, posts=0):
        with self.assertRaises(Blocked):
            self.execute()
        self.assertEqual(len(self.fake.posts), posts)

    def test_fresh_then_read_only_replay(self):
        first = self.execute()
        self.assertEqual(first["status"], "created-draft-verified")
        self.assertFalse(first["readiness_eligible"])
        self.assertEqual(first["draft_url"], URL)
        self.assertNotIn("credential_sha256", first)
        self.assertEqual([p for p, _ in self.fake.posts],
                         [T + "/git/trees", T + "/git/commits", T + "/git/refs", T + "/pulls"])
        self.assertEqual(self.execute()["status"], "verified-existing-draft")
        self.assertEqual(len(self.fake.posts), 4)

    def test_context_denials(self):
        for key, val in (("GITHUB_REF", "refs/heads/main"), ("GITHUB_RUN_ATTEMPT", "2"),
                         ("GITHUB_ACTOR", "foreign"), ("GITHUB_TRIGGERING_ACTOR", "foreign"),
                         ("GITHUB_WORKFLOW_SHA", BASE), ("GITHUB_WORKFLOW_REF", "foreign"),
                         ("CANARY_CONFIRMATION", ""), ("CANARY_AUTHORIZATION", ""),
                         ("OPENAI_API_KEY", "synthetic"), ("CODEX_ROUTER_TOKEN", "synthetic")):
            with self.subTest(key=key):
                with patch.dict(self.env, {key: val}):
                    self.deny()
        self.assertEqual(self.fake.reads, [])

    def test_release_and_permission_denials(self):
        for key, val in (("control_sha", BASE), ("registry_sha", BASE), ("adapter_sha", BASE),
                         ("main_sha", EXEC), ("publisher", OWNER), ("permission", False),
                         ("unreadable", True), ("base_marker", True)):
            with self.subTest(key=key):
                prior = getattr(self.fake, key)
                setattr(self.fake, key, val)
                self.deny()
                setattr(self.fake, key, prior)

    def test_existing_branch_no_pr_is_durable_stop(self):
        self.fake.head = HEAD
        self.deny()
        self.deny()

    def test_pr_without_branch(self):
        self.fake.pr = self.fake.draft()
        self.deny()

    def test_foreign_branch(self):
        self.fake.head = HEAD
        self.fake.foreign_marker = True
        self.deny()

    def test_invalid_draft(self):
        self.fake.head = HEAD
        for key, value in (("draft", False), ("state", "closed"), ("user", {"login": OWNER}),
                           ("body", "foreign"), ("base", {"repo": {"full_name": TARGET},
                                                          "ref": "main", "sha": EXEC})):
            self.fake.pr = self.fake.draft()
            self.fake.pr[key] = value
            with self.subTest(key=key):
                self.deny()

    def test_uncertain_ref_never_creates_pr(self):
        self.fake.ref_error = True
        self.deny(3)
        self.deny(3)

    def test_denied_pr_and_rerun(self):
        self.fake.pr_error = "denied"
        self.deny(4)
        self.deny(4)

    def test_ambiguous_pr_empty_and_rerun(self):
        self.fake.pr_error = "unknown"
        self.deny(4)
        self.deny(4)

    def test_ambiguous_stored_pr_readback_only(self):
        self.fake.pr_error = "stored-unknown"
        r = self.execute()
        self.assertEqual(r["status"], "reconciled-draft-not-fresh-proof")
        self.assertFalse(r["readiness_eligible"])
        self.assertEqual(len(self.fake.posts), 4)
        self.assertEqual(self.execute()["status"], "verified-existing-draft")
        self.assertEqual(len(self.fake.posts), 4)

    def test_http_boundary_trap(self):
        with patch.dict(os.environ, {"NO_NETWORK": "1"}):
            with self.assertRaises(Blocked):
                GitHub("synthetic").call("GET", T)
        with patch.dict(os.environ, {"NO_NETWORK": "0"}):
            for api, method, path in ((GitHub("synthetic"), "POST", T + "/pulls"),
                                      (GitHub("synthetic", publisher=True), "DELETE", T + "/git/refs"),
                                      (GitHub("synthetic", publisher=True), "POST", C + "/pulls"),
                                      (GitHub("synthetic", publisher=True), "GET", C + "/commits/main")):
                with self.assertRaises(Blocked):
                    api.call(method, path)


if __name__ == "__main__":
    unittest.main()
