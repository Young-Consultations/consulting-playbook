#!/usr/bin/env python3
"""Offline executable checks for the protected authentication probe."""

from __future__ import annotations

import io
import os
import subprocess
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import probe_production_codex_auth as probe


FAKE_CODEX = '''#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
home = Path(os.environ["CODEX_HOME"])
trace = Path(%r)
if sys.argv[1] == "login":
    (home / "auth.json").write_text(json.dumps({"OPENAI_API_KEY": sys.stdin.read()}))
elif sys.argv[1] == "exec":
    assert sys.argv[sys.argv.index("--sandbox") + 1] == "read-only"
    if %r:
        time.sleep(2)
    time.sleep(0.05)  # Force the ENXIO race before the FIFO reader opens.
    for index in range(2):
        assert json.loads((home / "auth.json").read_text())["OPENAI_API_KEY"] == "sentinel"
        with trace.open("a") as stream:
            stream.write("auth-consumed\\n")
    prompt = sys.stdin.read()
    with trace.open("a") as stream:
        stream.write("prompt-received\\n")
    assert prompt == "Do not use tools. Reply with AUTHENTICATED only."
    if %r:
        time.sleep(2)
    print("AUTHENTICATED")
else:
    sys.exit(2)
'''


def exercise(*, stall: bool = False, stall_before_auth: bool = False,
             timeout: float = 3) -> tuple[int, str, list[str]]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        executable = root / "codex"
        trace = root / "trace"
        executable.write_text(FAKE_CODEX % (str(trace), stall_before_auth, stall), encoding="utf-8")
        executable.chmod(0o700)
        captured = io.StringIO()
        with (
            patch.dict(os.environ, {"PATH": f"{root}:{os.environ['PATH']}"}),
            patch.object(probe, "_bootstrap_secret_environment"),
            patch.object(probe, "_take_optional_secret", return_value="sentinel"),
            redirect_stdout(captured),
        ):
            outcome = probe.main(timeout)
        return outcome, captured.getvalue(), trace.read_text().splitlines() if trace.exists() else []


def test_fifo_race_and_prompt_order() -> None:
    outcome, output, events = exercise()
    assert outcome == 0 and "probe passed" in output
    assert events == ["auth-consumed", "auth-consumed", "prompt-received"]


def test_provider_timeout_is_bounded() -> None:
    outcome, output, events = exercise(stall=True, timeout=0.3)
    assert outcome == 1 and "stage=probe; category=timeout" in output
    assert "sentinel" not in output
    assert events == ["auth-consumed", "auth-consumed", "prompt-received"]


def test_fifo_handoff_timeout_is_bounded() -> None:
    outcome, output, events = exercise(stall_before_auth=True, timeout=0.3)
    assert outcome == 1 and "stage=auth-handoff; category=timeout" in output
    assert "sentinel" not in output and events == []


def test_login_timeout_is_bounded() -> None:
    captured = io.StringIO()
    with (
        patch.object(probe, "_bootstrap_secret_environment"),
        patch.object(probe, "_take_optional_secret", return_value="sentinel"),
        patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("codex login", 1)),
        redirect_stdout(captured),
    ):
        assert probe.main(1) == 1
    assert "stage=login; category=timeout" in captured.getvalue()
    assert "sentinel" not in captured.getvalue()


if __name__ == "__main__":
    test_fifo_race_and_prompt_order()
    test_provider_timeout_is_bounded()
    test_fifo_handoff_timeout_is_bounded()
    test_login_timeout_is_bounded()
    print("passed 4 production-auth probe checks")
