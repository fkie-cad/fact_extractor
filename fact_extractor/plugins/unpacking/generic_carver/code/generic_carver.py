'''
This plugin unpacks all files via carving
'''
import logging
import os
import shutil
from pathlib import Path
import magic

from common_helper_process import execute_shell_command

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.8'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''

    logging.debug('File Type unknown: execute binwalk on {}'.format(file_path))
    output = execute_shell_command('binwalk --extract --carve --signature --directory  {} {}'.format(tmp_dir, file_path))

    drop_underscore_directory(tmp_dir)
    screening_meta = remove_false_positive_archives(file_path, tmp_dir)

    return {'output': output, 'screening': screening_meta}


def remove_false_positive_archives(original_filename: str, unpack_directory: str) -> str:
    binwalk_root = Path(unpack_directory) / f'_{original_filename}.extracted'
    if not binwalk_root.exists() or not binwalk_root.is_dir():
        return 'No files extracted, so nothing removed'
    screening_log = ''

    for file_path in binwalk_root.iterdir():
        file_type = magic.from_file(str(file_path), mime=True)

        if 'zip' in file_type:
            output_unzip = execute_shell_command('unzip -l {}'.format(file_path))
            if 'not a zipfile' in output_unzip.replace('\n ', ''):
                os.remove(file_path)
                screening_log = 'file was not a zipfile and was removed'
            else:
                screening_log = 'file seems to be a valid archive'

        elif 'x-tar' in file_type or 'gzip' in file_type or 'x-lzip' in file_type or 'x-bzip2' in file_type or 'x-xz' in file_type:
            output_tar = execute_shell_command('tar -tvf {}'.format(file_path))
            if 'does not look like a tar archive' in output_tar:
                os.remove(file_path)
                screening_log = 'file does not look like a valid archive and was removed'
            else:
                screening_log = 'file seems to be a valid archive'

        # elif 'x-lrzip' in file_type or or 'rzip' in file_type or 'x-lz4' in file_type:

        elif 'x-7z-compressed' in file_type or 'x-compress' in file_type:
            output_7z = execute_shell_command('7z l {}'.format(file_path))
            if 'Is not archive' in output_7z or 'Can not open the file as [7z] archive' in output_7z:
                os.remove(file_path)
                screening_log = 'file is not a valid archive and was removed'
            else:
                screening_log = 'file seems to be a valid archive'

        else:
            screening_log = 'archive type not supported yet'

    return screening_log


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
