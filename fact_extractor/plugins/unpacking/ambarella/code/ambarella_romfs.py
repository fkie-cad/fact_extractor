
import logging
from os import path

from common_helper_process import execute_shell_command_get_return_code
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'Ambarella_RomFS'
MIME_PATTERNS = ['filesystem/ambarella-romfs']
VERSION = '0.3'

TOOL_PATH = path.join(get_fact_bin_dir(), "amba_romfs.py")


def unpack_function(file_path, tmp_dir):
    if not path.exists(TOOL_PATH):
        return {'output': "Error: phantom_firmware_tools not installed! Re-Run the installation script!"}

    output, return_code = execute_shell_command_get_return_code('(cd {} && fakeroot {} -x -vv -p {})'.format(tmp_dir, TOOL_PATH, file_path))

    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))

    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
