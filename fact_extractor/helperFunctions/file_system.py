import logging
import lzma
from contextlib import contextmanager
from pathlib import Path
from re import match
from tempfile import TemporaryDirectory
from typing import Iterable

from common_helper_process import execute_shell_command_get_return_code

SRC_DIR_PATH = Path(__file__).parent.parent.absolute()


def get_src_dir() -> str:
    """
    Returns the absolute path of the src directory
    """
    return str(SRC_DIR_PATH)


def get_test_data_dir() -> str:
    """
    Returns the absolute path of the test data directory
    """
    return str(SRC_DIR_PATH / 'test' / 'data')


def get_fact_bin_dir() -> str:
    """
    Returns the absolute path of the bin directory
    """
    return str(SRC_DIR_PATH / 'bin')


def file_is_empty(file_path) -> bool:
    """
    Returns True if file in file_path has 0 Bytes
    Returns False otherwise
    """
    try:
        return Path(file_path).stat().st_size == 0
    except (FileNotFoundError, PermissionError, OSError, RuntimeError):
        return False


def file_name_sanitize(file_path) -> str:
    """
    Returns file path without directory traversal
    """
    return file_path.replace('../', '')


def change_owner_of_output_files(files_dir: Path, owner: str) -> int:
    if not match(r'\d+:\d+', owner):
        logging.error('ownership string should have the format <user id>:<group id>')
        return 1

    _, return_code_chown = execute_shell_command_get_return_code(f'sudo chown -R {owner} {files_dir}')
    _, return_code_chmod = execute_shell_command_get_return_code(f'sudo chmod -R u+rw {files_dir}')
    return return_code_chmod | return_code_chown


@contextmanager
def decompress_test_file(test_file: Path) -> Iterable[Path]:
    with TemporaryDirectory() as tmp_dir:
        target_file = Path(tmp_dir) / 'fs.img'
        with lzma.open(test_file) as decompressed_file:
            target_file.write_bytes(decompressed_file.read())
        yield target_file


def copy_file_offset_to_file(input_file: Path, output_file: Path, offset: int = 0, chunk_size: int = 2**20):
    """
    Copy contents of `input_file` from offset `offset` to `output_file`. The file is copied in chunks to save memory.
    """
    with output_file.open('wb') as fp_out, input_file.open('rb') as fp_in:
        fp_in.seek(offset)
        while chunk := fp_in.read(chunk_size):
            fp_out.write(chunk)
