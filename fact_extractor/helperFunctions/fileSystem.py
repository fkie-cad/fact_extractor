import logging
import os
import sys


def get_src_dir():
    '''
    Returns the absolute path of the src directory
    '''
    return get_parent_dir(get_directory_of_current_file())


def get_test_data_dir():
    '''
    Returns the absolute path of the test data directory
    '''
    return os.path.join(get_src_dir(), 'test/data')


def get_faf_bin_dir():
    '''
    Returns the absolute path of the bin directory
    '''
    return os.path.join(get_src_dir(), 'bin')


def get_directory_of_current_file():
    return os.path.dirname(os.path.abspath(__file__))


def get_parent_dir(dir_path):
    dir_path = dir_path.split('/')
    dir_path = dir_path[0:len(dir_path) - 1]
    dir_path = '/'.join(dir_path)
    return dir_path


def file_is_empty(file_path):
    '''
    Returns True if file in file_path has 0 Bytes
    Returns False otherwise
    '''
    try:
        if os.path.getsize(file_path) == 0:
            return True
    except (FileNotFoundError, PermissionError, OSError):
        return False
    except Exception as e:
        logging.error('Unexpected Exception: {} {}'.format(sys.exc_info()[0].__name__, e))
    else:
        return False
