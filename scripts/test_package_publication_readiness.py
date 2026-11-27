"""Synthetic offline tests; no real credentials or network."""
import base64
import ctypes
from datetime import datetime, timezone
import json
import os
import unittest
from unittest.mock import patch

import package_publication_readiness as p
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


if __name__ == "__main__":
    unittest.main()
