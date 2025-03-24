"""
This plugin uses 7z to extract several formats
"""

import logging
from pathlib import Path

from common_helper_files.fail_safe_file_operations import _iterate_path_recursively
from common_helper_passwords import get_merged_password_set
from common_helper_process import execute_shell_command

from helperFunctions import magic
from helperFunctions.file_system import get_src_dir

NAME = '7z'
MIME_PATTERNS = [
    # compressed archives
    'application/gzip',
    'application/rar',
    'application/x-7z-compressed',
    'application/x-gzip',
    'application/x-iso9660-image',
    'application/x-lzma',
    'application/x-rar',
    'application/x-rpm',
    'application/x-vhd',
    'application/x-vhdx',
    'application/x-zip-compressed',
    'application/zip',
    # file systems
    'filesystem/cramfs',
    'filesystem/ext2',
    'filesystem/ext3',
    'filesystem/ext4',
    'filesystem/fat',
    'filesystem/hfs',
    'filesystem/ntfs',
]
VERSION = '0.9.0'

UNPACKER_EXECUTABLE = '7z'
ZISOFS_MAGIC = bytes.fromhex('37 E4 53 96 C9 DB D6 07')
ZISOFS_MAGIC_SIZE = len(ZISOFS_MAGIC)

# Empty password must be first in list to correctly detect if archive has no password
PW_LIST = ['']
PW_LIST.extend(get_merged_password_set(Path(get_src_dir()) / 'unpacker/passwords'))


def _uncompress_zisofs(tmp_dir: Path) -> int:
    count = 0
    for file in _iterate_path_recursively(tmp_dir, include_symlinks=False, include_directories=False):
        if _is_zisofs_compressed(file):
            # in-place extraction is not supported so we extract to a temporary file and replace the original one
            outfile = file.with_suffix('.tmp')
            execute_shell_command(f'mkzftree -u -F {file} {outfile}')
            outfile.replace(file)
            count += 1
    return count


def _is_zisofs_compressed(file: Path) -> bool:
    with file.open('rb') as fp:
        fp.seek(0)
        return fp.read(ZISOFS_MAGIC_SIZE) == ZISOFS_MAGIC


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    meta = {}
    for password in PW_LIST:
        execution_string = f'fakeroot {UNPACKER_EXECUTABLE} x -y -p{password} -o{tmp_dir} {file_path}'
        output = execute_shell_command(execution_string)

        meta['output'] = output
        if 'Wrong password' not in output:
            if password:
                meta['password'] = password
            break

    # Inform the user if no correct password was found
    if 'Wrong password' in meta['output']:
        logging.warning(f'Password for {file_path} not found in fact_extractor/unpacker/passwords directory')

    # files in iso9660 can optionally be compressed with zisofs (which does not get decompressed by 7z)
    if magic.from_file(file_path, mime=True) == 'application/x-iso9660-image':
        count = _uncompress_zisofs(Path(tmp_dir))
        meta['output'] += f'\n\nunpacked {count} zisofs compressed files'

    return meta


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
