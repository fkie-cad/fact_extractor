"""
This plugin unpacks ubi filesystem images
"""

import logging

from common_helper_process.fail_safe_subprocess import execute_shell_command

NAME = 'UBIFS'
MIME_PATTERNS = ['filesystem/ubifs']
VERSION = '0.3'


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    local_tmp_dir should be used to store the extracted files.
    """
    output = execute_shell_command(f'fakeroot ubireader_extract_files -v --output-dir {tmp_dir} {file_path}') + '\n'

    meta_data = {'output': output}
    logging.debug(output)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
