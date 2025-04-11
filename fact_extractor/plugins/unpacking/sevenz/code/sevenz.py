"""
This plugin uses 7z to extract several formats
"""

from __future__ import annotations

import contextlib
import logging
import re
from lzma import FORMAT_AUTO, LZMADecompressor, LZMAError
from pathlib import Path

from common_helper_passwords import get_merged_password_set
from common_helper_process import execute_shell_command

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

# Empty password must be first in list to correctly detect if archive has no password
PW_LIST = ['']
PW_LIST.extend(get_merged_password_set(Path(get_src_dir()) / 'unpacker/passwords'))
TAIL_REGEX = re.compile(r'Tail Size = (\d+)')


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
