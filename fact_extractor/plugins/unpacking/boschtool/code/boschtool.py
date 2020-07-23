from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict

from common_helper_process import execute_shell_command

NAME = 'BoschFirmwareTool'
MIME_PATTERNS = ['firmware/bosch']
VERSION = '0.1'

TOOL_PATH = Path(__file__).parent.parent / 'bin' / 'boschfwtool'


def unpack_function(file_path: str, tmp_dir: TemporaryDirectory) -> Dict[str, str]:
    """
    Extract Bosch .fw files
    Source: https://github.com/anvilventures/BoschFirmwareTool
    """
    command = f'{TOOL_PATH} {file_path} -o {tmp_dir}'
    output = execute_shell_command(command, timeout=60)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
