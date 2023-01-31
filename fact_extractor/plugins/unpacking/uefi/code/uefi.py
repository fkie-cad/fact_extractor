'''
This plugin unpacks UEFI Firmware Container.
'''

from common_helper_process import execute_shell_command

NAME = 'UEFI'
MIME_PATTERNS = ['firmware/uefi']
VERSION = '0.6'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    extraction_command = f'uefi-firmware-parser --superbrute --extract --output {tmp_dir} {file_path}'
    output = execute_shell_command(extraction_command)
    return {'output': output}


# ----> Do not edit below this line <----

def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
