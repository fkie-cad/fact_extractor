'''
This plugin unpacks all files via carving
'''
import logging
import shutil
from pathlib import Path

from common_helper_process import execute_shell_command

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.7'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''

    logging.debug('File Type unknown: execute binwalk on {}'.format(file_path))
    output = execute_shell_command('binwalk --extract --carve --signature --directory  {} {}'.format(tmp_dir, file_path))

    drop_underscore_directory(tmp_dir)

    return {'output': output}


def drop_underscore_directory(tmp_dir):
    extracted_contents = list(Path(tmp_dir).iterdir())
    if not extracted_contents:
        return
    if not len(extracted_contents) == 1 or not extracted_contents[0].name.endswith('.extracted'):
        return
    for result in extracted_contents[0].iterdir():
        shutil.move(str(result), str(result.parent.parent))
    shutil.rmtree(str(extracted_contents[0]))


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
