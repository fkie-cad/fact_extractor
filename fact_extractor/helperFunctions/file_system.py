import logging
from pathlib import Path
from re import match

from common_helper_process import execute_shell_command_get_return_code

SRC_DIR_PATH = Path(__file__).parent.parent.absolute()


def get_src_dir() -> str:
    '''
    Returns the absolute path of the src directory
    '''
    return str(SRC_DIR_PATH)


def get_test_data_dir() -> str:
    '''
    Returns the absolute path of the test data directory
    '''
    return str(SRC_DIR_PATH / 'test' / 'data')


def get_fact_bin_dir() -> str:
    '''
    Returns the absolute path of the bin directory
    '''
    return str(SRC_DIR_PATH / 'bin')


def file_is_empty(file_path) -> bool:
    '''
    Returns True if file in file_path has 0 Bytes
    Returns False otherwise
    '''
    try:
        return Path(file_path).stat().st_size == 0
    except (FileNotFoundError, PermissionError, OSError, RuntimeError):
        return False


def file_name_sanitize(file_path) -> str:
    '''
    Returns file path without directory traversal
    '''
    return file_path.replace('../', '')


def change_owner_of_output_files(files_dir: Path, owner: str) -> int:
    if not match(r'\d+:\d+', owner):
        logging.error('ownership string should have the format <user id>:<group id>')
        return 1

    _, return_code_chown = execute_shell_command_get_return_code(f'sudo chown -R {owner} {files_dir}')
    _, return_code_chmod = execute_shell_command_get_return_code(f'sudo chmod -R u+rw {files_dir}')
    return return_code_chmod | return_code_chown
