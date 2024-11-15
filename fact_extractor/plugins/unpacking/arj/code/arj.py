from os import symlink
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command

NAME = 'ARJ'
MIME_PATTERNS = ['application/x-arj']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    """
    Extract arj files
    Since the arj binary only works correct when files end with .arj, this is taken care of
    """
    with TemporaryDirectory() as staging_dir:
        staged_path = str(Path(staging_dir) / f'{Path(file_path).name}.arj')
        symlink(file_path, staged_path)
        output = execute_shell_command(f'arj x -r -y {staged_path} {tmp_dir}', timeout=600)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
