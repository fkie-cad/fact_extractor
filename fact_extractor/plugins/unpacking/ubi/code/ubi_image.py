'''
This plugin unpacks ubi images
'''
from common_helper_process import execute_shell_command

NAME = 'UBI-Image'
MIME_PATTERNS = ['firmware/ubi-image']
VERSION = '0.2'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    local_tmp_dir should be used to store the extracted files.
    '''
    output = execute_shell_command('fakeroot ubireader_extract_images -v --output-dir {} {}'.format(tmp_dir, file_path)) + '\n'
    meta_data = {'output': output}
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
