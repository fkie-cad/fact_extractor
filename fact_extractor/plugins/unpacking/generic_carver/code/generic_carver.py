'''
This plugin unpacks all files via carving
'''
import logging

from common_helper_process import execute_shell_command_get_return_code

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.7'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''

    logging.debug('File Type unknown: execute binwalk on {}'.format(file_path))
    output, return_code = execute_shell_command_get_return_code('binwalk --extract --carve --signature --directory  {} {}'.format(tmp_dir, file_path))
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
