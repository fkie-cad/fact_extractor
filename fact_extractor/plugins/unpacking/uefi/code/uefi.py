'''
This plugin unpacks UEFI Firmware Container.
'''
import os

from common_helper_process import execute_shell_command
from helperFunctions.fileSystem import get_faf_bin_dir

NAME = 'UEFI'
MIME_PATTERNS = ['firmware/uefi']
VERSION = '0.5'

TOOL_PATH = os.path.join(get_faf_bin_dir(), 'uefi-firmware-parser')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    extraction_command = 'python2 {} --superbrute --extract --output {} {}'.format(TOOL_PATH, tmp_dir, file_path)
    output = execute_shell_command(extraction_command)
    return {'output': output}


# ----> Do not edit below this line <----

def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
