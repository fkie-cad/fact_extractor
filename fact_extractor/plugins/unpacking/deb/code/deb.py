'''
This plugin unpacks debian packages
'''
from common_helper_process import execute_shell_command

NAME = 'Deb'
MIME_PATTERNS = ['application/vnd.debian.binary-package']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    return {'output': execute_shell_command('fakeroot dpkg-deb -v -x {} {}'.format(file_path, tmp_dir))}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
