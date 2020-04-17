'''
This plugin unpacks SquashFS filesystem images
'''
from common_helper_files import get_files_in_dir
from common_helper_process import execute_shell_command
from pathlib import Path

from helperFunctions.file_system import get_fact_bin_dir


SASQUATCH = Path('/usr/local/bin/sasquatch')
UNSQUASHFS4_AVM_BE = Path(get_fact_bin_dir()) / 'unsquashfs4-avm-be'
UNSQUASHFS4_AVM_LE = Path(get_fact_bin_dir()) / 'unsquashfs4-avm-le'
UNSQUASHFS3_MULTI = Path(get_fact_bin_dir()) / 'unsquashfs3-multi'


NAME = 'SquashFS'
MIME_PATTERNS = ['filesystem/squashfs']
VERSION = '0.8'
SQUASH_UNPACKER = [SASQUATCH, UNSQUASHFS4_AVM_BE,
                   UNSQUASHFS4_AVM_LE, UNSQUASHFS3_MULTI]


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    unpack_result = dict()
    for unpacker in SQUASH_UNPACKER:
        output = execute_shell_command('fakeroot {} -d {}/fact_extracted {}'.format(unpacker, tmp_dir, file_path))
        if _unpack_success(tmp_dir):
            unpack_result['unpacking_tool'] = unpacker.name
            unpack_result['output'] = output
            break
        unpack_result['{} - error'.format(unpacker.name)] = output
    return unpack_result


def _unpack_success(tmp_dir):
    return len(get_files_in_dir(tmp_dir)) > 0


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
