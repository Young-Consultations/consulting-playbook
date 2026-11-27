#!/usr/bin/env python3
"""Owner-gated readiness packaging; no model, GitHub writes, or plaintext export."""
import base64
import ctypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TARGET = "Young-Consultations/consulting-playbook"
OWNER = "mightyjoe909"
ENVIRONMENT = "consulting-playbook-codex"
ADAPTER = "e4328a6ddde2da6e691b8127b01863b659a5537b"
CONTROL = "3cce887fc393fa80ed8f79308ca9b9c7241ce622"
TAG = "codex-adapter-v5.0.0"
REF = "refs/heads/review/v5-readiness-handoff"
WORKFLOW = ".github/workflows/package-publication-readiness.yml"
CANARY_WORKFLOW = ".github/workflows/publication-canary.yml"
PREFIX = "/repos/" + TARGET
POLICY = "v5-cutover-20261125-01"
SNAPSHOT_FIELDS = {"repository", "secret_name", "scope", "created_at", "updated_at",
                   "observed_at", "no_environment_override", "no_org_duplicate",
                   "credential_and_permissions_unchanged"}
EVIDENCE_FIELDS = {"status", "readiness_eligible", "owner_review_required",
                   "repository", "environment", "receiver_ref", "executor_sha",
                   "control_plane_sha", "policy_revision", "base_sha", "branch",
                   "candidate_sha", "draft_url", "publisher", "observed_at"}


class Blocked(ValueError):
    pass


def need(ok):
    if not ok:
        raise Blocked("readiness handoff evidence or authorization mismatch")


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result)
        result[key] = value
    return result


def parse(raw):
    def invalid(_):
        raise Blocked("nonfinite JSON")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(value):
    need(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value))
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def bindings():
    return {"repository": TARGET, "executor_sha": ADAPTER, "control_plane_sha": CONTROL,
            "environment": ENVIRONMENT, "receiver_ref": "ai-sdlc-v5.0.0",
            "policy_revision": POLICY}


def key_bytes(value):
    raw = base64.b64decode(value, validate=True)
    need(len(raw) == 32 and base64.b64encode(raw).decode() == value)
    return raw


def preflight(env):
    mode = env.get("MODE")
    sha = env.get("EXPECTED_HELPER_SHA", "")
    run = env.get("CANARY_RUN_ID", "")
    helper_run = env.get("GITHUB_RUN_ID", "")
    need(mode in {"package", "verify"} and re.fullmatch(r"[0-9a-f]{40}", sha)
         and re.fullmatch(r"[1-9][0-9]*", run)
         and re.fullmatch(r"[1-9][0-9]*", helper_run) and helper_run != run
         and env.get("GITHUB_REPOSITORY") == TARGET
         and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
         and env.get("GITHUB_REF") == REF
         and env.get("GITHUB_WORKFLOW_REF") == TARGET + "/" + WORKFLOW + "@" + REF
         and env.get("GITHUB_SHA") == env.get("GITHUB_WORKFLOW_SHA") == sha
         and env.get("GITHUB_ACTOR") == env.get("GITHUB_TRIGGERING_ACTOR") == OWNER
         and env.get("GITHUB_RUN_ATTEMPT") == "1"
         and env.get("CONFIRMATION") == mode + "-accepted-canary")
    need(not any(env.get(k) for k in ("OPENAI_API_KEY", "CODEX_API_KEY",
              "CODEX_ROUTER_TOKEN", "CODEX_RESULT_TOKEN", "AI_SDLC_RESULT_WRITER_PRIVATE_KEY")))
    continuity = parse(env["CONTINUITY_JSON"])
    need(isinstance(continuity, dict) and set(continuity) == {"before", "after"})
    key_id = env.get("ENV_KEY_ID", "")
    key = env.get("ENV_PUBLIC_KEY", "")
    if mode == "package":
        need(re.fullmatch(r"[A-Za-z0-9._-]{1,128}", key_id))
        pub = key_bytes(key)
        key_binding = key_id + ":" + digest(pub)
    else:
        need(not key_id and not key)
        pub = None
        key_binding = "no-key"
    return mode, int(run), continuity, key_id, pub, key_binding


def authorize(env):
    mode, run, continuity, key_id, pub, key_binding = preflight(env)
    need(env.get("AUTHORIZED_CONTROL_PLANE_SHA") == CONTROL
         and env.get("PUBLICATION_POLICY_REVISION") == POLICY
         and not env.get("PUBLICATION_CANARY_AUTHORIZATION"))
    grant = ":".join(("readiness-handoff", mode, env["EXPECTED_HELPER_SHA"], str(run),
                      env["GITHUB_RUN_ID"], env["GITHUB_RUN_ATTEMPT"],
                      digest(canonical(continuity).encode()), key_binding))
    need(env.get("MAINTENANCE_AUTHORIZATION") == grant)
    return mode, run, continuity, key_id, pub


def credential_free_preflight():
    try:
        need(not any(os.environ.get(k) for k in ("READ_TOKEN", "TARGET_PUBLICATION_TOKEN",
                  "PUBLICATION_READINESS_EVIDENCE", "MAINTENANCE_AUTHORIZATION")))
        preflight(os.environ)
        print("READINESS_CREDENTIAL_FREE_PREFLIGHT_PASS")
        return 0
    except Exception:
        print("READINESS_CREDENTIAL_FREE_PREFLIGHT_BLOCKED", file=sys.stderr)
        return 1


def continuity_check(pair, run, helper, now):
    before, after = pair["before"], pair["after"]
    for row in (before, after):
        need(isinstance(row, dict) and set(row) == SNAPSHOT_FIELDS
             and row["repository"] == TARGET and row["secret_name"] == "TARGET_PUBLICATION_TOKEN"
             and row["scope"] == "repository"
             and all(row[k] is True for k in ("no_environment_override", "no_org_duplicate",
                                              "credential_and_permissions_unchanged"))
             and stamp(row["created_at"]) <= stamp(row["updated_at"]) <= stamp(row["observed_at"]))
    need(all(before[k] == after[k] for k in SNAPSHOT_FIELDS - {"observed_at"}))
    started = stamp(run["created_at"])
    completed = stamp(run["updated_at"])
    pre, post = stamp(before["observed_at"]), stamp(after["observed_at"])
    queued = stamp(helper["created_at"])
    need(pre <= started <= completed <= post <= queued <= now
         and started - pre <= timedelta(hours=24)
         and now - post <= timedelta(hours=2))


def run_identity(run, run_id):
    need(type(run.get("id")) is int and run["id"] == run_id
         and run["path"] == CANARY_WORKFLOW and run["event"] == "workflow_dispatch"
         and run["head_sha"] == ADAPTER and run["head_branch"] == TAG
         and run["repository"]["full_name"] == run["head_repository"]["full_name"] == TARGET
         and run["actor"]["login"] == run["triggering_actor"]["login"] == OWNER
         and type(run["run_attempt"]) is int and run["run_attempt"] == 1
         and run["status"] == "completed" and run["conclusion"] == "success")


def canary_job(data, run_id):
    need(data["total_count"] == len(data["jobs"]) == 1)
    job = data["jobs"][0]
    need(job["name"] == "canary" and job["run_id"] == run_id
         and job["head_sha"] == ADAPTER and job["status"] == "completed"
         and job["conclusion"] == "success")
    steps = [s for s in job["steps"]
             if s["name"] == "Verify immutable authorization and publish one bounded draft"]
    need(len(steps) == 1 and steps[0]["status"] == "completed"
         and steps[0]["conclusion"] == "success" and type(job["id"]) is int)
    return job["id"]


def evidence_from_log(log):
    need(len(log) <= 2_000_000)
    candidates = []
    for line in log.splitlines():
        # The transport prints one JSON object on a line, with runner log prefixes.
        start = line.find("{")
        if start < 0:
            continue
        try:
            row = parse(line[start:])
        except (ValueError, TypeError):
            continue
        if isinstance(row, dict) and set(row) == EVIDENCE_FIELDS:
            candidates.append(row)
    need(len(candidates) == 1)
    return candidates[0]


def verify_evidence(row, run, reader, publisher, transport, plan_type, now):
    need(set(row) == EVIDENCE_FIELDS and row["status"] == "created-draft-verified"
         and row["readiness_eligible"] is False and row["owner_review_required"] is True
         and row["publisher"] == OWNER and all(row[k] == v for k, v in bindings().items()))
    when = stamp(row["observed_at"])
    need(stamp(run["created_at"]) <= when <= stamp(run["updated_at"]) <= now
         and now - when <= timedelta(days=30))
    need(isinstance(row["branch"], str) and row["branch"].startswith("ai-sdlc-canary/"))
    plan = plan_type(row["branch"].removeprefix("ai-sdlc-canary/"), ADAPTER, CONTROL,
                     row["base_sha"], POLICY)
    need(plan.branch == row["branch"])
    transport.release_check(reader, plan)
    transport.main_ref(reader, plan)
    need(reader.call("GET", PREFIX + "/commits/" + TAG)["sha"] == ADAPTER)
    need(publisher.call("GET", "/user")["login"] == OWNER)
    repo = publisher.call("GET", PREFIX)
    need(repo["full_name"] == TARGET and repo["default_branch"] == "main"
         and repo["permissions"]["push"] is True)
    head = transport.branch_ref(reader, plan)
    need(head is not None and head == row["candidate_sha"])
    transport.verify_branch(reader, plan, head)
    pr = transport.draft_list(reader, plan)
    need(transport.verify_draft(pr, plan, head, OWNER) == row["draft_url"])


def record_for(row, token, validator, now):
    need(bool(token))
    record = dict(bindings(), version=1, credential_sha256=digest(token.encode()),
                  verified_at=row["observed_at"], outcome="draft-pr-created",
                  draft_url=row["draft_url"])
    raw = canonical(record)
    validator(raw, bindings(), token, now=now)
    return raw


def seal(raw, public_key):
    # System libsodium; no external Python package or custom crypto implementation.
    lib = ctypes.CDLL("libsodium.so.23")
    lib.sodium_init.restype = ctypes.c_int
    need(lib.sodium_init() >= 0)
    lib.crypto_box_seal.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                    ctypes.c_ulonglong, ctypes.c_char_p]
    lib.crypto_box_seal.restype = ctypes.c_int
    clear = raw.encode()
    out = ctypes.create_string_buffer(len(clear) + 48)
    need(len(public_key) == 32 and lib.crypto_box_seal(out, clear, len(clear), public_key) == 0)
    return base64.b64encode(out.raw).decode()


def envelope(raw, key_id, public_key, run_id, helper_sha, continuity, helper_run_id, attempt):
    need(type(helper_run_id) is int and helper_run_id > 0 and type(attempt) is int and attempt == 1)
    return {"version": 1, "repository": TARGET, "environment": ENVIRONMENT,
            "secret_name": "PUBLICATION_READINESS_EVIDENCE", "key_id": key_id,
            "public_key_sha256": digest(public_key), "canary_run_id": run_id,
            "helper_run_id": helper_run_id, "helper_run_attempt": attempt,
            "helper_sha": helper_sha, "continuity_sha256": digest(canonical(continuity).encode()),
            "encrypted_value": seal(raw, public_key)}


def logs(job_id, read_token):
    need(os.environ.get("NO_NETWORK") != "1")
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG") if k in os.environ}
    env.update(GH_TOKEN=read_token, GH_HOST="github.com", GH_PROMPT_DISABLED="1",
               GH_NO_UPDATE_NOTIFIER="1")
    return subprocess.check_output(
        ["gh", "run", "view", "--repo", TARGET, "--job", str(job_id), "--log"],
        env=env, stderr=subprocess.DEVNULL, text=True, timeout=60)


def main():
    os.umask(0o077)
    try:
        mode, run_id, pair, key_id, pub = authorize(os.environ)
        need(os.environ.get("NO_NETWORK") != "1")
        read = os.environ.pop("READ_TOKEN", "")
        token = os.environ.pop("TARGET_PUBLICATION_TOKEN", "")
        installed = os.environ.pop("PUBLICATION_READINESS_EVIDENCE", "")
        need(bool(read) and bool(token) and (bool(installed) == (mode == "verify")))
        # Workflow checks the exact immutable checkout before secrets are mapped.
        immutable = Path(os.environ["IMMUTABLE_ROOT"]).resolve(strict=True)
        sys.path.insert(0, str(immutable / "scripts"))
        import publication_canary_transport as transport
        from publication_canary import Plan
        from publication_readiness import require_readiness

        reader = transport.GitHub(read)
        publisher = transport.GitHub(token)  # read-only client, never publisher=True
        run = reader.call("GET", PREFIX + "/actions/runs/" + str(run_id))
        run_identity(run, run_id)
        helper = reader.call("GET", PREFIX + "/actions/runs/" + os.environ["GITHUB_RUN_ID"])
        need(type(helper["id"]) is int and helper["id"] == int(os.environ["GITHUB_RUN_ID"])
             and helper["head_sha"] == os.environ["EXPECTED_HELPER_SHA"]
             and helper["head_branch"] == REF.removeprefix("refs/heads/")
             and helper["event"] == "workflow_dispatch" and helper["status"] == "in_progress"
             and helper["repository"]["full_name"] == helper["head_repository"]["full_name"] == TARGET
             and helper["path"] == WORKFLOW and type(helper["run_attempt"]) is int and helper["run_attempt"] == 1
             and helper["actor"]["login"] == helper["triggering_actor"]["login"] == OWNER)
        job = canary_job(reader.call("GET", PREFIX + "/actions/runs/" + str(run_id)
                                    + "/attempts/1/jobs?per_page=100"), run_id)
        row = evidence_from_log(logs(job, read))
        now = datetime.now(timezone.utc)
        continuity_check(pair, run, helper, now)
        verify_evidence(row, run, reader, publisher, transport, Plan, now)
        output = Path(os.environ["RUNNER_TEMP"]) / "readiness-envelope.json"
        need(not output.exists() and not output.is_symlink())
        if mode == "package":
            raw = record_for(row, token, require_readiness, now)
            result = envelope(raw, key_id, pub, run_id, helper["head_sha"], pair,
                              helper["id"], helper["run_attempt"])
            with output.open("x") as stream:
                stream.write(canonical(result) + "\n")
            print("READINESS_ENCRYPTED_HANDOFF_PASS; owner installation required")
        else:
            require_readiness(installed, bindings(), token, now=now)
            record = parse(installed)
            need(record["draft_url"] == row["draft_url"]
                 and record["verified_at"] == row["observed_at"])
            print("READINESS_INSTALLED_VALIDATOR_PASS")
        return 0
    except Exception:
        # Do not render exception messages, inputs, plaintext, or fingerprints.
        print("READINESS_HANDOFF_BLOCKED; preserve evidence and stop", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        raise SystemExit(credential_free_preflight())
    if sys.argv[1:]:
        raise SystemExit("READINESS_HANDOFF_BLOCKED")
    raise SystemExit(main())
