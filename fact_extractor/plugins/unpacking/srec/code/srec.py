'''
This plugin decodes / unpacks Motorola SRecord files (.srec)
'''
from __future__ import annotations
import re
from pathlib import Path

import bincopy

NAME = 'Motorola S-Record'
MIME_PATTERNS = ['firmware/srecord']
VERSION = '0.2'
SREC_REGEX = b'(S[0-6][0-9A-F]+[\n\r]{1,2})+(S[7-9][0-9A-F]+)?'


def unpack_function(file_path: str | Path, tmp_dir: str | Path) -> dict[str, str]:
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    try:
        file_data = Path(file_path).read_bytes()
    except FileNotFoundError as fnf_error:
        return {'output': f'Failed to open file: {str(fnf_error)}'}

    match = re.match(SREC_REGEX, file_data)
    if match is None:
        return {'output': 'Error: no valid srec data found'}

    try:
        decoded = _decode_srec(file_data[0:match.end()])
        target_file = Path(tmp_dir) / _get_unpacked_filename(file_path)
        target_file.write_bytes(decoded)
    except (bincopy.Error, ValueError) as srec_error:
        return {'output': f'Unknown error in srec decoding: {str(srec_error)}'}

    return {'output': 'Successfully decoded srec file'}


def _decode_srec(srec_data: bytes) -> bytes:
    decoded = b''
    for line in srec_data.splitlines():
        _, _, _, data = bincopy.unpack_srec(line.decode())
        decoded += data
    return decoded


def _get_unpacked_filename(file_path: str) -> str:
    return Path(file_path).with_suffix('.bin').name


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
