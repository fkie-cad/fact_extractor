"""
This plugin uses 7z to extract several formats
"""

from __future__ import annotations

import contextlib
import logging
import re
from lzma import FORMAT_AUTO, LZMADecompressor, LZMAError
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
    'application/x-arj',
    'application/x-iso9660-image',
    'application/x-lzma',
    'application/x-rar',
    'application/x-rpm',
    'application/x-vhd',
    'application/x-vhdx',
    'application/x-xar',
    'application/x-xz',
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
VERSION = '0.12.0'

UNPACKER_EXECUTABLE = '7zzs'
ZISOFS_MAGIC = bytes.fromhex('37 E4 53 96 C9 DB D6 07')
ZISOFS_MAGIC_SIZE = len(ZISOFS_MAGIC)

# Empty password must be first in list to correctly detect if the archive has no password
PW_LIST_DIR = Path(get_src_dir()) / 'unpacker/passwords'
PW_LIST = sorted(get_merged_password_set(str(PW_LIST_DIR)).union({''}))
TAIL_REGEX = re.compile(r'Tail Size = (\d+)')


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
        output = execute_shell_command(f'fakeroot {UNPACKER_EXECUTABLE} x -y -p{password} -o{tmp_dir} {file_path}')

        meta['output'] = output
        if 'Wrong password' in output:
            continue
        if password:
            meta['password'] = password
        if _contains_trailing_data(output):
            _store_trailing_data(output, file_path, output_path=Path(tmp_dir) / 'trailing_data')
        break

    # Inform the user if no correct password was found
    if 'Wrong password' in meta['output']:
        logging.warning(f'Password for {file_path} not found in fact_extractor/unpacker/passwords directory')

    # files in iso9660 can optionally be compressed with zisofs (which does not get decompressed by 7z)
    if magic.from_file(file_path, mime=True) == 'application/x-iso9660-image':
        count = _uncompress_zisofs(Path(tmp_dir))
        meta['output'] += f'\n\nunpacked {count} zisofs compressed files'

    return meta


def _contains_trailing_data(output: str) -> bool:
    return (
        'There are some data after the end of the payload data' in output
        or 'There are data after the end of archive' in output
    )


def _store_trailing_data(output: str, input_file: str, output_path: Path):
    # there is some data at the end of the file that does not belong to the compressed stream/archive
    # we must save this data so that is does not get lost
    contents = Path(input_file).read_bytes()
    offset = 0
    if 'Type = lzma' in output:
        offset = _find_trailing_data_offset(contents, LZMADecompressor(FORMAT_AUTO))
    elif match := TAIL_REGEX.search(output):
        # for some types (e.g. ZIP) the 7z output contains "Tail Size = X" which tells us the size of the trailing data
        offset = len(contents) - int(match.group(1))
    if offset != 0:
        output_path.write_bytes(contents[offset:])


def _find_trailing_data_offset(contents: bytes, decompressor: LZMADecompressor) -> int:
    # FixMe: the only practical way for finding the end of a compression stream like LZMA is to follow it to its end and
    #        since 7z does not log the offset, we need to unpack it again
    with contextlib.suppress(LZMAError):
        decompressor.decompress(contents)
    if decompressor.eof and len(decompressor.unused_data) > 0:
        return len(contents) - len(decompressor.unused_data)
    return 0


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
