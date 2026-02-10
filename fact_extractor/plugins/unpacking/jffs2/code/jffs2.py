"""
This plugin unpacks JFFS2 filesystem images
"""

import re
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'JFFS2'
MIME_PATTERNS = ['filesystem/jffs2', 'filesystem/jffs2-big']
VERSION = '0.7.0'
ENTRY_REGEX = re.compile(r'(0x[0-9A-F]{8}): Jffs2_raw_(?:dirent|inode)\(magic=\d+, nodetype=\d+, totlen=(\d+)')


def unpack_function(file_path, tmp_dir):
    tmp_dir_path = Path(tmp_dir)
    output = execute_shell_command(f'fakeroot jefferson -vfd {tmp_dir_path} {file_path}')

    entries = ENTRY_REGEX.findall(output)
    if entries:
        last_offset, length = entries[-1]
        fs_end = int(last_offset, 16) + int(length)
        return {'output': output, 'size': fs_end}

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
