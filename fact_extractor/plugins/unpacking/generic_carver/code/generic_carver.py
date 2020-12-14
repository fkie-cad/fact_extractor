'''
This plugin unpacks all files via carving
'''
import logging
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
    screening_logs = []

    for file_path in binwalk_root.iterdir():
        file_type = magic.from_file(str(file_path), mime=True)

        if 'application/x-tar' in file_type:
            screening_logs.append(check_archives_validity(file_path, 'tar -tvf {}', 'does not look like a tar archive'))

        elif 'application/x-xz' in file_type:
            screening_logs.append(check_archives_validity(file_path, 'xz -c -d {} | wc -c', 0))

        elif 'application/gzip' in file_type:
            screening_logs.append(check_archives_validity(file_path, 'gzip - l {}', 'not in gzip format'))

        elif 'application/zip' in file_type or 'application/x-7z-compressed' in file_type or 'application/x-lzma' in file_type:
            result_not_archive = check_archives_validity(file_path, '7z l {}', 'ERROR')
            if result_not_archive is not None:
                screening_logs.append(result_not_archive)

    return screening_logs


def check_archives_validity(file_path, command, search_key):
    output = execute_shell_command(command.format(file_path))

    if isinstance(search_key, str):
        if search_key in output.replace('\n ', ''):
            file_path.unlink()
            screening_log = '{} was removed'.format(str(file_path).rsplit('/', 1)[-1])
            return screening_log

    elif isinstance(search_key, int):
        if search_key != output:
            file_path.unlink()
            screening_log = '{} was removed'.format(str(file_path).rsplit('/', 1)[-1])
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
