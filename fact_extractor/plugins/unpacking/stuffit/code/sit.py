'''
This plugin unpacks StuffIt files (.sit, .sitx)
'''
import logging

from common_helper_process import execute_shell_command_get_return_code

NAME = 'StuffItFile'
MIME_PATTERNS = ['application/x-stuffit', 'application/x-sit', 'application/x-stuffitx', 'application/x-sitx']
VERSION = '0.3'

STUFFIT_UNPACKER = 'unar'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    output, return_code = execute_shell_command_get_return_code('fakeroot {} -o {} {}'.format(STUFFIT_UNPACKER, tmp_dir, file_path))
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    return meta_data

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
