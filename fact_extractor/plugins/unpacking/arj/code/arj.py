from os import symlink
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command

NAME = 'ARJ'
MIME_PATTERNS = ['application/x-arj']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    """
    Extract arj files using patool while ensuring files end with .arj
    """
    with TemporaryDirectory() as staging_dir:
        staged_path = str(Path(staging_dir) / '{}.arj'.format(Path(file_path).name))
        symlink(file_path, staged_path)
        output = execute_shell_command(
            'arj x -r -y {} {}'.format(staged_path, tmp_dir), timeout=600
        )

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
