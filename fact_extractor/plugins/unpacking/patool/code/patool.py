'''
This plugin unpacks several formats utilizing patool
'''
from os import symlink
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command

NAME = 'PaTool'
MIME_PATTERNS = [
    'application/x-lrzip', 'application/x-cpio', 'application/x-archive', 'application/x-adf',
    'application/x-redhat-package-manager', 'application/x-rpm', 'application/x-lzop', 'application/x-lzh',
    'application/x-lha', 'application/x-cab', 'application/vnd.ms-cab-compressed', 'application/zpaq',
    'application/x-chm', 'application/x-gzip', 'application/gzip', 'application/x-bzip2', 'application/x-dms',
    'application/x-debian-package', 'application/x-rzip', 'application/x-tar', 'application/x-shar',
    'application/x-lzip', 'application/x-alzip', 'application/x-rar', 'application/rar',
    'application/java-archive', 'application/x-iso9660-image', 'application/x-compress', 'application/x-arc',
    'audio/flac','application/x-ace', 'application/x-zoo', 'application/x-xz'
]
VERSION = '0.5.2'


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    return {
        'output': execute_shell_command('fakeroot patool extract --outdir {} {}'.format(tmp_dir, file_path), timeout=600)
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
