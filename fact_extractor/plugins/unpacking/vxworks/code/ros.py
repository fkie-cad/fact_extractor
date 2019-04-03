import os

from common_helper_process.fail_safe_subprocess import execute_shell_command
from helperFunctions.file_system import get_fact_bin_dir

NAME = 'ROSFile'
MIME_PATTERNS = ['firmware/ros']
VERSION = '0.7'

TOOL_PATH = os.path.join(get_fact_bin_dir(), 'ros_unpack')


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    output = execute_shell_command('(cd {} && fakeroot {} --extract {})'.format(tmp_dir, TOOL_PATH, file_path))
    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
