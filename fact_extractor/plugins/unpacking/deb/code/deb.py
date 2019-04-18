'''
This plugin unpacks debian packages
'''
import logging

from common_helper_process import execute_shell_command_get_return_code

NAME = 'Deb'
MIME_PATTERNS = ['application/vnd.debian.binary-package']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    output, return_code = execute_shell_command_get_return_code('fakeroot dpkg-deb -v -x {} {}'.format(file_path, tmp_dir))
    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))
    meta_data = {'output': output, 'return_code': return_code }
    logging.debug(output)
    return meta_data

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
