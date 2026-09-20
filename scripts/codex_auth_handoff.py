"""Deliver Codex's two auth reads across stdin prompt resolution."""

import errno
import os
import subprocess
import time
from pathlib import Path
from typing import Callable


# In Codex 0.154.0, cloud configuration and the in-process execution server
# each construct their own AuthManager before the exec prompt is submitted.
STARTUP_AUTH_READS = 2


def handoff_startup_auth(
    auth_path: Path,
    payload: bytes,
    proc: subprocess.Popen,
    remaining: Callable[[], float],
    submit_prompt: Callable[[], None],
) -> None:
    """Serve config auth, close stdin, then serve execution auth before tools."""
    try:
        for index in range(STARTUP_AUTH_READS):
            while True:
                if proc.poll() is not None:
                    raise RuntimeError("Codex terminated during authentication")
                try:
                    fd = os.open(auth_path, os.O_WRONLY | os.O_NONBLOCK)
                    break
                except OSError as exc:
                    if exc.errno != errno.ENXIO:
                        raise
                    if remaining() < 0.01:
                        raise subprocess.TimeoutExpired("codex auth", 0)
                    time.sleep(0.01)
            with os.fdopen(fd, "wb", buffering=0) as fifo:
                # The reader is now attached to this inode. Publish the next
                # FIFO before this writer can close and release the reader.
                auth_path.unlink()
                if index + 1 < STARTUP_AUTH_READS:
                    os.mkfifo(auth_path, 0o600)
                fifo.write(payload)
            if index == 0:
                # `codex exec -` reads stdin to EOF before it starts the
                # in-process server that performs the second auth read.
                submit_prompt()
    finally:
        auth_path.unlink(missing_ok=True)
