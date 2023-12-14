from os import path

from common_helper_process import execute_shell_command
from helperFunctions.file_system import get_fact_bin_dir
from helperFunctions.shell_utils import shell_escape_string

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
    output = execute_shell_command('fakeroot {} {} {}'.format(unpacker, shell_escape_string(str(file_path)), shell_escape_string(str(tmp_dir))))
    return {'output': output}


def _is_big_endian(file_path):
    with open(file_path, 'br') as fp:
        content = fp.read(10)
        big_endian = content[7:] == b'\x01\xFF\xFF'
    return big_endian


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
