import logging
from os import path

from common_helper_process import execute_shell_command_get_return_code
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'YAFFS'
MIME_PATTERNS = ['filesystem/yaffs']
VERSION = '0.4'

UNYAFFS_EXECUTEABLE = '/usr/bin/unyaffs'
UNYAFFS2_EXECUTEABLE = path.join(get_fact_bin_dir(), 'unyaffs2')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    unpacker = '{} -e'.format(UNYAFFS2_EXECUTEABLE) if _is_big_endian(file_path) else '{} -v'.format(UNYAFFS_EXECUTEABLE)
    output, return_code = execute_shell_command_get_return_code('fakeroot {} {} {}'.format(unpacker, file_path, tmp_dir))
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    return meta_data

def _is_big_endian(file_path):
    with open(file_path, 'br') as fp:
        content = fp.read(10)
        big_endian = content[7:] == b'\x01\xFF\xFF'
    return big_endian


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
