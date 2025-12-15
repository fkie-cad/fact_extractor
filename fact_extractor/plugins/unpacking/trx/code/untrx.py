from os import path
from tempfile import NamedTemporaryFile

from common_helper_process.fail_safe_subprocess import execute_shell_command

from helperFunctions.file_system import get_fact_bin_dir

NAME = 'untrx'
MIME_PATTERNS = ['firmware/trx']
VERSION = '0.4.1'

UNPACKER_EXECUTEABLE = path.join(get_fact_bin_dir(), 'untrx')


def unpack_function(file_path, tmp_dir):
    output = _unpack_trx(file_path, tmp_dir)

    return {'output': output}


def _unpack_trx(file_path, target_dir):
    return execute_shell_command(f'fakeroot {UNPACKER_EXECUTEABLE} {file_path} {target_dir}')


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
