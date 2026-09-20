#!/usr/bin/env python3
"""Probe the target's one-read auth handoff without publication credentials."""

from __future__ import annotations

import errno
import os
import subprocess
import tempfile
import time
from pathlib import Path

from codex_target_adapter import ROOT, SAFE_ENV, _bootstrap_secret_environment, _take_optional_secret


PROMPT = "Do not use tools. Reply with AUTHENTICATED only."


def fail(stage: str, category: str) -> int:
    print(f"::error title=Production auth probe failed::stage={stage}; category={category}")
    return 1


def main(timeout_seconds: float = 120) -> int:
    _bootstrap_secret_environment()
    api_key = _take_optional_secret("OPENAI_API_KEY")
    if not api_key:
        return fail("credential-check", "missing-credential")
    deadline = time.monotonic() + timeout_seconds

    def remaining() -> float:
        seconds = deadline - time.monotonic()
        if seconds <= 0:
            raise subprocess.TimeoutExpired("codex", timeout_seconds)
        return seconds

    with tempfile.TemporaryDirectory(prefix="codex-target-probe-") as codex_home:
        env = {key: value for key, value in os.environ.items() if key in SAFE_ENV}
        env["CODEX_HOME"] = codex_home
        try:
            login = subprocess.run(
                ["codex", "login", "--with-api-key"], input=api_key, text=True,
                cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=remaining(),
            )
        except subprocess.TimeoutExpired:
            return fail("login", "timeout")
        finally:
            api_key = ""
        if login.returncode:
            return fail("login", "authentication")

        # Mirror the production adapter's FIFO lifetime and handoff. The
        # probe runs read-only with a fixed prompt and no publication token.
        auth_path = Path(codex_home) / "auth.json"
        try:
            auth_payload = auth_path.read_bytes()
            auth_path.unlink()
            os.mkfifo(auth_path, 0o600)
        except OSError:
            return fail("auth-handoff", "authentication")
        proc = subprocess.Popen(
            ["codex", "exec", "--model", "gpt-5.3-codex", "--sandbox", "read-only",
             "-C", str(ROOT), "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=ROOT, env=env,
        )
        fifo_fd = None
        try:
            while fifo_fd is None:
                if proc.poll() is not None:
                    return fail("auth-handoff", "authentication")
                try:
                    fifo_fd = os.open(auth_path, os.O_WRONLY | os.O_NONBLOCK)
                except OSError as exc:
                    if exc.errno != errno.ENXIO:
                        return fail("auth-handoff", "authentication")
                    remaining()
                    time.sleep(0.01)
            auth_path.unlink()
            with os.fdopen(fifo_fd, "wb", buffering=0) as fifo:
                fifo_fd = None
                fifo.write(auth_payload)
            auth_payload = b""
            response, diagnostic = proc.communicate(
                input=PROMPT, timeout=remaining(),
            )
        except subprocess.TimeoutExpired:
            return fail("probe" if auth_payload == b"" else "auth-handoff", "timeout")
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            if fifo_fd is not None:
                os.close(fifo_fd)
            auth_path.unlink(missing_ok=True)

    if proc.returncode:
        category = "authentication" if "401 Unauthorized" in diagnostic else "codex-runtime"
        return fail("probe", category)
    if response.strip() != "AUTHENTICATED":
        return fail("probe", "unexpected-response")
    print("::notice title=Production auth probe passed::Provider response completed through the one-read handoff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
