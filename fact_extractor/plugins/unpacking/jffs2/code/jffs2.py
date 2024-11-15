"""
This plugin unpacks JFFS2 filesystem images
"""

import logging
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'JFFS2'
MIME_PATTERNS = ['filesystem/jffs2', 'filesystem/jffs2-big']
VERSION = '0.5'


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    local_tmp_dir should be used to store the extracted files.
    """

    extract_dir = Path(tmp_dir) / 'jffs-root'
    output = execute_shell_command(f'fakeroot jefferson -v -d {extract_dir} {file_path}') + '\n'
    meta_data = {'output': output}
    logging.debug(output)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
