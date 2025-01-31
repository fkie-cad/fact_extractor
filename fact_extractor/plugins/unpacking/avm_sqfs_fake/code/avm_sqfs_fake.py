"""
This plugin unpacks avm file system container
"""

from common_helper_process import execute_shell_command

NAME = 'avm_sqfs_fake'
MIME_PATTERNS = ['filesystem/avm-sqfs-fake']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    output = execute_shell_command(f'dd if={file_path} of={tmp_dir}/image.ext2 bs=256 skip=1 conv=sync')
    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
