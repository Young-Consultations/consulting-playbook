#!/usr/bin/env python3
"""Fail-closed audit of the immutable organization next-MVP release."""
from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import dataclass
from typing import Any

RELEASE_SHA = "f2491872976a4dcc1633997954c03c07cbc4fced"
REPOSITORY = "Young-Consultations/consulting-playbook"
BASE_URL = f"https://raw.githubusercontent.com/Young-Consultations/.github/{RELEASE_SHA}"
REQUIRED_FILES = (
    "contracts/task-contract.schema.json",
    "contracts/execution-input.schema.json",
    "contracts/execution-result.schema.json",
    "tests/fixtures/mvp-v2/manifest.json",
    "config/codex-repositories.json",
    ".github/workflows/codex-result-receiver.yml",
)


class ReadinessError(RuntimeError):
    """The immutable compatibility unit cannot safely enable this target."""


@dataclass(frozen=True)
class ReleaseFiles:
    values: dict[str, bytes]

    def json(self, path: str) -> Any:
        try:
            return json.loads(self.values[path])
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ReadinessError(f"immutable release file is invalid JSON: {path}") from error


def fetch_release(base_url: str = BASE_URL) -> ReleaseFiles:
    values: dict[str, bytes] = {}
    for path in REQUIRED_FILES:
        try:
            with urllib.request.urlopen(f"{base_url.rstrip('/')}/{path}", timeout=15) as response:  # noqa: S310
                values[path] = response.read()
        except OSError as error:
            raise ReadinessError(f"cannot read immutable release file: {path}") from error
    return ReleaseFiles(values)


def _entries(registry: Any) -> list[dict[str, Any]]:
    if isinstance(registry, list):
        return [value for value in registry if isinstance(value, dict)]
    if isinstance(registry, dict):
        for key in ("repositories", "targets", "entries"):
            if isinstance(registry.get(key), list):
                return [value for value in registry[key] if isinstance(value, dict)]
    raise ReadinessError("immutable registry has an unsupported top-level shape")


def assess(files: ReleaseFiles) -> list[str]:
    """Return external blockers without guessing organization semantics."""
    matches = [
        entry for entry in _entries(files.json("config/codex-repositories.json"))
        if entry.get("target", entry.get("repository")) == REPOSITORY
    ]
    if len(matches) != 1:
        raise ReadinessError("immutable registry must contain exactly one target entry")
    blockers: list[str] = []
    if matches[0].get("enabled") is not True:
        blockers.append("organization registry entry is disabled")
    receiver = files.values[".github/workflows/codex-result-receiver.yml"].decode("utf-8", "strict").lower()
    if any(signal in receiver for signal in ("not implemented", "fail-closed", "exit 1")):
        blockers.append("organization result receiver is fail-closed")
    manifest_text = json.dumps(files.json("tests/fixtures/mvp-v2/manifest.json"), sort_keys=True).lower()
    if "tc-mvp-ci-001" not in manifest_text:
        raise ReadinessError("immutable fixture manifest does not identify TC-MVP-CI-001")
    if any(value in manifest_text for value in ('"complete": false', '"executable": false')):
        blockers.append("shared executable fixture set is incomplete")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        blockers = assess(fetch_release(args.base_url))
    except ReadinessError as error:
        raise SystemExit(f"next-MVP readiness check failed closed: {error}") from error
    if blockers:
        raise SystemExit("next-MVP activation blocked: " + "; ".join(blockers))
    print(f"next-MVP release {RELEASE_SHA} is externally ready")


if __name__ == "__main__":
    main()
