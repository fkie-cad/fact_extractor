'''
This plugin unpacks UEFI Firmware Container.
'''
import logging
import os

from common_helper_process import execute_shell_command_get_return_code
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'UEFI'
MIME_PATTERNS = ['firmware/uefi']
VERSION = '0.5'

TOOL_PATH = os.path.join(get_fact_bin_dir(), 'uefi-firmware-parser')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    extraction_command = 'python2 {} --superbrute --extract --output {} {}'.format(TOOL_PATH, tmp_dir, file_path)
    output, return_code = execute_shell_command_get_return_code(extraction_command)
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    return meta_data

# ----> Do not edit below this line <----

def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
