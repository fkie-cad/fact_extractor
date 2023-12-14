'''
This plugin unpacks StuffIt files (.sit, .sitx)
'''
from common_helper_process import execute_shell_command
from helperFunctions.shell_utils import shell_escape_string

NAME = 'StuffItFile'
MIME_PATTERNS = ['application/x-stuffit', 'application/x-sit', 'application/x-stuffitx', 'application/x-sitx']
VERSION = '0.3'

STUFFIT_UNPACKER = 'unar'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    output = execute_shell_command('fakeroot {} -o {} {}'.format(STUFFIT_UNPACKER, shell_escape_string(str(tmp_dir)), shell_escape_string(str(file_path))))
    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
