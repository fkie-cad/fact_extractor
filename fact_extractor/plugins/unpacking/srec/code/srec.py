'''
This plugin decodes / unpacks Motorola SRecord files (.srec)
'''
from pathlib import Path
from typing import Dict

import bincopy

NAME = 'Motorola S-Record'
MIME_PATTERNS = ['firmware/srecord']
VERSION = '0.1'


def unpack_function(file_path: str, tmp_dir: str) -> Dict[str, str]:
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    target_file = Path(tmp_dir) / _get_unpacked_filename(file_path)
    decoded = b''
    try:
        srec = Path(file_path).read_bytes().splitlines()
        for line in srec:
            try:
                _, _, _, data = bincopy.unpack_srec(line.decode())
                decoded += data
            except UnicodeDecodeError:
                break
        target_file.write_bytes(decoded)

    except bincopy.Error as srec_error:
        return {'output': 'Unknown error in srec decoding: {}'.format(str(srec_error))}
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}

    return {'output': 'Successfully decoded srec file'}


def _get_unpacked_filename(file_path):
    file_name = f'{Path(file_path).name}.bin'
    return file_name.replace('.srec', '')


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
