'''
This plugin unpacks Vantiva DOCSIS cable modem images.
'''

import struct
from pathlib import Path
from common_helper_files import write_binary_to_file

NAME = "Vantiva"
MIME_PATTERNS = ['firmware/vantiva-docsis']
version = '0.1'

SOBJ_HEADER = b'SOBJ'

def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    '''

    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except IOError as io_error:
        return {'output': 'failed ot read file: []'.format(str(io_error))}
    
    return {
            'output': 'successfully unpacked Vantiva image'
    }

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
