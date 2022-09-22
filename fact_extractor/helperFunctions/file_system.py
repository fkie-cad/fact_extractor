from pathlib import Path

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
