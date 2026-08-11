#!/usr/bin/env python3
"""Unit checks for the immutable release readiness audit."""
from __future__ import annotations

import json

from check_next_mvp_readiness import RELEASE_SHA, REQUIRED_FILES, ReleaseFiles, ReadinessError, assess


def release(*, enabled: bool, receiver: str = "implemented", executable: bool = True) -> ReleaseFiles:
    values = {path: b"{}" for path in REQUIRED_FILES}
    values["config/codex-repositories.json"] = json.dumps(
        {"repositories": [{"repository": "Young-Consultations/consulting-playbook", "enabled": enabled}]}
    ).encode()
    values["tests/fixtures/mvp-v2/manifest.json"] = json.dumps(
        {"id": "TC-MVP-CI-001", "executable": executable}
    ).encode()
    values[".github/workflows/codex-result-receiver.yml"] = receiver.encode()
    return ReleaseFiles(values)


def test_all_release_paths_are_pinned() -> None:
    assert len(RELEASE_SHA) == 40
    assert len(REQUIRED_FILES) == 6


def test_ready_release() -> None:
    assert assess(release(enabled=True)) == []


def test_disabled_registry_blocks() -> None:
    assert "organization registry entry is disabled" in assess(release(enabled=False))


def test_receiver_and_fixtures_block_independently() -> None:
    assert assess(release(enabled=True, receiver="fail-closed\nexit 1", executable=False)) == [
        "organization result receiver is fail-closed",
        "shared executable fixture set is incomplete",
    ]


def test_missing_target_fails_closed() -> None:
    files = release(enabled=True)
    files.values["config/codex-repositories.json"] = b'{"repositories": []}'
    try:
        assess(files)
    except ReadinessError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("missing target did not fail closed")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"passed {len(tests)} next-MVP readiness checks")
