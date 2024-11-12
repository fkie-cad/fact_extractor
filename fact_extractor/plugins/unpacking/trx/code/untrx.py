from os import path
from tempfile import NamedTemporaryFile

from common_helper_process.fail_safe_subprocess import execute_shell_command

from helperFunctions.file_system import get_fact_bin_dir

NAME = 'untrx'
MIME_PATTERNS = ['firmware/trx']
VERSION = '0.4'

UNPACKER_EXECUTEABLE = path.join(get_fact_bin_dir(), 'untrx')


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    offset = _get_trx_offset(file_path)
    if offset > 0:
        with NamedTemporaryFile('bw') as tf:
            _remove_non_trx_header(file_path, tf, offset)
            output = _unpack_trx(tf.name, tmp_dir)
    else:
        output = _unpack_trx(file_path, tmp_dir)

    return {'output': output}


def _get_trx_offset(file_path):
    with open(file_path, 'br') as fp:
        content = fp.read()
        offset = content.find(b'HDR0')
    return offset


def _remove_non_trx_header(source_path, target_fp, offset):
    with open(source_path, 'br') as source_fp:
        source_fp.seek(offset)
        content = source_fp.read()
        target_fp.write(content)
        target_fp.seek(0)


def _unpack_trx(file_path, target_dir):
    return execute_shell_command(f'fakeroot {UNPACKER_EXECUTEABLE} {file_path} {target_dir}')


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
