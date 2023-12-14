'''
This plugin uses 7z to extract several formats
'''
import logging
import os

from common_helper_passwords import get_merged_password_set
from common_helper_process import execute_shell_command
from helperFunctions.shell_utils import shell_escape_string

from helperFunctions.file_system import get_src_dir

NAME = '7z'
MIME_PATTERNS = [
    # compressed archives
    'application/rar',
    'application/x-7z-compressed',
    'application/x-iso9660-image',
    'application/x-lzma',
    'application/x-rar',
    'application/x-rpm',
    'application/x-vhd',
    'application/x-vhdx',
    'application/x-zip-compressed',
    'application/zip',
    # file systems
    'filesystem/cramfs',
    'filesystem/ext2',
    'filesystem/ext3',
    'filesystem/ext4',
    'filesystem/fat',
    'filesystem/hfs',
    'filesystem/ntfs',
]
VERSION = '0.8.1'

UNPACKER_EXECUTABLE = '7z'
PW_LIST = get_merged_password_set(os.path.join(get_src_dir(), 'unpacker/passwords'))


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    meta = {}
    for password in PW_LIST:
        execution_string = f'fakeroot {UNPACKER_EXECUTABLE} x -y -p{password} -o{shell_escape_string(str(tmp_dir))} {shell_escape_string(str(file_path))}'
        output = execute_shell_command(execution_string)

        meta['output'] = output
        if 'Wrong password' not in output:
            if 'AES' in output:
                meta['password'] = password
            break

    # Inform the user if not correct password was found
    if 'Wrong password' in meta['output']:
        logging.warning(f'Password for {file_path} not found in fact_extractor/unpacker/passwords directory')

    return meta


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
