
import logging
import os
from shutil import copyfile

from common_helper_process import execute_shell_command, execute_shell_command_get_return_code
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'tpl-tool'
MIME_PATTERNS = ['firmware/tp-link']
VERSION = '0.3'
UNPACKER_EXECUTEABLE = os.path.join(get_fact_bin_dir(), 'tpl-tool')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    # tpl-tool unpacker unpacks files in the directory of the input file -> copy input file and delete afterwards
    tmp_file_path = os.path.join(tmp_dir, os.path.basename(file_path))
    copyfile(file_path, tmp_file_path)

    output, return_code = execute_shell_command_get_return_code('fakeroot {} -x {}'.format(UNPACKER_EXECUTEABLE, tmp_file_path))
    header = execute_shell_command('{} -s {}'.format(UNPACKER_EXECUTEABLE, tmp_file_path))
    os.remove(tmp_file_path)
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'header-info': header, 'return_code': return_code}
    logging.debug(output)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
