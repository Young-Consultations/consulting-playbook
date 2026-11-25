"""Bounded no-model GitHub publication canary, separate from the executor.

The immutable tag, owner authorization and existing protected environment are
mandatory. No credentials are logged. There is no auto-provisioning or cleanup.
"""
import base64
from datetime import datetime, timezone
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler

from publication_canary import Blocked, Plan, TARGET, ENVIRONMENT, RECEIVER

ADAPTER_TAG = "codex-adapter-v5.0.0"
CONTROL = "Young-Consultations/.github"
T = "/repos/" + TARGET
C = "/repos/" + CONTROL
WORKFLOW = TARGET + "/.github/workflows/publication-canary.yml@refs/tags/" + ADAPTER_TAG
WRITES = {T + "/git/trees", T + "/git/commits", T + "/git/refs", T + "/pulls"}
LIMIT = 2_000_000


def require(ok, message):
    if not ok:
        raise Blocked(message)


def exact_sha(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value),
            "invalid GitHub commit/tree identity")
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, token, *, publisher=False):
        require(bool(token), "required GitHub credential unavailable")
        self.token = token
        self.publisher = publisher
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def call(self, method, path, data=None):
        require(os.environ.get("NO_NETWORK") != "1", "offline network trap")
        allowed_read = path.startswith((T + "/", C + "/")) or path in (T, "/user")
        require((method == "GET" and allowed_read and
                 (not self.publisher or not path.startswith(C + "/"))) or
                (self.publisher and method == "POST" and path in WRITES),
                "GitHub request outside canary boundary")
        request = Request("https://api.github.com" + path, method=method,
                          data=None if data is None else json.dumps(data).encode(),
                          headers={"Authorization": "Bearer " + self.token,
                                   "Accept": "application/vnd.github+json",
                                   "Content-Type": "application/json",
                                   "X-GitHub-Api-Version": "2022-11-28",
                                   "User-Agent": "ai-sdlc-publication-canary"})
        try:
            with self.opener.open(request, timeout=20) as response:
                require(not response.headers.get("Link"), "paginated evidence is indeterminate")
                raw = response.read(LIMIT + 1)
                require(len(raw) <= LIMIT, "GitHub evidence exceeds bound")
                return json.loads(raw)
        except HTTPError as exc:
            raise Blocked("GitHub request failed (HTTP %d)" % exc.code) from None
        except (URLError, OSError, ValueError) as exc:
            if isinstance(exc, Blocked):
                raise
            raise Blocked("GitHub request or evidence unavailable") from None


def authorization(env):
    require(env.get("GITHUB_REPOSITORY") == TARGET
            and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and env.get("GITHUB_REF") == "refs/tags/" + ADAPTER_TAG
            and env.get("GITHUB_WORKFLOW_REF") == WORKFLOW
            and env.get("GITHUB_RUN_ATTEMPT") == "1"
            and env.get("GITHUB_SHA") == env.get("GITHUB_WORKFLOW_SHA")
            and env.get("CANARY_CONFIRMATION") == "publish-one-draft",
            "canary requires first-attempt immutable manual workflow authorization")
    owner = env.get("CANARY_APPROVER", "")
    publisher = env.get("CANARY_PUBLISHER", "")
    require(bool(re.fullmatch(r"[A-Za-z0-9-]{1,39}", owner))
            and bool(re.fullmatch(r"[A-Za-z0-9-]{1,39}", publisher))
            and env.get("GITHUB_ACTOR") == owner
            and env.get("GITHUB_TRIGGERING_ACTOR") == owner,
            "canary actor is not the configured owner")
    require(not any(env.get(k) for k in ("OPENAI_API_KEY", "CODEX_API_KEY",
                "AI_SDLC_RESULT_WRITER_PRIVATE_KEY", "RESULT_WRITER_PRIVATE_KEY",
                "CODEX_ROUTER_TOKEN", "CODEX_RESULT_TOKEN")),
            "unrelated execution credential present")
    plan = Plan(env.get("CANARY_ID", ""), env.get("GITHUB_SHA", ""),
                env.get("AUTHORIZED_CONTROL_PLANE_SHA", ""),
                env.get("CANARY_BASE_SHA", ""), env.get("PUBLICATION_POLICY_REVISION", ""))
    binding = ":".join(("automation-safe", plan.run_id, plan.executor_sha,
                        plan.control_plane_sha, plan.base_sha, plan.policy_revision, publisher))
    require(env.get("CANARY_AUTHORIZATION") == binding,
            "exact owner-approved canary authorization missing")
    return plan, publisher


def content(api, prefix, path, ref):
    value = api.call("GET", prefix + "/contents/" + path + "?" + urlencode({"ref": ref}))
    require(value.get("encoding") == "base64", "file evidence unavailable")
    try:
        return base64.b64decode("".join(value["content"].split()), validate=True)
    except (ValueError, KeyError, TypeError):
        raise Blocked("invalid file evidence") from None


def release_check(reader, plan):
    sha = reader.call("GET", C + "/commits/" + RECEIVER).get("sha")
    require(sha == plan.control_plane_sha, "control-plane tag mismatch")
    runtime = json.loads(content(reader, C, "release/current-runtime.json", "main"))
    cp = runtime["control_plane"]
    target_ref = TARGET + "/.github/workflows/codex-execute.yml@" + ADAPTER_TAG
    require(runtime["release_state"] == "published" and cp["tag"] == RECEIVER
            and cp["tag_published"] is True and cp["tag_commit_sha"] == sha
            and runtime["targets"][TARGET]["enabled"] is True
            and runtime["targets"][TARGET]["workflow_ref"] == target_ref,
            "control-plane publication attestation mismatch")
    registry = json.loads(content(reader, C, "config/codex-repositories.json", sha))
    entry = registry["repositories"][TARGET]
    pin = entry["conformance"]
    require(registry["registry_format_version"] == 1 and entry["workflow_ref"] == target_ref
            and entry["draft_pr_only"] is True and pin["status"] == "pass"
            and pin["adapter_ref"] == ADAPTER_TAG
            and pin["adapter_commit_sha"] == plan.executor_sha,
            "immutable registry does not authorize exact canary adapter")


def marker_path(plan):
    return "docs/ai-sdlc-canary/" + plan.run_id + ".json"


def title(plan):
    return "AI-SDLC no-model publication canary " + plan.run_id


def body(plan):
    return "<!-- ai-sdlc-publication-canary:" + plan.marker_digest + " -->\nDo not merge."


def main_ref(api, plan):
    ref = api.call("GET", T + "/git/ref/heads/main")
    require(ref["ref"] == "refs/heads/main" and ref["object"]["type"] == "commit"
            and ref["object"]["sha"] == plan.base_sha, "approved main base changed")


def branch_ref(api, plan):
    refs = api.call("GET", T + "/git/matching-refs/heads/" + plan.branch)
    require(isinstance(refs, list) and len(refs) < 100, "ambiguous branch evidence")
    exact = [r for r in refs if r["ref"] == "refs/heads/" + plan.branch]
    require(len(exact) <= 1, "ambiguous branch identity")
    if not exact:
        return None
    require(exact[0]["object"]["type"] == "commit", "branch is not a commit")
    return exact_sha(exact[0]["object"]["sha"])


def draft_list(api, plan):
    prs = api.call("GET", T + "/pulls?" + urlencode(
        {"state": "all", "head": TARGET.split("/")[0] + ":" + plan.branch, "per_page": 100}))
    require(isinstance(prs, list) and len(prs) <= 1, "ambiguous draft evidence")
    if not prs:
        return None
    number = prs[0]["number"]
    require(type(number) is int and number > 0, "invalid draft identity")
    return api.call("GET", T + "/pulls/" + str(number))


def verify_branch(api, plan, head):
    commit = api.call("GET", T + "/git/commits/" + head)
    require(commit["sha"] == head and [p["sha"] for p in commit["parents"]] == [plan.base_sha],
            "canary commit parent mismatch")
    diff = api.call("GET", T + "/compare/" + plan.base_sha + "..." + head)
    require(diff["ahead_by"] == 1 and diff["behind_by"] == 0
            and len(diff["files"]) == 1 and diff["files"][0]["filename"] == marker_path(plan)
            and diff["files"][0]["status"] == "added"
            and content(api, T, marker_path(plan), head) == plan.marker.encode(),
            "canary branch is not the exact harmless marker change")


def verify_draft(pr, plan, head, publisher):
    require(pr is not None, "draft evidence missing")
    number = pr["number"]
    require(type(number) is int and number > 0
            and pr["html_url"] == "https://github.com/" + TARGET + "/pull/" + str(number)
            and pr["state"] == "open" and pr["draft"] is True
            and pr["user"]["login"] == publisher and pr["title"] == title(plan)
            and pr["body"] == body(plan)
            and pr["head"]["repo"]["full_name"] == TARGET
            and pr["head"]["ref"] == plan.branch and pr["head"]["sha"] == head
            and pr["base"]["repo"]["full_name"] == TARGET
            and pr["base"]["ref"] == "main" and pr["base"]["sha"] == plan.base_sha,
            "draft ownership or exact head/base binding mismatch")
    return pr["html_url"]


def evidence(plan, head, url, publisher, status):
    # Never emit a token/fingerprint or a ready-to-install readiness record.
    return {"status": status, "readiness_eligible": False, "owner_review_required": True,
            "repository": TARGET, "environment": ENVIRONMENT, "receiver_ref": RECEIVER,
            "executor_sha": plan.executor_sha, "control_plane_sha": plan.control_plane_sha,
            "policy_revision": plan.policy_revision, "base_sha": plan.base_sha,
            "branch": plan.branch, "candidate_sha": head, "draft_url": url,
            "publisher": publisher,
            "observed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def run(env, reader, api):
    plan, publisher = authorization(env)
    release_check(reader, plan)
    require(api.call("GET", "/user")["login"] == publisher, "publisher identity mismatch")
    repo = api.call("GET", T)
    require(repo["full_name"] == TARGET and repo["default_branch"] == "main"
            and repo["permissions"]["push"] is True, "publisher repository permission denied")
    require(api.call("GET", T + "/commits/" + ADAPTER_TAG)["sha"] == plan.executor_sha,
            "adapter tag mismatch")
    main_ref(api, plan)
    head, pr = branch_ref(api, plan), draft_list(api, plan)
    if head:
        verify_branch(api, plan, head)
        # Existing branch is a durable reservation. No resume/create on reruns,
        # even if the PR read is empty after an ambiguous prior creation.
        url = verify_draft(pr, plan, head, publisher)
        return evidence(plan, head, url, publisher, "verified-existing-draft")
    require(pr is None, "draft exists without matching branch")
    base = api.call("GET", T + "/git/commits/" + plan.base_sha)
    base_tree = exact_sha(base["tree"]["sha"])
    entries = api.call("GET", T + "/git/trees/" + base_tree + "?recursive=1")
    require(entries["truncated"] is False and
            all(e["path"] != marker_path(plan) for e in entries["tree"]),
            "base marker path absent cannot be established")
    tree = exact_sha(api.call("POST", T + "/git/trees", {
        "base_tree": base_tree, "tree": [{"path": marker_path(plan), "mode": "100644",
                                        "type": "blob", "content": plan.marker}]})["sha"])
    head = exact_sha(api.call("POST", T + "/git/commits", {
        "message": title(plan), "tree": tree, "parents": [plan.base_sha]})["sha"])
    main_ref(api, plan)
    # POST create-ref is atomic create-only; never force, update, or delete a ref.
    # Any error here stops before PR creation, including an uncertain response.
    ref = api.call("POST", T + "/git/refs",
                   {"ref": "refs/heads/" + plan.branch, "sha": head})
    require(ref["ref"] == "refs/heads/" + plan.branch and ref["object"]["sha"] == head
            and branch_ref(api, plan) == head, "created ref cannot be verified")
    verify_branch(api, plan, head)
    main_ref(api, plan)
    require(draft_list(api, plan) is None, "unexpected existing draft; reconcile")
    created = None
    try:
        created = api.call("POST", T + "/pulls", {"title": title(plan), "body": body(plan),
                           "head": plan.branch, "base": "main", "draft": True})
    except Blocked:
        # At most one create. Reconciliation is read-only; a missing PR blocks.
        pass
    pr = draft_list(api, plan)
    url = verify_draft(pr, plan, head, publisher)
    if created is None:
        return evidence(plan, head, url, publisher, "reconciled-draft-not-fresh-proof")
    require(verify_draft(created, plan, head, publisher) == url,
            "create response differs from readback")
    return evidence(plan, head, url, publisher, "created-draft-verified")


def main():
    try:
        authorization(os.environ)
        require(os.environ.get("NO_NETWORK") != "1", "offline network trap")
        read_token = os.environ.pop("CANARY_READ_TOKEN", "")
        pub_token = os.environ.pop("TARGET_PUBLICATION_TOKEN", "")
        result = run(os.environ, GitHub(read_token), GitHub(pub_token, publisher=True))
        print(json.dumps(result, sort_keys=True))
    except Blocked as exc:
        print("CANARY_BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    except Exception:
        print("CANARY_BLOCKED: malformed or unavailable evidence", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
