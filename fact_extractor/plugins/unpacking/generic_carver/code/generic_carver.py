'''
This plugin unpacks all files via carving
'''
import json
import logging
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.9'


def unpack_function(file_path, tmp_dir):
    logging.debug(f'File type unknown: Execute unblob on {file_path}')

    temp_file = Path('/tmp/unblob_report.json')
    temp_file.unlink(missing_ok=True)
    output = execute_shell_command(
        f'unblob -sk --report {temp_file.absolute()} --entropy-depth 0 --depth 1 --extract-dir {tmp_dir} {file_path}'
    )
    return {'output': output, 'unblob_meta': json.loads(temp_file.read_text())}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
