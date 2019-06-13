'''
This plugin unpacks several formats utilizing patool
'''
from os import symlink
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command

NAME = 'PaTool'
MIME_PATTERNS = ['application/x-lrzip', 'application/x-cpio', 'application/x-archive', 'application/x-adf',
                 'application/x-redhat-package-manager', 'application/x-rpm', 'application/x-lzop', 'application/x-lzh',
                 'application/x-lha', 'application/x-cab', 'application/vnd.ms-cab-compressed', 'application/zpaq',
                 'application/x-chm', 'application/x-arj', 'application/x-gzip',
                 'application/gzip', 'application/x-bzip2', 'application/x-dms',
                 'application/x-debian-package', 'application/x-rzip', 'application/x-tar', 'application/x-shar',
                 'application/x-lzip', 'application/x-alzip', 'application/x-rar', 'application/rar',
                 'application/java-archive',
                 'application/x-iso9660-image', 'application/x-compress', 'application/x-arc', 'audio/flac',
                 'application/x-ace', 'application/x-zoo', 'application/x-xz']
VERSION = '0.5.1'


def run_patool(file_path, tmp_dir):
    return execute_shell_command('fakeroot patool extract --outdir {} {}'.format(tmp_dir, file_path), timeout=600)


def handle_arj_files_explicitly(file_path, output, tmp_dir):
    '''
    arj needs target files to end on .arj
    So here a fitting symlink is created
    '''
    if 'running /usr/bin/arj x -r' in output and not list(Path(tmp_dir).iterdir()):
        with TemporaryDirectory() as staging_dir:
            staged_path = str(Path(staging_dir) / '{}.arj'.format(Path(file_path).name))
            symlink(file_path, staged_path)
            output = run_patool(staged_path, tmp_dir)
    return output


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    output = run_patool(file_path, tmp_dir)

    output = handle_arj_files_explicitly(file_path, output, tmp_dir)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
