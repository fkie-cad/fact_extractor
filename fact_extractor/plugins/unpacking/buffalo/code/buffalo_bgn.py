import re
from pathlib import Path
from shlex import split
from subprocess import CompletedProcess, run

from helperFunctions.file_system import get_fact_bin_dir

NAME = 'buffalo_bgn'
MIME_PATTERNS = ['firmware/buffalo']
VERSION = '0.1.0'

TOOL_PATH = Path(get_fact_bin_dir()) / 'buffalo-enc'
FILE_MAGIC_REGEX = re.compile(rb'start\x00')


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    output = ''
    input_file = Path(file_path)
    contents = input_file.read_bytes()

    for match in FILE_MAGIC_REGEX.finditer(contents):
        offset = match.start()
        output += f'Found file header at offset {offset}\n'
        output += _decrypt_file(input_file, offset, Path(tmp_dir) / f'{hex(offset)}.decrypted')
    return {'output': output}


def _decrypt_file(file: Path, offset: int, target: Path) -> str:
    output = ''
    command = f'{TOOL_PATH} -d -O {offset} -i {file} -o {target}'
    # first try normal mode
    proc = _run(command)
    if proc.returncode != 0:
        # try "longstate" mode if decryption failed
        output += 'Unpacking failed. Trying longstate mode...\n'
        proc = _run(f'{command} -l')
        if proc.returncode != 0:
            output += proc.stderr
            output += 'Unpacking failed.\n'
        else:
            output += proc.stdout + '\n'
    else:
        output += proc.stdout + '\n'
    return output


def _run(command: str) -> CompletedProcess:
    return run(split(command), check=False, capture_output=True, text=True)


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
