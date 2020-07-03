'''
This plugin uses 7z to extract several formats
'''
import os
import logging

from common_helper_passwords import get_merged_password_set
from common_helper_process import execute_shell_command
from helperFunctions.file_system import get_src_dir

NAME = '7z'
MIME_PATTERNS = ['application/x-lzma', 'application/x-7z-compressed', 'application/zip', 'application/x-zip-compressed']
VERSION = '0.7'

UNPACKER_EXECUTEABLE = '7z'
PW_LIST = get_merged_password_set(os.path.join(get_src_dir(), 'unpacker/passwords'))


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    meta = {}
    for password in PW_LIST:
        execution_string = 'fakeroot {} x -y -p{} -o{} {}'.format(UNPACKER_EXECUTEABLE, password, tmp_dir, file_path)
        output = execute_shell_command(execution_string)

        meta['output'] = output
        if 'Wrong password' not in output:
            if 'AES' in output:
                meta['password'] = password
            break

    # Inform the user if not correct password was found
    if 'Wrong password' in meta['output']:
        logging.warn('Password for {} not found in fact_extractor/unpacker/passwords directory'.format(file_path))

    return meta


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
