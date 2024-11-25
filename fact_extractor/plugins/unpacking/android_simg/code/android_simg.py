"""
This plugin "unpacks" Android sparse image by converting them to regular filesystem images using the simg2img tool
"""

import logging
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'Android-sparse-image'
MIME_PATTERNS = ['filesystem/android-simg']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    extract_dir = Path(tmp_dir)
    file_to_unpack = Path(file_path)
    output = execute_shell_command(f'simg2img {file_path} {extract_dir / file_to_unpack.name}.raw') + '\n'
    meta_data = {'output': output}
    logging.debug(output)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
