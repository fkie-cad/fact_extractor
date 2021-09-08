'''
This plugin unpacks all files via carving
'''
import logging
import shutil
import zlib
from pathlib import Path

from common_helper_process import execute_shell_command, execute_interactive_shell_command
from fact_helper_file import get_file_type_from_path

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '0.9'

TAR_MAGIC = b'ustar'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''

    logging.debug(f'File Type unknown: execute binwalk on {file_path}')
    output = execute_interactive_shell_command(f'binwalk --extract --carve --signature --directory {tmp_dir} {file_path}', timeout=600)
    drop_underscore_directory(tmp_dir)
    return {'output': output, 'filter_log': ArchivesFilter(tmp_dir, original_file=file_path).remove_false_positive_archives()}


class ArchivesFilter:
    def __init__(self, unpack_directory, original_file=None):
        if original_file:
            self.original_size = Path(original_file).stat().st_size
        else:
            self.original_size = None

        self.unpack_directory = Path(unpack_directory)
        self.screening_logs = []

    def remove_false_positive_archives(self) -> str:
        for file_path in self.unpack_directory.iterdir():
            file_type = get_file_type_from_path(file_path)['mime']

            # If the carved file is the same as the original file, then we don't want to keep it.
            if self.check_file_size_same_as_original(file_path):
                continue

            if file_type == 'application/x-tar' or self._is_possible_tar(file_type, file_path):
                self.check_archives_validity(file_path, 'tar -tvf {}', 'does not look like a tar archive')
            elif file_type == 'application/x-xz':
                self.check_archives_validity(file_path, 'xz -c -d {} | wc -c')
            elif file_type == 'application/gzip':
                self.check_archives_validity(file_path, 'gzip -c -d {} | wc -c')
            elif file_type in ['application/zip', 'application/x-7z-compressed', 'application/x-lzma']:
                self.check_archives_validity(file_path, '7z l {}', 'ERROR')
            elif file_type in ['compression/zlib', 'application/zlib']:
                self.check_zlib_archive_validity(file_path)

        return '\n'.join(self.screening_logs)

    def check_file_size_same_as_original(self, file_path: Path):
        # binwalk will occasionally extract a file that is identical to the original
        # usually the filename is 0.yyy, and that's totally unhelpful. Remove if this is the case.
        if self.original_size is not None:
            file_size = file_path.stat().st_size
            if self.original_size == file_size:
                self.remove_file(file_path)
                return True
        return False

    @staticmethod
    def _is_possible_tar(file_type: str, file_path: Path) -> bool:
        # broken tar archives may be identified as octet-stream by newer versions of libmagic
        if file_type == 'application/octet-stream':
            with file_path.open(mode='rb') as fp:
                fp.seek(0x101)
                return fp.read(5) == TAR_MAGIC
        return False

    def check_archives_validity(self, file_path: Path, command, search_key=None):
        output = execute_shell_command(command.format(file_path))

        if search_key and search_key in output.replace('\n ', ''):
            self.remove_file(file_path)

        elif not search_key and self.output_is_empty(output):
            self.remove_file(file_path)

    def remove_file(self, file_path):
        file_path.unlink()
        screening_log = f'{file_path.name} was removed (invalid archive)'
        self.screening_logs.append(screening_log)

    @staticmethod
    def output_is_empty(output):
        return int((output.split())[-1]) == 0

    def check_zlib_archive_validity(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
            valid = False
            try:
                uncompressed = zlib.decompress(data)
                # It's only a valid file if it has data...
                if len(uncompressed):
                    valid = True
            except zlib.error:
                valid = False

        if not valid:
            self.remove_file(file_path)


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
