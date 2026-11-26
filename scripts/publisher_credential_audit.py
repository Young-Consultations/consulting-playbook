"""Temporary V5.6 read-only audit of the stored publisher credential."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from urllib.error import HTTPError

TARGET = "Young-Consultations/consulting-playbook"
CONTROL = "Young-Consultations/.github"
OWNER = "mightyjoe909"
WORKFLOW = TARGET + "/.github/workflows/publisher-credential-audit.yml@refs/heads/main"
CONTROL_SHA = "3cce887fc393fa80ed8f79308ca9b9c7241ce622"
ADAPTER_SHA = "e4328a6ddde2da6e691b8127b01863b659a5537b"
HOST = "https://api.github.com"
TARGET_PATH = "/repos/" + TARGET
MAIN = TARGET_PATH + "/git/ref/heads/main"
ADAPTER = TARGET_PATH + "/git/ref/tags/codex-adapter-v5.0.0"
CONTROL_TAG = "/repos/" + CONTROL + "/git/ref/tags/ai-sdlc-v5.0.0"
PUBLISHER_PATHS = frozenset(("/user", TARGET_PATH, MAIN, ADAPTER))
MAX_BYTES = 256 * 1024
TIMEOUT = 10


class Blocked(ValueError):
    """Only fixed, sanitized diagnostic categories may escape."""


def require(ok, category):
    if not ok:
        raise Blocked(category)


def authorize(env):
    sha = env.get("EXPECTED_MAIN_SHA", "")
    require(
        bool(re.fullmatch(r"[0-9a-f]{40}", sha))
        and env.get("GITHUB_SHA") == sha
        and env.get("GITHUB_WORKFLOW_SHA") == sha
        and env.get("GITHUB_WORKFLOW_REF") == WORKFLOW
        and env.get("GITHUB_REPOSITORY") == TARGET
        and env.get("GITHUB_REF") == "refs/heads/main"
        and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        and env.get("GITHUB_RUN_ATTEMPT") == "1"
        and env.get("GITHUB_ACTOR") == OWNER
        and env.get("GITHUB_TRIGGERING_ACTOR") == OWNER
        and env.get("CONFIRMATION") == "audit-publisher-read-only",
        "authorization-denied",
    )
    require(
        not any(env.get(k) for k in (
            "OPENAI_API_KEY", "CODEX_API_KEY", "PREFLIGHT_AUDIT_TOKEN",
            "CODEX_ROUTER_TOKEN", "AI_SDLC_RESULT_WRITER_PRIVATE_KEY",
            "PUBLICATION_READINESS_EVIDENCE",
        )),
        "unrelated-credential-present",
    )
    return sha


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Reader:
    def __init__(self, token=None):
        self._token = token
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )

    def get(self, path):
        require(os.environ.get("NO_NETWORK") != "1", "network-denied")
        require(
            path in (PUBLISHER_PATHS if self._token is not None else {CONTROL_TAG}),
            "endpoint-denied",
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "v5-publisher-read-only-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token is not None:
            headers["Authorization"] = "Bearer " + self._token
        try:
            request = urllib.request.Request(HOST + path, headers=headers, method="GET")
            with self._opener.open(request, timeout=TIMEOUT) as response:
                require(response.status == 200, "unexpected-response")
                raw = response.read(MAX_BYTES + 1)
                require(len(raw) <= MAX_BYTES, "response-too-large")
                def unique(pairs):
                    result = {}
                    for key, value in pairs:
                        require(key not in result, "malformed-response")
                        result[key] = value
                    return result

                data = json.loads(raw, object_pairs_hook=unique)
                require(isinstance(data, dict), "malformed-response")
                return data
        except Blocked:
            raise
        except HTTPError as exc:
            raise Blocked("http-" + str(exc.code) if exc.code in (
                301, 302, 303, 307, 308, 401, 403, 404, 429, 500, 502, 503, 504
            ) else "http-other") from None
        except Exception:
            raise Blocked("transport-or-malformed-response") from None


def exact_ref(data, ref, sha):
    return (
        data.get("ref") == ref
        and isinstance(data.get("object"), dict)
        and data["object"].get("type") == "commit"
        and data["object"].get("sha") == sha
    )


def audit(env, publisher, public_reader):
    sha = authorize(env)
    require(exact_ref(public_reader.get(CONTROL_TAG), "refs/tags/ai-sdlc-v5.0.0",
                      CONTROL_SHA), "control-tag-mismatch")
    require(exact_ref(publisher.get(MAIN), "refs/heads/main", sha), "main-moved")
    user = publisher.get("/user")
    login = user.get("login")
    require(
        isinstance(login, str)
        and bool(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", login))
        and user.get("type") == "User",
        "publisher-identity-invalid",
    )
    repo = publisher.get(TARGET_PATH)
    require(
        repo.get("full_name") == TARGET and repo.get("default_branch") == "main",
        "target-repository-mismatch",
    )
    permissions = repo.get("permissions")
    require(isinstance(permissions, dict) and permissions.get("push") is True,
            "publisher-push-not-reported")
    require(exact_ref(publisher.get(ADAPTER), "refs/tags/codex-adapter-v5.0.0",
                      ADAPTER_SHA), "adapter-tag-mismatch")
    require(exact_ref(publisher.get(MAIN), "refs/heads/main", sha), "main-moved")
    return {
        "status": "PUBLISHER_READ_ONLY_AUDIT_COMPLETE",
        "publisher_login": login,
        "target_repository_match": True,
        "reported_push_permission": True,
        "immutable_release_identities_match": True,
        "main_sha": sha,
        "publication_write_tested": False,
        "readiness_eligible": False,
        "model_executed": False,
    }


def main():
    try:
        authorize(os.environ)
        token = os.environ.pop("TARGET_PUBLICATION_TOKEN", "")
        require(bool(token) and not any(c.isspace() for c in token), "missing-or-invalid-credential")
        result = audit(os.environ, Reader(token), Reader())
        # Never render a response field that accidentally contains the credential.
        rendered = json.dumps(result, sort_keys=True)
        require(token not in rendered, "unsafe-output")
        print(rendered)
        return 0
    except Blocked as exc:
        print("PUBLISHER_AUDIT_BLOCKED: " + str(exc))
        return 1
    except Exception:
        print("PUBLISHER_AUDIT_BLOCKED: malformed-or-unavailable-evidence")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
