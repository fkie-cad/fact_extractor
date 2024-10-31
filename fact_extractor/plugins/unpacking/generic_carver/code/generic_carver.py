"""
This plugin unpacks all files via carving
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

import magic
from common_helper_process import execute_shell_command

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.8'

TAR_MAGIC = b'ustar'
BZ2_EOF_MAGIC = [  # the magic string is only aligned to half bytes -> two possible strings
    b'\x17\x72\x45\x38\x50\x90',
    b'\x77\x24\x53\x85\x09',
]
REAL_SIZE_REGEX = re.compile(r'Physical Size = (\d+)')


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """

    logging.debug(f'File Type unknown: execute binwalk on {file_path}')
    output = execute_shell_command(f'binwalk --extract --carve --signature --directory  {tmp_dir} {file_path}')

    drop_underscore_directory(tmp_dir)
    return {'output': output, 'filter_log': ArchivesFilter(tmp_dir).remove_false_positive_archives()}


class ArchivesFilter:
    def __init__(self, unpack_directory):
        self.unpack_directory = Path(unpack_directory)
        self.screening_logs = []

    def remove_false_positive_archives(self) -> str:
        for file_path in self.unpack_directory.glob('**/*'):
            if not file_path.is_file():
                continue
            file_type = magic.from_file(file_path, mime=True)

            if file_type == 'application/x-tar' or self._is_possible_tar(file_type, file_path):
                self._remove_invalid_archives(file_path, 'tar -tvf {}', 'does not look like a tar archive')

            elif file_type == 'application/x-xz':
                self._remove_invalid_archives(file_path, 'xz -c -d {} | wc -c')

            elif file_type == 'application/gzip':
                self._remove_invalid_archives(file_path, 'gzip -c -d {} | wc -c')

            elif file_path.suffix == '7z' or file_type in [
                'application/x-7z-compressed',
                'application/x-lzma',
                'application/zip',
                'application/zlib',
            ]:
                self._remove_invalid_archives(file_path, '7z l {}', 'ERROR')

            if file_path.is_file():
                self._remove_trailing_data(file_type, file_path)

        return '\n'.join(self.screening_logs)

    @staticmethod
    def _is_possible_tar(file_type: str, file_path: Path) -> bool:
        # broken tar archives may be identified as octet-stream by newer versions of libmagic
        if file_type == 'application/octet-stream':
            with file_path.open(mode='rb') as fp:
                fp.seek(0x101)
                return fp.read(5) == TAR_MAGIC
        return False

    def _remove_invalid_archives(self, file_path: Path, command, search_key=None):
        output = execute_shell_command(command.format(file_path))

        if search_key and search_key in output.replace('\n ', '') or not search_key and _output_is_empty(output):
            self._remove_file(file_path)

    def _remove_file(self, file_path):
        file_path.unlink()
        self.screening_logs.append(f'{file_path.name} was removed (invalid archive)')

    def _remove_trailing_data(self, file_type: str, file_path: Path):
        trailing_data_index = None

        if file_type in ['application/zip', 'application/zlib']:
            trailing_data_index = _find_trailing_data_index_zip(file_path)

        elif file_type == 'application/x-bzip2':
            trailing_data_index = _find_trailing_data_index_bz2(file_path)

        if trailing_data_index:
            self._resize_file(trailing_data_index, file_path)

    def _resize_file(self, actual_size: int, file_path: Path):
        with file_path.open('rb') as fp:
            actual_content = fp.read(actual_size)
        file_path.write_bytes(actual_content)
        self.screening_logs.append(f'Removed trailing data at the end of {file_path.name}')


def _output_is_empty(output):
    return int((output.split())[-1]) == 0


def _find_trailing_data_index_zip(file_path: Path) -> int | None:
    """Archives carved by binwalk often have trailing data at the end. 7z can determine the actual file size."""
    output = execute_shell_command(f'7z l {file_path}')
    if 'There are data after the end of archive' in output:
        match = REAL_SIZE_REGEX.search(output)
        if match:
            return int(match.groups()[0])
    return None


def _find_trailing_data_index_bz2(file_path: Path) -> int | None:
    output = execute_shell_command(f'bzip2 -t {file_path}')
    if 'trailing garbage' in output:
        file_content = file_path.read_bytes()
        matches = sorted(index for magic in BZ2_EOF_MAGIC if (index := file_content.find(magic)) != -1)
        # there may be two matches, but we want the first one (but also not -1 == no match)
        if matches:
            # 10 is magic string + CRC 32 checksum + padding (see https://en.wikipedia.org/wiki/Bzip2#File_format)
            return matches[0] + 10
    return None


def drop_underscore_directory(tmp_dir):
    extracted_contents = list(Path(tmp_dir).iterdir())
    if not extracted_contents:
        return
    if len(extracted_contents) != 1 or not extracted_contents[0].name.endswith('.extracted'):
        return
    for result in extracted_contents[0].iterdir():
        shutil.move(str(result), str(result.parent.parent))
    shutil.rmtree(str(extracted_contents[0]))


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
