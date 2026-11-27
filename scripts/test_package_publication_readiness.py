"""Synthetic offline tests; no real credentials or network."""
import base64
import ctypes
from datetime import datetime, timezone
import json
import os
import unittest
from unittest.mock import patch

import package_publication_readiness as p
import publication_canary_transport as transport
from publication_canary import Plan
from publication_readiness import require_readiness, ReadinessError

NOW = datetime(2026, 11, 27, 1, tzinfo=timezone.utc)
TOKEN = "synthetic-publisher-value"
ROW = {"observed_at": "2026-11-27T00:30:00Z",
       "draft_url": "https://github.com/" + p.TARGET + "/pull/123"}
SNAP = {"repository": p.TARGET, "secret_name": "TARGET_PUBLICATION_TOKEN",
        "scope": "repository", "created_at": "2026-10-01T00:00:00Z",
        "updated_at": "2026-11-01T00:00:00Z", "observed_at": "2026-11-27T00:00:00Z",
        "no_environment_override": True, "no_org_duplicate": True,
        "credential_and_permissions_unchanged": True}
RUN = {"created_at": "2026-11-27T00:25:00Z", "updated_at": "2026-11-27T00:35:00Z"}
HELPER = {"created_at": "2026-11-27T00:50:00Z"}


def pair():
    return {"before": dict(SNAP), "after": dict(SNAP, observed_at="2026-11-27T00:40:00Z")}


def keys():
    lib = ctypes.CDLL("libsodium.so.23")
    lib.sodium_init()
    pk, sk = ctypes.create_string_buffer(32), ctypes.create_string_buffer(32)
    assert lib.crypto_box_keypair(pk, sk) == 0
    return lib, pk.raw, sk.raw


class HandoffTests(unittest.TestCase):
    def test_ciphertext_roundtrip(self):
        lib, pk, sk = keys()
        raw = p.record_for(ROW, TOKEN, require_readiness, NOW)
        obj = p.envelope(raw, "42", pk, 123, "a" * 40, pair())
        encoded = json.dumps(obj)
        self.assertNotIn(TOKEN, encoded)
        self.assertNotIn(p.digest(TOKEN.encode()), encoded)
        self.assertNotIn(ROW["draft_url"], encoded)
        encrypted = base64.b64decode(obj["encrypted_value"])
        out = ctypes.create_string_buffer(len(encrypted) - 48)
        lib.crypto_box_seal_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                             ctypes.c_ulonglong, ctypes.c_char_p, ctypes.c_char_p]
        self.assertEqual(lib.crypto_box_seal_open(out, encrypted, len(encrypted), pk, sk), 0)
        require_readiness(out.raw.decode(), p.bindings(), TOKEN, now=NOW)
        _, other_pk, other_sk = keys()
        self.assertNotEqual(lib.crypto_box_seal_open(out, encrypted, len(encrypted), other_pk, other_sk), 0)

    def test_changed_credential(self):
        raw = p.record_for(ROW, TOKEN, require_readiness, NOW)
        with self.assertRaises(ReadinessError):
            require_readiness(raw, p.bindings(), "another-synthetic-value", now=NOW)

    def test_expired(self):
        with self.assertRaises(ReadinessError):
            p.record_for(dict(ROW, observed_at="2026-10-01T00:00:00Z"), TOKEN, require_readiness, NOW)

    def test_continuity(self):
        p.continuity_check(pair(), RUN, HELPER, NOW)
        for change in ({"updated_at": "2026-11-27T00:39:00Z"},
                       {"no_environment_override": False},
                       {"credential_and_permissions_unchanged": False},
                       {"observed_at": "2026-11-27T00:30:00Z"},
                       {"observed_at": "2026-11-27T00:55:00Z"},
                       {"no_org_duplicate": False}):
            with self.subTest(change=change):
                rows = pair()
                rows["after"].update(change)
                with self.assertRaises(p.Blocked):
                    p.continuity_check(rows, RUN, HELPER, NOW)

    def test_closed_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(p.Blocked):
                p.parse(raw)

    def test_log_evidence_unique(self):
        row = dict.fromkeys(p.EVIDENCE_FIELDS, "synthetic")
        line = "canary\tstep\t2026-11-27T00:30:00Z " + json.dumps(row)
        self.assertEqual(p.evidence_from_log(line), row)
        for log in ("empty", line + "\n" + line):
            with self.assertRaises(p.Blocked):
                p.evidence_from_log(log)

    def test_authorization(self):
        _, pk, _ = keys()
        sha = "a" * 40
        env = dict(MODE="package", EXPECTED_HELPER_SHA=sha, CANARY_RUN_ID="123",
                   GITHUB_REPOSITORY=p.TARGET, GITHUB_EVENT_NAME="workflow_dispatch",
                   GITHUB_REF=p.REF, GITHUB_WORKFLOW_REF=p.TARGET+"/"+p.WORKFLOW+"@"+p.REF,
                   GITHUB_SHA=sha, GITHUB_WORKFLOW_SHA=sha, GITHUB_ACTOR=p.OWNER,
                   GITHUB_TRIGGERING_ACTOR=p.OWNER, GITHUB_RUN_ATTEMPT="1",
                   CONFIRMATION="package-accepted-canary", AUTHORIZED_CONTROL_PLANE_SHA=p.CONTROL,
                   PUBLICATION_POLICY_REVISION=p.POLICY, CONTINUITY_JSON=p.canonical(pair()),
                   ENV_KEY_ID="42", ENV_PUBLIC_KEY=base64.b64encode(pk).decode())
        prefix = "readiness-handoff:"
        h = p.digest(p.canonical(pair()).encode())
        env["MAINTENANCE_AUTHORIZATION"] = prefix + f"package:{sha}:123:{h}:42:{p.digest(pk)}"
        self.assertEqual(p.authorize(env)[0], "package")
        for field, value in (("GITHUB_RUN_ATTEMPT", "2"), ("GITHUB_ACTOR", "other"),
                             ("GITHUB_WORKFLOW_SHA", "b"*40), ("GITHUB_REF", "refs/heads/main"),
                             ("PUBLICATION_CANARY_AUTHORIZATION", "active"),
                             ("OPENAI_API_KEY", "synthetic"), ("ENV_KEY_ID", "43")):
            with self.subTest(field=field), self.assertRaises(p.Blocked):
                p.authorize(dict(env, **{field:value}))
        env.update(MODE="verify", CONFIRMATION="verify-accepted-canary",
                   ENV_KEY_ID="", ENV_PUBLIC_KEY="")
        with self.assertRaises(p.Blocked):
            p.authorize(env)
        env["MAINTENANCE_AUTHORIZATION"] = prefix + f"verify:{sha}:123:{h}:no-key"
        self.assertEqual(p.authorize(env)[0], "verify")

    def test_unfresh_evidence_denies_before_network(self):
        row = dict.fromkeys(p.EVIDENCE_FIELDS, "synthetic")
        row.update(p.bindings(), publisher=p.OWNER, readiness_eligible=False,
                   owner_review_required=True)
        for status in ("verified-existing-draft", "reconciled-draft-not-fresh-proof"):
            row["status"] = status
            with self.assertRaises(p.Blocked):
                p.verify_evidence(row, RUN, None, None, None, None, NOW)

    def test_network_trap(self):
        with patch.dict(os.environ, {"NO_NETWORK": "1"}), patch.object(p.subprocess, "check_output") as call:
            with self.assertRaises(p.Blocked):
                p.logs(123, TOKEN)
            call.assert_not_called()


    def test_run_and_job_provenance(self):
        run = dict(RUN, id=123, path=p.CANARY_WORKFLOW, event="workflow_dispatch",
                   head_sha=p.ADAPTER, head_branch=p.TAG,
                   repository={"full_name": p.TARGET}, head_repository={"full_name": p.TARGET},
                   actor={"login": p.OWNER}, triggering_actor={"login": p.OWNER},
                   run_attempt=1, status="completed", conclusion="success")
        p.run_identity(run, 123)
        for change in ({"run_attempt": 2}, {"head_sha": "a"*40}, {"conclusion": "failure"},
                       {"triggering_actor": {"login": "other"}}, {"event": "push"}):
            with self.assertRaises(p.Blocked):
                p.run_identity(dict(run, **change), 123)
        job = {"id": 456, "run_id": 123, "name": "canary", "head_sha": p.ADAPTER,
               "status": "completed", "conclusion": "success", "steps": [
                   {"name": "Verify immutable authorization and publish one bounded draft",
                    "status": "completed", "conclusion": "success"}]}
        self.assertEqual(p.canary_job({"total_count": 1, "jobs": [job]}, 123), 456)
        for change in ({"run_id": 124}, {"steps": []}, {"head_sha": "b"*40}):
            with self.assertRaises(p.Blocked):
                p.canary_job({"total_count": 1, "jobs": [dict(job, **change)]}, 123)

    def test_real_immutable_readback_contract(self):
        plan = Plan("synthetic-01", p.ADAPTER, p.CONTROL, "a"*40, p.POLICY)
        head = "b"*40
        row = dict(p.bindings(), status="created-draft-verified", readiness_eligible=False,
                   owner_review_required=True, publisher=p.OWNER, branch=plan.branch,
                   base_sha=plan.base_sha, candidate_sha=head, **ROW)
        prefix = p.PREFIX
        ctrl = "/repos/Young-Consultations/.github"
        target_ref = p.TARGET + "/.github/workflows/codex-execute.yml@" + p.TAG
        runtime = {"release_state":"published", "control_plane": {
            "tag": "ai-sdlc-v5.0.0", "tag_published": True, "tag_commit_sha": p.CONTROL},
            "targets": {p.TARGET: {"enabled": True, "workflow_ref": target_ref}}}
        registry = {"registry_format_version": 1, "repositories": {p.TARGET: {
            "workflow_ref": target_ref, "draft_pr_only": True,
            "conformance": {"status": "pass", "adapter_ref": p.TAG, "adapter_commit_sha": p.ADAPTER}}}}
        def content(raw):
            return {"encoding": "base64", "content": base64.b64encode(raw).decode()}
        pr = {"number": 123, "html_url": ROW["draft_url"], "state": "open", "draft": True,
              "user": {"login": p.OWNER}, "title": transport.title(plan), "body": transport.body(plan),
              "head": {"repo": {"full_name": p.TARGET}, "ref": plan.branch, "sha": head},
              "base": {"repo": {"full_name": p.TARGET}, "ref": "main", "sha": plan.base_sha}}
        files = [{"filename": transport.marker_path(plan), "status": "added"}]
        routes = {
            ctrl + "/commits/ai-sdlc-v5.0.0": {"sha": p.CONTROL},
            ctrl + "/contents/release/current-runtime.json?ref=main": content(json.dumps(runtime).encode()),
            ctrl + "/contents/config/codex-repositories.json?ref="+p.CONTROL: content(json.dumps(registry).encode()),
            prefix + "/commits/" + p.TAG: {"sha": p.ADAPTER},
            prefix + "/git/ref/heads/main": {"ref": "refs/heads/main", "object": {"type":"commit","sha":plan.base_sha}},
            prefix + "/git/matching-refs/heads/" + plan.branch: [{"ref":"refs/heads/"+plan.branch,
                                                                 "object":{"type":"commit","sha":head}}],
            prefix + "/git/commits/" + head: {"sha":head,"parents":[{"sha":plan.base_sha}]},
            prefix + "/compare/" + plan.base_sha + "..." + head: {"ahead_by":1,"behind_by":0,"files":files},
            prefix + "/contents/" + transport.marker_path(plan) + "?ref="+head: content(plan.marker.encode()),
            prefix + "/pulls?state=all&head=Young-Consultations%3Aai-sdlc-canary%2Fsynthetic-01&per_page=100": [{"number":123}],
            prefix + "/pulls/123": pr,
            "/user": {"login":p.OWNER},
            prefix: {"full_name":p.TARGET,"default_branch":"main","permissions":{"push":True}},
        }
        class Fake:
            def call(self, method, path, data=None):
                if method != "GET" or data is not None:
                    raise AssertionError("write trap")
                return routes[path]
        fake = Fake()
        p.verify_evidence(row, RUN, fake, fake, transport, Plan, NOW)
        for changed in (dict(row, candidate_sha="c"*40), dict(row, policy_revision="other"),
                        dict(row, observed_at="2026-10-01T00:00:00Z"),
                        dict(row, draft_url="https://github.com/"+p.TARGET+"/pull/124")):
            with self.assertRaises((p.Blocked, transport.Blocked)):
                p.verify_evidence(changed, RUN, fake, fake, transport, Plan, NOW)
        pr["draft"] = False
        with self.assertRaises(transport.Blocked):
            p.verify_evidence(row, RUN, fake, fake, transport, Plan, NOW)

    def test_main_network_trap_stops_before_secret_read_or_output(self):
        with patch.dict(os.environ, {"NO_NETWORK": "1"}), \
             patch.object(p, "authorize", return_value=("package",123,pair(),"42",b"x"*32)), \
             patch.object(p, "logs") as log, patch.object(p, "envelope") as enc, \
             patch.object(p, "record_for") as rec:
            self.assertEqual(p.main(), 1)
            log.assert_not_called()
            enc.assert_not_called()
            rec.assert_not_called()


if __name__ == "__main__":
    unittest.main()
