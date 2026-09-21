"""Deliver Codex's two auth reads across stdin prompt resolution."""

import errno
import os
import select
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable


# In Codex 0.154.0, cloud configuration and the in-process execution server
# each construct their own AuthManager before the exec prompt is submitted.
STARTUP_AUTH_READS = 2


class CodexHomeCleanupError(Exception):
    """Ephemeral Codex state could not be completely removed."""


@contextmanager
def isolated_codex_home(prefix: str):
    """Remove transient Codex state despite short-lived background file writes."""
    home = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield str(home)
    finally:
        deadline = time.monotonic() + 3
        while True:
            try:
                shutil.rmtree(home)
                break
            except FileNotFoundError as exc:
                if not home.exists():
                    break
                if time.monotonic() >= deadline:
                    raise CodexHomeCleanupError() from exc
                time.sleep(0.05)
            except OSError as exc:
                if exc.errno != errno.ENOTEMPTY or time.monotonic() >= deadline:
                    raise CodexHomeCleanupError() from exc
                time.sleep(0.05)


def submit_stdin_prompt(
    proc: subprocess.Popen,
    prompt: str,
    remaining: Callable[[], float],
) -> None:
    """Write the full UTF-8 prompt and EOF within the admitted time budget."""
    if proc.stdin is None:
        raise RuntimeError("Codex stdin is unavailable")
    fd = proc.stdin.fileno()
    data = prompt.encode("utf-8")
    os.set_blocking(fd, False)
    written = 0
    while written < len(data):
        if proc.poll() is not None:
            raise RuntimeError("Codex terminated before accepting the prompt")
        if not select.select([], [fd], [], remaining())[1]:
            raise subprocess.TimeoutExpired("codex stdin", 0)
        try:
            count = os.write(fd, data[written:written + 65536])
        except BlockingIOError:
            continue
        if count == 0:
            raise RuntimeError("Codex stdin stopped accepting the prompt")
        written += count
    proc.stdin.close()
    proc.stdin = None


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
