"""
    shell_utils.py

    Shell/subprocess-related utility functions
"""
import shlex


def shell_escape_string(shell_string: str) -> str:
    """Returns the shell-escaped version of the provided string, if not already escaped

    This is a workaround for the fact that subprocess.check_output() and friends don't
    properly escape spaces in file paths, and instead just pass the path to the shell.

    Also calling this multiple times on the same string should be idempotent, which
    shlex.quote() is not."""
    shell_string_to_escape = shell_string.strip()
    if len(shlex.split(shell_string_to_escape)) == 1:
        shell_string_to_escape = shlex.split(shell_string_to_escape)[0]
    return shlex.quote(shell_string_to_escape)
