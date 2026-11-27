"""Synthetic offline tests; no real credentials or network."""
import base64
import ctypes
from datetime import datetime, timezone
import json
import os
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
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
        obj = p.envelope(raw, "42", pk, 123, "a" * 40, pair(), 456, 1)
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
                   GITHUB_TRIGGERING_ACTOR=p.OWNER, GITHUB_RUN_ATTEMPT="1", GITHUB_RUN_ID="456",
                   CONFIRMATION="package-accepted-canary", AUTHORIZED_CONTROL_PLANE_SHA=p.CONTROL,
                   PUBLICATION_POLICY_REVISION=p.POLICY, CONTINUITY_JSON=p.canonical(pair()),
                   ENV_KEY_ID="42", ENV_PUBLIC_KEY=base64.b64encode(pk).decode())
        prefix = "readiness-handoff:"
        h = p.digest(p.canonical(pair()).encode())
        env["MAINTENANCE_AUTHORIZATION"] = prefix + f"package:{sha}:123:456:1:{h}:42:{p.digest(pk)}"
        self.assertEqual(p.authorize(env)[0], "package")
        for field, value in (("GITHUB_RUN_ATTEMPT", "2"), ("GITHUB_RUN_ID", "457"), ("GITHUB_ACTOR", "other"),
                             ("GITHUB_WORKFLOW_SHA", "b"*40), ("GITHUB_REF", "refs/heads/main"),
                             ("PUBLICATION_CANARY_AUTHORIZATION", "active"),
                             ("OPENAI_API_KEY", "synthetic"), ("ENV_KEY_ID", "43")):
            with self.subTest(field=field), self.assertRaises(p.Blocked):
                p.authorize(dict(env, **{field:value}))
        env.update(MODE="verify", CONFIRMATION="verify-accepted-canary",
                   ENV_KEY_ID="", ENV_PUBLIC_KEY="")
        with self.assertRaises(p.Blocked):
            p.authorize(env)
        env["MAINTENANCE_AUTHORIZATION"] = prefix + f"verify:{sha}:123:456:1:{h}:no-key"
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

    def readback_fixture(self):
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
        return row, routes, pr, Fake

    def test_real_immutable_readback_contract(self):
        row, routes, pr, Fake = self.readback_fixture()
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


    def execution_env(self, mode, pk, tmp):
        sha = "a"*40
        env = dict(MODE=mode, EXPECTED_HELPER_SHA=sha, CANARY_RUN_ID="123",
                   GITHUB_REPOSITORY=p.TARGET, GITHUB_EVENT_NAME="workflow_dispatch",
                   GITHUB_REF=p.REF, GITHUB_WORKFLOW_REF=p.TARGET+"/"+p.WORKFLOW+"@"+p.REF,
                   GITHUB_SHA=sha, GITHUB_WORKFLOW_SHA=sha, GITHUB_ACTOR=p.OWNER,
                   GITHUB_TRIGGERING_ACTOR=p.OWNER, GITHUB_RUN_ATTEMPT="1", GITHUB_RUN_ID="456",
                   CONFIRMATION=mode+"-accepted-canary", AUTHORIZED_CONTROL_PLANE_SHA=p.CONTROL,
                   PUBLICATION_POLICY_REVISION=p.POLICY, CONTINUITY_JSON=p.canonical(pair()),
                   ENV_KEY_ID="42" if mode=="package" else "",
                   ENV_PUBLIC_KEY=base64.b64encode(pk).decode() if mode=="package" else "",
                   IMMUTABLE_ROOT=str(Path(__file__).resolve().parents[1]), RUNNER_TEMP=tmp)
        key = "42:"+p.digest(pk) if mode=="package" else "no-key"
        env["MAINTENANCE_AUTHORIZATION"] = ":".join(("readiness-handoff", mode, sha, "123",
            "456", "1", p.digest(p.canonical(pair()).encode()), key))
        return env

    def test_credential_free_preflight(self):
        _, pk, _ = keys()
        env = self.execution_env("package", pk, "/unused")
        del env["MAINTENANCE_AUTHORIZATION"]
        with patch.dict(os.environ, env, clear=True), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(p.credential_free_preflight(), 0)
            for name, value in (("MODE", "other"), ("GITHUB_RUN_ATTEMPT", "2"),
                                ("GITHUB_RUN_ID", "123"), ("GITHUB_REF", "refs/heads/main"),
                                ("TARGET_PUBLICATION_TOKEN", TOKEN)):
                with patch.dict(os.environ, {name:value}):
                    self.assertEqual(p.credential_free_preflight(), 1)

    def exercise_main(self, mode, *, mutation=None, expected=0, inject_effect=None):
        lib, pk, sk = keys()
        row, routes, pr, _ = self.readback_fixture()
        run = dict(RUN, id=123, path=p.CANARY_WORKFLOW, event="workflow_dispatch",
                   head_sha=p.ADAPTER, head_branch=p.TAG,
                   repository={"full_name":p.TARGET}, head_repository={"full_name":p.TARGET},
                   actor={"login":p.OWNER}, triggering_actor={"login":p.OWNER},
                   run_attempt=1, status="completed", conclusion="success")
        helper = dict(HELPER, id=456, head_sha="a"*40, path=p.WORKFLOW,
                      head_branch=p.REF.removeprefix("refs/heads/"), event="workflow_dispatch",
                      repository={"full_name":p.TARGET}, head_repository={"full_name":p.TARGET},
                      run_attempt=1, status="in_progress", actor={"login":p.OWNER},
                      triggering_actor={"login":p.OWNER})
        routes[p.PREFIX+"/actions/runs/123"] = run
        routes[p.PREFIX+"/actions/runs/456"] = helper
        routes[p.PREFIX+"/actions/runs/123/attempts/1/jobs?per_page=100"] = {
            "total_count":1, "jobs":[{"id":789,"run_id":123,"name":"canary",
             "head_sha":p.ADAPTER,"status":"completed","conclusion":"success","steps":[
              {"name":"Verify immutable authorization and publish one bounded draft",
               "status":"completed","conclusion":"success"}]}]}
        calls = []
        violations = []

        def deny(effect):
            violations.append(effect)
            raise AssertionError(effect)

        class Client:
            def __init__(self, token, *, publisher=False):
                if publisher:
                    deny("write-capable client")
                if token not in (TOKEN, "synthetic-reader"):
                    deny("unexpected credential")
                self.token = token
            def call(self, method, path, data=None):
                calls.append((self.token,method,path))
                if method != "GET" or data is not None:
                    deny("API write or request body")
                if self.token == TOKEN and path not in ("/user",p.PREFIX):
                    deny("publisher read scope")
                if path not in routes:
                    deny("unexpected API endpoint")
                return routes[path]
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return NOW
        with TemporaryDirectory() as tmp:
            env = self.execution_env(mode, pk, tmp)
            env.update(READ_TOKEN="synthetic-reader",TARGET_PUBLICATION_TOKEN=TOKEN)
            if mode=="verify":
                env["PUBLICATION_READINESS_EVIDENCE"] = p.record_for(row,TOKEN,require_readiness,NOW)
            if mutation:
                mutation(env,row,helper,pr)
            log = "canary\tstep\t" + p.canonical(row)
            def fake_subprocess(args, **kwargs):
                if args != ["gh","run","view","--repo",p.TARGET,"--job","789","--log"]:
                    deny("unexpected subprocess command")
                child = kwargs.get("env", {})
                if child.get("GH_TOKEN") != "synthetic-reader":
                    deny("subprocess credential scope")
                if TOKEN in json.dumps(child) or p.digest(TOKEN.encode()) in json.dumps(child):
                    deny("subprocess plaintext credential or fingerprint")
                for k in ("READ_TOKEN","TARGET_PUBLICATION_TOKEN","PUBLICATION_READINESS_EVIDENCE"):
                    if k in os.environ or k in child:
                        deny("secret retained at subprocess boundary")
                if inject_effect:
                    inject_effect(Client)
                return log
            stdout,stderr=StringIO(),StringIO()
            # Allow only fake GETs and exact fake gh log command; no live network.
            with patch.dict(os.environ,env,clear=True), patch.object(p,"datetime",Clock), \
                 patch.object(transport,"GitHub",Client), \
                 patch.object(p.subprocess,"check_output",side_effect=fake_subprocess), \
                 patch.object(p.subprocess,"run",side_effect=AssertionError("subprocess trap")) as run_trap, \
                 patch.object(p.subprocess,"Popen",side_effect=AssertionError("process trap")) as popen_trap, \
                 patch("socket.socket",side_effect=AssertionError("network trap")) as network_trap, \
                 patch.object(p.sys,"path",list(p.sys.path)), \
                 redirect_stdout(stdout), redirect_stderr(stderr):
                result=p.main()
            # Assertions must run OUTSIDE main(): its fail-closed exception handler
            # may swallow the trap exception and return the expected denial.
            self.assertEqual(violations, [], "prohibited-effect attempts")
            self.assertEqual(network_trap.call_count, 0, "prohibited network attempts")
            self.assertEqual(run_trap.call_count, 0, "prohibited subprocess attempts")
            self.assertEqual(popen_trap.call_count, 0, "prohibited process attempts")
            self.assertEqual(result,expected,stdout.getvalue()+stderr.getvalue())
            output=stdout.getvalue()+stderr.getvalue()
            self.assertNotIn(TOKEN,output)
            self.assertNotIn(p.digest(TOKEN.encode()),output)
            self.assertTrue(all(method=="GET" for _,method,_ in calls))
            files=list(Path(tmp).iterdir())
            if expected==0 and mode=="package":
                self.assertEqual([f.name for f in files],["readiness-envelope.json"])
                obj=json.loads(files[0].read_text())
                self.assertEqual((obj["helper_run_id"],obj["helper_run_attempt"]),(456,1))
                self.assertNotIn(TOKEN,files[0].read_text())
                self.assertNotIn(p.digest(TOKEN.encode()),files[0].read_text())
                encrypted=base64.b64decode(obj["encrypted_value"])
                clear=ctypes.create_string_buffer(len(encrypted)-48)
                lib.crypto_box_seal_open.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                    ctypes.c_ulonglong,ctypes.c_char_p,ctypes.c_char_p]
                self.assertEqual(lib.crypto_box_seal_open(clear,encrypted,len(encrypted),pk,sk),0)
                require_readiness(clear.raw.decode(),p.bindings(),TOKEN,now=NOW)
                self.assertIn("READINESS_ENCRYPTED_HANDOFF_PASS",output)
            else:
                self.assertEqual(files,[])
                if expected==0:
                    self.assertIn("READINESS_INSTALLED_VALIDATOR_PASS",output)
                else:
                    self.assertNotIn("_PASS",output)
            return calls

    def test_main_package_success(self):
        self.assertTrue(self.exercise_main("package"))

    def test_main_verify_success(self):
        self.assertTrue(self.exercise_main("verify"))

    def test_denial_harness_detects_swallowed_effects(self):
        # Inject effects inside the otherwise legitimate log fetch. The real
        # main() catches AssertionError and returns 1; the harness must still
        # fail for each forbidden attempt. All effects are intercepted mocks.
        import socket
        cases = [
            ("network", lambda client: socket.socket()),
            ("subprocess", lambda client: p.subprocess.run(["forbidden"])),
            ("process", lambda client: p.subprocess.Popen(["forbidden"])),
            ("command", lambda client: p.subprocess.check_output(["forbidden"])),
            ("write", lambda client: client("synthetic-reader").call("POST", p.PREFIX)),
            ("body", lambda client: client("synthetic-reader").call("GET", p.PREFIX, {})),
            ("credential", lambda client: client("unexpected-synthetic-token")),
            ("publisher mode", lambda client: client(TOKEN, publisher=True)),
            ("publisher scope", lambda client: client(TOKEN).call("GET", p.PREFIX+"/pulls")),
            ("child scope", lambda client: p.subprocess.check_output(
                ["gh","run","view","--repo",p.TARGET,"--job","789","--log"],
                env={"GH_TOKEN": TOKEN})),
        ]
        for label, effect in cases:
            with self.subTest(effect=label), self.assertRaisesRegex(AssertionError, "prohibited"):
                self.exercise_main("package", expected=1, inject_effect=effect)

    def test_main_denials(self):
        mutations=[
            ("package",lambda env,row,helper,pr:env.update(GITHUB_RUN_ID="457")),
            ("package",lambda env,row,helper,pr:helper.update(id=457)),
            ("package",lambda env,row,helper,pr:row.update(status="verified-existing-draft")),
            ("package",lambda env,row,helper,pr:pr.update(draft=False)),
            ("verify",lambda env,row,helper,pr:env.update(PUBLICATION_READINESS_EVIDENCE="{}")),
            ("verify",lambda env,row,helper,pr:env.update(PUBLICATION_READINESS_EVIDENCE=
                p.record_for(row,"different-synthetic-token",require_readiness,NOW))),
            ("verify",lambda env,row,helper,pr:env.update(PUBLICATION_READINESS_EVIDENCE=
                p.record_for(dict(row,draft_url="https://github.com/"+p.TARGET+"/pull/999"),TOKEN,require_readiness,NOW))),
        ]
        for mode, mutation in mutations:
            with self.subTest(mode=mode,mutation=mutation):
                self.exercise_main(mode,mutation=mutation,expected=1)


if __name__ == "__main__":
    unittest.main()
