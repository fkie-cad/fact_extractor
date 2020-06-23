'''
This plugin decodes / unpacks Motorola SRecord files (.srec)
'''
from pathlib import Path

import bincopy

NAME = 'Motorola S-Record'
MIME_PATTERNS = ['firmware/srecord']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    target_file = Path(tmp_dir, Path(file_path).name)
    decoded = b''
    try:
        srec = Path(file_path).read_text().splitlines()
        for item in srec:
            _, _, _, data = bincopy.unpack_srec(item)
            decoded += data
        Path(target_file).write_bytes(decoded)

    except bincopy.Error as srec_error:
        return {'output': 'Unknown error in srec decoding: {}'.format(str(srec_error))}
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}

    return {'output': 'Successfully decoded srec file'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
