'''
This plugin unpacks SquashFS filesystem images
'''
from common_helper_files import get_files_in_dir
from common_helper_process import execute_shell_command
from pathlib import Path

from helperFunctions.file_system import get_fact_bin_dir

SASQUATCH = Path('/usr/bin/sasquatch')
UNSQUASHFS4_AVM_BE = Path(get_fact_bin_dir()) / 'unsquashfs4-avm-be'
UNSQUASHFS4_AVM_LE = Path(get_fact_bin_dir()) / 'unsquashfs4-avm-le'
UNSQUASHFS3_MULTI = Path(get_fact_bin_dir()) / 'unsquashfs3-multi'

NAME = 'SquashFS'
MIME_PATTERNS = ['filesystem/squashfs']
VERSION = '0.10'
SQUASH_UNPACKER = [
    (SASQUATCH, '-c lzma-adaptive'),
    (UNSQUASHFS4_AVM_BE, '-scan'),
    (UNSQUASHFS4_AVM_LE, '-scan'),
    (UNSQUASHFS3_MULTI, '-scan'),
]


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    unpack_result = {}
    for unpacker, parameter in SQUASH_UNPACKER:
        # We need to force here since "-dest" does not allow existing directories
        output = execute_shell_command(
            f"fakeroot {unpacker} {parameter} -dest {tmp_dir} -force {file_path}",
        )
        if _unpack_success(tmp_dir):
            unpack_result['unpacking_tool'] = unpacker.name
            unpack_result['output'] = output
            break
        unpack_result[f'{unpacker.name} - error'] = output
    return unpack_result


def _unpack_success(tmp_dir):
    return len(get_files_in_dir(str(tmp_dir))) > 0


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
