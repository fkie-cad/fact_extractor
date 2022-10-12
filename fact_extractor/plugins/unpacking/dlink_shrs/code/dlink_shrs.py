'''
This plugin decrypts D-Link SHRS binaries.
'''
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'D-Link SHRS'
MIME_PATTERNS = ['firmware/dlink-shrs']
VERSION = '0.1'

TOOL_PATH = Path(__file__).parent.parent / 'internal/decrypt_dlink.py'


def unpack_function(file_path, tmp_dir):
    decrypted_file = Path(tmp_dir, 'decrypted_image')

    extraction_command = 'python3 {} -i {} -o {}'.format(TOOL_PATH, file_path, decrypted_file)
    output = execute_shell_command(extraction_command)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
