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

    try:
        with open(file_path, 'rb') as f:
            srec = f.readlines()
        with open(str(target_file.absolute()), 'wb') as f:
            for line in srec:
                type_, address, size, data = bincopy.unpack_srec(line.decode())
                f.write(data)
    except bincopy.Error as srecError:
        return {'output': 'Unknown error in srec decoding: {}'.format(str(srecError))}

    return {'output': 'Successfully decoded srec file'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
