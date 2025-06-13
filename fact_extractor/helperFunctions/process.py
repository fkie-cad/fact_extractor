from __future__ import annotations

from shlex import split
from subprocess import PIPE, STDOUT, run

from helperFunctions.file_system import get_environ_with_bin_dir


def run_command(command: str, env: dict | None = None, timeout: float = 590):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    _env = get_environ_with_bin_dir()
    if env:
        _env |= env
    proc = run(
        split(command),
        env=_env,
        timeout=timeout,
        stdout=PIPE,
        stderr=STDOUT,
        check=True,
    )
    return proc.stdout.decode(errors='replace').strip()
