"""Synthetic-only tests; no token, network, publication or model access."""
import contextlib
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch, Mock
import urllib.request
from urllib.error import HTTPError

import publisher_credential_audit as a

SHA = "a" * 40
TOKEN = "synthetic-token-not-a-real-credential"


def env():
    return {
        "EXPECTED_MAIN_SHA": SHA, "GITHUB_SHA": SHA, "GITHUB_WORKFLOW_SHA": SHA,
        "GITHUB_WORKFLOW_REF": a.WORKFLOW, "GITHUB_REPOSITORY": a.TARGET,
        "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": a.OWNER,
        "GITHUB_TRIGGERING_ACTOR": a.OWNER, "CONFIRMATION": "audit-publisher-read-only",
        "TARGET_PUBLICATION_TOKEN": TOKEN,
    }


def ref(name, sha):
    return {"ref": name, "object": {"type": "commit", "sha": sha}}


def fixtures():
    return {
        a.MAIN: ref("refs/heads/main", SHA),
        a.CONTROL_TAG: ref("refs/tags/ai-sdlc-v5.0.0", a.CONTROL_SHA),
        a.ADAPTER: ref("refs/tags/codex-adapter-v5.0.0", a.ADAPTER_SHA),
        "/user": {"login": "synthetic-publisher", "type": "User"},
        a.TARGET_PATH: {"full_name": a.TARGET, "default_branch": "main",
                        "permissions": {"push": True}},
    }


class Tests(unittest.TestCase):
    def setUp(self):
        for target in ("socket.create_connection", "socket.socket.connect",
                       "subprocess.run", "subprocess.Popen", "urllib.request.urlopen"):
            p = patch(target, side_effect=AssertionError("external effect"))
            p.start()
            self.addCleanup(p.stop)
        self.data = fixtures()
        self.publisher = Mock()
        self.publisher.get.side_effect = self.data.__getitem__
        self.public = Mock()
        self.public.get.side_effect = self.data.__getitem__

    def test_success_is_bounded_and_not_readiness(self):
        result = a.audit(env(), self.publisher, self.public)
        self.assertEqual(result["publisher_login"], "synthetic-publisher")
        self.assertFalse(result["publication_write_tested"])
        self.assertFalse(result["readiness_eligible"])
        self.assertFalse(result["model_executed"])
        self.assertEqual([x.args[0] for x in self.publisher.get.call_args_list],
                         [a.MAIN, "/user", a.TARGET_PATH, a.ADAPTER, a.MAIN])
        self.public.get.assert_called_once_with(a.CONTROL_TAG)
        self.assertNotIn(TOKEN, json.dumps(result))

    def test_authorization_faults_do_not_read(self):
        for key in env():
            if key == "TARGET_PUBLICATION_TOKEN":
                continue
            with self.subTest(key=key):
                bad = env()
                bad[key] = "wrong"
                with self.assertRaises(a.Blocked):
                    a.audit(bad, self.publisher, self.public)
        for key in ("OPENAI_API_KEY", "CODEX_ROUTER_TOKEN", "PREFLIGHT_AUDIT_TOKEN",
                    "AI_SDLC_RESULT_WRITER_PRIVATE_KEY", "PUBLICATION_READINESS_EVIDENCE"):
            with self.subTest(key=key):
                with self.assertRaises(a.Blocked):
                    a.audit({**env(), key: TOKEN}, self.publisher, self.public)
        self.publisher.get.assert_not_called()
        self.public.get.assert_not_called()

    def test_bad_identity_permission_refs_and_default_branch_deny(self):
        cases = [
            ("/user", {"login": "bad\\nline", "type": "User"}),
            ("/user", {"login": "app", "type": "Bot"}),
            (a.TARGET_PATH, {"full_name": "foreign/repo", "default_branch": "main",
                             "permissions": {"push": True}}),
            (a.TARGET_PATH, {"full_name": a.TARGET, "default_branch": "dev",
                             "permissions": {"push": True}}),
            (a.TARGET_PATH, {"full_name": a.TARGET, "default_branch": "main",
                             "permissions": {"push": 1}}),
            (a.CONTROL_TAG, ref("refs/tags/ai-sdlc-v5.0.0", SHA)),
            (a.ADAPTER, ref("refs/tags/codex-adapter-v5.0.0", SHA)),
            (a.MAIN, ref("refs/heads/main", a.CONTROL_SHA)),
        ]
        for path, value in cases:
            with self.subTest(path=path):
                self.data.clear()
                self.data.update(fixtures())
                self.data[path] = value
                with self.assertRaises(a.Blocked):
                    a.audit(env(), self.publisher, self.public)

    def test_main_drift_after_reads_denies(self):
        values = iter([self.data[a.MAIN], ref("refs/heads/main", a.CONTROL_SHA)])
        self.publisher.get.side_effect = lambda path: (
            next(values) if path == a.MAIN else self.data[path]
        )
        with self.assertRaises(a.Blocked):
            a.audit(env(), self.publisher, self.public)

    def test_transport_get_only_fixed_host_no_public_token(self):
        with patch.dict(os.environ, {"NO_NETWORK": "0"}):
            for token, path in ((TOKEN, a.MAIN), (None, a.CONTROL_TAG)):
                reader = a.Reader(token)
                response = Mock(status=200)
                response.read.return_value = b'{"ok": true}'
                fake = Mock()
                fake.open.return_value.__enter__ = Mock(return_value=response)
                fake.open.return_value.__exit__ = Mock(return_value=False)
                reader._opener = fake
                self.assertEqual(reader.get(path), {"ok": True})
                request = fake.open.call_args.args[0]
                self.assertEqual(request.full_url, a.HOST + path)
                self.assertEqual(request.get_method(), "GET")
                self.assertEqual(request.get_header("Authorization"),
                                 "Bearer " + TOKEN if token else None)
                self.assertEqual(fake.open.call_args.kwargs["timeout"], a.TIMEOUT)
                response.read.assert_called_once_with(a.MAX_BYTES + 1)

    def test_endpoint_no_network_and_redirect_guards(self):
        for token, path in ((TOKEN, a.CONTROL_TAG), (None, "/user"),
                            (TOKEN, "https://other.example"), (TOKEN, a.MAIN + "?x=1")):
            with patch.dict(os.environ, {"NO_NETWORK": "0"}):
                reader = a.Reader(token)
                reader._opener = Mock()
                with self.assertRaises(a.Blocked):
                    reader.get(path)
                reader._opener.open.assert_not_called()
        with patch.dict(os.environ, {"NO_NETWORK": "1"}):
            reader = a.Reader(TOKEN)
            reader._opener = Mock()
            with self.assertRaises(a.Blocked):
                reader.get("/user")
            reader._opener.open.assert_not_called()
        self.assertIsNone(a.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.example"))

    def test_http_errors_and_malformed_response_are_sanitized(self):
        with patch.dict(os.environ, {"NO_NETWORK": "0"}):
            reader = a.Reader(TOKEN)
            reader._opener = Mock()
            reader._opener.open.side_effect = HTTPError(a.HOST, 403, TOKEN, {}, None)
            with self.assertRaisesRegex(a.Blocked, "^http-403$"):
                reader.get("/user")
            reader._opener.open.side_effect = RuntimeError(TOKEN)
            with self.assertRaisesRegex(a.Blocked, "^transport-or-malformed-response$"):
                reader.get("/user")

    def test_main_never_prints_raw_failure_or_secret(self):
        for failure in (RuntimeError(TOKEN), a.Blocked("authorization-denied")):
            with patch.dict(os.environ, env(), clear=True), patch.object(a, "audit", side_effect=failure):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(a.main(), 1)
                self.assertNotIn(TOKEN, out.getvalue())
                self.assertIn("PUBLISHER_AUDIT_BLOCKED", out.getvalue())

    def test_workflow_manual_only_and_offline_has_no_credentials(self):
        root = Path(__file__).resolve().parents[1]
        live = (root / ".github/workflows/publisher-credential-audit.yml").read_text()
        offline = (root / ".github/workflows/publisher-audit-offline-ci.yml").read_text()
        for expected in ("workflow_dispatch:", "github.run_attempt == 1",
                         "github.triggering_actor", "github.workflow_sha == inputs.expected_main_sha",
                         "persist-credentials: false", "timeout-minutes: 3"):
            self.assertIn(expected, live)
        self.assertNotIn("pull_request:", live)
        self.assertNotIn("push:", live)
        self.assertEqual(live.count("secrets."), 1)
        self.assertIn("secrets.TARGET_PUBLICATION_TOKEN", live)
        self.assertNotIn("environment:", live)
        self.assertNotIn("secrets.", offline)
        self.assertIn('NO_NETWORK: "1"', offline)


if __name__ == "__main__":
    unittest.main()
