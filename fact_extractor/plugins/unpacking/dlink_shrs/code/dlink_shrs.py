'''
This plugin decrypts D-Link SHRS binaries.
'''
from subprocess import PIPE, STDOUT, run
from pathlib import Path
from shlex import split


NAME = 'D-Link SHRS'
MIME_PATTERNS = ['firmware/dlink-shrs']
VERSION = '0.1.1'

TOOL_PATH = Path(__file__).parent.parent / 'internal/decrypt_dlink.py'


def unpack_function(file_path, tmp_dir):
    decrypted_file = Path(tmp_dir, 'decrypted_image')

    extraction_command = f'python3 {TOOL_PATH} -i {file_path} -o {decrypted_file}'
    process = run(split(extraction_command), stdout=PIPE, stderr=STDOUT, text=True, check=False)
    return {'output': process.stdout}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
