import os
from shutil import copyfile

from common_helper_process import execute_shell_command
from helperFunctions.fileSystem import get_faf_bin_dir

NAME = 'tpl-tool'
MIME_PATTERNS = ['firmware/tp-link']
VERSION = '0.3'
UNPACKER_EXECUTEABLE = os.path.join(get_faf_bin_dir(), 'tpl-tool')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    # tpl-tool unpacker unpacks files in the directory of the input file -> copy input file and delete afterwards
    tmp_file_path = os.path.join(tmp_dir, os.path.basename(file_path))
    copyfile(file_path, tmp_file_path)

    result = {}

    result['output'] = execute_shell_command('fakeroot {} -x {}'.format(UNPACKER_EXECUTEABLE, tmp_file_path))
    result['header-info'] = execute_shell_command('{} -s {}'.format(UNPACKER_EXECUTEABLE, tmp_file_path))

    os.remove(tmp_file_path)

    return result


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
