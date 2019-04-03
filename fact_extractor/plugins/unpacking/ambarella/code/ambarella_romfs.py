
from os import path

from common_helper_process import execute_shell_command
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'Ambarella_RomFS'
MIME_PATTERNS = ['filesystem/ambarella-romfs']
VERSION = '0.3'

TOOL_PATH = path.join(get_fact_bin_dir(), "amba_romfs.py")


def unpack_function(file_path, tmp_dir):
    if not path.exists(TOOL_PATH):
        return {'output': "Error: phantom_firmware_tools not installed! Re-Run the installation script!"}

    output = execute_shell_command('(cd {} && fakeroot {} -x -vv -p {})'.format(tmp_dir, TOOL_PATH, file_path)) + "\n"
    meta_data = {'output': output}
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
