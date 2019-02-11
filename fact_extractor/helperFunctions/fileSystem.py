import logging
import os
import sys
from pathlib import Path
from typing import Union

import magic

from helperFunctions.dataConversion import make_unicode_string


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


def get_file_type_from_path(file_path: Union[str, Path]):
    '''
    This functions returns a dict with the file's mime- and full-type.
    It uses the custom mime database found in src/bin/custommime.mgc
    If no match was found, it uses the standard system magic file.
    '''
    path_string = file_path if isinstance(file_path, str) else str(file_path)
    return _get_file_type(path_string, 'from_file')


def _get_file_type(path_or_binary, function_name):
    magic_path = os.path.join(get_src_dir(), 'bin/custommime.mgc')

    magic_wrapper = magic.Magic(magic_file=magic_path, mime=True)
    mime = _get_type_from_magic_object(path_or_binary, magic_wrapper, function_name, mime=True)

    magic_wrapper = magic.Magic(magic_file=magic_path, mime=False)
    full = _get_type_from_magic_object(path_or_binary, magic_wrapper, function_name, mime=False)

    if mime == 'application/octet-stream':
        mime = _get_type_from_magic_object(path_or_binary, magic, function_name, mime=True)
        full = _get_type_from_magic_object(path_or_binary, magic, function_name, mime=False)
    return {'mime': mime, 'full': full}


def _get_type_from_magic_object(path_or_binary, magic_object, function_name, mime=True):
    try:
        if isinstance(magic_object, magic.Magic):
            result = make_unicode_string(getattr(magic_object, function_name)(path_or_binary))
        else:
            result = make_unicode_string(getattr(magic_object, function_name)(path_or_binary, mime=mime))
    except FileNotFoundError as e:
        logging.error('File not found: {}'.format(e))
        result = 'error/file-not-found' if mime else 'Error: File not in storage!'
    except Exception as exception:
        logging.error('Could not determine file type: {} {}'.format(type(exception), str(exception)))
        result = 'application/octet-stream' if mime else 'data'
    return result


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
